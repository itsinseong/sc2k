#!/usr/bin/env python3
"""Check the T-bill CUSIP rows PaddleOCR-VL read from the 21 Ripple RLUSD reserve reports.

Stdlib only.  Run: python3 scripts/reading/cusip_check.py
Reads   docs/research/읽기엔진시험_2026-10-09/paddle/ripple_YYYY-MM.md  and (read-only) data/reports_ripple.json
Calls   Treasury FiscalData auctions_query once per CUSIP (cache: docs/research/읽기엔진시험_2026-10-09/fiscaldata_cache.json)
Writes  docs/research/읽기엔진시험_2026-10-09/cusip_results.txt
OCR values are reported as read, never corrected.
"""
import calendar, datetime as dt, glob, json, os, pathlib, re, sys, time
import urllib.parse, urllib.request

HERE = pathlib.Path(__file__).resolve().parent                  # scripts/reading
D = str(HERE.parents[1] / 'docs/research/읽기엔진시험_2026-10-09')
sys.dont_write_bytecode = True      # keep __pycache__ untouched
sys.path.insert(0, str(HERE))
from paddle_rows import T           # existing parser: <table> -> rows -> cells

REF = str(HERE.parents[1] / 'data/reports_ripple.json')
CACHE, OUT = D + '/fiscaldata_cache.json', D + '/cusip_results.txt'
API = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query'
MON = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
SUB = re.compile(r'(total\s+u\.?\s*s\.?\s+treasury|subtotal)', re.I)
NINE = re.compile(r'[0-9A-Z]{9}')
cache = {}


# ---------- small pure helpers -------------------------------------------------
def pdate(s):
    """'August 18, 2026' or '12/24/2024' -> date; None if absent/unparseable (never guessed)."""
    s = (s or '').strip()
    try:
        m = re.fullmatch(r'([A-Za-z]+)\s*(\d{1,2})\s*,\s*(\d{4})', s)
        if m and m[1].lower() in MON: return dt.date(int(m[3]), MON[m[1].lower()], int(m[2]))
        m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
        if m: return dt.date(int(m[3]), int(m[1]), int(m[2]))
    except ValueError:
        pass
    return None


def cd(c8):
    """CUSIP check digit of the first 8 chars (None if a char is not allowed)."""
    s = 0
    for i, ch in enumerate(c8):
        v = int(ch) if ch in '0123456789' else ord(ch) - 55 if 'A' <= ch <= 'Z' else {'*': 36, '@': 37, '#': 38}.get(ch)
        if v is None: return None
        if i % 2: v *= 2
        s += v // 10 + v % 10
    return (10 - s % 10) % 10


def cusip_ok(c):
    """True/False; None when the code is not 9 chars long."""
    if len(c) != 9: return None
    d = cd(c[:8])
    return d is not None and c[8] == str(d)


def toks(cells):
    """Value tokens of a row.  '$' and '<fcel>' are stripped and empty cells (incl. trailing '') dropped,
    so '$ -' -> '-' (= 0) and the last token is always the month-end value."""
    return [t for c in cells for t in c.replace('<fcel>', ' ').replace('$', ' ').split()]


def val(t):
    if t in ('-', '–', '—'): return 0
    d = t.strip('()').replace(',', '')
    if not (d.isascii() and d.isdigit()): return None
    return -int(d) if t.startswith('(') else int(d)


def fm(n): return 'None' if n is None else f'{n:,}'


def selftest():
    assert cusip_ok('91282CRQ6') and cusip_ok('912810UW6'), 'check digit function broken'
    assert cusip_ok('91282CRQ7') is False and cusip_ok('91279TZ0') is None
    assert [val(t) for t in toks(['$ 39,456,447', '$ -', ''])] == [39456447, 0]     # 2025-01 MZ7 row
    assert pdate('August 18, 2026') == dt.date(2026, 8, 18) and pdate('12/24/2024') == dt.date(2024, 12, 24)
    assert pdate('Feb 30, 2025') is None and pdate('') is None


# ---------- FiscalData ---------------------------------------------------------
def omats(c):
    """Sorted distinct official maturity dates (ISO) of CUSIP c.
    [] = unknown to FiscalData; None = not looked up (not a 9-char A-Z/0-9 code) or request failed."""
    if not NINE.fullmatch(c): return None
    if c not in cache:
        q = urllib.parse.urlencode({'filter': f'cusip:eq:{c}', 'page[size]': 1000,
                                    'fields': 'cusip,security_type,security_term,issue_date,maturity_date'}, safe=':,')
        for k in range(4):
            try:
                req = urllib.request.Request(f'{API}?{q}', headers={'User-Agent': 'cusip-check/1.0'})
                with urllib.request.urlopen(req, timeout=30) as r:
                    cache[c] = json.load(r)['data']
                break
            except Exception:
                time.sleep(2 * (k + 1))
        else:
            return None                      # not cached -> retried on the next run
        with open(CACHE, 'w') as f: json.dump(cache, f, indent=1, sort_keys=True)
        time.sleep(0.3)
    return sorted({x['maturity_date'] for x in cache[c]})


# ---------- OCR table ----------------------------------------------------------
def parse(path):
    """-> (header dates, has maturity column, CUSIP rows, subtotal value tokens)."""
    p = T(); p.feed(open(path, encoding='utf-8').read())
    tb = next(t for t in p.tables if any(r and r[0].strip().upper() == 'CUSIP' for r in t))
    dates = next(([pdate(c) for c in r if pdate(c)] for r in tb if sum(bool(pdate(c)) for c in r) >= 2), [])
    h = next(i for i, r in enumerate(tb) if r and r[0].strip().upper() == 'CUSIP')
    mat_col = len(tb[h]) > 1 and 'matur' in tb[h][1].lower()
    rows, sub = [], None
    for r in tb[h + 1:]:
        lab = r[0].strip() if r else ''
        if SUB.match(lab):
            sub = [val(t) for t in toks(r[1:])]
            break
        rows.append({'cusip': lab, 'mat_raw': r[1].strip() if mat_col and len(r) > 1 else None,
                     'v': [val(t) for t in toks(r[2:] if mat_col else r[1:])], 'cells': r})
    return dates, mat_col, rows, sub


def ref_treasury(rep):
    """CUSIP -> (month-end amount, maturity ISO) of the reference treasury holdings."""
    out = {}
    for h in rep['holdings']:
        if str(h.get('kind', '')).startswith('treasury'):
            m = re.search(r'CUSIP\s+(\S+)', h['label'])
            out[m[1] if m else h['label']] = (h['amount'], h.get('maturity_date'))
    return out


def diag_short(rows):
    """Diagnostic only, never counted as a pass.  For codes one char short: (1) a CUSIP already known to FiscalData
    with the OCR maturity that equals the code after deleting one char; (2) else the same (position, char)
    insertion learned from (1) on the other rows, accepted if check digit and official maturity both fit."""
    out, learned = {}, set()
    for r in rows:
        c = r['cusip']
        for k in sorted(cache):
            if len(k) == len(c) + 1 and cache[k] and {x['maturity_date'] for x in cache[k]} == {r['mi']}:
                i = next((i for i in range(len(k)) if k[:i] + k[i + 1:] == c), None)
                if i is not None:
                    out[c] = f'OCR code = official CUSIP {k} (official maturity = OCR maturity) minus its char #{i + 1} ({k[i]})'
                    learned.add((i, k[i]))
                    break
    for r in rows:
        c = r['cusip']
        for i, ch in sorted(learned):
            k = c[:i] + ch + c[i:]
            if c not in out and cusip_ok(k) and omats(k) == [r['mi']]:
                out[c] = f'inserting {ch} as char #{i + 1} (as on the other rows) gives {k}: valid check digit, official maturity = OCR maturity'
    return out


def analyse(month, path, rep):
    dates, mat_col, rows, sub = parse(path)
    asof = dt.date.fromisoformat(rep['as_of'])
    ref = ref_treasury(rep)
    ref_mat = {v[1]: (c, v[0]) for c, v in ref.items()}
    iss, notes, paired = [], [], set()                 # iss/notes: (cusip, text)
    for r in rows:                                     # pass 1: facts
        c, v = r['cusip'], r['v']
        r['mid'], r['end'] = (v[0] if v else None), (v[-1] if len(v) > 1 else None)
        r['m'] = pdate(r['mat_raw'])
        r['mi'] = r['m'].isoformat() if r['m'] else None
        r['chk'] = cusip_ok(c)
        om = omats(c)
        r['om'] = om[0] if om and len(om) == 1 else None
        r['ms'] = ('skip' if om is None and not NINE.fullmatch(c) else 'apierr' if om is None else 'notfound' if not om
                   else 'multi' if len(om) > 1 else 'noocr' if not r['mi'] else 'match' if om[0] == r['mi'] else 'mismatch')
        r['omall'] = om
    dg = diag_short([r for r in rows if len(r['cusip']) == 8])
    for r in rows:                                     # pass 2: problems per row
        c, mi = r['cusip'], r['mi']
        p = []
        if r['chk'] is None: p.append(f'CHK: length {len(c)} (need 9), check digit not computable')
        elif not r['chk']: p.append(f'CHK: check digit fails (9th char {c[8]}, expected {cd(c[:8])})')
        p.append({'match': '',
                  'skip': 'MAT: not checkable, code is not a 9-char A-Z/0-9 string (not looked up)',
                  'apierr': 'MAT: FiscalData request failed',
                  'notfound': 'MAT: CUSIP not found in FiscalData',
                  'multi': f'MAT: official maturity differs between auctions {r["omall"]} (OCR {r["mat_raw"]!r})',
                  'noocr': f'MAT: no usable maturity in OCR row (raw {r["mat_raw"]!r})',
                  'mismatch': f'MAT: OCR {mi} vs official {r["om"]}'}[r['ms']])
        if c in dg: p.append('DIAG (not counted): ' + dg[c])
        if r['end']:
            if c in ref:
                if r['end'] != ref[c][0]: p.append(f'AMT: OCR month-end {fm(r["end"])} vs ref {fm(ref[c][0])}')
            else:
                rc = ref_mat.get(mi)
                hint = ''
                if rc:
                    paired.add(rc[0])
                    hint = (f'; ref CUSIP {rc[0]} has the same maturity and ' +
                            ('the same amount' if rc[1] == r['end'] else f'amount {fm(rc[1])}') +
                            f' (ref check digit {"ok" if cusip_ok(rc[0]) else "FAILS"}, official maturity {omats(rc[0])})')
                p.append(f'AMT: OCR month-end {fm(r["end"])} under a CUSIP that is not in the reference holdings{hint}')
        elif c in ref:
            p.append(f'AMT: OCR month-end {"missing" if r["end"] is None else 0} vs ref {fm(ref[c][0])}')
        mat = r['om'] or mi
        if r['end'] and mat and dt.date.fromisoformat(mat) <= asof:
            p.append(f'STATE: month-end value {fm(r["end"])} but maturity {mat} is on/before as_of {asof}')
        if r['mid'] and mat and len(dates) == 2 and dt.date.fromisoformat(mat) <= dates[0]:
            p.append(f'STATE: mid-month value {fm(r["mid"])} but maturity {mat} is on/before {dates[0]}')
        if len(r['v']) != 2 or None in r['v']:
            notes.append((c, f'{len(r["v"])} value cells {r["v"]} (first=mid-month, last=month-end); raw cells {r["cells"]}'))
        p = [x for x in p if x]
        if p: iss.append((c, '; '.join(p)))

    nz = [r for r in rows if r['end']]
    amt = {}
    for r in nz: amt[r['cusip']] = amt.get(r['cusip'], 0) + r['end']
    if len(amt) != len(nz): iss.append(('-', 'DUP: same CUSIP on several rows with a month-end value'))
    for c, (a, rm) in ref.items():                     # reference CUSIPs no OCR row carries and no OCR row was paired with
        if c in paired or any(r['cusip'] == c for r in rows): continue
        same = [r for r in rows if r['mi'] == rm]
        iss.append((c, f'ONLY_REF: ref holds {fm(a)} (maturity {rm}), no OCR row has this CUSIP; '
                       + (f'OCR row with same maturity: {same[0]["cusip"]!r} month-end {fm(same[0]["end"])}' if same else 'no OCR row with same maturity')
                       + f'; ref check digit {"ok" if cusip_ok(c) else "FAILS"}, official maturity {omats(c)}'))
    union = set(amt) | set(ref)
    eq = sum(amt.get(c) == ref[c][0] for c in union if c in ref)
    bm, rm_ = {}, {v[1]: v[0] for v in ref.values()}   # same comparison keyed by maturity date (diagnostic)
    for r in nz: bm[r['mi']] = bm.get(r['mi'], 0) + r['end']
    um = set(bm) | set(rm_)
    eqm = sum(bm.get(k) == rm_[k] for k in um if k in rm_)

    s_end, s_mid = sum(r['end'] or 0 for r in rows), sum(r['mid'] or 0 for r in rows)
    sub_mid, sub_end = (sub[0] if sub else None), (sub[-1] if sub and len(sub) > 1 else None)
    se, sm = sub_end is not None and s_end == sub_end, sub_mid is not None and s_mid == sub_mid
    if not se: iss.append(('-', f'SUM_END: CUSIP rows sum {fm(s_end)} vs subtotal {fm(sub_end)}'))
    if not sm: iss.append(('-', f'SUM_MID: CUSIP rows sum {fm(s_mid)} vs subtotal {fm(sub_mid)}'))
    if sub is None or len(sub) != 2 or None in sub: notes.append(('-', f'subtotal row value cells {sub}'))
    sr = sub_end == rep['components'].get('treasury')
    if not sr: iss.append(('-', f'SUB: OCR subtotal month-end {fm(sub_end)} vs ref components.treasury {fm(rep["components"].get("treasury"))}'))
    if len(dates) != 2 or dates[1] != asof: iss.append(('-', f'ASOF: OCR header dates {[str(x) for x in dates]} vs ref as_of {asof}'))

    off = [(dt.date.fromisoformat(r['om']) - asof).days if r['om'] else None for r in nz]
    ocr = [(r['m'] - asof).days if r['m'] else None for r in nz]
    md_off = max(off) if off and None not in off else None
    md_ocr = max(ocr) if ocr and None not in ocr else None
    ref_md = rep.get('treasury_max_maturity_days')
    mdst = 'NA' if nz and md_off is None else 'OK' if md_off == ref_md else 'DIFF'
    if mdst != 'OK':
        iss.append(('-', f'MAXD: official-maturity based {md_off} (OCR-date based {md_ocr}) vs ref treasury_max_maturity_days {ref_md}'
                         + ('; official maturities unavailable for some non-zero rows' if mdst == 'NA' else '')))
    return dict(month=month, mat_col=mat_col, rows=len(rows), nz=len(nz),
                chk=sum(r['chk'] is True for r in rows), mat=sum(r['ms'] == 'match' for r in rows),
                set_ok=set(amt) == set(ref), eq=eq, nu=len(union), eqm=eqm, num=len(um), se=se, sm=sm, sr=sr,
                md=f'{md_off}/{md_ocr}/{ref_md} {mdst}', mdst=mdst, iss=iss, notes=notes, dg=len(dg),
                ms={k: sum(r['ms'] == k for r in rows) for k in ('match', 'mismatch', 'notfound', 'multi', 'noocr', 'skip', 'apierr')})


# ---------- report -------------------------------------------------------------
W = (8, 5, 5, 10, 10, 6, 10, 10, 9, 9, 9)


def report(res):
    f2 = lambda a, b: f'{a}/{b}'
    line = lambda cells, tail: ''.join(f'{x!s:<{w}}' for x, w in zip(cells, W)) + tail
    hdr = line(('month', 'rows', 'nz', 'chk', 'mat', 'set', 'amt', 'bymat', 'sum_end', 'sum_mid', 'sub=ref'), 'maxd(off/ocr/ref)')
    ok = lambda b: 'OK' if b else 'DIFF'
    n = len(res)
    s = lambda k: sum(x[k] for x in res)
    L = ['Ripple RLUSD monthly reserve reports - T-bill CUSIP check of PaddleOCR-VL output',
         f'generated {dt.datetime.now():%Y-%m-%d %H:%M}; script cusip_check.py; OCR values reported as read (nothing corrected)', '',
         'rows     CUSIP rows between the "CUSIP | Maturity Date" header row and the subtotal row',
         'nz       rows whose month-end value is not 0 (the T-bills actually held at month-end)',
         'chk      CUSIP check digit passes / rows (a code that is not 9 chars counts as a failure)',
         'mat      official FiscalData maturity == maturity read from the OCR row / rows (codes that are not 9 chars cannot be looked up = not matched)',
         'set      Y if the CUSIPs with non-zero month-end equal the reference treasury holdings of that month',
         'amt      month-end amount equal to reference, per CUSIP / size of the union of both CUSIP sets',
         'bymat    same comparison keyed by maturity date instead of CUSIP (diagnostic only)',
         'sum_*    sum of the CUSIP-row values == subtotal row (month-end / mid-month)',
         'sub=ref  OCR subtotal month-end == reference components.treasury',
         'maxd     max days from as_of to maturity over non-zero rows: official maturities / OCR maturities / reference value; NA = official maturities unavailable',
         'value rule: "$" and "<fcel>" stripped, "-" = 0, empty cells dropped; last value cell = month-end, first = mid-month', '',
         hdr]
    for x in res:
        L.append(line((x['month'], x['rows'], x['nz'], f2(x['chk'], x['rows']), f2(x['mat'], x['rows']), 'Y' if x['set_ok'] else 'N',
                       f2(x['eq'], x['nu']), f2(x['eqm'], x['num']), ok(x['se']), ok(x['sm']), ok(x['sr'])), x['md']))
    L += ['-' * (sum(W) + 20),
          line(('TOTAL', s('rows'), s('nz'), f2(s('chk'), s('rows')), f2(s('mat'), s('rows')), f2(s('set_ok'), n),
                f2(s('eq'), s('nu')), f2(s('eqm'), s('num')), f2(s('se'), n), f2(s('sm'), n), f2(s('sr'), n)),
               f'OK {sum(x["mdst"] == "OK" for x in res)}/{n}, NA {sum(x["mdst"] == "NA" for x in res)}, DIFF {sum(x["mdst"] == "DIFF" for x in res)}'),
          f'maturity column present in {s("mat_col")}/{n} months; months without any CUSIP row: {[x["month"] for x in res if not x["rows"]] or "none"}; '
          f'months with no non-zero month-end CUSIP row: {[x["month"] for x in res if not x["nz"]] or "none"}',
          'official-maturity status over all rows: ' + ', '.join(f'{k} {sum(x["ms"][k] for x in res)}' for k in res[0]['ms']),
          f'rows with a 9-char code: {s("rows") - sum(x["ms"]["skip"] for x in res)}; of these check digit ok {s("chk")}, official maturity == OCR maturity {s("mat")}', '',
          f'MISMATCHES ({sum(len(x["iss"]) for x in res)} lines; one line per month+CUSIP, all problems of that row on the line; "-" = month-level)']
    for x in res:
        for c, t in x['iss']: L.append(f'{x["month"]}  {c:<10}  {t}')
    L += ['', f'LAYOUT NOTES ({sum(len(x["notes"]) for x in res)} lines; rows whose value-cell count is not 2, not mismatches by themselves)']
    for x in res:
        for c, t in x['notes']: L.append(f'{x["month"]}  {c:<10}  {t}')
    L += ['', 'NOT CHECKED / LIMITS',
          '- Only the OCR text is compared automatically; the script does not re-read the page images (two pages were looked at by eye, see below), '
          'so a misread that is consistent with the check digit, the official maturity and the sums would not show up.',
          '- Mid-month values cannot be compared with the reference (it holds month-end only); only the sum-to-subtotal check covers them.',
          '- Months with 8-char CUSIPs (check digit not computable, no FiscalData lookup, official-maturity max-days not computable): '
          + (', '.join(f'{x["month"]} ({x["ms"]["skip"]} rows)' for x in res if x['ms']['skip']) or 'none'),
          '- The check digit alone cannot tell some confusions apart (e.g. T vs 1 at an even 0-based position gives the same digit sum); '
          'the FiscalData lookup of the 9-char code plus the maturity comparison is what covers that.',
          '', 'MANUAL PAGE-IMAGE CHECKS (static text, looked at paddle/ripple_YYYY-MM.png by eye; not computed by this script)',
          '- 2025-04: the page prints 912797NB9 (April 10, 2025) 122,970,480 / "-" and 912797ND5 (May 1, 2025) "-" / 140,533,134. '
          'The OCR table put 140,533,134 into a third value cell of the NB9 row and left the ND5 month-end cell empty.',
          '- 2026-06: the page prints 9-char codes (912797TZ0, 912797QX8, ... 912797UH8, 21 rows). The OCR dropped the 6th character "7" on every row, '
          'so the 8-char codes are an OCR dropout, not a typo in the report; month-end amounts and maturity dates agree with the reference when matched by maturity date (bymat 14/14).']
    with open(OUT, 'w', encoding='utf-8') as f: f.write('\n'.join(L) + '\n')
    print('\n'.join(L))


def main():
    selftest()
    try:
        with open(CACHE) as f: cache.update(json.load(f))
    except (OSError, ValueError):
        pass
    refs = {r['month']: r for r in json.load(open(REF))['reports']}
    paths = sorted(glob.glob(D + '/paddle/ripple_*.md'))
    for p in paths:                                    # fill the cache first so the diagnostics do not depend on month order
        for r in parse(p)[2]: omats(r['cusip'])
        for c in ref_treasury(refs[os.path.basename(p)[7:14]]): omats(c)
    report([analyse(os.path.basename(p)[7:14], p, refs[os.path.basename(p)[7:14]]) for p in paths])


if __name__ == '__main__':
    main()
