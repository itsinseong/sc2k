import functools, json, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

# 기대값은 PDF 원문에서 독립 검증자가 직접 읽어 파서 값과 대조한 값이다. 파서 출력에 맞춰 바꾸지 않는다.
# 스캔본 쪽은 OCR로 읽는다(느림). 그래서 파서는 모듈마다 한 번만 돌린다.
EXPECTED = {
    '2024-12': dict(circulation=77208201, fair_value=83214671, as_of='2024-12-31', signed='2025-01-23', cash=22978696),
    '2025-01': dict(circulation=106666737, fair_value=115373144, as_of='2025-01-31', signed='2025-02-21', cash=31389878),
    '2025-02': dict(circulation=132416737, fair_value=139533257, as_of='2025-02-28', signed='2025-03-21', cash=42206630),
    '2025-03': dict(circulation=193692686, fair_value=202959289, as_of='2025-03-31', signed='2025-04-21', cash=100778550),
    '2025-04': dict(circulation=317042712, fair_value=329080840, as_of='2025-04-30', signed='2025-05-22', cash=48049698),
    '2025-05': dict(circulation=309043794, fair_value=322099766, as_of='2025-05-30', signed='2025-06-23', cash=43128885),
    '2025-06': dict(circulation=455243694, fair_value=471227699, as_of='2025-06-30', signed='2025-07-24', cash=70647552),
    '2025-07': dict(circulation=602743524, fair_value=622827197, as_of='2025-07-31', signed='2025-08-25', cash=115045087),
    '2025-08': dict(circulation=701950756, fair_value=728158022, as_of='2025-08-29', signed='2025-09-26', cash=107943638),
    '2025-09': dict(circulation=789696777, fair_value=823429425, as_of='2025-09-30', signed='2025-10-22', cash=123093692),
    '2025-10': dict(circulation=963198083, fair_value=1023817752, as_of='2025-10-31', signed='2025-11-24', cash=214890814),
    '2025-11': dict(circulation=1260898084, fair_value=1314484291, as_of='2025-11-28', signed='2025-12-19', cash=218835575),
    '2025-12': dict(circulation=1278206224, fair_value=1337307954, as_of='2025-12-31', signed='2026-01-26', cash=131338082),
    '2026-01': dict(circulation=1357255995, fair_value=1422590657, as_of='2026-01-30', signed='2026-02-25', cash=180689459),
    '2026-02': dict(circulation=1495023851, fair_value=1568986016, as_of='2026-02-27', signed='2026-03-26', cash=254840348),
    '2026-03': dict(circulation=1237271090, fair_value=1316184523, as_of='2026-03-31', signed='2026-04-27', cash=248144415),
    '2026-04': dict(circulation=1443684832, fair_value=1546747642, as_of='2026-04-30', signed='2026-05-28', cash=250005880),
    '2026-05': dict(circulation=1690410925, fair_value=1773001906, as_of='2026-05-29', signed='2026-06-25', cash=269247197),
    '2026-06': dict(circulation=1411034124, fair_value=1512689493, as_of='2026-06-30', signed='2026-07-29', cash=242129766),
    '2026-07': dict(circulation=1463694758, fair_value=1575160913, as_of='2026-07-31', signed='2026-08-27', cash=239096420),
    '2026-08': dict(circulation=2325969308, fair_value=2446312864, as_of='2026-08-31', signed='2026-09-29', cash=421617153),
    '2026-09': dict(circulation=2399995528, fair_value=2524008274, as_of='2026-09-30', signed='2026-10-26', cash=378585861),
}


@functools.cache
def _reports():
    r = subprocess.run([sys.executable, str(ROOT / 'scripts/parse_ripple.py')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return {x['month']: x for x in json.loads((ROOT / 'data/reports_ripple.json').read_text(encoding='utf-8'))['reports']}


def test_all_months_parse_and_reconcile():
    got = _reports()
    assert set(got) == set(EXPECTED), f'월 목록 불일치: {sorted(set(got) ^ set(EXPECTED))}'
    for m, exp in EXPECTED.items():
        r = got[m]
        assert r['ok'], f'{m} 대사 실패: {r["reconciliation"]}'
        assert r['circulation'] == exp['circulation'], m
        assert r['fair_value'] == exp['fair_value'], m
        assert r['as_of'] == exp['as_of'], m
        assert r['attestation']['signed'] == exp['signed'], m
        assert r['components']['cash'] == exp['cash'], f'{m} 은행 예금 불일치: {r["components"]["cash"]}'
        assert r['fair_value'] >= r['circulation'], m


def test_components_sum_matches_fair_value():
    for m, r in _reports().items():
        assert sum(r['components'].values()) == r['fair_value'], f'{m} 구성 합계 불일치'


def test_attestation_is_examination():
    """RLUSD는 AICPA examination 보고서다. firm은 글자에 나온 때만 채우고(2026-02, 2026-03 Deloitte & Touche LLP), 나머지는 None이다."""
    for m, r in _reports().items():
        assert r['attestation']['type'] == 'examination', m
        want = 'Deloitte & Touche LLP' if m in ('2026-02', '2026-03') else None
        assert r['attestation']['firm'] == want, m


def test_as_of_is_last_weekday_of_month():
    import calendar, datetime
    for m, r in _reports().items():
        d = datetime.date(*map(int, m.split('-')), calendar.monthrange(*map(int, m.split('-')))[1])
        while d.weekday() >= 5:
            d -= datetime.timedelta(days=1)
        assert r['as_of'] == d.isoformat(), m


# 규칙 입력값 기대값: 독립 검증자가 원문에서 확인한 값(verified.json의 RLUSD 21개월). 국채 최장 만기(일)는 달마다 다르다.
# 2025-06은 월말 T-bill이 0이라 null이다. 레포는 어느 달에도 없어 null, 보관 기관은 전 달 미공개다.
TREASURY_DAYS = {
    '2024-12': 7, '2025-01': 4, '2025-02': 4, '2025-03': 1, '2025-04': 1, '2025-05': 4, '2025-06': None,
    '2025-07': 5, '2025-08': 25, '2025-09': 56, '2025-10': 90, '2025-11': 76, '2025-12': 85,
    '2026-01': 55, '2026-02': 62, '2026-03': 86, '2026-04': 77, '2026-05': 69, '2026-06': 86,
    '2026-07': 83, '2026-08': 88, '2026-09': 90,
}


def test_rule_inputs_match_verified_values():
    got = _reports()
    assert set(TREASURY_DAYS) == set(got)
    for m, days in TREASURY_DAYS.items():
        r = got[m]
        assert r['treasury_max_maturity_days'] == days, m
        assert r['repo_max_maturity_days'] is None, m
        want = ['bank_deposit', 'government_mmf'] + ([] if days is None else ['treasury_bill'])
        assert sorted(r['asset_types']) == want, m
        assert r['circulation_formula_disclosed'] is False, m  # D-06: 정의 문장만 있음
        assert r['custodian_disclosure'] is False, m
        assert r['management_certification'] is True, m


def test_rule_inputs_structure():
    states = {'found', 'not_disclosed', 'not_in_report', 'not_applicable'}
    for m, r in _reports().items():
        assert sum(h['amount'] for h in r['holdings']) == r['fair_value'], f'{m} holdings 합계 불일치'
        assert r['redemption_days'] is None and r['interest_paid'] is None, m
        for f, n in r['field_notes'].items():
            assert n['state'] in states, f'{m} {f} state={n["state"]}'
            if n['state'] == 'not_applicable':
                assert r.get(f) is None, f'{m} {f} not_applicable인데 값이 있다'
            if n['state'] == 'not_disclosed':
                assert r.get(f) is False, f'{m} {f} not_disclosed인데 false가 아니다'
