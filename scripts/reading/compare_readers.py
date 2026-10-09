"""같은 표 쪽을 읽은 Sonnet, Opus, PaddleOCR-VL 결과를 줄마다 맞춰 본다(국채 종목 줄 포함). 기준값 대조는 claude_read.compare가 한다."""
import json, pathlib, sys
W = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(W))
D = W.parents[1] / 'docs/research/읽기엔진시험_2026-10-09'  # 읽은 결과
from paddle_rows import rows_of

def claude(tag, m):
    f = D / f'claude_{tag + "_" if tag else ""}{m}.json'
    if not f.exists(): return None, None
    e = json.loads(f.read_text()); t = e['result']
    return json.loads(t[t.index('{'):t.rindex('}') + 1]), e

import re
def norm(label):  # PaddleOCR의 수식 표기($ ^{*} $), 별표, 띄어쓰기 차이는 같은 이름으로 본다
    label = re.sub(r'\$\s*\^\{+\*\}+\s*\$', '', label).replace('*', '')
    return ' '.join(label.split()).lower()[:40]

def table(g):  # 줄 이름 -> 월말 값. 숫자 없는 제목 줄은 뺀다. 유통량, 총액도 넣는다
    d = {'(유통량)': g['circulation'][1], '(준비금 총액)': g['reserve_fair_value'][1]}
    for r in g['rows']:
        if r['values'] != [None, None]: d[norm(r['label'])] = r['values'][1]
    return d

def diff(a, b):  # 두 표의 다른 칸. 한쪽에만 있는 줄도 적는다
    out = []
    for k in sorted(set(a) | set(b)):
        x, y = a.get(k, '줄 없음'), b.get(k, '줄 없음')
        if x != y: out.append(f'{k}: {x} / {y}')
    return out

for m in sys.argv[1:]:
    son, es = claude('', m); opu, eo = claude('opus', m)
    pad = rows_of((D / 'paddle' / f'ripple_{m}.md').read_text())
    S, O, P = (table(g) if g else None for g in (son, opu, pad))
    t = lambda e: f"{round(e.get('duration_ms', 0) / 1000)}s ${round(e.get('total_cost_usd', 0), 2)}" if e else '-'
    print(f'== {m}  시간 Sonnet {t(es)} / Opus {t(eo)}')
    for name, a, b in (('Sonnet vs Opus', S, O), ('Opus vs Paddle', O, P)):
        if a is None or b is None: print(f'  {name}: 결과 없음'); continue
        d = diff(a, b); print(f'  {name}: {"모든 칸 같음" if not d else str(len(d)) + "칸 다름"}')
        for x in d: print('     ', x)
