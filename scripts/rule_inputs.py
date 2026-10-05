"""규칙 입력값(holdings 등) 공통부. parse_ripple.py, parse_gemini.py가 쓴다.

holdings = 준비자산을 원문 줄 단위로 정규화한 목록. 값은 전부 PDF 원문에서 읽고 읽은 곳(where)을 적는다.
field_notes 상태: found(원문에서 읽음) / not_disclosed(공개 여부를 묻는 항목이 원문에 없음) /
not_in_report(값이 원문에 없음) / not_applicable(해당 자산이 없음).
"""
import datetime, re, subprocess

KINDS = ('bank_deposit', 'term_deposit', 'treasury_bill', 'treasury_note', 'non_us_government_bill',
         'reverse_repo_overnight', 'reverse_repo_term', 'government_mmf', 'corporate_bond', 'precious_metal',
         'bitcoin', 'secured_loan', 'public_equity', 'other_investment', 'settlement', 'cash_equivalents_unsplit')
TREASURY = ('treasury_bill', 'treasury_note', 'non_us_government_bill')
REPO = ('reverse_repo_overnight', 'reverse_repo_term')
FIELDS = ('treasury_max_maturity_days', 'repo_max_maturity_days', 'disclosure_cadence', 'circulation_formula_disclosed',
          'custodian_disclosure', 'management_certification', 'redemption_days', 'interest_paid')
STATES = ('found', 'not_disclosed', 'not_in_report', 'not_applicable')


def date_of(iso):
    return datetime.date.fromisoformat(iso)


def days_to(as_of, maturity_iso):
    """기준일에서 만기일까지 달력일."""
    return (date_of(maturity_iso) - date_of(as_of)).days


def holding(kind, amount, label, where, as_of, maturity=None, maturity_days=None):
    """holdings 한 줄. maturity=ISO 날짜(종목별 만기가 원문에 있을 때), maturity_days=날짜 없이 원문이 일수로만 말할 때(하루짜리 역레포 등)."""
    assert kind in KINDS, kind
    listed = maturity is not None or maturity_days is not None
    days = days_to(as_of, maturity) if maturity else maturity_days
    assert days is None or days >= 0, (label, maturity, as_of)  # 기준일 전 만기는 있을 수 없다. 읽기 오류의 신호
    h = {'kind': kind, 'amount': amount, 'currency': 'USD', 'maturity_max_days': days, 'maturity_listed': listed,
         'label': label, 'where': where}
    if maturity: h['maturity_date'] = maturity
    return h


def note(state, where, text, **extra):
    assert state in STATES, state
    return {'state': state, 'where': where, 'note': text, **extra}


def derive(holdings, fund_holdings, as_of):
    """holdings와 fund_holdings에서 4, 5번 필드와 field_notes 두 개를 만든다."""
    pos = lambda hs: [h for h in hs if h['amount'] > 0]
    out = {'asset_types': sorted({h['kind'] for h in pos(holdings) if h['kind'] != 'settlement'})}
    notes = {}
    for key, kinds, basis_key, what in (('treasury_max_maturity_days', TREASURY, 'treasury_maturity_basis', '국채'),
                                        ('repo_max_maturity_days', REPO, None, '역레포')):
        d, f = ([h for h in pos(hs) if h['kind'] in kinds] for hs in (holdings, fund_holdings))
        allh = d + f
        if basis_key: out[basis_key] = None
        if not allh:
            out[key] = None
            notes[key] = note('not_applicable', None, f'{what} 줄이 직접 보유분에도 펀드 안 종목 목록에도 없다.')
            continue
        if basis_key: out[basis_key] = 'both' if d and f else ('direct' if d else 'fund')
        if any(h['maturity_max_days'] is None for h in allh):
            out[key] = None
            notes[key] = note('not_in_report', [h['where'] for h in allh if h['maturity_max_days'] is None][:3],
                              f'{what} 줄은 있으나 종목별 만기가 원문에 없다.')
            continue
        top = max(allh, key=lambda h: h['maturity_max_days'])
        out[key] = top['maturity_max_days']
        notes[key] = note('found', top['where'], f"{top['label']}, 만기 {top.get('maturity_date', '하루짜리')}, 기준일 {as_of} 기준 {top['maturity_max_days']}일")
    return out, notes


# ---- 원문 검색 ----

def find(text, pattern, flags=0, group=0):
    """text(쪽 구분 \\x0c) 안 첫 일치의 {page, line, raw}. 없으면 None."""
    m = re.search(pattern, text, flags)
    if not m: return None
    upto = m.start(group)
    for pi, pg in enumerate(text.split('\x0c'), 1):
        if upto <= len(pg):
            return {'page': pi, 'line': pg[:upto].count('\n') + 1, 'raw': re.sub(r'\s+', ' ', m.group(group))[:160]}
        upto -= len(pg) + 1


def hits(text, terms):
    """검색어 -> 일치 개수. 검색어는 낱말(대소문자 무시) 또는 (표시 이름, 정규식). 'not_disclosed' 근거(어떤 말로 찾았는지)를 note에 남기는 데 쓴다."""
    return {(t if isinstance(t, str) else t[0]): len(re.findall(t if isinstance(t, str) else t[1], text, re.I)) for t in terms}


def search_note(h):
    return '원문 전체 검색어(일치 수): ' + ', '.join(f"'{k}'({v})" for k, v in h.items())


# ---- 서명 이미지 ----

def _pdf_pages(pdf):
    return int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True, check=True).stdout)[1])


def name_y(pdf, page, name):
    """글자 층에서 이름(마지막 단어)의 위쪽 y(pt)와 쪽 높이. 없으면 None."""
    t = subprocess.run(['pdftotext', '-f', str(page), '-l', str(page), '-bbox', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
    h = re.search(r'<page width="[\d.]+" height="([\d.]+)"', t)
    ys = [float(y) for y, w in re.findall(r'yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">([^<]*)<', t) if w == name]
    return (ys[-1], float(h[1])) if ys and h else None


def signature_ink(pdf, page, y_pt, dpi=100):
    """이름 줄(y_pt, 위쪽) 바로 위 구역(52pt 위부터 2pt 위까지, 왼쪽 40pt~300pt)의 어두운 픽셀 수. 서명 줄(밑줄 글자, 가로로 긴 줄)은 빼고 센다.
    DocuSign 서명 이미지가 있으면 수백 개, 서명 줄만 있으면 0에 가깝다. pdftoppm 그레이 PGM을 표준 라이브러리로 읽는다."""
    s = dpi / 72
    raw = subprocess.run(['pdftoppm', '-gray', '-r', str(dpi), '-f', str(page), '-l', str(page), '-x', str(int(40 * s)),
                          '-y', str(int(max(y_pt - 52, 0) * s)), '-W', str(int(260 * s)), '-H', str(int(50 * s)), str(pdf)],
                         capture_output=True, check=True).stdout
    m = re.match(rb'P5\s+(\d+)\s+(\d+)\s+(\d+)\s', raw)
    w, px = int(m[1]), raw[m.end():]
    rows = [sum(1 for v in px[i:i + w] if v < 140) for i in range(0, len(px), w)]
    return sum(n for n in rows if n < w * 0.4)


def consecutive_months(paths):
    """파일 이름 끝의 YYYY-MM 목록이 빠짐없이 이어지는지. 이어지면 달 수, 아니면 ValueError. 보고 주기(월간) 근거."""
    ms = sorted(int(p.stem[-7:-3]) * 12 + int(p.stem[-2:]) - 1 for p in paths)
    if any(b - a != 1 for a, b in zip(ms, ms[1:])): raise ValueError('보고서 달이 이어지지 않음')
    return len(ms)
