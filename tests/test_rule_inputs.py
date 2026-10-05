"""규칙 입력값(asset_types, treasury_max_maturity_days, repo_max_maturity_days, circulation_formula_disclosed,
custodian_disclosure, management_certification, field_notes)과 사이트 데이터(excluded, series) 검사.

기대값은 PDF 원문을 독립 검증자가 직접 읽어 파서 값과 대조한 값이다. 파서 출력에 맞춰 바꾸지 않는다.
data/reports*.json 을 그대로 읽는다(파서를 다시 돌리지 않는다). 사이트 검사는 build_site.py 실행 뒤의 site/data/reports.json 을 읽는다.
PYUSD 2025-08, 2025-10, 2025-11은 두 번째 검증자가 따로 읽었고 이 표의 값과 같았다.
"""
import glob, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / 'site' / 'data' / 'reports.json'
STATES = ('found', 'not_disclosed', 'not_in_report', 'not_applicable')
FIELDS = ('treasury_max_maturity_days', 'repo_max_maturity_days', 'disclosure_cadence', 'circulation_formula_disclosed',
          'custodian_disclosure', 'management_certification', 'redemption_days', 'interest_paid')


def _load():
    reports, excluded = [], []
    for f in sorted(glob.glob(str(ROOT / 'data' / 'reports*.json'))):
        doc = json.loads(pathlib.Path(f).read_text(encoding='utf-8'))
        reports += doc['reports']
        excluded += doc['excluded']
    return reports, excluded


REPORTS, EXCLUDED = _load()
BY = {(r['token'], r['month']): r for r in REPORTS}


def _tmax(spec):
    """'2023-01:72 2023-02:- ...' -> {월: 일수 또는 None}. '-'는 국채 만기 없음(null)."""
    out = {}
    for item in spec.split():
        m, v = item.split(':')
        out[m] = None if v == '-' else int(v)
    return out


# 토큰별 월별 treasury_max_maturity_days(전 달 빠짐없이). 이 표의 달 목록이 곧 그 토큰의 보고서 달 목록이다.
TMAX = {
    'USDC': _tmax('2023-01:72 2023-02:86 2023-03:55 2023-04:33 2023-05:- 2023-06:41 2023-07:80 2023-08:91 2023-09:62 2023-10:37 2023-11:42 2023-12:46 '
                  '2024-01:34 2024-02:91 2024-03:83 2024-04:56 2024-05:76 2024-06:53 2024-07:78 2024-08:91 2024-09:80 2024-10:84 2024-11:83 2024-12:86 '
                  '2025-01:90 2025-02:62 2025-03:87 2025-04:71 2025-05:60 2025-06:94 2025-07:91 2025-08:69 2025-09:72 2025-10:83 2025-11:83 2025-12:85 '
                  '2026-01:83 2026-02:83 2026-03:79 2026-04:84 2026-05:83 2026-06:51 2026-07:76 2026-08:73'),
    # 2023-10는 대사 실패로 제외(excluded)
    'EURC': {m: None for m in ['2023-%02d' % i for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12)]
             + ['%d-%02d' % (y, i) for y in (2024, 2025) for i in range(1, 13)]
             + ['2026-%02d' % i for i in range(1, 9)]},
    # 2024-07은 대사 실패로 제외
    'PYUSD': _tmax('2023-08:- 2023-09:- 2023-10:- 2023-11:- 2023-12:- 2024-01:27 2024-02:- 2024-03:62 2024-04:30 2024-05:76 2024-06:90 2024-08:83 '
                   '2024-09:52 2024-10:21 2024-11:25 2024-12:- 2025-01:- 2025-02:- 2025-03:- 2025-04:- 2025-05:- 2025-06:- 2025-07:- 2025-08:76 '
                   '2025-09:44 2025-10:13 2025-11:69 2025-12:55 2026-01:25 2026-02:69 2026-03:37 2026-04:7 2026-05:- 2026-06:79 2026-07:48 2026-08:31'),
    'USDP': _tmax('2023-01:23 2023-02:7 2023-03:11 2023-04:4 2023-05:15 2023-06:25 2023-07:8 2023-08:26 2023-09:34 2023-10:37 2023-11:54 2023-12:- '
                  '2024-01:27 2024-02:91 2024-03:- 2024-04:- 2024-05:4 2024-06:- 2024-07:- 2024-08:- 2024-09:- 2024-10:- 2024-11:- 2024-12:- '
                  + ' '.join('2025-%02d:-' % i for i in range(1, 13)) + ' ' + ' '.join('2026-%02d:-' % i for i in range(1, 9))),
    'USDG': _tmax('2024-10:5 2024-11:20 2024-12:14 2025-01:27 2025-02:32 2025-03:24 2025-04:43 2025-05:34 2025-06:36 2025-07:14 2025-08:34 '
                  '2025-09:30 2025-10:20 2025-11:55 2025-12:48 2026-01:83 2026-02:83 2026-03:58 2026-04:63 2026-05:48 2026-06:79 2026-07:48 2026-08:31'),
    'RLUSD': _tmax('2024-12:7 2025-01:4 2025-02:4 2025-03:1 2025-04:1 2025-05:4 2025-06:- 2025-07:5 2025-08:25 2025-09:56 2025-10:90 2025-11:76 2025-12:85 '
                   '2026-01:55 2026-02:62 2026-03:86 2026-04:77 2026-05:69 2026-06:86 2026-07:83 2026-08:88'),
    # 2023-05, 2023-09, 2024-03, 2026-04는 대사 실패로 제외, 2026-08은 아직 게시 전
    'GUSD': _tmax('2023-01:- 2023-02:58 2023-03:53 2023-04:25 2023-06:76 2023-07:45 2023-08:14 2023-10:51 2023-11:70 2023-12:67 '
                  '2024-01:34 2024-02:5 2024-04:51 2024-05:67 2024-06:67 2024-07:48 2024-08:18 2024-09:- 2024-10:- 2024-11:- 2024-12:- '
                  + ' '.join('2025-%02d:-' % i for i in range(1, 13)) + ' 2026-01:- 2026-02:- 2026-03:- 2026-05:- 2026-06:- 2026-07:-'),
    # 분기 보고서. 국채 줄에 만기가 없다
    'USDT': {m: None for m in ('2023-03', '2023-06', '2023-09', '2023-12', '2024-03', '2024-06', '2024-09', '2024-12',
                               '2025-03', '2025-06', '2025-09', '2025-12', '2026-03', '2026-06')},
}

BD, MMF, TB, RRO, RRT = 'bank_deposit', 'government_mmf', 'treasury_bill', 'reverse_repo_overnight', 'reverse_repo_term'
CEU = 'cash_equivalents_unsplit'
USDT_ALL = ('bank_deposit', 'bitcoin', 'corporate_bond', 'government_mmf', 'non_us_government_bill', 'other_investment',
            'precious_metal', 'reverse_repo_overnight', 'reverse_repo_term', 'secured_loan', 'treasury_bill')

# 토큰마다 (시작 달, 값) 줄. 보고서 달 이하 중 가장 늦은 시작 달의 값이 그 달의 기대값이다(값이 바뀐 달에서만 줄을 나눈다).
# asset_types는 정렬된 목록. repo는 repo_max_maturity_days.
ASSET_TYPES = {
    'USDC': [('2023-01', [BD, MMF]), ('2026-07', [BD, MMF, TB])],
    'EURC': [('2023-01', [BD])],
    'PYUSD': [('2023-08', [BD, RRO]), ('2024-01', [BD, RRO, TB]), ('2024-02', [BD, RRO]), ('2024-03', [BD, RRO, TB]),
              ('2024-12', [BD, RRO]), ('2025-08', [BD, RRO, TB]), ('2026-05', [BD, RRO]), ('2026-06', [BD, RRO, TB]),
              ('2026-07', [BD, RRO, TB])],
    'USDP': [('2023-01', [BD, RRO, TB]), ('2023-12', [BD, RRO]), ('2024-01', [BD, RRO, TB]), ('2024-03', [BD, RRO]),
             ('2024-05', [BD, RRO, TB]), ('2024-06', [BD, RRO]), ('2024-09', [BD]), ('2024-10', [BD, RRO])],
    'USDG': [('2024-10', [CEU, TB]), ('2026-01', [BD, MMF, TB])],
    'RLUSD': [('2024-12', [BD, MMF, TB]), ('2025-06', [BD, MMF]), ('2025-07', [BD, MMF, TB])],
    'GUSD': [('2023-01', [BD, MMF, TB]), ('2023-06', [BD, TB]), ('2023-10', [BD, MMF, TB]), ('2024-09', [BD, MMF]), ('2024-10', [BD])],
    'USDT': [('2023-03', list(USDT_ALL)),
             ('2025-12', [k for k in USDT_ALL if k not in (MMF, 'non_us_government_bill')]),
             ('2026-03', sorted([k for k in USDT_ALL if k not in (MMF, 'non_us_government_bill')] + ['public_equity'])),
             ('2026-06', sorted([k for k in USDT_ALL if k != MMF] + ['public_equity']))],
}
REPO = {
    'USDC': [('2023-01', None), ('2023-05', 1)],
    'EURC': [('2023-01', None)],
    'PYUSD': [('2023-08', 1)],
    'USDP': [('2023-01', 1), ('2024-09', None), ('2024-10', 1)],
    'USDG': [('2024-10', None)],
    'RLUSD': [('2024-12', None)],
    'GUSD': [('2023-01', None)],
    'USDT': [('2023-03', None)],
}
CIRC = {
    'USDC': [('2023-01', True)], 'EURC': [('2023-01', True)], 'PYUSD': [('2023-08', False), ('2025-01', True)],
    'USDP': [('2023-01', False), ('2025-01', True)], 'USDG': [('2024-10', False), ('2026-01', True)],
    'RLUSD': [('2024-12', True)], 'GUSD': [('2023-01', False)], 'USDT': [('2023-03', True)],
}
CUST = {
    'USDC': [('2023-01', True), ('2023-09', False)], 'EURC': [('2023-01', True), ('2023-09', False)],
    'PYUSD': [('2023-08', False)], 'USDP': [('2023-01', False)],
    'USDG': [('2024-10', False), ('2025-09', True), ('2026-01', False)],
    'RLUSD': [('2024-12', False)], 'GUSD': [('2023-01', True)], 'USDT': [('2023-03', False)],
}


def _at(steps, month):
    val = None
    for start, v in steps:
        if start <= month:
            val = v
    return val


def test_report_months_match_verified():
    """보고서 달 목록이 검증한 달 목록과 같다(없는 달은 파서가 만들지 않았다는 뜻)."""
    for tok, exp in TMAX.items():
        got = {m for (t, m) in BY if t == tok}
        assert got == set(exp), f'{tok} 달 불일치: {sorted(got ^ set(exp))}'
    assert {t for (t, _) in BY} == set(TMAX)


def test_treasury_max_maturity_days_every_month():
    for tok, exp in TMAX.items():
        for m, v in exp.items():
            assert BY[(tok, m)]['treasury_max_maturity_days'] == v, f'{tok} {m} 국채 최장 만기'


def test_representative_months_all_fields():
    """토큰마다 값이 바뀌는 달과 첫 달, 마지막 달에서 나머지 5개 필드까지 확인한다."""
    for tok, exp in TMAX.items():
        for m in exp:
            r = BY[(tok, m)]
            assert r['asset_types'] == sorted(_at(ASSET_TYPES[tok], m)), f'{tok} {m} asset_types {r["asset_types"]}'
            assert r['repo_max_maturity_days'] == _at(REPO[tok], m), f'{tok} {m} repo'
            assert r['circulation_formula_disclosed'] is _at(CIRC[tok], m), f'{tok} {m} circulation_formula_disclosed'
            assert r['custodian_disclosure'] is _at(CUST[tok], m), f'{tok} {m} custodian_disclosure'
            assert r['management_certification'] is True, f'{tok} {m} management_certification'


def test_spot_values():
    """원문에서 직접 읽은 눈에 띄는 값. USDC 2026-07부터 직접 보유 국채, PYUSD 2026-04 최단 7일, USDT 분기 보고서."""
    assert BY[('USDC', '2026-07')]['asset_types'] == [BD, MMF, TB]
    assert BY[('USDC', '2023-05')]['treasury_max_maturity_days'] is None and BY[('USDC', '2023-05')]['repo_max_maturity_days'] == 1
    assert BY[('PYUSD', '2026-04')]['treasury_max_maturity_days'] == 7
    assert BY[('USDG', '2025-12')]['asset_types'] == [CEU, TB]
    assert BY[('RLUSD', '2025-06')]['asset_types'] == [BD, MMF]
    assert BY[('USDT', '2026-03')]['asset_types'].count('public_equity') == 1
    assert BY[('USDT', '2026-03')]['disclosure_cadence'] == 'quarterly'


def test_holdings_sum_equals_fair_value():
    for r in REPORTS:
        diff = abs(sum(h['amount'] for h in r['holdings']) - r['fair_value'])
        # GUSD 원문은 센트 단위라 fair_value를 정수 달러로 반올림했다(flags.cents). 나머지는 정확히 같다.
        assert diff < 1 if r['token'] == 'GUSD' else diff == 0, f'{r["token"]} {r["month"]} holdings 합계 차이 {diff}'
        assert r['holdings'], (r['token'], r['month'])


def test_field_notes_states_and_nulls():
    for r in REPORTS:
        who = f'{r["token"]} {r["month"]}'
        assert set(r['field_notes']) == set(FIELDS), who
        for k, n in r['field_notes'].items():
            assert n['state'] in STATES, f'{who} {k} state {n["state"]}'
            v = r[k]
            if n['state'] in ('not_applicable', 'not_in_report'):
                assert v is None, f'{who} {k}: {n["state"]}인데 값 {v!r}'
            elif n['state'] == 'not_disclosed':
                assert v is False, f'{who} {k}: not_disclosed인데 값 {v!r}'
            else:
                assert v is not None, f'{who} {k}: found인데 값 없음'


def test_treasury_and_repo_notes_match_holdings():
    """not_applicable이면 국채(역레포) 줄이 없다. found이면 값이 줄별 만기의 최댓값이다.
    줄이 없는데 not_in_report인 경우는 USDG 역레포뿐이다. 2024-10~2025-12는 현금성 자산을 나누지 않고 한 줄로만 공시했고,
    2026-01부터는 정부 MMF가 국채 대상 역레포를 보유한다고만 적고 펀드 안 종목과 만기는 적지 않았다."""
    for r in REPORTS:
        who = f'{r["token"]} {r["month"]}'
        allh = [h for h in r['holdings'] + r['fund_holdings'] if h['amount'] > 0]
        for key, kinds in (('treasury_max_maturity_days', ('treasury_bill', 'treasury_note', 'non_us_government_bill')),
                           ('repo_max_maturity_days', ('reverse_repo_overnight', 'reverse_repo_term'))):
            hs = [h for h in allh if h['kind'] in kinds]
            st = r['field_notes'][key]['state']
            hidden = r['token'] == 'USDG' and key == 'repo_max_maturity_days'
            if hs:
                assert st in ('found', 'not_in_report'), f'{who} {key} {st}'
            else:
                assert st == ('not_in_report' if hidden else 'not_applicable'), f'{who} {key} {st}'
            if st == 'found':
                assert r[key] == max(h['maturity_max_days'] for h in hs), who


def test_asset_types_are_holdings_kinds():
    for r in REPORTS:
        kinds = sorted({h['kind'] for h in r['holdings'] if h['amount'] > 0 and h['kind'] != 'settlement'})
        assert r['asset_types'] == kinds, f'{r["token"]} {r["month"]}'


# ---- 사이트 데이터 ----

def _site():
    return json.loads(SITE.read_text(encoding='utf-8'))


def test_site_has_rule_input_fields():
    site = _site()
    assert len(site['reports']) == len(REPORTS)
    for r in site['reports']:
        for k in ('holdings', 'fund_holdings', 'asset_types', *FIELDS, 'field_notes'):
            assert k in r, f'{r["token"]} {r["month"]} 사이트 데이터에 {k} 없음'
        src = BY[(r['token'], r['month'])]
        for k in ('circulation', 'fair_value', 'components', 'as_of', 'attestation', 'asset_types', *FIELDS):
            assert r[k] == src[k], f'{r["token"]} {r["month"]} {k}가 data/ 원본과 다름'


def test_site_excluded_and_series():
    site = _site()
    assert sorted((e['token'], e['month']) for e in site['excluded']) == sorted((e['token'], e['month']) for e in EXCLUDED)
    assert all(set(e) == {'token', 'month', 'reason'} and e['reason'] for e in site['excluded'])
    for tok, exp in TMAX.items():
        s = site['series'][tok]
        ms = sorted({m for (t, m) in BY if t == tok} | {e['month'] for e in site['excluded'] if e['token'] == tok})
        assert (s['first_month'], s['last_month']) == (ms[0], ms[-1]), tok
        if tok == 'GUSD':
            assert s['not_yet_published'] == ['2026-08']
        else:
            assert s['not_yet_published'] == [], tok
    assert site['series']['PYUSD']['first_month'] == '2023-08' and site['series']['USDT']['last_month'] == '2026-06'


def test_site_size_or_stripped_text():
    """label, where가 남아 있다면 사이트 데이터는 1MB 이하여야 한다(넘으면 build_site.py가 뺀다)."""
    site = _site()
    kept = any('label' in h or 'where' in h for r in site['reports'] for h in r['holdings'] + r['fund_holdings'])
    assert not kept or SITE.stat().st_size <= 1_000_000
