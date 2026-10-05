#!/usr/bin/env python3
"""Gemini GUSD 월간 검사보고서 PDF 파서.

data/samples/Gemini_GUSD_Examination_*.pdf 를 읽어 data/reports_gemini.json 을 만든다.
출력 스키마는 data/reports_paxos.json(parse_paxos.py)과 같다. 금액에 센트가 있어 정수 달러로 반올림해 싣고,
합계 대사는 센트 단위로 한다(flags.cents에 센트 값). 글자 층이 없는 쪽은 OCR로 채운다(scripts/ocr_util.py).
합계 대사가 어긋나면 그 보고서를 결과에서 빼고 이유를 로그로 남긴다.

사용: python3 scripts/parse_gemini.py [--verbose]
"""
import json, re, subprocess, sys, pathlib, datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ocr_util import ocr_boxes, box_lines
import rule_inputs as ri

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'samples'
OUT = ROOT / 'data' / 'reports_gemini.json'
VERBOSE = '--verbose' in sys.argv

MONTHS = {m: i for i, m in enumerate(
    'january february march april may june july august september october november december'.split(), 1)}
DATE = r'[A-Z][a-z]+ \d{1,2},\s*\d{4}'
AMT = r'(?:\(\s?\d[\d,]*\.\d{2}\s?\)|\d[\d,]*\.\d{2})'
def loose(label):
    """글자 사이 공백을 허용한 라벨 정규식. 글자 층에 'ci rculation'처럼 낱글자가 떨어져 나오는 쪽이 있다."""
    return r'\s*'.join(re.escape(c) for c in label if c != ' ')


# 표 줄 라벨의 첫머리. 라벨이 두 줄로 꺾여 금액이 첫 줄에 붙으므로 첫머리만 잡고 뒤의 금액 두 개를 읽는다.
ANCHORS = [
    ('circulation', loose('GUSD issued and in circulation') + r'\S{0,2}\s+(?=[\d(])'),
    ('treasury', '(?:' + loose('Total') + r'\s*)?' + loose('U.S. Treasury bills') + r'(?!\s*:)'),
    ('cash', loose('Cash deposits held at U.S. regulated')),
    ('government_mmf', loose('Money') + r'[\s-]*' + loose('market funds')),
    ('other', loose('Net cash receivable')),
    ('total', loose('Total Reserve')),
]


def to_iso(s):
    m = re.match(r'([A-Za-z]+) (\d{1,2}),\s*(\d{4})', s.strip())
    return f'{m[3]}-{MONTHS[m[1].lower()]:02d}-{int(m[2]):02d}' if m else None


def cents(tok):
    return (-1 if tok.startswith('(') else 1) * int(re.sub(r'\D', '', tok))


def dollars(c):
    """센트 -> 정수 달러(0.5달러는 절댓값이 큰 쪽으로)."""
    return (abs(c) + 50) // 100 * (1 if c >= 0 else -1)


def text_of(pdf):
    """pdftotext -layout. 글자가 없는 쪽은 OCR로 채운다. 쪽 구분(\\x0c)을 그대로 둬 인용 쪽 번호는 PDF 쪽과 같다."""
    # 함정: pdftotext를 스레드풀 안에서 부르면 빈 문자열이 나온다. 순차 호출만 쓴다.
    text = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
    pages = text.split('\x0c')
    if pages[-1] == '': pages.pop()
    blank = [i for i, pg in enumerate(pages, 1) if not pg.strip()]
    for i in blank:
        lines = ['   '.join(t for _, t in ln) for ln in box_lines(ocr_boxes(pdf, i))]
        # OCR가 천 단위 쉼표와 소수점을 서로 바꿔 읽는다(1.212,539.17). 뒤에 3자리 묶음이 더 이어질 때만 쉼표로 고친다.
        pages[i - 1] = re.sub(r'(?<=\d)[.,](?=\d{3}(?:[.,]\d{3})*[.,]\d{2}\b)', ',', '\n'.join(lines))
    return '\x0c'.join(pages) + '\x0c', blank


def locate(text, pos):
    upto = 0
    for pi, pg in enumerate(text.split('\x0c'), 1):
        if pos <= upto + len(pg): return pi, pg[:pos - upto].count('\n') + 1
        upto += len(pg) + 1
    return None, None


def cite(text, pos, raw):
    p, l = locate(text, pos)
    return {'page': p, 'line': l, 'raw': raw}

# 규칙 입력값(holdings 등). 표 줄을 원문 그대로 읽어 만든다. 값은 전부 PDF 원문에서 읽고 where에 쪽, 줄, 원문 글을 적는다.
VAL = r'\(\s?\d[\d,]*\.\d{2}\s?\)|\d[\d,]*\.\d{2}|(?<=\s)-(?=\s|$)'
HEADER = re.compile(r'Market\s*value\s*of\s*the\s*Res\s*erve|Treasury bills:|^\s*CUSIP\s+Maturity', re.I)
ROW_START = re.compile(r'Cash deposits|Money[\s-]*market|Net cash receivable|Total\s*Reserve|(?:Total\s*)?U\.S\. Treasury bills', re.I)
CUSIP_ROW = re.compile(r'^(\w{9})\s+(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})$')
LABELS = {  # 표 줄 -> (kind, 원문 라벨)
    'bank_deposit': 'Cash deposits held at U.S. regulated financial institutions',
    'government_mmf': 'Money-market funds',
    'settlement': 'Net cash receivable (payable) due to timing and settlement differences',
    'treasury_bill': 'U.S. Treasury bills',
}
# 준비자산을 맡긴 기관 이름. 각주 2 문장에서 이 목록으로 찾고, 남는 대문자 낱말이 있으면 실패시켜 새 이름을 놓치지 않는다.
CUSTODIAN_NAMES = [
    r'State Street Bank and Trust Company', r'State Street', r'BNY Mellon Asset Management', r'BNY Mellon N\.A\.',
    r'Western Alliance Bank', r'Western Alliance', r'Signature Bank', r'Signature Securities Group', r'Silvergate Bank',
    r'Oppenheimer & Co\. Inc\.', r'Goldman Sachs Asset Management', r'Flagstar Advisors, Inc\.']
CIRC_TERMS = ['burn', 'mint', 'redeem', 'total supply', 'exclud', 'held by the Company', 'less the', 'Etherscan']
SIGNERS = ('Beard', 'Stojanovic')


def table_rows(pg, page_no):
    """표 쪽에서 [(종류, 라벨, 값 칸 둘의 센트, where 둘)]. 종류: cusip, ust_total, ust_agg, bank_deposit, government_mmf, settlement, total.
    라벨이 두 줄로 꺾여 금액이 아랫줄에 붙으므로 금액이 두 개 나오는 줄에서 한 줄을 닫는다. 모르는 줄은 ValueError(조용히 빠지지 않게)."""
    lines = pg.split('\n')
    i0 = next((i for i, l in enumerate(lines) if re.search(loose('GUSD issued and in circulation'), l)), None)
    if i0 is None: raise ValueError('유통량 줄 없음')
    rows, label = [], []
    for i in range(i0 + 1, len(lines)):
        l = lines[i]
        if not l.strip(): continue
        toks = list(re.finditer(VAL, l))
        if len(toks) == 1: raise ValueError(f'금액이 한 칸뿐인 줄: {l.strip()}')
        if len(toks) < 2:
            if HEADER.search(l): label = []
            else:
                # OCR가 값 칸의 '-'를 못 읽으면 금액 없는 줄이 다음 줄 라벨에 붙는다(2024-10 Money-market funds 줄이 정산 줄에 붙음).
                # 앞 줄이 'Money-market funds' 한 줄뿐이고 지금 줄이 새 표 줄의 첫머리면 앞 줄을 두 칸 모두 대시(0)인 줄로 닫는다.
                if label == ['Money-market funds'] and ROW_START.match(l.strip()):
                    rows.append(('government_mmf', label[0], [0, 0], [{'page': page_no, 'line': i, 'raw': '-(OCR가 대시를 못 읽음, 쪽 그림에서 두 칸 모두 -)'}] * 2))
                    label = []
                label.append(l.strip())
            continue
        lab = re.sub(r'\s+', ' ', ' '.join(label + [l[:toks[0].start()]]).replace('$', '')).strip()
        label = []
        tk = toks[:2]
        wh = [{'page': page_no, 'line': i + 1, 'raw': t.group(0)} for t in tk]
        cs = [0 if t.group(0) == '-' else cents(t.group(0)) for t in tk]
        base = re.sub(r'[\d\s]+$', '', lab) if not CUSIP_ROW.match(lab) else lab  # 라벨 끝의 각주 번호를 뗀다
        if CUSIP_ROW.match(lab): kind = 'cusip'
        elif re.match(r'Total\s*U\.?S\.? Treasury bills', base, re.I): kind = 'ust_total'
        elif re.match(r'U\.S\. Treasury bills', base, re.I): kind = 'ust_agg'
        elif re.search(r'Cash deposits', base): kind = 'bank_deposit'
        elif re.search(r'Money[\s-]*market', base, re.I): kind = 'government_mmf'
        elif re.search(r'Net cash receivable', base): kind = 'settlement'
        elif re.match(r'Total\s*Reserve', base): kind = 'total'
        else: raise ValueError(f'알 수 없는 표 줄: {lab}')
        rows.append((kind, lab, cs, wh))
        if kind == 'total': break
    return rows


def rule_inputs(r, text, pdf, ocr):
    """r(대사를 통과한 보고서)에 규칙 입력값 필드를 더한다. 기존 필드는 건드리지 않는다."""
    as_of = r['as_of']
    pages = text.split('\x0c')
    tp = r['sources']['circulation']['page']
    rows = table_rows(pages[tp - 1], tp)
    hs, cusip_sum, ust_total = [], 0, None
    for kind, lab, cs, wh in rows:
        c = cs[1]  # 값은 월말(둘째 칸)
        if kind == 'cusip':
            m = CUSIP_ROW.match(lab)
            yy = int(m[4]); yy += 2000 if yy < 100 else 0
            cusip_sum += c
            if c: hs.append(ri.holding('treasury_bill', c, f'U.S. Treasury bill CUSIP {m[1]}', wh[1], as_of, f'{yy}-{int(m[2]):02d}-{int(m[3]):02d}'))
        elif kind == 'ust_total': ust_total = c
        elif kind == 'total': pass
        elif c: hs.append(ri.holding(kind if kind != 'ust_agg' else 'treasury_bill', c, LABELS[kind if kind != 'ust_agg' else 'treasury_bill'], wh[1], as_of))
    # 값은 센트 정수로 모아 마지막에 달러 소수 둘째 자리로 싣는다.
    got = sum(h['amount'] for h in hs)
    tot_c = r['flags']['cents']['fair_value']
    chk = {'expected_cents': tot_c, 'got_cents': got, 'diff': got - tot_c}
    if ust_total is not None: chk['treasury_rows_vs_total'] = {'cusip_rows_sum': cusip_sum, 'total_row': ust_total, 'diff': cusip_sum - ust_total}
    if chk['diff'] or chk.get('treasury_rows_vs_total', {'diff': 0})['diff']:
        raise ValueError(f'holdings 대사 불일치 {chk}')
    for h in hs:
        h['amount'] = round(h['amount'] / 100, 2)
        if h['where']['page'] in ocr: h['where']['ocr'] = True
    r['holdings'], r['fund_holdings'], r['holdings_reconciliation'] = hs, [], chk
    d, notes = ri.derive(hs, [], as_of)
    r.update(d)
    mm = next((h for h in hs if h['kind'] == 'government_mmf'), None)
    if mm:  # MMF 안 종목은 원문에 없다. 국채, 역레포가 들었을 수 있으나 목록이 없어 직접 보유분만 센다.
        for k in ('treasury_max_maturity_days', 'repo_max_maturity_days'):
            if notes[k]['state'] == 'not_applicable':
                notes[k]['note'] += f" 정부 MMF {mm['amount']:,.2f}달러가 있으나 각주는 'government securities, repurchase agreements ... and cash'만 말하고 종목 목록은 없어 fund_holdings는 비워 둔다."
    # 6. 보고 주기
    m = re.search(rf'(?:during|for) the period from\s+({DATE}),?\s+to\s+({DATE})', text)
    a, b = (datetime.date.fromisoformat(to_iso(m[i])) for i in (1, 2))
    span = (b - a).days + 1
    if span > 31: raise ValueError(f'보고 기간 {span}일')
    r['disclosure_cadence'], r['disclosure_cadence_days'] = 'monthly', 31
    notes['disclosure_cadence'] = ri.note('found', ri.find(text, m.re.pattern, group=0),
        f"보고 기간이 한 달 이내({m[1]}부터 {m[2]}까지 {span}일). 표본 {ri.consecutive_months(sorted(SRC.glob('Gemini_GUSD_Examination_*.pdf')))}개월이 빠짐없이 이어짐.")
    # 7. 유통량 산정 방식
    h = ri.hits(text, CIRC_TERMS)
    et = ri.find(text, r'Per the Etherscan\.io website')
    r['circulation_formula_disclosed'] = False
    notes['circulation_formula_disclosed'] = ri.note('not_disclosed', et,
        "유통량 줄의 각주 1이 'Per the Etherscan.io website'로 출처만 밝히고, 발행에서 소각을 빼는지나 발행사 보유분을 제외하는지 같은 산정 방식 설명은 없다. " + ri.search_note({k: v for k, v in h.items()}))
    # 8. 맡긴 기관 이름
    fn = re.search(r'The Gemini dollar reserves are held and maintained\b(.*?)(?:Market values are based|\n\s*3\s)', re.sub(r'[ \t]+', ' ', text), re.S)
    sent = re.sub(r'\s+', ' ', fn[1]) if fn else ''
    names, rest = [], sent
    for pat in CUSTODIAN_NAMES:
        mm_ = re.search(pat, rest)
        if mm_: names.append(mm_.group(0)); rest = rest.replace(mm_.group(0), ' ')
    left = [w for w in re.findall(r'\b[A-Z][A-Za-z.&]+\b', rest) if w.rstrip('.') not in ('U.S', 'Treasury', 'Gemini', 'The', 'Market')]
    if left: raise ValueError(f'각주 2에 이름 목록에 없는 대문자 낱말 {left}')
    names.sort(key=sent.find)  # 원문에 나온 순서
    r['custodian_disclosure'], r['custodians'] = bool(names), names
    notes['custodian_disclosure'] = ri.note('found' if names else 'not_disclosed', ri.find(text, r'The Gemini dollar reserves are held and maintained'),
        '각주 2 문장에 이름이 있다: ' + '; '.join(names) if names else '각주 2에 기관 이름이 없다.')
    if not names: raise ValueError('각주 2에서 기관 이름을 못 찾음')
    # 9. 경영진 확인서
    sig = re.search(rf'\n\s*([A-Z][\w.]+(?: [A-Z][\w.]+)+)\s*\n\s*((?:Interim )?(?:CEO/President|CFO|Chief [A-Za-z ]+ Officer))\s*\n\s*(Gemini [A-Za-z ,.]+?)\s*\n\s*({DATE})', text)
    asr = ri.find(text, r'we assert that the Company has complied')
    if not (sig and asr): raise ValueError('경영진 확인서나 서명 블록을 못 찾음')
    sp = ri.find(text, re.escape(sig[2]).replace(r'\ ', r'\s+'))
    last = sig[1].split()[-1]
    pgno = locate(text, sig.start(1))[0]
    y = ri.name_y(pdf, pgno, last)
    if y is None:  # 글자 층에 이름이 없는 쪽(OCR한 쪽)은 OCR 글상자 위치로 찾는다.
        bx = [(yy, t) for yy, xx, t in ocr_boxes(pdf, pgno, 200) if last in t]
        y = (bx[-1][0] * 792, 792) if bx else None
    ink = ri.signature_ink(pdf, pgno, y[0]) if y else 0
    if ink < 200: raise ValueError(f'서명 이미지 못 확인(어두운 픽셀 {ink})')
    r['management_certification'], r['certifier'] = True, sig[2]
    notes['management_certification'] = ri.note('found', {'page': pgno, 'line': locate(text, sig.start(2))[1], 'raw': f'{sig[2]}, {sig[3]}, {sig[4]}'},
        f"Management's Assertion(쪽 {asr['page']} 'we assert that the Company has complied')에 {sig[2]}({sig[3]}) 서명 블록이 있고 서명 이미지 확인(이름 줄 위 어두운 픽셀 {ink}개)."
        + (' 쪽에 DRAFT 표시가 있다.' if r['flags'].get('draft') else ''))
    # 10. 상환 기한, 이자 지급
    hr = ri.hits(text, ['redemption requirements', 'redeem', ('within N days', r'within \w+ (?:business )?days?'), ('T+N', r'\bT\+\d')])
    r['redemption_days'] = None
    notes['redemption_days'] = ri.note('not_in_report', ri.find(text, r'redemption requirements'),
        "상환 기한 값이 없다. 'redemption requirements discussed in paragraph 1 of the DFS Letter'(항목 2(c))로 DFS 서한을 가리킬 뿐이다. " + ri.search_note(hr))
    hi = ri.hits(text, ['interest'])
    ii = ri.find(text, r'accrued interest payment')
    r['interest_paid'] = None
    notes['interest_paid'] = ri.note('not_in_report', ii,
        "소유자에게 이자를 준다는 문장이 없다. " + (f"'interest' 일치 {hi['interest']}건은 2023-03 각주의 'The Company received a final accrued interest payment'(예금 이자를 발행사가 받은 것)뿐이다. " if ii else "원문에 'interest' 낱말이 없다. ") + ri.search_note(hi))
    r['field_notes'] = {k: notes[k] for k in ri.FIELDS}


def parse(pdf):
    text, ocr = text_of(pdf)
    r = {'source_file': str(pdf.relative_to(ROOT)), 'issuer': None, 'token': 'GUSD'}
    sources = {}
    m = re.search(r'(Gemini Trust Company, LLC)', text)
    r['issuer'] = m[1] if m else None
    m = re.search(rf'we\s+report\s+the\s+following\s+end[\s-]of[\s-]day\s+amounts\s+for\s+the\s+following\s+(?:dates:\s+)?({DATE})\s+({DATE})', text)
    if not m: return {**r, 'ok': False, 'error': '보고 날짜 두 개를 찾지 못함'}
    r['report_dates'] = [to_iso(m[1]), to_iso(m[2])]
    r['as_of'] = r['report_dates'][1]; r['month'] = r['as_of'][:7]
    r['as_of_time'] = 'end of day' if re.search(r'end[\s-]of[\s-]day', m[0]) else None
    sources['report_dates'] = [cite(text, m.start(1), m[1]), cite(text, m.start(2), m[2])]
    if r['month'] not in pdf.name: return {**r, 'ok': False, 'error': f'파일 이름의 달과 기준일({r["as_of"]}) 불일치'}
    m = re.search(r'U\.S\. dollar', text)
    r['reserve_currency'] = 'USD' if m else None
    if m: sources['reserve_currency'] = cite(text, m.start(), m[0])

    # 표 구역: 유통량 줄부터 Total Reserve 줄의 금액 두 개까지. 첫째 금액이 앞 기준일, 둘째가 월말.
    start = re.search(ANCHORS[0][1], text)
    end = re.search(ANCHORS[5][1] + r'\s+\$?\s*' + AMT + r'\s+\$?\s*' + AMT, text[start.start():]) if start else None
    if not start or not end: return {**r, 'ok': False, 'error': '표(유통량 줄에서 Total Reserve 줄)를 찾지 못함'}
    base = start.start()
    block = text[base:base + end.end()]
    hits = []
    for key, pat in ANCHORS:
        mm = re.search(pat, block)
        if mm: hits.append((mm.start(), mm.end(), key))
    hits.sort()
    vals, cites = {}, {}
    for i, (s, e, key) in enumerate(hits):
        seg = block[e:hits[i + 1][0] if i + 1 < len(hits) else len(block)]
        nums = list(re.finditer(AMT, seg))
        # CUSIP별 줄은 유통량 줄 뒤 구역에 끼어 있다. 첫 두 금액만 쓴다. 금액이 없는 줄(OCR가 못 읽은 대시)은 0.
        if key in ('circulation', 'total') and len(nums) < 2:
            return {**r, 'ok': False, 'error': f'{key} 줄 금액 부족'}
        if key not in ('circulation', 'total') and len(nums) not in (0, 2) and key != 'treasury':
            return {**r, 'ok': False, 'error': f'{key} 줄 금액 {len(nums)}개'}
        pair = nums[:2] if len(nums) >= 2 else None
        if key == 'circulation' and len(nums) > 2: vals['cusip_rows'] = sum(cents(n.group(0)) for n in nums[3::2])
        vals[key] = cents(pair[1].group(0)) if pair else 0
        cites[key] = cite(text, base + e + pair[1].start(), pair[1].group(0)) if pair else {'page': locate(text, base + s)[0], 'line': locate(text, base + s)[1], 'raw': '(금액 칸 비어 있음, 0으로 봄)'}
    for key in ('treasury', 'cash', 'government_mmf', 'other'):
        if key not in vals: vals[key], cites[key] = 0, {'page': None, 'line': None, 'raw': '(표에 줄 없음, 0으로 봄)'}
    circ_c, tot_c = vals['circulation'], vals['total']
    comp_c = {k: vals[k] for k in ('cash', 'government_mmf', 'treasury', 'other')}
    sum_c = sum(comp_c.values())

    r['circulation'], r['fair_value'] = dollars(circ_c), dollars(tot_c)
    # 정수 달러 구성 합이 fair_value와 같도록 other가 반올림 차이를 흡수한다(센트 합이 맞을 때만 의미 있음, 아래 대사).
    comp = {'cash': dollars(comp_c['cash']), 'repo': 0, 'government_mmf': dollars(comp_c['government_mmf']),
            'treasury': dollars(comp_c['treasury'])}
    comp['other'] = r['fair_value'] - sum(comp.values())
    r['components'] = comp
    sources['circulation'] = cites['circulation']
    sources['fair_value'] = cites['total']
    sources['components'] = {k: cites[k] for k in ('cash', 'government_mmf', 'treasury', 'other')}
    sources['components']['total'] = cites['total']

    checks = {
        'components_sum': {'expected': tot_c, 'got': sum_c, 'diff': sum_c - tot_c, 'unit': 'cents'},
        'total_equals_fair_value': {'expected': r['fair_value'], 'got': dollars(tot_c), 'diff': 0},
        'covers_circulation': {'surplus': r['fair_value'] - r['circulation'], 'ok': tot_c >= circ_c},
    }
    # OCR한 쪽은 유통량을 확인할 다른 줄이 없다. GUSD는 매 보고서 Total Reserve와 유통량이 센트까지 같으므로 어긋나면 OCR 오독으로 본다.
    if ocr and tot_c != circ_c:
        checks['ocr_circulation_equals_reserve'] = {'expected': tot_c, 'got': circ_c, 'diff': circ_c - tot_c}
    # 참고용: Total U.S. Treasury bills 줄이 CUSIP별 줄 합계와 같은지. 대사 실패 원인(원문 합계 줄 오기)을 가리는 데 쓴다.
    if 'cusip_rows' in vals:
        checks['treasury_rows_sum'] = {'expected': vals['treasury'], 'got': vals['cusip_rows'], 'diff': vals['cusip_rows'] - vals['treasury'], 'unit': 'cents', 'info_only': True}
    r['reconciliation'] = checks
    r['ok'] = (checks['components_sum']['diff'] == 0 and checks['covers_circulation']['ok']
               and checks.get('ocr_circulation_equals_reserve', {'diff': 0})['diff'] == 0)
    if r['ok']: r['coverage'] = round(r['fair_value'] / r['circulation'], 8)

    mo = re.search(r'In our opinion.*?\n\s*(' + DATE + r')\s*\n', text, re.S)
    r['attestation'] = {
        'type': 'examination' if 'We have examined' in text else None,
        'standard': 'AICPA attestation standards' if re.search(
            r'attestation\s+standards\s+established\s+by\s+the\s+(?:American\s+Institute\s+of\s+Certified\s+Public\s+Accountants|AICPA)', text) else None,
        'signed': to_iso(mo[1]) if mo else None,
        # 서명이 손글씨 이미지라 글자 층에는 회계법인 이름이 없다(레터헤드는 bpm.com 주소뿐).
        'firm': 'BPM LLP' if 'BPM LLP' in text else None,
    }
    if mo: sources['attestation.signed'] = cite(text, mo.start(1), mo[1])
    r['flags'] = {'amounts_have_cents': True,
                  'cents': {'circulation': circ_c, 'fair_value': tot_c, **comp_c},
                  'letterhead': 'bpm.com' if 'bpm.com' in text else None}
    if re.search(r'\bDRAFT\b', text): r['flags']['draft'] = True  # 서명 전 초안(DRAFT 표시)
    if ocr: r['flags']['ocr_pages'] = ocr
    r['sources'] = sources
    if r['ok']: rule_inputs(r, text, pdf, ocr)
    return r


# 원문 자체가 안 맞아 제외하는 보고서(파서 오류가 아님, 원문 숫자를 직접 더해 확인). 새로 대사에 실패한 보고서만 종료 코드 1로 알린다.
KNOWN_SOURCE_ERRORS = {
    'Gemini_GUSD_Examination_2023-05.pdf': '표의 Total U.S. Treasury bills 284,442,090.00이 CUSIP별 줄 합계 284,422,090.00보다 20,000.00 크다(원문 오기). '
                                           '줄 합계로 더하면 Total Reserve 571,710,397.95와 맞는다.',
    'Gemini_GUSD_Examination_2023-09.pdf': '줄 합계(국채 232,257,614.60 + 현금 19,316,644.07 + MMF 50,409,302.73 - 정산 차액 1,151,280.64 = 300,832,280.76)가 '
                                           'Total Reserve 300,832,300.76보다 20.00 작다(원문 오기).',
    'Gemini_GUSD_Examination_2024-03.pdf': '표의 Total U.S. Treasury bills 22,201,909.40이 CUSIP별 줄 합계 22,201,919.40보다 10.00 작다(원문 오기). '
                                           '줄 합계로 더하면 Total Reserve 130,655,646.73과 맞는다.',
    'Gemini_GUSD_Examination_2026-04.pdf': '현금 43,571,282.42 + 정산 차액 (725,005.09) = 42,846,277.33이 Total Reserve 40,465,459.06과 2,380,818.27 어긋난다'
                                           '(4월 20일 칸은 맞음, 이미지 쪽을 눈으로 대조해 OCR 오독이 아님을 확인).',
}


def main():
    reports, bad = [], []
    for p in sorted(SRC.glob('Gemini_GUSD_Examination_*.pdf')):
        r = parse(p)
        reports.append(r)
        if r.get('ok'):
            print(f"ok  GUSD {r['month']}  유통 {r['circulation']:,}  준비자산 {r['fair_value']:,}  "
                  f"커버리지 {r['coverage'] * 100:.4f}%  기준일 {r['as_of']}  서명 {r['attestation']['signed']}"
                  + (f"  OCR쪽 {r['flags']['ocr_pages']}" if 'ocr_pages' in r['flags'] else '')
                  + ('  DRAFT' if r['flags'].get('draft') else ''))
        else:
            bad.append(p.name)
            print(f"FAIL {p.name}: {r.get('error') or r.get('reconciliation')}"
                  + (f"\n     제외 사유(원문 오기): {KNOWN_SOURCE_ERRORS[p.name]}" if p.name in KNOWN_SOURCE_ERRORS else ''))
        if VERBOSE: print('    ', json.dumps(r.get('components'), ensure_ascii=False), json.dumps(r.get('flags', {}), ensure_ascii=False))
    if not reports:
        print('PDF 없음:', SRC); return 1
    excluded = [{'token': 'GUSD', 'month': p.stem[-7:], 'source_file': f'data/samples/{p.name}',
                 'reason': KNOWN_SOURCE_ERRORS.get(p.name) or str(r.get('error') or r.get('reconciliation'))}
                for p, r in zip(sorted(SRC.glob('Gemini_GUSD_Examination_*.pdf')), reports) if not r.get('ok')]
    OUT.write_text(json.dumps({
        'generated': datetime.date.today().isoformat(),
        'source': 'Gemini GUSD(발행 법인 Gemini Trust Company, LLC) 월간 examination report, pdftotext -layout(글자 층 없는 쪽은 macOS Vision OCR)',
        'note': ('기준일은 월 중순과 월말 두 날이며 값은 월말(둘째 칸)을 쓴다. 금액은 센트까지 나와 정수 달러로 반올림했고 합계 대사는 센트로 했다(flags.cents). '
                 'components 매핑: cash=Cash deposits held at U.S. regulated financial institutions, '
                 'government_mmf=Money-market funds(주석상 국채, 정부증권 담보 레포, 현금만 보유하는 펀드), '
                 'treasury=Total U.S. Treasury bills(CUSIP별 줄 합계; 줄이 없는 달은 0), repo=표에 줄이 없어 0, '
                 'other=Net cash receivable (payable) due to timing and settlement differences(음수 가능)에 달러 반올림 차이를 더한 값. '
                 'sources.components에 키별 원문 금액 위치가 있다. sources는 숫자별 {page, line, raw}. 대사 실패 보고서는 reports에서 제외하고 excluded에 이유를 남긴다. 제외: '
                 + ' / '.join(f'{k[-11:-4]} {v}' for k, v in KNOWN_SOURCE_ERRORS.items())
                 + ' 규칙 입력값(holdings, fund_holdings, asset_types, treasury_max_maturity_days, treasury_maturity_basis, repo_max_maturity_days, '
                 'disclosure_cadence(_days), circulation_formula_disclosed, custodian_disclosure(custodians), management_certification(certifier), '
                 'redemption_days, interest_paid, field_notes)는 표 줄을 원문 그대로 읽은 것이다. holdings.amount는 달러(센트 포함)이며 합은 flags.cents.fair_value와 센트까지 같다'
                 '(holdings_reconciliation). 종목별 만기는 CUSIP 줄의 Maturity Date, 값은 월말 칸이다. field_notes.state: found 원문에서 읽음, not_disclosed 공개 여부 항목이 원문에 없음, '
                 'not_in_report 값이 원문에 없음, not_applicable 해당 자산 없음.'),
        'excluded': excluded,
        'reports': [r for r in reports if r.get('ok')],
    }, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n{len(reports)}건 중 성공 {len(reports) - len(bad)} → {OUT.relative_to(ROOT)}, 대사 실패 {len(bad)}')
    return 1 if set(bad) - set(KNOWN_SOURCE_ERRORS) else 0


if __name__ == '__main__':
    sys.exit(main())
