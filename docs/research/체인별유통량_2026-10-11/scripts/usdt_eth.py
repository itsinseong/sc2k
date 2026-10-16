"""USDT 이더리움: totalSupply와 Tether 보관 지갑(0x5754...) 잔액을 과거 블록에서 읽는다. 시각은 00:00:00 UTC."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
URL = "https://eth.drpc.org"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
TREASURY = "0x5754284f345afc66a98fbb0a0afe71e0f007b949"
out = {}
for label, t in [("a", "2022-05-11 00:00:00"), ("b", "2022-05-18 00:00:00")]:
    b = block_at(URL, utc(t))
    out[label] = {"time": t, "block": b, "block_time": block_ts(URL, b), "totalSupply": total_supply(URL, USDT, b), "treasury": balance_of(URL, USDT, TREASURY, b)}
    print(label, out[label], flush=True)
save_gz("usdt_eth_supply.json.gz", out)
