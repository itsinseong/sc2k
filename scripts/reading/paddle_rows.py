"""PaddleOCR-VL 마크다운 속 표(HTML)를 claude_read.py와 같은 형태 {circulation, reserve_fair_value, rows}로 바꾼다."""
import re, sys, json
from html.parser import HTMLParser

class T(HTMLParser):
    def __init__(s): super().__init__(); s.tables, s.row, s.cell = [], None, None
    def handle_starttag(s, tag, a):
        if tag == 'table': s.tables.append([])
        elif tag == 'tr': s.row = []
        elif tag == 'td': s.cell = ''
    def handle_endtag(s, tag):
        if tag == 'td': s.row.append(s.cell.strip()); s.cell = None
        elif tag == 'tr': s.tables[-1].append(s.row)
    def handle_data(s, d):
        if s.cell is not None: s.cell += d

def num(c):
    c = c.replace('$', '').strip()  # "$ -"도 0으로 본다
    if c in ('-', '–', '—'): return 0
    d = re.sub(r'[^\d]', '', c)
    return None if not d else (-1 if '(' in c else 1) * int(d)

def rows_of(md):
    p = T(); p.feed(md)
    top, body = p.tables[0], p.tables[1]
    def two(r):  # 끝에 붙은 빈 칸은 떼고 마지막 두 칸
        while r and r[-1] == '': r = r[:-1]
        return [num(r[-2]), num(r[-1])] if len(r) >= 2 else [None, None]
    got = {'circulation': two(top[1]), 'reserve_fair_value': two(top[2]), 'rows': []}
    for r in body[1:]:
        label = next((c for c in r if c and num(c) is None), '') if len(r) < 3 else (r[0] or '')
        vals = two(r) if len(r) >= 3 else [None, None]
        got['rows'].append({'label': label, 'values': vals})
    return got

if __name__ == '__main__':
    print(json.dumps(rows_of(open(sys.argv[1]).read()), ensure_ascii=False)[:600])
