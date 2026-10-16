#!/usr/bin/env python3
"""Ripple RLUSD 월간 검사보고서 PDF 파서.

data/samples/Ripple_RLUSD_Examination_*.pdf 를 읽어 data/reports_ripple.json 을 만든다.
출력 스키마는 data/reports_paxos.json(parse_paxos.py)과 같다.
유통량과 준비자산 표는 모든 달이 그림이라 쪽을 OCR(scripts/ocr_util.py)로 읽는다. 글자 층은 날짜, 서명일, 기준 문구에만 쓴다.
OCR 값은 (1) 150dpi 두 해상도 판독이 같고 (2) 글자 층에 같은 값이 있으면 그것과 같고 (3) 합계 대사가 맞을 때만 받는다.
합계 대사가 어긋나면 그 보고서를 결과에서 빼고 이유를 로그로 남긴다.

사용: python3 scripts/parse_ripple.py [--verbose]
"""
import json, re, subprocess, sys, pathlib, datetime, statistics

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ocr_util import ocr_boxes, box_lines
import rule_inputs as ri
import collections, itertools

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'samples'
OUT = ROOT / 'data' / 'reports_ripple.json'
VERBOSE = '--verbose' in sys.argv
DPIS = (200, 300)

MONTHS = {m: i for i, m in enumerate(
    'january february march april may june july august september october november december'.split(), 1)}
DATE = r'[A-Z][a-z]+ \d{1,2},\s*\d{4}'
# 쉼표와 점 모두 천 단위로 받는다(OCR가 349,943.549처럼 읽는다). 'June 9,2025'의 '9,202'를 잡지 않도록 앞뒤 숫자를 막는다.
AMT = r'(?<![\d,.])\(?\$?\s?\d{1,3}(?:[,.]\d{3})+(?![\d,.])\)?'


def to_iso(s):
    m = re.match(r'([A-Za-z]+) (\d{1,2}),\s*(\d{4})', s.strip())
    return f'{m[3]}-{MONTHS[m[1].lower()]:02d}-{int(m[2]):02d}' if m else None


def locate(text, pos):
    """문자 오프셋 pos -> (쪽, 줄). 쪽 구분은 폼피드(\\x0c)."""
    upto = 0
    for pi, pg in enumerate(text.split('\x0c'), 1):
        if pos <= upto + len(pg): return pi, pg[:pos - upto].count('\n') + 1
        upto += len(pg) + 1
    return None, None


def cite(text, m, g=1):
    p, l = locate(text, m.start(g))
    return {'page': p, 'line': l, 'raw': m.group(g)}


def amounts_of(tok):
    """금액 글 하나 -> 정수. '-'는 0, 괄호는 음수."""
    return (-1 if '(' in tok else 1) * int(re.sub(r'\D', '', tok))


def read_table(pdf, page, dpi):
    """OCR한 쪽에서 {circulation, fair_value, rows, total}를 읽는다. 값은 둘째 칸(월말 기준일) 것이다.
    rows = [(라벨, 값, 쪽 안 줄 번호, 원문 글)] 표의 국채 줄(CUSIP 목록)은 빼고 합계 줄부터."""
    boxes = ocr_boxes(pdf, page, dpi)
    lines = box_lines(boxes)
    parsed = []  # (줄번호, 라벨, [(x, 값, 원문)])
    for n, ln in enumerate(lines, 1):
        am, label = [], []
        for x, t in ln:
            toks = list(re.finditer(AMT, t))
            if t.strip() in ('-', '–', '—'): am.append((x, 0, '-'))  # 빈 칸의 대시는 글상자 하나로 읽힌다
            elif toks: am += [(x, amounts_of(m[0]), m[0].strip()) for m in toks]
            else: label.append(t)
        if am: parsed.append((n, ' '.join(label), am))
    top = [p for p in parsed if len(p[2]) >= 2][:2]
    if len(top) < 2: raise ValueError('유통량과 준비자산 줄을 찾지 못함')
    top_n = {p[0] for p in top}
    body = [p for p in parsed if p[0] not in top_n and not re.search(r'^912\w{5,7}\b|\b912\w{5,7}\b', p[1])
            and not re.search(DATE, p[1])]
    # 칸 경계: 금액이 두 개씩 따로 놓인 줄들의 첫째 칸 x와 둘째 칸 x의 중앙값 평균
    pairs = [(p[2][0][0], p[2][1][0]) for p in parsed if len(p[2]) == 2 and p[2][1][0] - p[2][0][0] > 0.05]
    if not pairs: raise ValueError('칸 경계를 못 잡음')
    thr = (statistics.median(a for a, _ in pairs) + statistics.median(b for _, b in pairs)) / 2
    def cols(am):
        v, raw = [None, None], ['', '']
        for i, (x, val, r) in enumerate(am):
            c = (0 if i == 0 else 1) if len(am) == 2 and am[1][0] - am[0][0] < 0.05 else (0 if x < thr else 1)
            if v[c] is not None: raise ValueError('한 칸에 금액이 둘')
            v[c], raw[c] = val, r
        return [0 if a is None else a for a in v], raw
    rows, both = [], []
    for n, label, am in body:
        v, raw = cols(am)
        rows.append((label, v[1], n, raw[1] or '-'))
        both.append((v[0], v[1]))  # rows와 같은 순서, 두 칸 값(첫째 칸은 월 중순)
    return {'boxes': boxes, 'lines': lines, 'rows_both': both, 'circ': (cols(top[0][2])[0][1], top[0][0], cols(top[0][2])[1][1]),
            'fv': (cols(top[1][2])[0][1], top[1][0], cols(top[1][2])[1][1]),
            'rows': rows, 'thr': round(thr, 3), 'cusip': any(re.search(r'\b912\w{5,7}\b', p[1]) for p in parsed)}


def classify(rows, has_cusip):
    """합계 앞 줄들을 키로 나눈다. CUSIP 목록이 있으면 국채 합계 줄(라벨 'Total U.S. Treasury bills' 또는 'Subtotal',
    라벨이 지워졌으면 첫 라벨 없는 줄) 앞은 CUSIP별 줄이라 뺀다. 그 밖의 라벨 없는 줄은 other로 두고 라벨 없음으로 표시한다."""
    comp = {k: [] for k in ('cash', 'repo', 'government_mmf', 'treasury', 'other')}
    tr = next((i for i, x in enumerate(rows) if re.search(r'treasury|subtotal', x[0], re.I)), None)
    if tr is None and has_cusip: tr = next((i for i, x in enumerate(rows) if not x[0]), None)
    for i, (label, val, n, raw) in enumerate(rows):
        l = label.lower()
        if tr is not None and i < tr: continue
        if i == tr: k = 'treasury'
        elif re.search(r'money.?market|mmf|mon[eo]v', l): k = 'government_mmf'
        elif 'cash deposit' in l: k = 'cash'
        elif re.search(r'repurchase|repo', l): k = 'repo'
        else: k = 'other'
        comp[k].append({'label': label or '(라벨 없음)', 'line': n, 'raw': raw, 'value': val})
    return comp


def parse(pdf):
    r = {'source_file': str(pdf.relative_to(ROOT)), 'token': 'RLUSD'}
    # 함정: pdftotext를 스레드풀 안에서 부르면 빈 문자열이 나온다. 순차 호출만 쓴다.
    text = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
    sources = {}
    m = re.search(r'(Standard Custody & Trust Company, LLC)', text)
    r['issuer'] = m[1] if m else None
    m = re.search(rf'as of ({DATE}),?\s+and\s+(?:as of\s+)?({DATE}),?\s+at\s+(\d:\d\d\s*[ap]m)', text)
    if not m: return {**r, 'ok': False, 'error': 'Report Dates 문구를 찾지 못함'}
    r['report_dates'] = [to_iso(m[1]), to_iso(m[2])]
    r['as_of'] = r['report_dates'][1]; r['month'] = r['as_of'][:7]
    r['as_of_time'] = '17:00 ET' if re.search(r'5:00\s*pm', m[3]) and re.search(r'Eastern|\bET\b', text) else None
    sources['report_dates'] = [cite(text, m, 1), cite(text, m, 2)]
    if r['month'] not in pdf.name: return {**r, 'ok': False, 'error': f'파일 이름의 달과 기준일({r["as_of"]}) 불일치'}
    m = re.search(r'U\.S\. dollar', text)
    r['reserve_currency'] = 'USD' if m else None
    if m: sources['reserve_currency'] = cite(text, m, 0)

    pages = text.split('\x0c')
    tp = [i for i, pg in enumerate(pages, 1) if re.search(r'by asset class as of\s+the Report Dates', pg)]
    if not tp: return {**r, 'ok': False, 'error': '자산 종류별 표 쪽을 찾지 못함'}
    page = tp[-1]
    try:
        reads = [read_table(pdf, page, d) for d in DPIS]
    except ValueError as e:
        return {**r, 'ok': False, 'error': f'표 읽기 실패: {e}'}
    t = reads[0]
    key = lambda x: (x['circ'][0], x['fv'][0], [v for _, v, *_ in x['rows']])
    if any(key(x) != key(t) for x in reads[1:]):
        return {**r, 'ok': False, 'error': f'OCR {DPIS}dpi 판독 불일치 {[x["circ"][0] for x in reads]}/{[x["fv"][0] for x in reads]}'}
    r['circulation'], r['fair_value'] = t['circ'][0], t['fv'][0]
    # 글자 층에 같은 줄이 있으면(최근 보고서) OCR 값을 그것과 맞춰 본다.
    mt = re.search(r'(?:Outstanding Stablecoin Units|supply outstanding[^\n]*?)\s+[\d,]+\s+([\d,]+)\s*\n', pages[page - 1])
    if mt and int(mt[1].replace(',', '')) != r['circulation']:
        return {**r, 'ok': False, 'error': f'OCR 유통량 {r["circulation"]:,} != 글자 층 {mt[1]}'}
    sources['circulation'] = {'page': page, 'line': t['circ'][1], 'raw': t['circ'][2], 'ocr': True}
    sources['fair_value'] = {'page': page, 'line': t['fv'][1], 'raw': t['fv'][2], 'ocr': True}
    rows = t['rows']
    if len(rows) < 2: return {**r, 'ok': False, 'error': '표 줄 수 부족'}
    # 합계 줄: 'Total Market Value' 라벨 줄. 라벨이 지워진 달은 준비자산 총액과 같은 첫 줄(둘째 줄부터).
    ti = next((i for i, x in enumerate(rows) if re.search(r'total market value', x[0], re.I)), None)
    if ti is None:
        ti = next((i for i, x in enumerate(rows) if i > 0 and x[1] == r['fair_value']), None)
        if ti is not None: r.setdefault('flags', {})['total_row_unlabeled'] = True
    if ti is None: return {**r, 'ok': False, 'error': '합계 줄을 찾지 못함'}
    body, total = rows[:ti], rows[ti]
    has_cusip = t['cusip']
    try:
        comp = classify(body, has_cusip)
    except ValueError as e:
        return {**r, 'ok': False, 'error': str(e)}
    r['components'] = {k: sum(x['value'] for x in v) for k, v in comp.items()}
    comp_total = total[1]
    sources['components'] = {k: [{'page': page, 'line': x['line'], 'label': x['label'], 'raw': x['raw']} for x in v]
                              for k, v in comp.items() if v}
    sources['components']['total'] = {'page': page, 'line': total[2], 'label': total[0] or '(라벨 없음)', 'raw': total[3]}

    got = sum(r['components'].values())
    checks = {
        'components_sum': {'expected': comp_total, 'got': got, 'diff': got - comp_total},
        'total_equals_fair_value': {'expected': r['fair_value'], 'got': comp_total, 'diff': comp_total - r['fair_value']},
        'covers_circulation': {'surplus': r['fair_value'] - r['circulation'], 'ok': r['fair_value'] >= r['circulation']},
    }
    r['reconciliation'] = checks
    r['ok'] = checks['components_sum']['diff'] == 0 and checks['total_equals_fair_value']['diff'] == 0 and checks['covers_circulation']['ok']
    if r['ok']: r['coverage'] = round(r['fair_value'] / r['circulation'], 8)

    mo = re.search(r'In our opinion.*?\n\s*(' + DATE + r')\s*\n', text, re.S)
    r['attestation'] = {
        'type': 'examination' if re.search(r'We have examined', text) else None,
        'standard': 'AICPA attestation standards' if re.search(
            r'attestation\s+standards\s+established\s+by\s+the\s+(?:American\s+Institute\s+of\s+Certified\s+Public\s+Accountants|AICPA)', text) else None,
        'signed': to_iso(mo[1]) if mo else None,
        # 서명이 이미지라 글자 층에는 회계법인 이름이 대개 없다. 있으면 그대로 적는다.
        'firm': 'Deloitte & Touche LLP' if re.search(r'Deloitte & Touche LLP', text, re.I) else None,
    }
    if mo: sources['attestation.signed'] = cite(text, mo, 1)
    r.setdefault('flags', {}).update({'ocr_pages': [page], 'ocr_dpi_agree': list(DPIS), 'column_x_threshold': t['thr'],
                  'letterhead': 'bpm.com' if 'bpm.com' in text else ('deloitte.com' if 'deloitte' in text.lower() else None)})
    if any(x['label'] == '(라벨 없음)' for x in comp['other']): r['flags']['unlabeled_rows_in_other'] = True
    r['sources'] = sources
    if r['ok']: RAW[r['source_file']] = {'pdf': pdf, 'page': page, 'reads': reads, 'comp': comp, 'text': text, 'boxes': t['boxes']}
    return r


# ---- 규칙 입력값: 국채 CUSIP 줄(종목, 만기, 월말 금액)과 나머지 줄을 holdings로 ----
CUSIP = r'\b912\w{6}\b'
MON_NAMES = dict(MONTHS)
# OCR가 헷갈리는 글자(0과 O, 1과 T 등). CUSIP 검증 숫자(마지막 자리)로 후보를 거른다.
CONFUSED = {'0': 'OQDU', 'O': '0QDU', '1': 'ITLJ', 'I': '1', 'T': '17', '7': 'TJ', '5': 'S', 'S': '5', '2': 'ZQ', 'Z': '2',
            '8': 'B', 'B': '8', '6': 'G', 'G': '6', 'Q': '0O2', 'U': '0V', 'J': '1', 'L': '1'}
CANON = {'cash': 'Cash deposits held at U.S. regulated financial institutions', 'government_mmf': 'Government money-market funds'}
RAW = {}  # 파일 이름 -> parse가 남긴 OCR 줄, 쪽, 대사 구성(규칙 입력값 둘째 단계가 쓴다)


def cusip_ok(c):
    """CUSIP 검증 숫자(마지막 자리) 확인."""
    val = lambda ch: int(ch) if ch.isdigit() else ord(ch) - 55
    t = 0
    for i, ch in enumerate(c[:8]):
        v = val(ch) * (2 if i % 2 else 1)
        t += v // 10 + v % 10
    return c[8].isdigit() and (10 - t % 10) % 10 == int(c[8])


def cusip_candidates(raw):
    """OCR 글자를 한 자리 바꿔 검증 숫자가 맞는 CUSIP 후보(뒤 세 자리만 바꾼다. 앞 여섯 자리는 국채 발행 번호 912797 고정)."""
    out = set()
    for i in range(6, 9):
        for ch in CONFUSED.get(raw[i], ''):
            c = raw[:i] + ch + raw[i + 1:]
            if cusip_ok(c): out.add(c)
    return sorted(out)


def maturity_of(txt):
    """OCR 줄 글에서 만기일(ISO). 'September 3,2026', 'April9, 2026', '1/7/2025' 꼴을 받는다. 못 읽으면 None."""
    t = re.sub(CUSIP, '', txt)
    m = re.search(r'([A-Za-z]{3,9})\s*(\d{1,2})\s*[,.]?\s*(\d{4})', t)
    if m and m[1].lower() in MON_NAMES: return f'{m[3]}-{MON_NAMES[m[1].lower()]:02d}-{int(m[2]):02d}'
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', t)
    return f'{m[3]}-{int(m[1]):02d}-{int(m[2]):02d}' if m else None


def cusip_rows(lines, thr):
    """OCR 줄에서 CUSIP 줄 [{n, cusip, maturity, v=[첫째 칸, 둘째 칸], raw}]. 글자와 금액이 서로 다른 줄로 갈라진 줄은 이웃 금액 줄과 합친다."""
    info = []
    for n, ln in enumerate(lines, 1):
        txt = ' '.join(t for _, t in ln)
        am = [(x, amounts_of(m[0]), m[0].strip()) for x, t in ln for m in re.finditer(AMT, t)]
        rest = re.sub(r'[$:\-–—\s]', '', re.sub(AMT, '', txt))
        info.append({'n': n, 'txt': txt, 'cu': (re.search(CUSIP, txt) or [None])[0], 'am': am, 'only_amt': bool(am) and not rest})
    out, used = [], set()
    for i, x in enumerate(info):
        if not x['cu']: continue
        am, txt = x['am'], x['txt']
        if not am:
            for j in (i - 1, i + 1):
                if 0 <= j < len(info) and info[j]['only_amt'] and not info[j]['cu'] and j not in used:
                    am, txt = info[j]['am'], f"{x['txt']} {info[j]['txt']}"; used.add(j); break
        v = [0, 0]
        for xx, val, _ in am:
            c = 0 if xx < thr else 1
            if v[c]: raise ValueError(f'CUSIP 줄 한 칸에 금액이 둘: {txt}')
            v[c] = val
        out.append({'n': x['n'], 'cusip': x['cu'], 'maturity': maturity_of(x['txt']), 'v': v, 'raw': txt})
    return out


def label_near(lines, n):
    """금액만 읽힌 줄(쪽 안 줄 번호 n)의 라벨이 이웃 줄에 따로 읽혔으면 그 글."""
    for j in (n, n - 2):
        if 0 <= j < len(lines):
            t = ' '.join(x for _, x in lines[j])
            if re.search(r'accrued|timing|adjust', t, re.I) and not re.search(AMT, t): return t
    return None


ORG = r"\b(?:[A-Z][\w&.']*\s){0,4}(?:Bank|Bancorp|N\.A\.|Securities|Advisors|Asset Management|Trust Company|Trust, LLC)\b"
NAMES = ['BNY', 'Mellon', 'State Street', 'Citibank', 'Citi\\b', 'JPMorgan', 'Wells Fargo', 'Goldman', 'BlackRock', 'Fidelity', 'Signature',
         'Silvergate', 'Western Alliance', 'Flagstar', 'Cross River', 'Customers', 'Bank of']


def ocr_find(lines, pattern):
    """OCR 줄 목록에서 첫 일치의 줄 번호와 글."""
    for n, ln in enumerate(lines, 1):
        txt = ' '.join(t for _, t in ln)
        m = re.search(pattern, txt)
        if m: return n, m
    return None, None


def finalize_holdings(reports):
    """parse가 남긴 OCR 줄에서 보고서마다 holdings와 규칙 입력값을 채운다. CUSIP 표기는 모든 보고서의 판독을 모아 날짜별 다수결로 고른다."""
    votes = collections.defaultdict(collections.Counter)  # 만기일 -> {검증 숫자가 맞는 CUSIP: 표 수}
    rows_of = {}
    for r in reports:
        raw = RAW[r['source_file']]
        reads = []
        for d, rd in zip(DPIS, raw['reads']):
            reads.append(cusip_rows(rd['lines'], rd['thr']))
        # 두 해상도 판독이 같아야 한다(만기일, 금액). CUSIP 글자는 아래에서 다수결로 정한다.
        if [(x['maturity'], x['v']) for x in reads[0]] != [(x['maturity'], x['v']) for x in reads[1]]:
            raise ValueError(f"{r['month']}: CUSIP 줄 판독이 해상도마다 다름")
        for rd in reads:
            for x in rd:
                if x['maturity'] and cusip_ok(x['cusip']): votes[x['maturity']][x['cusip']] += 1
        rows_of[r['source_file']] = reads
    for r in reports:
        raw, reads = RAW[r['source_file']], rows_of[r['source_file']]
        as_of, page = r['as_of'], raw['page']
        hs = []
        for a, b in zip(*reads):
            if not b['v'][1]: continue  # 월말 칸에 금액 없음
            if not b['maturity']: raise ValueError(f"{r['month']}: 만기일을 못 읽음 {b['raw']}")
            c = votes[b['maturity']].most_common(1)
            if c: cusip, how = c[0][0], None
            else:  # 같은 만기가 다른 표에서 검증 숫자가 맞게 읽힌 적이 없으면 이 표의 두 판독에서 후보를 거른다.
                cs = {c for rr in (a, b) for c in ([rr['cusip']] if cusip_ok(rr['cusip']) else cusip_candidates(rr['cusip']))}
                cusip, how = (cs.pop(), 'repaired') if len(cs) == 1 else (b['cusip'], 'unverified')
            h = ri.holding('treasury_bill', b['v'][1], f'U.S. Treasury bill CUSIP {cusip}',
                           {'page': page, 'line': b['n'], 'raw': b['raw'], 'ocr': True}, as_of, b['maturity'])
            if how == 'unverified': h['cusip_unverified'] = True
            if how == 'repaired': h['cusip_repaired_from'] = b['cusip']  # OCR 글자가 검증 숫자에 안 맞아 한 자리 고친 것(후보가 하나뿐)
            hs.append(h)
        comp, lines = raw['comp'], raw['reads'][0]['lines']
        cusip_sum = sum(h['amount'] for h in hs)
        if cusip_sum != r['components']['treasury']: raise ValueError(f"{r['month']}: CUSIP 줄 합 {cusip_sum} != 국채 합계 {r['components']['treasury']}")
        if comp['repo']: raise ValueError(f"{r['month']}: 역레포 줄이 있음, kind를 정해야 함")
        for key, kind in (('cash', 'bank_deposit'), ('government_mmf', 'government_mmf'), ('other', 'settlement')):
            for x in comp[key]:
                lab = CANON.get(key, x['label'])  # OCR 오독('monev')을 피해 정해진 라벨을 쓴다. 원문 글은 where.raw에 있다.
                if lab == '(라벨 없음)':
                    lab = label_near(lines, x['line']) or lab
                if kind == 'settlement' and not re.search(r'accrued|timing|adjust', lab, re.I): raise ValueError(f"{r['month']}: 정산 줄로 볼 수 없는 라벨 {lab}")
                if x['value']:
                    hs.append(ri.holding(kind, x['value'], lab, {'page': page, 'line': x['line'], 'raw': x['raw'], 'ocr': True}, as_of))
        got = sum(h['amount'] for h in hs)
        chk = {'expected': r['fair_value'], 'got': got, 'diff': got - r['fair_value'],
               'treasury_rows_vs_total': {'cusip_rows_sum': cusip_sum, 'total_row': r['components']['treasury'], 'diff': cusip_sum - r['components']['treasury']}}
        if chk['diff']: raise ValueError(f"{r['month']}: holdings 합 != fair_value {chk}")
        r['holdings'], r['fund_holdings'], r['holdings_reconciliation'] = hs, [], chk
        d, notes = ri.derive(hs, [], as_of)
        r.update(d)
        text, ocr_lines = raw['text'], lines
        ocr_text = '\n'.join(' '.join(t for _, t in ln) for ln in ocr_lines)
        mm = next((h for h in hs if h['kind'] == 'government_mmf'), None)
        if mm:
            for k in ('treasury_max_maturity_days', 'repo_max_maturity_days'):
                if notes[k]['state'] == 'not_applicable':
                    notes[k]['note'] += f" 정부 MMF {mm['amount']:,}달러가 있으나 원문은 MMF 안 종목 목록을 싣지 않아 fund_holdings는 비워 둔다."
        # 6. 보고 주기
        rd = r['report_dates']
        if rd[0][:7] != rd[1][:7] or rd[1][:7] != r['month']: raise ValueError(f"{r['month']}: 보고 기준일 두 날이 같은 달이 아님 {rd}")
        mc = re.search(r'RLUSD\s+Reserves?\s+Report\s+([A-Z][a-z]+) (\d{4})', text)  # 표지 제목은 없는 보고서도 있다
        if mc and f'{mc[2]}-{MONTHS[mc[1].lower()]:02d}' != r['month']: raise ValueError(f"{r['month']}: 표지의 달이 기준일의 달과 다름")
        r['disclosure_cadence'], r['disclosure_cadence_days'] = 'monthly', 31
        notes['disclosure_cadence'] = ri.note('found', ri.find(text, r'as\s+of\s+[A-Z][a-z]+\s+\d{1,2},\s*\d{4},?\s+and\s+(?:as\s+of\s+)?[A-Z][a-z]+\s+\d{1,2},\s*\d{4}') or r['sources']['report_dates'][1],
            f"보고 기준일 두 날({rd[0]}, {rd[1]})이 같은 달이고 보고서 하나가 한 달을 다룬다" + (f"(표지 '{' '.join(mc[0].split())}')" if mc else '(이 보고서에는 표지 제목이 없음)')
            + f". 표본 {ri.consecutive_months(sorted(SRC.glob('Ripple_RLUSD_Examination_*.pdf')))}개월이 빠짐없이 이어짐.")
        # 7. 유통량 산정 방식
        pats = [r'Total RLUSD outstanding is defined as[^.]*\.', r'Outstanding Stablecoin Units means[^.]*\.']
        hit = next((p for p in pats if re.search(p, text)), None)
        if hit:
            # D-06: 무엇을 더하고 빼는지 밝혀야 공개. 정의 문장만으로는 공개가 아니다.
            r['circulation_formula_disclosed'] = False
            sen = re.sub(r'\s+', ' ', re.search(hit, text)[0])
            notes['circulation_formula_disclosed'] = ri.note('not_disclosed', ri.find(text, hit), f"정의 문장만 있고 무엇을 더하고 빼는지(발행, 상환과 소각, 동결 등)는 없다. D-06 기준으로 계산식 공개가 아님. 정의 문장: '{sen}'")
        else:
            r['circulation_formula_disclosed'] = False
            notes['circulation_formula_disclosed'] = ri.note('not_disclosed', None, ri.search_note(ri.hits(text, ['Outstanding Stablecoin Units means', 'defined as', 'burn', 'mint'])))
        # 8. 맡긴 기관 이름
        allt = text + '\n' + ocr_text
        orgs = sorted({re.sub(r'\s+', ' ', m.group(0)).strip() for m in re.finditer(ORG, re.sub(r'(?:Standard\s+)?Custody & Trust(?: Company)?(?:, LLC)?', ' ', allt))})
        nh = ri.hits(allt, NAMES + [('custodian', r'custodian')])
        names_found = [k for k, v in nh.items() if v and k != 'custodian']
        if orgs or names_found: raise ValueError(f"{r['month']}: 기관 이름 후보 {orgs} {names_found}, 수동 확인 필요")
        r['custodian_disclosure'], r['custodians'] = False, []
        kinds = [d for d, pt in (("'regulated financial institutions'", r'regulated financial institutions'),
                                 ("'depository institutions insured by the FDIC'", r'depository institutions (?:insured by|with deposits insured by)'),
                                 ("'asset custodians approved by DFS'", r'asset\s+custodians')) if re.search(pt, allt)]
        notes['custodian_disclosure'] = ri.note('not_disclosed', ri.find(text, r'regulated financial institutions') or ri.find(text, r'depository institutions'),
            f"준비자산을 맡긴 기관을 {', '.join(kinds)}처럼 종류로만 적고 이름은 없다"
            "(발행 법인 Standard Custody & Trust Company, LLC가 직접 쓴 이름이나 감사법인은 맡긴 기관이 아님). 이름 후보 검색(기관명 꼴 '... Bank/Securities/Advisors/Asset Management/N.A.'과 주요 은행 이름 17개, 본문과 표 OCR 모두)에서 0건. "
            + ri.search_note({'custodian': nh['custodian']}))
        # 9. 경영진 확인서
        sg = re.search(r'Jack McDonald\s*\n\s*(Chief Executive Officer)\s*\n\s*(Standard Custody & Trust[^\n]*)', text)
        src_page, ypt = None, None
        if sg:
            src_page = ri.find(text, r'Jack McDonald')['page']; y = ri.name_y(RAW[r['source_file']]['pdf'], src_page, 'McDonald'); ypt = y[0] if y else None
            where = ri.find(text, r'Jack McDonald\s*\n\s*Chief Executive Officer', flags=0)
        else:
            n, m = ocr_find(ocr_lines, r'Jack Mc\w+')
            if n:
                src_page = page; bx = [y for y, x, t in raw['boxes'] if re.search(r'Jack Mc\w+', t)]
                ypt = bx[-1] * 792
                where = {'page': page, 'line': n, 'raw': ' / '.join(' '.join(t for _, t in ocr_lines[k]) for k in (n - 1, n, n + 1) if k < len(ocr_lines)), 'ocr': True}
        asr = ri.find(text, r"(?:Management[’']s Assertion|The Company asserts)", re.I)
        if not (src_page and ypt and asr): raise ValueError(f"{r['month']}: 경영진 확인서나 서명 블록을 못 찾음")
        ink = ri.signature_ink(RAW[r['source_file']]['pdf'], src_page, ypt)
        if ink < 200: raise ValueError(f"{r['month']}: 서명 이미지 못 확인 {ink}")
        r['management_certification'], r['certifier'] = True, 'Chief Executive Officer'
        notes['management_certification'] = ri.note('found', where,
            f"쪽 {asr['page']}에 경영진 확인서('{asr['raw']}')가 있고 Chief Executive Officer(Standard Custody & Trust Company, LLC) 서명 블록(쪽 {src_page})과 서명 이미지가 있다(이름 줄 위 어두운 픽셀 {ink}개).")
        # 10. 상환 기한, 이자 지급
        hr = ri.hits(allt, ['redemption demands', 'redeemable', 'redeemed but not yet paid', ('within N days', r'within \w+ (?:business )?days?'), ('T+N', r'\bT\+\d')])
        where_of = {'redemption demands': "예금 한도 설명('anticipated redemption demands')", 'redeemable': "유통량 정의('redeemable')",
                    'redeemed but not yet paid': "정산 차이 설명('redeemed but not yet paid')"}
        seen = [where_of[k] for k in where_of if hr[k]]
        r['redemption_days'] = None
        notes['redemption_days'] = ri.note('not_in_report', ri.find(text, r'redemption demands|redeemable|redeemed but not yet paid'),
            "상환 기한(며칠 안에 상환)을 적은 문장이 없다. " + (f"상환은 {', '.join(seen)}에만 나온다. " if seen else "상환 낱말 자체가 거의 없다. ") + ri.search_note(hr))
        hi = ri.hits(allt, ['interest'])
        n, m = ocr_find(ocr_lines, r'(?i)accrued interest[^|]*')
        r['interest_paid'] = None
        notes['interest_paid'] = ri.note('not_in_report', ri.find(text, r'(?i)interest') or ({'page': page, 'line': n, 'raw': m.group(0).strip(), 'ocr': True} if n else None),
            "소유자에게 이자를 준다는 문장이 없다. " + ("'interest'는 준비자산 표의 'Accrued interest' 줄(준비금이 번 이자 수입, settlement로 분류)에만 나온다. " if hi['interest'] else "원문에 'interest' 낱말이 없다. ") + ri.search_note(hi))
        r['field_notes'] = {k: notes[k] for k in ri.FIELDS}


def main():
    reports, bad = [], []
    for p in sorted(SRC.glob('Ripple_RLUSD_Examination_*.pdf')):
        r = parse(p)
        reports.append(r)
        if r.get('ok'):
            print(f"ok  RLUSD {r['month']}  유통 {r['circulation']:,}  준비자산 {r['fair_value']:,}  "
                  f"커버리지 {r['coverage'] * 100:.4f}%  기준일 {r['as_of']}  서명 {r['attestation']['signed']}")
        else:
            bad.append(p.name)
            print(f"FAIL {p.name}: {r.get('error') or r.get('reconciliation')}")
        if VERBOSE: print('    ', json.dumps(r.get('components'), ensure_ascii=False), json.dumps(r.get('flags', {}), ensure_ascii=False))
    if not reports:
        print('PDF 없음:', SRC); return 1
    finalize_holdings([r for r in reports if r.get('ok')])
    excluded = [{'token': 'RLUSD', 'month': p.stem[-7:], 'source_file': f'data/samples/{p.name}',
                 'reason': str(r.get('error') or r.get('reconciliation'))}
                for p, r in zip(sorted(SRC.glob('Ripple_RLUSD_Examination_*.pdf')), reports) if not r.get('ok')]
    OUT.write_text(json.dumps({
        'generated': datetime.date.today().isoformat(),
        'source': 'Ripple RLUSD(발행 법인 Standard Custody & Trust Company, LLC) 월간 examination report, 표는 macOS Vision OCR, 글은 pdftotext -layout',
        'note': ('기준일은 월 중순과 월말 두 날이며 값은 월말(둘째 칸)을 쓴다. 표는 그림이라 OCR로 읽고 두 해상도 판독이 같을 때만 받는다. '
                 'components 매핑: cash=Cash deposits held at U.S. regulated financial institutions, '
                 'government_mmf=Government money-market funds, treasury=Total U.S. Treasury bills 또는 Subtotal(CUSIP별 줄 합계), '
                 'repo=역레포 줄(RLUSD 표에는 없음, 0), other=나머지 줄(Accrued interest and dividend income, Timing differences, '
                 'Adjustments due to timing 등. 음수 가능). sources.components에 키별 원문 줄(라벨, OCR 쪽 줄 번호, 원문 글)이 있다. '
                 'sources는 숫자별 {page, line, raw}. 대사 실패 보고서는 reports에서 제외하고 excluded에 이유를 남긴다. '
                 '규칙 입력값(holdings, fund_holdings, asset_types, treasury_max_maturity_days, treasury_maturity_basis, repo_max_maturity_days, '
                 'disclosure_cadence(_days), circulation_formula_disclosed, custodian_disclosure(custodians), management_certification(certifier), '
                 'redemption_days, interest_paid, field_notes)는 표의 CUSIP 줄(종목, 만기, 월말 금액)과 나머지 줄을 OCR로 읽은 것이다. 두 해상도(200, 300dpi) 판독의 만기일과 금액이 같을 때만 받고, '
                 'CUSIP 줄 월말 금액 합이 국채 합계 줄과 같아야 하며 holdings.amount 합은 fair_value와 같다(holdings_reconciliation). '
                 'CUSIP 글자는 OCR가 헷갈리는 자리(0과 O, T와 1 등)가 있어 검증 숫자가 맞는 판독의 만기일별 다수결로 정했다(맞는 판독이 없으면 cusip_unverified). '
                 'field_notes.state: found 원문에서 읽음, not_disclosed 공개 여부 항목이 원문에 없음, not_in_report 값이 원문에 없음, not_applicable 해당 자산 없음.'),
        'excluded': excluded,
        'reports': [r for r in reports if r.get('ok')],
    }, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n{len(reports)}건 중 성공 {len(reports) - len(bad)} → {OUT.relative_to(ROOT)}, 대사 실패 {len(bad)}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
