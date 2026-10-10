"""Jev(TypeSafe) 2차 시험: 어려운 정답 세트(docs/research/Jev시험2_2026-10-09/goldset_hard.json)를 두 판의 질문으로 묻는다.

v1  첫 시험(jev_choice_test.py) 질문 문구 그대로. 자산 입력은 발행사, 코인, 줄 이름만(첫 시험은 Circle 줄에 표 구역도 줬다).
    R08에는 선택지 none(검증 보고서 없음)을 더했다(정답이 none인 문항이 있다). R14는 첫 시험에 없어 화면 문구(site/화면문구.json
    R14 규칙 설명)를 첫 시험과 같은 방식으로 옮겼다.
v2  고친 질문. 자산 입력에 표 구역, 열 이름, 각주를 더하고 레포 관례(펀드 안 보유, 역레포 담보, 정산 줄)를 선택지 설명에 적었다.
    예/아니오는 규칙 뜻을 적고 근거가 없으면 아니오라고 적었다. R08은 선택지마다 판별 기준 한 줄(예시 문구는 뺐다).
    R11은 정답 기준이 미정이라 넓게, 좁게 두 질문을 한 요청에 함께 묻는다. 어느 판에도 문항별 힌트는 없다.
두 판 모두 문서 이름은 정답 세트의 state_label(문서 종류를 드러내지 않는 이름)이다.

  python3 -B scripts/jev/jev_hard_test.py run [--limit N]   Jev를 불러 results.json, summary.md를 쓴다(같은 요청의 200 응답은 다시 부르지 않는다)
  python3 -B scripts/jev/jev_hard_test.py report            API를 부르지 않고 results.json의 원응답으로 채점과 summary.md를 다시 쓴다

키는 jev_choice_test.load_key(레포 루트 .env.local TYPESAFE_API_KEY). 값은 출력하지 않는다. data/*.json은 읽기만 한다.
"""
import datetime, hashlib, json, pathlib, re, statistics, sys

sys.dont_write_bytecode = True  # 레포에 __pycache__를 새로 쓰지 않는다
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from jev_choice_test import (API, ASSET_Q, BUDGET_USD, KIND_TEXT, MODEL, NOUL, R08_Q, R08_TEXT, ROOT, USD_PER_TOKEN,  # noqa: E402
                             load_key, pct, request, show)

OUT = ROOT / 'docs' / 'research' / 'Jev시험2_2026-10-09'
FIRST = ROOT / 'docs' / 'research' / 'Jev시험_2026-10-09'
GOLD = json.loads((OUT / 'goldset_hard.json').read_text(encoding='utf-8'))

# ---- v1: 첫 시험 문구 ----
R08_TEXT1 = {**R08_TEXT, 'none': GOLD['yesno']['r08_option_proposed']['none']}
R14_V1 = ('Does the text say that holders of the stablecoin are not paid interest?',
          {'true': 'The text says that holders do not receive interest on the stablecoin.',
           'false': 'The text does not say that holders are not paid interest.'})

# ---- v2: 고친 문구(일반 설명. 문항별 힌트 없음) ----
ASSET_Q2 = ('Which asset category does this line of a stablecoin reserve report belong to? Decide from the line name together with '
            'the table section, column, and notes given with it, and follow the conventions written in the category descriptions.')
KIND_TEXT2 = {
    **KIND_TEXT,
    'reverse_repo_overnight': ("Overnight reverse repurchase agreements: cash lent for one day against securities as collateral. "
                               "Repurchase agreements held as reserve assets are reverse repurchase agreements from the reserve's side, "
                               'and securities listed as collateral received under them count as the agreement, not as securities held.'),
    'reverse_repo_term': ('Term reverse repurchase agreements: cash lent for more than one day against securities as collateral. '
                          'Securities listed as collateral received under them count as the agreement, not as securities held.'),
    'government_mmf': ("Shares of money market funds, such as government money market funds: the reserve's holding of the fund as a "
                       "whole. A line that breaks down what a fund holds, or shows the fund's indirect exposure to an asset, is "
                       'classified as that underlying asset instead.'),
    'settlement': ('Not an investment: an adjustment for timing and settlement differences (amounts due to or owed by the reserve for '
                   'deposits, withdrawals, trades, mints, or redemptions not yet settled), accrued interest or other income '
                   'receivable, or rounding differences.'),
}
R08_Q2 = ("What kind of independent accountant engagement is reported in this document? Decide from the accountant's own report on "
          'this document: what it calls the engagement and the form of its conclusion. If the document contains no report by an '
          'independent accountant on it, choose none.')
R08_TEXT2 = {
    'agreed_upon_procedures': ('The accountant performed procedures agreed with the company and reports the results, stating that it '
                               'gives no opinion, conclusion, or assurance.'),
    'review': ('Limited assurance: the accountant gives a negative-form conclusion, saying nothing came to its attention that the '
               'subject matter is misstated.'),
    'examination': ("Reasonable assurance that the accountant's report calls an examination: a positive opinion on management's "
                    'assertion or on the subject matter.'),
    'reasonable assurance': ("Reasonable assurance that the accountant's report calls a reasonable assurance engagement or report, "
                             'not an examination: a positive opinion.'),
    'audit': 'An audit opinion on a set of financial statements.',
    'none': 'There is no report by an independent accountant on this document; it was prepared by the issuer or another party.',
}
assert list(R08_TEXT2) == list(R08_TEXT1)
_AMT = ('The circulating amount means the number of tokens the issuer counts as outstanding and owed to holders; reports may call it '
        'tokens in circulation, outstanding tokens, or the liability for tokens issued.')
_TQ = GOLD['terms']['question']
NOUL2 = {
    'R11_broad': (f'Does the text say what the circulating amount of tokens consists of, or how it was calculated? {_AMT} Answer yes '
                  'if the text defines which tokens or balances are counted, even without a calculation; naming only where the number '
                  'was taken from does not count. If the text has neither a definition nor a calculation, answer no.',
                  {'true': 'The text defines which tokens or balances make up the circulating amount, or explains how it was calculated.',
                   'false': ('The text gives the circulating amount, or only its source, without saying what is counted or how it '
                             'was calculated.')}),
    'R11_narrow': (f'Does the text explain how the circulating amount of tokens was calculated? {_AMT} Answer yes only if the text '
                   'states which tokens are added or subtracted to reach it, for example tokens issued, redeemed or burned, frozen, '
                   'held by the issuer, or not redeemable. A definition that only names the balance counted, with nothing added or '
                   'subtracted, does not count. If the text has no such calculation, answer no.',
                   {'true': 'The text states which tokens are added to or subtracted from a total to reach the circulating amount.',
                    'false': 'The text gives the circulating amount, its definition, or its source, but no addition or subtraction.'}),
    'R12': ('Does the text name a specific bank or custodian that holds the reserve assets? Answer yes only if the text gives the '
            'proper name of at least one institution where reserve assets are deposited or held in custody. If it does not, answer no.',
            {'true': 'At least one bank or custodian where reserve assets are deposited or held is named.',
             'false': ('No such institution is named: institutions holding the reserve are described only by type (for example '
                       '"regulated financial institutions"), by an anonymous label (for example "Bank 1"), or not at all, and other '
                       'names in the text belong to parties that do not hold the reserve.')}),
    'R15': ("Did a member of the issuer's management sign or approve a statement or report in this document? Answer yes only if the "
            "document itself contains a statement or report from the issuer's management or board that is signed or approved by a "
            "named officer or director with a title; officers and directors of the issuer's parent company count as management. "
            'If it does not, answer no.',
            {'true': ("The document contains a statement or report from the issuer's management or board, signed or approved by a "
                      'named officer or director with a title.'),
             'false': ('No such signature or approval is in the document: only the accountant or another party signed, the text '
                       'only describes what management is responsible for or must certify, or nobody signed.')}),
    'R14': (_TQ['instructions_suggested'] + ' Answer yes only if the text itself contains such a statement. If it does not, answer no.',
            _TQ['criteria_suggested']),
}

TASKS = {'asset': '자산 종류(16종 중 하나)', 'R08': 'R08 검증 종류(6종 중 하나)', 'R11_broad': 'R11 계산식 공개 넓게 기준',
         'R11_narrow': 'R11 계산식 공개 좁게 기준', 'R12': 'R12 보관 기관 이름', 'R15': 'R15 경영진 서명', 'R14': 'R14 이자 없음 문장(약관)'}
DIFF = {'name_outside': '줄 이름 밖에 정체', 'misleading': '다른 종류로 끄는 말', 'near_class': '가까운 종류끼리',
        'format_variant': '발행사마다 다른 표기', 'old_format': '옛 서식', 'easy': '쉬운 대조'}
BINS = ((0, .5, '0.5 미만'), (.5, .8, '0.5~0.8'), (.8, .9, '0.8~0.9'), (.9, .95, '0.9~0.95'), (.95, 1.01, '0.95 이상'))
EDGES = (0.5, 0.8, 0.9, 0.95)  # 확신 기준 후보(구간 경계)
MIN_N = 10  # 확신 기준을 추천하려면 기준 위에 남는 문항이 이만큼은 있어야 한다


def noul_q(ins, crit):
    return {'type': 'noul', 'instructions': ins, 'criteria': crit}


def payload(kind, it, ver):
    v1 = ver == 'v1'
    if kind == 'asset':
        state = {'issuer': it['issuer'], 'token': it['coin'], 'line_name': it['line_name']}
        if not v1:
            # 구역 제목이 없는 표(section_note)는 section에 이 줄들을 묶는 아래 합계 줄 이름이 들어 있다
            state['group_total_line' if it.get('section_note') else 'table_section'] = it['section']
            if it.get('column'): state['table_column'] = it['column']
            if it['context']: state['notes'] = it['context']
        qs = {'asset_kind': {'type': 'choice', 'instructions': ASSET_Q if v1 else ASSET_Q2, 'criteria': KIND_TEXT if v1 else KIND_TEXT2}}
    elif kind == 'terms':
        state = {'document': it['context'], 'text': it['clause']}
        qs = {'R14': noul_q(*(R14_V1 if v1 else NOUL2['R14']))}
    else:
        state = {'document': it['state_label'], 'text': it['text']}
        rule = it['rule']
        if rule == 'R08':
            qs = {'R08': {'type': 'choice', 'instructions': R08_Q if v1 else R08_Q2, 'criteria': R08_TEXT1 if v1 else R08_TEXT2}}
        elif v1:
            qs = {rule: noul_q(*NOUL[rule])}
        elif rule == 'R11':
            qs = {k: noul_q(*NOUL2[k]) for k in ('R11_broad', 'R11_narrow')}
        else:
            qs = {rule: noul_q(*NOUL2[rule])}
    return {'model': MODEL, 'state': state, 'questions': qs}


def items():
    """(종류, 문항) 목록. 종류는 asset, yesno, terms."""
    return ([('asset', x) for x in GOLD['assets']['items']] + [('yesno', x) for x in GOLD['yesno']['items']]
            + [('terms', x) for x in GOLD['terms']['items']])


def plan():
    return [(f"{it['id']}-{ver}", kind, it, ver, payload(kind, it, ver)) for kind, it in items() for ver in ('v1', 'v2')]


def sha(p):
    return hashlib.sha256(json.dumps(p, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_results():
    f = OUT / 'results.json'
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}


def save(meta, calls):
    res = {'meta': meta, 'rows': score(calls), 'calls': calls}
    (OUT / 'results.json').write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return res


def run(limit=None):
    old = load_results()
    cached = {c['req']: c for c in old.get('calls', []) if c['status'] == 200}
    spend = old.get('meta', {}).get('spend_log', [])
    key = load_key()
    meta = {'date': datetime.date.today().isoformat(), 'endpoint': API + '/systemone', 'model_requested': MODEL,
            'usd_per_million_input_tokens': 0.042, 'goldset': 'goldset_hard.json',
            'questions': {'v1': {'asset': {'instructions': ASSET_Q, 'criteria': KIND_TEXT},
                                 'R08': {'instructions': R08_Q, 'criteria': R08_TEXT1},
                                 **{k: {'instructions': v[0], 'criteria': v[1]} for k, v in NOUL.items()},
                                 'R14': {'instructions': R14_V1[0], 'criteria': R14_V1[1]}},
                          'v2': {'asset': {'instructions': ASSET_Q2, 'criteria': KIND_TEXT2},
                                 'R08': {'instructions': R08_Q2, 'criteria': R08_TEXT2},
                                 **{k: {'instructions': v[0], 'criteria': v[1]} for k, v in NOUL2.items()}}},
            'state_fields': {'asset_v1': 'issuer, token, line_name',
                             'asset_v2': 'issuer, token, line_name, table_section(구역 제목이 없는 표는 group_total_line), table_column, notes',
                             'yesno': 'document(state_label), text', 'terms': 'document(context), text(clause)'}}
    calls, fresh, cost = [], [], 0.0
    for rid, kind, it, ver, p in plan()[:limit]:
        h = sha(p)
        if rid in cached and cached[rid].get('payload_sha256') == h:
            calls.append(cached[rid])
            continue
        if cost >= BUDGET_USD:
            print('예산 한도에 닿아 멈춘다', flush=True)
            break
        code, resp, sec = request(key, 'POST', '/systemone', p)
        u = resp.get('usage', {}) if code == 200 else {}
        cost += u.get('input_tokens', 0) * USD_PER_TOKEN
        fresh.append({'req': rid, 'set': kind, 'item': it['id'], 'ver': ver, 'status': code, 'seconds': round(sec, 3),
                      'model': resp.get('model'), 'usage': u, 'payload_sha256': h,
                      'state_chars': len(json.dumps(p['state'], ensure_ascii=False)), 'response': resp})
        calls.append(fresh[-1])
        print(rid, code, u, f'{sec:.2f}s', flush=True)
        if code not in (200, 422): break  # 키, 권한, 서버 문제면 더 부르지 않는다. 422(형식, 길이)는 적고 넘어간다
        if len(fresh) % 25 == 0: save({**meta, 'spend_log': spend}, calls)  # 중간 저장(끊겨도 받은 응답은 다시 부르지 않는다)
    tin = sum(c['usage'].get('input_tokens', 0) for c in fresh)
    spend.append({'at': datetime.datetime.now().isoformat(timespec='seconds'), 'limit': limit, 'calls': len(fresh),
                  'input_tokens': tin, 'output_tokens': sum(c['usage'].get('output_tokens', 0) for c in fresh),
                  'usd': round(tin * USD_PER_TOKEN, 6)})
    write_summary(save({**meta, 'spend_log': spend}, calls))


# ---- 채점 ----

def golds(it, kind):
    """{과제: 정답}. R11은 넓게, 좁게 기준 정답을 따로 둔다(미정이 아닌 문항은 둘이 같다)."""
    if kind == 'asset': return {'asset': it['gold']}
    if kind == 'terms': return {'R14': it['gold'] == '예'}
    if it['rule'] != 'R11': return {it['rule']: it['gold']}
    if it.get('r11_pending'): return {'R11_broad': it['gold_broad'], 'R11_narrow': it['gold_narrow']}
    return {'R11_broad': it['gold'], 'R11_narrow': it['gold']}


def score(calls):
    by = {c['req']: c for c in calls if c['status'] == 200}
    rows = []
    for kind, it in items():
        for ver in ('v1', 'v2'):
            c = by.get(f"{it['id']}-{ver}")
            if not c: continue
            ans = c['response']['answers']
            for task, g in golds(it, kind).items():
                qk = ('asset_kind' if kind == 'asset' else 'R14' if kind == 'terms'
                      else 'R11' if ver == 'v1' and task.startswith('R11') else task)
                a = ans[qk]
                row = {'id': it['id'], 'ver': ver, 'task': task, 'set': kind, 'gold': g,
                       'constructed': bool(it.get('constructed')), 'pending': bool(it.get('r11_pending'))}
                if a['type'] == 'noul':
                    row.update(answer=a['noul'] >= 0.5, p_yes=a['noul'], confidence=round(abs(2 * a['noul'] - 1), 4))
                else:
                    row.update(answer=a['choice'], confidence=a['confidence'], p_gold=a['probabilities'].get(g))
                row['correct'] = row['answer'] == g
                if kind == 'asset':
                    row.update(where=f"{it['coin']} {it['month']}", input=it['line_name'], group=it['difficulty'])
                elif kind == 'terms':
                    row.update(where=f"{it['coin']} 약관({it['doc_by']})", input=f"{pathlib.Path(it['doc_file']).name} {it['lines']}",
                               group=it['unit'])
                else:
                    row.update(where=f"{it['coin']} {it['month'] or it['date']}", input=pathlib.Path(it['source']).name,
                               group=it['publisher_group'])
                rows.append(row)
    return rows


# ---- 요약 ----

def acc(rs):
    return pct(sum(r['correct'] for r in rs), len(rs))


def sel(rows, **kw):
    return [r for r in rows if all(r[k] == v for k, v in kw.items())]


def gate(rs):
    """구간 경계 가운데 '그 값 이상이 모두 맞고 MIN_N개 이상 남는' 가장 낮은 값과 그 위 문항 수. 없으면 (None, 이유)."""
    for e in EDGES:
        keep = [r for r in rs if r['confidence'] >= e]
        if all(r['correct'] for r in keep):
            return (e, len(keep)) if len(keep) >= MIN_N else (None, f'{e} 이상이 모두 맞지만 {len(keep)}개뿐')
    return None, f'{EDGES[-1]} 이상에도 오답'


def top_wrong(rs):
    w = [r['confidence'] for r in rs if not r['correct']]
    return f'{max(w):.2f}' if w else '오답 없음'


def first_sentence(s):
    s = (s or '').strip()
    m = re.search(r'다\.(\s|$)', s)
    return s[:m.end()].strip() if m else s


def write_summary(res):
    meta, rows, calls = res['meta'], res['rows'], res['calls']
    by_id = {it['id']: (kind, it) for kind, it in items()}
    kept = GOLD['planned_vs_kept']
    built, now = sum(v['built'] for v in kept.values()), sum(v['kept'] for v in kept.values())
    a_items, y_items, t_items = GOLD['assets']['items'], GOLD['yesno']['items'], GOLD['terms']['items']
    L = ['# Jev 2차 시험: 어려운 정답 세트', '',
         f"> 정답 세트가 계획(만든 문항 {built}개)보다 작다: {built - now}개를 검증에서 뺐다. "
         + ', '.join(f"{name} {kept[k]['built']} → {kept[k]['kept']}({', '.join(kept[k]['dropped'])})"
                     for k, name in (('assets', '자산'), ('yesno', '예/아니오와 R08'), ('terms', '약관 R14')))
         + '. 그래서 R15 아니오 5문항은 모두 다른 회사 문서이고(만든 문항 없음), 자산 정답에 precious_metal이 없다. '
           '뺀 까닭은 goldset_hard.json dropped_reasons.', '',
         f"- 날짜 {meta['date']}, 모델 {MODEL}(TypeSafe), 주소 {meta['endpoint']}. 정답 세트 goldset_hard.json, 원응답과 채점 results.json, "
         '스크립트 scripts/jev/jev_hard_test.py.',
         f"- 자산 {len(a_items)}줄(어려운 줄 {sum(x['difficulty'] != 'easy' for x in a_items)}, 쉬운 대조 "
         f"{sum(x['difficulty'] == 'easy' for x in a_items)}). 예/아니오와 R08 {len(y_items)}문항("
         + ', '.join(f"{r} {sum(x['rule'] == r for x in y_items)}" for r in ('R08', 'R11', 'R12', 'R15'))
         + f"). 약관 R14 {len(t_items)}문항. 만든 문항(근거를 지운 아니오, 지운 쪽과 줄은 정답 세트에 적음) "
         f"{sum(bool(x.get('constructed')) for x in y_items + t_items)}개.",
         '- 두 판: v1은 첫 시험 질문 문구 그대로다(자산 입력은 발행사, 코인, 줄 이름만. R08에는 정답 none 문항이 있어 선택지 none을 더했고, '
         'R14는 첫 시험에 없어 화면 문구의 R14 설명을 같은 방식으로 옮겼다). v2는 고친 질문이다(아래 "고친 질문에서 바뀐 것"). '
         '문구 전문은 results.json meta.questions.',
         '- Noul(예/아니오) 확신값은 |2p-1|이다. 확신 0.8은 p 0.9 이상 또는 0.1 이하다. 고르기(choice) 확신값은 Jev가 준 값이다.', '']
    # 정답 세트 convention 칸(펀드 안 보유, 역레포 담보)이 있는 줄과 펀드 합계 줄(펀드 구역의 TOTAL 줄). v2 설명이 직접 닿는 줄이다
    conv = {it['id'] for it in a_items if it.get('convention')
            or (it['line_name'].upper().startswith('TOTAL') and 'FUND' in (it['section'] or '').upper())}
    idx2 = {(r['id'], r['task'], r['ver']): r for r in rows}
    flips = [(r, idx2[(r['id'], r['task'], 'v2')]) for r in rows
             if r['ver'] == 'v1' and (r['id'], r['task'], 'v2') in idx2 and r['correct'] != idx2[(r['id'], r['task'], 'v2')]['correct']]
    ca = lambda v, inside: acc([r for r in sel(rows, task='asset', ver=v) if (r['id'] in conv) == inside])
    v1hi = [r for r in rows if r['ver'] == 'v1' and not r['correct'] and r['confidence'] >= 0.8]
    v2hi = [r for r in rows if r['ver'] == 'v2' and not r['correct'] and r['confidence'] >= 0.8]
    pv = lambda t, v: acc([r for r in sel(rows, task=t, ver=v) if r['pending']])
    L += ['## 요점', '',
          '- 맞은 수 v1 → v2: ' + ', '.join(f"{TASKS[t].split('(')[0]} {sum(r['correct'] for r in sel(rows, task=t, ver='v1'))}→"
                                         f"{sum(r['correct'] for r in sel(rows, task=t, ver='v2'))}/{len(sel(rows, task=t, ver='v2'))}"
                                         for t in TASKS if sel(rows, task=t, ver='v2')) + '.',
          f"- v2에서 새로 맞음 {sum(b['correct'] for a, b in flips)}건, 새로 틀림 {sum(not b['correct'] for a, b in flips)}건"
          f"({', '.join(a['id'] for a, b in flips if not b['correct'])}).",
          f"- 자산 종류: 레포 관례가 닿는 줄 v1 {ca('v1', True)} → v2 {ca('v2', True)}, 나머지 줄 v1 {ca('v1', False)} → v2 {ca('v2', False)}.",
          f"- 확신 0.8 이상인데 틀린 답: v1 {len(v1hi)}건({', '.join(sorted({TASKS[r['task']].split('(')[0] for r in v1hi})) or '없음'}), v2 {len(v2hi)}건.",
          f"- R11 기준 미정 7문항: 넓게 기준 v1 {pv('R11_broad', 'v1')}, v2 {pv('R11_broad', 'v2')}. 좁게 기준 v1 {pv('R11_narrow', 'v1')}, "
          f"v2 {pv('R11_narrow', 'v2')}.",
          '- 추천 확신 기준(v2)은 아래 "확신 기준 추천" 표. 오답이 없는 항목은 기준을 좁힐 근거가 없어 가장 낮은 경계(0.5)가 나온다.', '']
    L += ['## 고친 질문(v2)에서 바뀐 것', '',
          '- 자산 종류: 입력에 표 구역 이름, 열 이름, 각주를 더했다. 선택지 설명에 레포 관례를 적었다. 펀드가 들고 있는 것을 풀어 적은 줄은 '
          '그 안의 자산으로, 펀드 전체를 가진 줄은 정부 MMF로, 역레포 담보로 적힌 국채는 역레포로 분류한다. 정산 줄은 결제 시점 차이, '
          '받을 이자와 수익, 반올림 차이라는 뜻이다.',
          '- R08: 선택지마다 판별 기준 한 줄(회계법인 보고서가 업무를 무엇이라 부르는지, 결론이 어떤 꼴인지). 예시 문구("We have examined")는 '
          '뺐다. 이 문서에 대한 회계법인 보고서가 없으면 none.',
          '- R11: 유통량이 무엇인지(발행사가 보유자에게 갚아야 할 토큰 수. 보고서에 따라 outstanding, liability for tokens issued로도 적음)를 '
          '적고 두 질문으로 나눴다. 넓게는 무엇을 세는지 정의만 있어도 예(출처만 적은 것은 아님), 좁게는 더하거나 뺀 토큰이 적혀 있어야 예.',
          '- R12: 준비금을 맡긴 은행이나 보관 기관의 고유 이름이 하나라도 있어야 예. 종류만 적은 것, "Bank 1" 같은 익명 표기, 준비금을 '
          '맡지 않은 곳의 이름은 아님.',
          '- R15: 이 문서 안에 경영진이나 이사회가 서명하거나 승인한 글이 이름, 직함과 함께 있어야 예. 모회사 임원과 이사회도 경영진으로 센다. '
          '회계법인 서명, 경영진 책임을 설명만 한 글은 아님.',
          '- R14: 보유자가 발행사에게서 이자나 수익을 받지 않는다는 문장이 글 안에 있어야 예(정답 세트의 제안 문구). 준비금 수익이 누구 몫인지만 '
          '적은 문장, 유통사나 거래소가 주는 보상은 아님.',
          '- 예/아니오 모두 "근거가 글에 없으면 아니오"라고 적었다. 설명은 모든 문항에 같은 글로 붙고, 문항마다 다른 힌트는 없다.', '']
    bad = [c for c in calls if c['status'] != 200]
    if bad:
        L += ['## 응답을 못 받은 요청', ''] + [f"- {c['req']} 상태 {c['status']}: {json.dumps(c['response'], ensure_ascii=False)[:300]}"
                                         for c in bad] + ['']

    L += ['## 항목별 정확도', '', '| 항목 | 문항 | v1 맞은 수 | v2 맞은 수 |', '|---|---|---|---|']
    for t, name in TASKS.items():
        v1, v2 = sel(rows, task=t, ver='v1'), sel(rows, task=t, ver='v2')
        if v1 or v2: L.append(f'| {name} | {max(len(v1), len(v2))} | {acc(v1)} | {acc(v2)} |')
    L += ['', 'R11 v1은 질문 하나의 답을 두 기준 정답에 각각 맞춰 봤다. v2는 넓게, 좁게 질문을 따로 물어 그 기준 정답에 맞췄다.']
    r11 = [r for r in rows if r['task'].startswith('R11') and not r['pending']]
    if r11:
        L.append('기준 미정이 아닌 R11 ' + str(len(sel(r11, task='R11_broad', ver='v1'))) + '문항(두 기준 정답이 같음): v1 '
                 + acc(sel(r11, task='R11_broad', ver='v1')) + ', v2 넓게 질문 ' + acc(sel(r11, task='R11_broad', ver='v2'))
                 + ', v2 좁게 질문 ' + acc(sel(r11, task='R11_narrow', ver='v2')) + '.')

    first = FIRST / 'results.json'
    if first.exists():
        fi = json.loads(first.read_text(encoding='utf-8'))['items']
        fa = {t: acc([x for x in fi if x['task'] == t]) for t in ('asset', 'R08', 'R11', 'R12', 'R15')}
        L += ['', '첫 시험(쉬운 세트, v1 문구)과 비교: 첫 시험 ' + ', '.join(f'{k} {v}' for k, v in fa.items())
              + ' → 이번 v1 ' + ', '.join(f"{k} {acc(sel(rows, task=k if k != 'R11' else 'R11_broad', ver='v1'))}"
                                         for k in ('asset', 'R08', 'R11', 'R12', 'R15'))
              + ', v2 ' + ', '.join(f"{k} {acc(sel(rows, task=k if k != 'R11' else 'R11_broad', ver='v2'))}"
                                   for k in ('asset', 'R08', 'R11', 'R12', 'R15'))
              + ' (R11은 넓게 기준).']

    if flips:
        L += ['', '## v1과 v2에서 맞고 틀림이 갈린 문항', '',
              f"v2에서 새로 맞음 {sum(b['correct'] for a, b in flips)}건, 새로 틀림 {sum(not b['correct'] for a, b in flips)}건. 칸 값: 답(확신값).", '',
              '| 번호 | 항목 | 정답 | v1 답 | v2 답 | 바뀜 |', '|---|---|---|---|---|---|']
        for a, b in sorted(flips, key=lambda ab: (ab[1]['correct'], ab[0]['task'], ab[0]['id'])):
            L.append(f"| {a['id']} | {TASKS[a['task']]} | {show(a['gold'])} | {show(a['answer'])}({a['confidence']:.2f}) | "
                     f"{show(b['answer'])}({b['confidence']:.2f}) | {'v2에서 맞음' if b['correct'] else 'v2에서 틀림'} |")

    L += ['', '## 어려움 유형별', '', '### 자산 종류', '', '| 유형 | 문항 | v1 | v2 |', '|---|---|---|---|']
    for g, name in DIFF.items():
        v1, v2 = sel(rows, task='asset', ver='v1', group=g), sel(rows, task='asset', ver='v2', group=g)
        if v1 or v2: L.append(f'| {name}({g}) | {max(len(v1), len(v2))} | {acc(v1)} | {acc(v2)} |')
    L += ['', 'v2 선택지 설명에 적은 레포 관례(펀드 안 보유, 펀드 합계 줄, 역레포 담보)가 직접 닿는 줄과 나머지 줄:', '',
          '| 묶음 | 문항 | v1 | v2 |', '|---|---|---|---|']
    for name, test in (('관례가 닿는 줄(' + ', '.join(sorted(conv)) + ')', lambda r: r['id'] in conv), ('나머지 줄', lambda r: r['id'] not in conv)):
        v1 = [r for r in sel(rows, task='asset', ver='v1') if test(r)]
        v2 = [r for r in sel(rows, task='asset', ver='v2') if test(r)]
        L.append(f'| {name} | {len(v1)} | {acc(v1)} | {acc(v2)} |')
    L += ['', '### 예/아니오와 R08: 정답 값별', '', '| 항목 | 정답 | 문항 | v1 | v2 |', '|---|---|---|---|---|']
    for t in ('R08', 'R11_broad', 'R11_narrow', 'R12', 'R15', 'R14'):
        for g in sorted({show(r['gold']) for r in sel(rows, task=t)}):
            v1 = [r for r in sel(rows, task=t, ver='v1') if show(r['gold']) == g]
            v2 = [r for r in sel(rows, task=t, ver='v2') if show(r['gold']) == g]
            L.append(f'| {TASKS[t]} | {g} | {max(len(v1), len(v2))} | {acc(v1)} | {acc(v2)} |')
    L += ['', '### 문서 묶음별(예/아니오와 R08, R11은 넓게 기준)', '', '| 문서 묶음 | 문항 | v1 | v2 |', '|---|---|---|---|']
    yrows = [r for r in rows if r['set'] == 'yesno' and r['task'] != 'R11_narrow']
    for g in sorted({r['group'] for r in yrows}, key=lambda g: -len([r for r in yrows if r['group'] == g])):
        v1, v2 = sel(yrows, ver='v1', group=g), sel(yrows, ver='v2', group=g)
        L.append(f'| {g} | {max(len(v1), len(v2))} | {acc(v1)} | {acc(v2)} |')
    L += ['', '### 약관 R14: 글 단위별', '', '| 단위 | 문항 | v1 | v2 |', '|---|---|---|---|']
    for g in ('전체', '절', '조항'):
        v1, v2 = sel(rows, task='R14', ver='v1', group=g), sel(rows, task='R14', ver='v2', group=g)
        if v1 or v2: L.append(f'| {g} | {max(len(v1), len(v2))} | {acc(v1)} | {acc(v2)} |')

    L += ['', '## 만든 사례와 진짜 사례', '', '만든 사례는 진짜 보고서나 약관에서 근거 쪽, 줄, 문장을 지운 아니오 문항이다. 진짜 아니오와 견주려고 진짜 쪽을 정답별로 나눴다.', '',
          '| 항목 | 진짜 예 v1 | 진짜 예 v2 | 진짜 아니오 v1 | 진짜 아니오 v2 | 만든 아니오 v1 | 만든 아니오 v2 |', '|---|---|---|---|---|---|---|']
    for t in ('R08', 'R11_broad', 'R11_narrow', 'R12', 'R15', 'R14'):
        cells = []
        for c, gtest in ((False, lambda g: g not in (False, 'none')), (False, lambda g: g in (False, 'none')), (True, lambda g: True)):
            for v in ('v1', 'v2'):
                cells.append(acc([r for r in sel(rows, task=t, ver=v, constructed=c) if gtest(r['gold'])]))
        L.append(f'| {TASKS[t]} | ' + ' | '.join(cells) + ' |')
    L += ['', 'R08은 none(검증 보고서 없음)을 아니오 쪽으로, 나머지 검증 종류를 예 쪽으로 셌다. R15는 만든 문항이 모두 검증에서 빠졌다.']

    L += ['', '## 확신값 구간별 정확도', '', '칸 값: 맞은 수/건수.']
    for v in ('v1', 'v2'):
        L += ['', f'### {v}', '', '| 항목 | ' + ' | '.join(b[2] for b in BINS) + ' |', '|---' * (len(BINS) + 1) + '|']
        for t, name in TASKS.items():
            rs = sel(rows, task=t, ver=v)
            if not rs: continue
            cells = []
            for lo, hi, _ in BINS:
                b = [r for r in rs if lo <= r['confidence'] < hi]
                cells.append(f"{sum(r['correct'] for r in b)}/{len(b)}" if b else '-')
            L.append(f'| {name} | ' + ' | '.join(cells) + ' |')

    L += ['', '## 확신 기준 추천(v2 기준)', '',
          f'후보는 구간 경계 {", ".join(map(str, EDGES))}이다. 항목마다 "이 값 이상만 자동 확정하면 그 안이 모두 맞는" 가장 낮은 경계를 골랐고, '
          f'그 위에 남는 문항이 {MIN_N}개 미만이면 추천하지 않는다. 기준 아래는 사람 확인 목록으로 간다.', '',
          '| 항목 | 문항 | 가장 높은 오답 확신값 | 추천 기준(확신값 이상) | 자동 확정 | 그 안의 정확도 | 확인 목록 | 참고: v1으로 재면 |',
          '|---|---|---|---|---|---|---|---|']
    for t, name in TASKS.items():
        rs = sel(rows, task=t, ver='v2')
        if not rs: continue
        cut, k = gate(rs)
        c1, k1 = gate(sel(rows, task=t, ver='v1'))
        ref = f'{c1}({k1}개 확정)' if c1 is not None else f'추천하지 않음({k1})'
        if cut is None:
            L.append(f'| {name} | {len(rs)} | {top_wrong(rs)} | 추천하지 않음({k}) | - | - | {len(rs)} | {ref} |')
        else:
            L.append(f'| {name} | {len(rs)} | {top_wrong(rs)} | {cut} | {pct(k, len(rs))} | {k}/{k} | {len(rs) - k} | {ref} |')
    L += ['', '- 이번 표본에서 잰 값이다. 기준 위가 모두 맞아도 문항이 n개면 실제 오답률이 약 3/n까지일 수 있다(95% 신뢰, 3의 규칙). '
          '예: 20문항이면 15%. 오답이 없는 항목은 표본 안에서 기준을 좁힐 근거가 없어 가장 낮은 경계가 나온다.',
          '- 같은 확신값이라도 16지선다(자산)와 예/아니오는 엄격함이 다르다. 예/아니오 확신 0.8은 p 0.9 이상 또는 0.1 이하다.']

    pend = [it for it in y_items if it.get('r11_pending')]
    if pend:
        L += ['', '## R11 기준 미정 문항', '',
              '넓게: 유통량의 정의만 밝혀도 예. 좁게: 더하고 뺀 계산까지 밝혀야 예. 칸 값: Jev 답(p, 예일 확률).', '',
              '| 번호 | 코인, 달 | 레포 값 | 넓게 정답 | 좁게 정답 | v1 답 | v2 넓게 질문 답 | v2 좁게 질문 답 |', '|---|---|---|---|---|---|---|---|']
        idx = {(r['id'], r['ver'], r['task']): r for r in rows}
        for it in pend:
            def cell(v, t):
                r = idx.get((it['id'], v, t))
                return f"{show(r['answer'])}({r['p_yes']:.2f})" if r else '-'
            L.append(f"| {it['id']} | {it['coin']} {it['month']} | {show(it['repo_value'])} | {show(it['gold_broad'])} | "
                     f"{show(it['gold_narrow'])} | {cell('v1', 'R11_broad')} | {cell('v2', 'R11_broad')} | {cell('v2', 'R11_narrow')} |")
        L.append('')
        for std, nm in (('R11_broad', '넓게'), ('R11_narrow', '좁게')):
            p1 = [r for r in sel(rows, task=std, ver='v1') if r['pending']]
            p2 = [r for r in sel(rows, task=std, ver='v2') if r['pending']]
            L.append(f'- {nm} 기준: v1 {acc(p1)}, v2({nm} 질문) {acc(p2)}')

    for v in ('v2', 'v1'):
        wrong = sorted([r for r in rows if r['ver'] == v and not r['correct']], key=lambda r: -r['confidence'])
        L += ['', f'## 틀린 사례({v}, 확신 높은 순)', '']
        if not wrong:
            L.append('없음')
            continue
        L += ['| 번호 | 항목 | 코인, 달 | 입력 | 정답 | Jev 답 | 확신값 | 만든 문항 | 문항을 어렵게 만든 점(정답 세트 why_hard 첫 문장) |',
              '|---|---|---|---|---|---|---|---|---|']
        for r in wrong:
            extra = f" (p={r['p_yes']:.2f})" if 'p_yes' in r else f" (정답 확률 {r.get('p_gold') or 0:.2f})"
            why = first_sentence(by_id[r['id']][1].get('why_hard')).replace('|', '/')
            inp = str(r['input']).replace('|', '/')
            L.append(f"| {r['id']} | {TASKS[r['task']]} | {r['where']} | {inp} | {show(r['gold'])} | {show(r['answer'])}{extra} | "
                     f"{r['confidence']:.2f} | {'예' if r['constructed'] else ''} | {why} |")
        hi = [r for r in wrong if r['confidence'] >= 0.8]
        L.append('')
        L.append(f'확신 0.8 이상 오답 {len(hi)}건' + (': ' + ', '.join(f"{r['id']} {r['task']}({r['confidence']:.2f})" for r in hi) if hi else '') + '.')

    ok = [c for c in calls if c['status'] == 200]
    tin, tout = sum(c['usage'].get('input_tokens', 0) for c in ok), sum(c['usage'].get('output_tokens', 0) for c in ok)
    log = meta.get('spend_log', [])
    L += ['', '## 비용', '',
          f'- 이번 결과의 요청 {len(ok)}건: 입력 {tin:,}토큰, 출력 {tout:,}토큰(무료). 입력 100만 토큰당 0.042달러로 {tin * USD_PER_TOKEN:.4f}달러.',
          f"- 실행 기록 {len(log)}회 합계(동작 확인 포함, 다시 쓴 응답은 한 번만 셈): 입력 {sum(s['input_tokens'] for s in log):,}토큰, "
          f"{sum(s['usd'] for s in log):.4f}달러.",
          '- 금액은 응답 usage.input_tokens와 문서 요금으로 셈했다. 콘솔 청구 화면과 맞춰 보지는 않았다.']
    if ok:
        big = max(ok, key=lambda c: c['usage'].get('input_tokens', 0))
        L += [f"- 요청 1건 응답 시간 가운데값 {statistics.median(c['seconds'] for c in ok):.2f}초(순차 호출). 가장 큰 요청 {big['req']} "
              f"입력 {big['usage']['input_tokens']:,}토큰(state {big['state_chars']:,}자).",
              f"- 응답 모델 이름: {', '.join(sorted({c['model'] for c in ok if c['model']}))}"]

    L += ['', '## 읽을 때 주의', '',
          '- R08 정답에 review(검토)와 audit(감사)는 없다. 레포와 받은 문서에 그런 보고서가 없다. 합의된 절차(AUP) 3문항은 모두 한국어 문서다.',
          '- R15 아니오 5문항은 다른 회사 문서(홍콩 주간 공시, 제3자 대사 문서, 국내 거래소 실사 3건)다. 레포 8개 코인 보고서의 R15 아니오는 없다.',
          '- 정답이 질문 문구에 기대는 문항: R15-02, R15-10(서명자가 모회사 임원. v1 문구 "officer or director of the issuer"를 글자대로 '
          '읽으면 아니오도 말이 된다. v2는 모회사 임원을 경영진으로 센다고 적었다), R11-19(옛 RLUSD 정의. 좁게 기준에서도 예로 볼 여지가 있다), '
          'T06(근거 문장에 interest가 없고 "not designed to create returns"만 있다. v1 문구에는 이 말이 없다).',
          '- 첫 시험과 입력이 다른 점: 문서 이름은 두 판 모두 state_label(문서 종류를 드러내지 않는 이름)이다. 첫 시험은 "reserve report as of"를 '
          '넣었다. 자산 v1은 첫 시험과 달리 Circle 줄에도 표 구역을 주지 않았다.',
          '- 같은 보고서에서 나온 문항이 여럿이다(예: USDG 2025-11은 R15-05와 R12-10). 문항 수보다 서로 다른 서식 수가 적다.',
          '- 자산 v1과 v2는 입력(표 구역, 각주)과 문구가 함께 바뀌어, 둘 가운데 무엇이 차이를 만들었는지는 이 시험으로 나눌 수 없다.',
          '- v2 문구에 적은 레포 관례가 직접 닿는 문항이 있다: 자산은 펀드 안 보유, 펀드 합계, 역레포 담보 줄(위 관례 표), R11은 유통량을 '
          '"liability for tokens issued"로 적는 보고서(' + ', '.join(x['id'] for x in y_items if x['rule'] == 'R11' and x['coin'] == 'USDT')
          + '), R15는 모회사 임원이나 이사회 서명(' + ', '.join(x['id'] for x in y_items if x['rule'] == 'R15' and '모회사' in
                                                       (x.get('check_note', '') + x.get('gold_note', '') + x.get('why_hard', ''))) + '). '
          '관례는 모든 문항에 같은 글로 붙는 일반 설명이고, 문항마다 다른 힌트는 넣지 않았다.']
    (OUT / 'summary.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'run':
        run(int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == '--limit' else None)
    elif cmd == 'report':
        old = load_results()
        write_summary(save(old['meta'], old['calls']))  # 채점을 다시 하고 요약을 쓴다
    else:
        sys.exit(__doc__)
