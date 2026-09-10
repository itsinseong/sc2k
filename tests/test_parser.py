import json, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

EXPECTED = {
    '2026-01': dict(circulation=69954717486, fair_value=70022091915, as_of='2026-01-30', signed='2026-02-26', tsub=False),
    '2026-03': dict(circulation=77049290538, fair_value=77125330954, as_of='2026-03-31', signed='2026-04-29', tsub=False),
    '2026-04': dict(circulation=77047590794, fair_value=77123668726, as_of='2026-04-30', signed='2026-05-28', tsub=False),
    '2026-07': dict(circulation=71826453410, fair_value=71904101332, as_of='2026-07-31', signed='2026-08-27', tsub=True),
}

def _reports():
    r = subprocess.run([sys.executable, str(ROOT/'scripts/parse_circle.py')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return {x['month']: x for x in json.loads((ROOT/'data/reports.json').read_text(encoding='utf-8'))['reports']}

def test_four_months_parse_and_reconcile():
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
        assert c['circle_reserve_fund'] + c['other'] == r['fair_value'], f'{m} 구성 합계 불일치'
        assert r['fair_value'] >= r['circulation'], m

def test_july_alone_has_treasury_subtable():
    """7월만 기타 준비자산 안에 국채 하위표가 있다. 파서 회귀 지점."""
    got = _reports()
    for m, exp in EXPECTED.items():
        assert got[m]['flags']['other_has_treasury_subtable'] is exp['tsub'], m

def test_month_end_is_last_day_except_january():
    """2026-01은 말일이 토요일이라 기준일이 30일이다. 공시안 D-01의 근거."""
    import calendar, datetime
    got = _reports()
    off = [m for m, r in got.items()
           if datetime.date.fromisoformat(r['as_of']).day
           != calendar.monthrange(*map(int, m.split('-')))[1]]
    assert off == ['2026-01'], off
