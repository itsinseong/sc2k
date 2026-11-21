#!/usr/bin/env python3
"""Ripple 준비금 표를 두 독자(PaddleOCR-VL, Claude Opus 5.5)가 따로 읽은 결과의 합의 판정.

두 표를 줄 이름(정규화)으로 맞추고, 칸(유통량, 준비금 총액, 줄마다 중순 값과 월말 값)이 같으면 합의로 본다.
이름만 다르고 금액이 모두 같은 CUSIP 줄은 검증 숫자를 통과한 쪽 이름으로 자동 해결한다(resolved_by_checkdigit).
그 밖의 불일치는 어느 쪽이 맞는지 고르지 않고 확인 목록에 올린다. 합의된 줄로 parse_ripple.classify를 써서
자산 5종과 합계 대사를 만들고, 월말 금액이 있는 국채 줄은 재무부 공식 만기(fiscaldata_cache.json)로 남은 일수를 본다.
정답(reports_ripple.json)은 summary.txt의 점수 매기기에만 쓴다. 숫자는 읽은 그대로 두고 고치지 않는다.

실행: python3 -B scripts/reading/reconcile.py [YYYY-MM ...]   (달을 안 주면 두 독자 결과가 다 있는 달 전부)
두 번째 독자는 READER로 고른다(기본 opus, 아니면 claude_read.py와 같은 Gateway 모델 ID). opus가 아니면 reconciled_<READER>/에 쓴다.
쓰는 곳: docs/research/읽기엔진시험_2026-10-09/reconciled/ (ripple_YYYY-MM.json, 확인목록.md, summary.txt)
"""
import datetime as dt, json, os, pathlib, re, subprocess, sys
sys.dont_write_bytecode = True                         # 기존 __pycache__를 건드리지 않는다
W = pathlib.Path(__file__).resolve().parent
REPO = W.parents[1]
D = REPO / 'docs/research/읽기엔진시험_2026-10-09'      # 읽은 결과
sys.path[:0] = [str(W), str(REPO / 'scripts')]
from paddle_rows import T, num
from cusip_check import cusip_ok, toks, val, pdate      # cusip_ok: 검증 숫자(A=10, *=36, @=37, #=38, 홀수 자리 2배)
from parse_ripple import classify, DATE, to_iso
READER = os.environ.get('READER', 'opus')
NAME = {'opus': 'Claude Opus'}.get(READER, READER)    # Jira 줄에 쓰는 두 번째 독자 이름
OUT = D / ('reconciled' if READER == 'opus' else f'reconciled_{READER}')
CUSIP = re.compile(r'\b912\w{5,7}\b')                  # claude_read.compare와 같은 CUSIP 줄 판별
CELL = ('중순', '월말')
MAT = {c: sorted({x['maturity_date'] for x in v}) for c, v in json.loads((D / 'fiscaldata_cache.json').read_text()).items()}
IMG = str(D.relative_to(REPO)) + '/png/paddle/ripple_{}.png'


def norm(label):  # compare_readers.norm과 같되 40자 자르기는 하지 않는다(뒤쪽만 다른 이름을 같은 줄로 보지 않게)
    label = re.sub(r'\$\s*\^\{+\*\}+\s*\$', '', label or '').replace('*', '')
    return ' '.join(label.split()).lower()


def pad_rows(md):
    """paddle_rows.rows_of와 같은 모양과 같은 줄 이름 규칙. 값만 다르게 집는다: rows_of는 끝의 두 칸을 집어서
    '$ | 27,561,764 | $ | -' 꼴 줄의 중순 값을 놓친다. 여기서는 cusip_check와 같은 규칙으로 '$', '<fcel>', 빈 칸을 빼고
    값 칸을 모두 차례로 담는다(만기 날짜 칸은 값이 아니라 뺀다). 값 칸이 둘이 아니면 그대로 두고 match가 확인 목록에 올린다."""
    p = T(); p.feed(md)
    top, body = p.tables[0], p.tables[1]
    def split(r):
        j = 0 if len(r) >= 3 else next((i for i, c in enumerate(r) if c and num(c) is None), None)
        return (r[j] or '' if j is not None else ''), [val(t) for t in toks(c for i, c in enumerate(r) if i != j and not pdate(c))]
    return {'circulation': split(top[1])[1], 'reserve_fair_value': split(top[2])[1],
            'rows': [{'label': l, 'values': v} for l, v in map(split, body[1:])]}


def opus(m):  # claude_read.read와 같은 방식으로 result 문자열 안 JSON을 꺼낸다(새로 읽히지는 않는다)
    t = json.loads((D / f'claude_{READER}_{m}.json').read_text())['result']
    return json.loads(t[t.index('{'):t.rindex('}') + 1])


def keyed(g):
    """(정규화 이름, 같은 이름 중 몇 번째) -> 줄. 숫자 없는 제목 줄은 칸이 없으니 뺀다. 읽은 순서를 지킨다."""
    out, seen = {}, {}
    for r in g['rows']:
        v = list(r.get('values') or [])
        if all(x is None for x in v): continue
        n = norm(r['label']); seen[n] = seen.get(n, -1) + 1
        out[(n, seen[n])] = {'label': r['label'], 'values': v}
    return out


def agree(a, b): return a is not None and a == b      # 둘 다 못 읽은 칸(null)은 합의로 보지 않는다
def same(a, b): return len(a) == len(b) == 2 and all(map(agree, a, b))


def diffs(name, a, b):
    """한 줄의 확인할 칸. a, b는 두 독자의 값 목록이고 None이면 그 독자에게 이 줄이 없다. 값 칸이 둘(중순, 월말)이
    아니면 어느 값이 어느 날짜 칸인지 알 수 없으니 줄 전체를 한 항목으로 올린다."""
    if any(v is not None and len(v) != 2 for v in (a, b)):
        return [{'name': name, 'cell': '값 칸 수', 'paddle': '줄 없음' if a is None else a, 'opus': '줄 없음' if b is None else b}]
    return [{'name': name, 'cell': CELL[i], 'paddle': '줄 없음' if a is None else a[i], 'opus': '줄 없음' if b is None else b[i]}
            for i in (0, 1) if a is None or b is None or not agree(a[i], b[i])]


def match(pad, opu):
    """-> (합의된 줄, 자동 해결 기록, 확인 목록). 확인 항목은 칸마다 하나: {name, cell, paddle, opus}."""
    P, O = keyed(pad), keyed(opu)
    pair = {k: k for k in P if k in O}                 # Paddle 키 -> Opus 키
    lp, lo = [k for k in P if k not in O], [k for k in O if k not in P]
    resolved = []
    for k in lp:  # 이름만 다른 줄: 금액이 모두 같은 짝이 양쪽에서 하나뿐이고, CUSIP 꼴 두 이름 중 한쪽만 검증 숫자를 통과
        cand = [c for c in lo if same(P[k]['values'], O[c]['values'])]
        if len(cand) != 1 or sum(same(P[x]['values'], O[cand[0]]['values']) for x in lp) != 1: continue
        c = cand[0]; a, b = P[k]['label'].strip(), O[c]['label'].strip()
        if not (CUSIP.fullmatch(a) and CUSIP.fullmatch(b)) or (cusip_ok(a) is True) == (cusip_ok(b) is True): continue
        pair[k] = c
        resolved.append({'paddle': a, 'opus': b, 'chosen': a if cusip_ok(a) else b, 'values': P[k]['values']})
    chosen = {r['paddle']: r['chosen'] for r in resolved}
    table, check, ok = [], [], set()
    for k in [k for k in P if k in pair]:              # 합의된 표는 Paddle 쪽 순서로 둔다(순서가 같은지는 아래에서 본다)
        c = pair[k]; a, b = P[k]['values'], O[c]['values']
        name = chosen.get(P[k]['label'].strip(), O[c]['label'])
        bad = diffs(name, a, b); check += bad
        if not bad:
            table.append({'label': name, 'values': a, 'labels': {'paddle': P[k]['label'], 'opus': O[c]['label']}}); ok.add(c)
    for k in lp:
        if k not in pair: check += diffs(P[k]['label'], P[k]['values'], None)
    for c in lo:
        if c not in pair.values(): check += diffs(O[c]['label'], None, O[c]['values'])
    if [pair[k] for k in P if pair.get(k) in ok] != [c for c in O if c in ok]:  # classify가 줄 순서에 기대므로 순서 차이도 본다
        check.append({'name': '(줄 순서)', 'why': '합의된 줄들의 위아래 순서가 두 독자 사이에서 다릅니다'})
    for key, nm in (('circulation', '유통량'), ('reserve_fair_value', '준비금 총액')):
        check += diffs(nm, list(pad[key]), list(opu[key]))
    return table, resolved, check


def components(table):  # claude_read.compare처럼 CUSIP 줄은 빼고 'Total Market Value' 줄에서 끊어 classify에 넘긴다
    body = []
    for i, r in enumerate(table):
        if re.search(r'total market value', r['label'], re.I): break
        if CUSIP.search(r['label']): continue
        body.append((r['label'], r['values'][1], i, str(r['values'][1])))
    comp = classify(body, any(CUSIP.search(r['label']) for r in table))
    return {k: sum(x['value'] for x in v) for k, v in comp.items()}


def as_of(m):  # 월말 기준일. 표 그림이 아니라 PDF 글자 층의 Report Dates 문구(parse_ripple과 같은 정규식)에서 읽는다
    pdf = REPO / f'data/samples/Ripple_RLUSD_Examination_{m}.pdf'
    t = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
    x = re.search(rf'as of ({DATE}),?\s+and\s+(?:as of\s+)?({DATE}),?\s+at', t)
    d = to_iso(x[2]) if x else None
    return dt.date.fromisoformat(d) if d else None


def run(m):
    pad = pad_rows((D / 'paddle' / f'ripple_{m}.md').read_text())
    try: opu = opus(m)
    except (ValueError, KeyError) as e:
        return {'month': m, 'status': '확인 필요', 'check': [{'name': f'({NAME} 결과)', 'why': f'{NAME} 결과 파일을 읽지 못했습니다 ({e})'}]}
    table, resolved, check = match(pad, opu)
    pick = lambda a, b: [x if agree(x, y) else None for x, y in zip(a, b)] if len(a) == len(b) == 2 else [None, None]
    circ, total = pick(pad['circulation'], opu['circulation']), pick(pad['reserve_fair_value'], opu['reserve_fair_value'])
    comp = components(table)
    rec = {'components_sum': sum(comp.values()), 'reserve_fair_value': total[1]}
    rec['ok'] = rec['reserve_fair_value'] is not None and rec['components_sum'] == rec['reserve_fair_value']
    if not rec['ok']:
        check.append({'name': '(합계 대사)', 'why': f'합의된 줄로 만든 자산 5종 합 {fmt(rec["components_sum"])}이 준비금 총액 '
                                                     f'{fmt(rec["reserve_fair_value"])}과 다릅니다'})
    d0 = as_of(m)
    if d0 is None: check.append({'name': '(기준일)', 'why': 'PDF 글자 층에서 월말 기준일을 찾지 못해 국채 만기 검사를 못 했습니다'})
    for r in table:  # 국채 줄마다 공식 만기 기준 남은 일수. 음수인데 월말 금액이 있으면 확인 목록
        if not CUSIP.search(r['label']): continue
        c, end = r['label'].strip(), r['values'][1]
        om = MAT.get(c)
        r['maturity'] = om[0] if om and len(om) == 1 else None
        r['days_to_maturity'] = (dt.date.fromisoformat(r['maturity']) - d0).days if r['maturity'] and d0 else None
        if not end or d0 is None: continue
        if r['maturity'] is None:
            why = ('재무부 만기 캐시에 없는 CUSIP' if om is None else '재무부 자료에 없는 CUSIP' if not om else f'공식 만기가 여럿 {om}')
            check.append({'name': c, 'why': f'월말 금액 {fmt(end)}이 있으나 {why}이라 남은 일수를 계산하지 못했습니다'})
        elif r['days_to_maturity'] < 0:
            check.append({'name': c, 'why': f'월말 금액 {fmt(end)}이 있으나 공식 만기 {r["maturity"]}가 기준일 {d0}보다 앞섭니다'
                                             f'(남은 일수 {r["days_to_maturity"]})'})
    return {'month': m, 'status': '확정' if not check and rec['ok'] else '확인 필요', 'as_of': d0 and d0.isoformat(),
            'circulation': circ, 'reserve_fair_value': total, 'table': table, 'components': comp, 'reconciliation': rec,
            'resolved_by_checkdigit': resolved, 'check': check,
            'readers': {'paddle': f'paddle/ripple_{m}.md', READER: f'claude_{READER}_{m}.json', 'image': IMG.format(m)}}


def fmt(v):
    if isinstance(v, list): return '[' + ', '.join(map(fmt, v)) + f'] ({len(v)}칸)'
    return f'{v:,}' if isinstance(v, int) else '읽지 못함(null)' if v is None else str(v)


def line(m, x):  # Jira에 그대로 붙일 수 있는 한 줄
    img = IMG.format(m)
    if 'cell' in x:
        what = '값 칸 수가 둘(중순, 월말)이 아니거나 서로 다릅니다' if x['cell'] == '값 칸 수' else f'{x["cell"]} 값이 두 독자 사이에서 다릅니다'
        return (f'- [RLUSD {m}] {x["name"] or "(이름 없는 줄)"} 줄의 {what}. '
                f'PaddleOCR-VL {fmt(x["paddle"])}, {NAME} {fmt(x["opus"])}. 그림 {img} 에서 맞는 값을 확인해 주세요.')
    return f'- [RLUSD {m}] {x["name"]}: {x["why"]}. 그림 {img} 에서 확인해 주세요.'


def score(res, b):
    """정답과 대조. -> (다른 항목 목록, 국채 종목 같은 수, 종목 합집합 크기)."""
    got = res.get('components') or {}
    items = [('유통량', (res.get('circulation') or [None, None])[-1], b['circulation']),
             ('준비금 총액', (res.get('reserve_fair_value') or [None, None])[-1], b['fair_value'])]
    items += [(k, got.get(k), b['components'][k]) for k in b['components']]
    bad = [f'{k} {fmt(x) if x is not None else "합의값 없음"} / 정답 {fmt(y)}' for k, x, y in items if x != y]
    held = {r['label'].strip(): r['values'][1] for r in res.get('table', []) if CUSIP.search(r['label']) and r['values'][1]}
    ref = {re.search(r'CUSIP\s+(\S+)', h['label'])[1]: h['amount'] for h in b['holdings']
           if str(h.get('kind', '')).startswith('treasury') and 'CUSIP' in h['label']}
    for c in sorted(set(held) | set(ref)):
        if held.get(c) != ref.get(c):
            bad.append(f'국채 {c} 월말 {fmt(held[c]) if c in held else "합의값 없음"} / 정답 {fmt(ref[c]) if c in ref else "보유 없음"}')
    return bad, sum(held.get(c) == ref[c] for c in ref), len(set(held) | set(ref))


def selftest():
    assert cusip_ok('91282CRQ6') and cusip_ok('912810UW6') and cusip_ok('912797QX8') and cusip_ok('91279QX8') is None
    p = {'circulation': [1, 2], 'reserve_fair_value': [3, 4], 'rows': [
        {'label': 'U.S. Treasury bills:', 'values': [None, None]}, {'label': '91279QX8', 'values': [5, 6]},
        {'label': 'Subtotal', 'values': [5, 6]}, {'label': 'Cash $ ^{*} $', 'values': [7, None]}]}
    o = {'circulation': [1, 2], 'reserve_fair_value': [3, 5], 'rows': [
        {'label': '912797QX8', 'values': [5, 6]}, {'label': 'Subtotal', 'values': [5, 7]}, {'label': 'Cash*', 'values': [7, None]}]}
    table, res, chk = match(p, o)
    assert [r['label'] for r in table] == ['912797QX8'] and res[0]['chosen'] == '912797QX8', (table, res)
    assert sorted((x['name'], x['cell']) for x in chk) == [('Cash*', '월말'), ('Subtotal', '월말'), ('준비금 총액', '월말')], chk
    o['rows'][0]['values'] = [5, 0, 6]                 # 값 칸이 셋이면 줄 전체를 한 항목으로
    assert ('912797QX8', '값 칸 수') in [(x['name'], x['cell']) for x in match(p, o)[2]]
    td = lambda *cs: '<tr>' + ''.join(f'<td>{c}</td>' for c in cs) + '</tr>'
    g = pad_rows('<table>' + td('', 'December 20, 2024') + td('RLUSD supply', '', '72,300,301', '', '77,208,201') + td('M', '$', '1', '$', '2')
                 + '</table><table>' + td('h') + td('912797MQ7', '12/24/2024', '$', '27,561,764', '$', '-') + td('Adj', '', '(5,000,000)', '') + '</table>')
    assert g['circulation'] == [72300301, 77208201] and g['reserve_fair_value'] == [1, 2], g
    assert [r['values'] for r in g['rows']] == [[27561764, 0], [-5000000]], g


def main():
    selftest()
    months = sys.argv[1:] or sorted(p.stem[7:] for p in (D / 'paddle').glob('ripple_*.md') if (D / f'claude_{READER}_{p.stem[7:]}.json').exists())
    ref = {r['month']: r for r in json.loads((REPO / 'data/reports_ripple.json').read_text())['reports']}
    OUT.mkdir(exist_ok=True)
    md = [f'# Ripple RLUSD 표 확인 목록 (reconcile.py, {dt.datetime.now():%Y-%m-%d %H:%M}, {len(months)}개월)', '']
    sm = [f'Ripple RLUSD 두 독자 합의 판정 (reconcile.py, {dt.datetime.now():%Y-%m-%d %H:%M})',
          '상태: 모든 칸 합의(자동 해결 포함) + 합계 대사 통과 + 국채 만기 검사 통과면 확정, 아니면 확인 필요',
          '정답 대조: 합의값을 시험용 정답(reports_ripple.json)의 유통량, 준비금 총액, 자산 5종, 국채 종목별 월말 금액과 비교', '']
    tally = {'확정': [], '확인 필요': [], '확정인데 정답과 다름': [], '확인 필요인데 정답과 모두 같음': []}
    for m in months:
        r = run(m)
        (OUT / f'ripple_{m}.json').write_text(json.dumps(r, ensure_ascii=False, indent=1))
        md += [line(m, x) for x in r['check']]
        bad, eq, n = score(r, ref[m])
        tally[r['status']].append(m)
        if r['status'] == '확정' and bad: tally['확정인데 정답과 다름'].append(m)
        if r['status'] == '확인 필요' and not bad: tally['확인 필요인데 정답과 모두 같음'].append(m)
        rec = r.get('reconciliation', {})
        sm.append(f'{m}  {r["status"]:<6} 확인 {len(r["check"])}건, 자동 해결 {len(r.get("resolved_by_checkdigit", []))}건, '
                  f'합계 대사 {"통과" if rec.get("ok") else "실패"} | 정답 대조 {"모두 같음" if not bad else f"{len(bad)}곳 다름"}, '
                  f'국채 종목 월말 {eq}/{n} 같음')
        sm += [f'          {x}' for x in bad]
    sm += [''] + [f'{k}: {len(v)}건 {v}' for k, v in tally.items()]
    (OUT / '확인목록.md').write_text('\n'.join(md) + '\n')
    (OUT / 'summary.txt').write_text('\n'.join(sm) + '\n')
    print('\n'.join(sm))


if __name__ == '__main__':
    main()
