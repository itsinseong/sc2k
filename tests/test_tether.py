import functools, json, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

# 기대값은 PDF 원문에서 독립 검증자가 직접 읽어 파서 값과 대조한 값이다. 파서 출력에 맞춰 바꾸지 않는다.
# Tether는 분기 보고서(3, 6, 9, 12월)이고 기준일은 말일 그대로다(주말이어도 평일로 당기지 않는다). 구성 합계는 다른 발행사와 달리 other에 연결 재무상태표의 나머지 자산이 들어간다.
EXPECTED = {
    '2023-03': dict(circulation=79372401626, fair_value=81833149345, as_of='2023-03-31', signed='2023-05-09', cash=481350555),
    '2023-06': dict(circulation=83178020411, fair_value=86499251218, as_of='2023-06-30', signed='2023-07-31', cash=90811797),
    '2023-09': dict(circulation=83153363663, fair_value=86384653832, as_of='2023-09-30', signed='2023-10-31', cash=292641978),
    '2023-12': dict(circulation=91572956801, fair_value=97020394556, as_of='2023-12-31', signed='2024-01-31', cash=394746540),
    '2024-03': dict(circulation=104019279735, fair_value=110289406409, as_of='2024-03-31', signed='2024-04-30', cash=100264024),
    '2024-06': dict(circulation=112395445973, fair_value=118436336293, as_of='2024-06-30', signed='2024-07-31', cash=109867228),
    '2024-09': dict(circulation=119376234010, fair_value=125472000279, as_of='2024-09-30', signed='2024-10-31', cash=78413266),
    '2024-12': dict(circulation=136613782874, fair_value=143704755547, as_of='2024-12-31', signed='2025-01-31', cash=108844601),
    '2025-03': dict(circulation=143678070759, fair_value=149274515988, as_of='2025-03-31', signed='2025-04-30', cash=64302555),
    '2025-06': dict(circulation=157100255857, fair_value=162574933798, as_of='2025-06-30', signed='2025-07-31', cash=32430726),
    '2025-09': dict(circulation=174356634812, fair_value=181223149214, as_of='2025-09-30', signed='2025-10-31', cash=30100334),
    '2025-12': dict(circulation=186450610920, fair_value=192877729144, as_of='2025-12-31', signed='2026-01-30', cash=33952735),
    '2026-03': dict(circulation=183438487810, fair_value=191767741495, as_of='2026-03-31', signed='2026-04-30', cash=107021630),
    '2026-06': dict(circulation=183622105630, fair_value=187751426411, as_of='2026-06-30', signed='2026-07-31', cash=40307440),
}


@functools.cache
def _reports():
    r = subprocess.run([sys.executable, str(ROOT / 'scripts/parse_tether.py')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return {x['month']: x for x in json.loads((ROOT / 'data/reports_tether.json').read_text(encoding='utf-8'))['reports']}


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


def test_attestation_is_isae3000_reasonable_assurance():
    """Tether는 ISAE 3000 reasonable assurance 보고서다. 검증인은 2025-12부터 BDO Advisory Services S.r.l.이고 그 전은 BDO Italia S.p.A.다."""
    for m, r in _reports().items():
        a = r['attestation']
        assert a['type'] == 'reasonable assurance', m
        assert a['standard'] == 'ISAE 3000 (Revised)', m
        assert a['firm'] == ('BDO Italia S.p.A.' if m < '2025-12' else 'BDO Advisory Services S.r.l.'), m


def test_as_of_is_calendar_quarter_end():
    """Tether 기준일은 분기 말일이다(2023-09, 2023-12, 2024-03, 2024-06은 주말). 평일 규칙을 적용하면 안 된다."""
    import calendar
    for m, r in _reports().items():
        y, mo = map(int, m.split('-'))
        assert mo % 3 == 0, m
        assert r['as_of'] == f'{y}-{mo:02d}-{calendar.monthrange(y, mo)[1]:02d}', m


# 규칙 입력값 기대값은 토큰별 달마다 독립 검증자가 원문에서 확인한 값이다(verified.json). 파서 출력에 맞춰 바꾸지 않는다.
# 첫 달(2023-03), 값이 달라진 달(2025-12는 MMF 행 사라짐, 2026-03은 공개 주식 추가, 2026-06은 비미국 국채 추가), 마지막 달(2026-06)을 고른다.
_BASE = ['bank_deposit', 'bitcoin', 'corporate_bond', 'other_investment', 'precious_metal', 'reverse_repo_overnight', 'reverse_repo_term', 'secured_loan', 'treasury_bill']
RULE_EXPECTED = {
    '2023-03': sorted(_BASE + ['government_mmf', 'non_us_government_bill']),
    '2025-12': _BASE,
    '2026-03': sorted(_BASE + ['public_equity']),
    '2026-06': sorted(_BASE + ['public_equity', 'non_us_government_bill']),
}


def test_rule_inputs_representative_months():
    got = _reports()
    for m, types in RULE_EXPECTED.items():
        r = got[m]
        assert r['asset_types'] == types, f'{m} asset_types: {r["asset_types"]}'
        # Tether 원문은 국채와 레포의 종목별 만기가 없고 평균 만기만 있어 최장 만기는 모든 달 null이다.
        assert r['treasury_max_maturity_days'] is None, m
        assert r['repo_max_maturity_days'] is None, m
        assert r['circulation_formula_disclosed'] is True, m
        assert r['custodian_disclosure'] is False, m
        assert r['management_certification'] is True, m


def test_rule_inputs_structure_all_reports():
    states = {'found', 'not_disclosed', 'not_in_report', 'not_applicable'}
    for m, r in _reports().items():
        assert sum(h['amount'] for h in r['holdings']) == r['fair_value'], f'{m} holdings 합 불일치'
        assert r['redemption_days'] is None and r['interest_paid'] is None, m
        for f, n in r['field_notes'].items():
            assert n['state'] in states, f'{m} {f} state: {n["state"]}'
            if n['state'] == 'not_applicable':
                assert r[f] is None, f'{m} {f} not_applicable인데 값 있음'
            if n['state'] == 'not_disclosed':
                assert r[f] is False, f'{m} {f} not_disclosed인데 false 아님'
