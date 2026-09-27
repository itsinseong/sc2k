import json, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

# 기대값은 data/samples/Paxos_*_Examination_2026-07.txt를 직접 읽어 확인한 값.
EXPECTED = {
    'PYUSD': dict(circulation=2689335674, fair_value=2694072163, as_of='2026-07-31', signed='2026-08-25'),
    'USDP': dict(circulation=31954027, fair_value=31975703, as_of='2026-07-31', signed='2026-08-25'),
    'USDG': dict(circulation=3400474143, fair_value=3404876225, as_of='2026-07-31', signed='2026-08-26'),
}


def _reports():
    r = subprocess.run([sys.executable, str(ROOT / 'scripts/parse_paxos.py')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return {x['token']: x for x in json.loads((ROOT / 'data/reports_paxos.json').read_text(encoding='utf-8'))['reports']}


def test_three_tokens_parse_and_reconcile():
    got = _reports()
    assert set(got) == set(EXPECTED), f'토큰 목록 불일치: {sorted(got)}'
    for tok, exp in EXPECTED.items():
        r = got[tok]
        assert r['ok'], f'{tok} 대사 실패: {r["reconciliation"]}'
        assert r['circulation'] == exp['circulation'], tok
        assert r['fair_value'] == exp['fair_value'], tok
        assert r['as_of'] == exp['as_of'], tok
        assert r['attestation']['signed'] == exp['signed'], tok
        assert r['fair_value'] >= r['circulation'], tok


def test_components_sum_matches_fair_value():
    got = _reports()
    for tok, r in got.items():
        assert sum(r['components'].values()) == r['fair_value'], f'{tok} 구성 합계 불일치'


def test_firm_is_kpmg_for_all_three():
    """KPMG LLP는 세 보고서 모두 텍스트에 그대로 나온다(서명 이미지가 아니다). Circle과 달리 firm이 None이면 안 된다."""
    got = _reports()
    for tok, r in got.items():
        assert r['attestation']['firm'] == 'KPMG LLP', tok


def test_usdg_uses_reasonable_assurance_not_examination():
    """USDG는 싱가포르 SSAE 3000 reasonable assurance 보고서라 examination이 아니다. 회귀 지점."""
    got = _reports()
    assert got['USDG']['attestation']['type'] == 'reasonable assurance'
    assert got['PYUSD']['attestation']['type'] == 'examination'
    assert got['USDP']['attestation']['type'] == 'examination'
