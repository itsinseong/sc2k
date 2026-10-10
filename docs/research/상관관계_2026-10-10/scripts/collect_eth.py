"""이더리움 발행, 소각 원자료 수집. 사용: python3 -I collect_eth.py <코인|all> [check|logs|inflow|daily]"""
import json, gzip, time, sys, os, urllib.request, csv, collections, datetime as dt
from Crypto.Hash import keccak
ROOT = '/Users/inseong/dev/git_inseong/sc2k'
OUT = ROOT + '/docs/research/상관관계_2026-10-10'
RAW = OUT + '/eth_raw'; RES = OUT + '/eth_out'
DL = ROOT + '/docs/research/Claude웹_1차/data/raw'
KEY = [l.split('=', 1)[1].strip().strip('"\'') for l in open(ROOT + '/.env.local') if l.startswith('ETHERSCAN_API_KEY')][0]
ZERO = '0x' + '0' * 64
TR = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
def kc(s): return '0x' + keccak.new(digest_bits=256, data=s.encode()).hexdigest()
COINS = {
 'USDC': ('0xA0b86991c6218b36c1d19D4a2e9eb0cE3606eB48', '2023-03-01', '2023-03-31', 6),
 'USDT': ('0xdAC17F958D2ee523a2206206994597C13D831ec7', '2022-05-01', '2022-05-31', 6),
 'PYUSD': ('0x6c3ea9036406852006290770BEdFcAbA0e23A0e8', '2024-02-13', '2024-03-19', 6),
 'USDP': ('0x8E870D67F660D95d5be530380D0eC0bd388289E1', '2024-01-26', '2024-03-01', 18),
}
last = [0.0]; ncalls = [0]
def api(**p):
    p['chainid'] = 1; p['apikey'] = KEY
    u = 'https://api.etherscan.io/v2/api?' + '&'.join(f'{a}={b}' for a, b in p.items())
    for t in range(6):
        w = 0.4 - (time.time() - last[0])
        if w > 0: time.sleep(w)
        last[0] = time.time(); ncalls[0] += 1
        try:
            r = json.load(urllib.request.urlopen(u, timeout=90))
        except Exception as e:
            r = {'status': '0', 'message': 'EXC', 'result': str(e).replace(KEY, '***')}
        if isinstance(r.get('result'), str) and ('rate limit' in r['result'].lower()):
            time.sleep(2); continue
        if r.get('message') == 'EXC': time.sleep(2); continue
        return r
    return r
def ts(d): return int(dt.datetime.strptime(d, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp())
def blk(t, closest):
    return int(api(module='block', action='getblocknobytime', timestamp=t, closest=closest)['result'])
def window(c):
    a, s, e, _ = COINS[c]
    return ts(s) - 14 * 86400, ts(e) + 86400 + 14 * 86400 - 1
def getlogs(addr, lo, hi, t0, t1=None, t2=None, out=None, depth=0):
    p = dict(module='logs', action='getLogs', address=addr, fromBlock=lo, toBlock=hi, topic0=t0, page=1, offset=1000)
    if t1: p['topic1'] = t1; p['topic0_1_opr'] = 'and'
    if t2:
        p['topic2'] = t2; p['topic0_2_opr'] = 'and'
        if t1: p['topic1_2_opr'] = 'and'
    r = api(**p)
    res = r.get('result')
    if isinstance(res, str):
        if 'No records' in res: return out
        raise RuntimeError(f'getLogs {lo}-{hi}: {res}')
    if len(res) >= 1000 and hi > lo:
        m = (lo + hi) // 2
        getlogs(addr, lo, m, t0, t1, t2, out, depth + 1); getlogs(addr, m + 1, hi, t0, t1, t2, out, depth + 1)
    else:
        out.extend(res)
    return out
def save(name, obj):
    with gzip.open(f'{RAW}/{name}.json.gz', 'wt') as f: json.dump(obj, f)
def load(name): return json.load(gzip.open(f'{RAW}/{name}.json.gz', 'rt'))
def ethcall(addr, data, tag='latest'):
    return api(module='proxy', action='eth_call', to=addr, data=data, tag=tag).get('result')

def check(c):
    addr = COINS[c][0]
    src = api(module='contract', action='getsourcecode', address=addr)['result'][0]
    info = {'address': addr, 'ContractName': src.get('ContractName'), 'Proxy': src.get('Proxy'), 'Implementation': src.get('Implementation'),
            'name_hex': ethcall(addr, '0x06fdde03'), 'symbol_hex': ethcall(addr, '0x95d89b41'), 'decimals_hex': ethcall(addr, '0x313ce567')}
    for k in ('name_hex', 'symbol_hex'):
        h = info[k]
        try: info[k.split('_')[0]] = bytes.fromhex(h[2:]).decode('utf8', 'ignore').strip('\x00 \x20 ').strip()
        except Exception: pass
    info['decimals'] = int(info['decimals_hex'], 16)
    if c == 'USDT':
        abi = json.loads(src['ABI'])
        info['events'] = [e['name'] for e in abi if e.get('type') == 'event']
        info['issue_topic'] = kc('Issue(uint256)'); info['redeem_topic'] = kc('Redeem(uint256)')
        info['owner_hex_latest'] = ethcall(addr, '0x8da5cb5b')
    save(f'{c}_check', info); print(c, {k: v for k, v in info.items() if k not in ('name_hex', 'symbol_hex')})

def logs(c):
    addr = COINS[c][0]; a, b = window(c)
    lo, hi = blk(a, 'after'), blk(b, 'before')
    d = {'window_utc': [a, b], 'blocks': [lo, hi]}
    d['mint'] = getlogs(addr, lo, hi, TR, t1=ZERO, out=[])
    d['burn'] = getlogs(addr, lo, hi, TR, t2=ZERO, out=[])
    if c == 'USDT':
        d['issue'] = getlogs(addr, lo, hi, kc('Issue(uint256)'), out=[])
        d['redeem'] = getlogs(addr, lo, hi, kc('Redeem(uint256)'), out=[])
    save(f'{c}_mintburn_logs', d)
    print(c, 'blocks', lo, hi, {k: len(v) for k, v in d.items() if isinstance(v, list)}, 'calls', ncalls[0])

def inflow(c, topn=5):
    """소각 주소로 들어온 Transfer. PYUSD, USDP는 전부, USDC, USDT는 소각 금액 상위 topn개 주소."""
    addr = COINS[c][0]; dec = COINS[c][3]; d = load(f'{c}_mintburn_logs'); lo, hi = d['blocks']
    amt = collections.Counter(); cnt = collections.Counter()
    for l in d['burn']:
        f = '0x' + l['topics'][1][-40:]; amt[f] += int(l['data'], 16); cnt[f] += 1
    rows = amt.most_common()
    if c == 'USDT':  # Redeem는 소유자 주소 잔액에서 소각된다
        o = ethcall(addr, '0x8da5cb5b', hex(lo)); o2 = ethcall(addr, '0x8da5cb5b', hex(hi))
        rows = [('0x' + o[-40:], 0)] + ([('0x' + o2[-40:], 0)] if o2 != o else [])
    elif c in ('USDC',): rows = rows[:topn]
    sel = {'rule': '전부' if c in ('PYUSD', 'USDP') else ('소각 금액 상위 %d개 주소' % topn if c == 'USDC' else 'owner() 주소'),
           'burn_addrs': [{'addr': a, 'burn_events': cnt[a], 'burn_amount': amt[a] / 10 ** dec} for a, _ in rows], 'inflows': {}}
    for a, _ in rows:
        sel['inflows'][a] = getlogs(addr, lo, hi, TR, t2='0x' + '0' * 24 + a[2:], out=[])
        print(c, a, 'inflow', len(sel['inflows'][a]))
    save(f'{c}_burn_addr_inflow', sel)

def daily(c):
    dec = COINS[c][3]; d = load(f'{c}_mintburn_logs')
    day = lambda l: dt.datetime.fromtimestamp(int(l['timeStamp'], 16), dt.timezone.utc).strftime('%Y-%m-%d')
    m = collections.defaultdict(int); b = collections.defaultdict(int); mn = collections.Counter(); bn = collections.Counter()
    for l in d['mint']: m[day(l)] += int(l['data'], 16); mn[day(l)] += 1
    for l in d['burn']: b[day(l)] += int(l['data'], 16); bn[day(l)] += 1
    extra = {}
    if c == 'USDT':
        for nm, k in (('issue', 'Issue'), ('redeem', 'Redeem')):
            x = collections.defaultdict(int); n = collections.Counter()
            for l in d[nm]: x[day(l)] += int(l['data'], 16); n[day(l)] += 1
            extra[nm] = (x, n)
    a, e = d['window_utc']; days = []
    t = a
    while t <= e: days.append(dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%d')); t += 86400
    with open(f'{RES}/{c}_eth_daily.csv', 'w', newline='') as f:
        w = csv.writer(f); hdr = ['date_utc', 'mint', 'burn', 'net', 'mint_n', 'burn_n']
        if extra: hdr += ['issue', 'redeem', 'issue_n', 'redeem_n', 'net_issue_redeem']
        w.writerow(hdr)
        for x in days:
            r = [x, m[x] / 10 ** dec, b[x] / 10 ** dec, (m[x] - b[x]) / 10 ** dec, mn[x], bn[x]]
            if extra:
                i, rd = extra['issue'], extra['redeem']
                r += [i[0][x] / 10 ** dec, rd[0][x] / 10 ** dec, i[1][x], rd[1][x], (i[0][x] - rd[0][x]) / 10 ** dec]
            w.writerow(r)
    # DefiLlama 이더리움 체인 잔액
    dl = json.load(gzip.open(f'{DL}/defillama_{ {"USDC":"USDC_2","USDT":"USDT_1","PYUSD":"PYUSD_120","USDP":"USDP_11"}[c] }.json.gz'))
    eth = dl['chainBalances'].get('Ethereum', {}).get('tokens', [])
    with open(f'{RES}/{c}_defillama_ethereum.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['date_utc', 'circulating_usd', 'minted_usd', 'unreleased_usd'])
        for r in eth:
            x = dt.datetime.fromtimestamp(r['date'], dt.timezone.utc).strftime('%Y-%m-%d')
            if days[0] <= x <= days[-1]:
                g = lambda k: (r.get(k) or {}).get('peggedUSD', '')
                w.writerow([x, g('circulating'), g('minted'), g('unreleased')])
    print(c, 'daily ok', len(days), 'days; defillama eth rows total', len(eth))

if __name__ == '__main__':
    cs = list(COINS) if sys.argv[1] == 'all' else [sys.argv[1]]
    for c in cs:
        for s in (sys.argv[2:] or ['check', 'logs', 'inflow', 'daily']): globals()[s](c)
