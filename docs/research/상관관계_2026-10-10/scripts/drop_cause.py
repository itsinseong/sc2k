"""PYUSD, USDP 최악 7일 감소 구간의 상환이 소수 주소에 몰렸는지 본다.
사용: python3 -I drop_cause.py fetch   추가 원자료를 받아 eth_raw/drop_cause_extra.json.gz 에 저장
      python3 -I drop_cause.py         표를 출력하고 eth_out/drop_cause_output.txt 에 저장
입력: collect_eth.py 가 받은 eth_raw/<코인>_mintburn_logs.json.gz, eth_raw/<코인>_burn_addr_inflow.json.gz
"""
import sys, os, json, gzip, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import collect_eth as ce  # api, getlogs, blk, ts, ethcall, kc, load, COINS 재사용. 키는 출력하지 않는다.

TRE = '0xe25a329d385f77df5d4ed56265babe2b99a5436e'  # 발행분을 받고 소각하는 주소(두 코인 공통)
P4 = '0x264bd8291fae1d75db2c5f573b07faa6715997b5'
PSM_JOIN = '0x7bbd8ca5e413bca521c2c80d8d1908616894cf21'
H657 = '0x65729807485f6f7695af863d97d62140b7d69d83'
CHAINLOG = '0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F'  # Sky(옛 MakerDAO) 주소 목록 컨트랙트
EXTRA = ce.RAW + '/drop_cause_extra.json.gz'
OUTTXT = ce.RES + '/drop_cause_output.txt'
# 구조 문서의 최악 7일 창. DefiLlama 날짜 값은 그날 00:00 UTC 시점 값이라 체인 기록은 [시작일 00:00, 종료일 00:00) UTC 로 자른다.
WIN = {'PYUSD': ('2024-02-27', '2024-03-05'), 'USDP': ('2024-02-09', '2024-02-16')}
# Claude웹_1차/data/compute_output.txt 2-A 7일 행: 시작 유통량, 종료 유통량, unreleased 변화(없으면 None)
DL = {'PYUSD': (281987555, 188447295, 15570882), 'USDP': (352851006, 215345761, None)}
# 토큰 이동 기록을 받을 주소. all = 처음부터 창 끝까지, win = 창 시작 약 하루 전(7200블록)부터 창 끝까지
HIST = {
    'PYUSD': {'0x149463398d8ecc45eef14765fbe0951ee358401c': 'all', '0xbabb07bbe931c4d7d1c9886396c566b9955c7340': 'all',
              '0x4f4f1c4118b2cc4fdb692b3073321c591ed1ae89': 'win', '0xcffad3200574698b78f32232aa9d63eabd290703': 'all'},
    'USDP': {'0x609b811d91ed19a57fe8494f952a2518c7635485': 'all', '0xa4e45f6fbaafa266b86591e46d39989a961ad9e2': 'all',
             '0x3691a5e752dac1788e2d393309930cc7128fdbd6': 'all', '0x4f4f1c4118b2cc4fdb692b3073321c591ed1ae89': 'win',
             '0x33566c9d8be6cf0b23795e0d380e112be9d75836': 'win', H657: 'all'},
}
FUND = ['0x149463398d8ecc45eef14765fbe0951ee358401c', '0xbabb07bbe931c4d7d1c9886396c566b9955c7340',
        '0x4f4f1c4118b2cc4fdb692b3073321c591ed1ae89', '0x609b811d91ed19a57fe8494f952a2518c7635485',
        '0xa4e45f6fbaafa266b86591e46d39989a961ad9e2', '0x3691a5e752dac1788e2d393309930cc7128fdbd6',
        '0x7707d9eaf2d7ba2343fe7504d687596f9cc618c7', '0xd14dafc47cbbb3065032452ba95879bf4e858ed8', H657]
# Etherscan 공개 이름표(https://etherscan.io/address/<주소>, 2026-10-10 조회). TAG = 이름표 있음, NOTAG = 페이지에 이름표 없음,
# 둘 다 아니면 조회하지 않은 주소라 '이름표 미확인'으로 적는다.
TAG = {
    TRE: 'Paxos: Treasury', P4: 'Paxos 4',
    '0x6fa67393be5d9a5b6b3570646ef238bb52795350': 'Paxos: Deposit Funder 2',
    '0x8a89e016750479dc1d7ad32ecffcecd76e118697': 'Paxos: Deposit Funder',
    '0xcffad3200574698b78f32232aa9d63eabd290703': 'Crypto.com 16',
    '0xb61bb0c3f4afc30b1d8dbcb8767c0e38c4829322': 'Kraken 101',
    '0x367c42a6f261ec54ffbecf5f41c226be12a3dca0': 'Bullish 1',
    '0x33566c9d8be6cf0b23795e0d380e112be9d75836': 'Galaxy Digital: OTC',
    PSM_JOIN: 'Sky: MCD Join PSM PAX A',
    '0x38699d04656ff537ef8671b6b595402ebdbdf6f4': 'PAXOS: PAXG Fees',
    '0xdfd5293d8e347dfe59e90efd55b2956a1343963d': 'Binance 16',
    '0x28c6c06298d514db089934071355e5743bf21d60': 'Binance 14',
    '0x21a31ee1afc51d94c2efccaa2092ad1028285549': 'Binance 15',
    '0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43': 'Coinbase 10',
    '0x51c72848c68a965f66fa7a88855f9f7784502a7f': 'Market Maker: 0x51c7...2a7f',
    '0x611479ce1d3d457ffe9fb2abbaf8d3fe2ad8fffb': 'Paxos: PAXG Fees 2',
}
NOTAG = {'0x149463398d8ecc45eef14765fbe0951ee358401c', '0x609b811d91ed19a57fe8494f952a2518c7635485',
         '0xbabb07bbe931c4d7d1c9886396c566b9955c7340', '0xa4e45f6fbaafa266b86591e46d39989a961ad9e2',
         '0x3691a5e752dac1788e2d393309930cc7128fdbd6', '0x4f4f1c4118b2cc4fdb692b3073321c591ed1ae89',
         '0x2bcb6bc69991802124f04a1114ee487ff3fad197', H657, '0x687cb60bc5ca330fbc727279a52642ee84b33554',
         '0x23a10f09fac6ccdbfb6d9f0215c795f9591d7476', '0x1e86cb085f249772f7e7443631a87c6bdba2aceb',
         '0x7707d9eaf2d7ba2343fe7504d687596f9cc618c7', '0xd14dafc47cbbb3065032452ba95879bf4e858ed8',
         '0x01820d92f8f86947ca0454789172ad60e05817fa', '0xcfb7e94d71ab3c65479dacd9d8f2159184ca17ed',
         '0x6d91f70aa356988db3ec1bfe702ccc1cfcfad8d3'}
PAXOS = {TRE, P4}  # Crypto.com 16 보유분 출처 비중 계산용
# 보유 주소가 토큰을 어디서 받았는지 달별로 본다: 주소 -> 출처 주소 집합
SRC = {'0xcffad3200574698b78f32232aa9d63eabd290703': PAXOS, H657: {PSM_JOIN}}


def utc(x): return dt.datetime.fromtimestamp(int(x, 16) if str(x).startswith('0x') else int(x), dt.timezone.utc)
def who(a): return f'{a} ({TAG[a] if a in TAG else "이름표 없음" if a in NOTAG else "이름표 미확인"})'
def topk(v, k): return sum(sorted(v, reverse=True)[:k]) / sum(v)
def window(c): return ce.ts(WIN[c][0]), ce.ts(WIN[c][1])


def fetch():
    ex = {}
    for c in WIN:
        tok = ce.COINS[c][0]; s, e = window(c)
        lo, hi = ce.blk(s, 'after'), ce.blk(e - 1, 'before')
        x = ex[c] = {'blocks': [lo, hi], 'tokentx': {}}
        x['treasury_out'] = ce.getlogs(tok, lo, hi, ce.TR, t1='0x' + '0' * 24 + TRE[2:], out=[])
        for a, mode in HIST[c].items():
            r = ce.api(module='account', action='tokentx', contractaddress=tok, address=a, startblock=0 if mode == 'all' else lo - 7200,
                       endblock=hi, page=1, offset=1000, sort='asc')['result']
            assert isinstance(r, list) and len(r) < 1000, (c, a, str(r)[:200])  # 1000건이면 잘렸을 수 있다
            x['tokentx'][a] = r
        if c == 'USDP':  # PSM 에서 USDP 를 꺼낸 거래의 호출 대상과 Sky 주소 목록
            x['psm_tx'] = []
            for t in x['tokentx'][H657]:
                if t['from'].lower() == PSM_JOIN and s <= int(t['timeStamp']) < e:
                    tx = ce.api(module='proxy', action='eth_getTransactionByHash', txhash=t['hash'])['result']
                    x['psm_tx'].append({'hash': t['hash'], 'block': int(t['blockNumber']), 'from': tx['from'], 'to': tx['to'], 'selector': tx['input'][:10]})
            # Etherscan eth_call 은 과거 블록을 줘도 현재 상태를 돌려준다(2026-10-10 확인). 그래서 현재 값만 받는다.
            x['chainlog'] = {k: ce.ethcall(CHAINLOG, ce.kc('getAddress(bytes32)')[:10] + k.encode().hex().ljust(64, '0'), 'latest')
                             for k in ('RWA015_A_OUTPUT_CONDUIT', 'MCD_JOIN_PSM_PAX_A')}
    ex['funder'] = {}
    for a in FUND:
        r = ce.api(module='account', action='txlist', address=a, startblock=0, endblock=99999999, page=1, offset=5, sort='asc')['result']
        f = [t for t in r if t['to'].lower() == a and int(t['value']) > 0][0]
        ex['funder'][a] = {'from': f['from'].lower(), 'time': f['timeStamp'], 'hash': f['hash']}
    with gzip.open(EXTRA, 'wt') as f: json.dump(ex, f)
    print('saved', EXTRA, 'calls', ce.ncalls[0])


def report():
    ex = json.load(gzip.open(EXTRA, 'rt')); L = []; p = L.append
    for c in WIN:
        dec = ce.COINS[c][3]; U = lambda v: v / 10 ** dec; s, e = window(c); x = ex[c]
        inw = lambda t: s <= int(t, 16 if str(t).startswith('0x') else 10) < e
        win = [l for l in ce.load(f'{c}_burn_addr_inflow')['inflows'][TRE] if inw(l['timeStamp'])]
        by, n = collections.Counter(), collections.Counter()
        for l in win: a = '0x' + l['topics'][1][-40:]; by[a] += int(l['data'], 16); n[a] += 1
        mb = ce.load(f'{c}_mintburn_logs')
        burns = [l for l in mb['burn'] if inw(l['timeStamp'])]; mints = [l for l in mb['mint'] if inw(l['timeStamp'])]
        out = collections.Counter()
        for l in x['treasury_out']: out['0x' + l['topics'][2][-40:]] += int(l['data'], 16)
        bsum, tot = sum(int(l['data'], 16) for l in burns), sum(by.values())
        nb = sum(v for a, v in out.items() if a != '0x' + '0' * 40)
        d0, d1, du = DL[c]
        # 점검: 창 경계가 DefiLlama 날짜와 맞는지(소각 합 + unreleased 변화 = DefiLlama 감소량)
        assert abs(U(bsum) - U(sum(int(l['data'], 16) for l in mints)) + (du or 0) - (d0 - d1)) < 1, c
        assert U(int(out['0x' + '0' * 40])) == U(bsum)  # 금고 출금 중 0 주소행 = 소각 기록
        p(f'## {c} {WIN[c][0]} ~ {WIN[c][1]} (UTC 00:00 기준, 블록 {x["blocks"][0]}~{x["blocks"][1]})')
        p(f'DefiLlama 유통량 {d0:,} -> {d1:,} ({(d1 - d0) / d0:+.2%}, {d1 - d0:+,}), unreleased 변화 {du if du is None else f"{du:+,}"}')
        p(f'창 안 발행 {U(sum(int(l["data"], 16) for l in mints)):,.2f} ({len(mints)}건), 소각 {U(bsum):,.2f} ({len(burns)}건)')
        p(f'창 안 금고 입금 {U(tot):,.2f} ({len(win)}건, 보낸 주소 {len(by)}곳), 금고에서 소각 아닌 출금 {U(nb):,.2f}: '
          + ', '.join(f'{who(a)} {U(v):,.2f}' for a, v in out.most_common() if a != '0x' + '0' * 40))
        p(f'금고 잔액 변화(흐름으로 계산) {U(tot + sum(int(l["data"], 16) for l in mints) - bsum - nb):+,.2f}')
        p('상위 주소 비중(금고 입금액 기준): ' + ', '.join(f'상위 {k}곳 {topk(list(by.values()), k):.2%}' for k in (1, 3, 10)))
        p('| 순위 | 금고로 보낸 주소 | 금액 | 건수 | 비중 |'); p('|---|---|---|---|---|')
        for i, (a, v) in enumerate(by.most_common(10), 1): p(f'| {i} | {who(a)} | {U(v):,.2f} | {n[a]} | {v / tot:.2%} |')
        p('소각 기록: ' + '; '.join(f'{utc(l["timeStamp"]):%m-%d %H:%M} {U(int(l["data"], 16)):,.2f}' for l in burns))
        p('100만 이상 금고 입금(UTC 시각, 금액, 보낸 주소, 거래):')
        for l in sorted(win, key=lambda l: int(l['timeStamp'], 16)):
            if U(int(l['data'], 16)) >= 1e6: p(f'- {utc(l["timeStamp"]):%Y-%m-%d %H:%M} {U(int(l["data"], 16)):,.2f} {who("0x" + l["topics"][1][-40:])} {l["transactionHash"]}')
        p('주소별 토큰 이동(창 안: 받은 곳 / 보낸 곳, all 주소는 창 끝까지 누적도 함께):')
        for a, mode in HIST[c].items():
            r = x['tokentx'][a]
            def agg(rows):
                i, o = collections.Counter(), collections.Counter()
                for t in rows:
                    v = int(t['value'])
                    if t['to'].lower() == a: i[t['from'].lower()] += v
                    if t['from'].lower() == a: o[t['to'].lower()] += v
                return i, o
            rw = [t for t in r if inw(t['timeStamp'])]
            i, o = agg(rw)
            p(f'- {who(a)}')
            if len(rw) <= 12:  # 건수가 적으면 한 건씩 적는다
                for t in rw: p(f'  {utc(t["timeStamp"]):%Y-%m-%d %H:%M} {t["from"].lower()} -> {t["to"].lower()} {U(int(t["value"])):,.2f} {t["hash"]}')
            p('  창 안 받음: ' + ', '.join(f'{who(k)} {U(v):,.2f}' for k, v in i.most_common(5)) + f' (보낸 곳 {len(i)}곳)')
            p('  창 안 보냄: ' + ', '.join(f'{who(k)} {U(v):,.2f}' for k, v in o.most_common(5)))
            if mode == 'all':
                i, o = agg(r)
                px = sum(v for k, v in i.items() if k in PAXOS)
                p(f'  누적({utc(r[0]["timeStamp"]):%Y-%m-%d}~{utc(r[-1]["timeStamp"]):%Y-%m-%d}, {len(r)}건) 받음 {U(sum(i.values())):,.2f}: '
                  + ', '.join(f'{who(k)} {U(v):,.2f}' for k, v in i.most_common(4)) + f' (보낸 곳 {len(i)}곳)'
                  + (f', Paxos: Treasury 와 Paxos 4 에서 받은 비중 {px / sum(i.values()):.1%}' if px else ''))
                p('  누적 보냄: ' + ', '.join(f'{who(k)} {U(v):,.2f}' for k, v in o.most_common(4)))
                if a in SRC:
                    m = collections.Counter()
                    for t in r:
                        if t['to'].lower() == a and t['from'].lower() in SRC[a]: m[f'{utc(t["timeStamp"]):%Y-%m}'] += int(t['value'])
                    p('  출처(' + ', '.join(TAG[k] for k in sorted(SRC[a])) + ')에서 받은 달별 합계: ' + ', '.join(f'{k} {U(v):,.2f}' for k, v in sorted(m.items())))
        if c == 'USDP':
            ch = x['chainlog']
            p(f'Sky 주소 목록(현재 값): RWA015_A_OUTPUT_CONDUIT = 0x{ch["RWA015_A_OUTPUT_CONDUIT"][-40:]}, '
              f'MCD_JOIN_PSM_PAX_A = 0x{ch["MCD_JOIN_PSM_PAX_A"][-40:]}')
            fn = {ce.kc(f)[:10]: f for f in ('push()', 'push(uint256)')}  # 함수 선택자 -> 이름
            for t in x['psm_tx']: p(f'- PSM 출금 거래 {t["hash"]}: 호출 {t["from"]} -> {t["to"]}, 함수 {t["selector"]} {fn.get(t["selector"], "")}')
        p('')
    p('첫 ETH 입금(가스비를 처음 보낸 주소, 거래):')
    for a, f in ex['funder'].items(): p(f'- {who(a)} <- {who(f["from"])} {utc(f["time"]):%Y-%m-%d %H:%M} {f["hash"]}')
    print('\n'.join(L))
    with open(OUTTXT, 'w') as f: f.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    assert topk([5, 3, 2], 1) == 0.5 and topk([5, 3, 2], 10) == 1.0
    fetch() if sys.argv[1:] == ['fetch'] else report()
