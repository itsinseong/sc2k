"""모델 3종 시험 현황 html 생성기.
results_gemma4e4b.jsonl, results_kanana.jsonl, results_gptoss20b(.partial).jsonl, Jev 2차(v2)와 1차 결과를 읽어 한 장으로 쓴다.
사용: python3 make_status.py [--status <Colab 상태 파일>] [--out <html 경로>]
"""
import collections, html, json, pathlib, re, sys, time

HERE = pathlib.Path(__file__).resolve().parent
RESEARCH = HERE.parent
CSS = pathlib.Path.home() / '.claude/skills/doc-html/두리번.css'
OUT = pathlib.Path.home() / 'HTML/미디어프로젝트_SC2K/모델시험/모델3종_이전기록.html'
TOTAL = 277
SETS = {'S1': '첫 시험', 'S2': '어려운 시험', 'S3': '더 어려운 시험'}
MODELS = [  # 키, 표시 이름, 회사와 크기, 실행 장비, 불러오기, 답 읽는 방법
    ('gemma', 'Gemma 4 E4B', 'Google, 8.0B', '집 PC RTX 2070 Super 8GB', '4비트(NF4), 임베딩은 CPU', '선택지 글자 확률'),
    ('kanana', 'Kanana 1.5 8B', '카카오, 8.0B', '집 PC RTX 2070 Super 8GB', '4비트(NF4)', '선택지 글자 확률'),
    ('gptoss', 'GPT-OSS-20B', 'OpenAI, 20.9B(MoE)', 'Colab 무료 T4 16GB', 'MXFP4(Unsloth)', '짧은 추론(low) 뒤 답 칸 첫 글자 확률'),
]
E = html.escape
CHIP = {'real': '<span class="kind real">실제</span>', 'syn': '<span class="kind syn">합성</span>', 'none': '<span class="kind none">학습 안 함</span>'}
SYN_STRIPE = 'repeating-linear-gradient(45deg,#FFCD00 0 7px,#8a63d2 7px 11px)'  # 노랑(Kanana) + 보라(합성)


def data_chips(label):
    """판 이름으로 학습 자료 종류 칩: '합성'이 들어 있으면 실제+합성, 학습 전은 칩 없음, 그 밖의 학습은 실제."""
    if label.startswith('학습 전'):
        return ''
    return CHIP['real'] + CHIP['syn'] if '합성' in label else CHIP['real']
# 브랜드 색(공식 로고에서 뽑은 값): Gemma(Google) 파랑, Kanana(카카오) 노랑, GPT-OSS(OpenAI) 검정, Jev(TypeSafe AI) 분홍
BRAND = {'gemma': '#446EFF', 'kanana': '#FFCD00', 'gptoss': '#111111', 'jev': '#E551BA', 'decisions': '#10A37F'}  # decisions: OpenAI Decisions API(gpt-6-luna), GPT-OSS 검정과 구분하려고 OpenAI 초록


STYLE = r'''.wrap{max-width:1180px}table.mx td.c{white-space:nowrap}.two{align-items:start}table.mx td,table.mx th{font-size:13.5px}
.tth{margin:8px 0 10px}.plan{display:inline-block;padding:1px 10px;border-radius:999px;font-size:12.5px;font-weight:700;color:#0b7a57;background:#e3f5ee;border:1px solid #10A37F}
.kcards{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}.kc{border:1px solid var(--line);border-radius:10px;padding:14px}
.kc .kv{font-size:26px;font-weight:700;line-height:1.2;margin-bottom:6px}.kc b{font-size:14px}.kc p{font-size:12.5px;color:var(--ink-2);margin:6px 0 0;line-height:1.55}
.knext{list-style:none;padding:0;margin:0}.knext li{display:flex;gap:14px;padding:12px 0;border-top:1px solid var(--line)}.knext .kn{font-size:22px;font-weight:700;min-width:22px}
.knext p{margin:4px 0 0;font-size:14px;color:var(--ink-2)}
@media (max-width:1100px){.kcards{grid-template-columns:1fr 1fr}}@media (max-width:560px){.kcards{grid-template-columns:1fr}}.tl .A{background:#3a3a38}
.mcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:0 0 18px}
.mc{border:1px solid var(--line);border-radius:10px;padding:14px 16px;background:#fff}
.mh{display:flex;align-items:center;gap:8px;font-size:14.5px}.mh img{width:26px;height:26px;border-radius:6px;object-fit:contain}.mh span{margin-left:auto;font-size:12px;color:var(--ink-3)}
.mv{font-size:30px;font-weight:700;line-height:1.2;margin-top:10px}.mg{font-size:12.5px;color:var(--ink-2)}
.mst{margin-top:10px;font-size:13px;font-weight:700;padding:4px 8px;border-radius:6px;background:color-mix(in srgb,var(--b) 14%,#fff)}
.ms{list-style:none;margin:8px 0 0;padding:0;font-size:12.5px}.ms li{display:flex;justify-content:space-between;gap:8px;padding:5px 0;border-top:1px solid var(--line)}
.ms li.now b{color:#111}.ms li.now span::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--b);margin-right:6px;vertical-align:1px}
.ms li.wait{color:var(--ink-3)}.ms li.wait b{font-weight:500}
@media (max-width:1100px){.mcards{grid-template-columns:1fr 1fr}}@media (max-width:560px){.mcards{grid-template-columns:1fr}}
.layout{display:grid;grid-template-columns:180px minmax(0,1fr);gap:40px;max-width:1440px;margin:0 auto;padding:0 24px 88px}
.layout main{min-width:0}
nav.side{position:sticky;top:0;align-self:start;padding-top:48px;font-size:14px}
nav.side b{display:block;font-size:12.5px;color:var(--ink-3);margin:0 0 10px 12px}
nav.side a{display:block;padding:6px 12px;color:var(--ink-2);text-decoration:none;border-left:2px solid var(--line)}
nav.side a.on{color:var(--accent);border-left-color:var(--accent);font-weight:600}
.two>*,.three>*{min-width:0}
.kind{display:inline-block;font-size:11.5px;font-weight:700;border-radius:4px;padding:1px 7px;margin-left:5px;vertical-align:1px;white-space:nowrap}.kind.real{background:#d9e7f8;color:#1d5fb0}.kind.syn{background:#ece3fb;color:#6a3fc1}.kind.none{background:#eee;color:#555}.legend{margin:6px 0 14px;font-size:13.5px;color:var(--ink-2)}
details{border-top:1px solid var(--line);padding:14px 0}details summary{cursor:pointer;font-weight:600;font-size:16px}
@media (max-width:900px){.layout{grid-template-columns:1fr;gap:0;padding:0 16px 64px}nav.side{position:static;display:flex;flex-wrap:wrap;gap:6px;padding-top:16px}nav.side b{display:none}nav.side a{border:1px solid var(--line);border-radius:999px;padding:3px 10px;font-size:13px}table.mx td.rw{white-space:nowrap}details>table.mx{display:block;overflow-x:auto}}
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--line);margin:28px 0 0}.tabs button{font:inherit;font-size:15px;background:none;border:0;border-bottom:2px solid transparent;padding:8px 14px;color:var(--ink-2);cursor:pointer}.tabs button.on{color:var(--ink);border-bottom-color:var(--accent);font-weight:700}
.who{display:inline-block;font-size:11.5px;font-weight:700;border-radius:4px;padding:1px 7px;margin-right:6px;vertical-align:1px}.who.me{background:#111;color:#fff}.who.cl{background:var(--tint);color:#1d5fb0}
.flow2{display:grid;grid-template-columns:1fr 1fr;gap:32px}.flow2 h4{margin:0 0 10px;font-size:14px;color:var(--ink-3)}.flow1{max-width:640px;margin:0 auto}.lanes{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.lanes .fn{padding:10px 12px}@media (max-width:700px){.lanes{grid-template-columns:1fr}}
.fn{border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:#fff}.fn b{font-size:15px}.fn p{margin:4px 0 0;font-size:13px;color:var(--ink-2);line-height:1.6}.fn.now{border:2px solid var(--accent)}.nowt{float:right;font-size:12px;font-weight:700;color:var(--accent)}
.fa{height:26px;position:relative}.fa::before{content:"";position:absolute;left:50%;top:2px;bottom:6px;border-left:2px solid #8c8c87}.fa::after{content:"";position:absolute;left:calc(50% - 5px);bottom:0;border:5px solid transparent;border-top:7px solid #8c8c87;border-bottom:0}
.fd{text-align:center}.fq{display:inline-block;padding:10px 18px;border:1px dashed #8c8c87;border-radius:999px;font-size:14px;font-weight:700}.fb{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px;font-size:13px;color:var(--ink-2)}.fb>div{border-top:2px solid #8c8c87;padding-top:6px}.yn{display:block;font-weight:700;color:var(--ink)}
.fmerge{height:40px;margin:6px 25% 0;border:2px solid #8c8c87;border-top:0;border-radius:0 0 12px 12px;position:relative}.fmerge::after{content:"";position:absolute;left:calc(50% - 1px);top:100%;height:20px;border-left:2px solid #8c8c87}.flow1{margin-top:24px}
@media (max-width:900px){.flow2{grid-template-columns:1fr}.fmerge{display:none}}'''


def logo(key):
    import base64
    for ext, mime in (('svg', 'image/svg+xml'), ('png', 'image/png')):
        f = HERE / 'logos' / f"{'gptoss' if key == 'decisions' else key}.{ext}"
        if f.exists():
            return f'<img src="data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}" alt="">'
    return ''


def jl(p):
    p = pathlib.Path(p)
    return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()] if p.exists() else []


def load():
    g = jl(HERE / 'results_gemma4e4b.jsonl')
    k = jl(HERE / 'results_kanana.jsonl')
    o = jl(HERE / 'results_gptoss20b.jsonl') or jl(HERE / 'results_gptoss20b.partial.jsonl')
    ans = lambda rs: {r['id']: r for r in rs if 'skipped' not in r}
    return {'gemma': ans(g), 'kanana': ans(k), 'gptoss': ans(o)}, {'gptoss': o}


def load_jev():
    """Jev v2 질문 결과를 시험 문항 번호(S1-A01, S2-B01-asset)로 맞춘다. S3는 Jev 결과 없음."""
    out = {}
    try:
        d1 = {i['id']: i for i in json.loads((RESEARCH / 'Jev시험_2026-10-09/results.json').read_text())['items']}
        rows = json.loads((RESEARCH / 'Jev시험2_2026-10-09/results.json').read_text())['rows']
    except Exception:
        return out
    d2 = {(r['id'], r['task']): r for r in rows if r.get('ver') == 'v2'}
    d3 = {r['id']: r for r in jl(HERE / 'results_jev_s3.jsonl') if 'pred' in r}
    return d1, d2, d3


def jev_for(ids_meta, jev):
    if not jev:
        return {}
    d1, d2, d3 = jev
    res = {}
    for qid, r in ids_meta.items():
        if r['set'] == 'S1':
            j = d1.get(qid.split('-', 1)[1])
        elif r['set'] == 'S2':
            j = d2.get(('-'.join(qid.split('-')[1:-1]), r['task']))
        else:
            j = d3.get(qid)
            if j is not None:
                res[qid] = {'correct': bool(j['correct']), 'conf': j.get('conf') or 0, 'pred': j['pred'], 'p_yes': j.get('p_yes'), 'task': r['task'], 'gold': r['gold']}
            continue
        if j is not None:
            a = j.get('answer')
            pred = ('true' if a else 'false') if isinstance(a, bool) else a  # Jev v1, v2는 예/아니오를 참/거짓 값으로 적었다
            py = None
            if r['gold'] in ('true', 'false') and j.get('p_gold') is not None:  # 정답 쪽 확률로 '예' 확률을 되돌린다(AUROC용)
                py = j['p_gold'] if r['gold'] == 'true' else 1 - j['p_gold']
            res[qid] = {'correct': bool(j['correct']), 'conf': j.get('confidence') or 0, 'pred': pred, 'p_yes': py, 'task': r['task'], 'gold': r['gold']}
    return res


FT = RESEARCH / '파인튜닝_2026-10-11'


def _res(path):
    rs = jl(path)
    d = [r for r in rs if 'pred' in r]
    if not d:
        return None
    ov = [r for r in d if r['set'] in ('S1', 'S2')]
    hi = [r for r in d if r['conf'] >= 0.95]
    return dict(c=sum(r['correct'] for r in d), n=len(d), c204=sum(r['correct'] for r in ov), n204=len(ov),
                hi=len(hi), hiw=sum(not r['correct'] for r in hi), lines=len(rs))


def _steps(path):
    p = pathlib.Path(path)
    if not p.exists():
        return '-'
    m = re.findall(r'step (\d+)/(\d+) loss ([\d.]+)', p.read_text(encoding='utf-8', errors='replace'))
    return f'{m[-1][0]}/{m[-1][1]} (손실 {m[-1][2]})' if m else '시작 전'


def _row(nm, dev, label, res, steps='-', valid=None):
    if res:
        prog = '끝남' if res['lines'] >= 324 else f"{res['lines']}/324"
        cells = f"<td class=\"c\">{res['c']}/{res['n']}</td><td class=\"c\">{res['c204']}/{res['n204']}</td><td class=\"c\">{res['hiw']}/{res['hi']}</td>"
    else:
        prog = '-'
        cells = '<td class="c">-</td>' * 3
    v = f"{valid['c']}/{valid['n']}" if valid else '-'
    return f'<tr><td class="rw">{E(nm)}</td><td>{E(dev)}</td><td>{E(label)}</td><td class="c">{E(steps)}</td><td class="c">{prog}</td><td class="c">{v}</td>{cells}</tr>'


def _table(rows):
    return ('<div class="tw"><table class="mx"><tr><th>모델</th><th>장비</th><th>구분</th><th class="c">학습 단계</th><th class="c">재시험 진행</th>'
            '<th class="c">검증 세트</th><th class="c">277문항</th><th class="c">S1, S2 204문항</th><th class="c">확신 0.95 이상 오답</th></tr>'
            + ''.join(rows) + '</table></div>')


def ft_sections(jev):
    R = FT / 'runs'
    jc = sum(v['correct'] for v in jev.values()); jh = [v for v in jev.values() if v['conf'] >= 0.95]
    j204 = {q: v for q, v in jev.items() if not q.startswith('S3')}
    jrow = (f'<tr class="me"><td class="rw">Jev(목표)</td><td>API</td><td>참고</td><td class="c">-</td><td class="c">-</td><td class="c">-</td>'
            f'<td class="c">{jc}/{len(jev)}</td><td class="c">{sum(v["correct"] for v in j204.values())}/{len(j204)}</td>'
            f'<td class="c">{sum(not v["correct"] for v in jh)}/{len(jh)}</td></tr>')
    kb = _res(FT / 'results_kanana_base_t4.jsonl'); gb = _res(FT / 'results_gemma_base_t4.jsonl')
    pilot = _table([
        _row('Kanana 1.5 8B', 'Colab 2(학교 계정)', '학습 전(T4)', kb),
        _row('Kanana 1.5 8B', 'Colab 2(학교 계정)', '맛보기 학습 뒤', _res(R / 'colab2/results_kanana-ft0.jsonl'),
             _steps(R / 'colab2/steps_kanana-ft0.log'), _res(R / 'colab2/valid_kanana-ft0.jsonl')),
        jrow])
    items = []
    for f in sorted((FT / 'items').glob('*.jsonl')):
        items += [json.loads(l) for l in f.read_text(encoding='utf-8').splitlines() if l.strip()]
    ver = {}
    for f in sorted((FT / 'verify').glob('*.jsonl')):
        for l in f.read_text(encoding='utf-8').splitlines():
            if l.strip():
                v = json.loads(l); ver[v['id']] = v['label']
    tr = jl(FT / 'sets' / 'train_v2.jsonl'); va = jl(FT / 'sets' / 'valid_v2.jsonl')
    names = {'asset': '자산 종류', 'R08': 'R08 검증 종류', 'R11_broad': 'R11 넓게', 'R11_narrow': 'R11 좁게', 'R12': 'R12 보관 기관', 'R15': 'R15 경영진 서명', 'R14': 'R14 이자 없음'}
    cnt = collections.Counter(i['task'] for i in items)
    agr = collections.Counter(i['task'] for i in items if ver.get(i['id']) == i['gold'])
    tct = collections.Counter(i['task'] for i in tr)
    drows = ''.join(f'<tr><td class="rw">{names[t]}</td><td class="c">{cnt[t]}</td><td class="c">{agr[t]}</td><td class="c">{tct[t]}</td></tr>' for t in names)
    drows += f'<tr class="me"><td class="rw">합계</td><td class="c">{len(items)}</td><td class="c">{sum(agr.values())}</td><td class="c">{len(tr)}</td></tr>'
    data = (f'<table class="mx"><tr><th>과제</th><th class="c">모은 문항</th><th class="c">두 독자 일치</th><th class="c">학습 세트</th></tr>{drows}</table>'
            f'<p class="cav">학습 세트는 두 독자가 같은 라벨을 단 문항에서 시험과 겹치는 문항, 같은 문항을 빼고 자산 종류마다 상한을 둔 것이다. 검증 세트 {len(va)}문항은 따로 둔다.</p>')
    main = _table([
        _row('Gemma 4 E4B', 'Colab 3(kanginseong24)', '학습 전(T4)', gb),
        _row('Gemma 4 E4B', 'Colab 3(kanginseong24)', '본 학습 뒤', _res(R / 'colab3/results_gemma-ft3.jsonl'),
             _steps(R / 'colab3/steps_gemma-ft3.log'), _res(R / 'colab3/valid_gemma-ft3.jsonl')),
        _row('Gemma 4 E4B', 'Colab 3(kanginseong24)', '본 학습 2차 뒤(자료 v3)', _res(R / 'colab3/results_gemma-ft4.jsonl'),
             _steps(R / 'colab3/steps_gemma-ft4.log'), _res(R / 'colab3/valid_gemma-ft4.jsonl')),
        _row('Kanana 1.5 8B', 'Colab 2(학교 계정)', '학습 전(T4)', kb),
        _row('Kanana 1.5 8B', 'Colab 2(학교 계정)', '본 학습 뒤', _res(R / 'colab2/results_kanana-ft2.jsonl'),
             _steps(R / 'colab2/steps_kanana-ft2.log'), _res(R / 'colab2/valid_kanana-ft2.jsonl')),
        _row('GPT-OSS-20B', 'Colab 4(healthchicken24)', '학습 전(추론 후 답)', _res(HERE / 'results_gptoss20b.jsonl') or _res(HERE / 'results_gptoss20b.partial.jsonl')),
        _row('GPT-OSS-20B', 'Colab 4(healthchicken24)', '학습 전(바로 답)', _res(R / 'colab4/results_gptoss_direct_base.jsonl')),
        _row('GPT-OSS-20B', 'Colab 4(healthchicken24)', '본 학습 뒤', _res(R / 'colab4/results_gptoss-ft2.jsonl'),
             _steps(R / 'colab4/steps_gptoss-ft2.log'), _res(R / 'colab4/valid_gptoss-ft2.jsonl')),
        jrow])
    return f'''<section><h2>파인튜닝 본 학습</h2>
<p>목표는 세 모델 모두 Jev 수준이다. 277문항에서 {jc}개, S1, S2 204문항에서 {sum(v["correct"] for v in j204.values())}개 이상을 맞히고, 확신 0.95 이상 오답을 Jev({sum(not v["correct"] for v in jh)}건) 이하로 줄이는 것이다. 학습 문항은 시험에 쓰인 발행사(Circle, Paxos, Gemini, Ripple, Tether, 한국 거래소 등) 밖의 문서로 새로 만들었고, 질문 글은 시험과 같은 틀이다. 모두 Colab에서 학습한다.</p>
<div class="two"><div class="chart"><h4>학습 문항</h4><p class="sub">수집, 두 독자 대조, 학습 세트</p>{data}</div>
<div class="chart"><h4>방식</h4><p class="sub">세 모델 공통</p><table class="mx"><tr><th>항목</th><th>값</th></tr>
<tr><td>학습</td><td>QLoRA(4비트 위에 LoRA r16), 2바퀴, 정답 글자 하나에만 손실</td></tr>
<tr><td>저장</td><td>10단계마다 드라이브에 저장, 끊기면 그 자리부터 이어서</td></tr>
<tr><td>재시험</td><td>집 PC와 같은 채점 방식, 277문항</td></tr>
<tr><td>GPT-OSS-20B</td><td>추론 칸을 비우고 바로 답 글자 확률을 읽는다. 어텐션과 전문가층을 조각으로 계산해 T4에서도 학습 문항을 하나도 빼지 않는다</td></tr></table></div></div>
{_table_note()}
{main}</section>''', f'''<section><h2>파인튜닝 맛보기</h2>
<p>두 번째 독자 대조 전의 자료(학습 453문항, 첫 라벨만)로 학습이 점수를 올리는지 미리 본 시험이다. 본 결과로 쓰지 않는다.</p>
{pilot}</section>'''


def _table_note():
    return '<p class="cav">학습 단계는 갱신 횟수(8문항마다 1번), 재시험 진행은 324문항 가운데 처리한 수(12000자 넘는 47문항은 건너뜀 기록), 확신 0.95 이상 오답은 오답 수/해당 문항 수다.</p>'


def score(rs, ids=None):
    xs = [r for q, r in rs.items() if ids is None or q in ids]
    return sum(bool(r['correct']) for r in xs), len(xs)


def pct(a, b):
    return f'{100 * a / b:.0f}%' if b else '-'


def read_status(path):
    st = {}
    if not path or not pathlib.Path(path).exists():
        return st
    s = pathlib.Path(path).read_text(encoding='utf-8', errors='replace')
    m = re.search(r'alive (\w+) lines (\d+) answered (\d+) correct (\d+) skipped (\d+)', s)
    if m:
        st.update(alive=m.group(1) == 'True', lines=int(m.group(2)))
    m = re.search(r'(\d+) MiB, (\d+) %', s)
    if m:
        st.update(mem=int(m.group(1)), util=int(m.group(2)))
    m = re.search(r'^CHECKED (.+)$', s, re.M)
    if m:
        st['checked'] = m.group(1).strip()
    return st


def _byid(path):
    return {r['id']: r for r in jl(path) if 'pred' in r}


def _best(cands):
    """(태그, 경로) 가운데 재시험을 끝낸(324줄) 첫 결과."""
    for t, f in cands:
        rs = jl(f)
        if len(rs) >= 324 and any('pred' in r for r in rs):
            return t, {r['id']: r for r in rs if 'pred' in r}
    return None, None


def _bars(rows, lo, hi, note):
    """rows = (이름, 값, 값 글, 파랑 여부). 같은 축 lo~hi."""
    out = '<div class="bars">'
    for lab, v, txt, acc in rows:
        w = 72 * max(0.0, min(1.0, (v - lo) / (hi - lo))) if v is not None else 0  # 값 글 자리를 남긴다
        col = BRAND['jev'] if acc is True else (acc or '')
        out += (f'<span>{E(lab)}</span><div class="row"><div class="bar" style="width:{w:.1f}%;{f"background:{col}" if col else ""}" '
                f'data-tip="{E(txt)}" tabindex="0"></div><span class="val">{E(txt)}</span></div>')
    return out + f'</div><p class="note">{E(note)}</p>'


def _steps_eta(path):
    p = pathlib.Path(path)
    m = re.findall(r'step (\d+)/(\d+) loss [\d.]+ (\d+)s', p.read_text(encoding='utf-8', errors='replace')) if p.exists() else []
    if not m:
        return None
    st, tot, sec = map(int, m[-1])
    return st, tot, (tot - st) * sec / max(1, st)


def _hm(sec):
    h, mnt = divmod(int(sec // 60), 60)
    return f'약 {h}시간 {mnt}분' if h else f'약 {mnt}분'


def _dec277():
    f = FT / 'results_openai_decisions_277.jsonl'
    return _byid(f) if len(jl(f)) >= 277 else None


def _place_labels(xy, texts, W, H, fs=11.5, avoid=()):
    """점 옆 글자 자리 고르기: 다른 글자, 점, 그림 밖과 겹치지 않는 첫 후보 자리. 점에서 멀면 잇는 선을 그린다.
    ponytail: 글자 폭은 글자 종류로 어림한다(한글 0.95em, 그 밖 0.56em). 실제 글꼴 폭과 다르면 여유값을 키운다."""
    wid = lambda t: sum(fs * (0.95 if ord(c) > 0x1100 else 0.56) for c in t)
    boxes = [(x - 8, y - 8, x + 8, y + 8) for x, y in xy] + list(avoid)
    hit = lambda a, b: a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
    cands = [(10, 4, 'start'), (-10, 4, 'end')]
    for dy in (-13, 19, -27, 33, -41, 47, -55, 61):
        cands += [(8, dy, 'start'), (-8, dy, 'end')]
    out = []
    for (x, y), t in zip(xy, texts):
        w = wid(t)
        for dx, dy, anc in cands:
            tx, ty = x + dx, y + dy
            x0 = tx if anc == 'start' else tx - w
            box = (x0 - 2, ty - fs, x0 + w + 2, ty + 3)
            if box[0] >= 0 and box[2] <= W and box[1] >= 0 and box[3] <= H and not any(hit(box, b) for b in boxes):
                break
        boxes.append(box)
        out.append((tx, ty, anc, abs(dy) > 20))
    return out


def overview(jev):
    R = FT / 'runs'
    gt, G = _best([('ft4', R / 'colab3/results_gemma-ft4.jsonl'), ('ft3', R / 'colab3/results_gemma-ft3.jsonl')])
    kt, K = _best([('synB', R / 'desktop/results_kanana-synB.jsonl'), ('ft3', R / 'desktop/results_kanana-ft3.jsonl'), ('ft2', R / 'colab2/results_kanana-ft2.jsonl')])
    ot, O = _best([('ft2', R / 'colab4/results_gptoss-ft2.jsonl')])
    gb, kb = _byid(FT / 'results_gemma_base_t4.jsonl'), _byid(FT / 'results_kanana_base_t4.jsonl')
    ob = _byid(R / 'colab4/results_gptoss_direct_base.jsonl')
    cnt = lambda d: sum(bool(r['correct']) for r in d.values())
    jc = sum(bool(v['correct']) for v in jev.values())
    line3 = jc - 0.03 * TOTAL

    # 1. 학습 전 → 학습 뒤(같은 축, Jev 선)
    def auto(models, th):
        ids = [q for q in models[0] if all(q in m for m in models)]
        ok = [q for q in ids if len({m[q]['pred'] for m in models}) == 1 and all(m[q]['conf'] >= th for m in models)]
        return len(ok), sum(not models[0][q]['correct'] for q in ok)
    lo, hi_ = 180, TOTAL
    X = lambda v: 150 + 340 * (v - lo) / (hi_ - lo)
    rows = [('Gemma 4 E4B', cnt(gb), cnt(G), 'gemma'), ('Kanana 1.5 8B', cnt(kb), cnt(K), 'kanana'),
            ('GPT-OSS-20B', cnt(ob), cnt(O) if O else None, 'gptoss')]
    H = 40 + 46 * len(rows)
    svg = [f'<svg viewBox="0 0 520 {H + 22}" style="max-width:520px;width:100%" role="img" aria-label="학습 전과 학습 뒤 정답 수">']
    for v, lab, dash, col, anc, dx in ((line3, f'Jev−3%p {line3:.0f}', '4 3', '#8c8c87', 'end', -4), (jc, f'Jev {jc}', '', BRAND['jev'], 'start', 4)):
        svg.append(f'<line x1="{X(v):.1f}" y1="22" x2="{X(v):.1f}" y2="{H}" stroke="{col}" stroke-width="2" stroke-dasharray="{dash}"/>'
                   f'<text x="{X(v) + dx:.1f}" y="14" font-size="12" text-anchor="{anc}" fill="{col}">{lab}</text>')
    D = _dec277()
    if D:
        dcn = sum(bool(x['correct']) for x in D.values())
        svg.append(f'<line x1="{X(dcn):.1f}" y1="34" x2="{X(dcn):.1f}" y2="{H}" stroke="{BRAND["decisions"]}" stroke-width="2"/>'
                   f'<text x="{X(dcn):.1f}" y="29" font-size="12" text-anchor="middle" fill="{BRAND["decisions"]}">Decisions {dcn}</text>')
    for i, (nm, b0, a0, key) in enumerate(rows):
        y = 48 + 46 * i
        svg.append(f'<text x="0" y="{y + 4}" font-size="13" fill="#111">{nm}</text><line x1="150" y1="{y}" x2="490" y2="{y}" stroke="#e3e3e0"/>')
        svg.append(f'<circle cx="{X(b0):.1f}" cy="{y}" r="6" fill="#fff" stroke="#8c8c87" stroke-width="2"/>'
                   f'<text x="{X(b0):.1f}" y="{y + 20}" font-size="11.5" text-anchor="middle" fill="#555">{b0}</text>')
        if a0 is not None:
            svg.append(f'<line x1="{X(b0) + 7:.1f}" y1="{y}" x2="{X(a0) - 8:.1f}" y2="{y}" stroke="{BRAND[key]}" stroke-width="3"/>'
                       f'<circle cx="{X(a0):.1f}" cy="{y}" r="8" fill="{BRAND[key]}" stroke="#111" stroke-width="{1 if key == "kanana" else 0}"/>'
                       f'<text x="{X(a0):.1f}" y="{y - 13}" font-size="12.5" font-weight="700" text-anchor="middle" fill="#111">{a0}</text>')
        else:
            svg.append(f'<text x="{X(b0) + 12:.1f}" y="{y + 4}" font-size="12" fill="#555">학습 중</text>')
    svg.append(f'<text x="150" y="{H + 18}" font-size="11" fill="#85857f">{lo}</text><text x="490" y="{H + 18}" font-size="11" text-anchor="end" fill="#85857f">{hi_}문항</text></svg>')
    c1 = ('<div class="chart"><h4>학습 전 → 학습 뒤 정답 수(277문항)</h4><p class="sub">빈 동그라미는 학습 전, 색 동그라미는 학습 뒤. 분홍 선이 목표인 Jev, 초록 선이 Decisions API(학습 없음)</p>'
          + ''.join(svg) + '</div>')

    # 2. 자동 확정 문항 수와 오답 비율(오른쪽 아래가 좋다)
    jh = [v for v in jev.values() if v['conf'] >= 0.95]
    jn, jw = len(jh), sum(not v['correct'] for v in jh)
    pts = [('Gemma 0.95', *auto([G], 0.95), BRAND['gemma'], -10, 4), ('Gemma 0.999', *auto([G], 0.999), BRAND['gemma'], -10, 4),
           ('G+K 0.95', *auto([G, K], 0.95), '#555', 10, -2), ('G+K 0.99', *auto([G, K], 0.99), '#555', 10, -6),
           ('G+K 0.999', *auto([G, K], 0.999), '#555', 10, 4), ('Jev 0.95', jn, jw, BRAND['jev'], -10, 4)]
    if _dec277():
        dd = _dec277(); dh = [q for q in dd if dd[q]['conf'] >= 0.95]
        pts.append(('Decisions 0.95', len(dh), sum(not dd[q]['correct'] for q in dh), BRAND['decisions'], -10, -6))  # (이름, 수, 오답, 색, 글자 x, y 이동)
    ymax = max(100 * w / n for _, n, w, *_ in pts if n) * 1.15
    PX = lambda n: 50 + 420 * n / TOTAL
    PY = lambda r: 210 - 180 * r / ymax
    sv = ['<svg viewBox="0 0 560 250" style="max-width:560px;width:100%" role="img" aria-label="자동 확정 문항 수와 오답 비율">',
          '<line x1="50" y1="210" x2="470" y2="210" stroke="#bbb"/><line x1="50" y1="20" x2="50" y2="210" stroke="#bbb"/>',
          f'<text x="470" y="238" font-size="11" text-anchor="end" fill="#85857f">자동 확정 문항 수(많을수록 사람 일이 준다) → {TOTAL}</text>',
          f'<text x="54" y="16" font-size="11" fill="#85857f">↑ 오답 비율(낮을수록 좋다), 위 끝 {ymax:.1f}%</text>']
    xy = [(PX(n), PY(100 * w / n if n else 0)) for _, n, w, *_ in pts]
    labs = [f'{nm}: {n}개, {100 * w / n if n else 0:.1f}%' for nm, n, w, *_ in pts]
    for (x, y), (*_, col, _dx, _dy) in zip(xy, pts):
        sv.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{col}"/>')
    for (x, y), (tx, ty, anc, lead), t in zip(xy, _place_labels(xy, labs, 560, 226, avoid=[(54, 4, 330, 20)]), labs):
        if lead:
            sv.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{tx:.1f}" y2="{ty - 4:.1f}" stroke="#b5b5b0" stroke-width="1"/>')
        sv.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="11.5" text-anchor="{anc}" fill="#111">{t}</text>')
    sv.append('</svg>')
    c2 = ('<div class="chart"><h4>자동 확정 문항 수와 오답 비율</h4><p class="sub">G+K는 Gemma와 Kanana가 같은 답일 때만 확정. 숫자는 확신 기준. 오른쪽 아래(많이 자동, 적게 틀림)가 좋다</p>'
          + ''.join(sv) + '</div>')

    # 2-1. 과제별 정답률(277문항): Jev보다 얼마나 낮은지만 색으로
    names = {'asset': '자산 종류', 'R14': 'R14 이자 없음', 'R08': 'R08 검증 종류', 'R11_broad': 'R11 넓게', 'R11_narrow': 'R11 좁게', 'R12': 'R12 보관 기관', 'R15': 'R15 경영진 서명'}
    task_of = {q: r['task'] for q, r in G.items()}
    grid_rows = [(f'Gemma({gt})', G, 'gemma'), (f'Kanana({kt})', K, 'kanana')] + ([(f'GPT-OSS({ot})', O, 'gptoss')] if O else []) + ([('Decisions API', _byid(FT / 'results_openai_decisions_277.jsonl'), 'decisions')] if len(jl(FT / 'results_openai_decisions_277.jsonl')) >= 277 else []) + [('Jev(목표)', jev, 'jev')]
    jt = {t: [q for q in jev if task_of.get(q) == t] for t in names}
    head = ''.join(f'<th class="c">{v}</th>' for v in names.values())
    body = ''
    for nm, d, key in grid_rows:
        cells = ''
        for t in names:
            qs = [q for q in jt[t] if q in d]
            acc = sum(bool(d[q]['correct']) for q in qs) / max(1, len(qs))
            jacc = sum(bool(jev[q]['correct']) for q in jt[t]) / max(1, len(jt[t]))
            gap = round(100 * (acc - jacc))
            bg = '#fff' if key == 'jev' or gap > -5 else ('#fde7cf' if gap > -15 else '#f6b77a')
            sub = f'<br><span style="font-size:12px">{gap:+d}</span>' if key != 'jev' and gap <= -5 else ''
            cells += f'<td class="c" style="background:{bg};font-size:16px"><b>{100 * acc:.0f}%</b>{sub}</td>'
        body += f'<tr><td class="rw"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{BRAND[key]};margin-right:6px"></span>{E(nm)}</td>{cells}</tr>'
    grid = ('<h3>과제별 정답률(277문항)</h3><div class="tw"><table class="mx"><tr><th>모델</th>' + head + '</tr>' + body + '</table></div>'
            '<p class="cav">주황 칸은 Jev보다 낮은 과제(연한 주황 5~15%p, 진한 주황 15%p 넘게). 숫자는 Jev와의 차이(%p).</p>')

    # 같은 문항 비교(Gemma vs Jev)
    ids = [q for q in jev if q in G]
    b = sum(bool(G[q]['correct']) and not jev[q]['correct'] for q in ids)
    c = sum(not G[q]['correct'] and bool(jev[q]['correct']) for q in ids)
    ga, gk = auto([G, K], 0.99)

    # 3. 단계
    stages = ('<div class="tl"><div class="A" style="flex:1">1판 학습</div><div class="A" style="flex:1">검증, 최종 시험 문항</div>'
              '<div class="B" style="flex:1">개선 판</div><div class="B" style="flex:1">최종 시험</div></div>'
              '<div class="tll"><span style="flex:1"><b>진행 중</b></span><span style="flex:1"><b>진행 중</b></span>'
              '<span style="flex:1">약한 과제 보강, 다시 학습</span><span style="flex:1">마지막에 한 번, Jev와 같이</span></div>')

    # 4. 지금 학습
    prog = []
    for nm, f, col in (('Gemma 2차', R / 'colab3/steps_gemma-ft4.log', BRAND['gemma']), ('GPT-OSS 1차', R / 'colab4/steps_gptoss-ft2.log', BRAND['gptoss'])):
        e = _steps_eta(f)
        if (R / f.parent.name / f.name.replace('steps_', 'stopped_').replace('.log', '.txt')).exists():
            prog.append((nm, 100 * e[0] / e[1] if e else 0, '중단(Colab 한도), 저장점에서 이어서 할 수 있음', col))
        elif e:
            st, tot, left = e
            prog.append((nm, 100 * st / tot, f'{st}/{tot}단계, 학습 {_hm(left)} 남음' if st < tot else f'{st}/{tot}단계, 학습 끝, 재시험 중', col))
    e = _steps_eta(R / 'desktop/steps_kanana-ft3.log')  # 데스크톱 학습, 사람이 가져온 기록 기준
    ev3 = [x for x in jl(R / 'desktop/evalset_kanana-ft3.jsonl') if 'pred' in x]
    if len(jl(R / 'desktop/results_kanana-ft3.jsonl')) >= 324:
        prog.append(('Kanana 2차', 100, f'학습 끝(데스크톱), 검증 세트 {sum(bool(x["correct"]) for x in ev3)}/{len(ev3)}' if len(ev3) >= 372
                     else '학습 끝(데스크톱), 다음: 검증 세트 372문항', BRAND['kanana']))
    else:
        prog.append(('Kanana 2차', 100 * e[0] / e[1] if e else 0, f'데스크톱 {e[0]}/{e[1]}단계(가져온 기록 기준)' if e else '대기', BRAND['kanana']))
    c4 = ('<div class="chart"><h4>지금 학습</h4><p class="sub">자료 v3, 세 모델 모두 2바퀴</p>'
          + _bars(prog, 0, 100, '막대는 학습 단계 진행률. 학습이 끝나면 277문항과 검증 세트 재시험이 이어진다.') + '</div>')

    # 5. 문항 모으기
    def ver(items_path, ver_path):
        it = {r['id']: r for r in jl(items_path)}
        v = {r['id']: r for f in sorted(pathlib.Path(ver_path).parent.glob('*.jsonl')) for r in jl(f) if r['id'] in it}  # 대조 파일이 여럿으로 나뉠 수 있다
        if not it:
            return '-', '수집 중'
        if not v:
            return str(len(it)), '대조 전'
        agree = sum(1 for q in it if q in v and v[q]['label'] == it[q]['gold'])
        return str(len(it)), f'대조 {len(v)}/{len(it)}, 두 독자 일치 {agree}'
    W = FT
    rows5 = [('약관 R14', '검증, 최종 시험', *ver(W / 'items_eval/eval-terms.jsonl', W / 'verify_eval/verify-eval-terms.jsonl')),
             ('달러 발행사 보고서', '검증, 최종 시험', *ver(W / 'items_eval/eval-a.jsonl', W / 'verify_eval/verify-eval-a.jsonl')),
             ('비달러 발행사 보고서', '검증, 최종 시험', *ver(W / 'items_eval/eval-b.jsonl', W / 'verify_eval/verify-eval-b.jsonl')),
             ('학습 발행사 다른 달 보고서', '학습 보강', *ver(W / 'items/rep-c.jsonl', W / 'verify/verify-repc.jsonl'))]
    t5 = ('<div class="tw"><table class="mx"><tr><th>묶음</th><th>용도</th><th class="c">모은 문항</th><th>두 번째 독자 대조</th></tr>'
          + ''.join(f'<tr><td class="rw">{E(a1)}</td><td>{E(a2)}</td><td class="c">{E(a3)}</td><td>{E(a4)}</td></tr>' for a1, a2, a3, a4 in rows5)
          + '</table></div><p class="cav">검증과 최종 시험 문항은 시험과 학습에 쓰지 않은 발행사 문서로 만든다. 두 독자의 라벨이 같은 문항만 쓴다.</p>')

    return f"""<section><h2>한눈에</h2>
<p>Gemma는 Jev보다 <b>{jc - cnt(G)}개</b>, Kanana는 <b>{jc - cnt(K)}개</b> 적게 맞혔다. 두 모델이 같은 답일 때만 확정하면 오답 비율은 Jev와 비슷하다.
<div class="two">{c1}{c2}</div>
{grid}
<p class="cav">277문항은 여러 번 본 시험이라 참고값이다.</p>
</section>""", f"""<section><h2>진행 단계</h2>
{stages}
<div class="two">{c4}</div>
<details id="d-collect"><summary>문항 모으기와 대조 현황</summary><p class="sub">수집은 Sonnet, 두 번째 독자는 Opus(검증과 최종 시험은 effort max, 학습은 high)</p>{t5}</details>
</section>""", f"""<section><h2>목표 판정 기준(안)</h2>
<dl class="def">
<dt>정답률</dt><dd>Gemma가 Jev보다 3%p 넘게 낮지 않을 것 <span class="tbd">미정</span></dd>
<dt>자동 확정 오답</dt><dd>오답 비율이 Jev 이하일 것 <span class="tbd">미정</span></dd>
<dt>최종 시험</dt><dd>553문항, 마지막에 한 번</dd>
<dt>Kanana</dt><dd>한국어 기준 모델이라 꼭 쓴다. 맡을 역할(한국어 문서 담당 등) <span class="tbd">미정</span></dd>
</dl>
</section>""", f"""<section><h2>용어</h2>
<dl class="def">
<dt>파인튜닝(QLoRA)</dt><dd>이미 만들어진 모델에 우리 문항을 더 학습시키는 방법. 모델 전체가 아니라 덧붙인 작은 부분만 학습한다.</dd>
<dt>2바퀴</dt><dd>학습 자료 전체를 두 번 학습하는 것.</dd>
<dt>확신</dt><dd>모델이 고른 답에 매긴 확률(0~1).</dd>
<dt>자동 확정</dt><dd>사람 확인 없이 모델 답을 그대로 쓰는 것. 확신이 정한 기준보다 높을 때만 한다.</dd>
<dt>277문항</dt><dd>처음부터 쓴 시험(12000자 이하 문항). 학습에는 쓰지 않는다.</dd>
<dt>검증 세트</dt><dd>무엇을 고칠지, 새 버전을 쓸지 정할 때 쓰는 문항.</dd>
<dt>최종 시험</dt><dd>마지막에 한 번만 푸는 문항. Jev도 같은 문항을 푼다.</dd>
<dt>두 번째 독자</dt><dd>첫 라벨을 보지 않고 같은 문항에 따로 답하는 모델. 두 답이 같은 문항만 쓴다.</dd>
</dl>
</section>
"""


def _metrics_block(ms, val, ids, full_ids):
    """판별 지표: 정답률, 매크로 F1, 예/아니오 AUROC, 확신값 AUROC, 과제별 F1. ms = (이름, 결과, 색, 학습 여부)."""
    from compare_eval import metrics
    names = {'asset': '자산', 'R08': 'R08', 'R11_broad': 'R11 넓게', 'R11_narrow': 'R11 좁게', 'R12': 'R12', 'R14': 'R14', 'R15': 'R15'}
    dot = lambda col: f'<span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{col};margin-right:6px"></span>'
    f3 = lambda v: '-' if v is None else f'{v:.3f}'
    def table(qs):
        trs = ''
        for nm, m, col, _ in ms:
            x = metrics(m, val, qs)
            hi = [q for q in qs if q in m and (m[q]['conf'] or 0) >= 0.95]
            hw = sum(m[q]['pred'] != val[q]['gold'] for q in hi)
            trs += (f'<tr><td class="rw">{dot(col)}{E(nm)}</td><td class="c">{x["acc"]:.3f}</td><td class="c"><b>{x["f1"]:.3f}</b></td>'
                    f'<td class="c">{f3(x["auc_yn"])}</td><td class="c">{f3(x["auc_conf"])}</td><td class="c">{100 * hw / max(1, len(hi)):.1f}%</td></tr>')
        return ('<div class="tw"><table class="mx"><tr><th>누가</th><th class="c">정답률</th><th class="c">매크로 F1</th><th class="c">예/아니오 AUROC</th>'
                '<th class="c">확신값 AUROC</th><th class="c">확신 0.95 이상 오답 비율</th></tr>' + trs + '</table></div>')
    X = [(nm, metrics(m, val, ids), col) for nm, m, col, _ in ms]
    b1 = _bars([(nm, x['f1'], f'{x["f1"]:.3f}', col) for nm, x, col in X], 0.7, 1.0, '매크로 F1, 축 0.7~1.0')
    b2 = _bars([(nm, x['auc_conf'], f'{x["auc_conf"]:.3f}', col) for nm, x, col in X], 0.5, 1.0, '확신값 AUROC, 축 0.5~1.0(0.5는 동전 던지기)')
    tasks = [t for t in names if any(val[q]['task'] == t for q in ids)]
    trs = ''.join(f'<tr><td class="rw">{dot(col)}{E(nm)}</td>' + ''.join(f'<td class="c">{x["f1_task"].get(t, 0):.2f}</td>' for t in tasks) + '</tr>' for nm, x, col in X)
    return (f'<h3>판별 지표(판단용 {len(ids)}문항)</h3>'
            '<dl class="def"><dt>매크로 F1</dt><dd>과제마다 답 종류별 F1(맞힌 것과 놓친 것을 함께 본 점수)을 평균하고, 과제끼리 다시 평균한다. 드문 답을 놓치면 정답률보다 크게 떨어진다.</dd>'
            '<dt>예/아니오 AUROC</dt><dd>모델이 낸 \'예\' 확률로 정답이 예인 문항과 아니오인 문항을 얼마나 잘 가르는지. 1이면 모두 가르고 0.5면 동전 던지기와 같다.</dd>'
            '<dt>확신값 AUROC</dt><dd>확신이 높은 답일수록 맞는지. 높을수록 확신값으로 자동 확정과 사람 확인을 가르기 좋다.</dd></dl>'
            f'<div class="two"><div class="chart"><h4>매크로 F1</h4><p class="sub">높을수록 좋다</p>{b1}</div>'
            f'<div class="chart"><h4>확신값 AUROC</h4><p class="sub">높을수록 확신값을 믿을 만하다</p>{b2}</div></div>'
            + table(ids) +
            '<p class="cav">AUROC는 확신값 전체 범위의 순서를 본다. 자동 확정은 0.95 이상 구간만 쓰므로 두 결과가 다를 수 있다.</p>'
            '<div class="tw"><table class="mx"><tr><th>과제별 F1</th>' + ''.join(f'<th class="c">{names[t]}</th>' for t in tasks) + '</tr>' + trs + '</table></div>'
            f'<details><summary>검증 전체 {len(full_ids)}문항 기준</summary>{table(full_ids)}</details>')


def _audit_block(sets):
    """시험지 점검: 검증 세트와 최종 시험이 실제 문서로 잘 만들어졌는지. 라벨은 고치지 않고 센 값만."""
    kw = re.compile(r'grand total|total supply|across (the )?(blockchains|chains)|per chain|by chain|network\s*\|', re.I)
    H = re.compile(r'[가-힣]')
    st = {}
    for n, lab in (('valid', '검증'), ('final', '최종')):
        rs = list(sets[n].values()); N = len(rs)
        iss = collections.Counter((r.get('source') or {}).get('issuer') for r in rs)
        r11 = [r for r in rs if r['task'] in ('R11_broad', 'R11_narrow')]
        a = [r for r in rs if r['task'] == 'asset']
        st[n] = {'lab': lab, 'N': N, 'url': sum(bool((r.get('source') or {}).get('url')) for r in rs), 'iss': len(iss),
                 'top3': sum(v for _, v in iss.most_common(3)), 'top': iss.most_common(1)[0],
                 'uns': sum(bool(r.get('second_unsure')) for r in rs), 'r11': len(r11), 'r11c': sum(bool(kw.search(r['state'].get('text', ''))) for r in r11),
                 'a': len(a), 'an': sum('notes' not in r['state'] for r in a), 'ko': sum(len(H.findall(json.dumps(r['state'], ensure_ascii=False))) > 50 for r in rs)}
    V, F = st['valid'], st['final']
    pc = lambda a, b: 100 * a / max(1, b)
    g, b = '#8c8c87', '#2a78d6'
    def pair(title, sub, fv, ff, tv, tf, hv=None, hf=None):  # hv, hf: 고칠 쪽 표시(없으면 40% 이상)
        hv = fv >= 40 if hv is None else hv; hf = ff >= 40 if hf is None else hf
        return (f'<div class="chart"><h4>{title}</h4><p class="sub">{sub}</p>'
                + _bars([('검증', fv, tv, b if hv else g), ('최종', ff, tf, b if hf else g)], 0, 100, '막대는 비율(%). 파란 막대는 고칠 필요가 큰 쪽') + '</div>')
    charts = ('<div class="two">'
              + pair('발행사 쏠림', '가장 큰 세 곳이 차지하는 비율. 한 곳이 30%를 넘으면 파랑', pc(V['top3'], V['N']), pc(F['top3'], F['N']),
                     f"{pc(V['top3'], V['N']):.0f}%(가장 큰 곳 {V['top'][0][:10]} {pc(V['top'][1], V['N']):.0f}%)", f"{pc(F['top3'], F['N']):.0f}%(가장 큰 곳 {F['top'][0][:10]} {pc(F['top'][1], F['N']):.0f}%)",
                     pc(V['top'][1], V['N']) >= 30, pc(F['top'][1], F['N']) >= 30)
              + pair('애매한 문항', '두 번째 독자가 애매하다고 표시한 비율', pc(V['uns'], V['N']), pc(F['uns'], F['N']),
                     f"{V['uns']}/{V['N']}", f"{F['uns']}/{F['N']}")
              + pair('정하지 않은 기준에 걸린 R11', 'R11 문항 중 체인별 합계 표현이 있는 비율', pc(V['r11c'], V['r11']), pc(F['r11c'], F['r11']),
                     f"{V['r11c']}/{V['r11']}", f"{F['r11c']}/{F['r11']}")
              + pair('각주가 없는 자산 줄', '자산 문항 중 줄 설명(notes)이 없는 비율', pc(V['an'], V['a']), pc(F['an'], F['a']),
                     f"{V['an']}/{V['a']}", f"{F['an']}/{F['a']}")
              + '</div>')
    ok = (f'<ul><li><b>실제 문서:</b> {V["N"] + F["N"]}문항 모두 출처 주소가 있다({V["url"] + F["url"]}개). 지어낸 문항은 없다.</li>'
          f'<li><b>오염 없음:</b> 처음 시험과 겹치는 문항을 미리 뺐고, 검증({V["iss"]}곳)과 최종({F["iss"]}곳)은 발행사가 겹치지 않는다.</li>'
          f'<li><b>한국어:</b> 검증 {V["ko"]}문항, 최종 {F["ko"]}문항뿐이다.</li></ul>')
    steps = ('<div class="tl"><div class="A" style="flex:1">1. 체인별 합계 기준 정하기</div><div class="B" style="flex:1">2. 검증 보충(새 회사)</div>'
             '<div class="B" style="flex:1">3. 최종 시험 자산 점검</div><div class="B" style="flex:1">4. 한국어 검증 따로</div></div>'
             '<div class="tll"><span style="flex:1">검증 R11 대부분이 여기에 달림 <span class="tbd">미정</span></span><span style="flex:1">BRLA 쏠림 줄이기</span>'
             '<span style="flex:1">각주 찾아 넣고, 애매한 문항은 기존 라벨 안 보고 다시 판정</span><span style="flex:1">DART 감사보고서 75건</span></div>')
    return ('<h3>시험지 점검(검증 세트, 최종 시험)</h3><p class="sub">라벨은 고치지 않고 센 값이다. 모델 점수를 보지 않고 할 수 있는 점검이다.</p>'
            + ok + charts + '<h4>고칠 순서</h4>' + steps)


def _syn_effect():
    """Kanana 합성 B가 오른 까닭: 합성 없는 ft3와 문항 단위로 비교하고, 합성 자료가 시험과 겹치는지 센다."""
    fa, fb = FT / 'runs/desktop/evalset_kanana-ft3.jsonl', FT / 'runs/desktop/evalset_kanana-synB.jsonl'
    if not (fa.exists() and fb.exists() and (FT / 'sets/syn_v1.jsonl').exists()):
        return ''
    val = {r['id']: r for r in jl(FT / 'sets/valid_v3.jsonl')}
    A, B = _byid(fa), _byid(fb)
    ids = [q for q in val if q in A and q in B]
    up, dn = collections.Counter(), collections.Counter()
    for q in ids:
        k = val[q]['task']
        up[k] += bool(B[q]['correct']) and not A[q]['correct']
        dn[k] += bool(A[q]['correct']) and not B[q]['correct']
    syn = jl(FT / 'sets/syn_v1.jsonl')
    covered = collections.Counter(r['task'] for r in syn)
    names = {'asset': '자산 줄', 'R08': 'R08 검증 종류', 'R11_broad': 'R11 넓게', 'R11_narrow': 'R11 좁게', 'R12': 'R12 보관 기관', 'R14': 'R14 이자 없음', 'R15': 'R15 경영진 서명'}
    trs = ''
    for t, nm in names.items():
        c = f'{CHIP["syn"]} {covered[t]}개' if covered[t] else '<span style="color:var(--ink-3)">없음</span>'
        trs += f'<tr><td class="rw">{nm}</td><td class="c">{c}</td><td class="c"><b>+{up[t]}</b></td><td class="c">−{dn[t]}</td></tr>'
    yn = lambda M: sum(1 for q in ids if val[q]['gold'] == 'false' and val[q]['task'] in covered and M[q]['pred'] == 'true')
    # 겹침 검사: 합성 재료 발행사, 넣은 문장이 시험 문서에 있는지
    items = {r['id']: r for f in ('items/rep-a.jsonl', 'items/rep-b.jsonl', 'items/rep-c.jsonl', 'items/terms.jsonl') for r in jl(FT / f)}
    fin = jl(FT / 'sets/final_v1.jsonl')
    si = {(items[r['from']].get('source') or {}).get('issuer') for r in syn if r.get('from') in items}
    ei = {(r.get('source') or {}).get('issuer') for r in list(val.values()) + fin}
    norm = lambda x: re.sub(r'\s+', ' ', x).lower()
    vt = ' '.join(norm(r['state'].get('text', '')) for r in list(val.values()) + fin)
    pieces = [norm(x) for r in syn for x in re.split(r'\n…\n|\n', (r.get('edit') or {}).get('added') or '') if len(x.strip()) >= 60]
    hit = sum(1 for x in pieces if x in vt)
    return (f'<h3>Kanana 합성 B가 오른 까닭 {CHIP["real"]}{CHIP["syn"]}</h3><p class="sub">합성 없는 ft3(실제 v3만)와 같은 검증 문항 {len(ids)}개를 하나씩 비교했다</p>'
            '<div class="tw"><table class="mx"><tr><th>과제</th><th class="c">합성 자료가 다룬 곳</th><th class="c">새로 맞힘</th><th class="c">새로 틀림</th></tr>' + trs + '</table></div>'
            f'<ul><li><b>합성이 다룬 과제에서 올랐다.</b> 합성이 없는 자산 줄에서는 오히려 {dn["asset"]}개를 새로 틀렸다.</li>'
            f'<li><b>예로 답하는 쏠림이 줄었다.</b> 정답이 아니오인데 예로 답한 문항이 {yn(A)}개에서 {yn(B)}개로 줄었다. 합성이 "근거 문장이 있으면 예, 없으면 아니오" 짝을 가르친 결과로 본다.</li>'
            f'<li><b>시험지와 겹침 검사:</b> 합성 재료 발행사 {len(si)}곳 가운데 시험 발행사와 겹친 곳 {len(si & ei)}곳, 넣은 문장 {len(pieces)}개 가운데 시험 문서에 그대로 있는 문장 {hit}개.</li>'
            '<li><b>남는 의심:</b> 시험지 라벨과 합성 자료는 같은 판정 기준(관례집)에서 나왔다. 그래서 오른 것은 "우리 기준에 더 잘 맞게 판정한다"는 뜻이다. 한 번의 학습 결과이므로 Gemma에서 같은 비교로 확인한다.</li></ul>')


def evalsets_section():
    """검증 세트와 최종 시험 구성, 그리고 지금까지 푼 결과(Jev, 모델)."""
    sp = FT / 'sets' / 'eval_split.json'
    if not sp.exists():
        return ''
    split = json.loads(sp.read_text(encoding='utf-8'))
    sets = {n: {r['id']: r for r in jl(FT / 'sets' / f'{f}.jsonl')} for n, f in (('valid', 'valid_v3'), ('final', 'final_v1'))}
    comp = ''
    for n, lab, use in (('valid', '검증 세트', '무엇을 고칠지, 새 버전을 쓸지, 자동 확정 기준, 긴 문서 규칙을 정할 때'),
                        ('final', '최종 시험', '마지막에 한 번. Jev와 같이 풀어 목표에 닿았는지 판정')):
        d = split[n]
        comp += (f'<tr><td class="rw">{lab}</td><td class="c">{len(split[n + "_issuers"])}곳</td><td class="c">{sum(d["short"].values())}</td>'
                 f'<td class="c">{d["long"]}</td><td>{use}</td></tr>')
    runs = [('Jev', FT / 'results_jev_eval.jsonl', BRAND['jev']), ('OpenAI Decisions', FT / 'results_openai_decisions.jsonl', BRAND['decisions'])]
    for key, nm in (('gemma', 'Gemma'), ('kanana', 'Kanana'), ('gptoss', 'GPT-OSS')):
        for f in sorted((FT / 'runs').glob(f'*/evalset_{key}*.jsonl')):
            runs.append((f'{nm}({f.stem.split("_", 1)[1]})', f, BRAND[key]))
    res = ''
    for key, nm in (('gemma', 'Gemma(gemma-ft3)'), ('kanana', 'Kanana(kanana-ft2)')):
        if not any((FT / 'runs').glob(f'*/evalset_{key}*.jsonl')):
            res += (f'<tr><td class="rw"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{BRAND[key]};margin-right:6px"></span>{nm}</td>'
                    '<td class="c" colspan="2">아직 안 풂(데스크톱 꾸러미 실행 대기)</td><td class="c" colspan="2">마지막에 한 번</td></tr>')
    for nm, f, col in runs:
        rs = {r['id']: r for r in jl(f) if 'pred' in r}
        cells = ''
        for n in ('valid', 'final'):
            for lg in (False, True):
                ids = [q for q, it in sets[n].items() if bool(it.get('long')) == lg]
                d = [rs[q] for q in ids if q in rs]
                cells += f'<td class="c">{sum(bool(r["correct"]) for r in d)}/{len(d)}</td>' if d else '<td class="c">-</td>'
        res += f'<tr><td class="rw"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{col};margin-right:6px"></span>{E(nm)}</td>{cells}</tr>'
    # 판단용 문항(결과 보기 전에 고정한 sets/eval_subsets.json): Jev는 10회 다수결, 학습 모델은 발행사 하나씩 빼는 교차 보정 뒤 확신
    judge = ''
    evf = sorted(f for f in (FT / 'runs').glob('*/evalset_*.jsonl') if not f.name.startswith('evalset_c_'))  # evalset_c_는 검증 보충용
    if evf and (FT / 'sets/eval_subsets.json').exists():
        sys.path.insert(0, str(FT / 'tools'))
        from compare_eval import jev_majority, dec_majority, cv_conf
        val = sets['valid']
        ids = json.loads((FT / 'sets/eval_subsets.json').read_text(encoding='utf-8'))['valid_capped']
        ms = [('Jev(10회 다수결)', jev_majority(val), BRAND['jev'], False),
              ('OpenAI Decisions(10회 다수결)', dec_majority(val), BRAND['decisions'], False)]
        for f in evf:
            key = next(k for k in ('gemma', 'kanana', 'gptoss') if f.stem.split('_', 1)[1].startswith(k))
            ms.append((f'{GROWTH_NAMES[key]}({f.stem.split("_", 1)[1]})', _byid(f), BRAND[key], True))
        jtot = sum(bool(ms[0][1][q]['correct']) for q in ids)
        trs, bars, st = '', [], {}
        for nm, m, col, trained in ms:
            sh = [q for q in ids if not val[q].get('long') and q in m]
            lg = [q for q in ids if val[q].get('long') and q in m]
            c = lambda qs: sum(bool(m[q]['correct']) for q in qs)
            tot = c(sh) + c(lg)
            hi = [q for q in ids if q in m and m[q]['conf'] >= 0.95]
            yn = [q for q in sh if val[q]['gold'] in ('true', 'false') and not m[q]['correct']]
            fy = sum(val[q]['gold'] == 'false' for q in yn)
            auto = '-'
            if trained:
                cal = cv_conf(m, val, ids)
                a = [q for q in cal if cal[q] >= 0.99]
                auto = f'{sum(not m[q]["correct"] for q in a)}/{len(a)}'
            dot = f'<span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{col};margin-right:6px"></span>'
            kc = CHIP['real'] + CHIP['syn'] if 'synB' in nm else (CHIP['real'] if trained else CHIP['none'])
            trs += (f'<tr><td class="rw">{dot}{E(nm)}{kc}</td><td class="c">{c(sh)}/{len(sh)}</td><td class="c">{c(lg)}/{len(lg)}</td>'
                    f'<td class="c"><b>{tot}/{len(sh) + len(lg)}</b></td><td class="c">{tot - jtot:+d}</td>'
                    f'<td class="c">{sum(not m[q]["correct"] for q in hi)}/{len(hi)}</td><td class="c">{auto}</td><td class="c">{fy} / {len(yn) - fy}</td></tr>')
            bars.append((nm, 100 * tot / len(ids), f'{tot}/{len(ids)}', SYN_STRIPE if 'synB' in nm else col))
            st[nm.split('(')[-1].rstrip(')') if trained else nm.split('(')[0]] = {'tot': tot, 'fy': fy, 'yn': len(yn), 'auto': auto, 'hi': (sum(not m[q]['correct'] for q in hi), len(hi))}
        notes = ''
        g, k2, k3 = st.get('gemma-ft3'), st.get('kanana-ft2'), st.get('kanana-ft3')
        if g:
            notes += (f'<li><b>Gemma 1차는 Jev보다 {jtot - g["tot"]}개 적다.</b> 확신값을 보정하면 0.99 이상 자동 확정 {g["auto"].split("/")[1]}개 중 오답 {g["auto"].split("/")[0]}개다'
                      f'(Jev는 0.95 이상 {st["Jev"]["hi"][1]}개 중 오답 {st["Jev"]["hi"][0]}개). 자동으로 넘기는 문항은 Jev보다 적다.</li>')
        if k2 and k3:
            r2, r3 = (sum(bool(x['correct']) for x in _byid(f).values()) for f in (FT / 'runs/colab2/results_kanana-ft2.jsonl', FT / 'runs/desktop/results_kanana-ft3.jsonl'))
            notes += (f'<li><b>Kanana 2차는 1차와 같은 {k3["tot"]}개다.</b> 277문항에서는 {r2}개에서 {r3}개로 올랐지만 처음 보는 문서에서는 오르지 않았다. '
                      '277문항의 몇 개 차이는 흔들림 범위로 본다.</li>')
        sb = st.get('kanana-synB')
        if sb:
            notes += (f'<li><b>Kanana 합성 B는 {sb["tot"]}개로 Jev와 {"같다" if sb["tot"] == jtot else f"{abs(sb[chr(116)+chr(111)+chr(116)] - jtot)}개 차이다"}.</b> '
                      f'실제 v3에 합성 자료를 더한 학습이고, 실제 v3만 쓴 2차({k3["tot"] if k3 else "-"}개)보다 올랐다. 확신 0.95 이상 오답은 {sb["hi"][0]}/{sb["hi"][1]}로 Jev({st["Jev"]["hi"][0]}/{st["Jev"]["hi"][1]})보다 많다.</li>')
        if g and k3:
            v4 = collections.Counter((r['task'], r['gold']) for r in jl(FT / 'sets/train_v4.jsonl'))
            notes += (f'<li><b>예/아니오 오답은 대부분 아니오를 예로 답한 것이다</b>(Gemma 1차 {g["fy"]}/{g["yn"]}, Kanana 2차 {k3["fy"]}/{k3["yn"]}). '
                      f'다음 학습 자료 v4도 예 쪽으로 쏠려 있어(R11 넓게 예 {v4[("R11_broad", "true")]}, 아니오 {v4[("R11_broad", "false")]} / '
                      f'R15 예 {v4[("R15", "true")]}, 아니오 {v4[("R15", "false")]}) 균형을 맞춘 뒤 학습한다.</li>')
        judge = (f'<h3>판단용 {len(ids)}문항 비교</h3><p class="sub">발행사당 월 보고서 6건까지, 섞인 합계 줄 제외. 결과를 보기 전에 정한 기준</p>'
                 + '<div class="chart">' + _bars(bars, 80, 95, '정답 비율, 축 80~95%') + '</div>'
                 + '<div class="tw"><table class="mx"><tr><th>누가</th><th class="c">12000자 이하</th><th class="c">긴 문서</th><th class="c">합계</th><th class="c">Jev와 차이</th>'
                 '<th class="c">확신 0.95 이상 오답</th><th class="c">보정 뒤 0.99 이상 오답</th><th class="c">예/아니오 오답 방향<br>(아니오→예 / 예→아니오)</th></tr>'
                 + trs + '</table></div>'
                 '<p class="cav">보정은 발행사 하나를 빼고 나머지로 확신값을 맞춘 뒤 뺀 발행사에 적용해 잰다. Jev, Decisions는 보정하지 않는다.</p>'
                 + (f'<ul>{notes}</ul>' if notes else '')
                 + _metrics_block(ms, val, ids, json.loads((FT / 'sets/eval_subsets.json').read_text(encoding='utf-8'))['valid_full'])
                 + _syn_effect())
    return f"""<section id="s4"><h2>4. 검증 세트와 최종 시험</h2>
<p>시험과 학습에 없던 발행사 문서로 새로 만든 문항. 검증 세트로 판단하고, 최종 시험은 마지막에 한 번 본다.</p>
<div class="tw"><table class="mx"><tr><th>구분</th><th class="c">발행사</th><th class="c">12000자 이하 문항</th><th class="c">긴 문서 문항</th><th>쓰는 때</th></tr>{comp}</table></div>
{_audit_block(sets)}
<h3>푼 결과(맞힌 수/푼 수)</h3>
<div class="tw"><table class="mx"><tr><th>누가</th><th class="c">검증, 12000자 이하</th><th class="c">검증, 긴 문서</th><th class="c">최종, 12000자 이하</th><th class="c">최종, 긴 문서</th></tr>{res}</table></div>
<p class="cav">긴 문서는 Jev는 통째로, 우리 모델은 조각으로 나눠 푼다.</p>
{judge}
{_rep_section()}
</section>
"""


CONTRIB_DONE = [  # (큰 숫자, 제목, 근거 한 줄)
    ('+7, +24', '무료 GPU(T4)에서 파인튜닝', 'QLoRA로 Gemma 252 → 259, Kanana 214 → 238(277문항, Jev 264)'),
    ('4묶음 분리', '시험 오염을 막은 학습 자료', '시험, 학습, 검증, 최종 시험의 발행사를 서로 나눔. 두 독자(Sonnet, Opus)가 일치한 라벨만 씀'),
    ('1.4%', '두 모델 서로 검산', 'Gemma와 Kanana가 같은 답일 때만 자동 확정: 213개 중 오답 3. Jev는 152개 중 2(1.3%)'),
    ('200억', '큰 모델을 무료 GPU에서 학습', 'GPT-OSS-20B를 조각 계산과 메모리 넘기기로 문항 하나도 빼지 않고 학습(110/256단계까지)'),
    ('0개', 'Jev 반복 측정', '10번 돌려 확신 0.95 이상 답 가운데 바뀐 답 0개. 점수 흔들림 0.8%p'),
]
CONTRIB_NEXT = [  # (순서, 이름, 표시, 내용)
    ('1', 'GGUF 내보내기', '먼저', '인터넷 없이 도는 파일로 만들어 은행 내부망 판(PRD X8)에 쓴다. 두 모델 다 llama.cpp가 지원한다(Kanana는 Llama 구조, Gemma 4 E4B는 공식 GGUF 있음). 우리 학습 결과는 따로 GGUF로 바꿔 얹거나 합쳐서 변환하고, 변환 뒤 다시 채점한다.'),
    ('2', '비전 파인튜닝', '큰 작업', '스캔 PDF(이번에 빠진 문서 22건 등)를 그림째 읽게 한다. Gemma 4 E4B는 그림을 받는다.'),
    ('3', 'GRPO(강화학습)', '뒤로', '점수 함수는 쉽지만 지금 학습보다 나을지 모르고 GPU가 많이 든다.'),
    ('-', 'DPO, 계속 사전학습, TTS', '해당 없음', '쓸 자리가 없다.'),
]


def contrib_section():
    done = ''.join(f'<div class="kc"><div class="kv">{E(v)}</div><b>{E(t)}</b><p>{E(d)}</p></div>' for v, t, d in CONTRIB_DONE)
    nxt = ''.join(f'<li><span class="kn">{E(n)}</span><div><b>{E(t)}</b> <span class="tag{" a" if g == "먼저" else ""}">{E(g)}</span><p>{E(d)}</p></div></li>'
                  for n, t, g, d in CONTRIB_NEXT)
    return f"""<section id="s8"><h2>8. 기술적 기여와 다음 개발</h2>
<h3>이미 해서 숫자가 있는 것</h3>
<div class="kcards">{done}</div>

<h3>다음 개발 후보</h3>
<ol class="knext">{nxt}</ol>
</section>
"""


# 판별 성장 기록. (판 이름, 날짜, 학습 자료, 277 결과 파일, 검증 세트 결과 파일, 학습 단계 기록)
GROWTH = {
    'gemma': [('학습 전', '10/11', '-', FT / 'results_gemma_base_t4.jsonl', None, None),
              ('1차(gemma-ft3)', '10/11', 'v2 1,025문항, 2바퀴', FT / 'runs/colab3/results_gemma-ft3.jsonl', FT / 'runs/desktop/evalset_gemma-ft3.jsonl', None),
              ('2차(gemma-ft4)', '진행', 'v3 1,049문항, 2바퀴', FT / 'runs/colab3/results_gemma-ft4.jsonl', None, FT / 'runs/colab3/steps_gemma-ft4.log')],
    'kanana': [('학습 전', '10/11', '-', FT / 'results_kanana_base_t4.jsonl', None, None),
               ('맛보기(kanana-ft0)', '10/11', '첫 라벨만 453문항', FT / 'runs/colab2/results_kanana-ft0.jsonl', None, None),
               ('1차(kanana-ft2)', '10/11', 'v2 1,025문항, 2바퀴', FT / 'runs/colab2/results_kanana-ft2.jsonl', FT / 'runs/desktop/evalset_kanana-ft2.jsonl', None),
               ('2차(kanana-ft3)', '진행', 'v3 1,049문항, 2바퀴', FT / 'runs/desktop/results_kanana-ft3.jsonl', FT / 'runs/desktop/evalset_kanana-ft3.jsonl', FT / 'runs/desktop/steps_kanana-ft3.log'),
               ('합성 B(kanana-synB)', '10/15', '실제 v3 + 합성 186, 2바퀴', FT / 'runs/desktop/results_kanana-synB.jsonl', FT / 'runs/desktop/evalset_kanana-synB.jsonl', FT / 'runs/desktop/steps_kanana-synB.log')],
    'gptoss': [('학습 전', '10/11', '-', FT / 'runs/colab4/results_gptoss_direct_base.jsonl', None, None),
               ('1차(gptoss-ft2)', '진행', 'v2 1,025문항, 2바퀴', FT / 'runs/colab4/results_gptoss-ft2.jsonl', None, FT / 'runs/colab4/steps_gptoss-ft2.log')],
}
GROWTH_NAMES = {'gemma': 'Gemma 4 E4B', 'kanana': 'Kanana 1.5 8B', 'gptoss': 'GPT-OSS-20B'}
GROWTH_CO = {'gemma': 'Google', 'kanana': '카카오', 'gptoss': 'OpenAI'}


def _grp(key, name, co, span):
    """표 안 모델 묶음 머리 줄: 로고, 이름, 회사, 브랜드 색 띠."""
    col = BRAND[key]
    img = logo(key).replace('<img ', '<img style="width:20px;height:20px;border-radius:5px;object-fit:contain;vertical-align:-5px;margin-right:8px" ')
    return (f'<tr><td colspan="{span}" style="border-left:5px solid {col};background:{col}1f;padding:9px 12px">'
            f'{img}<b>{E(name)}</b><span style="margin-left:10px;font-size:12.5px;color:var(--ink-3)">{E(co)}</span></td></tr>')


def _ver(key, label):
    """판 이름 칸: 브랜드 색 세로줄 + 판 이름 + 어댑터 이름."""
    nm, tag = (label.split('(')[0], label.split('(')[1].rstrip(')')) if '(' in label else (label, '')
    t = f'<span style="display:block;font-size:12px;color:var(--ink-3)">{E(tag)}</span>' if tag else ''
    return f'<td class="rw" style="border-left:5px solid {BRAND[key]};padding-left:12px">{E(nm)}{t}</td>'


KNOWN_CAUSE = {('gemma', 'R11_broad'): '학습 자료의 R11 넓게가 예 44, 아니오 12로 쏠려 있었다(v3, v4에서 보강)'}


def growth_section(jev):
    jc = sum(bool(v['correct']) for v in jev.values())
    sys.path.insert(0, str(FT / 'tools'))
    from compare_eval import metrics
    def fa(rows, meta=None):  # 277문항 매크로 F1과 확신값 AUROC 칸 두 개
        meta = meta or {q: {'task': x['task'], 'gold': x['gold']} for q, x in rows.items()}
        x = metrics(rows, meta, list(rows))
        return f'<td class="c">{x["f1"]:.3f}</td><td class="c">{x["auc_conf"]:.3f}</td>'
    names = {'asset': '자산 종류', 'R14': 'R14 이자 없음', 'R08': 'R08 검증 종류', 'R11_broad': 'R11 넓게', 'R11_narrow': 'R11 좁게', 'R12': 'R12 보관 기관', 'R15': 'R15 경영진 서명'}
    # 1) 판별 정답 수 선 그래프(277문항)
    lo, hi_ = 190, TOTAL
    stages = ['학습 전', '맛보기', '1차', '2차', '합성 B']
    X = lambda i: 70 + 420 * i / (len(stages) - 1)
    Y = lambda v: 230 - 200 * (v - lo) / (hi_ - lo)
    svg = ['<svg viewBox="0 0 600 270" style="max-width:600px;width:100%" role="img" aria-label="판별 정답 수">',
           f'<line x1="60" y1="{Y(jc):.1f}" x2="500" y2="{Y(jc):.1f}" stroke="{BRAND["jev"]}" stroke-width="2"/>'
           f'<text x="504" y="{Y(jc) + 4:.1f}" font-size="12" fill="{BRAND["jev"]}">Jev {jc}</text>']
    D = _dec277()
    if D:
        dcn = sum(bool(x['correct']) for x in D.values())
        svg.append(f'<line x1="60" y1="{Y(dcn):.1f}" x2="500" y2="{Y(dcn):.1f}" stroke="{BRAND["decisions"]}" stroke-width="2" stroke-dasharray="6 4"/>'
                   f'<text x="504" y="{Y(dcn) + 4:.1f}" font-size="12" fill="{BRAND["decisions"]}">Decisions {dcn}</text>')
    for i, st in enumerate(stages):
        svg.append(f'<text x="{X(i):.1f}" y="262" font-size="12" text-anchor="middle" fill="#555">{st}</text>')
    rows, quali = '', ''
    for key, vers in GROWTH.items():
        pts, prev, base = [], None, None
        rows += _grp(key, GROWTH_NAMES[key], GROWTH_CO[key], 9)
        q_rows = ''
        for label, date, data, f, vf, sf in vers:
            r = _byid(f) if pathlib.Path(f).exists() and len(jl(f)) >= 324 else None
            if not r:
                stop = sf.parent / sf.name.replace('steps_', 'stopped_').replace('.log', '.txt') if sf else None
                e = _steps_eta(sf) if sf else None
                st = (stop.read_text(encoding='utf-8').split(',')[0].strip() if stop and stop.exists()
                      else f'학습 중 {e[0]}/{e[1]}단계' if e and e[0] < e[1] else '학습 끝, 재시험 중' if e else '아직 결과 없음')
                rows += f'<tr>{_ver(key, label)}<td>{E(data)}</td><td class="c" colspan="7" style="color:var(--ink-3)">{E(st)}</td></tr>'
                continue
            c = sum(bool(x['correct']) for x in r.values())
            hi = [x for x in r.values() if x['conf'] >= 0.95]
            wrong = TOTAL - c
            if base is None:
                base = (r, c)
            d_prev = f'{c - prev[1]:+d}' if prev else '-'
            err_cut = f'{100 * ((TOTAL - base[1]) - wrong) / (TOTAL - base[1]):.0f}%' if prev else '-'
            gap_cut = f'{100 * ((jc - base[1]) - (jc - c)) / (jc - base[1]):.0f}%' if prev and jc > base[1] else '-'
            vtxt = '-'
            if vf and pathlib.Path(vf).exists():
                vr = [x for x in jl(vf) if 'pred' in x]
                vtxt = f"{sum(bool(x['correct']) for x in vr)}/{len(vr)}"
            rows += (f'<tr>{_ver(key, label)}<td>{E(data)}{data_chips(label)}</td><td class="c"><b>{c}</b> ({d_prev})</td>'
                     f'<td class="c">{err_cut}</td><td class="c">{gap_cut}</td><td class="c">{sum(not x["correct"] for x in hi)}/{len(hi)}</td>{fa(r)}<td class="c">{vtxt}</td></tr>')
            si = next(i for i, sname in enumerate(stages) if label.startswith(sname))
            pts.append((si, c))
            if prev:  # 직전 판 대비 과제별로 새로 맞힘, 새로 틀림
                p_r = prev[0]
                cells = ''
                for t, tn in names.items():
                    qs = [q for q in r if r[q]['task'] == t and q in p_r]
                    up = sum(r[q]['correct'] and not p_r[q]['correct'] for q in qs)
                    dn = sum(not r[q]['correct'] and p_r[q]['correct'] for q in qs)
                    cells += f'<td class="c">+{up} / −{dn}</td>' if up or dn else '<td class="c">-</td>'
                q_rows += f'<tr>{_ver(key, prev[2].split("(")[0] + " → " + label)}{cells}</tr>'
                for t in names:
                    if (key, t) in KNOWN_CAUSE:
                        dn = [q for q in r if r[q]['task'] == t and q in p_r and not r[q]['correct'] and p_r[q]['correct']]
                        if dn:
                            q_rows += f'<tr><td colspan="8" style="font-size:13px;color:#555">{names[t]} 새로 틀린 {len(dn)}문항 원인: {KNOWN_CAUSE[(key, t)]}</td></tr>'
            prev = (r, c, label)
        if q_rows:
            quali += _grp(key, GROWTH_NAMES[key], GROWTH_CO[key], 8) + q_rows
        if pts:
            col = BRAND[key]
            real_pts = [(i, v) for i, v in pts if stages[i] != '합성 B']
            syn_pts = [(i, v) for i, v in pts if stages[i] == '합성 B']
            svg.append(f'<polyline points="{" ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in real_pts)}" fill="none" stroke="{col}" stroke-width="3"/>')
            if syn_pts and real_pts:  # 실제 자료만 쓴 마지막 점에서 합성 점까지는 보라 점선
                (i0, v0), (i1, v1) = real_pts[-1], syn_pts[0]
                svg.append(f'<line x1="{X(i0):.1f}" y1="{Y(v0):.1f}" x2="{X(i1):.1f}" y2="{Y(v1):.1f}" stroke="#8a63d2" stroke-width="3" stroke-dasharray="6 4"/>')
            for i, v in pts:
                is_syn = stages[i] == '합성 B'
                svg.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="{7 if is_syn else 6}" fill="{col}" stroke="{"#8a63d2" if is_syn else "#111"}" stroke-width="{3 if is_syn else (1 if key == "kanana" else 0)}"/>'
                           f'<text x="{X(i) + 9:.1f}" y="{Y(v) + 4:.1f}" font-size="12" font-weight="700" fill="#111">{v}</text>')
    svg.append(f'<text x="60" y="{Y(lo) + 14:.1f}" font-size="11" fill="#85857f">{lo}</text></svg>')
    rows += ('<tr><td colspan="9" style="border-left:5px solid #c9c9c4;background:#f4f4f2;padding:9px 12px"><b>비교 기준</b>'
             '<span style="margin-left:10px;font-size:12.5px;color:var(--ink-3)">학습하지 않는 외부 서비스</span></td></tr>')
    vset = {json.loads(l)['id'] for l in (FT / 'sets' / 'valid_v3.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()}
    ext = lambda key, nm: (f'<td class="rw" style="border-left:5px solid {BRAND[key]};padding-left:12px">'
                           + logo(key).replace('<img ', '<img style="width:18px;height:18px;border-radius:4px;object-fit:contain;vertical-align:-4px;margin-right:6px" ') + f'{nm}</td>')
    if D:
        dh = [x for x in D.values() if x['conf'] >= 0.95]
        vv = [x for x in jl(FT / 'results_openai_decisions.jsonl') if 'pred' in x and x['id'] in vset]
        rows += (f'<tr>{ext("decisions", "OpenAI Decisions API")}<td>gpt-6-luna</td><td class="c"><b>{dcn}</b></td><td class="c">-</td><td class="c">-</td>'
                 f'<td class="c">{sum(not x["correct"] for x in dh)}/{len(dh)}</td>{fa(D)}<td class="c">{sum(bool(x["correct"]) for x in vv)}/{len(vv)}</td></tr>')
    jvv = [x for x in jl(FT / 'results_jev_eval.jsonl') if 'pred' in x]
    if jvv:
        jvx = [x for x in jvv if x['id'] in vset]
        jhh = [v for v in jev.values() if v['conf'] >= 0.95]
        rows += (f'<tr class="me">{ext("jev", "Jev(목표)")}<td>jev-1.13.0</td><td class="c"><b>{jc}</b></td><td class="c">-</td><td class="c">-</td>'
                 f'<td class="c">{sum(not v["correct"] for v in jhh)}/{len(jhh)}</td>{fa(jev)}<td class="c">{sum(bool(x["correct"]) for x in jvx)}/{len(jvx)}</td></tr>')
    head = ''.join(f'<th class="c">{v}</th>' for v in names.values())
    return f"""<section id="s2"><h2>2. 성장 기록</h2>
<div class="two"><div class="chart"><h4>판별 정답 수(277문항)</h4><p class="sub">선 하나가 모델 하나. 분홍 선이 Jev, 초록 점선이 Decisions API(둘 다 학습 없음). 보라 점선과 보라 테두리는 합성 자료를 더한 학습</p>{''.join(svg)}</div>
<div class="chart"><h4>성장률 읽는 법</h4><dl class="def"><dt>오답 감소율</dt><dd>학습 전 오답 가운데 줄어든 비율</dd><dt>Jev 격차 축소</dt><dd>학습 전 Jev와의 차이 가운데 메운 비율</dd><dt>검증</dt><dd>처음 보는 문서 372문항(정답/푼 수)</dd></dl></div></div>
<div class="tw"><table class="mx"><tr><th>판</th><th>학습 자료</th><th class="c">277문항(직전 대비)</th><th class="c">오답 감소율</th><th class="c">Jev 격차 축소</th><th class="c">확신 0.95 이상 오답</th><th class="c">매크로 F1</th><th class="c">확신값 AUROC</th><th class="c">검증</th></tr>{rows}</table></div>
<h3>과제별로 바뀐 문항(직전 판 대비, 새로 맞힘 / 새로 틀림)</h3>
<div class="tw"><table class="mx"><tr><th>바뀐 판</th>{head}</tr>{quali}</table></div>
</section>
"""


EXT_FEATURES = [  # (항목, Jev, Decisions, 어느 쪽이 나은지)
    ('입력', '글', '글과 이미지(base64)', 'Decisions'),
    ('스캔 PDF, 그림 표, 그림 서명란 판정', '못 함(글만)', '그림째 판정 가능(시험 전)', 'Decisions'),
    ('답 종류', '예/아니오 확률, 보기, 점수', '예/아니오 확률, 보기, 점수', '같음'),
    ('한 요청에 여러 질문, 데이터 미보관', '됨', '됨', '같음'),
    ('가격(입력 100만 토큰)', '0.042달러', '0.10달러(약 2.4배)', 'Jev'),
    ('상태', '정식 서비스(jev-1.13.0 고정)', '공개 베타(10/6), 정식 출시 예고', 'Jev'),
    ('은행 내부망 설치', '모름(영업 문의)', '안 됨(외부 API)', '-'),
]


def _rep(files, allq, gold, groups):
    """같은 문항을 여러 번 푼 결과(다 푼 회차만): 회차별 점수, 다수결, 답이 바뀐 문항, 확신 0.95 이상인데 바뀐 문항."""
    jr = [d for d in ({r['id']: r for r in jl(f) if 'pred' in r} for f in files) if all(q in d for q in allq)]
    if not jr:
        return None
    preds = {q: [d[q]['pred'] for d in jr] for q in allq}
    flip = [q for q in allq if len(set(preds[q])) > 1]
    return {'k': len(jr), 'per': [[sum(bool(d[q]['correct']) for q in g) for d in jr] for g in groups],
            'mv': [sum(collections.Counter(preds[q]).most_common(1)[0][0] == gold[q] for q in g) for g in groups],
            'flip': flip, 'hiflip': [q for q in flip if any(d[q]['conf'] >= 0.95 for d in jr)],
            'hw': [sum(not d[q]['correct'] for q in allq if d[q]['conf'] >= 0.95) for d in jr],
            'hn': [sum(d[q]['conf'] >= 0.95 for q in allq) for d in jr]}


def _rep_section():
    """Jev 10회와 Decisions 10회 반복 비교(정답 수, 답 흔들림, 확신값). Decisions가 10회를 다 풀기 전에는 진행 상황을 함께 적는다."""
    sets = {n: {r['id']: r for r in jl(FT / 'sets' / f'{f}.jsonl')} for n, f in (('valid', 'valid_v3'), ('final', 'final_v1'))}
    groups = [[q for q, it in sets[n].items() if bool(it.get('long')) == lg] for n in ('valid', 'final') for lg in (False, True)]
    allq = [q for g in groups for q in g]
    gold = {q: it['gold'] for n in sets for q, it in sets[n].items()}
    dfiles = [FT / 'results_openai_decisions.jsonl'] + sorted(FT.glob('results_openai_decisions_r*.jsonl'), key=lambda f: int(f.stem.rsplit('_r', 1)[1]))
    J = _rep(sorted(FT.glob('results_jev_eval*.jsonl')), allq, gold, groups)
    D = _rep(dfiles, allq, gold, groups)
    if not (J and D):
        return ''
    rng = lambda xs: f'{min(xs)}' if min(xs) == max(xs) else f'{min(xs)}~{max(xs)}'
    trs = ''
    for nm, R, col in (('Jev', J, BRAND['jev']), ('Decisions', D, BRAND['decisions'])):
        dot = f'<span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{col};margin-right:6px"></span>'
        trs += (f'<tr><td class="rw" style="white-space:nowrap">{dot}{nm} {R["k"]}회 범위</td>' + ''.join(f'<td class="c">{rng(p)}/{len(g)}</td>' for p, g in zip(R['per'], groups))
                + f'<td class="c">{rng(R["hw"])}건({rng(R["hn"])}문항 중)</td><td class="c" rowspan="2"><b>{len(R["flip"])}</b></td><td class="c" rowspan="2"><b>{len(R["hiflip"])}</b></td></tr>'
                f'<tr><td class="rw" style="white-space:nowrap">{dot}{nm} 다수결</td>' + ''.join(f'<td class="c">{m}/{len(g)}</td>' for m, g in zip(R['mv'], groups)) + '<td class="c">-</td></tr>')
    names = {'asset': '자산 종류', 'R08': 'R08 검증 종류', 'R11_broad': 'R11 넓게', 'R11_narrow': 'R11 좁게', 'R12': 'R12 보관 기관', 'R15': 'R15 경영진 서명', 'R14': 'R14 이자 없음'}
    task = {q: it['task'] for n in sets for q, it in sets[n].items()}
    ft = lambda R: ', '.join(f'{names.get(t, t)} {c}' for t, c in collections.Counter(task[q] for q in R['flip']).most_common()) or '없음'
    tot = lambda R: sum(R['mv'])
    rate = lambda R: (100 * min(R['hw']) / max(R['hn']), 100 * max(R['hw']) / min(R['hn']))  # 회차별 확신 0.95 이상 오답 비율 범위
    rtxt = lambda R: f'{rate(R)[0]:.1f}%' if round(rate(R)[0], 1) == round(rate(R)[1], 1) else f'{rate(R)[0]:.1f}~{rate(R)[1]:.1f}%'
    b1 = _bars([('Jev', len(J['flip']), f'{len(J["flip"])}문항', BRAND['jev']), ('Decisions', len(D['flip']), f'{len(D["flip"])}문항', BRAND['decisions'])],
               0, max(len(J['flip']), len(D['flip']), 1) * 1.2, f'{len(allq)}문항 가운데 회차마다 답이 바뀐 문항 수')
    b2 = _bars([('Jev', rate(J)[1], rtxt(J), BRAND['jev']), ('Decisions', rate(D)[1], rtxt(D), BRAND['decisions'])],
               0, max(rate(J)[1], rate(D)[1]) * 1.2, '확신 0.95 이상으로 답한 문항 가운데 틀린 비율')
    b3 = _bars([('Jev', tot(J), f'{tot(J)}/{len(allq)}', BRAND['jev']), ('Decisions', tot(D), f'{tot(D)}/{len(allq)}', BRAND['decisions'])],
               len(allq) * 0.8, len(allq), f'{J["k"]}회 다수결 정답 수, 축 {int(len(allq) * 0.8)}~{len(allq)}')
    state = '' if D['k'] >= 10 else f' <span class="plan">진행 중 {D["k"]}/10회</span>'
    return (f'<h3>Jev {J["k"]}회와 Decisions {D["k"]}회 반복 비교(같은 {len(allq)}문항){state}</h3>'
            '<div class="three">'
            f'<div class="chart"><h4>정답 수</h4><p class="sub">회차별 다수결</p>{b3}</div>'
            f'<div class="chart"><h4>답이 바뀐 문항</h4><p class="sub">적을수록 같은 문서에 같은 답</p>{b1}</div>'
            f'<div class="chart"><h4>확신 높은데 틀린 비율</h4><p class="sub">낮을수록 자동 확정에 쓰기 좋다</p>{b2}</div></div>'
            '<div class="tw"><table class="mx"><tr><th>구분</th><th class="c">검증, 12000자 이하</th><th class="c">검증, 긴 문서</th><th class="c">최종, 12000자 이하</th>'
            '<th class="c">최종, 긴 문서</th><th class="c">확신 0.95 이상 오답</th><th class="c">답이 바뀐 문항</th><th class="c">그중 확신 0.95 이상이 나온 문항</th></tr>'
            + trs + '</table></div>'
            '<ul>'
            f'<li><b>정답 수는 Jev가 {tot(J) - tot(D)}개 많다</b>({tot(J)} 대 {tot(D)}). 긴 문서는 Decisions가 많이 맞혔다'
            f'({D["mv"][1] + D["mv"][3]} 대 {J["mv"][1] + J["mv"][3]}).</li>'
            f'<li><b>Decisions는 {D["k"]}번 모두 같은 답</b>을 냈다. Jev는 {len(J["flip"])}문항({ft(J)})이 회차마다 바뀌었고, 확신 0.95 이상이 나온 문항은 {len(J["hiflip"])}개였다.</li>'
            f'<li><b>확신값은 Jev가 더 믿을 만하다.</b> 확신 0.95 이상 가운데 틀린 비율이 Jev {rtxt(J)}, Decisions {rtxt(D)}다. Decisions는 확신 0.95 이상을 더 자주 낸다({rng(D["hn"])}문항 대 {rng(J["hn"])}문항).</li>'
            '</ul><p class="cav">위 푼 결과 표의 Jev 값은 1회차다.</p>')


OPEN_ALTS = [  # 공개 판정 모델(검토만 함): (이름, 바탕 모델, 외부 순위표 능력 점수, 안 고른 이유, 미정 여부)
    ('Quyet-1.0-Large', 'Gemma 4 31B, 보기 글자 확률로 답 읽기(우리와 같은 방식)', '81.7',
     '310억 매개변수라 4비트로 줄여도 무게만 약 16GB. 무료 T4(16GB)와 데스크톱(8GB)에 올라가지 않는다. 같은 방식이 Jev를 넘은 근거로만 쓴다', False),
    ('Gemma 4 12B 학습판(decider-12b, torchcast-12b)', 'Gemma 4 12B', '72.5, 71.7',
     '같은 계열의 더 작은 E4B를 직접 학습하고 있다. 12B로 바꿀지는 E4B 결과를 보고 정한다(무료 T4에서 학습되는지 확인 안 함)', True),
    ('Open-Jev 27B v1.1', 'Qwen 27B + LoRA + 판정 머리', '68.0',
     'Qwen 바탕. 자체 발표(Jev보다 3문항 앞섬)와 외부 점수가 다르다', False),
    ('Kev', 'Qwen3, Qwen3.5 + LoRA, 0.5B~27B', '4B 44.0, 27B 78.9(비용 상한 밖)', 'Qwen 바탕', False),
    ('SemIf(옛 이름 OpenJev)', 'Qwen3.5 4B', '55.4', 'Qwen 바탕, 점수가 낮다', False),
    ('CLM-8B(Stanford, Nvidia)', 'Qwen3 8B', '20.1', '빠르기(Jev의 최대 9배, 자체 발표)만 앞서고 정답률이 낮다. Qwen 바탕', False),
    ('EXAONE 4.0 1.2B 학습판(비공식)', 'LG EXAONE 4.0 1.2B', '47.7', '점수가 낮고 LG가 낸 판이 아니다', False),
    ('Laya(Convai)', 'ModernBERT 4억 2천만, Apache 2.0', '32.5(판정 전용판 44.2)',
     '한 번에 512토큰(판정 전용판 1,024)만 읽어 우리 문서를 잘게 잘라야 한다. 다국어판 점수 17.0. 작고 빨라 내부망에 올리기는 쉽다. 가볍게 시험해 볼지', True),
    ('NanoJev', '약 6억', '순위표에 없음', '확인된 성적이 없다', False),
]


def ext_section(jev):
    """외부 판정 서비스 비교: Jev와 OpenAI Decisions API. 표는 기능, 그림과 표는 같은 문항 점수."""
    d277 = _byid(FT / 'results_openai_decisions_277.jsonl') if len(jl(FT / 'results_openai_decisions_277.jsonl')) >= 277 else None
    feat = ''.join(f'<tr><td class="rw">{E(a)}</td><td>{E(b)}</td><td>{E(c)}</td><td class="c"><b>{E(w)}</b></td></tr>' for a, b, c, w in EXT_FEATURES)
    body = ''
    if d277:
        names = {'asset': '자산 종류', 'R14': 'R14 이자 없음', 'R08': 'R08 검증 종류', 'R11_broad': 'R11 넓게', 'R11_narrow': 'R11 좁게', 'R12': 'R12 보관 기관', 'R15': 'R15 경영진 서명'}
        ids = [q for q in jev if q in d277]
        jc = sum(bool(jev[q]['correct']) for q in ids); dc = sum(bool(d277[q]['correct']) for q in ids)
        only_d = [q for q in ids if d277[q]['correct'] and not jev[q]['correct']]
        only_j = [q for q in ids if jev[q]['correct'] and not d277[q]['correct']]
        jh = [q for q in ids if jev[q]['conf'] >= 0.95]; dh = [q for q in ids if d277[q]['conf'] >= 0.95]
        rows = [('Jev', jc, f'{jc} ({100 * jc / len(ids):.1f}%)', BRAND['jev']), ('Decisions API', dc, f'{dc} ({100 * dc / len(ids):.1f}%)', BRAND['decisions'])]
        c1 = ('<div class="chart"><h4>277문항 정답 수</h4><p class="sub">같은 문항, 같은 질문 글</p>' + _bars(rows, 180, TOTAL, '막대 축은 180~277문항.')
              + f'<p class="note">Decisions만 맞힌 문항 {len(only_d)}개, Jev만 맞힌 문항 {len(only_j)}개. 확신 0.95 이상 오답: Jev {sum(not jev[q]["correct"] for q in jh)}/{len(jh)}, Decisions {sum(not d277[q]["correct"] for q in dh)}/{len(dh)}</p></div>')
        trs = ''
        for t, tn in names.items():
            qs = [q for q in ids if d277[q]['task'] == t]
            a = sum(bool(jev[q]['correct']) for q in qs); b = sum(bool(d277[q]['correct']) for q in qs)
            od = sum(1 for q in only_d if d277[q]['task'] == t); oj = sum(1 for q in only_j if d277[q]['task'] == t)
            win = 'Decisions' if b > a else ('Jev' if a > b else '같음')
            trs += f'<tr><td class="rw">{tn}</td><td class="c">{a}/{len(qs)}</td><td class="c">{b}/{len(qs)}</td><td class="c">{od}</td><td class="c">{oj}</td><td class="c"><b>{win}</b></td></tr>'
        c2 = ('<div class="chart"><h4>과제별(277문항)</h4><p class="sub">한쪽만 맞힌 문항 수 포함</p><div class="tw"><table class="mx"><tr><th>과제</th><th class="c">Jev</th><th class="c">Decisions</th>'
              '<th class="c">Decisions만 맞힘</th><th class="c">Jev만 맞힘</th><th class="c">나은 쪽</th></tr>' + trs + '</table></div></div>')
        body = f'<div class="two">{c1}{c2}</div>'
        # 검증, 최종 세트
        dv = {r['id']: r for r in jl(FT / 'results_openai_decisions.jsonl') if 'pred' in r}
        jv = {r['id']: r for r in jl(FT / 'results_jev_eval.jsonl') if 'pred' in r}
        if dv:
            sets = {n: {r['id']: r for r in jl(FT / 'sets' / f'{f}.jsonl')} for n, f in (('valid', 'valid_v3'), ('final', 'final_v1'))}
            cells = ''
            for n, lab in (('valid', '검증'), ('final', '최종')):
                for lg in (False, True):
                    qs = [q for q, it in sets[n].items() if bool(it.get('long')) == lg and q in dv and q in jv]
                    if qs:
                        cells += (f'<tr><td class="rw">{lab}, {"긴 문서" if lg else "12000자 이하"}</td><td class="c">{sum(bool(jv[q]["correct"]) for q in qs)}/{len(qs)}</td>'
                                  f'<td class="c">{sum(bool(dv[q]["correct"]) for q in qs)}/{len(qs)}</td></tr>')
            body += ('<h3>검증 세트와 최종 시험(처음 보는 문서)</h3><div class="tw"><table class="mx"><tr><th>구분</th><th class="c">Jev(1회차)</th><th class="c">Decisions</th></tr>'
                     + cells + f'</table></div><p class="cav">Decisions는 {len(dv)}/925문항까지 풀었다.</p>')
    body += ('<h3>그림 판정 시험(Decisions만 가능)</h3><div class="tw"><table class="mx"><tr><th>대상</th><th>문서</th><th>상태</th></tr>'
             '<tr><td class="rw">스캔 PDF 보고서</td><td>CADC 월별 19건 등 비달러 22건, StablR, BiLira</td><td>아직 안 함</td></tr>'
             '<tr><td class="rw">그림으로 된 자산 표</td><td>QCAD 준비금 구성표</td><td>아직 안 함</td></tr>'
             '<tr><td class="rw">그림 서명란(R15)</td><td>IDRT 감사인 쪽 이미지 페이지</td><td>아직 안 함</td></tr></table></div>')
    alt = ''.join(f'<tr><td class="rw">{E(a)}</td><td>{E(b)}</td><td class="c">{E(c)}</td><td>{E(d)}{" <span class=\"tbd\">미정</span>" if t else ""}</td></tr>' for a, b, c, d, t in OPEN_ALTS)
    body += ('<h3>공개 판정 모델(검토만 하고 고르지 않은 것)</h3><div class="tw"><table class="mx"><tr><th>이름</th><th>바탕 모델, 크기</th><th class="c">외부 순위표 점수</th><th>고르지 않은 이유</th></tr>'
             f'<tr class="me"><td class="rw">Jev(비교 기준)</td><td>비공개</td><td class="c">77.1</td><td>-</td></tr>'
             f'<tr><td class="rw">OpenAI Decisions(비교 기준)</td><td>gpt-6-luna, 비공개</td><td class="c">73.5</td><td>-</td></tr>'
             + alt + '</table></div>'
             '<p class="cav">점수는 Benchmark Heaven JevBench(2026-10-12)의 능력 점수(정답률과 확신값 정확도의 평균). 일반 판정 문항 기준이라 우리 문항 점수와 다르다. '
             'Qwen 계열은 중국계 가중치라 은행 보안 심사 위험이 있어 바탕 모델에서 뺐다.</p>')
    return f"""<section id="s5"><h2>5. 외부 판정 서비스 비교(Jev, Decisions API)</h2>
<div class="tw"><table class="mx"><tr><th>항목</th><th>Jev(TypeSafe)</th><th>Decisions API(OpenAI)</th><th class="c">나은 쪽</th></tr>{feat}</table></div>
{body}
</section>
"""


def build(status_path):
    A, raw = load()
    meta = {**A['kanana'], **A['gemma']}
    jev = jev_for(meta, load_jev())
    o = A['gptoss']
    o_lines = raw['gptoss']
    o_skip = [r for r in o_lines if 'skipped' in r]
    st = read_status(status_path)
    now = time.strftime('%Y-%m-%d %H:%M')
    names = {m[0]: m[1] for m in MODELS}

    # 맨 위 수치
    R = FT / 'runs'
    jc = sum(v['correct'] for v in jev.values())

    def stage(label, res_path, steps_path=None, wait=None):
        """학습 한 판의 상태: (글, 상태 class)."""
        r = _res(res_path) if res_path else None
        if r and r['lines'] >= 324:
            return label, f'{r["c"]}개', 'done', r['c']
        stop = pathlib.Path(str(steps_path).replace('steps_', 'stopped_').replace('.log', '.txt')) if steps_path else None
        if stop and stop.exists():
            return label, stop.read_text(encoding='utf-8').split(',')[0].strip(), 'wait', None
        e = _steps_eta(steps_path) if steps_path else None
        if e:
            st, tot, left = e
            return label, (f'학습 중 {st}/{tot}단계' if st < tot else '학습 끝, 재시험 중'), 'now', None
        return label, wait or '대기', 'wait', None

    cards = [('gemma', 'Gemma 4 E4B', 'Google', [
                 ('학습 전', FT / 'results_gemma_base_t4.jsonl'),
                 ('1차 학습(자료 v2)', R / 'colab3/results_gemma-ft3.jsonl', R / 'colab3/steps_gemma-ft3.log'),
                 ('2차 학습(자료 v3)', R / 'colab3/results_gemma-ft4.jsonl', R / 'colab3/steps_gemma-ft4.log')]),
             ('kanana', 'Kanana 1.5 8B', '카카오', [
                 ('학습 전', FT / 'results_kanana_base_t4.jsonl'),
                 ('1차 학습(자료 v2)', R / 'colab2/results_kanana-ft2.jsonl', R / 'colab2/steps_kanana-ft2.log'),
                 ('2차 학습(자료 v3)', R / 'desktop/results_kanana-ft3.jsonl', R / 'desktop/steps_kanana-ft3.log'),
                 ('합성 B(v3 + 합성 186)', R / 'desktop/results_kanana-synB.jsonl', R / 'desktop/steps_kanana-synB.log')]),
             ('gptoss', 'GPT-OSS-20B', 'OpenAI', [
                 ('학습 전', R / 'colab4/results_gptoss_direct_base.jsonl'),
                 ('1차 학습(자료 v2)', R / 'colab4/results_gptoss-ft2.jsonl', R / 'colab4/steps_gptoss-ft2.log')])]
    tiles = ''
    for key, nm, co, sts in cards:
        rows = [stage(*x) for x in sts]
        best = [r[3] for r in rows if r[3] is not None][-1]
        cur = next((r for r in rows if r[2] == 'now'), None)
        nxt = next((r[0] for r in rows if r[2] == 'wait'), None)
        state = ('지금 ' + cur[0] + ' 중') if cur else ('지금 쉬는 중' + (', 다음: ' + nxt if nxt else ''))
        lis = ''.join(f'<li class="{c}"><span>{E(l)}{data_chips(l)}</span><b>{E(v)}</b></li>' for l, v, c, _ in rows)
        tiles += (f'<div class="mc" style="--b:{BRAND[key]}"><div class="mh">{logo(key)}<b>{nm}</b><span>{co}</span></div>'
                  f'<div class="mv">{best}개</div><div class="mg">Jev보다 {jc - best}개 적음</div>'
                  f'<div class="mst">{E(state)}</div><ol class="ms">{lis}</ol></div>')
    dec = _byid(FT / 'results_openai_decisions_277.jsonl') if len(jl(FT / 'results_openai_decisions_277.jsonl')) >= 277 else None
    if dec:
        dc = sum(bool(x['correct']) for x in dec.values())
        tiles += (f'<div class="mc" style="--b:{BRAND["decisions"]}"><div class="mh">{logo("decisions")}<b>Decisions API</b><span>OpenAI</span></div>'
                  f'<div class="mv">{dc}개</div><div class="mg">Jev보다 {abs(jc - dc)}개 {"적음" if dc < jc else "많음"}</div>'
                  f'<div class="mst">학습하지 않음(외부 서비스, 비교 기준)</div><ol class="ms"><li class="done"><span>모델</span><b>gpt-6-luna</b></li></ol></div>')
    tiles += (f'<div class="mc goal" style="--b:{BRAND["jev"]}"><div class="mh">{logo("jev")}<b>Jev</b><span>TypeSafe AI</span></div>'
              f'<div class="mv">{jc}개</div><div class="mg">277문항 중 {pct(jc, TOTAL)}, 이만큼이 목표</div>'
              f'<div class="mst">학습하지 않음(외부 서비스, 비교 기준)</div><ol class="ms"><li class="done"><span>바꾸지 않는 기준 모델</span><b>jev-1.13.0</b></li></ol></div>')

    # 진행
    done_n = len(o_lines)
    secs = [r['secs'] for r in o_lines if 'secs' in r]
    avg = sum(secs) / len(secs) if secs else 0
    left = TOTAL - done_n
    eta = f'약 {left * avg / 3600:.1f}시간' if secs and left > 0 else ('끝남' if left <= 0 else '-')
    alive = st.get('alive')
    run_txt = '실행 중' if alive else ('멈춤' if alive is False else '확인 전')
    if done_n >= TOTAL:
        run_txt = '끝남'
    w = 100 * done_n / TOTAL
    masses = [r['letter_mass'] for r in o.values()]
    prog = f'''<div class="chart"><h4>GPT-OSS-20B 진행</h4><p class="sub">Colab 상태 {E(run_txt)}, 마지막 확인 {E(st.get('checked', '-'))}</p>
<div class="meter" role="img" aria-label="{done_n}/{TOTAL}"><i style="width:{w:.1f}%"></i></div>
<div class="meter-l"><span><b>{done_n}/{TOTAL}</b> 처리</span><span>남은 문항 {left}</span></div>
<table class="mx"><tr><th>항목</th><th>값</th></tr>
<tr><td>답한 문항</td><td>{len(o)}</td></tr>
<tr><td>건너뛴 문항</td><td>{len(o_skip)} (T4 메모리 부족 {sum('OutOfMemory' in r['skipped'] for r in o_skip)}, 입력 3,496토큰 초과 {sum('토큰 >' in r['skipped'] for r in o_skip)}, 모두 긴 문서 문항)</td></tr>
<tr><td>한 문항 평균 시간</td><td>{avg:.0f}초 (최소 {min(secs) if secs else 0:.0f}초, 최대 {max(secs) if secs else 0:.0f}초)</td></tr>
<tr><td>남은 시간</td><td>{E(eta)} (지금까지 평균으로 계산)</td></tr>
<tr><td>선택지 글자 확률 합(letter_mass) 최소</td><td>{min(masses) if masses else 0:.2f} (0.5 미만이면 답 형식 문제)</td></tr>
<tr><td>GPU 메모리</td><td>{st.get('mem', '-')} MiB / 15360 MiB</td></tr>
</table></div>'''

    # 같은 문항 비교 (GPT-OSS가 답한 문항)
    ids = set(o)
    rows = []
    for key, nm, *_ in MODELS:
        c, n = score(A[key], ids)
        rows.append((nm, c, n))
    jsub = {q: v for q, v in jev.items() if q in ids}
    jsc = sum(v['correct'] for v in jsub.values())
    bars = ''
    for nm, c, n in rows:
        r = c / n if n else 0
        cls = 'bar a' if nm == 'GPT-OSS-20B' else 'bar'
        bars += f'<span>{E(nm)}</span><div class="row"><div class="{cls}" style="width:{r * 78:.1f}%"></div><span class="val">{c}/{n} ({pct(c, n)})</span></div>'
    if jsub:
        bars += f'<span>Jev(참고)</span><div class="row"><div class="bar" style="width:{78 * jsc / len(jsub):.1f}%"></div><span class="val">{jsc}/{len(jsub)} ({pct(jsc, len(jsub))})</span></div>'
    same = f'''<div class="chart"><h4>같은 문항 정답률</h4><p class="sub">GPT-OSS-20B가 지금까지 답한 {len(ids)}문항만 놓고 비교</p>
<div class="bars">{bars}</div><p class="note">막대 길이는 모델끼리 같은 축. Jev도 같은 문항(n={len(jsub)}).</p></div>'''

    # 세트, 과제별
    groups = collections.OrderedDict()
    for q, r in sorted(meta.items(), key=lambda x: (x[1]['set'], x[1]['task'])):
        groups.setdefault((r['set'], r['task']), []).append(q)
    trs = ''
    for (s, t), qs in groups.items():
        qs = set(qs)
        cells = ''
        for key, *_ in MODELS:
            c, n = score(A[key], qs)
            cells += f'<td class="c">{c}/{n}</td>' if n else '<td class="c">-</td>'
        jx = [jev[q] for q in qs if q in jev]
        cells += f'<td class="c">{sum(v["correct"] for v in jx)}/{len(jx)}</td>' if jx else '<td class="c">-</td>'
        trs += f'<tr><td class="rw">{s} {SETS.get(s, "")}</td><td>{E("자산 종류" if t == "asset" else t)}</td><td class="c">{len(qs)}</td>{cells}</tr>'
    tot = ''.join(f'<td class="c"><b>{score(A[k])[0]}/{score(A[k])[1]}</b></td>' for k, *_ in MODELS)
    trs += f'<tr class="me"><td class="rw">합계</td><td></td><td class="c">{len(meta)}</td>{tot}<td class="c"><b>{jc}/{len(jev)}</b></td></tr>'
    bytask = f'''<table class="mx"><tr><th>세트</th><th>과제</th><th class="c">문항</th>{''.join(f'<th class="c">{E(m[1])}</th>' for m in MODELS)}<th class="c">Jev(참고)</th></tr>{trs}</table>
<p class="cav">GPT-OSS-20B 칸은 지금까지 답한 문항 수 기준. Jev의 S3는 10/11에 같은 질문 글로 따로 잰 값.</p>'''

    # 확신값
    ctr = ''
    for key, nm, *_ in MODELS:
        hi = [r for r in A[key].values() if r['conf'] >= 0.95]
        wrong = sum(not r['correct'] for r in hi)
        base = '전체 277문항' if key != 'gptoss' else '지금까지 답한 문항'
        ctr += f'<tr><td class="rw">{E(nm)}</td><td>{base}</td><td class="c">{len(A[key])}</td><td class="c">{len(hi)}</td><td class="c">{wrong}</td></tr>'
    jhi = [v for v in jev.values() if v['conf'] >= 0.95]
    ohi = sum(1 for r in o.values() if r['conf'] >= 0.95)
    oss_note = f' GPT-OSS-20B는 추론을 마친 뒤 답 글자를 읽기 때문에 확신값이 1.00 가까이 몰린다(답한 {len(o)}문항 중 {ohi}문항이 0.95 이상).' if o else ''
    ctr += f'<tr><td class="rw">Jev(참고)</td><td>277문항</td><td class="c">{len(jev)}</td><td class="c">{len(jhi)}</td><td class="c">{sum(not v["correct"] for v in jhi)}</td></tr>'
    conf = f'''<table class="mx"><tr><th>모델</th><th>기준</th><th class="c">답한 문항</th><th class="c">확신 0.95 이상</th><th class="c">그중 오답</th></tr>{ctr}</table>
<p class="cav">확신 0.95 이상인데 틀린 답이 있으면 확신값으로 자동 확정할 수 없다.{oss_note}</p>'''

    # 시험 조건
    def avg_secs(key):
        xs = [r['secs'] for r in A[key].values() if 'secs' in r]
        return f'{sum(xs) / len(xs):.1f}초' if xs else '-'
    cond = ''.join(f'<tr><td class="rw">{E(nm)}</td><td>{E(co)}</td><td>{E(dev)}</td><td>{E(ld)}</td><td>{E(how)}</td><td class="c">{avg_secs(k)}</td></tr>'
                   for k, nm, co, dev, ld, how in MODELS)
    cond = f'''<table class="mx"><tr><th>모델</th><th>회사, 크기</th><th>실행 장비</th><th>불러오기</th><th>답 읽는 방법</th><th class="c">문항당 평균</th></tr>{cond}</table>
<p class="cav">세 모델 공통: 학습 없음, 같은 질문 글, 입력 12000자 이하 {TOTAL}문항(전체 324문항 중 47문항 제외).</p>'''

    css = CSS.read_text(encoding='utf-8') if CSS.exists() else ''
    s_sum, s_prog, s_crit, s_terms = overview(jev)
    s_main, s_pilot = ft_sections(jev)
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>모델 3종 이전 기록</title>
<style>{css}
{STYLE}
</style></head><body><div class="layout">
<nav class="side"><b>목차</b><a href="#s1">1. 지금 성적</a><a href="#s2">2. 성장 기록</a><a href="#s3">3. 지금 하는 일</a><a href="#s4">4. 검증 세트, 최종 시험</a><a href="#s5">5. Jev, Decisions 비교</a><a href="#s6">6. 목표 판정 기준</a><a href="#s7">7. 모르는 것</a><a href="#s8">8. 기술적 기여, 다음 개발</a><a href="#s9">9. 부록</a></nav>
<main>
<header class="mast"><p class="eyebrow">SC2K 판정 블록 바탕 모델 시험, 2026-10-10~10-15 탐색 기록</p>
<h1>모델 3종 이전 기록</h1>
<p class="lede">처음부터 다시 학습하기 전의 결과다. 모델마다 학습 자료, 장비, 시험지가 달라 모델끼리 비교하는 데 쓰지 않는다. 합성 효과, 오답 분석은 지금 방침의 근거로 남긴다.</p></header>
<p class="legend">학습 자료 구분 &nbsp;{CHIP['real']} 공개 문서로 만든 실제 자료 &nbsp;{CHIP['syn']} 실제 학습 문서를 한 군데만 고쳐 만든 자료(학습에만 씀) &nbsp;{CHIP['none']} 외부 서비스. 시험지는 모두 실제 문서</p>
<h3 class="tth">모델별 상태(같은 시험 277문항에서 맞힌 개수)</h3>
<div class="mcards">{tiles}</div>

{s_sum.replace('<section><h2>한눈에</h2>', '<section id="s1"><h2>1. 지금 성적</h2>')}

{growth_section(jev)}

{s_prog.replace('<section><h2>진행 단계</h2>', '<section id="s3"><h2>3. 지금 하는 일</h2>')}

{evalsets_section()}

{ext_section(jev)}

{s_crit.replace('<section><h2>목표 판정 기준(안)</h2>', '<section id="s6"><h2>6. 목표 판정 기준(안)</h2>')}

<section id="s7"><h2>7. 모르는 것</h2>
<ul class="unk">
<li><span>?</span><div><b>최종 시험에서도 Jev만큼인지</b><p>검증 판단용에서는 Gemma가 Jev보다 1개 적었다. 최종 시험 553문항은 마지막에 한 번 본다.</p></div></li>
<li><span>?</span><div><b>2차 학습(자료 v3)이 '아니오를 예로' 오답을 줄이는지</b><p>Kanana 2차는 277문항에서 15개에서 10개로, 검증 판단용에서 14개에서 12개로 줄었지만 반대쪽(예를 아니오로) 오답이 늘어 정답 수는 그대로다(판단용 210). Gemma 2차는 중단.</p></div></li>
<li><span>?</span><div><b>GPT-OSS-20B 학습 효과</b><p>학습이 중단돼 아직 결과가 없다.</p></div></li>
</ul></section>

{contrib_section()}

<section id="s9"><h2>9. 부록</h2>
<p>눌러서 펼친다.</p>
<details id="d-train"><summary>학습 기록(문항 수, 방식, 학습별 점수)</summary>{s_main.replace('<section><h2>파인튜닝 본 학습</h2>', '').replace('</section>', '')}</details>
<details id="d-terms"><summary>용어</summary>{s_terms.replace('<section><h2>용어</h2>', '').replace('</section>', '')}</details>
<details id="d-pilot"><summary>파인튜닝 맛보기</summary>{s_pilot.replace('<section><h2>파인튜닝 맛보기</h2>', '').replace('</section>', '')}</details>
<details id="d-base"><summary>학습 전 시험(세 모델, 277문항)</summary>
<p>학습 전 모델(Gemma, Kanana는 집 PC, GPT-OSS-20B는 추론 후 답)의 결과다.</p>
<h3>GPT-OSS-20B 추론 후 답</h3><div class="two">{prog}{same}</div>
<h3>세트, 과제별 정답</h3><div class="tw">{bytask}</div>
<h3>확신값 신뢰도</h3>{conf}
<h3>시험 조건</h3>{cond}
</details>
<details id="d-log"><summary>진행 기록(10/10~10/11)</summary>
<div class="tw"><table class="mx"><tr><th>날짜</th><th>내용</th><th>결과</th></tr>
<tr><td class="rw">10/10</td><td>후보 3종 결정(GPT-OSS-20B, Gemma 4 E4B, Kanana 1.5 8B)</td><td>학습 없이 시험해 1종 선택</td></tr>
<tr><td class="rw">10/11 오전</td><td>Gemma, Kanana 시험(집 PC)</td><td>Gemma 254/277, Kanana 215/277</td></tr>
<tr><td class="rw">10/11 오후</td><td>GPT-OSS-20B Colab 첫 실행</td><td>맛보기 10문항 전부 오류(자료형 불일치, Float와 Half)</td></tr>
<tr><td class="rw">10/11 오후</td><td>오류 원인 확인과 수정</td><td>Unsloth의 답 생성은 float16 자동 변환(autocast) 안에서 돌고, 답 글자 확률을 읽는 단계는 밖에서 돌아 어긋남. 확률 읽기 단계도 같은 자동 변환으로 감쌈. 질문 글, 정답, 채점 방식은 그대로</td></tr>
<tr><td class="rw">10/11 오후</td><td>GPT-OSS-20B 추론 후 답 전체 실행</td><td>{E(run_txt)}, {done_n}/{TOTAL}</td></tr>
<tr><td class="rw">10/11 저녁</td><td>파인튜닝 1판(자료 v2)</td><td>Gemma 252 → 259, Kanana 214 → 238</td></tr>
<tr><td class="rw">10/11 밤</td><td>파인튜닝 1판 보강(자료 v3), 검증 세트와 최종 시험 문항 수집</td><td>진행 중</td></tr>
</table></div>
</details>
</section>
</main></div>
<script>
(function () {{
  var K = 'sc2k-status';
  function load() {{ try {{ return JSON.parse(sessionStorage.getItem(K) || '{{}}'); }} catch (e) {{ return {{}}; }} }}
  function save(v) {{ try {{ sessionStorage.setItem(K, JSON.stringify(v)); }} catch (e) {{}} }}
  var st = load();
  document.querySelectorAll('details[id]').forEach(function (d) {{
    if ((st.open || []).indexOf(d.id) >= 0) d.open = true;
    d.addEventListener('toggle', function () {{
      var v = load(); var o = (v.open || []).filter(function (x) {{ return x !== d.id; }});
      if (d.open) o.push(d.id); v.open = o; save(v);
    }});
  }});
  if (st.y) window.scrollTo(0, st.y);
  addEventListener('scroll', function () {{ var v = load(); v.y = scrollY; save(v); }}, {{passive: true}});
  var links = document.querySelectorAll('nav.side a');
  var io = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{
      if (e.isIntersecting) links.forEach(function (a) {{ a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); }});
    }});
  }}, {{rootMargin: '-20% 0px -70% 0px'}});
  document.querySelectorAll('section[id]').forEach(function (s) {{ io.observe(s); }});
}})();
</script>
</body></html>'''


def main():
    args = sys.argv[1:]
    status = args[args.index('--status') + 1] if '--status' in args else None
    out = pathlib.Path(args[args.index('--out') + 1]) if '--out' in args else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(status), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
