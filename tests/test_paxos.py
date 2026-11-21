import functools, json, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

# 기대값은 PDF 원문에서 독립 검증자가 직접 읽어 파서 값과 대조한 값(2026-07은 data/samples/Paxos_*_Examination_2026-07.txt 직접 확인).
EXPECTED = {
    ('PYUSD', '2023-08'): dict(circulation=44376440, fair_value=45361493, as_of='2023-08-31', signed='2023-09-21'),
    ('PYUSD', '2023-09'): dict(circulation=94396540, fair_value=96460833, as_of='2023-09-29', signed='2023-10-18'),
    ('PYUSD', '2023-10'): dict(circulation=158956937, fair_value=162721994, as_of='2023-10-31', signed='2023-11-14'),
    ('PYUSD', '2023-11'): dict(circulation=156753068, fair_value=160593198, as_of='2023-11-30', signed='2023-12-15'),
    ('PYUSD', '2023-12'): dict(circulation=264531846, fair_value=270731892, as_of='2023-12-29', signed='2024-01-22'),
    ('PYUSD', '2024-01'): dict(circulation=301175241, fair_value=308523572, as_of='2024-01-31', signed='2024-02-28'),
    ('PYUSD', '2024-02'): dict(circulation=304427933, fair_value=311839014, as_of='2024-02-29', signed='2024-03-20'),
    ('PYUSD', '2024-03'): dict(circulation=188485924, fair_value=192863328, as_of='2024-03-29', signed='2024-04-22'),
    ('PYUSD', '2024-04'): dict(circulation=328083118, fair_value=335352011, as_of='2024-04-30', signed='2024-05-17'),
    ('PYUSD', '2024-05'): dict(circulation=444103023, fair_value=454251277, as_of='2024-05-31', signed='2024-06-21'),
    ('PYUSD', '2024-06'): dict(circulation=499487564, fair_value=510204106, as_of='2024-06-28', signed='2024-07-17'),
    ('PYUSD', '2024-08'): dict(circulation=908164708, fair_value=924348143, as_of='2024-08-30', signed='2024-09-23'),
    ('PYUSD', '2024-09'): dict(circulation=704883091, fair_value=720152403, as_of='2024-09-30', signed='2024-10-16'),
    ('PYUSD', '2024-10'): dict(circulation=570851729, fair_value=583791579, as_of='2024-10-31', signed='2024-11-18'),
    ('PYUSD', '2024-11'): dict(circulation=539827757, fair_value=551145414, as_of='2024-11-29', signed='2024-12-27'),
    ('PYUSD', '2024-12'): dict(circulation=497959719, fair_value=509395838, as_of='2024-12-31', signed='2025-01-20'),
    ('PYUSD', '2025-01'): dict(circulation=482747103, fair_value=484456701, as_of='2025-01-31', signed='2025-02-28'),
    ('PYUSD', '2025-02'): dict(circulation=751638595, fair_value=753544744, as_of='2025-02-28', signed='2025-03-28'),
    ('PYUSD', '2025-03'): dict(circulation=744827297, fair_value=747497079, as_of='2025-03-31', signed='2025-04-29'),
    ('PYUSD', '2025-04'): dict(circulation=887766152, fair_value=890506892, as_of='2025-04-30', signed='2025-05-28'),
    ('PYUSD', '2025-05'): dict(circulation=906606815, fair_value=909579635, as_of='2025-05-30', signed='2025-06-25'),
    ('PYUSD', '2025-06'): dict(circulation=950362292, fair_value=953684788, as_of='2025-06-30', signed='2025-07-28'),
    ('PYUSD', '2025-07'): dict(circulation=1037124620, fair_value=1040131414, as_of='2025-07-31', signed='2025-08-26'),
    ('PYUSD', '2025-08'): dict(circulation=1169714720, fair_value=1173383198, as_of='2025-08-29', signed='2025-09-29'),
    ('PYUSD', '2025-09'): dict(circulation=2432687333, fair_value=2437877550, as_of='2025-09-30', signed='2025-10-28'),
    ('PYUSD', '2025-10'): dict(circulation=2814793868, fair_value=2824669787, as_of='2025-10-31', signed='2025-11-24'),
    ('PYUSD', '2025-11'): dict(circulation=3847610644, fair_value=3858115385, as_of='2025-11-28', signed='2025-12-23'),
    ('PYUSD', '2025-12'): dict(circulation=3604579180, fair_value=3617530827, as_of='2025-12-31', signed='2026-01-23'),
    ('PYUSD', '2026-01'): dict(circulation=3608697613, fair_value=3622145209, as_of='2026-01-30', signed='2026-02-26'),
    ('PYUSD', '2026-02'): dict(circulation=4188341569, fair_value=4201086728, as_of='2026-02-27', signed='2026-03-24'),
    ('PYUSD', '2026-03'): dict(circulation=3905879288, fair_value=3919760406, as_of='2026-03-31', signed='2026-04-24'),
    ('PYUSD', '2026-04'): dict(circulation=3372021912, fair_value=3386175889, as_of='2026-04-30', signed='2026-05-27'),
    ('PYUSD', '2026-05'): dict(circulation=3019072414, fair_value=3030833747, as_of='2026-05-29', signed='2026-06-25'),
    ('PYUSD', '2026-06'): dict(circulation=2686586963, fair_value=2693757338, as_of='2026-06-30', signed='2026-07-24'),
    ('PYUSD', '2026-07'): dict(circulation=2689335674, fair_value=2694072163, as_of='2026-07-31', signed='2026-08-25'),
    ('PYUSD', '2026-08'): dict(circulation=2886948845, fair_value=2893935877, as_of='2026-08-31', signed='2026-09-24'),
    ('PYUSD', '2026-09'): dict(circulation=2747625868, fair_value=2754709360, as_of='2026-09-30', signed='2026-10-23'),
    ('USDP', '2023-01'): dict(circulation=969514797, fair_value=981761482, as_of='2023-01-31', signed='2023-02-27'),
    ('USDP', '2023-02'): dict(circulation=766369357, fair_value=776277036, as_of='2023-02-28', signed='2023-03-21'),
    ('USDP', '2023-03'): dict(circulation=757552716, fair_value=768331155, as_of='2023-03-31', signed='2023-04-19'),
    ('USDP', '2023-04'): dict(circulation=1041056795, fair_value=1060369224, as_of='2023-04-28', signed='2023-05-10'),
    ('USDP', '2023-05'): dict(circulation=1027011081, fair_value=1044987680, as_of='2023-05-31', signed='2023-06-22'),
    ('USDP', '2023-06'): dict(circulation=986890936, fair_value=1006580250, as_of='2023-06-30', signed='2023-07-20'),
    ('USDP', '2023-07'): dict(circulation=549583263, fair_value=558881467, as_of='2023-07-31', signed='2023-08-17'),
    ('USDP', '2023-08'): dict(circulation=505170765, fair_value=512589593, as_of='2023-08-31', signed='2023-09-15'),
    ('USDP', '2023-09'): dict(circulation=486062949, fair_value=491398017, as_of='2023-09-29', signed='2023-10-18'),
    ('USDP', '2023-10'): dict(circulation=438824451, fair_value=445266577, as_of='2023-10-31', signed='2023-11-14'),
    ('USDP', '2023-11'): dict(circulation=446640157, fair_value=451291387, as_of='2023-11-30', signed='2023-12-15'),
    ('USDP', '2023-12'): dict(circulation=372639175, fair_value=377969477, as_of='2023-12-29', signed='2024-01-30'),
    ('USDP', '2024-01'): dict(circulation=353101046, fair_value=355500160, as_of='2024-01-31', signed='2024-02-28'),
    ('USDP', '2024-02'): dict(circulation=203051111, fair_value=205455608, as_of='2024-02-29', signed='2024-03-18'),
    ('USDP', '2024-03'): dict(circulation=147984690, fair_value=149191905, as_of='2024-03-29', signed='2024-04-22'),
    ('USDP', '2024-04'): dict(circulation=148503536, fair_value=149776167, as_of='2024-04-30', signed='2024-05-17'),
    ('USDP', '2024-05'): dict(circulation=145982340, fair_value=147279620, as_of='2024-05-31', signed='2024-06-21'),
    ('USDP', '2024-06'): dict(circulation=121706620, fair_value=122462052, as_of='2024-06-28', signed='2024-07-17'),
    ('USDP', '2024-07'): dict(circulation=114706089, fair_value=115438715, as_of='2024-07-31', signed='2024-08-13'),
    ('USDP', '2024-08'): dict(circulation=106940788, fair_value=107519419, as_of='2024-08-30', signed='2024-09-19'),
    ('USDP', '2024-09'): dict(circulation=107115484, fair_value=107129837, as_of='2024-09-30', signed='2024-10-16'),
    ('USDP', '2024-10'): dict(circulation=110099031, fair_value=110262333, as_of='2024-10-31', signed='2024-11-18'),
    ('USDP', '2024-11'): dict(circulation=103115718, fair_value=103162626, as_of='2024-11-29', signed='2024-12-18'),
    ('USDP', '2024-12'): dict(circulation=93477695, fair_value=93590466, as_of='2024-12-31', signed='2025-01-20'),
    ('USDP', '2025-01'): dict(circulation=80050903, fair_value=80364541, as_of='2025-01-31', signed='2025-02-28'),
    ('USDP', '2025-02'): dict(circulation=80578596, fair_value=80829428, as_of='2025-02-28', signed='2025-03-28'),
    ('USDP', '2025-03'): dict(circulation=79443384, fair_value=79487100, as_of='2025-03-31', signed='2025-04-29'),
    ('USDP', '2025-04'): dict(circulation=71319225, fair_value=71352992, as_of='2025-04-30', signed='2025-05-28'),
    ('USDP', '2025-05'): dict(circulation=73223449, fair_value=73238801, as_of='2025-05-30', signed='2025-06-25'),
    ('USDP', '2025-06'): dict(circulation=67953449, fair_value=67967318, as_of='2025-06-30', signed='2025-07-28'),
    ('USDP', '2025-07'): dict(circulation=64953459, fair_value=64963877, as_of='2025-07-31', signed='2025-08-26'),
    ('USDP', '2025-08'): dict(circulation=66953468, fair_value=66968807, as_of='2025-08-29', signed='2025-09-29'),
    ('USDP', '2025-09'): dict(circulation=63264568, fair_value=63284396, as_of='2025-09-30', signed='2025-10-28'),
    ('USDP', '2025-10'): dict(circulation=55711456, fair_value=55732558, as_of='2025-10-31', signed='2025-11-24'),
    ('USDP', '2025-11'): dict(circulation=57569455, fair_value=57598157, as_of='2025-11-28', signed='2025-12-23'),
    ('USDP', '2025-12'): dict(circulation=47569455, fair_value=47623184, as_of='2025-12-31', signed='2026-01-23'),
    ('USDP', '2026-01'): dict(circulation=47569455, fair_value=47608970, as_of='2026-01-30', signed='2026-02-26'),
    ('USDP', '2026-02'): dict(circulation=40569453, fair_value=40603453, as_of='2026-02-27', signed='2026-03-24'),
    ('USDP', '2026-03'): dict(circulation=40569461, fair_value=40590082, as_of='2026-03-31', signed='2026-04-24'),
    ('USDP', '2026-04'): dict(circulation=40569460, fair_value=40588300, as_of='2026-04-30', signed='2026-05-27'),
    ('USDP', '2026-05'): dict(circulation=31954027, fair_value=31972770, as_of='2026-05-29', signed='2026-06-25'),
    ('USDP', '2026-06'): dict(circulation=31954027, fair_value=31977534, as_of='2026-06-30', signed='2026-07-24'),
    ('USDP', '2026-07'): dict(circulation=31954027, fair_value=31975703, as_of='2026-07-31', signed='2026-08-25'),
    ('USDP', '2026-08'): dict(circulation=29168261, fair_value=29189905, as_of='2026-08-31', signed='2026-09-24'),
    ('USDP', '2026-09'): dict(circulation=26084307, fair_value=26113649, as_of='2026-09-30', signed='2026-10-23'),
    ('USDG', '2024-10'): dict(circulation=10750140, fair_value=10757815, as_of='2024-10-31', signed='2024-11-27'),
    ('USDG', '2024-11'): dict(circulation=29386864, fair_value=29467869, as_of='2024-11-29', signed='2024-12-27'),
    ('USDG', '2024-12'): dict(circulation=29860177, fair_value=30049879, as_of='2024-12-31', signed='2025-01-28'),
    ('USDG', '2025-01'): dict(circulation=37007580, fair_value=37239743, as_of='2025-01-31', signed='2025-02-28'),
    ('USDG', '2025-02'): dict(circulation=117651317, fair_value=118253500, as_of='2025-02-28', signed='2025-03-26'),
    ('USDG', '2025-03'): dict(circulation=189048942, fair_value=189635253, as_of='2025-03-31', signed='2025-04-28'),
    ('USDG', '2025-04'): dict(circulation=238227303, fair_value=238772158, as_of='2025-04-30', signed='2025-05-29'),
    ('USDG', '2025-05'): dict(circulation=313642614, fair_value=314192325, as_of='2025-05-30', signed='2025-06-27'),
    ('USDG', '2025-06'): dict(circulation=324890204, fair_value=325281956, as_of='2025-06-30', signed='2025-07-29'),
    ('USDG', '2025-07'): dict(circulation=313710454, fair_value=314300307, as_of='2025-07-31', signed='2025-08-26'),
    ('USDG', '2025-08'): dict(circulation=553678623, fair_value=555580297, as_of='2025-08-29', signed='2025-09-24'),
    ('USDG', '2025-09'): dict(circulation=730514012, fair_value=732896229, as_of='2025-09-30', signed='2025-10-28'),
    ('USDG', '2025-10'): dict(circulation=1005923645, fair_value=1006587646, as_of='2025-10-31', signed='2025-11-24'),
    ('USDG', '2025-11'): dict(circulation=1230553949, fair_value=1234120131, as_of='2025-11-28', signed='2025-12-29'),
    ('USDG', '2025-12'): dict(circulation=1529283030, fair_value=1538375883, as_of='2025-12-31', signed='2026-01-24'),
    ('USDG', '2026-01'): dict(circulation=1590150523, fair_value=1595949747, as_of='2026-01-30', signed='2026-02-27'),
    ('USDG', '2026-02'): dict(circulation=1767447250, fair_value=1769033199, as_of='2026-02-27', signed='2026-03-26'),
    ('USDG', '2026-03'): dict(circulation=1846711210, fair_value=1851063917, as_of='2026-03-31', signed='2026-04-29'),
    ('USDG', '2026-04'): dict(circulation=2439082259, fair_value=2444192275, as_of='2026-04-30', signed='2026-05-28'),
    ('USDG', '2026-05'): dict(circulation=2632390397, fair_value=2638846632, as_of='2026-05-29', signed='2026-06-25'),
    ('USDG', '2026-06'): dict(circulation=2984505939, fair_value=2989975984, as_of='2026-06-30', signed='2026-07-24'),
    ('USDG', '2026-07'): dict(circulation=3400474143, fair_value=3404876225, as_of='2026-07-31', signed='2026-08-26'),
    ('USDG', '2026-08'): dict(circulation=3340650602, fair_value=3350462467, as_of='2026-08-31', signed='2026-09-25'),
    ('USDG', '2026-09'): dict(circulation=3164996248, fair_value=3168423407, as_of='2026-09-30', signed='2026-10-23'),
}


@functools.cache
def _reports():
    r = subprocess.run([sys.executable, str(ROOT / 'scripts/parse_paxos.py')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return {(x['token'], x['month']): x for x in json.loads((ROOT / 'data/reports_paxos.json').read_text(encoding='utf-8'))['reports']}


def test_all_reports_parse_and_reconcile():
    got = _reports()
    assert set(got) == set(EXPECTED), f'(토큰, 월) 목록 불일치: {sorted(set(got) ^ set(EXPECTED))}'
    for key, exp in EXPECTED.items():
        r = got[key]
        assert r['ok'], f'{key} 대사 실패: {r["reconciliation"]}'
        assert r['circulation'] == exp['circulation'], key
        assert r['fair_value'] == exp['fair_value'], key
        assert r['as_of'] == exp['as_of'], key
        assert r['attestation']['signed'] == exp['signed'], key
        assert r['fair_value'] >= r['circulation'], key


def test_components_sum_matches_fair_value():
    got = _reports()
    for key, r in got.items():
        assert sum(v or 0 for v in r['components'].values()) == r['fair_value'], f'{key} 구성 합계 불일치'


def test_usdg_legacy_bank_deposit_is_unknown_not_zero():
    """USDG 2024-10~2025-12는 원문이 은행 예금과 MMF를 나누지 않는다. 0으로 두면 판정기가 '은행 예금 0%, 미충족'으로 읽는다."""
    got = _reports()
    legacy = [r for (tok, m), r in got.items() if tok == 'USDG' and '2024-10' <= m <= '2025-12']
    assert len(legacy) == 15
    for r in legacy:
        assert r['components']['cash'] is None and r['flags']['cash_is_bank_deposit'] is False, r['month']


def test_firm_follows_report_era():
    """firm은 보고서 글자에 나온 이름이다. PYUSD, USDP는 2023~2024년 보고서에 로고와 서명이 이미지뿐이라 None이고(flags.firm_signature_image),
    2025-01부터 KPMG LLP다. USDG는 2024-10~2025-12가 Enrome LLP, 2026년부터 KPMG LLP다."""
    got = _reports()
    for (tok, m), r in got.items():
        firm = r['attestation']['firm']
        if tok == 'USDG':
            want = 'Enrome LLP' if m < '2026-01' else 'KPMG LLP'
        else:
            want = None if m < '2025-01' else 'KPMG LLP'
        assert firm == want, (tok, m, firm)


def test_usdg_uses_reasonable_assurance_from_2026():
    """USDG는 2026-01부터 싱가포르 SSAE 3000 reasonable assurance 보고서다. 2024-10~2025-12 보고서 제목은 examination 그대로다. 회귀 지점."""
    got = _reports()
    for (tok, m), r in got.items():
        want = 'reasonable assurance' if (tok == 'USDG' and m >= '2026-01') else 'examination'
        assert r['attestation']['type'] == want, (tok, m)


# 규칙 입력값 기대값. 독립 검증자가 원문에서 확인한 값만 쓴다(첫 달, 마지막 달, 값이 앞 달과 달라진 달).
RULE_INPUTS = {
    ('PYUSD', '2023-08'): dict(treasury=None, repo=1, types=['bank_deposit', 'reverse_repo_overnight'], formula=False, custodian=False, cert=True),
    ('PYUSD', '2024-01'): dict(treasury=27, repo=1, types=['bank_deposit', 'reverse_repo_overnight', 'treasury_bill'], formula=False, custodian=False, cert=True),
    ('PYUSD', '2024-02'): dict(treasury=None, repo=1, types=['bank_deposit', 'reverse_repo_overnight'], formula=False, custodian=False, cert=True),
    ('PYUSD', '2025-01'): dict(treasury=None, repo=1, types=['bank_deposit', 'reverse_repo_overnight'], formula=True, custodian=False, cert=True),
    ('PYUSD', '2026-05'): dict(treasury=None, repo=1, types=['bank_deposit', 'reverse_repo_overnight'], formula=True, custodian=False, cert=True),
    ('PYUSD', '2026-08'): dict(treasury=31, repo=1, types=['bank_deposit', 'reverse_repo_overnight', 'treasury_bill'], formula=True, custodian=False, cert=True),
    ('PYUSD', '2026-09'): dict(treasury=36, repo=1, types=['bank_deposit', 'reverse_repo_overnight', 'treasury_bill'], formula=True, custodian=False, cert=True),
    ('USDP', '2023-01'): dict(treasury=23, repo=1, types=['bank_deposit', 'reverse_repo_overnight', 'treasury_bill'], formula=False, custodian=False, cert=True),
    ('USDP', '2023-12'): dict(treasury=None, repo=1, types=['bank_deposit', 'reverse_repo_overnight'], formula=False, custodian=False, cert=True),
    ('USDP', '2024-09'): dict(treasury=None, repo=None, types=['bank_deposit'], formula=False, custodian=False, cert=True),
    ('USDP', '2024-10'): dict(treasury=None, repo=1, types=['bank_deposit', 'reverse_repo_overnight'], formula=False, custodian=False, cert=True),
    ('USDP', '2025-01'): dict(treasury=None, repo=1, types=['bank_deposit', 'reverse_repo_overnight'], formula=True, custodian=False, cert=True),
    ('USDG', '2024-10'): dict(treasury=5, repo=None, types=['cash_equivalents_unsplit', 'treasury_bill'], formula=False, custodian=False, cert=True),
    ('USDG', '2025-09'): dict(treasury=30, repo=None, types=['cash_equivalents_unsplit', 'treasury_bill'], formula=False, custodian=True, cert=True),
    ('USDG', '2026-01'): dict(treasury=83, repo=None, types=['bank_deposit', 'government_mmf', 'treasury_bill'], formula=True, custodian=False, cert=True),
    ('USDG', '2026-08'): dict(treasury=31, repo=None, types=['bank_deposit', 'government_mmf', 'treasury_bill'], formula=True, custodian=False, cert=True),
    ('USDG', '2026-09'): dict(treasury=36, repo=None, types=['bank_deposit', 'government_mmf', 'treasury_bill'], formula=True, custodian=False, cert=True),
}
FIELD_STATES = {'found', 'not_disclosed', 'not_in_report', 'not_applicable'}


def test_rule_inputs_representative_months():
    got = _reports()
    for key, exp in RULE_INPUTS.items():
        r = got[key]
        assert r['treasury_max_maturity_days'] == exp['treasury'], key
        assert r['repo_max_maturity_days'] == exp['repo'], key
        assert sorted(r['asset_types']) == exp['types'], key
        assert r['circulation_formula_disclosed'] is exp['formula'], key
        assert r['custodian_disclosure'] is exp['custodian'], key
        assert r['management_certification'] is exp['cert'], key


def test_rule_inputs_first_and_last_month_are_covered():
    """대표 달 표가 각 토큰의 첫 달과 마지막 달을 빠뜨리지 않는지 본다."""
    months = {}
    for tok, m in _reports():
        months.setdefault(tok, []).append(m)
    for tok, ms in months.items():
        for m in (min(ms), max(ms)):
            if tok == 'USDP' and m == '2026-09':  # USDP 마지막 달은 2025-01과 값이 같아 따로 두지 않는다
                continue
            assert (tok, m) in RULE_INPUTS, (tok, m)


def test_rule_inputs_structure_all_reports():
    for key, r in _reports().items():
        assert sum(h['amount'] for h in r['holdings']) == r['fair_value'], f'{key} holdings 합계 불일치'
        for field, note in r['field_notes'].items():
            assert note['state'] in FIELD_STATES, (key, field, note['state'])
            if note['state'] == 'not_applicable':
                assert r[field] is None, (key, field)
            if note['state'] == 'not_disclosed':
                assert r[field] is False, (key, field)
        assert r['redemption_days'] is None and r['interest_paid'] is None, key
