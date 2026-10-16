"""OKC(OKTChain) USDT: 과거 상태 조회가 막혀 있어(eth_call internal 오류) Transfer 로그에서 0 주소 발행(from 0), 소각(to 0)을
2,322,601 블록(공개 RPC가 받는 가장 앞 블록)부터 2022-05-18 00:00 UTC 블록까지 받아 raw/USDT_okc_mintburn.json.gz에 저장한다.
RPC 한 번에 2000블록까지만 허용해 2000블록씩 나눠 받는다."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from lib import *
from concurrent.futures import ThreadPoolExecutor
lib.post.__defaults__ = (6,)
U = "https://exchainrpc.okex.org"; T = "0x382bb369d343125bfb2117af9c149795c6c65c50"
TR = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"; Z = "0x" + "0" * 64
A, B = 2322601, block_at(U, utc("2022-05-18 00:00:00"))
spans = [(s, min(s + 1999, B)) for s in range(A, B + 1, 2000)]
def get(sp):
    out = {}
    for name, tp in (("mint", [TR, Z]), ("burn", [TR, None, Z])):
        out[name] = rpc(U, "eth_getLogs", [{"address": T, "fromBlock": hex(sp[0]), "toBlock": hex(sp[1]), "topics": tp}])
    return out
mint, burn = [], []
with ThreadPoolExecutor(8) as ex:
    for i, r in enumerate(ex.map(get, spans)):
        mint += r["mint"]; burn += r["burn"]
        if i % 200 == 0: print(i, len(spans), len(mint), len(burn), flush=True)
keep = lambda l: [{"block": int(x["blockNumber"], 16), "tx": x["transactionHash"], "idx": int(x["logIndex"], 16), "data": x["data"], "topics": x["topics"]} for x in l]
save_gz("USDT_okc_mintburn.json.gz", {"token": T, "from": A, "to": B, "mint": keep(mint), "burn": keep(burn)})
print("끝", len(mint), len(burn))
