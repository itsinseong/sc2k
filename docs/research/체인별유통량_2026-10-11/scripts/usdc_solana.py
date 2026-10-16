"""USDC 솔라나: Circle 보관 지갑(7VHUFJ...)의 토큰 계정 6개가 2023-03-10~03-17 사이 어떻게 변했는지 거래 단위로 받는다.
- 보관 지갑 계정의 모든 거래(서명 목록 + 거래 원문)를 받아 raw/usdc_solana_txs.json.gz에 저장
- 발행 권한 계정(BJE5MM...)의 같은 기간 거래 수
스크립트는 받기만 한다. 분석은 usdc_solana_analyze.py."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sol import *
MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
WALLET = "7VHUFJHWu2CuExkJcJrzhQPJ2oygupTWkL2A2For4BmE"
AUTH = "BJE5MMbqXjVwjAF7oxwPYXnTXDyspzZyt4vwenNw5ruG"
T0 = utc("2023-03-09 22:00:00"); T1 = utc("2023-03-17 02:00:00")   # 양 끝 여유 두 시간
accts = [x["pubkey"] for x in q("getTokenAccountsByOwner", [WALLET, {"mint": MINT}, {"encoding": "jsonParsed"}])["value"]]
print("계정", accts, flush=True)
s1 = slot_at(T1, lo=181000000); sg1 = any_sig(s1)
out = {"wallet": WALLET, "accts": accts, "T0": T0, "T1": T1, "sigs": {}, "txs": {}}
def window_sigs(A):
    before = sg1; res = []
    while True:
        l = sigs_before(A, before, limit=1000)
        if not l: break
        done = False
        for x in l:
            if x["blockTime"] and x["blockTime"] < T0: done = True; break
            res.append(x)
        if done or len(l) < 1000: break
        before = l[-1]["signature"]
    return res
for A in accts + [AUTH]:
    out["sigs"][A] = window_sigs(A); print(A, len(out["sigs"][A]), flush=True)
allsig = {x["signature"] for A in accts for x in out["sigs"][A]}
print("거래 수", len(allsig), flush=True)
for i, sg in enumerate(sorted(allsig)):
    out["txs"][sg] = tx(sg)
    if i % 100 == 0: print(i, flush=True)
save_gz("usdc_solana_txs.json.gz", out)
