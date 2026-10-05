#!/usr/bin/env python3
"""Tether USDT 연결 준비금 보고서(BDO 보증보고서 + Consolidated Reserves Report) PDF 파서.

data/samples/Tether_USDT_Assurance_*.pdf 를 읽어 data/reports_tether.json 을 만든다.
출력 스키마는 data/reports_paxos.json(parse_paxos.py)과 같다.
Tether 보고서는 USD₮, EUR₮ 등 여러 토큰을 발행하는 법인들의 연결 보고서라 token은 'USDT', flags.consolidated=true.
합계 대사가 어긋나거나 모르는 행이 나오면 그 보고서를 결과에서 빼고 이유를 로그로 남긴다.

사용: python3 scripts/parse_tether.py
"""
import json, re, subprocess, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'samples'
OUT = ROOT / 'data' / 'reports_tether.json'

MONTHS = {m: i for i, m in enumerate(
    'january february march april may june july august september october november december'.split(), 1)}
AMT = r'\d{1,3}(?:,\d{3})+'

# 표 행 라벨 -> (키, components 키). 위에서부터 처음 맞는 것. 모르는 라벨은 오류로 멈춘다.
# 함정: 라벨이 줄바꿈되고 각주 번호가 붙어('Treasury Bills4') 라벨 전체가 아닌 앞부분만 본다.
ROWS = [
    (r'subtotal', 'subtotal', None),
    (r'^\W*total\b', 'total', None),
    (r'non-?\s?u\.?s\.? treasury', 'non_us_treasury', 'other'),
    (r'u\.s\. treasury bills', 'us_treasury', 'treasury'),
    (r'overnight reverse', 'overnight_repo', 'repo'),
    (r'term reverse', 'term_repo', 'repo'),
    (r'money market funds', 'mmf', 'government_mmf'),
    (r'cash & bank', 'cash_bank', 'cash'),
    (r'corporate bonds', 'corporate_bonds', 'other'),
    (r'precious metals', 'precious_metals', 'other'),
    (r'bitcoin', 'bitcoin', 'other'),
    (r'public equities', 'public_equities', 'other'),
    (r'other investments', 'other_investments', 'other'),
    (r'secured loans', 'secured_loans', 'other'),
]
SHORT_TERM = ('us_treasury', 'overnight_repo', 'term_repo', 'mmf', 'cash_bank', 'non_us_treasury')  # Subtotal 대상


def num(s):
    return int(s.replace(',', ''))


def to_iso(s):
    """'31 March 2023' -> '2023-03-31'"""
    d, mon, y = s.split()
    return f'{y}-{MONTHS[mon.lower()]:02d}-{int(d):02d}'


def locate(text, pos):
    """문자 오프셋 -> (쪽, 줄). 쪽 구분은 폼피드(\\x0c)."""
    upto = 0
    for pi, pg in enumerate(text.split('\x0c'), 1):
        if pos <= upto + len(pg):
            return pi, pg[:pos - upto].count('\n') + 1
        upto += len(pg) + 1
    return None, None


def cite(text, pos, raw):
    page, line = locate(text, pos)
    return {'page': page, 'line': line, 'raw': raw}


def text_of(pdf):
    # 함정: pdftotext를 스레드풀 안에서 부르면 빈 문자열이 나온다. 순차 호출만 쓴다.
    return subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, check=True).stdout


def table_rows(text):
    """'Asset Category' 표를 (키, 금액, 라벨, 오프셋) 목록으로. 라벨과 금액이 다른 줄에 걸쳐도 이어 붙인다.
    금액만 있는 줄은 바로 앞의 금액 없는 라벨 줄에 붙이고, 라벨 줄에 금액이 있으면 그 줄 안에서 푼다."""
    m = re.search(r'Asset Category', text)
    end = re.search(r'^\s*Total\b.*\(1\+', text[m.end():], re.M) if m else None
    if not end:
        return None, '자산 표(Asset Category ... Total (1+)를 찾지 못함'
    start, stop = m.start(), text.find('\n', m.end() + end.end())
    body, rows, pending, pos = text[start:stop], [], None, start
    for ln in body.splitlines(keepends=True):
        lab = ln.strip()
        hit = next(((k, ck) for pat, k, ck in ROWS if re.search(pat, lab.lower())), None)
        amts = list(re.finditer(AMT, ln))
        if hit and not amts:
            pending = (hit, lab)
        elif amts:
            if not hit and pending: hit, lab = pending[0], pending[1]
            if hit: rows.append((hit[0], num(amts[-1].group(0)), re.split(r'\s{3,}', re.sub(r'^\d+\.\s*', '', lab))[0], pos + amts[-1].start(), hit[1]))
            elif re.search(r'[A-Za-z]{4}', lab.replace('Asset Category', '').replace('Amount in USD', '').replace('US$', '')):
                return None, f'모르는 표 행: {lab!r}'
            pending = None
        pos += len(ln)
    return rows, None


# ---- 규칙 입력값(holdings 등). 값은 전부 원문에서 읽고 쪽, 줄을 남긴다. ----
KIND = {  # 표 행 키 -> (holdings kind, 표준 라벨)
    'us_treasury': ('treasury_bill', 'U.S. Treasury Bills'),
    'overnight_repo': ('reverse_repo_overnight', 'Overnight Reverse Repurchase Agreements'),
    'term_repo': ('reverse_repo_term', 'Term Reverse Repurchase Agreements'),
    'mmf': ('government_mmf', 'Money Market Funds'),
    'cash_bank': ('bank_deposit', 'Cash & Bank Deposits'),
    'non_us_treasury': ('non_us_government_bill', 'Non-U.S. Treasury Bills'),
    'corporate_bonds': ('corporate_bond', 'Corporate Bonds'),
    'precious_metals': ('precious_metal', 'Precious Metals'),
    'bitcoin': ('bitcoin', 'Bitcoin'),
    'public_equities': ('public_equity', 'Public Equities'),
    'other_investments': ('other_investment', 'Other Investments'),
    'secured_loans': ('secured_loan', 'Secured Loans'),
}
TREASURY_KINDS = ('treasury_bill', 'treasury_note', 'non_us_government_bill')
CUSTODIAN_NAMES = (r'Cantor|BNY|Bank of|JPMorgan|Citi(?:bank|group)|Goldman|Deutsche|Anchorage|Fireblocks|Wells Fargo|'
                   r'Standard Chartered|Silvergate|Signature Bank|Metropolitan|Credit Suisse|UBS|HSBC|Barclays|Fidelity|'
                   r'State Street|Coinbase|BitGo|Zodia|Loomis|Brink|Malca|Cumberland|Maple|Frick|Sygnum|Kraken|Binance|'
                   r'Wedbush|Mizuho|Natixis|Morgan Stanley|Jefferies|Marex|StoneX|Amundi')


def find(text, pat):
    """원문에서 패턴(공백 줄바꿈 무시)을 찾아 (인용, 정리한 원문) 반환. 없으면 (None, None)."""
    m = re.search(pat, text, re.S)
    if not m: return None, None
    raw = re.sub(r'\s+', ' ', m.group(0)).strip()
    return cite(text, m.start(), raw), raw


def rule_fields(text, r, rows):
    """보고서마다 holdings, fund_holdings, 만기, 공시 주기 외 규칙 입력값을 r에 더한다."""
    hold = []
    for key, amt, _label, pos, _ck in rows:
        if key not in KIND: continue  # subtotal, total
        kind, label = KIND[key]
        hold.append({'kind': kind, 'amount': amt, 'currency': r['reserve_currency'], 'maturity_max_days': None,
                     'maturity_listed': False, 'label': label, 'where': cite(text, pos, f'{amt:,}')})

    # 만기 문장. 종목별 만기는 보고서 어디에도 없고 범주 설명(평균 만기)만 있다.
    c_ovn, t_ovn = find(text, r'The\s+\W+Overnight\s+Reverse-Repurchase\s+Agreements\W+\s+category\s+comprises\s+Reverse-Repurchase\s+Agreements\s+with\s+a\s+maturity\s+of\s+1\s+day')
    c_term, t_term = find(text, r'The\s+\W+Term\s+Reverse-Repurchase\s+Agreements\W+[^.]*?maturity\s+of\s+less\s+than\s+\d+\s+days')
    c_ust, t_ust = find(text, r'The\s+\W+U\.S\.\s+Treasury\s+Bills\W+\s+category\s+comprises\s+U\.S\.\s+Treasury\s+Bills\s+with\s+a\s+[^.]*?\d+\s+days')
    c_non, t_non = find(text, r'The\s+\W+Non-\s?U\.?S\.?\s+Treasury\s+Bills\W+\s+have\s+a\s+[^.]*?\d+\s+days')
    for h in hold:
        if h['kind'] == 'reverse_repo_overnight' and c_ovn:
            h['maturity_max_days'], h['maturity_listed'] = 1, True  # 범주 전체가 '1 day'

    # 펀드 안 보유 종목: MMF 간접 노출(미국 단기국채) 표. 2023-06부터 2025-09까지만 있다.
    fund = []
    m = re.search(rf'Money Market Funds\s+({AMT})\s+({AMT})', text[text.find('indirect exposure') if 'indirect exposure' in text else 0:])
    if 'indirect exposure' in text and m:
        base = text.find('indirect exposure')
        fund.append({'kind': 'treasury_bill', 'amount': num(m.group(2)), 'currency': r['reserve_currency'],
                     'maturity_max_days': None, 'maturity_listed': False,
                     'label': 'Money Market Funds: Fair value of the US Treasuries bills indirect exposure',
                     'where': cite(text, base + m.start(2), m.group(2))})
    r['holdings'], r['fund_holdings'] = hold, fund
    hsum = sum(h['amount'] for h in hold)
    r['holdings_check'] = {'expected': r['fair_value'], 'got': hsum, 'diff': hsum - r['fair_value']}
    r['asset_types'] = sorted({h['kind'] for h in hold if h['amount'] > 0})
    notes = {}

    # 4. 국채 최장 만기
    direct_t = [h for h in hold if h['kind'] in TREASURY_KINDS and h['amount'] > 0]
    fund_t = [h for h in fund if h['kind'] in TREASURY_KINDS and h['amount'] > 0]
    mats = [h['maturity_max_days'] for h in direct_t + fund_t]
    r['treasury_maturity_basis'] = 'both' if direct_t and fund_t else 'direct' if direct_t else 'fund' if fund_t else None
    if not direct_t and not fund_t:
        r['treasury_max_maturity_days'] = None
        notes['treasury_max_maturity_days'] = {'state': 'not_applicable', 'where': None, 'note': '국채 보유 없음'}
    elif mats and all(x is not None for x in mats):
        r['treasury_max_maturity_days'] = max(mats)
        notes['treasury_max_maturity_days'] = {'state': 'found', 'where': None, 'note': '종목별 만기에서 계산'}
    else:
        r['treasury_max_maturity_days'] = None
        wh = [c for c in (c_ust, c_non) if c] + [h['where'] for h in fund_t]
        txt = ' / '.join(t for t in (t_ust, t_non) if t)
        fnote = (f" 펀드 안 국채(MMF 간접 노출 {fund_t[0]['amount']:,})도 종목별 만기가 없다." if fund_t else '')
        notes['treasury_max_maturity_days'] = {'state': 'not_in_report', 'where': wh or None, 'note':
            f'종목별 만기가 원문에 없다. 범주 설명만 있고 평균 만기라 최장 만기로 쓸 수 없다. 원문: {txt}.{fnote} '
            f"treasury_maturity_basis는 국채를 가진 곳을 뜻한다({'직접' if direct_t else ''}{' 및 ' if direct_t and fund_t else ''}{'펀드 안' if fund_t else ''})."}

    # 5. 역레포 최장 만기
    ovn = any(h['kind'] == 'reverse_repo_overnight' and h['amount'] > 0 for h in hold)
    term = any(h['kind'] == 'reverse_repo_term' and h['amount'] > 0 for h in hold)
    if not ovn and not term:
        r['repo_max_maturity_days'] = None
        notes['repo_max_maturity_days'] = {'state': 'not_applicable', 'where': None, 'note': '역레포 보유 없음'}
    elif ovn and not term and c_ovn:
        r['repo_max_maturity_days'] = 1
        notes['repo_max_maturity_days'] = {'state': 'found', 'where': c_ovn, 'note': f'원문: {t_ovn}'}
    else:
        r['repo_max_maturity_days'] = None
        notes['repo_max_maturity_days'] = {'state': 'not_in_report', 'where': [c for c in (c_ovn, c_term) if c], 'note':
            f'하루짜리 역레포 원문: {t_ovn}. 기간물 역레포는 만기일 없이 평균 만기만 있어 최장 만기를 알 수 없다. 원문: {t_term}'}

    # 7. 유통량 계산식
    c_cf, t_cf = find(text, r'comprises\s+the\s+(?:consolidated\s+)?amount\s+related\s+to\s+the\s+total\s+digital\s+tokens\s+issued\s+less\s+digital\s+tokens\s+held\s+by\s+the[^.]*?treasury\s+wallet\.\s+Digital\s+tokens\s+in\s+the\s+treasury\s+wallet\s+are\s+authori[sz]ed\s+but\s+not\s+yet\s+issued[^.]*\.')
    g = re.search(rf'related\s+to\s+all\s+digital\s+tokens\s+issued[^$]*?US\$\.?\s*({AMT})', text)
    h = re.search(rf'not\s+in\s+its\s+treasury\s+wallet\s+is\s+equal\s+to\s+US\$\.?\s*({AMT})', text)
    r['circulation_formula_disclosed'] = bool(c_cf)
    if c_cf:
        calc = (f" 각주 수치: 총 발행 {num(g.group(1)):,} - 발행사 보유(국고 지갑 밖) {num(h.group(1)):,} = {num(g.group(1)) - num(h.group(1)):,}, "
                f"확인문 유통량 {r['circulation']:,}과 차이 {num(g.group(1)) - num(h.group(1)) - r['circulation']:,}.") if g and h else ''
        notes['circulation_formula_disclosed'] = {'state': 'found', 'where': c_cf, 'note':
            f'유통량(발행 토큰 부채)을 발행 토큰 총액에서 발행사가 갖고 있지만 국고 지갑(treasury wallet) 밖인 토큰을 뺀 값으로 센다고 적었다. 국고 지갑 안 토큰은 승인만 되고 미발행이라 부채가 아니다. 원문: {t_cf}{calc}'}
    else:
        notes['circulation_formula_disclosed'] = {'state': 'not_disclosed', 'where': None, 'note':
            "원문 전체에서 'digital tokens issued', 'treasury wallet', 'less digital tokens held'를 검색했으나 계산식 설명이 없다."}

    # 8. 보관 기관 이름
    names = sorted(set(re.findall(CUSTODIAN_NAMES, text)))
    ncust = len(re.findall(r'custodian', text, re.I)); nbank = len(re.findall(r'\bbanks?\b', text, re.I))
    r['custodian_disclosure'], r['custodians'] = bool(names), names
    notes['custodian_disclosure'] = ({'state': 'found', 'where': None, 'note': f'기관 이름: {names}'} if names else {'state': 'not_disclosed', 'where': None, 'note':
        f"원문 전체에서 'custodian'(대소문자 무시, {ncust}회), 'bank'({nbank}회)와 주요 은행, 수탁기관 이름 목록({CUSTODIAN_NAMES.count('|') + 1}개)을 검색했다. "
        "모두 일반 명사이거나 Tether 계열사, BDO 이름뿐이고 준비자산을 맡긴 기관 이름은 없다. 'Cash & Bank Deposits' 각주는 기관 이름 없이 'cash deposits at financial institutions'라고만 적었다."})

    # 9. 경영진 서명
    c_sg, t_sg = find(text, r'Authori[sz]ed\s+and\s+approved\s+by\s+the\s+(?:Board\s+of\s+Directors|Sole\s+Administrator)[^:]*?:')
    mt = re.search(r'as\s+(Chairman\s+of\s+the\s+Board\s+of\s+Directors|director)\s*:|approved\s+by\s+the\s+(Sole\s+Administrator)', t_sg or '')
    r['management_certification'] = bool(c_sg and mt)
    r['certifier'] = re.sub(r'\s+', ' ', mt.group(1) or mt.group(2)) if c_sg and mt else None
    notes['management_certification'] = ({'state': 'found', 'where': c_sg, 'note':
        f"'Management's Assertion'라는 이름의 별도 문서는 없고, 보고서 말미에 이사회 승인문과 서명(이미지)이 있다. 서명 줄은 PDF 쪽을 그림으로 열어 확인했다. 원문: {t_sg}"}
        if r['management_certification'] else {'state': 'not_disclosed', 'where': None, 'note': "'Authorized and approved by ... signed' 문장을 찾지 못했다."})

    # 10. 상환 기한, 이자 지급
    red = re.search(r'redemption\s+(?:period|deadline|within)|within\s+\d+\s+(?:business\s+)?days|\d+\s+(?:business\s+)?days\s+of\s+(?:a\s+)?redemption', text, re.I)
    c_dem, t_dem = find(text, r'Tether\s+tokens\s+issued\s+have\s+been\s+classified\s+as\s+refund\s+liabilities[^.]*?repayable\s+on\s+demand')
    r['redemption_days'] = None
    notes['redemption_days'] = {'state': 'not_in_report', 'where': c_dem, 'note':
        ("확인 필요: 상환 기한 문장 후보가 있음. " if red else '') +
        f"상환 기한(일 수) 문장이 없다. 검색: 'redemption period/deadline/within N days'. 원문에는 {t_dem} 만 있고 이는 회계 분류라 일 수가 아니다. 상환 수수료는 10 basis points."}
    ints = re.search(r'\binterest\b|\byield\b|\bcoupon\b', text, re.I)
    r['interest_paid'] = None
    notes['interest_paid'] = {'state': 'not_in_report', 'where': None, 'note':
        ("확인 필요: 이자 관련 단어가 있음. " if ints else '') + "원문 전체에서 'interest', 'yield', 'coupon'을 검색했으나 토큰 보유자에게 이자를 지급한다는 문장이 없다."}

    # 6. 공시 주기는 main에서 연속 보고서 간격으로 채운다. 인용만 먼저 남긴다.
    r['_cadence_cite'] = find(text, r'perform\s+enquiries\s+with\s+the\s+management\s+on\s+the\s+business\s+operation\s+of\s+the\s+last\s+quarter')
    r['field_notes'] = notes


def parse(pdf):
    text = text_of(pdf)
    if len(text.strip()) < 2000 or any(not p.strip() for p in text.split('\x0c')[:-1]):
        return {'source_file': str(pdf.relative_to(ROOT)), 'ok': False, 'error': '글자 층 없는 쪽이 있음(OCR 필요)'}
    r = {'source_file': str(pdf.relative_to(ROOT)),
         'issuer': next(l.strip() for l in text.splitlines() if l.strip()), 'token': 'USDT'}
    sources = {}

    m = re.search(r'point in time as of\s+(\d{1,2} [A-Za-z]+ \d{4})\s+at\s+(\d{1,2}:\d{2})\s*([AP])M\s+UTC', text)
    if not m:
        return {**r, 'ok': False, 'error': 'Reporting Date 문구를 찾지 못함'}
    hh = int(m.group(2).split(':')[0]) % 12 + (12 if m.group(3) == 'P' else 0)
    r['as_of'] = to_iso(m.group(1))
    r['report_dates'] = [r['as_of']]
    r['month'] = r['as_of'][:7]
    r['as_of_time'] = f'{hh:02d}:{m.group(2).split(":")[1]} UTC'
    sources['as_of'] = cite(text, m.start(1), m.group(1))
    m = re.search(r'Amount in USD|^\s*Asset Category\s+US\$', text, re.M)
    r['reserve_currency'] = 'USD' if m else None
    if m: sources['reserve_currency'] = cite(text, m.start(), re.sub(r'\s+', ' ', m.group(0).strip()))

    # 유통량 = 총부채가 아니라 '그중 발행 토큰 부채' 줄. 2023은 '...total liabilities amount to US$ L of which US$ T relates to ...'
    m = re.search(rf'US\$\s*({AMT}),?\s+of\s+which\s+US\$\s*({AMT})[\d\s]{{0,40}}relates\s+to\s+digital\s+tokens\s+issued', text)
    if not m:
        return {**r, 'ok': False, 'error': '발행 토큰 부채 줄(of which US$ ... relates to digital tokens issued)을 찾지 못함'}
    total_liab, r['circulation'] = num(m.group(1)), num(m.group(2))
    sources['circulation'] = cite(text, m.start(2), m.group(2))
    sources['total_liabilities'] = cite(text, m.start(1), m.group(1))
    # 각주 번호가 금액 뒤에 붙는 경우(…,6262)를 거르는 교차 확인: 총발행 - 그룹 보유분 = 부채로 잡힌 발행 토큰
    g = re.search(rf'redemption\s+value\s+related\s+to\s+all\s+digital\s+tokens\s+issued[^$]*?US\$\s*({AMT})', text)
    h = re.search(rf'but\s+not\s+in\s+its\s+treasury\s+wallet\s+is\s+equal\s+to\s+US\$\s*({AMT})', text)
    note_gap = (num(g.group(1)) - num(h.group(1)) - r['circulation']) if g and h else None

    # 준비자산 총액 = 경영진 확인문의 총자산
    m = re.search(rf'(?:total assets amount to at least|Reserves for Tether tokens in circulation amount to)\s+US\$\s*(\d{{1,3}}(?:,\s?\d{{3}})+)', text)
    if not m:
        return {**r, 'ok': False, 'error': '총자산 확인문(total assets ... / Reserves ... amount to)을 찾지 못함'}
    r['fair_value'] = num(re.sub(r'\s', '', m.group(1)))
    sources['fair_value'] = cite(text, m.start(1), m.group(1))

    rows, err = table_rows(text)
    if err:
        return {**r, 'ok': False, 'error': err}
    comp = dict.fromkeys(('cash', 'repo', 'government_mmf', 'treasury', 'other'), 0)
    got = {}
    sources['rows'] = []
    for key, amt, label, pos, ck in rows:
        got[key] = got.get(key, 0) + amt
        if ck: comp[ck] += amt
        sources['rows'].append({'label': label, 'key': key, **cite(text, pos, f'{amt:,}')})
    if 'total' not in got or 'subtotal' not in got:
        return {**r, 'ok': False, 'error': 'Subtotal 또는 Total 행이 없음'}
    r['components'] = comp

    checks = {
        'components_sum': {'expected': got['total'], 'got': sum(comp.values()), 'diff': sum(comp.values()) - got['total']},
        'total_equals_fair_value': {'expected': r['fair_value'], 'got': got['total'], 'diff': got['total'] - r['fair_value']},
        'subtotal': {'expected': got['subtotal'], 'got': sum(got.get(k, 0) for k in SHORT_TERM),
                     'diff': sum(got.get(k, 0) for k in SHORT_TERM) - got['subtotal']},
        'covers_circulation': {'surplus': r['fair_value'] - r['circulation'], 'ok': r['fair_value'] >= r['circulation']},
        'liabilities_cover_tokens': {'ok': total_liab >= r['circulation']},
    }
    r['reconciliation'] = checks
    r['ok'] = (all(checks[k]['diff'] == 0 for k in checks if 'diff' in checks[k])
               and checks['covers_circulation']['ok'] and checks['liabilities_cover_tokens']['ok'])
    if r['ok']:
        r['coverage'] = round(r['fair_value'] / r['circulation'], 8)

    m = re.search(r'(?:Milan|Roma),\s+(\d{1,2} [A-Za-z]+ \d{4})\s*\n+\s*(BDO[^\n]*?)\s*\n', text)
    r['attestation'] = {
        # ISAE 3000 Revised, 'for reasonable assurance engagements'. 2023부터 2026까지 같은 문구.
        'type': 'reasonable assurance' if re.search(r'reasonable\s+assurance\s+engagement', text) else None,
        'standard': 'ISAE 3000 (Revised)' if re.search(r'International Standard on\s+Assurance Engagements 3000 \(Revised\)', text) else None,
        'signed': to_iso(m.group(1)) if m else None,
        'firm': m.group(2) if m else None,
    }
    if m: sources['attestation.signed'] = cite(text, m.start(1), m.group(1))
    r['flags'] = {
        'consolidated': True,
        'scan_suspected': False,
        'mmf_row_absent': 'mmf' not in got,  # 2025-12부터 Money Market Funds 행이 표에서 빠짐
        # 각주 '총발행 - 그룹 보유분'이 확인문 발행 토큰 부채와 다른 보고서(2026-03, 2026-06은 원문 자체가 안 맞음). 대사에는 넣지 않는다.
        'token_note_gap': note_gap if note_gap else None,
        'public_equities_row': 'public_equities' in got,  # 2026-03부터 새 행(other로 합산)
    }
    r['sources'] = sources
    rule_fields(text, r, rows)
    r['ok'] = r['ok'] and r['holdings_check']['diff'] == 0
    return r


def main():
    reports, bad = [], []
    for p in sorted(SRC.glob('Tether_USDT_Assurance_*.pdf')):
        r = parse(p)
        reports.append(r)
        if r.get('ok'):
            print(f"ok  USDT {r['month']}  유통 {r['circulation']:,}  준비자산 {r['fair_value']:,}  "
                  f"커버리지 {r['coverage'] * 100:.4f}%  기준일 {r['as_of']}  서명 {r['attestation']['signed']}")
        else:
            bad.append(p.name)
            print(f"FAIL {p.name}: {r.get('error') or r.get('reconciliation')}")
    if not reports:
        print('PDF 없음:', SRC); return 1
    good = [r for r in reports if r.get('ok')]
    # 6. 공시 주기: 연속 보고서 기준일 간격과 BDO 문장('the last quarter')으로 정한다. monthly=31일, quarterly=92일.
    ds = [datetime.date.fromisoformat(r['as_of']) for r in good]
    for i, r in enumerate(good):
        gap = (ds[i] - ds[i - 1]).days if i else (ds[1] - ds[0]).days if len(ds) > 1 else None
        cad = None if gap is None else 'monthly' if gap <= 35 else 'quarterly' if 85 <= gap <= 95 else None
        c, t = r.pop('_cadence_cite')
        r['disclosure_cadence'] = cad
        r['disclosure_cadence_days'] = {'monthly': 31, 'quarterly': 92}.get(cad)
        r['field_notes']['disclosure_cadence'] = {'state': 'found' if cad else 'not_in_report', 'where': c, 'note':
            f"기준일 간격 {gap}일(" + ('다음 보고서와' if not i else '직전 보고서와') + f" 비교, data/samples 연속 {len(good)}건). 원문: {t}"}
    excluded = [{'token': 'USDT', 'month': r.get('month') or pathlib.Path(r['source_file']).stem[-7:],
                 'source_file': r['source_file'], 'reason': r.get('error') or f"대사 실패: {r.get('reconciliation')} {r.get('holdings_check')}"}
                for r in reports if not r.get('ok')]
    OUT.write_text(json.dumps({
        'generated': datetime.date.today().isoformat(),
        'source': 'Tether USDT 분기 연결 준비금 보고서(BDO ISAE 3000 reasonable assurance), pdftotext -layout',
        'note': ('연결 준비금 보고서라 token=USDT, flags.consolidated=true. '
                 'circulation=확인문 "of which US$ X relates to digital tokens issued" 줄(발행 토큰 부채, 총부채 아님). '
                 'fair_value=확인문 총자산(2023 "total assets amount to at least", 2024 이후 "Reserves for Tether tokens in circulation amount to")이며 자산 표 Total과 같아야 한다. '
                 'components: cash=Cash & Bank Deposits, treasury=U.S. Treasury Bills, repo=Overnight 및 Term Reverse Repurchase Agreements 합, '
                 'government_mmf=Money Market Funds(2025-12부터 행 없음, 0), '
                 'other=Non-U.S. Treasury Bills, Corporate Bonds, Precious Metals, Bitcoin(s), Public Equities(2026-03부터), Other Investments, Secured Loans 합. '
                 'sources.rows는 표 행별 원문 라벨, 금액, 쪽, 줄. Subtotal은 단기 6행 합과 따로 대사. '
                 '대사 실패 보고서는 reports에서 제외하고 excluded에 이유를 남김. '
                 '규칙 입력값: holdings(표 행별 kind, 합=fair_value는 holdings_check), fund_holdings(MMF 간접 노출 미국 단기국채), asset_types, '
                 'treasury_max_maturity_days, repo_max_maturity_days(원문에 종목별 만기가 없으면 null이고 field_notes에 not_in_report와 원문 문장), '
                 'disclosure_cadence, circulation_formula_disclosed, custodian_disclosure, management_certification, redemption_days, interest_paid, field_notes.'),
        'excluded': excluded,
        'reports': good,
    }, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n{len(reports)}건 중 성공 {len(reports) - len(bad)} → {OUT.relative_to(ROOT)}, 대사 실패 {len(bad)}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
