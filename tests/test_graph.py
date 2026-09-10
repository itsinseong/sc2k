import subprocess, sys, pathlib
def test_edges_match_sources():
    r = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve().parent.parent/'scripts/validate_graph.py')], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
