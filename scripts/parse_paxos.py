#!/usr/bin/env python3
"""Paxos (PYUSD, USDP, USDG) 검사보고서 PDF 파서.

data/samples/Paxos_{토큰}_Examination_*.pdf 를 읽어 data/reports_paxos.json 을 만든다.
출력 스키마는 data/reports.json(parse_circle.py)과 같은 항목 구성에 sources를 더했다.
합계 대사가 어긋나면 그 보고서를 결과에서 빼고 이유를 로그로 남긴다.

사용: python3 scripts/parse_paxos.py [--verbose]
"""
import json, re, subprocess, sys, pathlib, datetime, tempfile
from decimal import Decimal, ROUND_HALF_UP

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'samples'
OUT = ROOT / 'data' / 'reports_paxos.json'
VERBOSE = '--verbose' in sys.argv

MONTHS = {m: i for i, m in enumerate(
    'january february march april may june july august september october november december'.split(), 1)}

AMT = r'\$?\d{1,3}(?:,\d{3})+'
AMTZ = r'-|' + AMT

ISSUERS = {
    'PYUSD': 'Paxos Trust Company, National Association',
    'USDP': 'Paxos Trust Company, National Association',
    'USDG': 'Paxos Digital Singapore Pte. Ltd.',
}


def text_of(pdf):
    """pdftotext 결과. 글자가 하나도 없는 쪽(USDG 2026-01, 02는 5쪽부터 이미지)은 OCR로 채운다.
    쪽 구분(\\x0c)을 그대로 두므로 인용의 쪽 번호는 PDF 쪽과 같다."""
    # 함정: pdftotext를 스레드풀 안에서 부르면 빈 문자열이 나온다. 순차 호출만 쓴다.
    text = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
    # 2025-01 보고서는 글자마다 방향 표시(U+202D, U+202C)가 붙어 정규식이 깨지므로 뺀다. 줄바꿈이 아니라 쪽, 줄 인용은 그대로다.
    text = text.replace('\u202d', '').replace('\u202c', '')
    pages = text.split('\x0c')
    if pages[-1] == '': pages.pop()
    blank = [i for i, pg in enumerate(pages, 1) if not pg.strip() or garbled(pg)]
    if blank:
        for i, t in ocr_pages(pdf, blank).items():
            pages[i - 1] = t
    return '\x0c'.join(pages) + '\x0c', blank


def garbled(pg):
    """글자 층은 있지만 글꼴 인코딩이 깨져 쓸 수 없는 쪽(USDG 2025-09의 5~7쪽은 ASCII 밖 글자가 330개 넘음).
    ’ “ ” 같은 정상 기호는 세지 않고, 100개 이상일 때만 깨진 쪽으로 본다(정상 쪽 최대 23개)."""
    return sum(1 for c in pg if ord(c) > 127 and c not in "’“”‘●•–—§…·®™°") >= 100


def ocr_pages(pdf, pages):
    """쪽 번호 목록 -> {쪽: 줄 단위 글}. macOS Vision(scripts/ocr_vision.swift)을 쓴다.
    Vision은 칸 안의 '-'를 못 읽으므로 빈 금액 칸은 parse()가 따로 처리한다."""
    with tempfile.TemporaryDirectory() as tmp:
        imgs = {}
        for i in pages:
            prefix = pathlib.Path(tmp) / f'p{i}'
            subprocess.run(['pdftoppm', '-r', '200', '-png', '-f', str(i), '-l', str(i), '-singlefile',
                            str(pdf), str(prefix)], check=True)
            imgs[str(prefix) + '.png'] = i
        out = subprocess.run(['swift', str(ROOT / 'scripts' / 'ocr_vision.swift'), *imgs],
                             capture_output=True, text=True, check=True).stdout
    boxes, cur = {}, None
    for ln in out.splitlines():
        f = ln.split('\t', 2)
        if f[0] == '#': cur = imgs[f[1]]; boxes[cur] = []
        elif cur and len(f) == 3: boxes[cur].append((float(f[0]), float(f[1]), f[2]))
    return {i: boxes_to_lines(b) for i, b in boxes.items()}


def boxes_to_lines(boxes):
    """위쪽 y가 0.005 안으로 붙은 글상자를 한 줄로 묶고 왼쪽에서 오른쪽으로 잇는다(칸 사이는 공백 3개).
    표 한 행의 라벨과 금액이 같은 줄에 오도록 해 pdftotext -layout 출력과 같은 정규식을 쓴다."""
    lines, y0 = [], None
    for y, x, t in sorted(boxes):
        if y0 is None or y - y0 > 0.005:
            lines.append([]); y0 = y
        lines[-1].append((x, t))
    return '\n'.join('   '.join(t for _, t in sorted(ln)) for ln in lines)


def num(s):
    return int(s.replace('$', '').replace(',', ''))


def to_iso(s):
    """'August 25, 2026' 또는 '26 August 2026' -> '2026-08-25'"""
    s = s.strip()
    m = re.match(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', s)
    if m:
        mon, day, year = m.groups()
    else:
        m = re.match(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', s)
        if not m: return None
        day, mon, year = m.groups()
    i = MONTHS.get(mon.lower())
    return f'{year}-{i:02d}-{int(day):02d}' if i else None


def locate(text, pos):
    """문자 오프셋 pos가 pdftotext 출력의 몇 페이지 몇 줄인지. 폼피드(\\x0c)로 페이지를 나눈다."""
    upto = 0
    for pi, pg in enumerate(text.split('\x0c'), 1):
        end = upto + len(pg)
        if pos <= end:
            return pi, pg[:pos - upto].count('\n') + 1
        upto = end + 1  # 잘려나간 \x0c 한 글자
    return None, None


def cite(text, m, group=1):
    return {'page': locate(text, m.start(group))[0], 'line': locate(text, m.start(group))[1], 'raw': m.group(group)}


def two_after(full_text, slice_start, slice_text, anchor_pat, window=250):
    """anchor 뒤 window자 안에서 처음 나오는 금액 두 개. 같은 라벨이라도 줄바꿈 위치가
    보고서마다 달라(PYUSD는 라벨 뒤, USDP는 라벨 앞) 정확한 표 칸 대신 근접 탐색으로 잡는다.
    slice_text는 full_text의 부분 문자열이라 페이지/줄 인용은 slice_start를 더해 full_text 기준으로 낸다."""
    m = re.search(anchor_pat, slice_text)
    if not m: return None
    seg_start = m.end()
    seg = slice_text[seg_start:seg_start + window]
    nums = list(re.finditer(AMT, seg))
    if len(nums) < 2: return None
    a, b = nums[0], nums[1]
    def mk(mm):
        page, line = locate(full_text, slice_start + seg_start + mm.start())
        return {'page': page, 'line': line, 'raw': mm.group(0)}
    return num(a.group(0)), num(b.group(0)), mk(a), mk(b)


def find_signed(text):
    """검증인(KPMG) 서명일. 미국 사무소는 'New York, New York' 다음 줄, 싱가포르는
    'Chartered Accountants' 다음 'Singapore' 다음 줄에 날짜가 온다."""
    for pat in (r'New York, New York\s*\n\s*([A-Za-z]+ \d{1,2}, \d{4})',
                r'Chartered Accountants\s*\n+\s*(?:Singapore\s*\n+\s*)?(\d{1,2} [A-Za-z]+ \d{4})'):
        m = re.search(pat, text)
        if m:
            return to_iso(m.group(1)), cite(text, m, 1)
    return None, None


def issuer_of(text, token):
    """PDF에 적힌 발행 법인 이름 그대로(2025년 초까지 PYUSD, USDP는 'Paxos Trust Company, LLC', 이후 'National Association')."""
    m = re.search(r'Paxos Trust Company, (?:LLC|National Association)|Paxos Digital Singapore Pte\. Ltd\.', text)
    return m.group(0) if m else ISSUERS[token]


DATE = r'(?:[A-Za-z]+ \d{1,2},\s*\d{4}|\d{1,2} [A-Za-z]+ \d{4})'
AMTN = r'(?<![\w,.])\$?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?(?!\d|,\d)'   # 쉼표 없는 소액('$601')과 센트('.45')도 읽는다
SECTION_END = r'^\s*NOTES\b|To the best of the knowledge'


def amt_after(text, start, end, label, window=260):
    """text[start:end] 안에서 label 뒤 window자 안의 첫 금액 -> (Decimal, 인용). 라벨이 줄을 넘어가도
    금액은 라벨 줄 끝이나 다음 줄에 오므로 근접 탐색으로 잡는다(two_after와 같은 이유)."""
    m = re.search(label, text[start:end])
    if not m: return None
    pos = start + m.end()
    seg = text[pos:pos + window]
    # 금액 칸이 빈 줄(USDP 2024-09 월말 표의 역레포)은 다음 'Total' 줄의 금액을 가져오지 않도록 거기서 자른다.
    nxt = re.search(r'Total\b', seg)
    if nxt: seg = seg[:nxt.start()]
    a = re.search(AMTN, seg)
    if not a: return None
    page, line = locate(text, pos + a.start())
    return Decimal(a.group(0).replace('$', '').replace(',', '')), {'page': page, 'line': line, 'raw': a.group(0)}


def to_int(d):
    return int(d.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def parse_legacy(pdf, token, text, ocr):
    """Exhibit B가 없는 옛 형식(2023~2024년 PYUSD, USDP와 2024-10~2025-12 USDG).
    기준일 두 개의 표가 따로 있고 월말 기준일(두 번째)의 표만 읽는다. 구성 규칙:
    treasury=Total U.S. Treasury Bills(직접 보유 단기국채), repo=Total U.S. Government Guaranteed Debt Instruments
    Held Pursuant to Overnight Reverse Repurchase Agreements(역레포 담보 국채 합), cash=Total U.S. Dollars Held 또는
    Total Cash and Cash Equivalents(USDG는 구분 불가라 other), government_mmf=0(행 없음), other=0."""
    r = {'source_file': str(pdf.relative_to(ROOT)), 'issuer': issuer_of(text, token), 'token': token}
    sources = {}

    # 기준일: 'Report Dates' 표가 있으면 그것, 없으면(2023년) 표지의 'A and B at 5:00 PM'.
    m = re.search(rf'Report Dates\s+({DATE})\s+({DATE})', text) or \
        re.search(rf'({DATE}) and ({DATE}) at 5:00', text)
    if not m:
        return {**r, 'ok': False, 'error': '기준일 두 개를 찾지 못함'}
    d1raw, d2raw = m.group(1), m.group(2)
    r['report_dates'] = [to_iso(d1raw), to_iso(d2raw)]
    r['as_of'] = r['report_dates'][1]
    r['month'] = r['as_of'][:7]
    if token == 'USDG' and re.search(r'5:00\s*pm\s+SGT', text, re.I): r['as_of_time'] = '17:00 SGT'
    elif re.search(r'5:00\s*[Pp][Mm]\s*(?:ET|Eastern Time)', text): r['as_of_time'] = '17:00 ET'
    else: r['as_of_time'] = None
    sources['report_dates'] = [cite(text, m, 1), cite(text, m, 2)]
    m = re.search(r'Fair Value \(\$\)|U\.S\. Dollars Held|USD \d', text)
    r['reserve_currency'] = 'USD' if m else None
    if m: sources['reserve_currency'] = {'page': locate(text, m.start())[0], 'line': locate(text, m.start())[1], 'raw': m.group(0)}

    # 기준일 두 번째 표: 'D at 5:00 pm ET:' 제목 줄의 마지막 등장(첫 등장은 유통량 주장 쪽).
    heads = list(re.finditer(rf'^\s*(?:\S\s+)?{re.escape(d2raw)}(?: at 5:00\s*[pP][mM] (?:ET|SGT))?\s*:\s*$', text, re.M))
    head_mismatch = None
    if not heads:
        # USDP 2024-11은 표 제목 날짜가 옛 날짜(October 11/31)로 남아 있다. 'Description' 표 바로 앞의 마지막 날짜 제목을 쓴다.
        heads = list(re.finditer(rf'^\s*(?:\S\s+)?{DATE}(?: at 5:00\s*[pP][mM] (?:ET|SGT))?\s*:\s*$', text, re.M))
        if len(heads) < 2:
            return {**r, 'ok': False, 'error': '월말 기준일 표 제목을 찾지 못함'}
        head_mismatch = heads[-1].group(0).strip()
    s0 = heads[-1].end()
    mend = re.search(SECTION_END, text[s0:], re.M)
    s1 = s0 + mend.start() if mend else len(text)

    # 유통량: 표 행('tokens in circulation  A  B') 또는 2023년식 'N PYUSD' 줄(소수점 2자리 토큰 수).
    circ = None
    m = re.search(rf'tokens in circulation\s+({AMTN})\s+({AMTN})', text)
    if m:
        circ = (Decimal(m.group(2).replace(',', '')), cite(text, m, 2))
    else:
        ms = list(re.finditer(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+(?:PYUSD|USDP)\b', text))
        if len(ms) >= 2:
            circ = (Decimal(ms[1].group(1).replace(',', '')), cite(text, ms[1], 1))
    if not circ:
        return {**r, 'ok': False, 'error': '유통량을 찾지 못함'}
    circ_exact = circ[0]
    r['circulation'] = to_int(circ_exact)
    sources['circulation'] = circ[1]

    parts = {
        'treasury': amt_after(text, s0, s1, r'Total (?:U\.?S\.? )?Treasury [Bb]ills?:?'),
        'repo': amt_after(text, s0, s1, r'Total U\.?S\.? Government Guaranteed Debt Instruments Held Pursuant'),
        'cash': amt_after(text, s0, s1, r'Total U\.S\. Dollars Held:?|Total Cash and Cash Equivalents:?'),
    }
    tot = amt_after(text, s0, s1, r'Total (?:Assets Held in (?:Reserve Accounts|Redemption Assets)|(?:Fair Value )?of Redemption Assets|Fair Value of Redemption Assets):?')
    if not tot or not parts['cash']:
        return {**r, 'ok': False, 'error': '표의 합계 줄(현금, 총계)을 찾지 못함'}
    r['components'] = {'cash': to_int(parts['cash'][0]), 'repo': to_int(parts['repo'][0]) if parts['repo'] else 0,
                       'government_mmf': 0,
                       'treasury': to_int(parts['treasury'][0]) if parts['treasury'] else 0, 'other': 0}
    if token == 'USDG':
        # 'Total Cash and Cash Equivalents'는 은행 예금, MMF, 레포가 나뉘지 않은 한 줄이다(2026-01 이후 Exhibit B에서 Cash와 MMF로 갈라지며
        # 합계 12.6억 달러가 Cash 1.2억과 MMF 10.9억으로 나뉜 것이 같은 줄에 MMF가 섞여 있었다는 정황). cash는 은행 예금만이라는 정의를 지키려고
        # 이 줄 전체를 other(구분 불가)에 두고, 은행 예금은 0이 아니라 알 수 없음(None)으로 둔다.
        r['components']['other'] = r['components']['cash']; r['components']['cash'] = None
    sources['components'] = {k: v[1] for k, v in parts.items() if v}
    sources['components']['total'] = tot[1]
    components_total = to_int(tot[0])

    # 머리표의 준비자산 총액(2024년식)이 있으면 표 총계와 같아야 한다. 없으면(2023년식) 표 총계가 준비자산 총액이다.
    fv = two_after(text, 0, text, r'Fair Value of Redemption(?! Assets:)')
    if fv:
        r['fair_value'] = fv[1]; sources['fair_value'] = fv[3]
    else:
        r['fair_value'] = components_total; sources['fair_value'] = tot[1]

    # 유통량 두 번째 출처(주석 2 '... equal to or greater than $A and $B')와 맞아야 한다. OCR 오독을 잡는 용도.
    note_ok = True
    m = re.search(rf'equal to or greater than\s+(?:USD |\$)\s?({AMTN})\s+and\s+(?:USD |\$)\s?({AMTN})', text)
    if m:
        note_ok = Decimal(m.group(2).replace(',', '')) == circ_exact
        sources['circulation_note'] = cite(text, m, 2)
    note_gap = not note_ok
    # 글자 층이 있는 보고서는 원문 안의 두 숫자가 어긋나도(PYUSD 2024-04: 표 328,083,118, 주석 328,083,103) 표 값을 쓰고
    # flags로만 알린다. OCR한 쪽이 있으면 오독을 잡아야 하므로 어긋남을 대사 실패로 본다.
    if not ocr: note_ok = True

    csum = sum(v or 0 for v in r['components'].values())
    # 원문은 줄마다 달러 단위로 반올림해 적어 부분 합이 총계와 1달러 어긋나는 보고서가 있다(2023-09, 2024-01 등).
    # 총계가 머리표와 같고 어긋남이 2달러 이하일 때만 그 차액을 other에 두고 flags.rounding_residual로 표시한다.
    residual = 0
    if components_total == r['fair_value'] and 0 < abs(components_total - csum) <= 2:
        residual = components_total - csum
        r['components']['other'] += residual  # USDG 옛 형식은 other에 현금성 줄이 이미 있다
        csum += residual
    checks = {
        'components_sum': {'expected': components_total, 'got': csum, 'diff': csum - components_total},
        'total_equals_fair_value': {'expected': r['fair_value'], 'got': components_total, 'diff': components_total - r['fair_value']},
        'covers_circulation': {'surplus': r['fair_value'] - r['circulation'], 'ok': Decimal(r['fair_value']) >= circ_exact},
        'circulation_matches_note': {'ok': note_ok},
    }
    r['reconciliation'] = checks
    r['ok'] = (checks['components_sum']['diff'] == 0 and checks['total_equals_fair_value']['diff'] == 0
               and checks['covers_circulation']['ok'] and note_ok and r['month'] == pdf.stem[-7:])
    if r['month'] != pdf.stem[-7:]: checks['file_month'] = {'ok': False, 'file': pdf.stem[-7:], 'as_of_month': r['month']}
    if r['ok']:
        r['coverage'] = round(r['fair_value'] / r['circulation'], 8)

    # 검증 의견: 미국 사무소는 의견 문단 끝 'in all material respects.' 다음 줄, 싱가포르는 'Singapore, D'.
    m = re.search(r'in all material respects\.\s*\n(?:\s*\n)*\s*([A-Z][a-z]+ \d{1,2}, \d{4})', text) or \
        re.search(r'Singapore,\s*(\d{1,2} [A-Za-z]+ \d{4})', text)
    signed = to_iso(m.group(1)) if m else None
    if m: sources['attestation.signed'] = cite(text, m, 1)
    if re.search(r'Singapore\s+Standard\s+on\s+Assurance\s+Engagements\s+\(SSAE\)\s+3000', text):
        standard = 'Singapore Standard on Assurance Engagements 3000 (SSAE 3000)'
    elif re.search(r'attestation\s+standards\s+established\s+by\s+the\s+American\s+Institute\s+of\s+Certified\s+Public\s+Accountants', text):
        standard = 'AICPA attestation standards'
    else:
        standard = None
    # firm: 2023~2024년 PYUSD, USDP는 로고와 서명이 이미지뿐이라 글자로 안 나온다(눈으로는 WithumSmith+Brown, PC). 글자가 없으면 null.
    mf = re.search(r'KPMG LLP|Enrome LLP', text) or re.search(r'ENROME LLP', text)
    r['attestation'] = {
        'type': 'examination' if re.search(r'We have examined|Our examination was conducted', text) else None,
        'standard': standard, 'signed': signed,
        'firm': ('Enrome LLP' if mf.group(0) == 'ENROME LLP' else mf.group(0)) if mf else None,
    }
    r['flags'] = {'scan_suspected': len(text.strip()) < 2000, 'layout': 'legacy', 'rounding_residual': residual,
                  'circulation_decimals': circ_exact != circ_exact.to_integral_value(),
                  'firm_signature_image': mf is None}
    if token == 'USDG':
        # USDG 옛 형식의 'Total Cash and Cash Equivalents'는 은행 예금만이 아니라 현금성 자산 전체다. 원문에 은행 예금, MMF, 레포 구분이
        # 없어 금액을 나눌 수 없으므로 값은 그대로 cash에 두고 '은행 예금만'이 아님을 flags로 표시한다(repo, government_mmf의 0은 구분 없음).
        r['flags'].update({'cash_is_bank_deposit': False, 'cash_line_label': 'Total Cash and Cash Equivalents',
                           'repo_mmf_not_split': True, 'cash_equivalents_in_other': r['components']['other']})
        mc = re.search(r'custodied Redemption Assets at(.+?)\n\s*To the best', text, re.S)
        if mc: r['flags']['cash_custodians_note5'] = ' '.join(mc.group(1).split()).rstrip('.')  # 2025-09 이후만. Dreyfus(자산운용사)가 있어 MMF 가능성
    if note_gap: r['flags']['circulation_note_mismatch'] = sources['circulation_note']['raw']
    if head_mismatch: r['flags']['table_heading_date_mismatch'] = head_mismatch
    if ocr: r['flags']['ocr_pages'] = ocr
    r['sources'] = sources
    return r


def parse(pdf, token):
    text, ocr = text_of(pdf)
    r = parse_base(pdf, token, text, ocr)
    if r.get('ok'): r.update(rule_inputs(r, text))   # 기존 필드는 그대로 두고 규칙 입력값만 더한다
    return r


def parse_base(pdf, token, text, ocr):
    if 'Exhibit B: Composition of Redemption Assets by Asset Type' not in text:
        return parse_legacy(pdf, token, text, ocr)
    r = {'source_file': str(pdf.relative_to(ROOT)), 'issuer': issuer_of(text, token), 'token': token}
    sources = {}

    m = re.search(r'Report Dates\s+([A-Za-z]+ \d{1,2},\s*\d{4})\s+([A-Za-z]+ \d{1,2},\s*\d{4})', text)
    if not m:
        return {**r, 'ok': False, 'error': 'Report Dates 줄을 찾지 못함'}
    r['report_dates'] = [to_iso(m.group(1)), to_iso(m.group(2))]
    r['as_of'] = r['report_dates'][1]
    r['month'] = r['as_of'][:7]
    r['as_of_time'] = '17:00 ET' if re.search(r'5:00\s*[Pp][Mm].*Eastern Time', text) else None
    sources['report_dates'] = [cite(text, m, 1), cite(text, m, 2)]
    m = re.search(r'redemption assets by asset type in (United States Dollar)', text)
    r['reserve_currency'] = 'USD' if m else None
    if m: sources['reserve_currency'] = cite(text, m, 1)

    # 제목 줄 'Summary' 뒤 각주 번호 1을 OCR는 '!' 같은 글자로 읽거나 빠뜨린다.
    ms = re.search(r'^\s*Summary\S?\s*$', text, re.M)
    if not ms:
        return {**r, 'ok': False, 'error': 'Summary 절을 찾지 못함'}
    summary_start = ms.start()
    summary_end = text.find('To the best of the knowledge', summary_start)
    summary = text[summary_start:summary_end if summary_end != -1 else len(text)]
    circ = two_after(text, summary_start, summary, r'Total \w+ redeemable tokens')
    fv = two_after(text, summary_start, summary, r'Total redemption assets in United')
    if not circ or not fv:
        return {**r, 'ok': False, 'error': 'Summary 표(유통량, 준비자산 총액)를 찾지 못함'}
    r['circulation'] = circ[1]
    r['fair_value'] = fv[1]
    sources['circulation'] = circ[3]
    sources['fair_value'] = fv[3]

    exb_marker = 'Exhibit B: Composition of Redemption Assets by Asset Type'
    exb_start = text.find(exb_marker)
    if exb_start == -1:
        return {**r, 'ok': False, 'error': 'Exhibit B를 찾지 못함'}
    exb_end = text.find('The redemption assets included in this Exhibit B relate to', exb_start)
    exb = text[exb_start:exb_end if exb_end != -1 else len(text)]
    # USDP 2025-04 repo 첫 칸 금액 뒤에 오타 마침표('$12,452,000.')가 있어 허용한다.
    pairs = list(re.finditer(rf'({AMTZ})\.?\s+({AMTZ})\s*$', exb, re.M))
    rows = [(mm.group(2), exb_start + mm.start(2)) for mm in pairs]
    # OCR는 빈 칸의 '-'를 못 읽어 repo 행이 통째로 빠진다. 라벨 줄에 금액이 없으면 0으로 본다.
    repo = re.search(r'^\s*Repurchase agreements[^\d$\n]*$', exb, re.M)
    if len(rows) == 4 and ocr and repo:
        rows.insert(2, ('-', exb_start + repo.start()))
    if len(rows) != 5:
        return {**r, 'ok': False, 'error': f'Exhibit B 행 수 불일치(5개 기대, {len(rows)}개 발견)'}
    def val(row):
        return 0 if row[0] == '-' else num(row[0])
    cash, ggmf, repo, treas, total = rows
    r['components'] = {'cash': val(cash), 'government_mmf': val(ggmf),
                        'repo': val(repo), 'treasury': val(treas)}  # Exhibit B는 4행뿐이라 other 키가 없다(2026년 출력 유지)
    components_total = val(total)
    sources['components'] = {}
    for k, (raw, pos) in zip(['cash', 'government_mmf', 'repo', 'treasury', 'total'], rows):
        page, line = locate(text, pos)
        sources['components'][k] = {'page': page, 'line': line, 'raw': raw}

    checks = {
        'components_sum': {'expected': components_total,
                            'got': sum(r['components'].values()),
                            'diff': sum(r['components'].values()) - components_total},
        'total_equals_fair_value': {'expected': r['fair_value'], 'got': components_total,
                                     'diff': components_total - r['fair_value']},
        'covers_circulation': {'surplus': r['fair_value'] - r['circulation'],
                                'ok': r['fair_value'] >= r['circulation']},
    }
    r['reconciliation'] = checks
    r['ok'] = (checks['components_sum']['diff'] == 0 and checks['total_equals_fair_value']['diff'] == 0
               and checks['covers_circulation']['ok'])
    if r['ok']:
        r['coverage'] = round(r['fair_value'] / r['circulation'], 8)

    signed, signed_cite = find_signed(text)
    # 함정: USDG 보고서에도 각주에 'Independent Accountants’ Examination Report'가 있어 제목 문구를 먼저 본다.
    if 'Independent reasonable assurance report' in text:
        atype = 'reasonable assurance'
    elif 'Independent Accountants’ Examination Report' in text or 'We have examined management' in text:
        atype = 'examination'
    else:
        atype = None
    if 'attestation standards established by the American Institute of Certified Public Accountants' in text:
        standard = 'AICPA attestation standards'
    elif 'Singapore Standard on Assurance Engagements 3000' in text:
        standard = 'Singapore Standard on Assurance Engagements 3000 (SSAE 3000)'
    else:
        standard = None
    r['attestation'] = {
        'type': atype, 'standard': standard, 'signed': signed,
        'firm': 'KPMG LLP' if 'KPMG LLP' in text else None,
    }
    if signed_cite: sources['attestation.signed'] = signed_cite

    r['flags'] = {
        'scan_suspected': len(text.strip()) < 2000,
        # 함정: 유통량/준비자산 총액 줄바꿈 순서가 토큰마다 다르다(PYUSD=라벨 뒤 숫자, USDP=라벨 앞 숫자).
        # two_after()가 근접 탐색으로 흡수하므로 파서는 안 깨지지만, 표 구조가 또 바뀌면 여기부터 의심한다.
    }
    if ocr: r['flags']['ocr_pages'] = ocr  # 글자 층이 없어 OCR로 읽은 쪽. 값은 합계 대사로만 검증된다.
    r['sources'] = sources
    return r


# ---------------------------------------------------------------------------------------------------------------------
# 규칙 입력값: 준비자산 줄 단위 목록(holdings)과 판정기가 쓰는 만기, 공시 주기, 공시 여부 필드.
# 금액은 위 parse가 이미 검증한 components를 그대로 쓰고(바꾸지 않음), 여기서는 줄 이름, 만기, 출처 쪽과 줄을 원문에서 읽어 붙인다.
# ---------------------------------------------------------------------------------------------------------------------
DT = r'\d{1,2}/\d{1,2}/(?:\d{4}|\d{2})'
MONEY = r'\$?\s?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
TITLES = r'Acting Executive Director|Executive Director|Head of Treasury and Portfolio Management|Head of Portfolio Management|Controller|Head of EU'


def to_date(s):
    """'08/15/24', '8/11/2026' -> datetime.date. 두 자리 연도는 2000년대로 읽는다(원문은 2023~2026년 보고서뿐)."""
    mo, dd, yy = (int(x) for x in s.split('/'))
    return datetime.date(yy + 2000 if yy < 100 else yy, mo, dd)


def at(text, pos, raw):
    page, line = locate(text, pos)
    return {'page': page, 'line': line, 'raw': raw}


def money(s):
    return Decimal(re.sub(r'[$\s,]', '', s))


def rows_with_date(text, s0, s1, row_start):
    """text[s0:s1]에서 row_start(정규식, 줄 시작 라벨)로 시작하는 줄마다 (줄 위치, 줄 글, 줄 번호) 목록. 줄이 나뉜 표(PYUSD 국채표)는
    숫자가 든 줄만 남기도록 날짜가 있는 줄만 고른다."""
    out = []
    for m in re.finditer(row_start, text[s0:s1], re.M):
        a = s0 + m.start()
        e = text.find('\n', a); e = e if e != -1 else len(text)
        out.append((a, text[a:e]))
    return out


def legacy_region(text, d2raw):
    """parse_legacy가 읽은 월말 기준일 표의 [시작, 끝) 위치. 제목 줄 찾는 방식은 parse_legacy와 같다."""
    heads = list(re.finditer(rf'^\s*(?:\S\s+)?{re.escape(d2raw)}(?: at 5:00\s*[pP][mM] (?:ET|SGT))?\s*:\s*$', text, re.M)) or \
        list(re.finditer(rf'^\s*(?:\S\s+)?{DATE}(?: at 5:00\s*[pP][mM] (?:ET|SGT))?\s*:\s*$', text, re.M))
    s0 = heads[-1].end()
    mend = re.search(SECTION_END, text[s0:], re.M)
    return s0, (s0 + mend.start() if mend else len(text))


def legacy_items(text, s0, s1, as_of):
    """옛 형식 표의 종목 줄(U.S. Treasury Bills/Bonds/Debt)을 읽어 (묶음, 종목) 목록으로 낸다. 묶음은 'Total U.S. Treasury Bills' 앞의 줄=bills(직접 보유),
    그 뒤 줄=collateral(역레포 담보). 종목 줄은 라벨, (CUSIP), 만기일, 금액이 한 줄에 있다(USDG는 CUSIP이 다음 줄에 올 때도 있음)."""
    mb = re.search(r'Total (?:U\.?S\.? )?Treasury [Bb]ills?:?', text[s0:s1])
    bills_end = s0 + mb.start() if mb else s0
    items = []
    for a, line in rows_with_date(text, s0, s1, r'^[ \t]*(?:\S[ \t]+)?U\.?S\.?[ \t]*Treasury[ \t]+(?:Bills?|Bonds?|Debt|Notes?)\b'):
        kind = re.search(r'Bills?|Bonds?|Debt|Notes?', line).group(0)
        d = re.search(DT, line)
        if not d: items.append({'type': kind, 'maturity': None, 'pos': a, 'raw': line.strip()}); continue
        amt = re.search(AMTN, line[d.end():])
        nxt = text[a + len(line) + 1:a + len(line) + 80].split('\n')[0].strip()
        cusip = re.search(r'\b9[0-9A-Z]{8,11}\b', line) or re.fullmatch(r'(9[0-9A-Z]{8,11})', nxt)
        mat = to_date(d.group(0))
        items.append({'type': 'Bills' if kind.startswith('Bill') else kind, 'id': cusip.group(0) if cusip else None,
                      'maturity': mat.isoformat(), 'days': (mat - as_of).days,
                      'amount': float(money(amt.group(0).replace('$', ''))) if amt else None,
                      'pos': a, 'raw': d.group(0), 'group': 'bills' if a < bills_end else 'collateral'})
    return items


def exhibit_region(text, start_pat, as_of_iso, total_pat, window_after=None):
    """Exhibit B 안에서 '<제목> as of <기준일>' 표(기준일이 월말 기준일인 것)의 [시작, 끝) 위치. 제목 날짜는 영어 월 표기."""
    exb = text.find('Exhibit B: Composition of Redemption Assets by Asset Type')
    mc = re.search(r'Exhibit C:\s*Comparison', text[exb:])
    end = exb + mc.start() if mc else len(text)
    for m in re.finditer(start_pat + r'\s+as of\s+([A-Za-z]+ \d{1,2},\s*\d{4})', text[exb:end], re.I):
        if to_iso(m.group(1)) == as_of_iso:
            a = exb + m.end()
            t = re.search(total_pat, text[a:end], re.I)
            return a, (a + t.end() if t else end)
    return None


def exhibit_rows(text, a, b):
    """text[a:b] 안에서 날짜가 든 줄마다 (줄 위치, 줄 글)."""
    return [(a + m.start(), m.group(0)) for m in re.finditer(r'^[^\n]*\b' + DT + r'[^\n]*$', text[a:b], re.M)]


def sum_diff(items, total, tol=2):
    s = sum(i['amount'] or 0 for i in items)
    return abs(s - float(total)) <= tol, s


def sig_block(text):
    """서명 문단('To the best of the knowledge and belief of the undersigned ...')과 그 뒤 서명란. 서명란이 다음 쪽에 있는 보고서(PYUSD 2024-06)가 있어
    다음 절 제목(Notes, Exhibit A)이나 1500자 앞까지 본다. OCR이 belief를 beliet로 읽은 쪽(USDG 2025-03)도 잡도록 철자를 느슨하게 둔다."""
    m = re.search(r'To the best of the knowledge and belie\w+ of the undersigned', text)
    if not m: return None, ''
    blk = text[m.start():m.start() + 1500]
    cut = re.search(r'Notes to the (?:Redemption|Reserve)|Exhibit A:', blk)
    return m, blk[:cut.start()] if cut else blk


def rule_inputs(r, text):
    """보고서 하나의 규칙 입력값. 반환 필드는 모두 새 키이며 r의 기존 값은 읽기만 한다."""
    token, as_of_iso = r['token'], r['as_of']
    as_of = datetime.date.fromisoformat(as_of_iso)
    comp, src, flags = r['components'], r['sources']['components'], r['flags']
    legacy = flags.get('layout') == 'legacy'
    holdings, notes, warn = [], {}, []

    def H(kind, amount, label, where, maturity_max_days=None, maturity_listed=False, **extra):
        holdings.append({'kind': kind, 'amount': amount, 'currency': r.get('reserve_currency') or 'USD', 'maturity_max_days': maturity_max_days,
                         'maturity_listed': maturity_listed, 'label': label, 'where': where, **extra})
        return holdings[-1]

    def latest(items):
        it = max(items, key=lambda i: i['maturity'])
        return it, {'page': locate(text, it['pos'])[0], 'line': locate(text, it['pos'])[1], 'raw': it['raw']}

    def clean(items):
        return [{k: v for k, v in i.items() if k not in ('pos', 'raw', 'group')} for i in items]

    # ---- 1) holdings, 4) 국채 만기, 5) 역레포 만기 -------------------------------------------------------------------
    tmax = rmax = None            # (일수, 인용, 설명)
    if legacy:
        d2raw = r['sources']['report_dates'][1]['raw']
        s0, s1 = legacy_region(text, d2raw)
        its = legacy_items(text, s0, s1, as_of)
        bills = [i for i in its if i['group'] == 'bills']; coll = [i for i in its if i['group'] == 'collateral']
        if any(i['type'] != 'Bills' for i in bills) or any(i['type'] == 'Bills' for i in coll): warn.append('국채 줄 묶음 어긋남')
        if any(i['maturity'] is None for i in its): warn.append('만기 없는 종목 줄')
        residual = flags.get('rounding_residual') or 0
        if token == 'USDG':
            H('cash_equivalents_unsplit', comp['other'] - residual, 'Total Cash and Cash Equivalents', src['cash'])
        elif comp['cash']:
            H('bank_deposit', comp['cash'], 'Total U.S. Dollars Held', src['cash'])
        if comp['treasury']:
            ok, ssum = sum_diff(bills, comp['treasury'])
            if not ok: warn.append(f'국채 종목 합 {ssum} != 줄 합계 {comp["treasury"]}')
            it, c = latest(bills)
            H('treasury_bill', comp['treasury'], 'Total U.S. Treasury Bills', src['treasury'], it['days'], True, items=clean(bills),
              maturity_date=it['maturity'])
            tmax = (it['days'], c, f'직접 보유 단기국채 {len(bills)}종 중 최장 만기 {it["maturity"]}({it["id"]})')
        if comp['repo']:
            ok, ssum = sum_diff(coll, comp['repo'])
            if not ok: warn.append(f'담보 종목 합 {ssum} != 줄 합계 {comp["repo"]}')
            lab = 'Total U.S. Government Guaranteed Debt Instruments Held Pursuant to Overnight Reverse Repurchase Agreements'
            H('reverse_repo_overnight', comp['repo'], lab, src['repo'], 1, True, items=clean(coll),
              collateral_max_maturity_days=max(i['days'] for i in coll) if coll else None)
            rmax = (1, src['repo'], '표 제목이 Overnight Reverse Repurchase Agreements(하루짜리). 종목 줄의 만기일은 역레포 담보 국채의 만기이지 역레포 만기가 아님')
        if residual:
            H('settlement', residual, '원문 줄 합계와 표 총계의 반올림 차이(줄마다 달러 단위로 반올림)', src['total'])
        mmf_total = 0
    else:
        mmf = comp['government_mmf']
        if comp['cash']:
            H('bank_deposit', comp['cash'], 'Cash', src['cash'])
        if mmf:
            H('government_mmf', mmf, 'Government money market funds, at net asset value', src['government_mmf'])
        if comp['repo']:
            reg = exhibit_region(text, r'Repurchase Agreements', as_of_iso, r'Total Repurchase Agreements')
            items = []
            if reg:
                for a, line in exhibit_rows(text, reg[0], reg[1]):
                    ds = re.findall(DT, line)
                    am = re.findall(r'\$\s?[\d,]+', line)
                    if len(ds) >= 2 and am:
                        pm, mt = to_date(ds[0]), to_date(ds[1])
                        items.append({'purchase': pm.isoformat(), 'maturity': mt.isoformat(), 'days': (mt - as_of).days,
                                      'amount': float(money(am[-1])), 'pos': a, 'raw': ds[1]})
            if not items: warn.append('역레포 표 행을 못 읽음')
            ok, ssum = sum_diff(items, comp['repo'], 0)
            if not ok: warn.append(f'역레포 행 합 {ssum} != {comp["repo"]}')
            # 하루짜리 판정: 매수일이 기준일이고 만기일이 그 뒤 첫 영업일(주말 사이는 달력일 3일, 휴일이 낀 연휴는 4일까지 본다)
            if any(i['purchase'] != as_of_iso or not (0 < i['days'] <= 4) or to_date(i['raw']).weekday() >= 5 for i in items):
                warn.append('하루짜리가 아닌 역레포 행')
            c = at(text, items[0]['pos'], items[0]['raw']) if items else src['repo']
            H('reverse_repo_overnight', comp['repo'], 'Repurchase agreements, at fair value', src['repo'], 1, True, items=clean(items))
            rmax = (1, c, '본문이 "the repurchase agreements mature overnight"이라 하고 표의 매수일=기준일, 만기일=다음 영업일(' + ', '.join(sorted({i['maturity'] for i in items})) + ')')
        if comp['treasury']:
            reg = exhibit_region(text, r'Treasury bills', as_of_iso, r'Total Treasury bills')
            items = []
            if reg:
                for a, line in exhibit_rows(text, reg[0], reg[1]):
                    d = re.search(DT, line)
                    am = re.findall(r'\$\s?[\d,]+(?:\.\d+)?', line[d.end():])
                    # CUSIP이 같은 줄에 없으면(은행 이름이 줄을 나눈 PYUSD 표, OCR가 줄을 어긋나게 읽은 USDG 표) 다음 줄을 본다.
                    nxt = text[a + len(line) + 1:a + len(line) + 120].split('\n')[0]
                    cusip = re.search(r'\b(?:US)?(9[0-9A-Z]{8,11})\b', line) or re.search(r'\b(?:US)?(9[0-9A-Z]{8,11})\b', nxt)
                    mt = to_date(d.group(0))
                    items.append({'id': cusip.group(1) if cusip else None, 'maturity': mt.isoformat(), 'days': (mt - as_of).days,
                                  'amount': float(money(am[-1])) if am else None, 'pos': a, 'raw': d.group(0)})
            if not items: warn.append('국채 표 행을 못 읽음')
            ok, ssum = sum_diff(items, comp['treasury'], 2)
            if not ok and not flags.get('ocr_pages'): warn.append(f'국채 행 합 {ssum} != {comp["treasury"]}')
            xnote = ''
            if not ok:
                xnote = ' OCR가 한 종목의 금액을 윗줄에 붙여 읽어 종목별 금액 합이 줄 합계와 맞지 않아 종목 금액은 싣지 않고 만기일만 이미지와 대조해 확인함.'
                for i in items: i['amount'] = None   # OCR가 한 종목의 금액을 윗줄에 붙여 읽어 줄별 금액을 믿을 수 없음. 만기일은 이미지와 대조해 확인
            it, c = latest(items)
            H('treasury_bill', comp['treasury'], 'Obligations of U.S. Treasury, at fair value', src['treasury'], it['days'], True, items=clean(items),
              maturity_date=it['maturity'])
            tmax = (it['days'], c, f'Treasury bills {len(items)}줄 중 최장 만기 {it["maturity"]}({it["id"]}). 본문은 3개월 이하 국채만 보유한다고 적음.' + xnote)
        mmf_total = mmf
        if mmf:
            mi = mmf_items(text, as_of_iso)
            if not sum_diff(mi, mmf, 0)[0]: warn.append('MMF 표 합이 줄 합계와 다름')
            holdings[[h['kind'] for h in holdings].index('government_mmf')]['items'] = mi

    # 대사: holdings amount 합 = fair_value
    hsum = sum(h['amount'] for h in holdings)
    if hsum != r['fair_value']: warn.append(f'holdings 합 {hsum} != fair_value {r["fair_value"]}')
    kinds = sorted({h['kind'] for h in holdings if h['kind'] != 'settlement' and h['amount'] > 0})

    # ---- 4) 국채 만기 필드 ---------------------------------------------------------------------------------------------
    unsplit = any(h['kind'] == 'cash_equivalents_unsplit' for h in holdings)
    if tmax:
        extra = ''
        if unsplit: extra = ' 현금과 현금성 자산 한 줄(Total Cash and Cash Equivalents)은 나뉘지 않아 그 안의 국채 만기는 알 수 없고, 값은 표에 적힌 단기국채 줄만 본 것.'
        if mmf_total: extra = ' 정부 MMF는 펀드 CUSIP 줄만 있고 펀드 안 보유 종목과 만기가 원문에 없어(fund_holdings=[]) 직접 보유분만 본 것.'
        notes['treasury_max_maturity_days'] = {'state': 'found', 'where': tmax[1], 'note': tmax[2].rstrip('.') + '.' + extra}
        tbasis = 'direct'; tdays = tmax[0]
    else:
        tbasis, tdays = None, None
        coll = [h for h in holdings if h['kind'] == 'reverse_repo_overnight']
        cm = ''
        if legacy and coll and coll[0].get('collateral_max_maturity_days') is not None:
            cm = f' 역레포 담보 국채의 최장 만기는 {coll[0]["collateral_max_maturity_days"]}일이나 담보는 준비자산이 아니라 역레포의 담보여서 국채 보유로 세지 않음.'
        notes['treasury_max_maturity_days'] = {'state': 'not_applicable', 'where': None,
                                              'note': '직접 보유한 국채(treasury_bill, treasury_note) 없음, 펀드 안 국채 목록 없음.' + cm}
    # ---- 5) 역레포 만기 -----------------------------------------------------------------------------------------------
    if rmax:
        notes['repo_max_maturity_days'] = {'state': 'found', 'where': rmax[1], 'note': rmax[2]}
    elif unsplit:
        notes['repo_max_maturity_days'] = {'state': 'not_in_report', 'where': None,
                                          'note': '현금과 현금성 자산이 한 줄(Total Cash and Cash Equivalents)로 합쳐져 그 안에 역레포가 있는지와 만기를 원문에서 알 수 없음.'}
    elif mmf_total and (mm := re.search(r'[Gg]overnment [Mm]oney [Mm]arket [Ff]unds at net asset value\s+hold[^.]*?reverse\s+repurchase[^.]*\.', text, re.S)):
        # 직접 보유 레포는 없어도 정부 MMF가 역레포를 담는다고 원문이 적었으면 레포가 있는 것이고, 펀드 안 레포 종목과 만기는 원문에 없다.
        m = re.search(r'held no repurchase agreements', text)
        notes['repo_max_maturity_days'] = {'state': 'not_in_report', 'where': at(text, mm.start(), ' '.join(mm.group(0).split())),
            'note': '직접 보유 역레포는 없음(원문 "held no repurchase agreements", ' + (f'쪽 {locate(text, m.start())[0]}' if m else '표 칸 "-"') +
                    '). 그러나 정부 MMF가 미국 국채와 그 국채 대상 역레포를 보유한다고 적어 펀드 안에 역레포가 있고, 펀드 안 종목과 만기는 원문에 없음(MMF 표는 펀드 CUSIP 줄과 Maturity N/A뿐).'}
    else:
        m = re.search(r'held no repurchase agreements|Repurchase agreements, at fair value\s+-', text)
        notes['repo_max_maturity_days'] = {'state': 'not_applicable', 'where': at(text, m.start(), m.group(0)) if m else None,
                                          'note': '역레포 줄이 없거나 0(원문이 "held no repurchase agreements" 또는 표 칸이 "-").'}
    rdays = rmax[0] if rmax else None

    # ---- 6) 공시 주기 ------------------------------------------------------------------------------------------------
    d0, d1 = r['report_dates']
    cnote = f'보고서 하나가 월중 기준일({d0})과 월말 기준일({d1}) 두 날짜를 다루고 월마다 한 건씩 나옴(월별 연속성은 data/samples PDF 목록으로 확인).'
    if d0[:7] != d1[:7]:
        # PYUSD 2026-01은 본문 표 머리에 첫 기준일 연도가 2025로 잘못 적혔다(1쪽 소개 문장은 2026).
        d0d = datetime.date.fromisoformat(d0); alt = f'{list(MONTHS)[d0d.month - 1].capitalize()} {d0d.day}, {as_of.year}'
        cnote = f'본문 표의 첫 기준일은 {d0}로 적혔고 같은 보고서의 다른 쪽에는 {alt}로 적혀 연도 오기이며 월말 기준일은 {d1}. 월마다 한 건씩 나옴(월별 연속성은 data/samples PDF 목록으로 확인).' if alt in text else cnote
    notes['disclosure_cadence'] = {'state': 'found', 'where': r['sources']['report_dates'][0], 'note': cnote}

    # ---- 7) 유통량 산정 설명 -----------------------------------------------------------------------------------------
    m = re.search(r'Total \w+ natively minted tokens', text)
    if m and re.search(r'Less (?:temporary|permanent) \w+ nonredeemable tokens', text):
        circ_raw, circ_pos = m.group(0), m.start()
    else:
        circ_raw, circ_pos = exhibit_a_formula(text)
    if circ_pos is not None:
        circ_formula = True
        notes['circulation_formula_disclosed'] = {'state': 'found', 'where': at(text, circ_pos, circ_raw),
            'note': 'Exhibit A가 (a) 발행 토큰 총량에서 (b) 임시 상환 불가, (c) 영구 상환 불가 토큰을 빼 (d) 상환 가능 토큰 잔액을 내는 식을 표로 적음.'}
    else:
        circ_formula = False
        m2 = re.search(r'\(which also represents the total circulating supply\)', text)
        notes['circulation_formula_disclosed'] = {'state': 'not_disclosed', 'where': at(text, m2.start(), m2.group(0)) if m2 else None,
            'note': '원문 전체에서 natively minted, burn, less ... nonredeemable, excluding, issuer-held 같은 산정 말을 찾았으나 없음. 원문은 계약 주소의 공급량(supply as denoted under contract)을 유통량으로 적을 뿐 소각 차감이나 발행사 보유분 제외를 설명하지 않음'
                    + ('(2023년식은 "total supply ... which also represents the total circulating supply", Etherscan API와 자체 노드 출처 명시)' if m2 else '') + '.'}

    # ---- 8) 보관 기관 이름 ------------------------------------------------------------------------------------------
    cust_names, cust_where = [], None
    mc = re.search(r'custodied Redemption Assets at(.+?)\n\s*(?:To the best|\x0c)', text, re.S)
    if mc:
        raw = ' '.join(mc.group(1).split()).rstrip('.')
        cust_where = at(text, mc.start(1), raw)
        for nm in re.findall(r'DBS Bank Ltd\.|Banking Circle S\.A\.|Standard Chartered Bank \(Singapore\) Limited|Dreyfus Asset Management', raw):
            cust_names.append(nm + (' (a subsidiary of Bank of New York Mellon)' if nm.startswith('Dreyfus') and 'Bank of New York Mellon' in raw else ''))
    if cust_names:
        notes['custodian_disclosure'] = {'state': 'found', 'where': cust_where, 'note': 'Note 5 "the Company custodied Redemption Assets at ..."에 기관 이름이 적힘: ' + '; '.join(cust_names) + '.'}
    else:
        named = re.search(r'\b(?:DBS|Banking Circle|Standard Chartered|Dreyfus|Bank of New York|BNY|Citi|JPMorgan|Wells Fargo|Cross River|Customers Bank|Silvergate|Signature Bank|Goldman|State Street|Fidelity|BlackRock|Federated|Morgan Stanley|HSBC)', text)
        if named: warn.append('보관 기관 이름 후보 ' + named.group(0))
        have = [x for x in ('Bank 1 in', 'Federal Reserve Board', 'Monetary Authority of Singapore', 'regulated financial institutions', 'U.S. insured depository institutions',
                            'FDIC', 'qualified custodian', 'commercial banks') if x in text]
        notes['custodian_disclosure'] = {'state': 'not_disclosed', 'where': None,
            'note': '원문 전체에서 custod, DBS, Banking Circle, Standard Chartered, Dreyfus, BNY, Citi, JPMorgan 등 기관 이름을 찾았으나 보관 은행 이름 없음. 원문에 있는 것은 이름 없는 표현뿐: ' + ', '.join(have) + '.'}

    # ---- 9) 경영진 확인서 ------------------------------------------------------------------------------------------
    sm, blk = sig_block(text)
    titles = []
    for t in re.findall(TITLES, blk):
        if t not in titles: titles.append(t)
    if sm and titles and re.search(r"Management.s Assertion|assertions?\b", text):
        notes['management_certification'] = {'state': 'found', 'where': at(text, sm.start(), sm.group(0)),
            'note': '경영진 주장(Management\'s Assertion 또는 management ... assertions)과 "To the best of the knowledge and belief of the undersigned, the information ... is accurate and complete" 서명 문단이 있고 서명자 직함은 ' + '; '.join(titles) + '.'}
        mgmt, certifier = True, '; '.join(titles)
    else:
        warn.append('경영진 서명 못 찾음')
        mgmt, certifier = False, None
        notes['management_certification'] = {'state': 'not_disclosed', 'where': None, 'note': 'undersigned 서명 문단 또는 직함을 찾지 못함.'}

    # ---- 10) 상환 기한, 이자 지급 ---------------------------------------------------------------------------------
    mi = re.search(r'accrued but unswept interest', text)
    notes['redemption_days'] = {'state': 'not_in_report', 'where': None,
        'note': 'business day, within N days, redemption fee, redeem 같은 말을 찾았으나 상환 기한 문장 없음. 본문은 매수와 상환 조건을 회사 약관(terms and conditions) 링크로만 가리킴.'}
    notes['interest_paid'] = {'state': 'not_in_report', 'where': at(text, mi.start(), mi.group(0)) if mi else None,
        'note': 'interest, yield, reward를 찾았으나 토큰 보유자에게 이자를 준다는 문장 없음.'
                + (' 각주에 "준비자산에 쌓인 미수 이자도 준비자산 총액에 포함, 유통량을 넘는 순수익은 Paxos가 인출할 수 있음"이 있어 이자는 발행사가 가져간다는 취지이며 지급 값은 아님.' if mi else '')}

    return {
        'holdings': holdings, 'fund_holdings': [], 'asset_types': kinds,
        'treasury_max_maturity_days': tdays, 'treasury_maturity_basis': tbasis, 'repo_max_maturity_days': rdays,
        'disclosure_cadence': 'monthly', 'disclosure_cadence_days': 31,
        'circulation_formula_disclosed': circ_formula,
        'custodian_disclosure': bool(cust_names), 'custodians': cust_names,
        'management_certification': mgmt, 'certifier': certifier,
        'redemption_days': None, 'interest_paid': None,
        'field_notes': notes,
        **({'rule_input_warnings': warn} if warn else {}),
    }


def exhibit_a_formula(text):
    """Exhibit A 표 안에서 유통량 산정식(natively minted - Less temporary/permanent nonredeemable = redeemable)을 찾는다.
    표 줄 라벨이 두 줄로 접히거나 사이에 금액 칸이 끼고(PYUSD 2025-07 이후) 글 순서가 섞여(USDG OCR) 한 줄 정규식으로는 놓치므로
    'Exhibit A:' 제목부터 'Exhibit B:' 제목 앞까지를 한 구역으로 보고 세 말(natively, Less temporary|permanent, nonredeemable)이 다 있는지 본다.
    -> (인용 raw, 위치) 또는 (None, None)"""
    a = re.search(r'Exhibit A:\s*Total \w+ Natively Minted Tokens', text)
    if not a: return None, None
    b = re.search(r'Exhibit B: Composition', text[a.end():])
    reg = text[a.start():a.end() + b.start()] if b else text[a.start():]
    m = re.search(r'\bnatively\b', reg)
    if m and re.search(r'Less\s+(?:temporary|permanent)', reg) and 'nonredeemable' in reg:
        pos = a.start() + m.start()
        ls = text.rfind('\n', 0, pos) + 1
        line = text[ls:text.find('\n', pos)]
        mr = re.search(r'Total \w+ natively(?: minted)?', line) or re.search(r'natively(?: minted)?', line)  # 행 라벨 "a"와 "."은 PDF 표에서 칸이 달라 붙여 쓰지 않는다
        return mr.group(0), ls + mr.start()
    return None, None


def mmf_items(text, as_of_iso):
    """USDG Exhibit B 정부 MMF 표(Entity, CUSIP/ISIN, Maturity N/A, 금액 두 칸)의 월말 금액 줄. 펀드 안 보유 종목은 원문에 없다."""
    exb = text.find('Exhibit B: Composition of Redemption Assets by Asset Type')
    mc = re.search(r'Exhibit C:\s*Comparison', text[exb:])
    seg = text[exb:exb + mc.start()] if mc else text[exb:]
    out = []
    for m in re.finditer(r'^\s*(PDS|PIE)\s+([0-9A-Z]{9,12})\s+N/A\s+\$?\s?([\d,]+)(?:\s+\$?\s?([\d,]+))?', seg, re.M):
        out.append({'entity': m.group(1), 'id': m.group(2), 'maturity': 'N/A', 'amount': float(money(m.group(4) or m.group(3)))})
    return out


NOTE = (
    'sources는 숫자별 {page, line, raw} 출처. 대사 실패 보고서는 reports에서 제외. as_of=월말 기준일(두 번째 기준일). '
    '구성 매핑: [2025-01 이후 Exhibit B 형식] cash=Cash, government_mmf=Government money market funds, repo=Repurchase agreements, '
    'treasury=Obligations of U.S. Treasury(other 키 없음). '
    '[2023~2024년 PYUSD, USDP와 USDG 2024-10~2025-12 옛 형식, 월말 기준일 표만 읽음] treasury=Total U.S. Treasury Bills(직접 보유 단기국채), '
    'repo=Total U.S. Government Guaranteed Debt Instruments Held Pursuant to Overnight Reverse Repurchase Agreements(역레포 담보 국채 합. 줄이 비면 0), '
    'cash=Total U.S. Dollars Held(USDG는 Total Cash and Cash Equivalents를 other로, 아래 참고), government_mmf=0(행 없음), '
    'other=0(원문 줄마다 달러 반올림으로 부분 합이 총계와 1달러 어긋난 PYUSD 2023-09, 2024-01, 2024-05, USDP 2024-02는 그 차액 +-1을 other에 두고 flags.rounding_residual로 표시). '
    '2023년 PYUSD, USDP의 유통량은 소수점 둘째 자리까지 적혀 있어 반올림한 정수(flags.circulation_decimals). 옛 형식에는 회계법인이 글자로 안 나온다: '
    'PYUSD, USDP 2023~2024-12는 로고와 서명이 이미지뿐이라 firm=null(flags.firm_signature_image), USDG 2024-10~2025-12는 Enrome LLP, 2025-01 이후 PYUSD, USDP는 KPMG LLP. '
    'USDG 2024-10~2025-12 attestation.type은 원문 제목 그대로 examination(2026년만 reasonable assurance). USDP 2024-11은 표 제목 날짜가 옛 날짜(October 31, 2024)로 남아 있어 '
    '마지막 표를 월말 표로 읽었고(flags.table_heading_date_mismatch) 표 총계가 머리표와 같음을 확인. PYUSD 2024-04는 원문 표 유통량 328,083,118과 주석 328,083,103이 서로 달라 표 값을 썼다(flags.circulation_note_mismatch). '
    'USDG 2025-09의 5~7쪽은 글자 층 인코딩이 깨져 OCR로 읽었다(flags.ocr_pages). '
    'USDG 2024-10~2025-12는 \'Total Cash and Cash Equivalents\' 한 줄이라(원문에 은행 예금, MMF, 레포 구분 없음) cash=null(알 수 없음)로 두고 그 줄 전체를 other에 넣었다'
    '(flags.cash_equivalents_in_other, flags.cash_is_bank_deposit=false), 은행 예금 금액은 알 수 없음. '
    'repo와 government_mmf의 0은 구분 없음(flags.repo_mmf_not_split), 2025-09 이후는 Note 5 보관처에 Dreyfus Asset Management(자산운용사)가 있어 MMF가 섞였을 수 있다(flags.cash_custodians_note5).'
)

RULE_NOTE = (
    'holdings=준비자산을 원문 줄 단위로 나눈 목록(amount 합=fair_value, 대사 실패 시 rule_input_warnings). 금액은 components와 같은 값이며 줄 이름, 만기, 쪽과 줄을 원문에서 읽어 붙임. '
    'kind 매핑: Cash 또는 Total U.S. Dollars Held=bank_deposit, Total U.S. Treasury Bills 또는 Obligations of U.S. Treasury(Treasury bills 표)=treasury_bill, '
    'Repurchase agreements 또는 Held Pursuant to Overnight Reverse Repurchase Agreements=reverse_repo_overnight, Government money market funds=government_mmf, '
    'USDG 2024-10~2025-12의 Total Cash and Cash Equivalents=cash_equivalents_unsplit, 원문 줄 합계와 총계의 반올림 차이=settlement. '
    '옛 형식(2023~2024년 PYUSD, USDP)의 역레포 줄 아래 종목(U.S. Treasury Bonds/Debt, CUSIP, 만기일)은 역레포 담보이므로 reverse_repo_overnight 줄의 items에 담고 국채 보유로 세지 않으며 '
    'collateral_max_maturity_days로만 남김. 역레포 만기는 표 제목 또는 본문이 overnight이라 하고 만기일이 다음 영업일이므로 1. '
    '국채 만기(treasury_max_maturity_days)는 직접 보유 Treasury bills 중 가장 늦은 만기일에서 as_of를 뺀 달력일이며 basis=direct. 보고서에 펀드 안 보유 종목을 적은 표가 없어 fund_holdings는 모두 []. '
    'USDG 2024-10~2025-12는 한 줄(cash_equivalents_unsplit) 안의 구성을 알 수 없고, 그 안에 국채나 MMF가 더 있을 수 있음. '
    '만기 날짜는 글자 층이 없는 쪽(USDG 대부분)은 OCR로 읽고 이미지와 대조한 값. 유통량 설명 없음(false)은 옛 형식이 계약 공급량만 적었기 때문. '
    '경영진 확인서 certifier는 서명 문단의 직함. 상환 기한과 이자 지급은 모든 보고서에 없어 null(not_in_report).'
)

# 원문 자체가 안 맞아 제외하는 보고서(파서 오류가 아님). 새로 대사에 실패한 보고서만 종료 코드 1로 알린다.
KNOWN_SOURCE_ERRORS = {
    'Paxos_PYUSD_Examination_2024-07.pdf': '2024-07-31 표 총계 $639,945,680이 줄 합계(국채 81,453,620 + 역레포 552,487,080 + 현금 5,004,980 = '
                                           '$638,945,680)와 $1,000,000 어긋나고 머리표 준비자산 총액($638,945,680)과도 다르다(원문 오기).',
}


def main():
    reports, bad = [], []
    for token in ('PYUSD', 'USDP', 'USDG'):
        pdfs = sorted(SRC.glob(f'Paxos_{token}_Examination_*.pdf'))
        for p in pdfs:
            r = parse(p, token)
            reports.append(r)
            if r.get('ok'):
                print(f"ok  {token} {r['month']}  유통 {r['circulation']:,}  준비자산 {r['fair_value']:,}  "
                      f"커버리지 {r['coverage'] * 100:.4f}%  기준일 {r['as_of']}  서명 {r['attestation']['signed']}"
                      + (f"  OCR쪽 {r['flags']['ocr_pages']}" if 'ocr_pages' in r['flags'] else ''))
            else:
                bad.append(p.name)
                print(f"FAIL {p.name}: {r.get('error') or r.get('reconciliation')}"
                      + (f"\n     제외 사유(원문 오기): {KNOWN_SOURCE_ERRORS[p.name]}" if p.name in KNOWN_SOURCE_ERRORS else ''))
            if VERBOSE:
                print('    ', json.dumps(r.get('flags', {}), ensure_ascii=False))
    if not reports:
        print('PDF 없음:', SRC); return 1
    # 월별 연속성: 토큰마다 첫 달부터 마지막 달까지 PDF가 빠진 달 없이 있는지(제외 보고서 포함) 확인해 cadence 메모에 적는다.
    for token in ('PYUSD', 'USDP', 'USDG'):
        months = [p.stem[-7:] for p in sorted(SRC.glob(f'Paxos_{token}_Examination_*.pdf'))]
        idx = [int(m[:4]) * 12 + int(m[5:]) for m in months]
        gaps = [m for m in range(idx[0], idx[-1] + 1) if m not in idx]
        for r in reports:
            if r['token'] == token and r.get('ok'):
                r['field_notes']['disclosure_cadence']['note'] += f' {token} PDF {len(months)}건이 {months[0]}부터 {months[-1]}까지 ' + ('빠진 달 없이 월별로 이어짐.' if not gaps else f'이어지나 빠진 달 {gaps}.')
    # 같은 CUSIP이 보고서마다 다른 만기로 적힌 경우(원문 오기 의심)는 읽은 값은 그대로 두고 메모만 남긴다.
    seen = {}
    for r in reports:
        for h in r.get('holdings', []):
            for i in (h['items'] if h['kind'] == 'treasury_bill' else []):
                if i.get('id'): seen.setdefault((r['token'], i['id'][:9]), {}).setdefault(i['maturity'], set()).add(r['month'])
    for r in reports:
        for h in r.get('holdings', []):
            for i in (h['items'] if h['kind'] == 'treasury_bill' else []):
                v = seen.get((r['token'], (i.get('id') or '')[:9]), {})
                if len(v) > 1:
                    other = '; '.join(f'{m} 보고서는 {d}' for d, ms in sorted(v.items()) if d != i['maturity'] for m in sorted(ms))
                    r['field_notes']['treasury_max_maturity_days']['note'] += f' 같은 CUSIP {i["id"][:9]}가 이 보고서에서는 {i["maturity"]}, {other}로 적혀 원문끼리 어긋남(이 보고서는 적힌 대로 읽음).'
    excluded = [{'token': r['token'], 'month': r['source_file'][-11:-4], 'source_file': r['source_file'],
                 'reason': KNOWN_SOURCE_ERRORS.get(pathlib.Path(r['source_file']).name) or r.get('error') or 'reconciliation 실패'}
                for r in reports if not r.get('ok')]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        'generated': datetime.date.today().isoformat(),
        'source': 'Paxos PYUSD/USDP/USDG 월간 examination report(USDG 2026년은 reasonable assurance), pdftotext -layout, 글자 층 없는 쪽은 macOS Vision OCR',
        'note': NOTE + ' 제외: ' + ' / '.join(f'{k[6:-4]} {v}' for k, v in KNOWN_SOURCE_ERRORS.items()),
        'rule_inputs_note': RULE_NOTE,
        'excluded': excluded,
        'reports': [r for r in reports if r.get('ok')],
    }, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n{len(reports)}건 중 성공 {len(reports) - len(bad)} → {OUT.relative_to(ROOT)}, 대사 실패 {len(bad)}')
    return 1 if set(bad) - set(KNOWN_SOURCE_ERRORS) else 0


if __name__ == '__main__':
    sys.exit(main())
