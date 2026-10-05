#!/usr/bin/env python3
"""data/reports*.json 을 전부 읽어 site/data/reports.json 으로 합친다.

같은 스키마의 data/reports_paxos.json 등이 늘어나도 파일명만 늘리면 된다.
보고서마다 issuer_short(발행사 짧은 이름)와 home(그 발행사를 감독하는 관할권 id 목록)을 붙인다.
표준 라이브러리만 쓴다.

사용: python3 scripts/build_site.py
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
OUT = ROOT / 'site' / 'data' / 'reports.json'

# 끝까지 독립 검증과 불일치로 남은 보고서는 (토큰, 월)로 적는다. 지금은 없다.
# 대사 실패 보고서는 각 파서가 data/reports*.json 에 아예 쓰지 않는다.
EXCLUDE = set()

TOKEN_ORDER = ['USDC', 'EURC', 'PYUSD', 'USDP', 'USDG', 'RLUSD', 'GUSD', 'USDT']

# issuer 문자열(소문자)에 들어 있는 말 -> 짧은 이름. 위에서부터 처음 맞는 줄을 쓴다.
ISSUER_SHORT = [
    ('circle', 'Circle'),
    ('paxos', 'Paxos'),
    ('standard custody', 'Ripple'),
    ('gemini', 'Gemini'),
    ('tether', 'Tether'),
]


def issuer_short(r):
    low = r['issuer'].lower()
    for key, short in ISSUER_SHORT:
        if key in low:
            return short
    raise SystemExit(f"모르는 issuer: {r['issuer']!r} ({r['token']} {r['month']})")


def eurc_issued_by_europe_sas(r):
    """파서의 issuer는 보증을 낸 Circle Internet Group, Inc.(2024-07부터)나 Circle Internet Financial, LLC라서 발행 법인을 알려 주지 않는다.
    발행 법인은 PDF 본문의 'EURC is issued and redeemed by Circle Internet Financial Europe SAS' 문장으로 가른다(2024-07 보고서부터 있다).
    pdftotext는 하나씩 순서대로 부른다(스레드풀 안에서는 빈 문자열이 나온다)."""
    pdf = ROOT / r['source_file']
    out = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        raise SystemExit(f"pdftotext 실패: {pdf}")
    return bool(re.search(r'issued\s+and\s+redeemed\s+by\s+Circle\s+Internet\s+Financial\s+Europe\s+SAS', out.stdout, re.I))


def home(r):
    """발행사를 감독하는 관할권 id 목록. 모르는 조합이면 멈춘다."""
    tok, issuer = r['token'], r['issuer']
    if tok == 'USDC' and 'Circle' in issuer:
        return ['us']
    if tok == 'EURC' and 'Circle' in issuer:
        return ['eu-emt'] if eurc_issued_by_europe_sas(r) else ['us']
    if tok in ('PYUSD', 'USDP') and issuer.startswith('Paxos Trust Company'):
        return ['us']
    if tok == 'USDG' and issuer.startswith('Paxos Digital Singapore'):
        return ['sg']
    if tok == 'RLUSD' and issuer.startswith('Standard Custody & Trust Company'):
        return ['us']
    if tok == 'GUSD' and issuer.startswith('Gemini Trust Company'):
        return ['us']
    if tok == 'USDT' and 'tether' in issuer.lower():
        return []
    raise SystemExit(f"모르는 issuer와 토큰 조합: {issuer!r} / {tok} ({r['month']})")


def load_reports(path):
    doc = json.loads(path.read_text(encoding='utf-8'))
    # data/reports.json 형식: {"reports": [...]}. 만약을 위해 그냥 리스트인 파일도 받는다.
    return doc['reports'] if isinstance(doc, dict) else doc


def load_excluded(path):
    """파서가 대사 실패로 reports에서 뺀 보고서 목록(최상위 excluded). 없으면 빈 목록."""
    doc = json.loads(path.read_text(encoding='utf-8'))
    return doc.get('excluded', []) if isinstance(doc, dict) else []


def next_month(m, step):
    y, mo = int(m[:4]), int(m[5:])
    n = y * 12 + mo - 1 + step
    return f'{n // 12:04d}-{n % 12 + 1:02d}'


def build_series(reports, excluded):
    """토큰마다 첫 보고서 달, 마지막 보고서 달, 아직 게시 전인 달.
    제외 보고서도 발행사는 게시한 달이라 첫 달, 마지막 달, 전체 최신 달 계산에 넣는다.
    게시 전인 달 = 마지막 달 다음부터 전체 최신 달까지 그 토큰의 공시 주기(월간 1, 분기 3)로 센 달."""
    months = {}
    for r in reports:
        months.setdefault(r['token'], set()).add(r['month'])
    for e in excluded:
        months.setdefault(e['token'], set()).add(e['month'])
    latest = max(m for ms in months.values() for m in ms)
    step = {r['token']: 3 if r.get('disclosure_cadence') == 'quarterly' else 1 for r in reports}
    series = {}
    for t in TOKEN_ORDER:
        ms = sorted(months[t])
        pending, m = [], next_month(ms[-1], step[t])
        while m <= latest:
            pending.append(m)
            m = next_month(m, step[t])
        series[t] = {'first_month': ms[0], 'last_month': ms[-1], 'not_yet_published': pending}
    return series


# 화면과 엔진이 읽지 않는 큰 필드. 사이트 쪽 사본에서만 뺀다(data/ 원본은 그대로).
SITE_DROP = ('sources', 'reconciliation', 'holdings_reconciliation', 'source_file', 'report_dates', 'holdings_check')
# holdings, fund_holdings 줄에서 뺄 글자와 종목별 상세(만기 판정은 maturity_max_days가 한다)
HOLDING_DROP = ('label', 'where', 'items')
# flags 중 화면과 엔진이 읽는 것만 남긴다
FLAGS_KEEP = ('cash_is_bank_deposit',)


def slim(reports):
    """사이트 쪽 사본을 만든다. field_notes의 note는 같은 글이 여러 보고서에 되풀이되므로
    두 번 이상 나온 글은 최상위 notes 목록에 한 번만 두고, 그 자리에는 note 대신 note_ref(notes 목록 번호)를 적는다.
    읽는 쪽은 `fn.note ?? notes[fn.note_ref]` 로 푼다. 반환: (보고서 목록, notes 목록)."""
    count = {}
    for r in reports:
        for fn in r['field_notes'].values():
            count[fn['note']] = count.get(fn['note'], 0) + 1
    notes, ref = [], {}
    out = []
    for r in reports:
        c = {k: v for k, v in r.items() if k not in SITE_DROP}
        for k in ('holdings', 'fund_holdings'):
            c[k] = [{a: b for a, b in h.items() if a not in HOLDING_DROP} for h in r[k]]
        c['flags'] = {k: v for k, v in r['flags'].items() if k in FLAGS_KEEP}
        fns = {}
        for name, fn in r['field_notes'].items():
            fn = dict(fn)
            t = fn.get('note')
            if t and count[t] > 1:
                if t not in ref:
                    ref[t] = len(notes)
                    notes.append(t)
                del fn['note']
                fn['note_ref'] = ref[t]
            fns[name] = fn
        c['field_notes'] = fns
        out.append(c)
    return out, notes


# 사이트 데이터 크기 상한(1MB).
SITE_MAX_BYTES = 1_000_000


def main():
    files = sorted(DATA.glob('reports*.json'))
    if not files:
        print('data/reports*.json 을 찾지 못했다', file=sys.stderr)
        return 1

    reports = []
    sources = []
    excluded = []
    for f in files:
        excluded.extend({'token': e['token'], 'month': e['month'], 'reason': e['reason']} for e in load_excluded(f))
        batch = load_reports(f)
        kept = [r for r in batch if (r['token'], r['month']) not in EXCLUDE]
        reports.extend(kept)
        sources.append(f.relative_to(ROOT).as_posix())
        print(f'{f.relative_to(ROOT)}: 보고서 {len(kept)}개')

    for r in reports:
        if r['token'] not in TOKEN_ORDER:
            raise SystemExit(f"모르는 토큰: {r['token']}")
        r['issuer_short'] = issuer_short(r)
        r['home'] = home(r)
    reports.sort(key=lambda r: (TOKEN_ORDER.index(r['token']), r['as_of']))

    excluded.sort(key=lambda e: (TOKEN_ORDER.index(e['token']), e['month']))
    series = build_series(reports, excluded)

    site_reports, notes = slim(reports)
    doc = {'source_files': sources, 'excluded': excluded, 'series': series, 'notes': notes, 'reports': site_reports}
    text = json.dumps(doc, ensure_ascii=False, separators=(',', ':')) + '\n'
    size = len(text.encode('utf-8'))
    if size > SITE_MAX_BYTES:
        raise SystemExit(f'사이트 데이터 {size:,} bytes > {SITE_MAX_BYTES:,}')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding='utf-8')
    counts = {t: sum(r['token'] == t for r in reports) for t in TOKEN_ORDER}
    print(f'{OUT.relative_to(ROOT)}: 총 {len(reports)}개 보고서 {counts}, {OUT.stat().st_size:,} bytes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
