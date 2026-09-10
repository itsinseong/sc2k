#!/usr/bin/env python3
"""Circle USDC 월간 검사보고서 PDF 파서 (F1).

data/samples/Circle_USDC_Examination_*.pdf 를 읽어 data/reports.json 을 만든다.
합계 대사가 어긋나면 그 달을 실패로 표시하고 종료 코드 1을 낸다.

사용: python3 scripts/parse_circle.py [--verbose]
"""
import json, re, subprocess, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'samples'
OUT = ROOT / 'data' / 'reports.json'
VERBOSE = '--verbose' in sys.argv

MONTHS = {m: i for i, m in enumerate(
    'january february march april may june july august september october november december'.split(), 1)}


def text_of(pdf, first=None, last=None):
    cmd = ['pdftotext', '-layout']
    if first: cmd += ['-f', str(first)]
    if last: cmd += ['-l', str(last)]
    cmd += [str(pdf), '-']
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def num(s):
    return int(s.replace(',', ''))


def to_iso(s):
    """'July 31, 2026' -> '2026-07-31'"""
    m = re.match(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', s.strip())
    if not m: return None
    mon, day, year = m.groups()
    i = MONTHS.get(mon.lower())
    return f'{year}-{i:02d}-{int(day):02d}' if i else None


def last_amount(text, label):
    """label 뒤에 오는 마지막 금액. 보고서에 기준일별 구획이 둘이고 월말 구획이 뒤에 온다."""
    hits = re.findall(re.escape(label) + r'[^\n\d]*([\d,]{7,})', text)
    return num(hits[-1]) if hits else None


def parse(pdf):
    text = text_of(pdf)
    page1 = text_of(pdf, 1, 1)
    r = {'source_file': str(pdf.relative_to(ROOT)), 'issuer': 'Circle Internet Group, Inc.', 'token': 'USDC'}

    m = re.search(r'Report Dates\s+([A-Za-z]+ \d{1,2}, \d{4})\s+([A-Za-z]+ \d{1,2}, \d{4})', text)
    if not m:
        return {**r, 'ok': False, 'error': 'Report Dates 줄을 찾지 못함'}
    r['report_dates'] = [to_iso(m.group(1)), to_iso(m.group(2))]
    r['as_of'] = r['report_dates'][1]
    r['month'] = r['as_of'][:7]
    r['as_of_time'] = '23:59 UTC' if '11:59pm' in text else None

    m = re.search(r'USDC in Circulation\s+([\d,]+)\s+([\d,]+)', text)
    r['circulation'] = num(m.group(2)) if m else None
    m = re.search(r'Fair Value of Assets Held in USDC Reserve\s+\$?\s*([\d,]+)\s+\$?\s*([\d,]+)', text)
    r['fair_value'] = num(m.group(2)) if m else None

    crf = last_amount(text, 'TOTAL CIRCLE RESERVE FUND ASSETS')
    oth = last_amount(text, 'TOTAL OTHER USDC RESERVE ASSETS')
    tot = last_amount(text, 'TOTAL USDC RESERVE ASSETS AS OF')
    r['components'] = {'circle_reserve_fund': crf, 'other': oth}

    # 합계 대사. 구획을 잘못 잡으면 여기서 걸린다.
    checks = {}
    if None not in (crf, oth, tot):
        checks['components_sum'] = {'expected': tot, 'got': crf + oth, 'diff': crf + oth - tot}
    if None not in (tot, r['fair_value']):
        checks['total_equals_fair_value'] = {'expected': r['fair_value'], 'got': tot, 'diff': tot - r['fair_value']}
    if None not in (r['fair_value'], r['circulation']):
        checks['covers_circulation'] = {'surplus': r['fair_value'] - r['circulation'],
                                        'ok': r['fair_value'] >= r['circulation']}
    r['reconciliation'] = checks
    r['ok'] = (all(c.get('diff', 0) == 0 for c in checks.values() if 'diff' in c)
               and checks.get('covers_circulation', {}).get('ok', False))

    if r['ok']:
        r['coverage'] = round(r['fair_value'] / r['circulation'], 8)

    # 검증 정보. 회계법인명은 서명 이미지라 텍스트로 안 나온다.
    dates = re.findall(r'^\s*([A-Za-z]+ \d{1,2}, \d{4})\s*$', text, re.M)
    r['attestation'] = {
        'type': 'examination' if 'We have examined' in text else None,
        'standard': 'AICPA attestation standards' if 'American Institute of Certified Public Accountants' in text else None,
        'signed': to_iso(dates[-1]) if dates else None,
        'firm': None,  # 이미지 서명. 서식 항목 D1은 수동 확인 필요
    }

    # 구조 차이. 7월만 기타 준비자산 안에 국채 하위표가 있다.
    tail = text.split('OTHER USDC RESERVE ASSETS AS OF')[-1]
    r['flags'] = {
        'garbled_page1': 'Circle Internet Group' not in page1,
        'other_has_treasury_subtable': 'TOTAL U.S. TREASURY SECURITIES' in tail,
        'scan_suspected': len(text.strip()) < 2000,
    }
    return r


def main():
    pdfs = sorted(SRC.glob('Circle_USDC_Examination_*.pdf'))
    if not pdfs:
        print('PDF 없음:', SRC); return 1
    reports, bad = [], []
    for p in pdfs:
        r = parse(p)
        reports.append(r)
        tag = 'ok ' if r.get('ok') else 'FAIL'
        print(f"{tag} {r.get('month', p.name)}  유통 {r.get('circulation'):,}  준비자산 {r.get('fair_value'):,}  "
              f"커버리지 {r.get('coverage', 0) * 100:.4f}%  기준일 {r.get('as_of')}  서명 {r['attestation']['signed']}"
              if r.get('ok') else f"{tag} {p.name}: {r.get('error') or r.get('reconciliation')}")
        if VERBOSE: print('   ', json.dumps(r['flags'], ensure_ascii=False))
        if not r.get('ok'): bad.append(p.name)
    reports.sort(key=lambda x: x.get('as_of') or '')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        'generated': datetime.date.today().isoformat(),
        'source': 'Circle USDC 월간 examination report, pdftotext -layout',
        'note': '회계법인명은 서명 이미지라 자동 추출되지 않는다. 서식 항목 D1은 수동 확인.',
        'reports': reports,
    }, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n{len(reports)}개월 → {OUT.relative_to(ROOT)}, 대사 실패 {len(bad)}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
