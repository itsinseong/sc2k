"""발행사 이용약관 원문 받기(R14 이자 지급 문항용).

  python3 -I scripts/jev/fetch_terms.py RAW_DIR   받아서 쓰기
  python3 -I scripts/jev/fetch_terms.py check     글 뽑기 확인만

주소마다 curl(-L, 브라우저 User-Agent)로 HTML을 RAW_DIR에 받고, 글자만 뽑아 docs/research/약관_2026-10-09/<id>.txt 로 쓴다.
BROWSER의 문서는 curl이 막혀(403) Aside 브라우저 repl에서 openTab 뒤 page.content()로 RAW_DIR/<id>.html 에 미리 저장해 둔 것을 쓴다.
파일 머리에 주소, 받은 날짜, 문서 제목, 개정일을 적는다. 단어와 문장은 바꾸지 않는다: script, style 같은 태그 안의 글은 버리고,
블록 태그(p, li, h1 등) 경계에 줄 바꿈을 넣고, 빈칸과 빈 줄만 정리한다. 받은 결과(못 받은 문서 포함)는 같은 폴더 sources.json 에 적는다.
"""
import datetime, hashlib, json, pathlib, re, subprocess, sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs' / 'research' / '약관_2026-10-09'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
# (파일 이름, 문서를 낸 회사, 코인, 주소, 무엇). 주소는 E-3, E-5 원문 대조(2026-10-09)에서 확인한 것을 먼저 썼다
DOCS = [
    ('circle_usdc_terms', 'Circle', 'USDC', 'https://www.circle.com/legal/usdc-terms', 'USDC 이용약관(EEA 밖 보유자)'),
    ('circle_eurc_terms', 'Circle', 'EURC', 'https://www.circle.com/legal/eurc-terms', 'EURC 이용약관'),
    ('circle_eea_terms', 'Circle France', 'USDC, EURC', 'https://www.circle.com/legal/eea-terms', 'Circle France 약관(EEA 보유자)'),
    ('paxos_stablecoin_terms', 'Paxos', 'USDP, PYUSD, USDG', 'https://www.paxos.com/terms-and-conditions/stablecoin-terms-conditions',
     'Paxos USD 스테이블코인 약관'),
    ('paxos_usdg_eu_whitepaper', 'Paxos', 'USDG', 'https://www.paxos.com/terms-and-conditions/usdg-eu-whitepaper', 'USDG EU 백서(MiCA)'),
    ('paypal_crypto_terms', 'PayPal', 'PYUSD', 'https://www.paypal.com/us/legalhub/paypal/cryptocurrencies-tnc',
     'PayPal 암호자산 약관(PYUSD 보상 프로그램 절 포함, 유통사)'),
    ('gemini_trust_user_agreement', 'Gemini', 'GUSD', 'https://www.gemini.com/legal/gemini-trust-user-agreement',
     'Gemini Trust 이용약관(Gemini Dollar 절 포함)'),
    ('ripple_rlusd_terms', 'Ripple', 'RLUSD', 'https://ripple.com/legal/stablecoin/', 'RLUSD 이용약관'),
    ('tether_terms', 'Tether', 'USDT', 'https://tether.to/en/legal/', 'Tether 약관 현행판'),
    ('coinbase_user_agreement', 'Coinbase', 'USDC', 'https://www.coinbase.com/legal/user_agreement/united_states',
     'Coinbase 이용약관(USDC 보상 절, 거래소)'),
]
NOTE = ['WebFetch는 모델이 손본 글을 돌려줘 원문을 그대로 저장할 수 없어 curl로 HTML을 받았다.',
        'Coinbase는 발행사가 아니지만 거래소가 주는 보상(USDC Rewards) 조항 문항을 위해 받았다.',
        'Tether 위험 고지문(Risk Disclosure Statement, 2025-01-27, 약관에 포함된 문서)은 같은 주소의 다른 탭이라 받은 HTML 본문에 없다. '
        '따로 저장하지 않았다.',
        'text_file 줄 번호는 머리 6줄(주소, 받은 날짜, 문서 제목, 개정일, 받은 방법, 구분선)을 포함한다.']
BROWSER = {'coinbase_user_agreement'}
CURL_HOW = 'curl(-L, 브라우저 User-Agent)로 받은 HTML'
BROWSER_HOW = 'curl이 403이라 Aside 브라우저 repl(openTab 뒤 page.content())로 받은 HTML'
SKIP = {'script', 'style', 'noscript', 'svg', 'template', 'iframe', 'title'}
BLOCK = {'p', 'br', 'div', 'li', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tr', 'td', 'th', 'table', 'thead', 'tbody',
         'section', 'article', 'header', 'footer', 'nav', 'main', 'aside', 'blockquote', 'pre', 'dt', 'dd', 'dl', 'hr',
         'figure', 'figcaption', 'details', 'summary', 'button', 'form'}
MONTH = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
DATE_RE = re.compile(r'(?:Last\s+(?:[Uu]pdated|[Mm]odified|[Rr]evised)(?:\s+on)?|Effective(?:\s+[Dd]ate)?(?:\s+as\s+of)?|'
                     r'Gemini Trust User Agreement)\s*:?\s*' + MONTH + r'\s+\d{1,2},\s+\d{4}')


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.skip, self.title, self.h1, self._t = [], 0, [], [], None

    def handle_starttag(self, tag, attrs):
        if tag == 'title' and not self.title: self._t = self.title  # svg 아이콘 안 title은 뺀다
        elif tag == 'h1' and not self.h1: self._t = self.h1
        if tag in SKIP: self.skip += 1
        elif tag in BLOCK: self.out.append('\n')

    def handle_endtag(self, tag):
        if tag in ('title', 'h1'): self._t = None
        if tag in SKIP: self.skip = max(0, self.skip - 1)
        elif tag in BLOCK: self.out.append('\n')

    def handle_data(self, data):
        if self._t is not None: self._t.append(data)
        if not self.skip: self.out.append(re.sub(r'\s+', ' ', data))


def to_text(html):
    p = Text()
    p.feed(html)
    lines = [ln.strip() for ln in ''.join(p.out).split('\n')]
    one = lambda xs: re.sub(r'\s+', ' ', ''.join(xs)).strip()
    return '\n'.join(ln for ln in lines if ln), one(p.title), one(p.h1)


def fetch(doc_id, url, raw_dir):
    raw = raw_dir / f'{doc_id}.html'
    r = subprocess.run(['curl', '-sSL', '--compressed', '--max-time', '60', '-A', UA, '-H', 'Accept-Language: en-US,en;q=0.9',
                        '-o', str(raw), '-w', '%{http_code} %{url_effective}', url], capture_output=True, text=True)
    code, _, final = r.stdout.partition(' ')
    return raw, int(code or 0), final, r.stderr.strip()[:300]


def main(raw_dir):
    raw_dir = pathlib.Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for doc_id, company, coins, url, what in DOCS:
        if doc_id in BROWSER:
            raw, final, err = raw_dir / f'{doc_id}.html', url, ''
            code = 200 if raw.exists() else 0
            if not code: err = 'Aside로 받은 HTML이 RAW_DIR에 없다(curl은 403)'
            now = datetime.datetime.fromtimestamp(raw.stat().st_mtime).astimezone() if raw.exists() else None
        else:
            for _ in range(3):  # PayPal은 가끔 본문 없는 껍데기를 준다. 그러면 다시 받는다
                now = datetime.datetime.now().astimezone()
                raw, code, final, err = fetch(doc_id, url, raw_dir)
                if code != 200 or len(to_text(raw.read_text(encoding='utf-8', errors='replace'))[0]) > 5000: break
        row = {'id': doc_id, 'company': company, 'coins': coins, 'what': what, 'url': url, 'final_url': final or None,
               'http_status': None if doc_id in BROWSER else code, 'how': BROWSER_HOW if doc_id in BROWSER else CURL_HOW,
               'fetched_at': now.isoformat(timespec='seconds') if now else None}
        body = raw.read_bytes() if raw.exists() else b''
        text, title, h1 = to_text(body.decode('utf-8', errors='replace')) if body else ('', '', '')
        dates = list(dict.fromkeys(re.sub(r'\s+', ' ', m[0]) for m in DATE_RE.finditer(text)))
        # 본문이 짧으면(봇 차단 쪽, 빈 껍데기) 받지 못한 것으로 둔다
        ok = code == 200 and len(text) > 5000
        row.update(raw_bytes=len(body), raw_sha256=hashlib.sha256(body).hexdigest() if body else None,
                   title=title or None, h1=h1 or None, revision=dates or None, text_chars=len(text))
        if ok:
            head = [f'주소: {url}' + (f' (최종 주소 {final})' if final and final != url else ''),
                    f'받은 날짜: {now.date().isoformat()}',
                    f'문서 제목: {title or h1}' + (f' (본문 첫 제목 {h1})' if h1 and title and title != h1 else ''),
                    '개정일: ' + ('; '.join(dates) if dates else '원문에 표기 없음'),
                    f"받은 방법: {row['how']}에서 글자만 뽑음. 단어와 문장은 바꾸지 않았고 "
                    '블록 태그 경계 줄 바꿈과 빈칸만 정리함. scripts/jev/fetch_terms.py',
                    '=' * 40]
            (OUT / f'{doc_id}.txt').write_text('\n'.join(head) + '\n' + text + '\n', encoding='utf-8')
            row.update(text_file=f'docs/research/약관_2026-10-09/{doc_id}.txt', header_lines=len(head), result='받음')
        else:
            row.update(text_file=None, result='못 받음', reason=err or f'상태 {code}, 본문 글자 {len(text)}자')
        rows.append(row)
        print(doc_id, code, len(body), len(text), row['result'], dates[:3], flush=True)
    (OUT / 'sources.json').write_text(json.dumps({'made': datetime.date.today().isoformat(), 'note': NOTE, 'docs': rows},
                                                 ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def check():
    """python3 -I scripts/jev/fetch_terms.py check : 글 뽑기 확인(받기 없음)"""
    html = ('<html><head><title>Doc</title><style>p{}</style></head><body><nav>Menu</nav><h1>Terms</h1>'
            '<p>One <b>two</b>\n three.</p><p>four</p><script>var x=1</script><svg><title>icon</title></svg></body></html>')
    assert to_text(html) == ('Menu\nTerms\nOne two three.\nfour', 'Doc', 'Terms'), to_text(html)
    print('ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['check']: check()
    elif len(sys.argv) == 2: main(sys.argv[1])
    else: sys.exit(__doc__)
