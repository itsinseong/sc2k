import functools, json, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

# 기대값은 PDF 원문에서 독립 검증자가 직접 읽어 파서 값과 대조한 값이다. 파서 출력에 맞춰 바꾸지 않는다.
# 원문 금액은 센트까지 있다. 파서는 달러로 반올림하고 센트 원값은 flags.cents에 둔다. 2023-05, 2023-09, 2024-03, 2026-04 보고서는 대사 실패로 파서가 reports에서 뺐으므로 월 목록에 없다.
EXPECTED = {
    '2023-01': dict(circulation=571958626, fair_value=571958626, as_of='2023-01-31', signed='2023-02-28', cash=267068445),
    '2023-02': dict(circulation=562760934, fair_value=562760934, as_of='2023-02-28', signed='2023-03-29', cash=279749812),
    '2023-03': dict(circulation=392237856, fair_value=392237856, as_of='2023-03-31', signed='2023-04-28', cash=83842051),
    '2023-04': dict(circulation=486889531, fair_value=486889531, as_of='2023-04-28', signed='2023-05-30', cash=176924957),
    '2023-06': dict(circulation=566230295, fair_value=566230295, as_of='2023-06-30', signed='2023-07-30', cash=312468870),
    '2023-07': dict(circulation=362411618, fair_value=362411618, as_of='2023-07-31', signed='2023-08-30', cash=176416663),
    '2023-08': dict(circulation=310472293, fair_value=310472293, as_of='2023-08-31', signed='2023-09-29', cash=286275288),
    '2023-10': dict(circulation=163281567, fair_value=163281567, as_of='2023-10-31', signed='2023-11-30', cash=20612430),
    '2023-11': dict(circulation=150246564, fair_value=150246564, as_of='2023-11-30', signed='2023-12-21', cash=16859093),
    '2023-12': dict(circulation=38738140, fair_value=38738140, as_of='2023-12-29', signed='2024-01-30', cash=10768813),
    '2024-01': dict(circulation=37478807, fair_value=37478807, as_of='2024-01-31', signed='2024-02-29', cash=9184442),
    '2024-02': dict(circulation=146604590, fair_value=146604590, as_of='2024-02-29', signed='2024-03-29', cash=124337414),
    '2024-04': dict(circulation=94176469, fair_value=94176469, as_of='2024-04-30', signed='2024-05-30', cash=6114759),
    '2024-05': dict(circulation=167144550, fair_value=167144550, as_of='2024-05-31', signed='2024-06-28', cash=89262831),
    '2024-06': dict(circulation=115715310, fair_value=115715310, as_of='2024-06-28', signed='2024-07-30', cash=36838412),
    '2024-07': dict(circulation=101205063, fair_value=101205063, as_of='2024-07-31', signed='2024-08-30', cash=22010785),
    '2024-08': dict(circulation=95075089, fair_value=95075089, as_of='2024-08-30', signed='2024-09-27', cash=15916920),
    '2024-09': dict(circulation=74877618, fair_value=74877618, as_of='2024-09-30', signed='2024-10-30', cash=16294449),
    '2024-10': dict(circulation=67417232, fair_value=67417232, as_of='2024-10-31', signed='2024-11-25', cash=68629771),
    '2024-11': dict(circulation=66056789, fair_value=66056789, as_of='2024-11-29', signed='2024-12-19', cash=66196351),
    '2024-12': dict(circulation=58435216, fair_value=58435216, as_of='2024-12-31', signed='2025-01-31', cash=58684582),
    '2025-01': dict(circulation=57930423, fair_value=57930423, as_of='2025-01-31', signed='2025-02-27', cash=58304984),
    '2025-02': dict(circulation=53199204, fair_value=53199204, as_of='2025-02-28', signed='2025-03-29', cash=53689662),
    '2025-03': dict(circulation=50845959, fair_value=50845959, as_of='2025-03-31', signed='2025-04-30', cash=51453803),
    '2025-04': dict(circulation=57352229, fair_value=57352229, as_of='2025-04-30', signed='2025-05-29', cash=58431910),
    '2025-05': dict(circulation=49419839, fair_value=49419839, as_of='2025-05-30', signed='2025-06-27', cash=49687421),
    '2025-06': dict(circulation=47022449, fair_value=47022449, as_of='2025-06-30', signed='2025-07-31', cash=47187704),
    '2025-07': dict(circulation=53980249, fair_value=53980249, as_of='2025-07-31', signed='2025-08-29', cash=54295289),
    '2025-08': dict(circulation=50751408, fair_value=50751408, as_of='2025-08-29', signed='2025-09-30', cash=51221558),
    '2025-09': dict(circulation=48653635, fair_value=48653635, as_of='2025-09-30', signed='2025-10-29', cash=49196667),
    '2025-10': dict(circulation=48157034, fair_value=48157034, as_of='2025-10-31', signed='2025-11-26', cash=48910156),
    '2025-11': dict(circulation=44791274, fair_value=44791274, as_of='2025-11-28', signed='2025-12-19', cash=45664985),
    '2025-12': dict(circulation=45587226, fair_value=45587226, as_of='2025-12-31', signed='2026-01-29', cash=46577808),
    '2026-01': dict(circulation=48064766, fair_value=48064766, as_of='2026-01-30', signed='2026-02-27', cash=49172898),
    '2026-02': dict(circulation=44560166, fair_value=44560166, as_of='2026-02-27', signed='2026-03-27', cash=45072364),
    '2026-03': dict(circulation=42948974, fair_value=42948974, as_of='2026-03-31', signed='2026-04-30', cash=43571282),
    '2026-05': dict(circulation=40136855, fair_value=40136855, as_of='2026-05-29', signed='2026-06-29', cash=40637066),
    '2026-06': dict(circulation=39163190, fair_value=39163190, as_of='2026-06-30', signed='2026-08-27', cash=39757812),
    '2026-07': dict(circulation=38641266, fair_value=38641266, as_of='2026-07-31', signed='2026-10-02', cash=39332270),
}

KNOWN_FAIL = ['2023-05', '2023-09', '2024-03', '2026-04']


@functools.cache
def _reports():
    r = subprocess.run([sys.executable, str(ROOT / 'scripts/parse_gemini.py')], capture_output=True, text=True)
    # 대사 실패 보고서가 있으면 파서는 종료 코드 1을 낸다. 실패는 아래 네 달뿐이어야 하고 reports에는 들어가지 않는다.
    failed = sorted(l.split()[1] for l in r.stdout.splitlines() if l.startswith('FAIL '))
    assert failed == [f'Gemini_GUSD_Examination_{m}.pdf:' for m in KNOWN_FAIL], r.stdout + r.stderr
    return {x['month']: x for x in json.loads((ROOT / 'data/reports_gemini.json').read_text(encoding='utf-8'))['reports']}


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
    """GUSD는 AICPA examination 보고서다. 서명 이미지뿐이라 firm은 None이다."""
    for m, r in _reports().items():
        assert r['attestation']['type'] == 'examination', m
        assert r['attestation']['firm'] is None, m


def test_cents_reconcile_exactly():
    """달러 반올림 전의 센트 값으로도 구성 합계가 준비금 총액과 같다."""
    for m, r in _reports().items():
        c = r['flags']['cents']
        parts = sum(v for k, v in c.items() if k not in ('circulation', 'fair_value'))
        assert parts == c['fair_value'], m


# 규칙 입력값 기대값은 독립 검증자가 원문 PDF에서 읽은 값이다(scratchpad rule_inputs/verified.json). 파서 출력에 맞춰 바꾸지 않는다.
# 대표 달: 첫 달, 마지막 달, 값이 앞 달과 달라진 달(국채 만기 처음 등장, MMF 빠짐과 복귀, 국채 보유 끝, 은행 예금만 남음).
_BTM = ['bank_deposit', 'government_mmf', 'treasury_bill']
_BT = ['bank_deposit', 'treasury_bill']
RULE_INPUTS = {
    '2023-01': dict(asset_types=_BTM, treasury_max_maturity_days=None),
    '2023-02': dict(asset_types=_BTM, treasury_max_maturity_days=58),
    '2023-04': dict(asset_types=_BTM, treasury_max_maturity_days=25),
    '2023-06': dict(asset_types=_BT, treasury_max_maturity_days=76),
    '2023-08': dict(asset_types=_BT, treasury_max_maturity_days=14),
    '2023-10': dict(asset_types=_BTM, treasury_max_maturity_days=51),
    '2024-02': dict(asset_types=_BTM, treasury_max_maturity_days=5),
    '2024-08': dict(asset_types=_BTM, treasury_max_maturity_days=18),
    '2024-09': dict(asset_types=['bank_deposit', 'government_mmf'], treasury_max_maturity_days=None),
    '2024-10': dict(asset_types=['bank_deposit'], treasury_max_maturity_days=None),
    '2026-07': dict(asset_types=['bank_deposit'], treasury_max_maturity_days=None),
}


def test_rule_inputs_representative_months():
    got = _reports()
    for m, exp in RULE_INPUTS.items():
        r = got[m]
        assert r['asset_types'] == exp['asset_types'], f'{m} 자산 종류'
        assert r['treasury_max_maturity_days'] == exp['treasury_max_maturity_days'], f'{m} 국채 최장 만기'
        # GUSD는 39개월 내내 레포 줄이 없고, 유통량 산정 방식 문장이 없고, 보관 기관 이름과 경영진 서명이 있다.
        assert r['repo_max_maturity_days'] is None, m
        assert r['circulation_formula_disclosed'] is False, m
        assert r['custodian_disclosure'] is True, m
        assert r['management_certification'] is True, m


def test_rule_inputs_structure_all_reports():
    states = {'found', 'not_disclosed', 'not_in_report', 'not_applicable'}
    for m, r in _reports().items():
        assert abs(sum(h['amount'] for h in r['holdings']) - r['flags']['cents']['fair_value'] / 100) < 0.005, f'{m} holdings 합계'
        assert r['redemption_days'] is None and r['interest_paid'] is None, m
        for f, n in r['field_notes'].items():
            assert n['state'] in states, f'{m} {f} 상태 {n["state"]}'
            if n['state'] == 'not_applicable':
                assert r[f] is None, f'{m} {f} not_applicable인데 값 있음'
            if n['state'] == 'not_disclosed':
                assert r[f] is False, f'{m} {f} not_disclosed인데 값이 false가 아님'
