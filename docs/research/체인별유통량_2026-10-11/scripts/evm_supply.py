"""EVM 체인의 토큰 공급량을 과거 블록에서 읽는다(아카이브 eth_call).
사용: python3 -I evm_supply.py <코인> <체인> -> raw/<코인>_<체인>_supply.json.gz
시각은 코인별 두 날짜의 00:40:24 UTC(DefiLlama 기록 시각에 가장 가까운 값, 이더리움 totalSupply가 DefiLlama minted와 1달러 안으로 맞는 시각)와 00:00:00 UTC."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import lib
RPC = {
 "arbitrum": ["https://arbitrum-one.public.blastapi.io"],
 "bsc": ["https://bsc-mainnet.public.blastapi.io"],
 "polygon": ["https://polygon-mainnet.public.blastapi.io", "https://polygon.drpc.org"],
 "avalanche": ["https://api.avax.network/ext/bc/C/rpc"],
 "ethereum": ["https://eth.drpc.org", "https://rpc.mevblocker.io"],
 "okc": ["https://exchainrpc.okex.org"],
}
TOK = {
 ("USDC", "arbitrum"): ["0xff970a61a04b1ca14834a43f5de4533ebddb5cc8", "0xaf88d065e77c8cc2239327c5edb3a432268e5831"],
 ("USDC", "polygon"): ["0x2791bca1f2de4661ed88a30c99a7a9449aa84174", "0x4318cb63a2b8edf2de971e2f17f77097e499459d", "0x750e4c4984a9e0f12978ea6742bc1c5d248f40ed", "0x5bEF2617eCCA9a39924c09017c5F1E25Efbb3bA8", "0x576cf361711cd940cd9c397bb98c4c896cbd38de", "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359"],
 ("USDC", "bsc"): ["0xB04906e95AB5D797aDA81508115611fee694c2b3", "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", "0x91Ca579B0D47E5cfD5D0862c21D5659d39C8eCf0", "0x672147dD47674757C457eB155BAA382cc10705Dd", "0xc1F47175d96Fe7c4cD5370552e5954f384E3C791"],
 ("USDC", "avalanche"): ["0xB97ef9ef8734C71904D8002F8b6Bc66Dd9c48a6E", "0xa7d7079b0fead91f3e65f86e8915cb59c1a4c664", "0xB24CA28D4e2742907115fECda335b40dbda07a4C", "0xfab550568c688d5d8a52c7d794cb93edc26ec0ec", "0x0950Fc1AD509358dAeaD5eB8020a3c7d8b43b9DA", "0x6145E8a910aE937913426BF32De2b26039728ACF", "0x543672E9CBEC728CBBa9C3Ccd99ed80aC3607FA8"],
 ("USDT", "bsc"): ["0x55d398326f99059fF775485246999027B3197955", "0x2B90E061a517dB2BbD7E39Ef7F733Fd234B494CA", "0x524bC91Dc82d6b90EF29F76A3ECAaBAffFD490Bc", "0x49d5cC521F75e13fa8eb4E89E9D381352C897c96"],
 ("USDT", "okc"): ["0x382bb369d343125bfb2117af9c149795c6c65c50"],
 ("USDT", "polygon"): ["0xc2132d05d31c914a87c6611c10748aeb04b58e8f", "0x9417669fBF23357D2774e9D421307bd5eA1006d2", "0xceed2671d8634e3ee65000edbbee66139b132fbf", "0x3553f861dEc0257baDA9F8Ed268bf0D74e45E89C"],
 ("USDT", "avalanche"): ["0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7", "0xc7198437980c041c805a1edcba50c1ce5db95118", "0xf976ba91b6bb3468c91e4f02e68b37bc64a57e66", "0xF0FF231e3F1A50F83136717f287ADAB862f89431", "0xA67BCC0D06d7d13A13A2AE30bF30f1B434f5a28B"],
}
# 보관 지갑 잔액도 읽을 (코인, 체인): (토큰, 지갑)
UNREL = {("USDT", "avalanche"): ("0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7", "0x5754284f345afc66a98fbb0a0afe71e0f007b949")}
TIMES = {"USDC": ["2023-03-10", "2023-03-17"], "USDT": ["2022-05-11", "2022-05-18"]}
HM = {"USDC": "00:40:24", "USDT": "00:00:00"}
def pick(urls, token, T):
    last = None
    for u in urls:
        try:
            b = block_at(u, T); total_supply(u, token, b); return u
        except Exception as e: last = e
    raise RuntimeError(f"쓸 수 있는 RPC 없음: {last}")
if __name__ == "__main__":
    coin, chain = sys.argv[1:3]
    lib.post.__defaults__ = (4,)
    urls = RPC[chain]; out = {"coin": coin, "chain": chain, "tokens": {}}
    for tok in TOK[(coin, chain)]:
        info = {}
        for d in TIMES[coin]:
            for hm in sorted({HM[coin], "00:00:00"}):
                T = utc(f"{d} {hm}")
                try: u = pick(urls, tok, T); b = block_at(u, T)
                except RuntimeError as e:   # 그 시점에 계약이 없으면 eth_call이 '0x'를 돌려준다
                    info[f"{d} {hm}"] = {"error": str(e), "raw": None, "decimals": None}; continue
                try:
                    raw = total_supply(u, tok, b)
                    dec = call_uint(u, tok, "0x313ce567", b)
                except Exception as e:
                    raw, dec = None, None
                info[f"{d} {hm}"] = {"rpc": u, "block": b, "block_time": block_ts(u, b), "raw": raw, "decimals": dec}
        out["tokens"][tok] = info
        if UNREL.get((coin, chain), (None,))[0] == tok:
            ow = UNREL[(coin, chain)][1]; un = {}
            for k, v in info.items():
                un[k] = balance_of(v["rpc"], tok, ow, v["block"])
            out["unreleased"] = {"owner": ow, "raw": un}; print("unreleased", {k: x / 10 ** 6 for k, x in un.items()}, flush=True)
        print(tok, {k: (v["raw"] / 10 ** v["decimals"] if v["raw"] is not None else None) for k, v in info.items()}, flush=True)
    save_gz(f"{coin}_{chain}_supply.json.gz", out)
