"""모델 시험용 문항 파일(questions.jsonl)을 만든다. Jev API를 부르지 않는다. data/*.json은 읽기만 한다.

  python3 -B scripts/jev/export_modeltest.py OUT_DIR

문항 한 줄: {id, set, task, kind(choice|noul), instructions, state, options, gold, chars}
  set  S1 첫 시험 자산 종류, S2 어려운 시험(v2 질문), S3 어려운 시험 2(goldset_hard3.json이 있을 때)
  gold choice는 선택지 이름, noul은 'true' 또는 'false'
"""
import json, pathlib, sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import jev_choice_test as C  # noqa: E402
import jev_hard_test as H  # noqa: E402

ROOT = C.ROOT
H3 = ROOT / 'docs' / 'research' / 'Jev시험3_2026-10-10' / 'goldset_hard3.json'


def norm(g):
    return 'true' if g is True else 'false' if g is False else g


def rec(i, s, task, q, state, gold):
    opts = q['criteria']
    return {'id': i, 'set': s, 'task': task, 'kind': q['type'], 'instructions': q['instructions'], 'state': state,
            'options': opts, 'gold': norm(gold), 'chars': len(json.dumps(state, ensure_ascii=False))}


def s1():
    g = json.loads((C.OUT.parent / 'Jev시험_2026-10-09' / 'goldset.json').read_text(encoding='utf-8'))
    order = g['asset_kinds']['options']
    out = []
    for it in g['asset_items']:
        p = C.asset_payload(it, order)
        out.append(rec('S1-' + it['id'], 'S1', 'asset', p['questions']['asset_kind'], p['state'], it['gold']))
    return out


def s2():
    out = []
    for kind, it in H.items():
        p = H.payload(kind, it, 'v2')
        gold = H.golds(it, kind)
        for task, q in p['questions'].items():
            t = 'asset' if task == 'asset_kind' else task
            out.append(rec(f"S2-{it['id']}-{t}", 'S2', t, q, p['state'], gold[t]))
    return out


def s3():
    """goldset_hard3.json 문항. asset은 v2 자산 질문, yesno는 rule별 v2 질문."""
    if not H3.exists():
        return []
    out = []
    for it in json.loads(H3.read_text(encoding='utf-8'))['items']:
        if it['kind'] == 'asset':
            q = {'type': 'choice', 'instructions': H.ASSET_Q2, 'criteria': H.KIND_TEXT2}
            t = 'asset'
        elif it['rule'] == 'R08':
            q = {'type': 'choice', 'instructions': H.R08_Q2, 'criteria': H.R08_TEXT2}
            t = 'R08'
        elif it['rule'] == 'R11':
            q = H.noul_q(*H.NOUL2['R11_narrow'])
            t = 'R11_narrow'
        else:
            t = it['rule']
            q = H.noul_q(*H.NOUL2[t])
        gold = it['gold']
        if q['type'] == 'noul':
            gold = 'true' if str(gold).lower() in ('yes', 'true', '예') else 'false'
        try:
            state = json.loads(it['input'])  # 입력이 {document, text} JSON 문자열인 문항
            assert isinstance(state, dict)
        except (ValueError, AssertionError):
            state = {'text': it['input']}
        out.append(rec('S3-' + it['id'], 'S3', t, q, state, gold))
    return out


if __name__ == '__main__':
    out_dir = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else sys.exit(__doc__)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = s1() + s2() + s3()
    ids = [r['id'] for r in rows]
    assert len(ids) == len(set(ids)), '문항 이름이 겹침'
    for r in rows:
        assert r['gold'] in r['options'], (r['id'], r['gold'])
    (out_dir / 'questions.jsonl').write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n', encoding='utf-8')
    from collections import Counter
    print(len(rows), dict(Counter(r['set'] for r in rows)))
    print(dict(Counter((r['set'], r['task']) for r in rows)))
    print('chars max', max(r['chars'] for r in rows), 'median', sorted(r['chars'] for r in rows)[len(rows) // 2])
