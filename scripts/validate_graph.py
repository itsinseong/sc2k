#!/usr/bin/env python3
"""근거 그래프 검사. 간선의 quote가 코퍼스 원문에 있는지, 스키마를 지키는지 본다.
사용: python3 scripts/validate_graph.py [--fix]  (--fix면 불일치 간선의 verified를 "partial"로 바꿔 저장)
"""
import json, re, sys, glob, pathlib, xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parent.parent
FIX = '--fix' in sys.argv
def norm(s):
    s = (s or '').translate(str.maketrans({'“':'"','”':'"','‘':"'",'’':"'"}))
    s = re.sub(r'-\s*\d{1,3}\s*-', '', s)          # PDF 쪽 번호 "- 17 -"
    return re.sub(r'\s+', '', s)
def law_text(root):
    parts = []
    for el in root.iter():
        if el.tag.endswith('내용') and el.text: parts.append(el.text)
    return ''.join(parts)
def segs(q):
    out = []
    for s in re.split(r'\(\.\.\.\)|\.\.\.|…|\(\s*\)', norm(q)):
        s = s.strip('.,;:()[]「」"\'’“”·ㆍ-')
        if len(s) >= 8: out.append(s)
    return out
def load_sources():
    src = {}
    for f in glob.glob(str(ROOT/'graph/corpus/law/*.xml')):
        try: src[pathlib.Path(f).name] = norm(law_text(ET.fromstring(open(f,'rb').read())))
        except Exception: pass
    for f in glob.glob(str(ROOT/'graph/corpus/bills/*_원문.txt')) + glob.glob(str(ROOT/'graph/corpus/bills/*검토보고서.txt')) + glob.glob(str(ROOT/'graph/corpus/gov/*.txt')):
        src[pathlib.Path(f).name] = norm(open(f, encoding='utf-8').read())
    return src
def find(doc, src):
    if not doc: return None
    kind, *rest = doc.split(':')
    if kind == 'law':
        key = rest[-1]
        for n, t in src.items():
            if n.endswith('.xml') and key in n: return t
    if kind == 'bill':
        for n, t in src.items():
            if n.startswith(rest[0]) and n.endswith('_원문.txt'): return t
    if kind == 'gov' and 'assembly' in rest[0]:
        for n, t in src.items():
            if '검토보고서' in n: return t
    if kind == 'gov' and 'bok' in rest[0]:
        for n, t in src.items():
            if '한국은행' in n: return t
    return None
LAYERS = {1, 2, 3, 4, 5, 'foreign', None}
def main():
    src = load_sources(); hard = 0; checked = 0; partial = 0; skipped = 0; schema_err = 0
    for ef in sorted(glob.glob(str(ROOT/'graph/edges/*.json'))):
        edges = json.load(open(ef, encoding='utf-8')); changed = False
        for e in edges:
            for k in ('axis', 'layer', 'doc', 'quote', 'verified', 'confirmed'):
                if k not in e: print(f'SCHEMA {pathlib.Path(ef).name}: 필드 없음 {k}'); schema_err += 1
            if e.get('layer') not in LAYERS: print(f'SCHEMA {pathlib.Path(ef).name}: layer {e.get("layer")!r}'); schema_err += 1
            if e.get('confirmed') and not (e.get('confirmed_by') and e.get('confirmed_at')):
                print(f'SCHEMA {pathlib.Path(ef).name}: confirmed인데 confirmed_by/at 없음 {e.get("doc")}'); schema_err += 1
            if e.get('verified') is not True or not e.get('quote'): continue
            t = find(e.get('doc'), src)
            if t is None: skipped += 1; continue
            checked += 1
            miss = [s for s in segs(e['quote']) if s not in t]
            if miss:
                hard += 1
                print(f'MISMATCH {pathlib.Path(ef).name} {e["axis"]} {e["doc"]} {e.get("article")}: {[m[:28] for m in miss][:2]}')
                if FIX:
                    e['verified'] = 'partial'; e['note'] = ((e.get('note') or '') + ' [validate] 인용 세그먼트가 원문과 불일치, 축약 인용').strip(); changed = True; partial += 1
        if changed: json.dump(edges, open(ef, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'checked {checked}, mismatch {hard}, skipped(로컬 원문 없음) {skipped}, schema errors {schema_err}' + (f', set partial {partial}' if FIX else ''))
    return 1 if (hard and not FIX) or schema_err else 0
if __name__ == '__main__': sys.exit(main())
