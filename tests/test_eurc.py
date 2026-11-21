import functools, json, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

# 기대값은 PDF 원문에서 독립 검증자가 직접 읽어 파서 값과 대조한 값이다. 파서 출력에 맞춰 바꾸지 않는다.
# EURC는 유로 준비금이라 금액 단위가 EUR이다. Circle 파서(parse_circle.py)가 USDC와 EURC를 같이 읽고 EURC는 data/reports_eurc.json에 쓴다.
EXPECTED = {
    '2023-01': dict(circulation=31077321, fair_value=31077321, as_of='2023-01-31', signed='2023-03-02', cash=31288991),
    '2023-02': dict(circulation=29807117, fair_value=29807117, as_of='2023-02-28', signed='2023-03-30', cash=29807164),
    '2023-03': dict(circulation=31068113, fair_value=31318984, as_of='2023-03-31', signed='2023-04-28', cash=31571321),
    '2023-04': dict(circulation=48171006, fair_value=48421985, as_of='2023-04-28', signed='2023-05-30', cash=48655531),
    '2023-05': dict(circulation=48157539, fair_value=48408644, as_of='2023-05-31', signed='2023-06-30', cash=48684736),
    '2023-06': dict(circulation=47917232, fair_value=48168455, as_of='2023-06-30', signed='2023-07-28', cash=48271939),
    '2023-07': dict(circulation=47725692, fair_value=47976927, as_of='2023-07-31', signed='2023-08-30', cash=48089738),
    '2023-08': dict(circulation=49225433, fair_value=49476668, as_of='2023-08-31', signed='2023-09-29', cash=49708789),
    '2023-09': dict(circulation=49354779, fair_value=49606006, as_of='2023-09-29', signed='2023-10-30', cash=49728538),
    '2023-11': dict(circulation=51397804, fair_value=51649035, as_of='2023-11-30', signed='2023-12-22', cash=51779694),
    '2023-12': dict(circulation=52199724, fair_value=52450950, as_of='2023-12-29', signed='2024-01-30', cash=52577183),
    '2024-01': dict(circulation=51734446, fair_value=51985679, as_of='2024-01-31', signed='2024-02-29', cash=52051081),
    '2024-02': dict(circulation=48474978, fair_value=48726194, as_of='2024-02-29', signed='2024-03-30', cash=48856104),
    '2024-03': dict(circulation=51257692, fair_value=52009000, as_of='2024-03-29', signed='2024-04-30', cash=52145177),
    '2024-04': dict(circulation=40749720, fair_value=41501157, as_of='2024-04-30', signed='2024-05-30', cash=41881030),
    '2024-05': dict(circulation=36995250, fair_value=37746702, as_of='2024-05-31', signed='2024-06-27', cash=37851861),
    '2024-06': dict(circulation=35434916, fair_value=36186236, as_of='2024-06-28', signed='2024-07-30', cash=36697000),
    '2024-07': dict(circulation=35419463, fair_value=36172122, as_of='2024-07-31', signed='2024-08-28', cash=35106353),
    '2024-08': dict(circulation=52867999, fair_value=53620711, as_of='2024-08-30', signed='2024-09-27', cash=53953752),
    '2024-09': dict(circulation=61976108, fair_value=62728914, as_of='2024-09-30', signed='2024-10-30', cash=62908455),
    '2024-10': dict(circulation=81713273, fair_value=82465938, as_of='2024-10-31', signed='2024-11-26', cash=83012237),
    '2024-11': dict(circulation=87759186, fair_value=88509695, as_of='2024-11-29', signed='2024-12-20', cash=87182480),
    '2024-12': dict(circulation=80705696, fair_value=81456210, as_of='2024-12-31', signed='2025-01-30', cash=104925677),
    '2025-01': dict(circulation=101293431, fair_value=102043948, as_of='2025-01-31', signed='2025-02-27', cash=102075725),
    '2025-02': dict(circulation=115640112, fair_value=116390630, as_of='2025-02-28', signed='2025-03-28', cash=112800881),
    '2025-03': dict(circulation=170726017, fair_value=171476538, as_of='2025-03-31', signed='2025-04-30', cash=139571789),
    '2025-04': dict(circulation=201534426, fair_value=202284947, as_of='2025-04-30', signed='2025-05-29', cash=211202029),
    '2025-05': dict(circulation=188175019, fair_value=188925542, as_of='2025-05-30', signed='2025-06-27', cash=188929799),
    '2025-06': dict(circulation=171793247, fair_value=172543770, as_of='2025-06-30', signed='2025-07-30', cash=172544021),
    '2025-07': dict(circulation=180600510, fair_value=181351029, as_of='2025-07-31', signed='2025-08-29', cash=181351280),
    '2025-08': dict(circulation=203610054, fair_value=204360573, as_of='2025-08-29', signed='2025-09-30', cash=204131533),
    '2025-09': dict(circulation=214594363, fair_value=215344883, as_of='2025-09-30', signed='2025-10-30', cash=215356693),
    '2025-10': dict(circulation=241565152, fair_value=244315671, as_of='2025-10-31', signed='2025-11-26', cash=247122082),
    '2025-11': dict(circulation=286688320, fair_value=289438841, as_of='2025-11-28', signed='2025-12-19', cash=289618902),
    '2025-12': dict(circulation=309608590, fair_value=312359116, as_of='2025-12-31', signed='2026-01-30', cash=314042591),
    '2026-01': dict(circulation=347804540, fair_value=350555067, as_of='2026-01-30', signed='2026-02-26', cash=350555401),
    '2026-02': dict(circulation=393662772, fair_value=396413298, as_of='2026-02-27', signed='2026-03-27', cash=396560668),
    '2026-03': dict(circulation=357896076, fair_value=360646610, as_of='2026-03-31', signed='2026-04-29', cash=362379695),
    '2026-04': dict(circulation=371443746, fair_value=374194276, as_of='2026-04-30', signed='2026-05-28', cash=376595996),
    '2026-05': dict(circulation=372655505, fair_value=375406036, as_of='2026-05-29', signed='2026-06-29', cash=373377679),
    '2026-06': dict(circulation=381986779, fair_value=384737359, as_of='2026-06-30', signed='2026-07-29', cash=389833314),
    '2026-07': dict(circulation=397363133, fair_value=400113753, as_of='2026-07-31', signed='2026-08-27', cash=400053404),
    '2026-08': dict(circulation=390534293, fair_value=393284908, as_of='2026-08-31', signed='2026-09-29', cash=395424211),
    '2026-09': dict(circulation=412549121, fair_value=415299735, as_of='2026-09-30', signed='2026-10-26', cash=415354210),
}


@functools.cache
def _reports():
    r = subprocess.run([sys.executable, str(ROOT / 'scripts/parse_circle.py')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return {x['month']: x for x in json.loads((ROOT / 'data/reports_eurc.json').read_text(encoding='utf-8'))['reports']}


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
    """Circle은 AICPA attestation standards의 examination 보고서다. 서명 이미지뿐이라 firm은 None이다."""
    for m, r in _reports().items():
        assert r['attestation']['type'] == 'examination', m
        assert r['attestation']['firm'] is None, m
        assert r['reserve_currency'] == 'EUR', m


# 규칙 입력값 기대값은 독립 검증자가 PDF 원문에서 직접 읽은 값이다(verified.json). EURC는 은행 예금만 있어 국채와 레포 만기는 전 달 해당 없음(None)이다.
# 항목: 보관 기관 공개 여부. 2023-01~08은 은행 이름이 나오고 2023-09부터 없다. 유통량 계산식 공개와 경영진 서명은 전 달 True다.
RULE_INPUTS = {'2023-01': True, '2023-08': True, '2023-09': False, '2024-07': False, '2025-11': False, '2026-08': False}


def test_rule_inputs_representative_months():
    got = _reports()
    for m, cust in RULE_INPUTS.items():
        r = got[m]
        assert r['treasury_max_maturity_days'] is None, m
        assert r['repo_max_maturity_days'] is None, m
        assert r['asset_types'] == ['bank_deposit'], m
        assert r['circulation_formula_disclosed'] is True, m
        assert r['custodian_disclosure'] is cust, m
        assert r['management_certification'] is True, m


def test_rule_inputs_structure_all_reports():
    STATES = {'found', 'not_disclosed', 'not_in_report', 'not_applicable'}
    for m, r in _reports().items():
        assert sum(h['amount'] for h in r['holdings']) == r['fair_value'], f'{m} holdings 합계 불일치'
        assert r['redemption_days'] is None and r['interest_paid'] is None, m
        for f, n in r['field_notes'].items():
            assert n['state'] in STATES, f'{m} {f} state={n["state"]}'
            if n['state'] == 'not_applicable':
                assert r[f] is None, f'{m} {f} not_applicable인데 값이 있다'
            if n['state'] == 'not_disclosed':
                assert r[f] is False, f'{m} {f} not_disclosed인데 값이 False가 아니다'
