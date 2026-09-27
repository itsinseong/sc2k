#!/usr/bin/env python3
"""Paxos (PYUSD, USDP, USDG) 검사보고서 PDF 파서.

data/samples/Paxos_{토큰}_Examination_*.pdf 를 읽어 data/reports_paxos.json 을 만든다.
출력 스키마는 data/reports.json(parse_circle.py)과 같은 항목 구성에 sources를 더했다.
합계 대사가 어긋나면 그 보고서를 결과에서 빼고 이유를 로그로 남긴다.

사용: python3 scripts/parse_paxos.py [--verbose]
"""
import json, re, subprocess, sys, pathlib, datetime

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
    # 함정: pdftotext를 스레드풀 안에서 부르면 빈 문자열이 나온다. 순차 호출만 쓴다.
    return subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, check=True).stdout


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


def parse(pdf, token):
    text = text_of(pdf)
    r = {'source_file': str(pdf.relative_to(ROOT)), 'issuer': ISSUERS[token], 'token': token}
    sources = {}

    m = re.search(r'Report Dates\s+([A-Za-z]+ \d{1,2}, \d{4})\s+([A-Za-z]+ \d{1,2}, \d{4})', text)
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

    summary_start = text.find('Summary1')
    if summary_start == -1:
        return {**r, 'ok': False, 'error': 'Summary1 절을 찾지 못함'}
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
    pairs = list(re.finditer(rf'({AMTZ})\s+({AMTZ})\s*$', exb, re.M))
    if len(pairs) != 5:
        return {**r, 'ok': False, 'error': f'Exhibit B 행 수 불일치(5개 기대, {len(pairs)}개 발견)'}
    def val(mm, g):
        raw = mm.group(g)
        return 0 if raw == '-' else num(raw)
    cash, ggmf, repo, treas, total = pairs
    r['components'] = {'cash': val(cash, 2), 'government_mmf': val(ggmf, 2),
                        'repo': val(repo, 2), 'treasury': val(treas, 2)}
    components_total = val(total, 2)
    sources['components'] = {}
    for k, p in zip(['cash', 'government_mmf', 'repo', 'treasury', 'total'], pairs):
        pos = exb_start + p.start(2)
        page, line = locate(text, pos)
        sources['components'][k] = {'page': page, 'line': line, 'raw': p.group(2)}

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
    if 'Independent Accountants’ Examination Report' in text or 'We have examined management' in text:
        atype = 'examination'
    elif 'Independent reasonable assurance report' in text:
        atype = 'reasonable assurance'
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
    r['sources'] = sources
    return r


def main():
    reports, bad = [], []
    for token in ('PYUSD', 'USDP', 'USDG'):
        pdfs = sorted(SRC.glob(f'Paxos_{token}_Examination_*.pdf'))
        for p in pdfs:
            r = parse(p, token)
            reports.append(r)
            if r.get('ok'):
                print(f"ok  {token} {r['month']}  유통 {r['circulation']:,}  준비자산 {r['fair_value']:,}  "
                      f"커버리지 {r['coverage'] * 100:.4f}%  기준일 {r['as_of']}  서명 {r['attestation']['signed']}")
            else:
                bad.append(p.name)
                print(f"FAIL {p.name}: {r.get('error') or r.get('reconciliation')}")
            if VERBOSE:
                print('    ', json.dumps(r.get('flags', {}), ensure_ascii=False))
    if not reports:
        print('PDF 없음:', SRC); return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        'generated': datetime.date.today().isoformat(),
        'source': 'Paxos PYUSD/USDP/USDG 월간 examination(USDG는 reasonable assurance) report, pdftotext -layout',
        'note': 'sources는 숫자별 {page, line, raw} 출처. 대사 실패 보고서는 reports에서 제외.',
        'reports': [r for r in reports if r.get('ok')],
    }, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n{len(reports)}건 중 성공 {len(reports) - len(bad)} → {OUT.relative_to(ROOT)}, 대사 실패 {len(bad)}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
