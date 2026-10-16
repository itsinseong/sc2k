"""모델 3종 시험 현황판 생성기(처음부터 다시 한 학습의 결과만 채운다). 탭: 결과, 할 순서, 자료. 사용: python3 -I make_status2.py"""
import html, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
FT = HERE.parent / '파인튜닝_2026-10-11'
sys.path.insert(0, str(FT / 'tools')); sys.path.insert(0, str(HERE))
import compare_eval as C
import make_status as MS
import make_data_overview as DO
CSS = (pathlib.Path.home() / '.claude/skills/doc-html/두리번.css').read_text(encoding='utf-8')
OUT = pathlib.Path.home() / 'HTML/미디어프로젝트_SC2K/모델시험/모델3종_시험현황.html'
E = html.escape


def table(head, body, cls='mx'):
    h = ''.join(f'<th{" class=\"c\"" if i else ""}>{E(x)}</th>' for i, x in enumerate(head))
    b = ''.join('<tr>' + ''.join(f'<td{" class=\"rw\"" if i == 0 else ""}>{x}</td>' for i, x in enumerate(r)) + '</tr>' for r in body)
    return f'<div class="tw"><table class="{cls}"><tr>{h}</tr>{b}</table></div>'



def baselines():
    v = {r['id']: r for r in C.jl(FT / 'sets/valid_v3.jsonl')}
    f = {r['id']: r for r in C.jl(FT / 'sets/final_v2.jsonl')}
    cap = json.load(open(FT / 'sets/eval_subsets.json'))['valid_capped']
    out = {}
    vc = {r['id']: r for r in C.jl(FT / 'sets/valid_c.jsonl')}
    vk = {r['id']: r for r in C.jl(FT / 'sets/valid_ko.jsonl')}
    fk = {r['id']: r for r in C.jl(FT / 'sets/final_ko.jsonl')}  # 한국어 검증과 최종 결과는 같은 results_*_ko 파일에 들어 있다(문항 id가 달라 다수결은 시험지별로 나뉜다)
    for key, fn, pre in (('jev', C.jev_majority, 'results_jev_'), ('decisions', C.dec_majority, 'results_decisions_')):
        mv, mf = fn(v), fn(f)
        mc = C.majority(vc, sorted(FT.glob(pre + 'c*.jsonl')))
        mk = C.majority(vk, sorted(FT.glob(pre + 'ko*.jsonl')))
        mfk = C.majority(fk, sorted(FT.glob(pre + 'ko*.jsonl')))
        out[key] = (sum(mv[i]['correct'] for i in v), sum(mv[i]['correct'] for i in cap), sum(mf[i]['correct'] for i in f),
                    sum(x['correct'] for x in mc.values()), f"{sum(x['correct'] for x in mk.values())}/{len(vk)}", f"{sum(x['correct'] for x in mfk.values())}/{len(fk)}")
    return out, len(v), len(cap), len(f)


MODELS = [('kanana', 'Kanana 1.5 8B', '카카오', '데스크톱 RTX 2070 SUPER, fp16'),
          ('gemma', 'Gemma 4 E4B', 'Google', 'RunPod RTX A5000, bf16'),
          ('gptoss', 'GPT-OSS-20B', 'OpenAI', 'RunPod RTX A6000, bf16')]
STAGE_KEYS = ['A', 'B', 'C', 'D', 'F']  # ①~⑤ 결과 폴더 이름: runs_restart/<model>-<key>/results/<model>-<key>__valid_v3.jsonl


def stage_score(model, key):
    """검증 372문항(valid_v3)에서 맞힌 개수. 결과가 없으면 None, 푸는 중이면 (맞힌 수, 푼 수)."""
    f = FT / 'runs_restart' / f'{model}-{key}' / 'results' / f'{model}-{key}__valid_v3.jsonl'
    if not f.exists():
        return None
    rs = [r for r in C.jl(f) if 'pred' in r]
    return sum(r['correct'] for r in rs), len(rs)
def set_score(model, key, s, ids=None):
    f = FT / 'runs_restart' / f'{model}-{key}' / 'results' / f'{model}-{key}__{s}.jsonl'
    rs = [r for r in C.jl(f) if 'pred' in r and (ids is None or r['id'] in ids)] if f.exists() else []
    return sum(r['correct'] for r in rs) if rs else None


def compare_chart(base, nv, nc):
    """시험지별 가로 막대: Jev, Decisions, 세 모델의 끝난 단계. 막대 시작은 정답률 70%."""
    cap = set(json.load(open(FT / 'sets/eval_subsets.json'))['valid_capped'])
    sets = [(f'영어 검증 {nv}', 'valid_v3', None, nv, 0), (f'검증 판단용 {nc}', 'valid_v3', cap, nc, 1), ('검증 보충 68', 'valid_c', None, 68, 3), ('한국어 검증 71', 'valid_ko', None, 71, 4)]
    out = ''
    for title, s, ids, n, bi in sets:
        rows = [('Jev', 'jev', int(str(base['jev'][bi]).split('/')[0])), ('Decisions', 'decisions', int(str(base['decisions'][bi]).split('/')[0]))]
        for k, nm, _, _ in MODELS:
            for st in ('A', 'B'):
                v = set_score(k, st, s, ids)
                if v is not None:
                    rows.append((f'{nm.split(" ")[0]} {"①②"[st == "B"]}' + (' *' if k == 'kanana' else ''), k, v))
        bars = ''.join(f'<span>{E(lb)}</span><div class="row"><div class="bar" style="width:{max(0, v / n - .7) / .3 * 85:.1f}%;background:{MS.BRAND[k]}"></div><span class="val">{v}</span></div>' for lb, k, v in rows)
        out += f'<div><h4>{title}</h4><div class="bars">{bars}</div></div>'
    return (f'<div class="cmp">{out}</div><p class="cav">막대는 정답률 70%에서 시작한다. ①은 A(v3), ②는 B(v3 + 합성 ①). '
            '* Kanana는 데스크톱에서 채점한 값이라 참고용이며, A6000에서 다시 채점할 예정이다.</p>')


STEPS = ['① A(v3)', '② B(v3 + 합성 ①)', '③ 합성 추가', '④ 실제 전부 + 합성', '⑤ 최종 시험']


TODO = [
    ('시험지 준비', [
        ('me', '한국어 시험지 나누기 확인', '확정: 검증은 빗썸, NHN페이코 문서 20건. 최종은 나머지 20곳, 회사당 감사보고서 3건 + 공시 3건(68건)', 'done'),
        ('cl', '한국어 문항 만들기', 'Sonnet 첫 라벨, Opus 대조, 두 독자 일치분만. 검증 71문항, 최종 275문항 확정', 'done'),
        ('cl', '영어 최종 자산 문항 점검', 'keep 104, relabel 0, drop 34. 최종 553 → 519문항으로 고정', 'done'),
        ('cl', 'Jev, Decisions 호출 조건 점검', '지난 925문항과 같은 코드, 같은 질문 글', 'done'),
        ('me', 'Jev, Decisions 추가 호출 허락', '허락함(10/15)', 'done'),
        ('cl', 'Jev, Decisions 추가로 풀기', '검증 보충 68(Jev 62, Decisions 62), 한국어 검증 71(둘 다 71), 한국어 최종 275(Jev 242, Decisions 267)', 'done'),
        ('me', '통과 기준, 합성 상한 정하기', '확정(10/15): Jev와 3%p 이내, 확신 높은 오답 수 Jev 이하, 합성은 ③까지', 'done')]),
    ('학습 준비', [
        ('me', 'RunPod 준비', '결제(잔액 15달러), SSH 키 등록, MCP 로그인', 'done'),
        ('cl', '학습 코드 정리', 'kit/ft_core.py(정밀도 설정, fp16 GradScaler), run_stage.py, pod_run.sh(20시간 뒤 자동 멈춤)', 'done'),
        ('cl', 'GPU 정하기', 'GPT-OSS는 RTX A6000(48GB), Gemma는 RTX A5000(24GB), Kanana는 데스크톱', 'done')]),
    ('학습과 판단', [
        ('cl', '① A 학습: 실제 v3', 'GPT-OSS(A6000)부터 학습 중. Gemma(A5000)는 재고가 나면, Kanana는 데스크톱 꾸러미로', 'now'),
        ('cl', '② B 학습: v3 + 합성 ①', '같은 설정, 자료만 바꿈'),
        ('cl', '검증 세트 채점', '세 모델 모두 RunPod 한 곳, 같은 코드. 영어 372 + 보충 68, 한국어 2곳'),
        ('me', '결과 확인', '편향(예→아니오, 아니오→예 오답)과 통과 기준'),
        ('dec', '미달이면 ③ 합성 추가 → 다시 학습', '합성 상한까지 반복. 매번 바탕 모델에서 새로 학습'),
        ('cl', '④ 실제 전부 + 합성으로 학습', '학습 자료 279건 + 후보 208건, 바탕 모델에서 새로 시작'),
        ('dec', '나쁘면 합성 더 넣어 ④ 다시', '검증 세트로만 판단. 최종 시험지는 열지 않음')]),
    ('마무리', [
        ('me', '⑤ 최종 시험 실행 허락', '최종 시험지는 이때 처음 엶'),
        ('cl', '최종 시험 한 번', '영어 519, 한국어 20곳. 세 모델 같은 곳, 같은 코드. 결과로 모델을 고르지 않음'),
        ('both', '결과 정리', '은행이 모델 하나만 골라도 쓸 수 있는지 모델별로 기록. Kanana는 fp16 학습으로 표기')]),
]
CHIPS = {'me': '<span class="wc me">인성</span>', 'cl': '<span class="wc cl">Claude</span>', 'both': '<span class="wc me">인성</span><span class="wc cl">Claude</span>'}
TODO_CSS = """.cmp{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px 40px}.cmp h4{margin:0 0 8px;font-size:14px}
nav.side .tf{margin:24px 0 0;font-size:13px}nav.side .tf>b{margin:0 0 8px 12px}
nav.side .tf li{position:relative;list-style:none;margin:0;line-height:1.5;display:flex;justify-content:space-between;gap:6px;padding:5px 12px;border-left:2px solid var(--line);cursor:default}
nav.side .tf ul{margin:0;padding:0}nav.side .tf li:hover{border-left-color:var(--accent)}nav.side .tf li i{font-style:normal;color:var(--ink-3)}
nav.side .tf li.on b{color:#1d5fb0}nav.side .tf li b{font-weight:600;font-size:12.5px}
nav.side .tf .tip{display:none;position:absolute;left:calc(100% + 10px);top:0;width:250px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:9px 11px;box-shadow:0 4px 14px rgba(0,0,0,.08);color:var(--ink);font-size:12.5px;line-height:1.5;z-index:5}
nav.side .tf li:hover .tip{display:block}
.layout.l3{grid-template-columns:170px minmax(0,1fr) 270px;gap:32px;max-width:none;padding:0 32px 88px}
aside.todo{position:sticky;top:0;align-self:start;padding:44px 0 24px;font-size:13px}
aside.todo>b{display:block;font-size:15px;color:var(--ink);margin:0 0 6px}
aside.todo .lg{font-size:12px;color:var(--ink-3);margin:0 0 12px}
aside.todo ol{list-style:none;margin:0;padding:0}
aside.todo li.gh{font-size:12px;font-weight:700;color:var(--ink-3);margin:12px 0 6px}
aside.todo li.st{position:relative;border:1px solid var(--line);border-radius:8px;padding:7px 10px;background:#fff;line-height:1.4;cursor:default;margin-bottom:16px}
aside.todo li.st::after{content:"";position:absolute;left:50%;bottom:-15px;height:13px;border-left:2px solid #b5b5b0}
aside.todo li.st::before{content:"";position:absolute;left:calc(50% - 4px);bottom:-16px;border:4px solid transparent;border-top:5px solid #b5b5b0;border-bottom:0}
aside.todo li.st.last::after,aside.todo li.st.last::before{display:none}
aside.todo li.st:hover{border-color:var(--accent)}
aside.todo li.st.now{border:2px solid var(--accent);background:var(--tint-2)}
aside.todo li.st.done{opacity:.45;text-decoration:line-through}aside.todo li.st.done .tip{text-decoration:none}aside.todo li.st.part .nw{float:right;font-size:11px;font-weight:700;color:#0b7a57}
aside.todo li.st.now .nw{float:right;font-size:11px;font-weight:700;color:var(--accent)}
aside.todo li.dec{position:relative;font-size:12px;color:var(--ink-2);border:1px dashed #9a9a95;border-radius:999px;padding:3px 10px;margin:0 0 16px 18px;cursor:default}
aside.todo li.dec::before{content:"↳";position:absolute;left:-16px;top:2px;color:#9a9a95}
.wc{display:inline-block;font-size:10.5px;font-weight:700;border-radius:4px;padding:0 5px;margin-right:6px;vertical-align:1px}.wc.me{background:#111;color:#fff}.wc.cl{background:#fbe6dc;color:#b4532a}
aside.todo .tip{display:none;position:absolute;right:calc(100% + 12px);top:0;width:260px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px 12px;box-shadow:0 4px 14px rgba(0,0,0,.08);color:var(--ink);font-weight:400;font-size:13px;z-index:5}
aside.todo li:hover .tip,aside.todo li:focus .tip{display:block}aside.todo li:focus{outline:none}
@media (max-width:1280px){.layout.l3{grid-template-columns:170px minmax(0,1fr)}aside.todo{grid-column:2;position:static}aside.todo .tip{position:static;width:auto;margin-top:6px;box-shadow:none}}
@media (max-width:900px){.layout.l3{grid-template-columns:1fr}aside.todo{grid-column:auto}}"""


def files_side():
    n = lambda f: len(C.jl(FT / f)) if (FT / f).exists() else 0
    v3ids = {r['id'] for r in C.jl(FT / 'sets/train_v3.jsonl')}
    new4 = len({r['id'] for r in C.jl(FT / 'sets/train_v4.jsonl')} - v3ids)
    rows = [('v2', n('sets/train_v2.jsonl'), True, '실제 문서. 자산 줄, 보고서 문항, 약관'),
            ('v3', n('sets/train_v3.jsonl'), True, 'v2와 같은 문서. R11 넓게 아니오 12개를 3번씩 반복해 24행 추가(새 문서 없음). ①에서 학습'),
            ('v4', n('sets/train_v4.jsonl'), False, f'v3 고유 1,025 + 새 {new4}문항(다른 달 보고서, 옛 검증 문항). 예 쪽 쏠림'),
            ('긴 문서 조각', n('build/long_chunks_candidate_cap2.jsonl'), False, '12,000자 넘는 학습 문서 17건을 조각냄'),
            ('합성 ①', n('sets/syn_v1.jsonl'), True, '실제 학습 문서에서 한 군데만 고친 문서. Opus 확인 통과분. ②에서 v3와 함께 학습')]
    lis = ''.join(f'<li{" class=\"on\"" if on else ""}><b>{E(nm)}</b><i>{c:,}{"" if on else ", 안 넣음"}</i><div class="tip">{E(tip)}</div></li>' for nm, c, on, tip in rows)
    return f'<div class="tf"><b>학습 자료</b><ul>{lis}</ul></div>'


def todo_side():
    flat = [(g, it) for g, items in TODO for it in items]
    lis, prev, n = '', None, 0
    steps = [i for i, (_, it) in enumerate(flat) if it[0] != 'dec']
    for i, (grp, (who, title, tip, *st)) in enumerate(flat):
        st = st[0] if st else ''
        if grp != prev:
            lis += f'<li class="gh">{E(grp)}</li>'; prev = grp
        if who == 'dec':
            lis += f'<li class="dec" tabindex="0">{E(title)}<div class="tip">{E(tip)}</div></li>'
            continue
        n += 1
        cls = 'st' + (f' {st}' if st else '') + (' last' if i == steps[-1] else '')
        badge = {'now': '지금', 'part': '일부 끝'}.get(st)
        lis += (f'<li class="{cls}" tabindex="0">{f'<span class="nw">{badge}</span>' if badge else ''}{CHIPS[who]}{E(title)}'
                f'<div class="tip">{E(tip)}</div></li>')
    return (f'<aside class="todo"><b>할 순서</b><p class="lg">{CHIPS["me"]}직접 &nbsp;{CHIPS["cl"]}맡김 &nbsp; 올리면 자세히</p><ol>{lis}</ol></aside>')


def vff_compare():
    """영어 검증(valid_v3) 372문항: 규칙 없는 기준선(처음 5회 다수결)과 질문 글 앞에 판정 지침을 붙인 결과(있는 회차 다수결). Jev, Decisions 각각."""
    v = {r['id']: r for r in C.jl(FT / 'sets/valid_v3.jsonl')}
    out = {}
    for key, base_files, pat in (
            ('jev', [FT / 'results_jev_eval.jsonl'] + [FT / f'results_jev_eval_r{i}.jsonl' for i in range(2, 6)], 'results_jev_rules*.jsonl'),
            ('dec', [FT / 'results_openai_decisions.jsonl'] + [FT / f'results_openai_decisions_r{i}.jsonl' for i in range(2, 6)], 'results_decisions_rules*.jsonl')):
        rf = [f for f in sorted(FT.glob(pat)) if f.stat().st_size and sum(1 for _ in open(f)) >= len(v)]
        if not rf:
            out[key] = None
            continue
        b, r = C.majority(v, base_files), C.majority(v, rf)
        by = {}
        for q, row in v.items():
            t = row['task']
            d = by.setdefault(t, [0, 0, 0, 0, 0])  # 문항, 기준 맞음, 규칙 맞음, 새로 맞힘, 새로 틀림
            d[0] += 1; d[1] += b[q]['correct']; d[2] += r[q]['correct']
            d[3] += (not b[q]['correct']) and r[q]['correct']; d[4] += b[q]['correct'] and not r[q]['correct']
        out[key] = dict(runs=len(rf), base=sum(x['correct'] for x in b.values()), rules=sum(x['correct'] for x in r.values()), n=len(v), by=by)
    return out


def vff_pane():
    cmp_ = vff_compare()
    TN = {'asset': '자산', 'R08': 'R08 감사 종류', 'R11_broad': 'R11 넓게', 'R11_narrow': 'R11 좁게', 'R12': 'R12', 'R14': 'R14', 'R15': 'R15'}
    names = {'jev': 'Jev', 'dec': 'Decisions API'}
    tiles = ''
    for k in ('jev', 'dec'):
        c = cmp_[k]
        if c:
            d = c['rules'] - c['base']
            tiles += (f'<div class="tile"><div class="v">{c["rules"]}<small> / {c["n"]}</small></div><div class="l">{names[k]}, 판정 지침을 붙였을 때</div>'
                      f'<div class="s">붙이기 전 {c["base"]}, 차이 {d:+d}문항(각 {c["runs"]}회 다수결)</div></div>')
        else:
            tiles += f'<div class="tile"><div class="v">-</div><div class="l">{names[k]}, 판정 지침을 붙였을 때</div><div class="s">푸는 중</div></div>'
    rows = ''
    if cmp_['jev'] and cmp_['dec']:
        for t, lab in TN.items():
            j, d = cmp_['jev']['by'].get(t), cmp_['dec']['by'].get(t)
            if not j:
                continue
            cell = lambda x, i: f'{x[1]} → {x[2]}<small> (+{x[3]}, -{x[4]})</small>'
            rows += f'<tr><td class="rw">{lab}</td><td class="c">{j[0]}</td><td class="c">{cell(j, 0)}</td><td class="c">{cell(d, 0)}</td></tr>'
    table = (f'<div class="tw"><table class="mx"><tr><th>과제</th><th class="c">문항</th><th class="c">Jev: 지침 전 → 후</th><th class="c">Decisions: 지침 전 → 후</th></tr>{rows}</table></div>'
             '<p class="cav">괄호의 +는 지침을 붙여 새로 맞힌 문항, -는 새로 틀린 문항입니다.</p>') if rows else ''
    import rules_prefix as RPX
    sample = E(RPX.prefix('asset')).replace('\n', '<br>')
    return f'''<div data-pane="vff" hidden>
<section id="v1"><h2>판정 지침 시험</h2>
<p class="lede">질문 글 앞에 판정 지침(공통 머리말과 과제별 관례집 규칙)을 붙이면 점수가 오르는지, 학습 없이 Jev와 Decisions API로 먼저 재 봅니다. 영어 검증 372문항을 같은 문항, 같은 선택지로 풀고, 지침 앞뒤를 같은 횟수의 다수결로 비교합니다.</p>
<div class="tiles" style="grid-template-columns:repeat(2,1fr)">{tiles}</div>
{table}
</section>
<section id="v2"><h2>붙인 지침</h2>
<p>공통 머리말은 VFF의 verification 절(문서에 적힌 것만 근거로, 적히지 않은 것은 없는 것으로)을 판정용으로 바꾼 것이고, 규칙은 관례집 24개를 과제별로 나눠 해당 과제 것만 붙였습니다. 자산 문항에 붙는 글은 아래와 같습니다.</p>
<div class="warn" style="font-family:ui-monospace,Menlo,monospace;font-size:12px;line-height:1.6">{sample}</div>
</section>
<section id="v3"><h2>읽는 법</h2>
<div class="tw"><table class="mx">
<tr><th>한계</th><th>내용</th></tr>
<tr><td class="rw">정답 라벨</td><td>검증 세트 라벨은 규칙 일부(ASSET-7 등)가 정해지기 전에 두 독자가 만든 것이라, 규칙대로 답하면 오답으로 세는 문항이 있을 수 있습니다. 표의 -가 이런 문항일 수 있습니다.</td></tr>
<tr><td class="rw">우리 모델과 다름</td><td>Jev와 Decisions는 질문 글을 읽는 방식이 우리 모델과 다릅니다. 여기서 오르거나 오르지 않았다고 해서 학습한 모델도 같다고 말할 수 없습니다.</td></tr>
<tr><td class="rw">한쪽으로 미는 방향</td><td>규칙이 정답과 반대 방향으로 답을 밀 수 있습니다. 예를 들어 정의로 인정하는 경우를 넓게 적으면 "아니오"가 정답인 문항을 "예"로 답하게 됩니다. 과제별로 붙일지 따로 정해야 합니다.</td></tr>
<tr><td class="rw">한국어 시험지</td><td>ASSET-7은 한국어 검증 문항에서 두 독자가 갈린 것을 보고 만들었고, 한국어 최종 라벨도 이 규칙으로 만들었습니다. 한국어에서 지침을 붙인 점수가 오르는 것은 규칙을 배운 결과이지 판정 능력의 근거가 아닙니다. 판정 능력은 영어 최종(발행사가 규칙 작성에 쓰이지 않음)으로 봅니다.</td></tr>
<tr><td class="rw">흔들림</td><td>지침 전은 5회, 지침 후는 끝까지 푼 회차(Jev 4회, Decisions 3회)의 다수결입니다. 나머지 회차는 특정 문항에서 서버가 연결을 끊어 멈췄습니다. 같은 문항도 회차마다 답이 흔들려서 몇 문항 차이는 노이즈일 수 있습니다.</td></tr>
<tr><td class="rw">비교 기준</td><td>은행이 실제로 쓸 Jev는 우리 규칙을 받지 않은 상태라, 지침을 붙인 Jev는 "Jev만큼"의 기준선이 아닙니다.</td></tr>
</table></div>
</section>
<section id="v4"><h2>글 모델 지침</h2>
<p>은행 서버 글 모델에는 VFF 구조의 시스템 프롬프트를 넣습니다(전체 구조 그림 참고). 6개 절은 글쓰기(결론 먼저), 출처(문장 옆에, 지어내지 않음), 정직성(0.95 미만은 "확인 필요"), 빈칸(숫자는 비우고 코드가 채움), 형식(산출물 4종 틀), 금지(상투어와 과장)입니다. 효과는 근거 검사의 첫 통과율, 다시 쓴 횟수, 사람에게 넘어간 비율로 잽니다.</p>
</section>
</div>'''


# 세 모델의 학습 장소. started가 있으면 그때부터 요금을 셈(RunPod get-pod의 startedAt을 한국 시간으로). Pod를 지우면 ended를 적는다.
RUNS = [
    dict(model='kanana', where='데스크톱 RTX 2070 SUPER(fp16)', price=0, started=None, ended=None,
         note='데스크톱 꾸러미(kanana_restart.zip)로 돌리고, 결과 zip을 받아 runs_restart에 넣음'),
    dict(model='gemma', where='RunPod RTX A5000(시큐어, bf16)', price=0.27, started=None, ended=None,
         note='A5000 재고가 나면 시작'),
    dict(model='gptoss', where='RunPod RTX A6000(시큐어, EU-SE-1, bf16)', price=0.59, started='2026-10-15 18:41', ended='2026-10-16 02:25',
         note='Pod wpzg91y8t1my9j. 결과를 받아 지문을 대조한 뒤 지움(요금 끝)'),
]

def stage_progress(model, key):
    """runs_restart/<tag>/logs에서 학습 단계(step a/b, 걸린 초)와 끝남 여부를 읽는다."""
    import re
    d = FT / 'runs_restart' / f'{model}-{key}' / 'logs'
    if not d.exists():
        return None
    st = d / f'steps_{model}-{key}.log'
    m = re.findall(r'step (\d+)/(\d+) loss ([\d.]+) (\d+)s', st.read_text()) if st.exists() else []
    lg = (d / f'{model}-{key}.log').read_text(encoding='utf-8') if (d / f'{model}-{key}.log').exists() else ''
    ev = re.findall(r'eval(?:_long)? (\d+)/(\d+)', lg)
    return dict(step=int(m[-1][0]) if m else 0, total=int(m[-1][1]) if m else 0, loss=float(m[-1][2]) if m else None,
                secs=int(m[-1][3]) if m else 0, done=(d / f'{model}-{key}.DONE').exists(), evaluating='adapter saved' in lg,
                err=' ERR ' in lg, eval_last=ev[-1] if ev else None)


def progress_section():
    import datetime as dt
    now = dt.datetime.now()
    names = {m[0]: m[1] for m in MODELS}
    labs = {'A': '① A(v3)', 'B': '② B(v3 + 합성 ①)'}
    rows = ''
    for r in RUNS:
        col = MS.BRAND[r['model']]
        logo = MS.logo(r['model'])
        for i, k in enumerate(['A', 'B']):
            g = stage_progress(r['model'], k) or {}
            if g.get('err'):
                state, pct = '<b style="color:#d4452b">오류로 멈춤</b>', 0
            elif g.get('done'):
                state, pct = '끝(학습과 검증 풀이)', 100
            elif g.get('evaluating'):
                e = g.get('eval_last')
                state, pct = '검증 풀이 중' + (f' {e[0]}/{e[1]}' if e else ''), 100
            elif g.get('total'):
                left = (g['total'] - g['step']) * g['secs'] / max(1, g['step'])
                state, pct = f'학습 {g["step"]}/{g["total"]}단계, 손실 {g["loss"]:.3f}, 남은 학습 약 {left / 3600:.1f}시간', 100 * g['step'] / g['total']
            else:
                state, pct = '<span class="mut">대기</span>', 0
            who = f'<span class="pm">{logo}<b>{names[r["model"]]}</b></span>' if i == 0 else ''
            rows += (f'<tr><td class="rw">{who}</td><td>{labs[k]}</td>'
                     f'<td><div class="pbar" style="background:color-mix(in srgb,{col} 16%,#fff)"><i style="width:{pct:.0f}%;background:{col}"></i></div></td><td>{state}</td></tr>')
        cost = ''
        if r['started']:
            t0 = dt.datetime.strptime(r['started'], '%Y-%m-%d %H:%M')
            t1 = dt.datetime.strptime(r['ended'], '%Y-%m-%d %H:%M') if r['ended'] else now
            hrs = (t1 - t0).total_seconds() / 3600
            cost = f', {r["started"]} 시작, {"쓴 시간" if r["ended"] else "지금까지"} 약 {hrs:.1f}시간, GPU 요금 약 {hrs * r["price"]:.2f}달러'
        price = f'시간당 {r["price"]}달러' if r['price'] else '비용 0'
        rows += f'<tr class="pnote"><td></td><td colspan="3" class="mut">{r["where"]}, {price}{cost}. {r["note"]}</td></tr>'
    return (f'<section id="s0"><h2>지금 도는 학습</h2><p class="cav">10분마다 Pod에서 진행 기록을 받아 갱신합니다. 마지막 갱신 {now:%H:%M}.</p>'
            f'<div class="tw"><table class="mx"><tr><th>모델</th><th>단계</th><th>진행</th><th>상태</th></tr>{rows}</table></div></section>')


def build():
    base, nv, nc, nf = baselines()
    jv = base['jev'][0]
    tiles = ''
    for key, nm, co, dev in MODELS:
        sc = [stage_score(key, k) for k in STAGE_KEYS]
        done = [(i, x) for i, x in enumerate(sc) if x and x[1] >= nv]
        def val(x, k):
            if x:
                return str(x[0]) if x[1] >= nv else f'검증 {x[1]}/{nv}'
            g = stage_progress(key, k)
            return f'학습 {g["step"]}/{g["total"]}' if g and g.get('total') else '-'
        lis = ''.join(f'<li class="{"done" if x and x[1] >= nv else "now" if (x or stage_progress(key, k)) else "wait"}"><span>{E(st)}</span><b>{val(x, k)}</b></li>' for st, x, k in zip(STEPS, sc, STAGE_KEYS))
        if done:
            i, (cor, _) = done[-1]
            mv, mg = f'{cor}개', f'{STEPS[i]} 기준, Jev보다 {abs(jv - cor)}개 {"적음" if cor < jv else "많음"}'
            nxt = STEPS[i + 1] if i + 1 < len(STEPS) else ''
            mst = f'{STEPS[i]}까지 끝' + (f', 다음: {nxt}' if nxt else '')
        else:
            g = stage_progress(key, 'A')
            mv, mg, mst = '-', E(dev), ('① A 학습 중' if g else '학습 전, 다음: ① A 학습(v3)')
        tiles += (f'<div class="mc" style="--b:{MS.BRAND[key]}"><div class="mh">{MS.logo(key)}<b>{nm}</b><span>{co}</span></div>'
                  f'<div class="mv">{mv}</div><div class="mg">{mg}</div>'
                  f'<div class="mst">{mst}</div><ol class="ms">{lis}</ol></div>')
    for key, nm, co, cls, model in (('decisions', 'Decisions API', 'OpenAI', 'mc', 'gpt-6-luna'), ('jev', 'Jev', 'TypeSafe AI', 'mc goal', 'jev-1.13.0')):
        a, c, f, vc, vk, fk = base[key]
        mg = '이만큼이 목표' if key == 'jev' else f'Jev보다 {abs(jv - a)}개 {"적음" if a < jv else "많음"}'
        tiles += (f'<div class="{cls}" style="--b:{MS.BRAND[key]}"><div class="mh">{MS.logo(key)}<b>{nm}</b><span>{co}</span></div>'
                  f'<div class="mv">{a}개</div><div class="mg">{mg}</div>'
                  f'<div class="mst">학습하지 않음(외부 서비스, 비교 기준)</div><ol class="ms">'
                  f'<li class="done"><span>검증 판단용 {nc}</span><b>{c}</b></li><li class="done"><span>최종 {nf}(영어)</span><b>{f}</b></li>'
                  f'<li class="done"><span>모델</span><b>{model}</b></li>'
                  f'<li class="done"><span>검증 보충 68</span><b>{vc}</b></li><li class="done"><span>한국어 검증 71</span><b>{vk.split("/")[0]}</b></li><li class="done"><span>한국어 최종 275</span><b>{fk.split("/")[0]}</b></li>'
                  f'<li class="done"><span>바뀐 영어 최종 문항</span><b>없음</b></li></ol></div>')
    t_board = table(['누가', f'검증 {nv}', f'검증 판단용 {nc}', f'최종 {nf}(영어)', '검증 보충 68', '한국어 검증', '한국어 최종'],
                    [(n, f'{base[k][0]}', f'{base[k][1]}', f'{base[k][2]}', f'{base[k][3]}', base[k][4], base[k][5])
                     for k, n in (('jev', 'Jev(10회 다수결)'), ('decisions', 'Decisions API(10회 다수결)'))])
    t_more = table(['할 일', '문항', '언제', '상태'], [
        ('호출 조건 점검', '-', '10/15', '끝. 같은 코드, 같은 질문 글. 결과 파일만 따로 둠'),
        ('검증 보충 풀기', '68 × 10회', '10/15', '끝. Jev 62, Decisions 62'),
        ('한국어 검증 풀기', '71 × 10회', '10/15', '끝. Jev 71/71, Decisions 71/71'),
        ('한국어 최종 풀기', '275 × 10회', '10/15', '끝. Jev 242, Decisions 267'),
        ('바뀐 영어 최종 문항 다시 풀기', '0', '10/15', '정답이 바뀐 문항이 없어 다시 풀 것 없음. 빠진 34문항은 기존 결과에서 뺌'),
    ])
    def cell(x):
        if not x:
            return '<span class="mut">-</span>'
        return f'{x[0]}' if x[1] >= nv else f'<span class="mut">푸는 중 {x[1]}/{nv}</span>'
    t_ours = table(['모델(장비, 정밀도)'] + STEPS, [(f'<b>{n}</b><br><small>{d}</small>', *[cell(stage_score(k, s)) for s in STAGE_KEYS]) for k, n, _, d in MODELS])
    t_sets = table(['시험지', '문항', '회사', '상태', '쓰는 때'], [
        ('영어 검증', '372(판단용 245)', '13', '그대로 씀', '② ③ ④ 판단'),
        ('검증 보충', '68', '3', '더함. Jev, Decisions 풀었음', '② ③ ④ 판단'),
        ('한국어 검증', '71', '2(빗썸, NHN페이코)', '확정. 두 독자 일치 77문항에서 ASSET-7과 맞지 않는 6문항 뺌', '② ③ ④ 판단'),
        ('영어 최종', '519', '26', '고정. 553문항에서 모델이 보는 정보만으로 풀 수 없는 자산 33문항과 중복 1문항을 뺌', '⑤ 한 번'),
        ('한국어 최종', '275', '20', '확정. 회사당 감사보고서 3건 + 공시 3건(문서 68건), 두 독자 일치 275/278', '⑤ 한 번')])
    t_rule = table(['규칙', '내용'], [
        ('처음부터 다시', '이전 학습 결과는 탐색 기록으로만 둔다. 세 모델 모두 바탕 모델에서 ①부터 새로 학습한다.'),
        ('같은 조건', '한 모델 안에서는 장비, 정밀도, 설정을 바꾸지 않는다. 단계마다 자료만 바뀐다.'),
        ('모델 사이', '장비와 정밀도는 달라도 된다. 결과표에 적는다(Kanana만 fp16).'),
        ('채점', '세 모델 모두 같은 곳에서 같은 코드로 채점한다.'),
        ('Jev, Decisions API', '비교 기준으로만 쓴다. 학습 라벨이나 합성의 정답으로 쓰지 않는다.'),
        ('통과 기준', '검증 세트에서 Jev와 3%p 이내, 확신 0.95 이상 오답 수가 Jev 이하. 합성 추가는 ③까지(10/15 확정).'),
        ('최종 시험', '한 번만 푼다. 결과로 모델을 고르지 않는다.')])
    data = DO.sections()
    dnames = ['흐름', '수집한 실제 문서', '학습 자료', '합성 데이터 계획', '학습 환경']
    for n, t in enumerate(dnames, 1):
        data = data.replace(f'<section><h2>{n}. ', f'<section id="d{n}"><h2>{n + 4}. ', 1)
    nav = ('<a href="#s0">지금 도는 학습</a><a href="#s1">1. 결과</a><a href="#s2">2. Jev, Decisions 추가</a><a href="#s3">3. 시험지</a><a href="#s4">4. 규칙</a>'
           '<b class="nh">자료 설명</b>' + ''.join(f'<a href="#d{n}">{n + 4}. {t}</a>' for n, t in enumerate(dnames, 1)))
    CH = MS.CHIP
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="120"><title>모델 3종 시험 현황</title>
<style>{CSS}
{MS.STYLE}
.mut{{color:#85857f}}table.mx td.rw{{width:24%}}table.mx td{{white-space:normal}}table.mx td.c{{white-space:nowrap}}{DO.EXTRA_CSS}
{TODO_CSS}
.pbar{{height:10px;background:#eceae6;border-radius:5px;overflow:hidden;min-width:160px}}.pbar i{{display:block;height:100%;background:var(--accent)}}.pm{{display:inline-flex;align-items:center;gap:8px}}.pm img{{width:22px;height:22px;border-radius:5px;object-fit:contain}}tr.pnote td{{font-size:12.5px;padding-top:2px}}
.tabs2{{display:flex;gap:8px;margin:22px 0 4px}}.tabs2 button{{font:inherit;font-size:15px;font-weight:600;padding:8px 18px;border-radius:999px;border:1.5px solid var(--line);background:#fff;color:var(--ink-2);cursor:pointer}}.tabs2 button.on{{background:#111;border-color:#111;color:#fff}}.tabs2 button.vffb{{background:#fbe6dc;border-color:#e8743b;color:#b4532a}}.tabs2 button.vffb.on{{background:#e8743b;border-color:#e8743b;color:#fff}}.tile .v small{{font-size:14px;font-weight:500;color:var(--ink-3)}}td small{{color:var(--ink-3);font-size:12px}}</style></head><body><div class="layout l3">
<nav class="side"><b>목차</b>{nav}{files_side()}</nav>
<main>
<header class="mast"><p class="eyebrow">SC2K 판정 블록 바탕 모델 시험</p>
<h1>모델 3종 시험 현황</h1>
<p class="lede">은행 내부망에서 준비금 보고서를 판정할 AI 모델 3개를 같은 순서, 같은 자료, 같은 시험지로 처음부터 다시 학습한다. 목표는 외부 서비스 Jev만큼 맞히는 것이다.</p></header>
<div class="tabs2"><button data-tab="main" class="on">시험 현황</button><button data-tab="vff" class="vffb">VFF 적용</button></div>
{vff_pane()}
<div data-pane="main">
<p class="legend">학습 자료 구분 &nbsp;{CH['real']} 공개 문서로 만든 실제 자료 &nbsp;{CH['syn']} 실제 학습 문서를 한 군데만 고쳐 만든 자료(학습에만 씀) &nbsp;{CH['none']} 외부 서비스. 시험지는 모두 실제 문서</p>
<h3 class="tth">모델별 상태(검증 {nv}문항에서 맞힌 개수)</h3>
<div class="mcards">{tiles}</div>
{progress_section()}
<section id="s1"><h2>1. 결과</h2><h3>비교</h3>{compare_chart(base, nv, nc)}<h3>우리 모델</h3>{t_ours}
<p class="cav">단계가 끝나면 검증 세트에서 맞힌 개수를 채운다. ⑤는 최종 시험 한 번의 결과만 넣는다.</p>
<h3>기준선</h3>{t_board}
<p class="cav">Jev, Decisions API는 영어 검증, 최종, 검증 보충을 10회씩 풀었다.</p></section>
<section id="s2"><h2>2. Jev, Decisions API가 더 풀 것</h2>{t_more}</section>
<section id="s3"><h2>3. 시험지</h2>{t_sets}</section>
<section id="s4"><h2>4. 규칙</h2>{t_rule}</section>
{data}
</div>
</main>
{todo_side()}
</div>
<script>
(function () {{
  var K = 'sc2k-tab2';
  function tab(t) {{
    document.querySelectorAll('[data-pane]').forEach(function (d) {{ d.hidden = d.dataset.pane !== t; }});
    document.querySelectorAll('.tabs2 button').forEach(function (b) {{ b.classList.toggle('on', b.dataset.tab === t); }});
    document.querySelector('nav.side').style.visibility = t === 'vff' ? 'hidden' : '';
    try {{ sessionStorage.setItem(K, t); }} catch (e) {{}}
  }}
  document.querySelectorAll('.tabs2 button').forEach(function (b) {{ b.addEventListener('click', function () {{ tab(b.dataset.tab); }}); }});
  var t0 = null; try {{ t0 = sessionStorage.getItem(K); }} catch (e) {{}}
  if (t0 === 'vff') tab('vff');
  var links = document.querySelectorAll('nav.side a');
  var io = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{ if (e.isIntersecting) links.forEach(function (a) {{ a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); }}); }});
  }}, {{rootMargin: '-20% 0px -70% 0px'}});
  document.querySelectorAll('section[id]').forEach(function (s) {{ io.observe(s); }});
}})();
</script>
</body></html>'''


def main():
    OUT.write_text(build(), encoding='utf-8')
    print(OUT)


if __name__ == '__main__':
    main()
