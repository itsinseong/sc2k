"""Gemini OCR 쪽(4쪽)을 PaddleOCR-VL(paddle/<달>.json)과 Claude Opus(claude_opus_<달>.json) 글로 채워 parse_gemini.parse를 부르고,
data/reports_gemini.json(Vision 판독 정답)과 필드마다 대조한다. 레포 파일은 고치지 않는다(이 실행 안에서만 text_of, ocr_boxes를 바꾼다).
글 모양만 맞춘다: 윗첨자 표기($ ^{1} $, ¹)를 숫자 한 글자로, 표 칸을 공백 3칸으로 잇는다. 숫자는 손대지 않는다.
사용: python3 scripts/reading/gemini/compare_gemini.py > docs/research/읽기엔진시험_2026-10-09/gemini/compare.txt"""
import html, json, pathlib, re, subprocess, sys
W = pathlib.Path(__file__).resolve().parent
REPO = W.parents[2]
G = REPO / 'docs/research/읽기엔진시험_2026-10-09/gemini'  # 읽은 결과
sys.path.insert(0, str(REPO / 'scripts'))
import parse_gemini as pg

MONTHS = ['2024-10', '2026-03']
PAGE = 4
base = {r['month']: r for r in json.loads((REPO / 'data/reports_gemini.json').read_text())['reports']}
SUP = str.maketrans('¹²³⁴', '1234')


def norm(s):
    s = re.sub(r'\s*\$\s*\^\{\s*\\textregistered\s*\}\s*\$', '®', s)
    s = re.sub(r'\s*\$\s*\^\{(.*?)\}\s*\$', r'\1', s)
    return s.translate(SUP)


def paddle_page(month):
    """블록을 위에서 아래로. 표는 줄마다 칸을 잇는다. 글상자 = (위쪽y 비율, 왼쪽x 비율, 줄), 블록 안 줄은 블록 높이를 줄 수로 나눠 y를 준다."""
    d = json.loads((G / f'paddle/{month}.json').read_text())
    H, Wd = d['height'], d['width']
    lines, boxes = [], []
    for b in sorted(d['parsing_res_list'], key=lambda b: (b['block_bbox'][1], b['block_bbox'][0])):
        x0, y0, x1, y1 = b['block_bbox']
        if b['block_label'] == 'table':
            ls = ['   '.join(html.unescape(re.sub(r'<.*?>', '', c)).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)).strip()
                  for tr in re.findall(r'<tr>(.*?)</tr>', b['block_content'], re.S)]
        else:
            ls = [l for l in b['block_content'].split('\n') if l.strip()]
        ls = [norm(l) for l in ls]
        for k, l in enumerate(ls):
            boxes.append(((y0 + (y1 - y0) * k / len(ls)) / H, x0 / Wd, l))
        lines += ls
    return '\n'.join(lines), boxes, d


def claude_page(month):
    env = json.loads((G / f'claude_opus_{month}.json').read_text())
    t = env['result']; got = json.loads(t[t.index('{'):t.rindex('}') + 1])
    out = []
    for ln in got['lines']:
        if ln['text'] and ln['text'].startswith('[signature image'): continue  # 내가 시킨 주석 줄, 쪽 글이 아님
        out.append(norm('   '.join([ln['text'] or ''] + [v if v is not None else '' for v in (ln['values'] or [])])))
    return '\n'.join(out), got, env


def run_parse(month, page_text, boxes):
    """pg.text_of와 같되 빈 쪽을 page_text로 채운다(Vision 전용 쉼표/소수점 교정은 하지 않음). 서명 위치는 boxes로."""
    def text_of(pdf):
        text = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
        pages = text.split('\x0c')
        if pages[-1] == '': pages.pop()
        blank = [i for i, p in enumerate(pages, 1) if not p.strip()]
        assert blank == [PAGE], blank
        pages[PAGE - 1] = page_text
        return '\x0c'.join(pages) + '\x0c', blank
    pg.text_of = text_of
    pg.ocr_boxes = lambda pdf, page, dpi=200: boxes if page == PAGE else []
    try:
        return pg.parse(REPO / f'data/samples/Gemini_GUSD_Examination_{month}.pdf')
    except Exception as e:
        return {'ok': False, 'error': f'{type(e).__name__}: {e}'}


def flat(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items(): yield from flat(v, f'{p}.{k}' if p else k)
    elif isinstance(o, list) and o and isinstance(o[0], (dict, list)):
        for i, v in enumerate(o): yield from flat(v, f'{p}[{i}]')
    else: yield p, o


def diff(got, want):
    g, w = dict(flat(got)), dict(flat(want))
    out = []
    for k in sorted(set(g) | set(w)):
        if g.get(k, '∅') != w.get(k, '∅'): out.append((k, g.get(k, '∅'), w.get(k, '∅')))
    return out


def facts(page_text):
    """두 독자 줄 대조용: 날짜, 표 줄(종류, 칸 둘 센트), 서명 블록, 각주."""
    rows = pg.table_rows(page_text, PAGE)
    f = {'dates': re.findall(pg.DATE, page_text)}
    f.update({f'row:{k}': cs for k, _, cs, _ in rows})
    circ = re.search(pg.loose('GUSD issued and in circulation') + r'\S{0,2}\s+(' + pg.AMT + r')\s+(' + pg.AMT + ')', page_text)
    f['row:circulation'] = [pg.cents(circ[1]), pg.cents(circ[2])] if circ else None
    sig = re.search(rf'\n\s*([A-Z][\w.]+(?: [A-Z][\w.]+)+)\s*\n\s*((?:Interim )?(?:CEO/President|CFO|Chief [A-Za-z ]+ Officer))\s*\n\s*(Gemini [A-Za-z ,.]+?)\s*\n\s*({pg.DATE})', page_text)
    f['signature_block'] = list(sig.groups()) if sig else None
    for n in '123':
        m = re.search(rf'^\s*{n}\s*(\S.*)$', page_text, re.M)
        f[f'footnote{n}'] = re.sub(r'\s+', ' ', m[1]).strip() if m else None
    return f


def all_lines(t):
    """전체 줄 대조용: 글머리표(•, o), $, 밑줄 칸(___), DocuSign 틀의 앞 대시만 떼고 공백을 하나로. 글자와 숫자는 그대로."""
    out = []
    for l in t.split('\n'):
        l = re.sub(r'^\s*[•o-]\s+|^-(?=DocuSigned)', '', l).replace('$', ' ')
        l = re.sub(r'\s*_{2,}\s*$', '', re.sub(r'\s+', ' ', l)).strip()
        if l: out.append(l)
    return out


LAYOUT = re.compile(r'(\.line$|\.where\.line$|^field_notes\..*\.line$)')
if __name__ == '__main__':
    for month in MONTHS:
        b = base[month]
        print(f'\n######## {month}')
        readers = {}
        if (G / f'paddle/{month}.json').exists():
            t, bx, d = paddle_page(month); readers['paddle'] = (t, bx)
            (G / f'paddle_text_{month}.txt').write_text(t)
        if (G / f'claude_opus_{month}.json').exists() and (G / f'claude_opus_{month}.json').stat().st_size:
            t, got, env = claude_page(month)
            # Claude는 좌표가 없다. 서명 위치는 PaddleOCR 글상자를 빌린다(없으면 빈 목록 -> 서명 확인 실패).
            readers['claude'] = (t, readers.get('paddle', (None, []))[1])
            (G / f'claude_text_{month}.txt').write_text(t)
        F = {}
        for name, (t, bx) in readers.items():
            try: F[name] = facts(t)
            except Exception as e: F[name] = {'error': repr(e)}
        if len(F) == 2:
            print('-- 두 독자 줄 대조 (paddle | claude)')
            for k in sorted(set(F['paddle']) | set(F['claude'])):
                a, c = F['paddle'].get(k, '∅'), F['claude'].get(k, '∅')
                print(f"  {'같음' if a == c else '다름'}  {k}: {a}" + ('' if a == c else f'  |  {c}'))
            import difflib
            pl, cl = all_lines(readers['paddle'][0]), all_lines(readers['claude'][0])
            ops = [o for o in difflib.SequenceMatcher(None, pl, cl, autojunk=False).get_opcodes() if o[0] != 'equal']
            print(f'-- 전체 줄 대조: paddle {len(pl)}줄, claude {len(cl)}줄, 다른 곳 {len(ops)}군데')
            for tag, i1, i2, j1, j2 in ops: print(f'   {tag}: paddle {pl[i1:i2]}  |  claude {cl[j1:j2]}')
        for name, (t, bx) in readers.items():
            r = run_parse(month, t, bx)
            print(f'-- {name}: parse ok={r.get("ok")}' + (f' error={r["error"]}' if 'error' in r else ''))
            ds = diff(r, b)
            val = [x for x in ds if not LAYOUT.search(x[0])]
            lay = [x for x in ds if LAYOUT.search(x[0])]
            print(f'   정답과 다른 값 필드 {len(val)}개, 줄 번호만 다른 필드 {len(lay)}개')
            for k, g, w in val: print(f'   값 다름 {k}: 얻음={g!r}  정답={w!r}')
            for k, g, w in lay: print(f'   줄번호 {k}: {g} (정답 {w})')
