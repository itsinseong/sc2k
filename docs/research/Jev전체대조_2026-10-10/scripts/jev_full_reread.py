"""Jev로 보고서 전체(data/reports*.json)의 R11, R12, R15를 다시 읽는다. 실행만 한다(분석 없음).
질문 문구와 요청 함수는 scripts/jev/jev_hard_test.py v2(NOUL2)와 jev_choice_test.py(request, load_key, pdf_pages)를 그대로 쓴다.
  python3 -B jev_full_reread.py run [N]   N건만(기본 전체). 캐시(scratchpad)에 있는 200 응답은 다시 부르지 않는다
  python3 -B jev_full_reread.py save      캐시를 results.json.gz로 쓴다
"""
import gzip, json, pathlib, sys, time
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'scripts' / 'jev'))
from jev_hard_test import NOUL2  # noqa: E402
from jev_choice_test import MODEL, USD_PER_TOKEN, load_key, load_reports, pdf_pages, request  # noqa: E402

OUT = ROOT / 'docs' / 'research' / 'Jev전체대조_2026-10-10'
CACHE = pathlib.Path('/private/tmp/claude-501/-/85357e67-132d-4096-913a-c1c782b41dc5/scratchpad/corr/jev_cache.json')
QS = ('R11_broad', 'R11_narrow', 'R12', 'R15')
REPO = ('circulation_formula_disclosed', 'custodian_disclosure', 'management_certification')
MAX_TOK = 30000  # 서버 한도 32k(state와 가장 긴 질문 합). 글자수/2로 어림(첫 시험 est_tokens와 같은 방식)하고 질문 몫을 남긴다
GAP = 0.4  # 요청 사이 초


def build(f, i, r):
    pdf = ROOT / r['source_file']
    pages = pdf_pages(pdf)
    have = [n for n, p in enumerate(pages, 1) if p]
    empty = [n for n in range(1, len(pages) + 1) if n not in have]
    if not have: return None, {'skipped': 'no_text_layer', 'pages': len(pages)}
    used, parts, tok = [], [], 0
    for n in have:
        t = len(pages[n - 1]) // 2 + 10
        if tok + t > MAX_TOK: break
        tok += t; used.append(n); parts.append(f'[page {n}]\n{pages[n - 1]}')
    info = {'pages_total': len(pages), 'pages_used': used, 'pages_no_text': empty, 'est_tokens': tok,
            'over_limit_cut': len(used) < len(have)}
    state = {'document': f"{r['token']} document, {r['month']}", 'text': '\n\n'.join(parts)}
    return {'model': MODEL, 'state': state,
            'questions': {k: {'type': 'noul', 'instructions': NOUL2[k][0], 'criteria': NOUL2[k][1]} for k in QS}}, info


def load_cache():
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def run(limit=None):
    cache, key = load_cache(), load_key()
    rows = load_reports()[:limit]
    for n, (f, i, r) in enumerate(rows, 1):
        rid = f'{f}#{i}'
        if rid in cache and cache[rid].get('status') in (200, None): continue
        p, info = build(f, i, r)
        row = {'id': rid, 'file': f, 'index': i, 'token': r['token'], 'month': r['month'], 'source_file': r['source_file'],
               'repo': {k: r.get(k) for k in REPO}, 'input': info}
        if p is None:
            row['status'] = None
        else:
            code, resp, sec = request(key, 'POST', '/systemone', p)
            row.update(status=code, seconds=round(sec, 3), model=resp.get('model'), usage=resp.get('usage', {}), response=resp)
            time.sleep(GAP)
        cache[rid] = row
        CACHE.write_text(json.dumps(cache, ensure_ascii=False))
        print(n, rid, row['status'], row.get('usage'), info.get('over_limit_cut', ''), flush=True)


def save():
    cache = load_cache()
    rows = list(cache.values())
    ok = [r for r in rows if r.get('status') == 200]
    tin = sum(r['usage'].get('input_tokens', 0) for r in ok)
    tout = sum(r['usage'].get('output_tokens', 0) for r in ok)
    meta = {'date': '2026-10-10', 'model_requested': MODEL, 'endpoint': 'https://api.typesafe.ai/v1/systemone',
            'questions': {k: {'instructions': NOUL2[k][0], 'criteria': NOUL2[k][1]} for k in QS},
            'repo_keys': {'R11': REPO[0], 'R12': REPO[1], 'R15': REPO[2]},
            'reports': len(rows), 'ok': len(ok), 'skipped_no_text': [r['id'] for r in rows if r['status'] is None],
            'failed': [(r['id'], r['status']) for r in rows if r['status'] not in (None, 200)],
            'cut_over_limit': [(r['id'], r['input']['pages_used']) for r in rows if r['input'].get('over_limit_cut')],
            'input_tokens': tin, 'output_tokens': tout, 'usd': round(tin * USD_PER_TOKEN, 4), 'usd_per_million_input': 0.042}
    with gzip.open(OUT / 'results.json.gz', 'wt', encoding='utf-8') as g:
        json.dump({'meta': meta, 'rows': rows}, g, ensure_ascii=False)
    print(json.dumps({k: v for k, v in meta.items() if k != 'questions'}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'run': run(int(sys.argv[2]) if len(sys.argv) > 2 else None)
    else: save()
