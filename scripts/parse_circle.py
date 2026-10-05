#!/usr/bin/env python3
"""Circle USDC, EURC 월간 검사보고서 PDF 파서 (F1).

data/samples/Circle_USDC_Examination_*.pdf 를 읽어 data/reports.json,
data/samples/Circle_EURC_Examination_*.pdf 를 읽어 data/reports_eurc.json 을 만든다.
합계 대사가 어긋난 달은 reports에서 빼고 로그에 이유를 남기며 종료 코드 1을 낸다.

규칙 입력값(holdings, fund_holdings, 만기, 공시 항목, field_notes)도 같은 PDF 원문에서 읽는다(rules_inputs).
사용: python3 scripts/parse_circle.py [--verbose]
"""
import json, re, subprocess, sys, pathlib, datetime, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'samples'
# 토큰별 설정. 2023년 상반기 EURC 보고서는 토큰 이름이 EUROC로 적혀 있다.
TOKENS = {
    'USDC': dict(out=ROOT / 'data' / 'reports.json', name=r'USDC', ccy='USD', fund=True,
                 source='Circle USDC 월간 examination report, pdftotext -layout'),
    'EURC': dict(out=ROOT / 'data' / 'reports_eurc.json', name=r'EUROC|EURC', ccy='EUR', fund=False,
                 source='Circle EURC 월간 examination report(2023년 일부는 토큰명 EUROC), pdftotext -layout'),
}
VERBOSE = '--verbose' in sys.argv

MONTHS = {m: i for i, m in enumerate(
    'january february march april may june july august september october november december'.split(), 1)}


def text_of(pdf, first=None, last=None):
    cmd = ['pdftotext', '-layout']
    if first: cmd += ['-f', str(first)]
    if last: cmd += ['-l', str(last)]
    cmd += [str(pdf), '-']
    # NFKC: 2023년 PDF의 합자(ﬁ, ﬀ)를 풀어 'financial', 'differences'로 읽는다.
    return unicodedata.normalize('NFKC', subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)


def num(s):
    return int(s.replace(',', ''))


def to_iso(s):
    """'July 31, 2026' -> '2026-07-31'"""
    m = re.match(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', s.strip())
    if not m: return None
    mon, day, year = m.groups()
    i = MONTHS.get(mon.lower())
    return f'{year}-{i:02d}-{int(day):02d}' if i else None


def line_amount(line):
    """줄 끝 금액. 괄호는 음수. '€ (1,234)', '(€ 251)', '$ 1,234' 꼴과 각주 번호(net1)를 구분한다."""
    m = re.search(r'(?<![\w,])(\(?)\s*[$€]?\s*(\(?)([\d,]*\d)\)?\s*$', line)
    if not m: return None
    return -num(m.group(3)) if m.group(1) or m.group(2) else num(m.group(3))


def other_breakdown(text, name, fund):
    """월말 '기타 준비자산'(EURC는 준비자산 전체) 구획을 은행 예금, 국채, 정산 차액으로 나눈다.
    은행 예금 금액은 같은 줄 끝에 있거나(4, 7월) 레이아웃 때문에 바로 윗줄에 혼자 있다(1, 3월, 2023년)."""
    if fund:
        block = text.split('OTHER USDC RESERVE ASSETS AS OF')[-1].split('TOTAL OTHER USDC RESERVE ASSETS')[0]
    else:  # 'TOTAL EURC RESERVE ASSETS AS OF' 줄은 앞에 TOTAL이 있어 줄 머리 일치로 걸러진다
        block = re.split(rf'^\s*(?:{name}) RESERVE ASSETS AS OF.*$', text, flags=re.M | re.I)[-1]
        block = re.split(rf'TOTAL (?:{name}) RESERVE ASSETS', block)[0]
    lines = block.splitlines()
    out = {'cash': None, 'treasury': 0, 'due': None}
    for i, line in enumerate(lines):
        if 'Cash held at' in line and 'financial institutions' in line:
            out['cash'] = line_amount(line)
            for j in (i - 1, i - 2, i + 1):  # 금액만 있는 이웃 줄
                if out['cash'] is None and 0 <= j < len(lines) and re.fullmatch(r'\s*[\d,]{7,}\s*', lines[j]):
                    out['cash'] = num(lines[j].strip())
        elif 'Cash due to/(owed by)' in line:
            out['due'] = line_amount(line)
        elif 'TOTAL U.S. TREASURY SECURITIES' in line:
            out['treasury'] = line_amount(line) or 0
    return out


def last_amount(text, label):
    """label이 있는 마지막 줄의 줄 끝 금액. 보고서에 기준일별 구획이 둘이고 월말 구획이 뒤에 온다.
    라벨과 금액 사이에 날짜나 각주 번호가 끼는 달이 있어 줄 단위로 읽는다."""
    hits = re.findall(re.escape(label) + r'[^\n]*?\s[$€]?\s*([\d,]{7,})[ \t]*$', text, re.M)
    return num(hits[-1]) if hits else None


def total_amount(text, name):
    """'TOTAL ... RESERVE ASSETS AS OF 날짜 금액' 줄의 마지막 금액. 토큰명은 정규식(EUROC|EURC 등)으로 받는다."""
    hits = re.findall(rf'TOTAL (?:{name}) RESERVE ASSETS AS OF[^\n]*?\s[$€]?\s*([\d,]{{7,}})[ \t]*$', text, re.M | re.I)
    return num(hits[-1]) if hits else None


# ---------------------------------------------------------------------------
# 규칙 입력값(F2): 준비자산 줄 단위 정규화, 만기, 공시 항목. 값은 전부 PDF 원문에서 읽고 읽은 쪽(where)을 적는다.
# ---------------------------------------------------------------------------
CUSIP_ROW = re.compile(r'^\s*([0-9A-Z]{9})\s+(\d\d)/(\d\d)/(\d\d)\s+\$?\s*([\d,]+)\s*$')
AMOUNT_ONLY = re.compile(r'^\s*\(?[$€]?\s*\(?([\d,]{5,})\)?\s*$')
KNOWN_BANKS = ['Bank of New York Mellon', 'Citizens Trust Bank', 'Customers Bank', 'New York Community Bank',
               'Signature Bank', 'Silicon Valley Bank', 'Silvergate Bank', 'Cross River Bank']
BANK_GENERIC = re.compile(r'\b[A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+){0,3} (?:Bank|Trust|Bancorp)\b')
MONTH_RE = '|'.join(m.capitalize() for m in MONTHS)


def pages_lines(text):
    """[(쪽번호, 줄)]. pdftotext는 쪽 사이에 \\f를 넣는다."""
    out, page = [], 1
    for ln in text.split('\n'):
        page += ln.count('\f')
        out.append((page, ln.replace('\f', '')))
    return out


def days_between(as_of, mdy):
    """'07/09/26' -> as_of로부터 달력일."""
    mm, dd, yy = int(mdy[0]), int(mdy[1]), 2000 + int(mdy[2])
    return (datetime.date(yy, mm, dd) - datetime.date.fromisoformat(as_of)).days


def cusip_kind(cusip):
    # 912796, 912797 접두는 미국 재무부 단기채(T-bill), 그 밖의 9128xx는 중장기 국채(T-note)
    return 'treasury_bill' if cusip.startswith(('912796', '912797', '912795')) else 'treasury_note'


def clean_label(line):
    """줄 머리 라벨. 금액 앞 공백 두 칸 이전까지, 끝에 붙은 각주 번호(net4, Agreements3)는 뗀다."""
    return re.sub(r'(?<=[A-Za-z])\d$', '', line.strip().split('  ')[0])


def read_block(pl, a, b):
    """pl[a:b] 구획의 줄을 읽어 [(종류, 금액, 줄번호, 보조)]로. 금액이 윗줄이나 아랫줄에 혼자 있는 레이아웃을 이웃 줄로 채운다."""
    labels = [  # (종류, 줄 머리 정규식)
        ('tsy_total', r'TOTAL U\.S\. TREASURY SECURITIES'), ('repo', r'U\.S\.? Treasury Repurchase Agreements'),
        ('cash_fund', r'Cash held in Circle Reserve Fund'), ('cash_bank', r'Cash held at (?:U\.S\. )?regulated financial institutions'),
        ('due', r'Cash due to/\(owed by\)')]
    items, used = [], set()
    for i in range(a, b):
        s = pl[i][1].strip()
        m = CUSIP_ROW.match(pl[i][1])
        if m:
            items.append(['cusip', num(m.group(5)), i, m.group(1), (m.group(2), m.group(3), m.group(4))]); used.add(i); continue
        for kind, rx in labels:
            if re.match(rx, s):
                amt = line_amount(s)
                if amt is not None and abs(amt) < 10 and not re.search(r'[\d],\d', s):  # 각주 번호('net 4')
                    amt = None
                items.append([kind, amt, i, None, None])
                if amt is not None: used.add(i)
                break
    def neighbor(i, step):
        j = i + step
        while a <= j < b and not pl[j][1].strip(): j += step
        if a <= j < b and j not in used and AMOUNT_ONLY.match(pl[j][1]):
            return j
    for it in items:
        if it[1] is None:
            cand = [j for j in (neighbor(it[2], -1), neighbor(it[2], 1)) if j is not None]
            if len(cand) == 1:
                j = cand[0]; used.add(j); line = pl[j][1].strip()
                it[1] = line_amount(line)
    return items


def custody_info(text, as_of):
    """원문에 이름이 나온 은행. 월말 기준일 문장(예: 'As of March 31, 2023, cash was held ...')이 있으면 그 문단만 본다."""
    flat = re.sub(r'\s+', ' ', text).split('Subsequent Event Not Subject')[0]  # 2023-02 후속 사건 문단의 은행명은 '보유 없음' 설명이라 보관처가 아니다
    y, mo, d = as_of.split('-')
    mon = [k for k, v in MONTHS.items() if v == int(mo)][0].capitalize()
    m = re.search(rf'As of {mon} {int(d)}, {y}, cash was held[^:]*:(.*?)(?:\d\. |$)', flat)
    seg = m.group(1) if m else flat
    names = [n for n in KNOWN_BANKS if n in seg]
    generic = sorted({g for g in BANK_GENERIC.findall(flat) if not any(g in n or n in g for n in KNOWN_BANKS)})
    return names, generic, bool(m)


def rules_inputs(pdf, text, r, token, crf, oth, tot, ob):
    """보고서 한 건의 규칙 입력값. 구획은 월말(뒤쪽 날짜)만 쓴다."""
    cfg = TOKENS[token]; ccy = cfg['ccy']; fund = cfg['fund']; as_of = r['as_of']
    pl = pages_lines(text)
    # 구획 경계
    head_rx = r'^\s*CIRCLE RESERVE FUND ASSETS AS OF' if fund else rf'^\s*(?:{cfg["name"]}) RESERVE ASSETS AS OF'
    heads = [i for i, (_, l) in enumerate(pl) if re.match(head_rx, l, re.I)]
    oth_heads = [i for i, (_, l) in enumerate(pl) if re.match(r'^\s*OTHER USDC RESERVE ASSETS AS OF', l)] if fund else []
    end_rx = r'TOTAL (?:USDC|%s) RESERVE ASSETS AS OF' % cfg['name']
    ends = [i for i, (_, l) in enumerate(pl) if re.search(end_rx, l, re.I)]
    hd = pl[heads[-1]][1].strip()
    mm = re.search(rf'({MONTH_RE})[A-Z]*\.?,?\s+(\d{{1,2}}),?\s+(\d{{4}})', hd, re.I)
    if not mm or to_iso(f'{mm.group(1)} {mm.group(2)}, {mm.group(3)}') != as_of:
        raise ValueError(f'월말 구획 제목이 기준일과 다름: {hd}')
    if fund:
        fa, fb, oa, ob_end = heads[-1], oth_heads[-1], oth_heads[-1], ends[-1]
    else:
        fa = fb = None; oa, ob_end = heads[-1], ends[-1]
    hold, fh = [], []

    def where(i, what):
        return f"p.{pl[i][0]} '{pl[heads[-1] if (not fund or i < oa) else oa][1].strip()}' 구획 {what}"

    # 펀드 구획
    fund_mat = []
    repo_rows = []
    if fund:
        for kind, amt, i, cus, md in read_block(pl, fa, fb):
            if kind == 'cusip':
                d = days_between(as_of, md)
                fh.append(dict(kind=cusip_kind(cus), amount=amt, currency=ccy, maturity_max_days=d, maturity_listed=True,
                               label=f'U.S. Treasury Securities Cusip {cus}', where=where(i, f'{cus} 줄, 만기 {md[0]}/{md[1]}/{md[2]}')))
                fund_mat.append(d)
            elif kind == 'repo':
                repo_rows.append((amt, i))
            elif kind == 'cash_fund' or kind == 'cash_bank':
                fh.append(dict(kind='bank_deposit', amount=amt, currency=ccy, maturity_max_days=None, maturity_listed=False,
                               label=clean_label(pl[i][1]), where=where(i, '펀드 안 현금 줄')))
            elif kind == 'due':
                fh.append(dict(kind='settlement', amount=amt, currency=ccy, maturity_max_days=None, maturity_listed=False,
                               label=clean_label(pl[i][1]), where=where(i, '정산 차액 줄')))
    # 레포 만기: 각주가 하루짜리(overnight)라고 적은 달만 1. 줄이 있는데 각주가 없으면 만기 모름.
    repo_note = None
    for i, (pg, l) in enumerate(pl):
        if re.search(r'Repurchase Agreements within the Circle Reserve Fund involve the', ' '.join(x[1] for x in pl[i:i + 2])):
            nxt = re.sub(r'\s+', ' ', ' '.join(x[1] for x in pl[i:i + 3]))
            if re.search(r'involve the overnight lending of cash', nxt): repo_note = (pg, 'involve the overnight lending of cash')
    repo_state = None
    for amt, i in repo_rows:
        if amt is None: raise ValueError('레포 금액을 못 읽음')
        fh.append(dict(kind='reverse_repo_overnight', amount=amt, currency=ccy, maturity_max_days=1 if repo_note else None,
                       maturity_listed=bool(repo_note), label='U.S. Treasury Repurchase Agreements',
                       where=where(i, '레포 줄' + (f", 각주(p.{repo_note[0]}) '{repo_note[1]}'" if repo_note else ', 만기 각주 없음'))))
    if fund:
        # 펀드 한 줄 = 정부 MMF. 그 줄에 든 종목 중 가장 늦은 만기는 펀드 안 국채 만기와 레포 만기 중 큰 값.
        mats = fund_mat + ([1] if repo_rows and repo_note else [])
        hold.append(dict(kind='government_mmf', amount=crf, currency=ccy, maturity_max_days=max(mats) if mats else None,
                         maturity_listed=bool(mats), label='TOTAL CIRCLE RESERVE FUND ASSETS',
                         where=where(fa, 'TOTAL CIRCLE RESERVE FUND ASSETS 줄(펀드 보유 종목은 fund_holdings)')))
    # 기타 준비자산(EURC는 준비자산 전체) 구획
    direct_mat = []
    for kind, amt, i, cus, md in read_block(pl, oa, ob_end):
        if kind == 'cusip':
            d = days_between(as_of, md)
            hold.append(dict(kind=cusip_kind(cus), amount=amt, currency=ccy, maturity_max_days=d, maturity_listed=True,
                             label=f'U.S. Treasury Securities Cusip {cus}', where=where(i, f'{cus} 줄, 만기 {md[0]}/{md[1]}/{md[2]}')))
            direct_mat.append(d)
        elif kind in ('cash_bank', 'cash_fund'):
            hold.append(dict(kind='bank_deposit', amount=amt, currency=ccy, maturity_max_days=None, maturity_listed=False,
                             label=clean_label(pl[i][1]), where=where(i, '은행 예금 줄')))
        elif kind == 'due':
            hold.append(dict(kind='settlement', amount=amt, currency=ccy, maturity_max_days=None, maturity_listed=False,
                             label=clean_label(pl[i][1]), where=where(i, '정산 차액 줄')))
        elif kind == 'repo':
            raise ValueError('직접 보유 레포 줄: 처리 규칙 필요')
    for h in hold + fh:
        if h['amount'] is None: raise ValueError(f"금액을 못 읽음: {h['label']}")
    # 대사: holdings 합 = fair_value, fund_holdings 합 = 펀드 합계
    hsum, fsum = sum(h['amount'] for h in hold), sum(h['amount'] for h in fh)
    rec = {'holdings_sum': {'expected': r['fair_value'], 'got': hsum, 'diff': hsum - r['fair_value']}}
    if rec['holdings_sum']['diff'] != 0:
        raise ValueError(f'준비자산 줄 합계 불일치 {rec}')
    if fund:  # 펀드 안 줄 합계는 대사에 넣지 않는다. 원문 반올림 오차(2025-03은 1달러)는 기록만 하고, 크게 어긋나면 읽기 오류로 본다.
        rec['fund_holdings_sum'] = {'expected': crf, 'got': fsum, 'diff': fsum - crf, 'in_reconciliation': False}
        if abs(fsum - crf) > 1000:
            raise ValueError(f'펀드 안 줄 합계 불일치 {rec}')
    asset_types = sorted({h['kind'] for h in hold if h['amount'] > 0 and h['kind'] != 'settlement'})

    notes = {}
    # 국채 최장 잔존만기
    ts = [h for h in hold + fh if h['kind'] in ('treasury_bill', 'treasury_note', 'non_us_government_bill') and h['amount'] > 0]
    d_dir = [h['maturity_max_days'] for h in hold if h in ts]
    d_fund = [h['maturity_max_days'] for h in fh if h in ts]
    basis = 'both' if d_dir and d_fund else 'direct' if d_dir else 'fund' if d_fund else None
    if ts:
        tmax = max(d_dir + d_fund)
        src = '직접 보유분' if d_dir and max(d_dir) == tmax else '펀드 안'
        notes['treasury_max_maturity_days'] = dict(state='found', where=sorted({h['where'] for h in ts if h['maturity_max_days'] == tmax})[0],
                                                   note=f'국채 종목별 만기(Cusip 표)에서 최장 {tmax}일. 최장 종목은 {src}. 국채 보유 위치: ' +
                                                        {'both': '직접 보유와 펀드 안 모두', 'direct': '직접 보유만', 'fund': '펀드 안만'}[basis])
    else:
        tmax = None
        notes['treasury_max_maturity_days'] = dict(state='not_applicable', where=f'p.{pl[heads[-1]][0]}~{pl[ob_end][0]} 월말 구획 전체',
                                                   note='월말 구획에 국채 표(Cusip) 없음. 직접 보유와 펀드 안 모두 국채 없음')
    # 레포 최장 만기
    if repo_rows and any(a > 0 for a, _ in repo_rows):
        if repo_note:
            rmax = 1
            notes['repo_max_maturity_days'] = dict(state='found', where=f'p.{pl[repo_rows[0][1]][0]} 레포 줄, 각주 p.{repo_note[0]}',
                                                   note="각주 'U.S Treasury Repurchase Agreements within the Circle Reserve Fund involve the overnight lending of cash'로 하루짜리(1일)")
        else:
            rmax = None
            notes['repo_max_maturity_days'] = dict(state='not_in_report', where=f'p.{pl[repo_rows[0][1]][0]} 레포 줄', note='레포 줄은 있으나 만기 각주를 찾지 못함')
    else:
        rmax = None
        notes['repo_max_maturity_days'] = dict(state='not_applicable', where=f'p.{pl[heads[-1]][0]}~{pl[ob_end][0]} 월말 구획 전체', note='월말 구획에 역레포 줄 없음')

    # 공시 주기: 보고서 한 건에 기준일이 둘(월중, 월말)이고 파일이 달마다 이어진다.
    months = sorted(re.search(r'(\d{4}-\d{2})', p.name).group(1) for p in SRC.glob(f'Circle_{token}_Examination_*.pdf'))
    seq = [datetime.date(int(x[:4]), int(x[5:]), 1) for x in months]
    gaps = [x for a_, x in zip(seq, seq[1:]) if (x.year * 12 + x.month) - (a_.year * 12 + a_.month) != 1]
    notes['disclosure_cadence'] = dict(state='found', where='p.2 Management’s Assertion 표 Report Dates 두 칸(월중, 월말), data/samples 파일명',
                                       note=f'월 1회 보고서(기준일 {r["report_dates"][0]}, {r["report_dates"][1]}). 표본 {months[0]}~{months[-1]} {len(months)}개월'
                                            + ('이 빠짐없이 이어짐' if not gaps else f', 빠진 달 있음 {gaps}'))
    # 유통량 계산법
    flat = re.sub(r'\s+', ' ', text)
    mc = re.search(rf'(?:{cfg["name"]}) In Circulation is defined as ([^.]*?)(?=\. )', flat, re.I)
    circ = bool(mc)
    if circ:
        pg = next(pl[i][0] for i, (_, l) in enumerate(pl) if re.search(r'In Circulation is defined as', l, re.I))
        notes['circulation_formula_disclosed'] = dict(state='found', where=f'p.{pg} CRITERIA A', note='발행 토큰 총량에서 미발행 허용 토큰, 접근 제한 토큰 등을 뺀다고 정의: ' + mc.group(1)[:200])
    else:
        notes['circulation_formula_disclosed'] = dict(state='not_disclosed', where='전문 검색', note="검색어: 'In Circulation is defined as', 'in Circulation is d(e)fined', 'less (i)', 'burn'. 설명 없음")
    # 보관 기관
    names, generic, month_end_only = custody_info(text, as_of)
    has_subseq = 'Subsequent Event Not Subject' in text
    if names:
        pg = [pg for pg, l in pl if l.strip() == 'Notes'][-1]  # 은행명은 Notes 쪽 각주에 있다(줄바꿈으로 이름이 갈려 줄 단위 검색 불가)
        notes['custodian_disclosure'] = dict(state='found', where=f'p.{pg} 각주(Notes)',
                                             note='각주에 은행명 있음: ' + ', '.join(names) + (' (월말 기준일 문장만 사용)' if month_end_only else '')
                                                  + (' 후속 사건(Subsequent Event) 문단의 은행명은 보관처 목록이 아니라 제외' if has_subseq else ''))
    else:
        notes['custodian_disclosure'] = dict(state='not_disclosed', where='전문 검색',
                                             note="검색어: 알려진 은행명 8개(Bank of New York Mellon, Citizens Trust, Customers, New York Community, Signature, Silicon Valley, Silvergate, Cross River), "
                                                  "'… Bank/Trust/Bancorp' 꼴, custodian, trustee, held at. 'regulated financial institutions'로 종류만 적고 이름 없음"
                                                  + (f'. 일반 패턴 걸린 것: {generic}' if generic else ''))
    # 경영진 확인서
    tail = text.rsplit('Notes', 1)[-1]
    tl = [x.strip() for x in tail.splitlines() if x.strip() and 'Circle.com' not in x and 'DocuSign' not in x]
    sig = None
    for k in range(len(tl) - 1, 1, -1):
        if re.match(r'^Circle Internet (?:Group, Inc\.|Financial, LLC)$', tl[k]):
            sig = (tl[k - 2], tl[k - 1], tl[k]); break
    has_assertion = 'Management’s Assertion' in text
    if sig and has_assertion:
        mgmt, certifier = True, f'{sig[1]}, {sig[2]}'
        notes['management_certification'] = dict(state='found', where=f'p.{[pg for pg, l in pl if sig[1] in l][-1]} Notes 뒤 서명 블록',
                                                 note=f"Management’s Assertion 쪽 말미에 {sig[1]} 서명 블록(이름, 직함, 법인, 날짜). 직함으로 경영진 서명 판정")
    else:
        mgmt, certifier = False, None
        notes['management_certification'] = dict(state='not_disclosed', where='전문 검색', note="검색어: Management’s Assertion, 서명 블록(직함 줄 + 법인명). 없음")
    # 상환 기한, 이자 지급: 문장이 있어야 값
    red = re.search(r'[^.]*\bredee?m[^.]*\bwithin\s+\w+\s+(?:business |calendar )?days?[^.]*\.', flat, re.I)
    intr = re.search(r'[^.]*\b(?:interest|yield|rewards?)\b[^.]*\b(?:paid|distribut\w+|pay(?:s|ment)?)\b[^.]*\bholders?\b[^.]*\.', flat, re.I)
    if red:
        notes['redemption_days'] = dict(state='found', where='원문 문장', note=red.group(0).strip()[:200]); rdays = None
    else:
        rdays = None
        notes['redemption_days'] = dict(state='not_in_report', where='전문 검색',
                                        note="검색어: redeem/redemption + within N days. 'issued and redeemed by Circle…'(발행, 상환 주체)만 있고 상환 기한 문장 없음")
    if intr:
        notes['interest_paid'] = dict(state='found', where='원문 문장', note=intr.group(0).strip()[:200])
    else:
        notes['interest_paid'] = dict(state='not_in_report', where='전문 검색',
                                      note="검색어: interest/yield/reward + paid/distribute + holders. 'interest receivable or payable'은 준비금 잔액 시차 조정 설명이라 이자 지급이 아님")
    return dict(holdings=hold, fund_holdings=fh, asset_types=asset_types,
                treasury_max_maturity_days=tmax, treasury_maturity_basis=basis, repo_max_maturity_days=rmax,
                disclosure_cadence='monthly', disclosure_cadence_days=31,
                circulation_formula_disclosed=circ, custodian_disclosure=bool(names), custodians=names,
                management_certification=mgmt, certifier=certifier,
                redemption_days=rdays, interest_paid=None,
                holdings_reconciliation=rec, field_notes=notes)


def parse(pdf, token='USDC'):
    cfg = TOKENS[token]
    name, fund = cfg['name'], cfg['fund']
    text = text_of(pdf)
    page1 = text_of(pdf, 1, 1)
    # 발행 법인 = 경영진 주장서의 주체. 2024-07부터 Group, 그 전은 Circle Internet Financial, LLC.
    m = re.search(r'(Circle Internet (?:Group, Inc\.|Financial,? LLC))\s*\(', text.split('Management’s Assertion')[-1])
    r = {'source_file': str(pdf.relative_to(ROOT)), 'issuer': m.group(1) if m else None, 'token': token}

    m = re.search(r'Report Dates\s+([A-Za-z]+ \d{1,2}, \d{4})\s+([A-Za-z]+ \d{1,2}, \d{4})', text)
    if not m:
        return {**r, 'ok': False, 'error': 'Report Dates 줄을 찾지 못함'}
    r['report_dates'] = [to_iso(m.group(1)), to_iso(m.group(2))]
    r['as_of'] = r['report_dates'][1]
    r['month'] = r['as_of'][:7]
    # 시각은 경영진 주장서 문단의 마지막 'at 11:59pm ... Time'. 2024-09부터 UTC, 그 전은 태평양 표준시(PST)와 일광절약시간(PDT).
    tz = re.findall(r'at\s+11:59\s*pm\s+(Pacific\s+Standard|Pacific\s+Daylight|Coordinated)', text.split('Management’s Assertion')[-1])
    r['as_of_time'] = '23:59 ' + {'Pacific Standard': 'PST', 'Pacific Daylight': 'PDT', 'Coordinated': 'UTC'}[' '.join(tz[-1].split())] if tz else None
    r['reserve_currency'] = ('USD' if 'U.S. dollar denominated assets' in text else
                             'EUR' if re.search(r'euro denominated assets', text) else None)

    m = re.search(rf'(?:{name}) in Circulation[^\d\n]*([\d,]+)\s+([\d,]+)', text, re.I)
    r['circulation'] = num(m.group(2)) if m else None
    m = re.search(rf'Fair Value of Assets Held in (?:{name}) Reserve\s+[$€]?\s*([\d,]+)\s+[$€]?\s*([\d,]+)', text)
    r['fair_value'] = num(m.group(2)) if m else None

    crf = last_amount(text, 'TOTAL CIRCLE RESERVE FUND ASSETS') if fund else 0
    oth = last_amount(text, 'TOTAL OTHER USDC RESERVE ASSETS') if fund else None
    tot = total_amount(text, name)
    ob = other_breakdown(text, name, fund)
    # 기타 준비자산 = 은행 예금 + 국채(2026년 7월부터) + 정산 차액. 판정기는 cash를 은행 예금으로 읽는다.
    # 서클 준비금 펀드(circle_reserve_fund)는 국채, 역레포, 펀드 내 현금을 한 줄로 합친 정부 MMF라 쪼개지 않는다.
    r['components'] = {'circle_reserve_fund': crf, 'cash': ob['cash'], 'treasury': ob['treasury'], 'other': ob['due']}

    # 합계 대사. 구획을 잘못 잡으면 여기서 걸린다.
    checks = {}
    comp = list(r['components'].values())
    if None not in comp and tot is not None:
        checks['components_sum'] = {'expected': tot, 'got': sum(comp), 'diff': sum(comp) - tot}
    else:
        checks['components_sum'] = {'expected': tot, 'got': None, 'diff': 'parse_fail'}
    if fund:
        if None not in (oth, ob['cash'], ob['due']):
            got = ob['cash'] + ob['treasury'] + ob['due']
            checks['other_breakdown'] = {'expected': oth, 'got': got, 'diff': got - oth}
        else:
            checks['other_breakdown'] = {'expected': oth, 'got': None, 'diff': 'parse_fail'}
    if None not in (tot, r['fair_value']):
        checks['total_equals_fair_value'] = {'expected': r['fair_value'], 'got': tot, 'diff': tot - r['fair_value']}
    else:
        checks['total_equals_fair_value'] = {'expected': r['fair_value'], 'got': tot, 'diff': 'parse_fail'}
    if None not in (r['fair_value'], r['circulation']):
        checks['covers_circulation'] = {'surplus': r['fair_value'] - r['circulation'],
                                        'ok': r['fair_value'] >= r['circulation']}
    r['reconciliation'] = checks
    r['ok'] = (all(c.get('diff', 0) == 0 for c in checks.values() if 'diff' in c)
               and checks.get('covers_circulation', {}).get('ok', False))

    if r['ok']:
        r['coverage'] = round(r['fair_value'] / r['circulation'], 8)

    # 검증 정보. 회계법인명은 서명 이미지라 텍스트로 안 나온다.
    dates = re.findall(r'^\s*([A-Za-z]+ \d{1,2}, \d{4})\s*$', text, re.M)
    r['attestation'] = {
        'type': 'examination' if re.search(r'We have examined|Our examination', text) else None,
        'standard': 'AICPA attestation standards' if 'American Institute of Certified Public Accountants' in text else None,
        'signed': to_iso(dates[-1]) if dates else None,
        'firm': None,  # 이미지 서명. 서식 항목 D1은 수동 확인 필요
    }

    # 구조 차이. 2026년 7월부터 기타 준비자산 안에 국채 하위표가 있다(USDC만).
    tail = text.split('OTHER USDC RESERVE ASSETS AS OF')[-1]
    squash = lambda t: re.sub(r'[^A-Za-z]', '', t)
    r['flags'] = {
        'garbled_page1': squash(r['issuer'] or 'Circle') not in squash(page1),
        'other_has_treasury_subtable': fund and 'TOTAL U.S. TREASURY SECURITIES' in tail,
        'scan_suspected': len(text.strip()) < 2000,
    }
    # 규칙 입력값. 줄 단위 합계가 안 맞으면 억지로 맞추지 않고 보고서를 제외한다.
    if r['ok']:
        try:
            r.update(rules_inputs(pdf, text, r, token, crf, oth, tot, ob))
        except ValueError as e:
            r['ok'] = False; r['error'] = f'규칙 입력값 읽기 실패: {e}'
    return r


def exclusion_reason(r):
    """제외 사유 한 줄. 합계 대사가 어긋난 검사를 풀어 쓴다."""
    if r.get('error'): return r['error']
    bad = {k: v for k, v in (r.get('reconciliation') or {}).items() if v.get('diff') not in (None, 0) or v.get('ok') is False}
    name = {'components_sum': '구성 항목 합계와 TOTAL 줄', 'other_breakdown': '기타 준비자산 내역과 합계', 'total_equals_fair_value': '준비자산 표 TOTAL 줄과 Management’s Assertion 표의 Fair Value',
            'covers_circulation': '준비자산이 유통량 이상'}
    return '; '.join(f"{name.get(k, k)} 불일치(기대 {v.get('expected')}, 읽은 값 {v.get('got')}, 차이 {v.get('diff')})" for k, v in bad.items()) or '사유 미상'


def run(token):
    cfg = TOKENS[token]
    pdfs = sorted(SRC.glob(f'Circle_{token}_Examination_*.pdf'))
    if not pdfs:
        print('PDF 없음:', SRC, token); return 1
    reports, bad, excluded = [], [], []
    for p in pdfs:
        r = parse(p, token)
        tag = 'ok ' if r.get('ok') else 'FAIL'
        if r.get('ok'):
            print(f"{tag} {token} {r['month']}  유통 {r['circulation']:,}  준비자산 {r['fair_value']:,}  "
                  f"커버리지 {r['coverage'] * 100:.4f}%  기준일 {r['as_of']}  서명 {r['attestation']['signed']}")
            reports.append(r)
        else:
            print(f"제외 {token} {p.name}: {r.get('error') or r.get('reconciliation')}")  # 억지로 맞추지 않고 제외
            bad.append(p.name)
            excluded.append({'token': token, 'month': re.search(r'(\d{4}-\d{2})', p.name).group(1),
                             'source_file': str(p.relative_to(ROOT)), 'reason': exclusion_reason(r)})
        if VERBOSE: print('   ', json.dumps(r.get('flags'), ensure_ascii=False))
    reports.sort(key=lambda x: x.get('as_of') or '')
    cfg['out'].parent.mkdir(parents=True, exist_ok=True)
    cfg['out'].write_text(json.dumps({
        'generated': datetime.date.today().isoformat(),
        'source': cfg['source'],
        'note': NOTE[token],
        'excluded': excluded,
        'reports': reports,
    }, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n{token} {len(reports)}개월 → {cfg["out"].relative_to(ROOT)}, 대사 실패 {len(bad)}\n')
    return 1 if bad else 0


NOTE = {
    'USDC': '회계법인명은 서명 이미지라 자동 추출되지 않는다. 서식 항목 D1은 수동 확인. '
            '구성: circle_reserve_fund=TOTAL CIRCLE RESERVE FUND ASSETS(국채, 역레포, 펀드 내 현금, 정산 차액을 합친 정부 MMF, 역레포는 따로 쪼개지 않음), '
            'cash=OTHER USDC RESERVE ASSETS의 Cash held at (U.S.) regulated financial institutions(은행 예금만), '
            'treasury=OTHER 구획의 TOTAL U.S. TREASURY SECURITIES(2026-07부터, 이전은 0), '
            'other=OTHER 구획의 Cash due to/(owed by) Circle(정산 차액). '
            '대사 실패 보고서는 reports에서 제외. issuer는 경영진 주장서 주체(2024-06까지 Circle Internet Financial, LLC, 2024-07부터 Circle Internet Group, Inc.). '
            'signed는 보고서 말미 Circle 임원 서명일(회계법인 의견서 날짜와 같다). '
            '규칙 입력값(F2): holdings=준비자산 줄 단위 정규화(합계=fair_value), fund_holdings=서클 준비금 펀드 안 종목(합계 대사 제외), '
            'treasury_max_maturity_days, repo_max_maturity_days=월말 기준일로부터 달력일, 공시 항목은 field_notes에 state와 읽은 쪽을 적는다. '
            '1달러 이내 반올림 오차는 holdings_reconciliation에 기록(2025-03 펀드 Cusip 합계).',
    'EURC': '회계법인명은 서명 이미지라 자동 추출되지 않는다. EURC 준비자산은 은행 예금뿐이라 circle_reserve_fund, treasury는 0. '
            '구성: cash=EURC RESERVE ASSETS의 Cash held at (U.S.) regulated financial institutions(은행 예금만, 유로), '
            'other=Cash due to/(owed by) the Company(Circle)(정산 차액). 2023년 상반기 원문은 토큰명이 EUROC(EURO Coin)이며 token은 EURC로 통일. '
            '대사 실패 보고서는 reports에서 제외. 금액 단위는 EUR(원문 €). '
            '규칙 입력값(F2): holdings는 은행 예금과 정산 차액뿐이라 국채, 레포는 not_applicable. 제외 보고서는 최상위 excluded에 적는다.',
}


def main():
    # 종료 코드는 USDC 대사 실패만 반영한다(tests/test_parser.py가 이 코드를 본다). EURC 실패는 로그와 제외로만 남긴다.
    codes = {t: run(t) for t in TOKENS}
    return codes['USDC']


if __name__ == '__main__':
    sys.exit(main())
