"""Ripple 표 쪽 그림을 claude -p(구독)로 옮겨 적고, parse_ripple.classify로 묶어 Vision 기준값(커밋본)과 대조한다."""
import json, os, pathlib, re, subprocess, sys
W = pathlib.Path(__file__).resolve().parent
REPO = W.parents[1]
D = REPO / 'docs/research/읽기엔진시험_2026-10-09'  # 읽은 결과. 그림은 D/png(커밋 안 함)
sys.path.insert(0, str(REPO / 'scripts'))
from parse_ripple import classify
PROMPT = (W / 'prompt_ripple_table_v1.md').read_text()
MODEL = os.environ.get('CLAUDE_MODEL', 'claude-opus-5-5')  # 기본은 Opus 5.5 effort max(인성 10/09)
EFFORT = os.environ.get('CLAUDE_EFFORT', 'max')
TAG = os.environ.get('TAG', 'opus')  # 결과 파일 이름 구분. Sonnet 비교용 옛 결과는 TAG='' (claude_<달>.json)
base = {r['month']: r for r in json.loads((REPO / 'data/reports_ripple.json').read_text())['reports']}

def read(month):
    cached = D / f'claude_{TAG + "_" if TAG else ""}{month}.json'
    if cached.exists():
        t = json.loads(cached.read_text())['result']; return json.loads(t[t.index('{'):t.rindex('}') + 1])
    page = base[month]['flags']['ocr_pages'][0]
    png = D / 'png' / f'ripple_{month}_p{page}'; png.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['pdftoppm', '-r', '200', '-png', '-f', str(page), '-l', str(page), '-singlefile',
                    str(REPO / f'data/samples/Ripple_RLUSD_Examination_{month}.pdf'), str(png)], check=True)
    out = subprocess.run(['claude', '-p', PROMPT + f'\nImage file: {png.name}.png', '--model', MODEL, *(['--effort', EFFORT] if EFFORT else []),
                          '--output-format', 'json', '--allowedTools', 'Read'], cwd=png.parent, capture_output=True, text=True, timeout=1800)
    env = json.loads(out.stdout)
    (D / f'claude_{TAG + "_" if TAG else ""}{month}.json').write_text(json.dumps(env, ensure_ascii=False, indent=1))
    text = env['result'].strip()
    return json.loads(text[text.index('{'):text.rindex('}') + 1])

def compare(month, got):
    b = base[month]
    # 파서와 같게: 숫자 없는 제목 줄과 CUSIP 줄은 빼고, 'Total Market Value' 줄에서 끊는다
    body = []
    for i, r in enumerate(got['rows']):
        if re.search(r'total market value', r['label'], re.I): break
        if r['values'] == [None, None] or re.search(r'\b912\w{5,7}\b', r['label']): continue
        body.append((r['label'], r['values'][1], i, str(r['values'][1])))
    rows = body
    has_cusip = any(re.search(r'\b912\w{5,7}\b', r['label']) for r in got['rows'])
    comp = {k: sum(x['value'] or 0 for x in v) for k, v in classify(rows, has_cusip).items()}
    res = {'circulation': (got['circulation'][1], b['circulation']), 'fair_value': (got['reserve_fair_value'][1], b['fair_value'])}
    res.update({k: (comp[k], b['components'][k]) for k in b['components']})
    bad = {k: v for k, v in res.items() if v[0] != v[1]}
    print(month, 'OK' if not bad else f'DIFF {bad}', '| 합계 대사', sum(comp.values()) == got['reserve_fair_value'][1], flush=True)
    return not bad

if __name__ == '__main__':
    print(sum(compare(m, read(m)) for m in sys.argv[1:]), '/', len(sys.argv) - 1, '일치')
