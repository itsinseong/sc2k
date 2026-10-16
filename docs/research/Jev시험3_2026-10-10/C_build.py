"""갈래 C: R15 어려운 문항 만들기. 실행: python3 C_build.py (레포 루트에서). pdftotext만 부른다."""
import json, re, subprocess, hashlib
OUT = 'docs/research/Jev시험3_2026-10-10/'
def pdf_pages(pdf):  # scripts/jev/jev_choice_test.py pdf_pages와 같은 방식
    raw = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True, check=True).stdout
    pages = raw.split('\x0c')
    if pages and pages[-1] == '': pages.pop()
    return ['\n'.join(re.sub(r'\s{2,}', '  ', ln).strip() for ln in p.splitlines() if ln.strip()) for p in pages]
def join(pg): return '\n\n'.join(f'[page {i}]\n{p}' for i, p in enumerate(pg, 1) if p)
GOLD15 = json.load(open('docs/research/Jev시험2_2026-10-09/goldset_hard.json'))['yesno']['items']
old = {(x['source'], x['gold']) for x in GOLD15 if x['rule'] == 'R15'}

# (id, 파일, 상태 이름, 지울 줄 번호 범위들, 지울 줄 첫머리 확인, 어려운 이유, 근거 문장)
SPEC = [
 ('C-01', 'Circle_USDC_Examination_2025-06', 'USDC document, 2025-06', [(148, 151)],
  ['Tamara Schulz', 'Chief Accounting Officer', 'Circle Internet Group, Inc.', 'July 30, 2025'],
  'Circle 서식에서 마지막 쪽 서명 4줄만 지움. 회계법인 보고서와 "Circle Group management asserts" 경영진 주장문은 그대로 남음'),
 ('C-02', 'Circle_EURC_Examination_2024-09', 'EURC document, 2024-09', [(88, 91)],
  ['Tamara Schulz', 'Chief Accounting', 'Circle Internet Group, Inc.', 'October 30, 2024'],
  '짧은 EURC 문서에서 서명 4줄만 지움. 경영진 주장문("management asserts")과 "management is responsible" 문장이 남음'),
 ('C-03', 'Paxos_PYUSD_Examination_2024-06', 'PYUSD document, 2024-06', [(151, 153)],
  ['Adam Ackermann, Head of Portfolio Management', 'Paxos Trust Company, LLC', 'July 17, 2024'],
  '서명자 이름과 직함 줄만 지움. "To the best of the knowledge and belief of the undersigned" 확인 문장과 "REDEMPTION ASSETS REPORT" 제목이 서명자 없이 남음'),
 ('C-04', 'Paxos_USDP_Examination_2023-05', 'USDP document, 2023-05', [(169, 172)],
  ['Jennifer Kattamis, Controller', 'Paxos Trust Company, LLC', '6/22/2023', 'Date'],
  '서명자(Controller)와 날짜 줄만 지움. "undersigned" 확인 문장이 남고 앞에 회계법인의 "Examination of Management Assertions"가 길게 있음'),
 ('C-05', 'Gemini_GUSD_Examination_2025-04', 'GUSD document, 2025-04', [(95, 100)],
  ['_____', 'Marshall Beard', 'CEO/President', 'Gemini Trust Company, LLC', 'May 29, 2025', '_____'],
  '서명 줄과 서명 블록 6줄을 지움. 본문에 "we assert that the Company has complied" 경영진 확인 문장이 남음'),
 ('C-06', 'Ripple_RLUSD_Examination_2026-03', 'RLUSD document, 2026-03', [(100, 104)],
  ['________', 'Jack McDonald', 'Chief Executive Officer', 'Standard Custody & Trust Company, LLC', 'April 27, 2026'],
  '서명 블록 5줄을 지움. "The Company\'s Management asserts" 경영진 주장문과 회계법인 보고서가 남음'),
 ('C-07', 'Paxos_USDG_Examination_2026-03', 'USDG document, 2026-03', [(209, 216)],
  ['Wee Siang Lee', 'Executive Director', 'Paxos Digital Singapore Pte. Ltd.', 'April 29, 2026', 'Tero Reuna', 'Head of EU', 'Paxos Issuance Europe Oy', 'April 29, 2026'],
  '두 법인 서명자 2명(8줄)을 모두 지움. 합리적 확신 보고서가 "Board of Directors and Management"에게 보내는 글로 시작하고 "undersigned" 확인 문장이 남음'),
 ('C-08', 'Tether_USDT_Assurance_2025-09', 'USDT document, 2025-09', [(177, 177), (204, 204), (240, 240), (301, 301), (334, 334), (338, 340), (342, 342), (379, 379)],
  ['Authorized & approved on 31 October 2025', 'Authorized & approved on 31 October 2025', 'Authorized & approved on 31 October 2025', 'Authorized & approved on 31 October 2025',
   'Authorized & approved on 31 October 2025', 'Authorized and approved by the Board of Directors', 'the Board of Directors by Giancarlo Devasini', 'Giancarlo Devasini',
   'Authorized & approved on 31 October 2025', 'Authorized & approved on 31 October 2025'],
  '이사회 승인 문단(Giancarlo Devasini, 이사회 의장)과 쪽마다 있는 "Authorized & approved on" 줄 7개를 모두 지움. 긴 재무제표형 문서라 서명이 쪽 구석에만 있었다는 점을 찾아야 함'),
]
KEEP = {}  # name -> 남길 쪽 번호. 아래에서 자동 계산(첫 쪽, 지운 줄이 있던 쪽, 경영진 주장 문장이 있는 첫 쪽)
def cut(text, name):
    if name not in KEEP: return text
    ch = re.split(r'\n\n(?=\[page \d+\]\n)', text)
    return '\n\n'.join(c for c in ch if int(re.match(r'\[page (\d+)\]', c)[1]) in KEEP[name])
YES_PAIR = {'C-01': 'C-09', 'C-05': 'C-10', 'C-07': 'C-11'}
KNOWN = {}  # Jev 답은 아직 모름
items = []
def mk(iid, name, label, text, gold, basis, loc, tag, synth):
    src = f'data/samples/{name}.pdf'
    return dict(id=iid, kind='yesno', rule='R15', input=f'document: {label}\ntext:\n{text}', gold=gold, gold_basis=basis,
                source_file=src, source_locator=loc, tag=tag, jev_known='', synthetic=synth)
for iid, name, label, rngs, heads, tag in SPEC:
    src = f'data/samples/{name}.pdf'
    lines = join(pdf_pages(src)).splitlines()
    drop = []
    for a, b in rngs: drop += list(range(a, b + 1))
    assert len(drop) == len(heads), iid
    for i, h in zip(drop, heads): assert lines[i].startswith(h) or h in lines[i], (iid, i, lines[i], h)
    removed = [lines[i] for i in drop]
    pgof, cur = {}, 0
    for i, l in enumerate(lines):
        m = re.fullmatch(r'\[page (\d+)\]', l)
        if m: cur = int(m[1])
        pgof[i] = cur
    keep = {1} | {pgof[i] for i in drop}
    for i, l in enumerate(lines):
        if re.search(r'(management asserts|Management asserts|we assert that|makes the following assertions|undersigned)', l): keep.add(pgof[i]); break
    keep |= {'Paxos_PYUSD_Examination_2024-06': {3}, 'Paxos_USDP_Examination_2023-05': {3}, 'Paxos_USDG_Examination_2026-03': {2}}.get(name, set())
    if name.startswith('Tether'): keep = {1, 2, 6, 11}
    KEEP[name] = sorted(keep)
    kept = cut('\n'.join(l for i, l in enumerate(lines) if i not in set(drop)), name)
    # 남은 글에서 이름+직함 점검용 출력
    chk = [l for l in kept.splitlines() if re.search(r'(Chief .*Officer|Head of|Executive Director|\bCEO\b|\bCFO\b|Controller|Chairman|Administrator|President|VP,)', l)]
    print(iid, name, 'removed', len(removed), '| 남은 직함 후보 줄:', chk)
    loc = ' / '.join(removed[:4])
    first = removed[0] if not removed[0].startswith('_') else removed[1]
    if name in KEEP: tag += f' (입력은 원래 {KEEP[name]}쪽만 남김)'
    ndiff = f'원 문서 {name}.pdf의 서명 블록({loc})을 지운 글(합성). 남은 글 어디에도 이름과 직함이 서명이나 승인 문장과 함께 있지 않아 질문 기준으로 아니오.'
    items.append(mk(iid, name, label, kept, 'no', ndiff, loc, tag, True))
    if iid in YES_PAIR:
        full = cut(join(pdf_pages(src)), name)
        yb = f'원 문서 그대로. 서명 블록 "{loc}"가 이름, 직함, 회사와 함께 문서에 있으므로 예. {iid}와 같은 문서에서 서명 줄만 다름.'
        items.append(mk(YES_PAIR[iid], name, label, full, 'yes', yb, loc, f'{iid}의 짝(서명이 있는 원본). 같은 서식에서 서명 유무만 다름', False))
        items[-1]['pair_of'] = iid
LOCFIX = {'C-07': 'Wee Siang Lee / Executive Director / Paxos Digital Singapore Pte. Ltd. / April 29, 2026 // Tero Reuna / Head of EU / Paxos Issuance Europe Oy / April 29, 2026',
          'C-08': 'Authorized and approved by the Board of Directors on 31 October 2025 and signed on behalf of / the Board of Directors by Giancarlo Devasini, as Chairman of the Board of Directors:'}
for it in items:
    base = it.get('pair_of') or it['id']
    if base in LOCFIX:
        old = it['source_locator']; it['source_locator'] = LOCFIX[base]
        it['gold_basis'] = it['gold_basis'].replace(old if it['gold'] == 'yes' else old.replace(' / ', ' / '), LOCFIX[base]) if old in it['gold_basis'] else it['gold_basis']
    it['gold_basis'] = it['gold_basis'].replace('와 같은 문서에서', '과 같은 문서에서').replace('C-05과', 'C-05와')
items.sort(key=lambda x: x['id'])
# 기존 세트와 같은 문항이 없는지
for it in items:
    for x in GOLD15:
        if x['rule'] == 'R15': assert not (x['text'] == it['input'].split('text:\n', 1)[1] and (x['gold'] is True) == (it['gold'] == 'yes')), it['id']
json.dump(items, open(OUT + 'C_items.json', 'w'), ensure_ascii=False, indent=1)
print(len(items), [ (i['id'], i['gold']) for i in items])
