"""usdc_solana.py가 받은 거래로 (1) 보관 지갑 토큰 계정 6개 합계를 시각별로 다시 만들고 (2) 기간 안 발행(mintTo), 소각(burn) 명령을 센다."""
import gzip, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import utc, RAW
d = json.load(gzip.open(os.path.join(RAW, "usdc_solana_txs.json.gz"), "rt"))
MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"; accts = d["accts"]
# 거래별: 시각, 계정별 사후 잔액
ev = []   # (blockTime, slot, sig, {acct: post})
mint_burn = []
for sg, t in d["txs"].items():
    if not t or t["meta"]["err"]: continue
    keys = [k["pubkey"] for k in t["transaction"]["message"]["accountKeys"]]
    post = {}
    for b in t["meta"]["postTokenBalances"]:
        a = keys[b["accountIndex"]]
        if a in accts and b["mint"] == MINT: post[a] = int(b["uiTokenAmount"]["amount"])
    ev.append((t["blockTime"], t["slot"], sg, post))
    ins = list(t["transaction"]["message"]["instructions"])
    for inner in t["meta"].get("innerInstructions") or []: ins += inner["instructions"]
    for i in ins:
        p = i.get("parsed")
        if isinstance(p, dict) and p.get("type") in ("mintTo", "mintToChecked", "burn", "burnChecked") and p["info"].get("mint") == MINT:
            amt = p["info"].get("amount") or p["info"]["tokenAmount"]["amount"]
            mint_burn.append((t["blockTime"], p["type"], int(amt), sg))
ev.sort()
def at(ts):
    """ts 이하 마지막 거래 이후의 계정별 잔액(기간 시작 전 거래가 없으면 첫 거래의 사전 잔액으로 역산)."""
    state = {}
    for bt, sl, sg, post in ev:
        if bt > ts: break
        state.update(post)
    return state
# 시작 전 잔액이 없는 계정은 첫 거래의 사전 잔액
pre = {}
for sg, t in sorted(d["txs"].items(), key=lambda kv: (kv[1] or {}).get("blockTime", 0)):
    if not t: continue
    keys = [k["pubkey"] for k in t["transaction"]["message"]["accountKeys"]]
    for b in t["meta"]["preTokenBalances"]:
        a = keys[b["accountIndex"]]
        if a in accts and a not in pre: pre[a] = int(b["uiTokenAmount"]["amount"])
res = {"n_tx": len(ev), "mint_burn_in_window": mint_burn}
for label, t in [("2023-03-10 00:00:00", None), ("2023-03-10 00:40:24", None), ("2023-03-17 00:00:00", None), ("2023-03-17 00:40:24", None)]:
    ts = utc(label); st = {a: pre.get(a, 0) for a in accts}; st.update(at(ts))
    res[label] = sum(st.values()) / 1e6
    print(label, "6계정 합계", res[label], {a[:6]: v / 1e6 for a, v in st.items()})
print("기간 안 mintTo/burn 명령:", mint_burn)
print("인증 권한 거래 수:", len(d["sigs"]["BJE5MMbqXjVwjAF7oxwPYXnTXDyspzZyt4vwenNw5ruG"]))
