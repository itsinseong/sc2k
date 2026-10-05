import functools, json, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

EXPECTED = {
    '2023-01': dict(circulation=42288053870, fair_value=42335734074, as_of='2023-01-31', signed='2023-03-02', tsub=False, cash=8700672117),
    '2023-02': dict(circulation=42404871070, fair_value=42456417425, as_of='2023-02-28', signed='2023-03-30', tsub=False, cash=10626132587),
    '2023-03': dict(circulation=32518607650, fair_value=32571701308, as_of='2023-03-31', signed='2023-04-28', tsub=False, cash=3707781370),
    '2023-04': dict(circulation=30494122886, fair_value=30546069033, as_of='2023-04-28', signed='2023-05-30', tsub=False, cash=5178160327),
    '2023-05': dict(circulation=28870143470, fair_value=28925130135, as_of='2023-05-31', signed='2023-06-30', tsub=False, cash=4159033351),
    '2023-06': dict(circulation=27384351887, fair_value=27439541303, as_of='2023-06-30', signed='2023-07-28', tsub=False, cash=2673143113),
    '2023-07': dict(circulation=26407355247, fair_value=26462068123, as_of='2023-07-31', signed='2023-08-30', tsub=False, cash=2196028208),
    '2023-08': dict(circulation=26153201149, fair_value=26205114631, as_of='2023-08-31', signed='2023-09-29', tsub=False, cash=1932308264),
    '2023-09': dict(circulation=24973159027, fair_value=25025027673, as_of='2023-09-29', signed='2023-10-30', tsub=False, cash=1247386546),
    '2023-10': dict(circulation=24668300827, fair_value=24720265667, as_of='2023-10-31', signed='2023-11-30', tsub=False, cash=1252660496),
    '2023-11': dict(circulation=24477366310, fair_value=24529287113, as_of='2023-11-30', signed='2023-12-22', tsub=False, cash=1902038972),
    '2023-12': dict(circulation=24641390742, fair_value=24693288222, as_of='2023-12-29', signed='2024-01-30', tsub=False, cash=2499849775),
    '2024-01': dict(circulation=26739379540, fair_value=26790484649, as_of='2024-01-31', signed='2024-02-29', tsub=False, cash=3261418999),
    '2024-02': dict(circulation=28683063584, fair_value=28733994331, as_of='2024-02-29', signed='2024-03-30', tsub=False, cash=3301872815),
    '2024-03': dict(circulation=32374547608, fair_value=32425876781, as_of='2024-03-29', signed='2024-04-30', tsub=False, cash=4228498699),
    '2024-04': dict(circulation=33028099172, fair_value=33079391140, as_of='2024-04-30', signed='2024-05-30', tsub=False, cash=3126173077),
    '2024-05': dict(circulation=32289248060, fair_value=32340643744, as_of='2024-05-31', signed='2024-06-27', tsub=False, cash=3357248617),
    '2024-06': dict(circulation=32222674248, fair_value=32274321543, as_of='2024-06-28', signed='2024-07-30', tsub=False, cash=3601833723),
    '2024-07': dict(circulation=33183776501, fair_value=33247845322, as_of='2024-07-31', signed='2024-08-28', tsub=False, cash=3728381623),
    '2024-08': dict(circulation=34644410354, fair_value=34718608570, as_of='2024-08-30', signed='2024-09-27', tsub=False, cash=3961910997),
    '2024-09': dict(circulation=35468964901, fair_value=35533322286, as_of='2024-09-30', signed='2024-10-30', tsub=False, cash=4047881285),
    '2024-10': dict(circulation=34673185631, fair_value=34737568377, as_of='2024-10-31', signed='2024-11-26', tsub=False, cash=4316618640),
    '2024-11': dict(circulation=39737020007, fair_value=39801630749, as_of='2024-11-29', signed='2024-12-20', tsub=False, cash=6505203707),
    '2024-12': dict(circulation=43856799846, fair_value=43921522065, as_of='2024-12-31', signed='2025-01-30', tsub=False, cash=6479363032),
    '2025-01': dict(circulation=53218939728, fair_value=53283800358, as_of='2025-01-31', signed='2025-02-27', tsub=False, cash=6115166801),
    '2025-02': dict(circulation=56284318550, fair_value=56349194760, as_of='2025-02-28', signed='2025-03-28', tsub=False, cash=7019243460),
    '2025-03': dict(circulation=59975771715, fair_value=60040707040, as_of='2025-03-31', signed='2025-04-30', tsub=False, cash=6592595197),
    '2025-04': dict(circulation=61412761631, fair_value=61477725087, as_of='2025-04-30', signed='2025-05-29', tsub=False, cash=7270084526),
    '2025-05': dict(circulation=60883338651, fair_value=60948366559, as_of='2025-05-30', signed='2025-06-27', tsub=False, cash=7919350020),
    '2025-06': dict(circulation=61332530506, fair_value=61397784739, as_of='2025-06-30', signed='2025-07-30', tsub=False, cash=8421833092),
    '2025-07': dict(circulation=63935611557, fair_value=64000903241, as_of='2025-07-31', signed='2025-08-29', tsub=False, cash=8850709405),
    '2025-08': dict(circulation=71384711725, fair_value=71450126631, as_of='2025-08-29', signed='2025-09-30', tsub=False, cash=10347775187),
    '2025-09': dict(circulation=73748934193, fair_value=73814526973, as_of='2025-09-30', signed='2025-10-30', tsub=False, cash=9554821716),
    '2025-10': dict(circulation=75812280166, fair_value=75878386060, as_of='2025-10-31', signed='2025-11-26', tsub=False, cash=9747275564),
    '2025-11': dict(circulation=76435499580, fair_value=76502172739, as_of='2025-11-28', signed='2025-12-19', tsub=False, cash=10415377445),
    '2025-12': dict(circulation=75266033823, fair_value=75332981976, as_of='2025-12-31', signed='2026-01-30', tsub=False, cash=9003263619),
    '2026-01': dict(circulation=69954717486, fair_value=70022091915, as_of='2026-01-30', signed='2026-02-26', tsub=False, cash=10156944576),
    '2026-02': dict(circulation=75109039300, fair_value=75176561300, as_of='2026-02-27', signed='2026-03-27', tsub=False, cash=10382232878),
    '2026-03': dict(circulation=77049290538, fair_value=77125330954, as_of='2026-03-31', signed='2026-04-29', tsub=False, cash=10361225037),
    '2026-04': dict(circulation=77047590794, fair_value=77123668726, as_of='2026-04-30', signed='2026-05-28', tsub=False, cash=10567044499),
    '2026-05': dict(circulation=75885403148, fair_value=75961621872, as_of='2026-05-29', signed='2026-06-29', tsub=False, cash=10794851072),
    '2026-06': dict(circulation=73268560097, fair_value=73344909176, as_of='2026-06-30', signed='2026-07-29', tsub=False, cash=11382256398),
    '2026-07': dict(circulation=71826453410, fair_value=71904101332, as_of='2026-07-31', signed='2026-08-27', tsub=True, cash=10607410596),
    '2026-08': dict(circulation=73320757305, fair_value=73398532613, as_of='2026-08-31', signed='2026-09-29', tsub=True, cash=9591096978),
}

@functools.cache
def _reports():
    r = subprocess.run([sys.executable, str(ROOT/'scripts/parse_circle.py')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return {x['month']: x for x in json.loads((ROOT/'data/reports.json').read_text(encoding='utf-8'))['reports']}

def test_all_months_parse_and_reconcile():
    got = _reports()
    assert set(got) == set(EXPECTED), f'월 목록 불일치: {sorted(got)}'
    for m, exp in EXPECTED.items():
        r = got[m]
        assert r['ok'], f'{m} 대사 실패: {r["reconciliation"]}'
        assert r['circulation'] == exp['circulation'], m
        assert r['fair_value'] == exp['fair_value'], m
        assert r['as_of'] == exp['as_of'], m
        assert r['attestation']['signed'] == exp['signed'], m
        c = r['components']
        assert c['circle_reserve_fund'] + c['cash'] + c['treasury'] + c['other'] == r['fair_value'], f'{m} 구성 합계 불일치'
        assert c['cash'] == exp['cash'], f'{m} 은행 예금(Cash held at regulated financial institutions) 불일치: {c["cash"]}'
        assert r['fair_value'] >= r['circulation'], m

def test_treasury_subtable_months():
    """기타 준비자산 안에 국채 하위표가 있는 달은 2026-07, 2026-08이다. 나머지 달은 없다. 파서 회귀 지점."""
    got = _reports()
    for m, exp in EXPECTED.items():
        assert got[m]['flags']['other_has_treasury_subtable'] is exp['tsub'], m

def test_as_of_is_last_weekday_of_month():
    """기준일은 그 달의 마지막 평일이다(말일이 주말이면 직전 금요일). 공시안 D-01의 근거."""
    import calendar, datetime
    got = _reports()
    off = []
    for m, r in got.items():
        d = datetime.date(*map(int, m.split('-')), calendar.monthrange(*map(int, m.split('-')))[1])
        while d.weekday() >= 5:
            d -= datetime.timedelta(days=1)
        if datetime.date.fromisoformat(r['as_of']) != d:
            off.append(m)
    assert off == [], off


# 규칙 입력값 기대값은 독립 검증자가 PDF 원문에서 직접 읽은 값이다(verified.json). 파서 출력에 맞춰 바꾸지 않는다.
# 항목 순서: 국채 최장 만기(일), 레포 최장 만기(일), 자산 종류, 보관 기관 공개 여부. 유통량 계산식 공개와 경영진 서명은 전 달 True다.
_B, _M, _T = 'bank_deposit', 'government_mmf', 'treasury_bill'
RULE_INPUTS = {
    '2023-01': (72, None, [_B, _M], True),    # 첫 달. 레포 줄 없음
    '2023-04': (33, None, [_B, _M], True),    # 펀드 안 국채 중장기물 최장 33일
    '2023-05': (None, 1, [_B, _M], True),     # 펀드가 레포, 현금뿐이라 국채 만기 없음. 레포 1일 시작
    '2023-06': (41, 1, [_B, _M], True),
    '2023-09': (62, 1, [_B, _M], False),      # 이 달부터 보관 기관 이름이 없다
    '2025-11': (83, 1, [_B, _M], False),
    '2026-02': (83, 1, [_B, _M], False),
    '2026-06': (51, 1, [_B, _M], False),
    '2026-07': (76, 1, [_B, _M, _T], False),  # 기타 준비자산에 국채 하위표가 생겨 자산 종류가 늘어난 달
    '2026-08': (73, 1, [_B, _M, _T], False),  # 마지막 달
}

def test_rule_inputs_representative_months():
    got = _reports()
    for m, (tmax, repo, types, cust) in RULE_INPUTS.items():
        r = got[m]
        assert r['treasury_max_maturity_days'] == tmax, m
        assert r['repo_max_maturity_days'] == repo, m
        assert r['asset_types'] == types, m
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
