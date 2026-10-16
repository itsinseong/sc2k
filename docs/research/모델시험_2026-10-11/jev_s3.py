"""Jev로 S3 문항(12000자 이하)을 잰다. 질문 글과 선택지는 시험 파일 그대로. 결과는 다른 모델과 같은 꼴로 results_jev_s3.jsonl에.
  python3 -B jev_s3.py <questions.jsonl>
확신값은 Jev 2차 시험과 같은 정의: 고르기는 Jev가 준 confidence, 예/아니오는 |2p-1|.
"""
import json, pathlib, sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'scripts' / 'jev'))
import jev_choice_test as C  # noqa: E402  (키 불러오기와 API 호출만 쓴다)

BUDGET_USD = 0.50
LONG = len(sys.argv) > 2 and sys.argv[2] == '--long'  # 12000자 넘는 문항(모든 세트)
OUT = HERE / ('results_jev_long.jsonl' if LONG else 'results_jev_s3.jsonl')


def main():
    qs = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
    qs = [q for q in qs if q['chars'] > 12000] if LONG else [q for q in qs if q['set'] == 'S3' and q['chars'] <= 12000]
    have = {json.loads(l)['id'] for l in OUT.read_text(encoding='utf-8').splitlines() if l.strip()} if OUT.exists() else set()
    key = C.load_key()
    cost = 0.0
    with OUT.open('a', encoding='utf-8') as fh:
        for q in qs:
            if q['id'] in have:
                continue
            if cost >= BUDGET_USD:
                print('예산 한도'); break
            p = {'model': C.MODEL, 'state': q['state'],
                 'questions': {q['task']: {'type': q['kind'], 'instructions': q['instructions'], 'criteria': q['options']}}}
            code, resp, sec = C.request(key, 'POST', '/systemone', p)
            r = {'id': q['id'], 'set': q['set'], 'task': q['task'], 'gold': q['gold'], 'chars': q['chars'], 'model': C.MODEL, 'status': code}
            if code == 200:
                cost += resp.get('usage', {}).get('input_tokens', 0) * C.USD_PER_TOKEN
                a = resp['answers'][q['task']]
                if a['type'] == 'noul':
                    pred = 'true' if a['noul'] >= 0.5 else 'false'
                    r.update(pred=pred, p_yes=a['noul'], conf=round(abs(2 * a['noul'] - 1), 4))
                else:
                    r.update(pred=a['choice'], conf=a['confidence'], probs=a.get('probabilities'))
                r['correct'] = r['pred'] == q['gold']
                r['usage'] = resp.get('usage')
            else:
                r['skipped'] = f"HTTP {code}: {str(resp.get('error', ''))[:200]}"
            fh.write(json.dumps(r, ensure_ascii=False) + '\n'); fh.flush()
            print(q['id'], code, r.get('pred'), r.get('correct'), f'{sec:.1f}s', flush=True)
            if code not in (200, 422):
                break
    rs = [json.loads(l) for l in OUT.read_text(encoding='utf-8').splitlines() if l.strip()]
    d = [r for r in rs if 'pred' in r]
    print('answered', len(d), 'correct', sum(r['correct'] for r in d), 'usd', round(cost, 5))


if __name__ == '__main__':
    main()
