"""모델 시험: questions.jsonl을 모델에 묻고 선택지 확률과 정답 여부를 results_<이름>.jsonl에 쓴다. 학습은 하지 않는다.

  python run_eval.py --model kakaocorp/kanana-1.5-8b-instruct-2505 --name kanana
  python run_eval.py --model google/gemma-4-E4B-it --name gemma4e4b
  python run_eval.py --report            results_*.jsonl을 읽어 점수표만 출력

옵션: --load 4bit|fp16(기본 4bit)  --max-chars N(기본 12000, 이보다 긴 입력은 건너뛰고 skipped로 기록)  --limit N
이미 결과가 있는 문항은 다시 묻지 않는다(중간에 끊겨도 이어서 돌린다).
방식: 채팅 틀로 질문을 만들고 'Answer: '를 미리 채운 뒤, 다음 글자가 선택지 글자(A, B, ...)일 확률을 읽는다.
"""
import argparse, json, math, pathlib, sys, time

HERE = pathlib.Path(__file__).resolve().parent
LETTERS = 'ABCDEFGHIJKLMNOP'


def build_prompt(q):
    names = list(q['options'])
    if q['kind'] == 'noul':
        names = ['true', 'false']
    lines = [q['instructions'], '', 'Input:']
    for k, v in q['state'].items():
        lines.append(f'{k}: {v}')
    lines += ['', 'Options:']
    for L, n in zip(LETTERS, names):
        label = {'true': 'yes', 'false': 'no'}.get(n, n) if q['kind'] == 'noul' else n
        lines.append(f"{L}. {label}: {q['options'][n]}")
    lines += ['', 'Answer with the letter of the best option only.']
    return '\n'.join(lines), names


def load_model(name, mode):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    tok = AutoTokenizer.from_pretrained(name)
    kw = {'device_map': 'auto'}
    if mode == '4bit':
        kw['quantization_config'] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype=torch.float16)
    else:
        kw['torch_dtype'] = torch.float16
    return tok, AutoModelForCausalLM.from_pretrained(name, **kw)


def letter_ids(tok, n):
    ids = []
    for L in LETTERS[:n]:
        s = {tok.encode(L, add_special_tokens=False)[-1], tok.encode(' ' + L, add_special_tokens=False)[-1]}
        ids.append(sorted(s))
    return ids


def ask(tok, model, q):
    import torch
    text, names = build_prompt(q)
    chat = tok.apply_chat_template([{'role': 'user', 'content': text}], add_generation_prompt=True, tokenize=False) + 'Answer: '
    enc = tok(chat, return_tensors='pt', add_special_tokens=False).to(model.device)
    with torch.inference_mode():
        logits = model(**enc).logits[0, -1].float()
    lp = torch.log_softmax(logits, -1)
    ids = letter_ids(tok, len(names))
    sc = [torch.logsumexp(lp[i], 0).item() for i in ids]
    m = max(sc)
    z = sum(math.exp(s - m) for s in sc)
    probs = {n: math.exp(s - m) / z for n, s in zip(names, sc)}
    mass = math.exp(torch.logsumexp(torch.stack([torch.logsumexp(lp[i], 0) for i in ids]), 0).item())
    return probs, mass, enc['input_ids'].shape[1]


def report():
    for f in sorted(HERE.glob('results_*.jsonl')):
        rows = [json.loads(l) for l in f.read_text(encoding='utf-8').splitlines() if l.strip()]
        done = [r for r in rows if not r.get('skipped')]
        print(f'\n## {f.name}: 답한 {len(done)}, 건너뜀 {len(rows) - len(done)}')
        keys = sorted({(r['set'], r['task']) for r in done})
        for s, t in keys:
            rs = [r for r in done if (r['set'], r['task']) == (s, t)]
            ok = sum(r['correct'] for r in rs)
            hi = [r for r in rs if r['conf'] >= 0.95]
            print(f'{s} {t}: {ok}/{len(rs)}  확신 0.95 이상 {len(hi)}건 중 오답 {sum(not r["correct"] for r in hi)}')
        ok = sum(r['correct'] for r in done)
        print(f'합계: {ok}/{len(done)}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model'); ap.add_argument('--name'); ap.add_argument('--load', default='4bit')
    ap.add_argument('--max-chars', type=int, default=12000); ap.add_argument('--limit', type=int); ap.add_argument('--report', action='store_true')
    a = ap.parse_args()
    if a.report:
        return report()
    out = HERE / f'results_{a.name}.jsonl'
    qs = [json.loads(l) for l in (HERE / 'questions.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    have = {json.loads(l)['id'] for l in out.read_text(encoding='utf-8').splitlines() if l.strip()} if out.exists() else set()
    todo = [q for q in qs if q['id'] not in have][:a.limit]
    print(f'문항 {len(qs)}, 이미 한 것 {len(have)}, 이번에 할 것 {len(todo)}', flush=True)
    tok, model = load_model(a.model, a.load)
    with out.open('a', encoding='utf-8') as fh:
        for i, q in enumerate(todo, 1):
            r = {'id': q['id'], 'set': q['set'], 'task': q['task'], 'gold': q['gold'], 'chars': q['chars'], 'model': a.model, 'load': a.load}
            if q['chars'] > a.max_chars:
                r['skipped'] = f"입력 {q['chars']}자 > {a.max_chars}"
            else:
                t0 = time.time()
                try:
                    probs, mass, ntok = ask(tok, model, q)
                    pred = max(probs, key=probs.get)
                    r.update(pred=pred, conf=probs[pred], probs=probs, letter_mass=mass, tokens=ntok, correct=pred == q['gold'], secs=round(time.time() - t0, 2))
                except Exception as e:  # 메모리 부족 등은 기록하고 다음 문항으로
                    r['skipped'] = f'오류 {type(e).__name__}: {str(e)[:200]}'
            fh.write(json.dumps(r, ensure_ascii=False) + '\n'); fh.flush()
            if i % 10 == 0 or i == len(todo):
                print(f'{i}/{len(todo)}', flush=True)
    report()


if __name__ == '__main__':
    main()
