"""Jev(TypeSafe) 글 항목 고르기 시험.

레포의 검증된 값(tests/test_rule_inputs.py 표, 코인별 시험이 확인하는 data/reports*.json 값)으로 정답 세트를 만들고,
Jev가 고른 답과 확신값을 채점한다. 숫자 판독은 묻지 않는다(두 독자 대조와 합계 대사가 맡는다).

  python3 scripts/jev/jev_choice_test.py gold            정답 세트(goldset.json)만 만든다. API를 부르지 않는다.
  python3 scripts/jev/jev_choice_test.py run [--limit N]  Jev를 불러 results.json, summary.md를 쓴다.
  python3 scripts/jev/jev_choice_test.py report          results.json으로 summary.md만 다시 쓴다.

키: 레포 루트 .env.local의 TYPESAFE_API_KEY. 값은 출력하지 않는다(오류 본문에서도 지운다).
data/*.json은 읽기만 한다. 파서와 pytest는 부르지 않는다(test_rule_inputs는 정답 표만 읽으려고 import한다).
API: POST https://api.typesafe.ai/v1/systemone (docs.typesafe.ai/api). 요금은 입력 토큰 100만 개당 0.042달러, 출력 무료(docs.typesafe.ai/models).
"""
import datetime, json, pathlib, re, statistics, subprocess, sys, time, urllib.error, urllib.request

sys.dont_write_bytecode = True  # 레포 모듈 import 때 __pycache__를 새로 쓰지 않는다
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs' / 'research' / 'Jev시험_2026-10-09'
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests')]
from rule_inputs import KINDS  # noqa: E402  자산 종류 16종(파서가 holdings[].kind에 쓰는 목록)
import test_rule_inputs as V  # noqa: E402  검증된 값 표(CIRC, CUST, ASSET_TYPES)

API = 'https://api.typesafe.ai/v1'
MODEL = 'jev-1.13.0'
USD_PER_TOKEN = 0.042 / 1_000_000
BUDGET_USD = 1.0  # 충전액 5달러 가운데 이 시험에 쓰는 한도. 넘기 전에 멈춘다
GATE = 0.8  # 확신값 기준
TOKENS = ('USDC', 'EURC', 'PYUSD', 'USDP', 'USDG', 'RLUSD', 'GUSD', 'USDT')

# ---- 질문(영어. 문서상 영어 정확도가 가장 높다). 설명은 레포 정의를 옮겼다 ----
# 자산 종류: site/app.js KIND_NAMES, data/reports*.json의 kind 매핑 메모
ASSET_Q = ('Which asset category does this line of a stablecoin reserve report belong to? In these reports, repurchase '
           "agreements held as reserve assets are reverse repurchase agreements from the reserve's side.")
KIND_TEXT = {
    'bank_deposit': 'Cash held as deposits at banks or other regulated financial institutions.',
    'term_deposit': 'Fixed-term (time) deposits at banks.',
    'treasury_bill': 'U.S. Treasury bills: U.S. government debt that matures in one year or less.',
    'treasury_note': 'U.S. Treasury notes or bonds: U.S. government debt issued with a maturity of more than one year.',
    'non_us_government_bill': 'Treasury bills issued by a government other than the United States.',
    'reverse_repo_overnight': 'Overnight reverse repurchase agreements: cash lent for one day against securities as collateral.',
    'reverse_repo_term': 'Term reverse repurchase agreements: cash lent for more than one day against securities as collateral.',
    'government_mmf': 'Shares of money market funds, such as government money market funds.',
    'corporate_bond': 'Bonds issued by companies.',
    'precious_metal': 'Gold or other precious metals.',
    'bitcoin': 'Bitcoin.',
    'secured_loan': 'Loans made to others that are secured by collateral.',
    'public_equity': 'Shares of listed companies.',
    'other_investment': 'Other investments that fit none of the other categories.',
    'settlement': ('Not an investment: timing and settlement differences, amounts receivable or payable from pending '
                   'transactions, accrued interest, or rounding differences.'),
    'cash_equivalents_unsplit': ('One combined line of cash and cash equivalents that the report does not split into '
                                 'deposits, funds, or repurchase agreements.'),
}
assert tuple(KIND_TEXT) == KINDS
# R08: site/engine.js ASSURANCE_LEVEL의 종류, site/화면문구.json R08 설명. 값 이름은 attestation.type 그대로
R08_Q = 'What kind of engagement did the independent accountant perform on this reserve report?'
R08_TEXT = {
    'agreed_upon_procedures': ('Agreed-upon procedures: the accountant performs procedures agreed with the company and '
                               'reports findings without giving assurance.'),
    'review': 'Review: a limited assurance engagement (for example "We have reviewed").',
    'examination': ("Examination: the accountant examined management's assertion (for example \"We have examined\" or "
                    '"Our examination was conducted in accordance with").'),
    'reasonable assurance': ("Reasonable assurance engagement: the accountant's report is titled or described as a "
                             'reasonable assurance report or engagement rather than as an examination.'),
    'audit': 'Audit: an audit of financial statements (for example "We have audited the financial statements").',
}
# R11, R12, R15: site/화면문구.json 규칙 설명(728, 729, 732행)과 근거 설명(745, 746, 749행)
NOUL = {
    'R11': ('Does the report explain how the number of tokens in circulation was counted, for example whether issued, '
            'burned, frozen, or non-redeemable tokens are included or excluded?',
            {'true': 'The report describes the method or definition used to count the tokens in circulation.',
             'false': 'The report gives the number of tokens in circulation without explaining how it was counted.'}),
    'R12': ('Does the report name the specific banks or custodians that hold the reserve assets?',
            {'true': 'At least one bank or custodian holding reserve assets is named.',
             'false': ('Institutions holding the reserve are described only by type (for example "regulated financial '
                       'institutions") or anonymously (for example "Bank 1"), or not at all.')}),
    'R15': ("Did a member of the issuer's management, such as the chief executive or a finance officer, sign a statement "
            "that the report's information is correct?",
            {'true': ('The report contains a management assertion or a signature block with the name and title of an '
                      'officer or director of the issuer.'),
             'false': "No one from the issuer's management signed; only the accountant signed, or nobody did."}),
}
FIELD = {'R11': 'circulation_formula_disclosed', 'R12': 'custodian_disclosure', 'R15': 'management_certification'}
TABLE = {'R11': 'CIRC', 'R12': 'CUST'}
# attestation.type을 확인하는 시험. USDC는 이 값을 확인하는 시험이 없어 R08에서 뺀다
R08_TEST = {'EURC': 'tests/test_eurc.py test_attestation_is_examination',
            'GUSD': 'tests/test_gemini.py test_attestation_is_examination',
            'RLUSD': 'tests/test_ripple.py test_attestation_is_examination',
            'PYUSD': 'tests/test_paxos.py test_usdg_uses_reasonable_assurance_from_2026',
            'USDP': 'tests/test_paxos.py test_usdg_uses_reasonable_assurance_from_2026',
            'USDG': 'tests/test_paxos.py test_usdg_uses_reasonable_assurance_from_2026',
            'USDT': 'tests/test_tether.py test_attestation_is_isae3000_reasonable_assurance'}
R08_SIGN = {'examination': r'We have examined|Our examination', 'reasonable assurance': r'reasonable\s+assurance\s+(report|engagement)'}
TASK_NAME = {'asset': '자산 종류(16종 중 하나)', 'R08': 'R08 검증 종류', 'R11': 'R11 발행잔액 계산식 공개',
             'R12': 'R12 보관 기관 공개', 'R15': 'R15 경영진 서명'}
# 틀린 문항을 원문, 파서와 대조해 적은 까닭(2026-10-09 실행). 틀린 문항에만 표에 나온다
_CUSIP = '단기(bill)와 중기(note)는 CUSIP 앞자리로 가른다(scripts/parse_circle.py 121행). 줄 이름은 둘 다 U.S. Treasury Securities다.'
_RLUSD = ('2025-08부터 정의 문장에서 "issued, outstanding and redeemable"이 빠지고 "currently present on ... blockchain networks"'
          '(체인 위 잔액)만 남았다. 옛 문장(D26 2024-12)은 맞혔다. 레포 메모는 RLUSD 모든 달에 계산식은 아니라고 적고 값은 예로 둔다'
          '(data/reports_ripple.json field_notes).')
_USDT = ('"total digital tokens issued less digital tokens held by the group but not in its treasury wallet" 문장이 입력에 있다. '
         '유통량이 아니라 발행 토큰 부채(liabilities)라는 말로 적혀 있다.')
REVIEW = {'A01': 'Circle Reserve Fund가 정부 MMF라는 설명은 보고서 다른 곳에 있고 줄 이름에는 없다.',
          'A07': _CUSIP, 'A12': _CUSIP,
          'A56': 'MMF 안 국채 내역을 따로 적은 줄이라 파서는 펀드 안 보유(fund_holdings)의 국채로 둔다. 입력에는 내역 줄이라는 표시가 없다.',
          'D27-R11': _RLUSD, 'D28-R11': _RLUSD, 'D32-R11': _USDT, 'D33-R11': _USDT, 'D34-R11': _USDT}


# ---- 정답 세트 ----

def load_reports():
    out = []
    for f in sorted((ROOT / 'data').glob('reports*.json')):
        for i, r in enumerate(json.loads(f.read_text(encoding='utf-8'))['reports']):
            out.append((f.relative_to(ROOT).as_posix(), i, r))
    return sorted(out, key=lambda x: (TOKENS.index(x[2]['token']), x[2]['month']))


def pdf_pages(pdf):
    """pdftotext -layout(파서와 같은 방식) 쪽별 글. 칸 맞춤 공백은 두 칸으로 줄인다. 글자 층이 없는 쪽은 빈 글."""
    raw = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
    pages = raw.split('\x0c')
    if pages and pages[-1] == '': pages.pop()
    return ['\n'.join(re.sub(r'\s{2,}', '  ', ln).strip() for ln in p.splitlines() if ln.strip()) for p in pages]


def page_of(where):
    if isinstance(where, dict): return where.get('page')
    m = re.search(r'p\.(\d+)', where or '')
    return int(m[1]) if m else None


def evidence_ok(r, field, pages):
    """'예' 정답의 근거 쪽이 글자 층에 있는지. 파서가 OCR로 읽은 쪽(flags.ocr_pages)은 pdftotext 글에 없다."""
    w = r['field_notes'][field]['where']
    p = page_of(w)
    return bool(p and p <= len(pages) and pages[p - 1] and p not in r['flags'].get('ocr_pages', [])
                and not (isinstance(w, dict) and w.get('ocr')))


def asset_items(reports):
    items, seen = [], set()
    for f, i, r in reports:
        tok, m = r['token'], r['month']
        for src in ('holdings', 'fund_holdings'):
            for j, h in enumerate(r[src]):
                if re.search('[가-힣]', h['label']): continue  # 파서가 붙인 설명(반올림 차이)은 원문 줄 이름이 아니다
                key = (tok, src, h['kind'], re.sub(r'(?i)cusip\s*\w+', 'CUSIP', h['label']))
                if key in seen: continue
                seen.add(key)
                k = h['kind']
                check = None  # 파서 분류만(정산 줄, 펀드 안 줄은 자산 종류 목록 시험에 들어가지 않는다)
                if src == 'holdings' and k != 'settlement':
                    assert k in V._at(V.ASSET_TYPES[tok], m), (tok, m, k)
                    check = 'ASSET_TYPES'
                sec = re.search(r"'([^']+?)\s+AS OF", h['where']) if isinstance(h.get('where'), str) else None
                items.append({'id': f'A{len(items) + 1:02d}', 'token': tok, 'issuer': r['issuer'], 'month': m,
                              'line_name': h['label'], 'table_section': sec[1] if sec else None, 'gold': k,
                              'gold_source': f'{f} reports[{i}].{src}[{j}].kind', 'test_check': check})
    return items


def report_gold(f, i, r):
    tok, m = r['token'], r['month']
    g = {'R11': V._at(V.CIRC[tok], m), 'R12': V._at(V.CUST[tok], m), 'R15': True}
    for rule, field in FIELD.items():
        assert r[field] is g[rule], (tok, m, rule)
    src = {rule: (f"tests/test_rule_inputs.py {TABLE[rule]}['{tok}'] 단계표; " if rule in TABLE else
                  'tests/test_rule_inputs.py test_representative_months_all_fields(전 달 True); ')
                 + f'{f} reports[{i}].{FIELD[rule]}' for rule in FIELD}
    if tok in R08_TEST:
        g['R08'] = r['attestation']['type']
        src['R08'] = f"{R08_TEST[tok]}; {f} reports[{i}].attestation.type"
    return g, src


def report_items(reports):
    """코인마다 첫 달, 가운데 달, 마지막 달, 정답이 바뀌는 달과 그 앞 달을 고른다.
    R08, R11, R12의 근거가 글자 층에 없으면(OCR 쪽) 정답이 같은 달 가운데 가장 가까운 달로 바꾼다.
    R15는 근거 쪽이 글자 층에 없는 달에서만 문항을 뺀다(정답이 모두 예라 달을 바꿀 이유가 없다)."""
    rows = {}
    for f, i, r in reports:
        pdf = ROOT / r['source_file']
        pages = pdf_pages(pdf)
        text = '\n\n'.join(f'[page {n}]\n{p}' for n, p in enumerate(pages, 1) if p)
        g, src = report_gold(f, i, r)
        keep = {k: not g[k] or evidence_ok(r, FIELD[k], pages) for k in FIELD}
        if 'R08' in g: keep['R08'] = bool(re.search(R08_SIGN[g['R08']], text, re.I))
        ok = all(v for k, v in keep.items() if k != 'R15')
        rows.setdefault(r['token'], []).append(dict(f=f, i=i, r=r, g=g, src=src, ok=ok, keep=keep, text=text,
                                                    ocr=r['flags'].get('ocr_pages', [])))
    items = []
    for tok in TOKENS:
        rs = rows[tok]
        sig = [tuple(sorted(x['g'].items())) for x in rs]
        targets = {0, len(rs) // 2, len(rs) - 1} | {k for t in range(1, len(rs)) if sig[t] != sig[t - 1] for k in (t - 1, t)}
        chosen = []
        for t in sorted(targets):
            cands = [k for k, x in enumerate(rs) if x['ok'] and sig[k] == sig[t]]
            if cands:
                k = min(cands, key=lambda k: (abs(k - t), k))
                if k not in chosen: chosen.append(k)
        for k in sorted(chosen):
            x = rs[k]
            items.append({'id': f'D{len(items) + 1:02d}', 'token': tok, 'issuer': x['r']['issuer'], 'month': x['r']['month'],
                          'as_of': x['r']['as_of'], 'source_pdf': x['r']['source_file'], 'ocr_pages_skipped': x['ocr'],
                          'dropped': [rule for rule, v in x['keep'].items() if not v],
                          'questions': [{'rule': rule, 'gold': x['g'][rule], 'gold_source': x['src'][rule]}
                                        for rule in ('R08', 'R11', 'R12', 'R15') if rule in x['g'] and x['keep'][rule]],
                          'text': x['text']})
    return items


def build_gold():
    reports = load_reports()
    gold = {'made': datetime.date.today().isoformat(),
            'asset_kinds': {'options': list(KINDS), 'source': 'scripts/rule_inputs.py KINDS'},
            'rules': {
                'asset': '줄마다 하나. 같은 코인에서 줄 이름(CUSIP 번호는 같게 봄), 표 구역, 종류가 같은 줄은 처음 나온 줄만 넣는다. '
                         '파서가 한국어로 붙인 설명 줄(반올림 차이)은 원문 줄 이름이 아니라 뺀다. 정답은 파서 분류(holdings[].kind). '
                         'test_check: ASSET_TYPES=그 달 자산 종류 목록(tests/test_rule_inputs.py ASSET_TYPES)에 이 종류가 있음, '
                         'null=파서 분류만(정산 줄과 펀드 안 줄은 그 목록에 들어가지 않는다).',
                'report': '코인마다 첫 달, 가운데 달, 마지막 달, 정답이 바뀌는 달과 그 앞 달. R08, R11, R12의 근거 쪽이 글자 층에 없으면(파서가 OCR로 읽은 쪽) '
                          '정답이 같은 달 가운데 가장 가까운 달로 바꾼다. R15는 서명 쪽이 글자 층에 없는 달에서 문항만 뺀다(dropped). '
                          '입력은 보고서 전체 pdftotext -layout 글(글자 층이 없는 쪽은 빈 쪽이라 빠짐). 아니오 정답은 근거 쪽이 따로 없어, '
                          '해당 쪽만 넣으면 예 사례에만 단서를 주게 되므로 전체 글을 넣는다.',
                'excluded': {'R14': '이용약관 원문이 레포에 없고, interest_paid는 264건 모두 null(not_in_report)이라 정답이 없다.',
                             'R08(USDC)': 'USDC attestation.type을 확인하는 시험이 없다(tests/test_parser.py는 서명일만 확인).'},
            },
            'asset_items': asset_items(reports),
            'report_items': report_items(reports)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'goldset.json').write_text(json.dumps(gold, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    a, d = gold['asset_items'], gold['report_items']
    qs = [q for x in d for q in x['questions']]
    print('자산 줄', len(a), {t: sum(x['token'] == t for x in a) for t in TOKENS})
    print('보고서', len(d), {t: [x['month'] for x in d if x['token'] == t] for t in TOKENS})
    for rule in ('R08', 'R11', 'R12', 'R15'):
        vals = [q['gold'] for q in qs if q['rule'] == rule]
        print('문항', rule, len(vals), {show(v): vals.count(v) for v in set(vals)})


# ---- API ----

def load_key():
    env = ROOT / '.env.local'
    for ln in env.read_text().splitlines():
        if '=' in ln and not ln.lstrip().startswith('#'):
            k, v = ln.split('=', 1)
            if k.strip().removeprefix('export ').strip() == 'TYPESAFE_API_KEY':
                return v.strip().strip('"\'')
    sys.exit('.env.local에 TYPESAFE_API_KEY가 없다')


def request(key, method, path, payload=None):
    """(상태 코드, 응답 JSON 또는 {'error': 본문}, 걸린 초). 429, 529는 문서대로 기다렸다 다시 부른다. 키는 오류 글에서 지운다."""
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    for n in range(4):
        t = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.status, json.loads(resp.read()), time.monotonic() - t
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors='replace').replace(key, '***')[:800]
            if e.code in (429, 529) and n < 3:
                time.sleep(2 ** n)
                continue
            return e.code, {'error': body}, time.monotonic() - t
        except (urllib.error.URLError, TimeoutError) as e:
            return 0, {'error': str(e).replace(key, '***')[:300]}, time.monotonic() - t


def asset_payload(it, order):
    state = {'issuer': it['issuer'], 'token': it['token'], 'line_name': it['line_name']}
    if it['table_section']: state['table_section'] = it['table_section']
    return {'model': MODEL, 'state': state, 'questions': {'asset_kind': {
        'type': 'choice', 'instructions': ASSET_Q, 'criteria': {k: KIND_TEXT[k] for k in order}}}}


def report_payload(it):
    qs = {}
    for q in it['questions']:
        if q['rule'] == 'R08':
            qs['R08'] = {'type': 'choice', 'instructions': R08_Q, 'criteria': R08_TEXT}
        else:
            ins, crit = NOUL[q['rule']]
            qs[q['rule']] = {'type': 'noul', 'instructions': ins, 'criteria': crit}
    state = {'report': f"{it['issuer']} {it['token']} reserve report as of {it['as_of']}", 'text': it['text']}
    return {'model': MODEL, 'state': state, 'questions': qs}


def plan(gold):
    """(요청 번호, 종류, 문항, payload) 목록. 자산 줄은 선택지 순서를 바꿔 두 번 묻는다(문서의 순서 쏠림 확인 방법)."""
    out = []
    for it in gold['asset_items']:
        out.append((it['id'], 'asset', it, asset_payload(it, KINDS)))
    for it in gold['report_items']:
        out.append((it['id'], 'report', it, report_payload(it)))
    for it in gold['asset_items']:
        out.append((it['id'] + 'r', 'asset_rev', it, asset_payload(it, KINDS[::-1])))
    return out


def run(limit=None):
    gold = json.loads((OUT / 'goldset.json').read_text(encoding='utf-8'))
    old = json.loads((OUT / 'results.json').read_text(encoding='utf-8')) if (OUT / 'results.json').exists() else {}
    spend = old.get('meta', {}).get('spend_log', [])
    key = load_key()
    st, models, _ = request(key, 'GET', '/models')
    meta = {'date': datetime.date.today().isoformat(), 'endpoint': API + '/systemone', 'model_requested': MODEL,
            'usd_per_million_input_tokens': 0.042, 'models_status': st,
            'models_listed': [m.get('name') for m in models.get('models', [])] if st == 200 else None,
            'questions': {'asset': {'instructions': ASSET_Q, 'criteria': KIND_TEXT},
                          'R08': {'instructions': R08_Q, 'criteria': R08_TEXT},
                          **{k: {'instructions': v[0], 'criteria': v[1]} for k, v in NOUL.items()}}}
    calls, cost = [], 0.0
    if st == 200:
        for rid, kind, it, payload in plan(gold)[:limit]:
            if cost >= BUDGET_USD: break
            code, resp, sec = request(key, 'POST', '/systemone', payload)
            u = resp.get('usage', {}) if code == 200 else {}
            cost += u.get('input_tokens', 0) * USD_PER_TOKEN
            calls.append({'req': rid, 'kind': kind, 'status': code, 'seconds': round(sec, 3), 'model': resp.get('model'),
                          'usage': u, 'response': resp})
            print(rid, kind, code, u, f'{sec:.2f}s', flush=True)
            if code != 200 and code not in (422,): break  # 키, 권한, 서버 문제면 더 부르지 않는다
    tok_in = sum(c['usage'].get('input_tokens', 0) for c in calls)
    spend.append({'at': datetime.datetime.now().isoformat(timespec='seconds'), 'limit': limit, 'calls': len(calls),
                  'input_tokens': tok_in, 'output_tokens': sum(c['usage'].get('output_tokens', 0) for c in calls),
                  'usd': round(tok_in * USD_PER_TOKEN, 6)})
    meta['spend_log'] = spend
    res = {'meta': meta, 'items': score(gold, calls), 'calls': calls}
    (OUT / 'results.json').write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    write_summary(res, gold)


# ---- 채점과 요약 ----

def score(gold, calls):
    by = {(c['req'], c['kind']): c for c in calls if c['status'] == 200}
    items = []
    for it in gold['asset_items']:
        c, cr = by.get((it['id'], 'asset')), by.get((it['id'] + 'r', 'asset_rev'))
        if not c: continue
        a = c['response']['answers']['asset_kind']
        row = {'id': it['id'], 'task': 'asset', 'token': it['token'], 'month': it['month'], 'input': it['line_name'],
               'gold': it['gold'], 'answer': a['choice'], 'correct': a['choice'] == it['gold'],
               'confidence': a['confidence'], 'p_gold': a['probabilities'].get(it['gold'])}
        if cr:
            b = cr['response']['answers']['asset_kind']
            row.update(answer_reversed=b['choice'], confidence_reversed=b['confidence'])
        items.append(row)
    for it in gold['report_items']:
        c = by.get((it['id'], 'report'))
        if not c: continue
        for q in it['questions']:
            a = c['response']['answers'][q['rule']]
            row = {'id': f"{it['id']}-{q['rule']}", 'task': q['rule'], 'token': it['token'], 'month': it['month'],
                   'input': it['source_pdf'], 'gold': q['gold']}
            if a['type'] == 'noul':
                row.update(answer=a['noul'] >= 0.5, noul=a['noul'], confidence=round(abs(2 * a['noul'] - 1), 4))
            else:
                row.update(answer=a['choice'], confidence=a['confidence'], p_gold=a['probabilities'].get(q['gold']))
            row['correct'] = row['answer'] == q['gold']
            items.append(row)
    return items


def pct(a, b):
    return f'{a}/{b} ({100 * a / b:.0f}%)' if b else '0/0'


def show(v):
    return '예' if v is True else '아니오' if v is False else str(v)


def write_summary(res, gold):
    meta, items, calls = res['meta'], res['items'], res['calls']
    n_checked = sum(x['test_check'] == 'ASSET_TYPES' for x in gold['asset_items'])
    L = ['# Jev 글 항목 고르기 시험', '',
         f"- 날짜 {meta['date']}, 모델 {MODEL}(TypeSafe), 주소 {meta['endpoint']}",
         f"- 정답 세트: goldset.json(자산 줄 {len(gold['asset_items'])}개, 보고서 {len(gold['report_items'])}건). 원응답과 채점: results.json",
         '- 코인별 자산 줄: ' + ', '.join(f"{t} {sum(x['token'] == t for x in gold['asset_items'])}" for t in TOKENS)
         + '. 코인별 보고서: ' + ', '.join(f"{t} {sum(x['token'] == t for x in gold['report_items'])}" for t in TOKENS) + '.',
         f"- 자산 종류 정답은 파서 분류(holdings[].kind)다. {len(gold['asset_items'])}줄 가운데 {n_checked}줄은 그 달 자산 종류 목록 시험"
         '(tests/test_rule_inputs.py ASSET_TYPES)이 확인하고, 나머지(정산 줄, 펀드 안 줄)는 파서 분류만 있다.',
         '- R08, R11, R12, R15 정답은 시험이 확인하는 값이다(goldset.json gold_source). 입력은 보고서 전체 pdftotext 글이다.', '']
    api = ['', '## API', '',
           '- POST /v1/systemone, 머리글 Authorization: Bearer 키. 본문은 state(글 또는 JSON), model, questions(choice, noul, score). '
           '응답은 answers(choice는 choice, probabilities, confidence, noul은 noul 하나)와 usage(input_tokens, output_tokens).',
           '- 요금은 입력 토큰에만 붙는다(100만 토큰당 0.042달러, 출력 무료). 입력은 글만 받는다(이미지, 소리, 영상 없음). '
           '한 요청 64k 토큰, state와 가장 긴 질문 합 32k 토큰. 출처 docs.typesafe.ai/api, docs.typesafe.ai/models.',
           f"- GET /v1/models 상태 {meta['models_status']}, 목록 {', '.join(meta['models_listed'] or [])}. "
           f'요청 model은 {MODEL}로 고정했다(별칭 jev-latest는 새 판이 나오면 바뀐다).']
    if meta['models_status'] != 200 or any(c['status'] != 200 for c in calls):
        bad = [c for c in calls if c['status'] != 200]
        L += ['## 호출 오류', '', f"- GET /v1/models 상태 {meta['models_status']}"]
        L += [f"- {c['req']} 상태 {c['status']}: {json.dumps(c['response'], ensure_ascii=False)[:300]}" for c in bad[:5]]
        L += ['- 문서(docs.typesafe.ai/api Errors): 401 키 없음 또는 틀림, 422 요청 형식 오류, 429 속도 한도, 529 서버 과부하.', '']
    if items:
        L += ['## 항목별 정확도', '',
              f'Noul(예/아니오) 확신값은 문서 Confidence 쪽의 식 |2p-1|로 셈했다. 확신 {GATE} 이상은 p가 0.9 이상이거나 0.1 이하인 경우다.', '',
              f'| 항목 | 맞은 수/전체 | 확신 {GATE} 이상 남는 비율 | 확신 {GATE} 이상 정확도 |', '|---|---|---|---|']
        for t in TASK_NAME:
            xs = [x for x in items if x['task'] == t]
            if not xs: continue
            hi = [x for x in xs if x['confidence'] >= GATE]
            L.append(f"| {TASK_NAME[t]} | {pct(sum(x['correct'] for x in xs), len(xs))} | {pct(len(hi), len(xs))} | "
                     f"{pct(sum(x['correct'] for x in hi), len(hi))} |")
        L += ['', '## 확신값 분포', '', '칸 값: 건수(그 가운데 맞은 수)', '',
              '| 항목 | 0.5 미만 | 0.5 이상 0.8 미만 | 0.8 이상 0.95 미만 | 0.95 이상 |', '|---|---|---|---|---|']
        bins = ((0, .5), (.5, .8), (.8, .95), (.95, 1.01))
        for t in TASK_NAME:
            xs = [x for x in items if x['task'] == t]
            if not xs: continue
            cells = []
            for lo, hi in bins:
                b = [x for x in xs if lo <= x['confidence'] < hi]
                cells.append(f"{len(b)}({sum(x['correct'] for x in b)})")
            L.append(f"| {TASK_NAME[t]} | " + ' | '.join(cells) + ' |')
        golds = {t: sorted({show(x['gold']) for x in items if x['task'] == t}) for t in ('R08', 'R11', 'R12', 'R15')}
        L += ['', '정답 값 구성: ' + ', '.join(
            f"{t} " + ', '.join(f"{g} {sum(show(x['gold']) == g for x in items if x['task'] == t)}" for g in golds[t])
            for t in golds if golds[t])]
        wrong = [x for x in items if not x['correct']]
        L += ['', '## 틀린 사례', '']
        if wrong:
            L += ['| 번호 | 항목 | 코인, 달 | 입력 | 정답 | Jev 답 | 확신값 | 까닭 |', '|---|---|---|---|---|---|---|---|']
            for x in wrong:
                extra = f" (p={x['noul']:.2f})" if 'noul' in x else f" (정답 확률 {x.get('p_gold') or 0:.2f})"
                L.append(f"| {x['id']} | {TASK_NAME[x['task']]} | {x['token']} {x['month']} | {x['input']} | {show(x['gold'])} | "
                         f"{show(x['answer'])}{extra} | {x['confidence']:.2f} | {REVIEW.get(x['id'], '')} |")
            sure = [x for x in wrong if x['confidence'] >= GATE]
            if sure:
                L += ['', f"확신 {GATE} 이상인데 틀린 문항: " + ', '.join(f"{x['id']}({x['confidence']:.2f})" for x in sure) + '.']
        else:
            L.append('없음')
        rev = [x for x in items if 'answer_reversed' in x]
        if rev:
            diff = [x for x in rev if x['answer_reversed'] != x['answer']]
            L += ['', '## 선택지 순서', '',
                  f"자산 종류 질문을 선택지 순서만 거꾸로 해 한 번 더 물었다(문서 'Choice option order' 확인 방법). "
                  f"같은 답 {pct(len(rev) - len(diff), len(rev))}. 거꾸로 한 순서의 정확도 "
                  f"{pct(sum(x['answer_reversed'] == x['gold'] for x in rev), len(rev))}."]
            L += [f"- {x['id']} {x['token']} '{x['input']}': 원래 순서 {x['answer']}({x['confidence']:.2f}), "
                  f"거꾸로 {x['answer_reversed']}({x['confidence_reversed']:.2f}), 정답 {x['gold']}" for x in diff]
    ok = [c for c in calls if c['status'] == 200]
    tok_in = sum(c['usage'].get('input_tokens', 0) for c in ok)
    tok_out = sum(c['usage'].get('output_tokens', 0) for c in ok)
    total = sum(s['usd'] for s in meta['spend_log'])
    L += ['', '## 비용과 속도', '',
          f"- 이번 실행: 요청 {len(calls)}건, 입력 {tok_in:,}토큰, 출력 {tok_out:,}토큰(무료). 입력 100만 토큰당 0.042달러로 {tok_in * USD_PER_TOKEN:.4f}달러.",
          f"- 이 시험 전체(형식 확인 호출 포함 {len(meta['spend_log'])}회 실행): {sum(s['input_tokens'] for s in meta['spend_log']):,}토큰, {total:.4f}달러. 충전액 5달러.",
          '- 금액은 응답 usage.input_tokens와 문서 요금으로 셈한 값이다. 콘솔 청구 화면과 맞춰 보지는 않았다.']
    if ok:
        L.append(f"- 요청 1건 응답 시간 가운데값 {statistics.median(c['seconds'] for c in ok):.2f}초(네트워크 포함, 순차 호출).")
        L.append(f"- 응답 모델 이름: {', '.join(sorted({c['model'] for c in ok if c['model']}))}")
    L += api
    L += ['', '## 정답 세트에서 뺀 것', '']
    L += [f'- {k}: {v}' for k, v in gold['rules']['excluded'].items()]
    L.append('- R08, R11, R12 예 정답의 근거가 글자 층이 없는 쪽(파서가 OCR로 읽은 쪽)에 있는 달은 고르지 않았다(USDG 다수 달, GUSD 2024-10, 2026-03).')
    drop = [f"{x['token']} {x['month']}" for x in gold['report_items'] if 'R15' in x['dropped']]
    if drop: L.append(f"- R15는 서명 블록이 그림 쪽에만 있는 보고서에서 문항을 뺐다: {', '.join(drop)}.")
    L += ['', '## 읽을 때 주의', '',
          '- R15 정답은 레포 264건 모두 예라서, 아니오 사례가 없다. R15 정확도는 예를 알아보는 비율만 보여 준다.',
          '- 같은 발행사, 같은 시기 보고서는 서식과 문장이 거의 같다. 문항 수보다 서로 다른 서식 수가 적다.',
          '- 자산 종류 입력은 줄 이름과 발행사, 코인 이름(Circle은 표 구역 이름도)이다. 각주나 만기 표는 넣지 않았다.']
    (OUT / 'summary.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'gold':
        build_gold()
    elif cmd == 'run':
        run(int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == '--limit' else None)
    elif cmd == 'report':
        write_summary(json.loads((OUT / 'results.json').read_text(encoding='utf-8')),
                      json.loads((OUT / 'goldset.json').read_text(encoding='utf-8')))
    else:
        sys.exit(__doc__)
