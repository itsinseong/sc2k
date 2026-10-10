"""Jev 다시 읽기(results.json.gz)의 R11, R12, R15 답을 레포 값과 맞춰 보고, 불일치를 원문으로 확인한 분류와 함께 summary.md를 쓴다.
  python3 -B jev_compare.py
- Jev 답: p(예일 확률) 0.5 이상이면 예. 확신값은 |2p-1|(scripts/jev/jev_hard_test.py와 같다).
- 분류 규칙(rule)은 불일치 64건의 원문을 읽고 정했다. 규칙마다 근거 문장을 원문에서 다시 찾고,
  못 찾거나 규칙에 없는 불일치가 나오면 멈춘다(새 불일치는 원문을 읽고 규칙을 더한다).
- 글 층이 있는 쪽은 Jev 입력과 같은 글(jev_choice_test.pdf_pages), 글 층이 없거나 깨진 쪽은 300dpi 그림을 tesseract로 읽는다.
  바로 놓은 그림에서 근거를 못 찾으면 180도 돌려(sips) 다시 읽는다.
- data/*.json은 읽기만 한다. 파서, pytest, Jev API는 부르지 않는다.
"""
import collections, glob, gzip, json, pathlib, re, subprocess, sys, tempfile
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'scripts' / 'jev'))
from jev_choice_test import pdf_pages  # noqa: E402  Jev 입력과 같은 쪽별 글

OUT = ROOT / 'docs' / 'research' / 'Jev전체대조_2026-10-10'
QS = {'R11_broad': 'circulation_formula_disclosed', 'R11_narrow': 'circulation_formula_disclosed',
      'R12': 'custodian_disclosure', 'R15': 'management_certification'}
NAME = {'R11_broad': 'R11 넓게 질문', 'R11_narrow': 'R11 좁게 질문', 'R12': 'R12 보관 기관 이름', 'R15': 'R15 경영진 서명'}
BINS = ((0, .5, '0.5 미만'), (.5, .8, '0.5~0.8'), (.8, .9, '0.8~0.9'), (.9, .95, '0.9~0.95'), (.95, 1.01, '0.95 이상'))
CLASSES = ('Jev 오답', '레포 값 오류', '기준 문제', '판단 불가')
TOKENS = ('USDC', 'EURC', 'PYUSD', 'USDP', 'USDG', 'RLUSD', 'GUSD', 'USDT')
PAXOS = ('PYUSD', 'USDP', 'USDG')
CALC = r'natively minted|nonredeemable|burn|Tokens Allowed But Not Issued|less digital tokens'  # 좁게 기준 계산 말
G_A, G_B = 'R11 가: RLUSD 정의 문장', 'R11 나: Paxos 계약 공급량 문장'


def rule(q, r):
    """원문을 읽고 정한 분류. pats는 모두 원문에 있어야 하고 첫 패턴이 인용문이다. guard는 Jev 입력 글에 없어야 한다."""
    tok, rv = r['token'], r['repo'][QS[q]]
    if q == 'R11_narrow' and tok == 'RLUSD' and rv:
        return dict(cls='기준 문제', group=G_A, src='text', guard=CALC,
                    pats=[r'(?:Total RLUSD outstanding is defined as|Outstanding Stablecoin Units means) .*?Report Dates\.'])
    if q == 'R11_broad' and tok in PAXOS and not rv:
        return dict(cls='기준 문제', group=G_B, src='text', guard=CALC,
                    pats=[r'The (?:total )?supply of .*?as denoted under contracts? .*?respectively[^.]*\.'])
    if q.startswith('R11') and tok == 'USDG' and rv:
        return dict(cls='Jev 오답', src='ocr', page=7,
                    pats=[r'Exhibit A: Total USDG Natively Minted Tokens and Total USDG Redeemable Tokens Outstanding',
                          r'Less permanent', r'nonredeemable'],
                    what='Exhibit A 표: (a) 발행 토큰에서 (b) 임시, (c) 영구 상환 불가 토큰을 빼 (d) 상환 가능 토큰')
    if q == 'R12' and tok == 'USDG' and rv:
        return dict(cls='Jev 오답', src='ocr', page=6, pats=[r'the Company custodied Redemption Assets at .*?Mellon\.'],
                    what='Note 5 보관 기관 이름')
    if q == 'R12' and tok == 'GUSD' and rv:
        return dict(cls='Jev 오답', src='ocr', page=4,
                    pats=[r'The Gemini dollar reserves are held and maintained as cash deposits at .*?(?:;|\. )'],
                    what='각주 2 예금 은행 이름')
    if q == 'R15' and tok == 'USDG' and rv:
        return dict(cls='Jev 오답', src='ocr', page=6,
                    pats=[r'To the best of the knowledge and belief of the undersigned, .*?accurate and complete\.',
                          r'Signed by', r'Executive Director'],
                    what='경영진 확인 문장과 서명 블록(이름, Executive Director)')
    if q == 'R15' and tok == 'GUSD' and rv:
        return dict(cls='Jev 오답', src='ocr', page=4,
                    pats=[r'(?:CEO/President|Interim Chief Financial Officer) Gemini [A-Za-z ,]+?(?:LLC|Inc\.)'],
                    what='경영진 확인서 서명 블록(이름, 직함)')
    return None


def flat(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def short(s):
    s = re.sub(r'\b(?:0x[0-9a-fA-F]{40}|[1-9A-HJ-NP-Za-km-z]{32,44})\b', '(주소)', s)
    return s.replace('|', '/').strip()


def ocr(pdf, page):
    """그림 쪽을 300dpi로 읽은 글(빈칸 정리). 바로 놓은 판을 먼저 주고, 더 달라고 하면 180도 돌린 판을 준다."""
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm', '-r', '300', '-f', str(page), '-l', str(page), '-png', str(pdf), f'{d}/p'], check=True)
        img = glob.glob(f'{d}/p*.png')[0]
        yield flat(subprocess.run(['tesseract', img, '-'], capture_output=True, text=True, check=True).stdout)
        subprocess.run(['sips', '-r', '180', img], capture_output=True, check=True)
        yield flat(subprocess.run(['tesseract', img, '-'], capture_output=True, text=True, check=True).stdout)


def check(r, q, spec, pages):
    """규칙의 근거를 원문에서 찾아 쪽과 인용을 붙인다. 못 찾으면 멈춘다."""
    used = r['input']['pages_used']
    inp = {n: flat(pages[n - 1]) for n in used}
    tag = f"{q} {r['token']} {r['month']}"
    if re.search(spec.get('guard', '$^'), ' '.join(inp.values()), re.I):
        sys.exit(f'{tag}: 입력 글에 계산 말이 있다. 원문을 다시 읽는다')
    if spec['src'] == 'text':
        for n, t in inp.items():
            m = re.search(spec['pats'][0], t)
            if m: return dict(page=n, quote=short(m[0]), read='글 층(Jev 입력과 같은 글)')
        sys.exit(f'{tag}: 근거 문장을 입력 글에서 못 찾음')
    if any(re.search(spec['pats'][0], t, re.I) for t in inp.values()):
        sys.exit(f'{tag}: 근거가 Jev 입력 글에 있다(입력 누락 분류가 아님)')
    p = spec['page']
    for t in ocr(ROOT / r['source_file'], p):
        if all(re.search(x, t, re.I) for x in spec['pats']):
            why = (f'{p}쪽이 글 층 없는 그림이라 Jev 입력에 없었다' if p in r['input']['pages_no_text'] else
                   f'{p}쪽 글 층이 깨진 글자라 Jev 입력에서 읽을 수 없었다')
            return dict(page=p, quote=short(re.search(spec['pats'][0], t, re.I)[0]), read='그림 쪽 OCR(tesseract 300dpi)', why=why)
    sys.exit(f'{tag}: {p}쪽 OCR에서 근거를 못 찾음')


def pct(a, b):
    return f'{a}/{b} ({100 * a / b:.1f}%)' if b else '-'


def yn(v):
    return '예' if v else '아니오'


def main():
    res = json.load(gzip.open(OUT / 'results.json.gz', 'rt', encoding='utf-8'))
    rows = sorted([r for r in res['rows'] if r['status'] == 200], key=lambda r: (TOKENS.index(r['token']), r['month']))
    ans = []  # (q, row, p, jev, conf, agree)
    for r in rows:
        for q, k in QS.items():
            p = r['response']['answers'][q]['noul']
            assert abs(p * 100 - round(p * 100)) < 1e-9, (r['id'], q, p)  # 요약의 'p는 0.01 단위' 문장 근거
            ans.append((q, r, p, p >= 0.5, round(abs(2 * p - 1), 4), (p >= 0.5) == r['repo'][k]))
    mis = sorted([a for a in ans if not a[5]], key=lambda a: (-a[4], list(QS).index(a[0]), a[1]['token'], a[1]['month']))
    text = {}
    rev = []
    for q, r, p, jev, conf, _ in mis:
        spec = rule(q, r)
        if spec is None: sys.exit(f"규칙에 없는 불일치: {q} {r['id']} {r['token']} {r['month']}. 원문을 읽고 rule()에 더한다")
        if r['id'] not in text: text[r['id']] = pdf_pages(ROOT / r['source_file'])
        rev.append({'q': q, 'row': r, 'p': p, 'jev': jev, 'conf': conf, **spec, **check(r, q, spec, text[r['id']])})
        print(len(rev), q, r['token'], r['month'], spec['cls'], flush=True)

    # 넓게 기준이면 바뀌는 레포 아니오: Paxos 보고서 중 레포 아니오이고 계약 공급량 문장이 입력 글에 있는 것
    pax_no = [r for r in rows if r['token'] in PAXOS and not r['repo'][QS['R11_broad']]]
    pax_sent = [r for r in pax_no if re.search(r'as\s+denoted\s+under\s+contracts?', ' '.join(pdf_pages(ROOT / r['source_file'])))]
    skip_rec = []
    for s in res['meta']['skipped_no_text']:
        f, i = s.split('#')
        rec = json.loads((ROOT / f).read_text(encoding='utf-8'))['reports'][int(i)]
        skip_rec.append((rec['token'], rec['month'], rec['circulation_formula_disclosed']))
    write(res, rows, ans, mis, rev, pax_no, pax_sent, skip_rec)


def write(res, rows, ans, mis, rev, pax_no, pax_sent, skip_rec):
    n_rows = len(rows)
    by_q = {q: [a for a in ans if a[0] == q] for q in QS}
    cnt = collections.Counter((x['q'], x['cls']) for x in rev)
    jev_wrong = [x for x in rev if x['cls'] == 'Jev 오답']
    hi_conf = [a for a in ans if a[4] >= 0.99]
    hi_p = [a for a in ans if a[2] >= 0.99 or a[2] <= 0.01]
    gA = [x for x in rev if x.get('group') == G_A]
    gB = [x for x in rev if x.get('group') == G_B]
    no_text_reports = [r for r in rows if r['input']['pages_no_text']]
    garbled = [x for x in jev_wrong if '깨진' in x['why']]
    n_cls = {c: sum(1 for x in rev if x['cls'] == c) for c in CLASSES}
    n_1215 = sum(1 for a in mis if a[0] in ('R12', 'R15'))
    r15_all = [r['repo']['management_certification'] for r in res['rows']]
    n_rlusd = sum(1 for r in rows if r['token'] == 'RLUSD')
    L = ['# Jev 전체 대조: R11, R12, R15 레포 값과 Jev 답의 불일치 분류', '',
         f"- 날짜 2026-10-10. Jev 모델 {res['meta']['model_requested']}. 입력은 results.json.gz(보고서 {res['meta']['reports']}건 중 Jev 답 {n_rows}건, "
         f"글 층이 없어 건너뛴 {len(skip_rec)}건). 스크립트 scripts/jev_compare.py.",
         '- 레포 값: R11 circulation_formula_disclosed, R12 custodian_disclosure, R15 management_certification(data/reports*.json, 고치지 않았다). '
         'R11 레포 값 하나를 Jev의 넓게 질문 답과 좁게 질문 답에 각각 맞춰 봤다.',
         '- Jev 답은 p(예일 확률) 0.5 이상이면 예로 셌다. 확신값은 |2p-1|이다(2차 시험 summary와 같은 정의). 확신 0.8은 p 0.9 이상 또는 0.1 이하다.',
         f'- 불일치 {len(mis)}건을 확신 높은 순으로 모두 원문과 대조했다. 글 층이 있는 쪽은 Jev 입력과 같은 pdftotext 글로, 글 층이 없거나 깨진 쪽은 '
         '300dpi 그림을 tesseract로 읽은 글로 확인했다. 그림 쪽 가운데 USDG 2025-03 6쪽, 2025-09 6쪽, 2026-05 7쪽(옆으로 놓인 표)은 그림을 눈으로도 봤다.',
         '- 쪽 번호는 PDF 파일 안 순서다. 보고서에 인쇄된 쪽 번호와 다를 수 있다(예: USDG 2025-09 6쪽의 인쇄 번호는 4).', '']

    L += ['## 요점', '']
    L += ['- 일치율: ' + ', '.join(f"{NAME[q]} {pct(sum(a[5] for a in by_q[q]), len(by_q[q]))}" for q in QS) + '.']
    L += [f'- 확신 0.99 이상 불일치: 0건. 확신값 |2p-1|이 0.99 이상인 답이 한 건도 없다(가장 높은 확신값 {max(a[4] for a in ans):.2f}, '
          f'Jev p는 0.01 단위로 오고 범위가 {min(a[2] for a in ans):.2f}~{max(a[2] for a in ans):.2f}). '
          f"p 자체를 0.99 이상 또는 0.01 이하로 잡아도 {len(hi_p)}건({', '.join(sorted({f'{NAME[a[0]]} p={a[2]:.2f}' for a in hi_p}))})이고 "
          f"{'모두 레포와 같다' if all(a[5] for a in hi_p) else '레포와 다른 답이 있다'}."]
    L += [f"- 불일치 {len(mis)}건 분류: " + ', '.join(f"{c} {sum(1 for x in rev if x['cls'] == c)}건" for c in CLASSES) + '.']
    L += [f'- Jev 오답 {len(jev_wrong)}건은 모두 근거 쪽이 Jev 입력에 없던 경우다(글 층 없는 그림 쪽 {len(jev_wrong) - len(garbled)}건, '
          f'글 층이 깨진 글자인 쪽 {len(garbled)}건). 레포 값은 원문과 맞고, 입력 글에 근거가 있는데 틀린 답은 없었다.',
          f'- R12, R15 불일치 {n_1215}건이 모두 이 경우라, 근거 쪽 글이 Jev 입력에 들어간 보고서에서는 R12, R15가 모두 레포와 같았다.',
          f'- R11 기준 문제 {len(gA) + len(gB)}건: 레포 R11 값은 넓게도 좁게도 아닌 중간 기준이다. 정의 문장(RLUSD)은 예, '
          f'Paxos 옛 형식의 계약 공급량 문장은 아니오로 센다. 그래서 좁게 질문과는 RLUSD {len(gA)}건, 넓게 질문과는 Paxos {len(gB)}건이 갈린다(아래 따로 묶음).',
          '- 레포 값 오류(파서가 틀림) 후보: 0건. 판단 불가: 0건.', '']

    L += ['## 항목별 일치율', '', '| 항목 | 답한 보고서 | 일치 | 불일치 | 레포 예일 때 일치 | 레포 아니오일 때 일치 |', '|---|---|---|---|---|---|']
    for q, k in QS.items():
        a = by_q[q]
        ys = [x for x in a if x[1]['repo'][k]]
        ns = [x for x in a if not x[1]['repo'][k]]
        L.append(f'| {NAME[q]} | {len(a)} | {pct(sum(x[5] for x in a), len(a))} | {sum(not x[5] for x in a)} | '
                 f'{pct(sum(x[5] for x in ys), len(ys))} | {pct(sum(x[5] for x in ns), len(ns))} |')
    L += ['', '코인별 불일치 건수(보고서 수 대비):', '', '| 코인 | 보고서 | ' + ' | '.join(NAME[q] for q in QS) + ' |', '|---|---|' + '---|' * len(QS)]
    for t in TOKENS:
        rs = [r for r in rows if r['token'] == t]
        L.append(f'| {t} | {len(rs)} | ' + ' | '.join(str(sum(1 for a in mis if a[0] == q and a[1]["token"] == t)) for q in QS) + ' |')
    L += ['']

    L += ['## 확신 구간별 일치율', '', '칸 값: 레포와 같은 답 수/답 수. 확신값은 |2p-1|이다.', '',
          '| 항목 | ' + ' | '.join(b[2] for b in BINS) + ' |', '|---|' + '---|' * len(BINS)]
    for q in QS:
        cells = []
        for lo, hi, _ in BINS:
            b = [a for a in by_q[q] if lo <= a[4] < hi]
            cells.append(f'{sum(a[5] for a in b)}/{len(b)}' if b else '-')
        L.append(f'| {NAME[q]} | ' + ' | '.join(cells) + ' |')
    allb = []
    for lo, hi, _ in BINS:
        b = [a for a in ans if lo <= a[4] < hi]
        allb.append(f'{sum(a[5] for a in b)}/{len(b)}' if b else '-')
    L += ['| 네 항목 합 | ' + ' | '.join(allb) + ' |', '']
    L += ['- 확신 0.8 이상 불일치 ' + str(sum(1 for a in mis if a[4] >= 0.8)) + '건 가운데 Jev 오답(입력 누락) '
          + str(sum(1 for x in rev if x['conf'] >= 0.8 and x['cls'] == 'Jev 오답')) + '건, R11 기준 문제 '
          + str(sum(1 for x in rev if x['conf'] >= 0.8 and x['cls'] == '기준 문제')) + '건이다. 확신값이 높아도 입력에 근거 쪽이 빠지면 틀린다.', '']

    L += ['## 0.99 기준 위 불일치', '',
          f'- 확신값 |2p-1| 0.99 이상: 답 {len(hi_conf)}건, 불일치 0건. Jev p가 0.01 단위라 |2p-1|은 0.98(p 0.99 또는 0.01)이 가장 높다.',
          f"- p 0.99 이상 또는 0.01 이하로 읽으면: 답 {len(hi_p)}건({', '.join(sorted(set(NAME[a[0]] for a in hi_p)))}), 불일치 0건.",
          f'- 그래서 이번 확인은 0.99 아래 불일치 {len(mis)}건을 확신 높은 순으로 모두 읽은 것이다(요청 30건 이상).', '']

    L += ['## 분류 표', '', '| 항목 | 불일치 | ' + ' | '.join(CLASSES) + ' |', '|---|---|' + '---|' * len(CLASSES)]
    for q in QS:
        L.append(f"| {NAME[q]} | {sum(1 for a in mis if a[0] == q)} | " + ' | '.join(str(cnt[(q, c)]) for c in CLASSES) + ' |')
    L.append(f'| 합 | {len(mis)} | ' + ' | '.join(str(sum(1 for x in rev if x["cls"] == c)) for c in CLASSES) + ' |')
    L += ['', '- Jev 오답: 원문에 근거가 있어 레포 값이 맞고 Jev 답이 틀렸다. 이번 건은 모두 근거 쪽이 Jev 입력에 없었다(원인 칸).',
          '- 기준 문제: 원문 글은 확인됐고, 답이 갈린 까닭이 R11을 넓게 보느냐 좁게 보느냐의 차이다.',
          '- 레포 값 오류, 판단 불가: 해당 없음.', '']

    L += ['## R11 기준 문제(따로 묶음)', '',
          '레포 R11 값의 기준(site/화면문구.json R11 근거 설명과 같음): Circle, Tether와 Paxos 새 형식(PYUSD, USDP 2025-01부터, '
          'USDG 2026-01부터)은 계산식이 있어 예, '
          'Ripple은 유통량 정의 문장이 있어 예, Gemini는 출처만 적어 아니오, Paxos 옛 형식(2023~2024년 PYUSD, USDP와 2024-10~2025-12 USDG)은 '
          '계약 공급량 문장만 있어 아니오다. 넓게 질문은 정의만 있어도 예, 좁게 질문은 더하거나 뺀 토큰이 있어야 예다.', '']
    for g, lst, side in ((G_A, gA, '좁게 질문 아니오, 레포 예'), (G_B, gB, '넓게 질문 예, 레포 아니오')):
        ps = [x['p'] for x in lst]
        L += [f'### {g} ({len(lst)}건, {side})', '',
              f"- 달: {', '.join(sorted(x['row']['token'] + ' ' + x['row']['month'] for x in lst))}",
              f'- Jev p 범위 {min(ps):.2f}~{max(ps):.2f}, 확신값 {min(x["conf"] for x in lst):.2f}~{max(x["conf"] for x in lst):.2f}.',
              '- 원문 문장(이 묶음 안에서 문장 꼴이 달라질 때마다 첫 달 하나, 쪽은 PDF 순서, 계약 주소는 (주소)로 줄임):', '']
        seen = {}
        for x in sorted(lst, key=lambda x: (x['row']['token'], x['row']['month'])):
            key = re.sub(r'[\d,.]+', '#', x['quote'])
            key = re.sub(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b', 'M', key)
            if key not in seen: seen[key] = x
        for x in seen.values():
            L.append(f"  - {x['row']['token']} {x['row']['month']} 보고서 {x['page']}쪽: \"{x['quote']}\"")
        L.append('')
    pB = sorted((a for a in ans if a[0] == 'R11_broad' and a[1] in pax_no), key=lambda a: a[2])
    rng = lambda xs: f'{min(xs):.2f}~{max(xs):.2f}'  # noqa: E731
    py_old = [a[2] for a in pB if a[1]['token'] == 'PYUSD' and a[1]['month'] < '2024-05']
    py_new = [a[2] for a in pB if a[1]['token'] == 'PYUSD' and a[1]['month'] >= '2024-05']
    usdp12 = next(a[2] for a in pB if a[1]['token'] == 'USDP' and a[1]['month'] == '2023-12')
    L += [f'- Paxos 옛 형식 보고서({len(pax_no)}건, 레포 아니오)에 Jev 넓게 답 p는 {pB[0][2]:.2f}~{pB[-1][2]:.2f}로 흩어져 있다. '
          f'같은 꼴의 문장인데 PYUSD는 2024-04까지 계약 하나("as denoted under contract")일 때 p {rng(py_old)}(아니오), '
          f'2024-05부터 두 체인 계약을 합친 문장("on the Ethereum network and ... on the Solana network ... combined")에서 p {rng(py_new)}(예)다. '
          f'USDP 2023-12는 p {usdp12:.2f}, 확신 {abs(2 * usdp12 - 1):.2f}이다. 이 문장에서 Jev 넓게 답은 확신이 낮아 기준 판단에 쓰기 어렵다.',
          f'- RLUSD 정의 문장에 Jev 좁게 답은 p {rng([x["p"] for x in gA])}(아니오), 넓게 답은 '
          f"{sum(1 for a in ans if a[0] == 'R11_broad' and a[1]['token'] == 'RLUSD' and a[3])}/"
          f"{sum(1 for r in rows if r['token'] == 'RLUSD')}건 예라 RLUSD는 넓게 기준이면 레포와 같다.", '']
    L += ['R11 기준을 하나로 정하면 바뀌는 레포 값(이번에는 고치지 않음):', '',
          '| 정하는 기준 | 바뀌는 보고서 | 지금 → 바뀔 값 | 근거 |', '|---|---|---|---|',
          f'| 넓게(정의만 있어도 예) | Paxos 옛 형식 중 Jev 입력 글에 계약 공급량 문장("as denoted under contract")이 있는 {len(pax_sent)}건 '
          f'(레포 아니오 {len(pax_no)}건 중. 나머지 '
          + ', '.join(f"{r['token']} {r['month']}(입력 글 {','.join(map(str, r['input']['pages_used']))}쪽뿐)" for r in pax_no if r not in pax_sent)
          + '은 문장이 그림 쪽에 있어 확인 못 함) | 아니오 → 예 | 이번 넓게 질문과 2차 시험 정답 세트(R11-22~25) |',
          f"| 좁게(더하거나 뺀 토큰이 있어야 예) | RLUSD {len(gA)}건{'(Jev가 답한 RLUSD 전부)' if len(gA) == n_rlusd else ''} | 예 → 아니오 | 정의 문장만 있고 계산 없음 |", '']
    sk = [f'{t} {m}' for t, m, _ in skip_rec]
    L += [f"- 글 층이 없어 Jev가 건너뛴 {len(skip_rec)}건({', '.join(sk)})은 레포 R11 값이 "
          f"{', '.join(sorted(set(yn(v) for *_, v in skip_rec)))}이고, 이번 대조에 들어가지 않았다. 넓게 기준으로 바꿀 때는 이 {len(skip_rec)}건도 그림 쪽을 읽어 따로 봐야 한다.", '']

    L += ['## Jev 오답(근거 쪽이 Jev 입력에 없음)', '',
          '레포 값이 원문과 맞는다. 인용은 그림 쪽을 OCR로 읽은 글이다(서명자 이름은 OCR이 서명 그림과 겹쳐 흐려 직함까지만 적었다).', '',
          '| 항목 | 코인, 달 | 레포 | Jev 답(p) | 확신 | 근거 쪽 | 근거 | 원문 인용 | 원인 |', '|---|---|---|---|---|---|---|---|---|']
    for x in sorted(jev_wrong, key=lambda x: (-x['conf'], x['q'], x['row']['month'])):
        L.append(f"| {NAME[x['q']]} | {x['row']['token']} {x['row']['month']} | {yn(x['row']['repo'][QS[x['q']]])} | {yn(x['jev'])}({x['p']:.2f}) | "
                 f"{x['conf']:.2f} | {x['page']}쪽 | {x['what']} | \"{x['quote']}\" | {x['why']} |")
    L += ['', f'- 글 층 없는 쪽이 있는 보고서는 Jev가 답한 {n_rows}건 중 {len(no_text_reports)}건이다(코인별: '
          + ', '.join(f"{t} {c}" for t, c in collections.Counter(r['token'] for r in no_text_reports).most_common()) + '). '
          + f"글 층이 깨진 글자인 쪽이 있는 보고서({', '.join(sorted({x['row']['token'] + ' ' + x['row']['month'] for x in garbled}))})도 같은 처지다. "
          '이 보고서들은 일치한 답도 입력에 없는 쪽을 보지 않고 낸 답이다.', '']

    L += ['## 레포 값 오류 후보', '',
          f"- 없음. 불일치 {len(mis)}건 가운데 원문과 레포 값이 어긋난 건은 없었다. Jev 오답 {n_cls['Jev 오답']}건은 원문 그림 쪽에 레포 근거가 그대로 있고(위 표), "
          f"기준 문제 {n_cls['기준 문제']}건은 원문 문장이 레포 메모(field_notes)에 적힌 문장과 같다.",
          '- 이 결론은 불일치 건에 한한다. Jev와 레포가 같은 답을 낸 건은 원문과 대조하지 않았다(둘 다 틀린 경우는 이 대조로 찾을 수 없다).', '']

    L += ['## 불일치 전체 목록(확신 높은 순)', '', '| 순위 | 항목 | 코인, 달 | 레포 | Jev 답(p) | 확신 | 분류 | 근거 쪽 | 읽은 글 |',
          '|---|---|---|---|---|---|---|---|---|']
    for i, x in enumerate(rev, 1):
        cls = x['cls'] + (f" ({x['group'].split(':')[0]})" if x.get('group') else ' (입력 누락)')
        L.append(f"| {i} | {NAME[x['q']]} | {x['row']['token']} {x['row']['month']} | {yn(x['row']['repo'][QS[x['q']]])} | "
                 f"{yn(x['jev'])}({x['p']:.2f}) | {x['conf']:.2f} | {cls} | {x['page']}쪽 | {x['read']} |")
    L += ['']

    L += ['## 읽을 때 주의', '',
          f"- 분류는 원문 글을 읽은 판단이다. 기준 문제 {n_cls['기준 문제']}건은 원문 문장이 그대로 확인됐고, 어느 쪽이 맞는지는 R11 기준을 정해야 갈린다.",
          '- 그림 쪽 근거는 tesseract OCR 글로 확인했다. 그 인용의 철자는 OCR 판독이라 원문과 한두 글자 다를 수 있고, 숫자는 넣지 않았다.',
          f"- R15 레포 값은 {len(r15_all)}건 중 예 {sum(r15_all)}건이다. 이번 대조로는 서명 없는 보고서를 Jev가 가려내는지 알 수 없다(2차 시험의 R15 아니오 문항은 다른 회사 문서였다).",
          '- 확신 구간별 일치율은 레포 값과 같은지를 잰 것이고 정답률이 아니다. R11은 레포 기준이 중간이라 넓게, 좁게 질문 모두 기준 차이만큼 낮게 나온다.']
    (OUT / 'summary.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('summary.md', len(L), '줄')


if __name__ == '__main__':
    main()
