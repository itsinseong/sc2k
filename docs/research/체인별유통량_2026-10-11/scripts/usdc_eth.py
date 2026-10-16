"""USDC 이더리움: 발행량(totalSupply)과 Circle 보관 지갑 잔액을 과거 블록에서 읽는다(아카이브 RPC eth_call)."""
import sys; sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from lib import *
URL = "https://eth.drpc.org"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
TREASURY = "0x55FE002aefF02F77364de339a1292923A15844B8"
out = {}
for label, t in [("a_0040", "2023-03-10 00:40:24"), ("b_0040", "2023-03-17 00:40:24"), ("a_0000", "2023-03-10 00:00:00"), ("b_0000", "2023-03-17 00:00:00")]:
    ts = utc(t); b = block_at(URL, ts)
    out[label] = {"time": t, "block": b, "block_time": block_ts(URL, b), "totalSupply": total_supply(URL, USDC, b), "treasury": balance_of(URL, USDC, TREASURY, b)}
    print(label, out[label], flush=True)
save_gz("usdc_eth_supply.json.gz", out)
