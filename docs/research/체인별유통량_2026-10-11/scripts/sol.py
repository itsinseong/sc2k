"""Solana 공개 RPC 보조 함수: 시각에서 슬롯 찾기, 토큰 계정의 과거 잔액(그 시각 직전 거래의 사후 잔액)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
S = "https://api.mainnet-beta.solana.com"
def q(m, p): return rpc(S, m, p)

def slot_time(s):
    try: return q("getBlockTime", [s])
    except RuntimeError: return None

def slot_at(ts, lo=1, hi=None):
    hi = hi or q("getSlot", [])
    while lo < hi:
        mid = (lo + hi + 1) // 2
        t = None; k = mid
        for k in range(mid, min(mid + 50, hi + 1)):
            t = slot_time(k)
            if t: break
        if t is None: hi = mid - 1; continue
        if t <= ts: lo = mid
        else: hi = mid - 1
    return lo

def any_sig(slot):
    for s in range(slot, slot + 100):
        try:
            b = q("getBlock", [s, {"transactionDetails": "signatures", "rewards": False, "maxSupportedTransactionVersion": 0}])
        except RuntimeError: continue
        if b and b["signatures"]: return b["signatures"][0]

def sigs_before(acct, before, limit=1000, until=None):
    o = {"limit": limit, "before": before}
    if until: o["until"] = until
    return q("getSignaturesForAddress", [acct, o])

def tx(sig):
    return q("getTransaction", [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])

def post_balance(t, acct):
    keys = [k["pubkey"] if isinstance(k, dict) else k for k in t["transaction"]["message"]["accountKeys"]]
    i = keys.index(acct)
    for b in t["meta"]["postTokenBalances"]:
        if b["accountIndex"] == i: return int(b["uiTokenAmount"]["amount"])
    return None
