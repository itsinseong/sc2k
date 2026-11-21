"""Ripple 표 쪽 그림을 두 번째 독자로 옮겨 적고, parse_ripple.classify로 묶어 Vision 기준값(커밋본)과 대조한다.
독자는 READER로 고른다: opus(기본, claude -p 구독) 또는 아주LLM Gateway 모델 ID(gpt-6.1-sol, gemini-4-argon).
Gateway 키는 환경변수 AJOU_LLM_API_KEY, 없으면 .env.local의 같은 이름 줄.
실행: READER=gemini-4-argon python3 scripts/reading/claude_read.py [YYYY-MM ...]   (달을 안 주면 전부)"""
import base64, json, os, pathlib, re, subprocess, sys, urllib.request
W = pathlib.Path(__file__).resolve().parent
REPO = W.parents[1]
D = REPO / 'docs/research/읽기엔진시험_2026-10-09'  # 읽은 결과. 그림은 D/png(커밋 안 함)
sys.path.insert(0, str(REPO / 'scripts'))
from parse_ripple import classify
PROMPT = (W / 'prompt_ripple_table_v1.md').read_text()
MODEL = os.environ.get('CLAUDE_MODEL', 'claude-opus-5-5')  # 기본은 Opus 5.5 effort max(인성 10/09)
EFFORT = os.environ.get('CLAUDE_EFFORT', 'max')
READER = os.environ.get('READER', 'opus')
TAG = os.environ.get('TAG', READER)  # 결과 파일 이름 구분. Sonnet 비교용 옛 결과는 TAG='' (claude_<달>.json)
base = {r['month']: r for r in json.loads((REPO / 'data/reports_ripple.json').read_text())['reports']}

def read(month):
    cached = D / f'claude_{TAG + "_" if TAG else ""}{month}.json'
    if cached.exists():
        t = json.loads(cached.read_text())['result']; return json.loads(t[t.index('{'):t.rindex('}') + 1])
    page = base[month]['flags']['ocr_pages'][0]
    png = D / 'png' / f'ripple_{month}_p{page}'; png.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['pdftoppm', '-r', '200', '-png', '-f', str(page), '-l', str(page), '-singlefile',
                    str(REPO / f'data/samples/Ripple_RLUSD_Examination_{month}.pdf'), str(png)], check=True)
    if READER != 'opus':
        text = gateway(png.with_suffix('.png'))
        (D / f'claude_{TAG}_{month}.json').write_text(json.dumps({'reader': READER, 'result': text}, ensure_ascii=False, indent=1))
        return json.loads(text[text.index('{'):text.rindex('}') + 1])
    out = subprocess.run(['claude', '-p', PROMPT + f'\nImage file: {png.name}.png', '--model', MODEL, *(['--effort', EFFORT] if EFFORT else []),
                          '--output-format', 'json', '--allowedTools', 'Read'], cwd=png.parent, capture_output=True, text=True, timeout=1800)
    env = json.loads(out.stdout)
    (D / f'claude_{TAG + "_" if TAG else ""}{month}.json').write_text(json.dumps(env, ensure_ascii=False, indent=1))
    text = env['result'].strip()
    return json.loads(text[text.index('{'):text.rindex('}') + 1])

GW = 'https://factchat-cloud.mindlogic.ai/v1/gateway'

def key():
    if os.environ.get('AJOU_LLM_API_KEY'): return os.environ['AJOU_LLM_API_KEY']
    for line in (REPO / '.env.local').read_text().splitlines():
        k, _, v = line.strip().partition('=')
        if k.removeprefix('export ').strip() == 'AJOU_LLM_API_KEY': return v.strip().strip('"\'')
    sys.exit('AJOU_LLM_API_KEY 없음')

def gateway(png):
    """같은 프롬프트와 그림을 Gateway로 보낸다. gemini는 Gemini 네이티브 경로, 그 밖은 chat 경로(10/18 그림 입력 실측)."""
    img = base64.b64encode(png.read_bytes()).decode()
    q = PROMPT.replace('Read the image file given below with the Read tool.', 'The page image is attached.')
    if READER.startswith('gemini'):
        path, body = f'/gemini/v1beta/models/{READER}:generateContent', {'contents': [{'parts': [{'text': q}, {'inline_data': {'mime_type': 'image/png', 'data': img}}]}]}
    else:
        path, body = '/chat/completions/', {'model': READER, 'reasoning_effort': 'high', 'messages': [{'role': 'user', 'content': [
            {'type': 'text', 'text': q}, {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + img}}]}]}
    req = urllib.request.Request(GW + path, json.dumps(body).encode(), {'Authorization': 'Bearer ' + key(), 'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=1800))
    if READER.startswith('gemini'): return ''.join(p.get('text', '') for p in r['candidates'][0]['content']['parts'])
    return r['choices'][0]['message']['content']

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
    months = sys.argv[1:] or sorted(base)
    print(READER, sum(compare(m, read(m)) for m in months), '/', len(months), '일치')
