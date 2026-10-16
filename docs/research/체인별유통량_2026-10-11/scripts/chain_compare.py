"""DefiLlama 체인별 값(Claude웹_1차/data/raw 원응답)과 이 폴더 raw의 공식 원자료 재계산 값을 나란히 놓는다. 호출 없음, 읽기만 한다.
사용: python3 -I chain_compare.py  (표준 출력으로 비교 숫자를 낸다. 보고서 체인별대조.md의 숫자는 이 출력에서 옮겼다.)"""
import gzip, json, os, datetime, sys
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "..", "raw")
DL = os.path.join(HERE, "..", "..", "Claude웹_1차", "data", "raw")
def g(n): return json.load(gzip.open(os.path.join(RAW, n), "rt"))
def D(s): return int(datetime.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).timestamp())
def U(s): return int(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp())
def dl(coin, chain, day):
    f = {"USDC": "defillama_USDC_2.json", "USDT": "defillama_USDT_1.json"}[coin]
    d = json.load(open(os.path.join(DL, f)))["chainBalances"][chain]["tokens"]
    t = next(x for x in d if x["date"] == D(day)); return t
def f(x): return "-" if x is None else f"{x:,.2f}"
def row(label, a, b): print(f"  {label:<46} DL {f(a):>22}  원자료 {f(b):>22}  차이 {f(None if a is None or b is None else b - a):>16}")

DAYS = {"USDC": ("2023-03-10", "2023-03-17"), "USDT": ("2022-05-11", "2022-05-18")}
# 1. 체인별 비중(체인 기록 합 기준, 구간 시작일)
for coin in DAYS:
    d = json.load(open(os.path.join(DL, {"USDC": "defillama_USDC_2.json", "USDT": "defillama_USDT_1.json"}[coin])))["chainBalances"]
    for day in DAYS[coin]:
        vals = {}
        for c, v in d.items():
            t = next((x for x in v["tokens"] if x["date"] == D(day)), None)
            if t: vals[c] = t["circulating"].get("peggedUSD", 0)
        tot = sum(vals.values()); cum = 0
        print(f"[비중] {coin} {day} 체인 기록 합 {tot:,}")
        for c, x in sorted(vals.items(), key=lambda kv: -kv[1])[:9]:
            cum += x; print(f"   {c:<10}{x:>16,}  {x / tot * 100:6.2f}%  누적 {cum / tot * 100:6.2f}%")

# 2. USDC
print("\n[USDC 이더리움]")
e = g("usdc_eth_supply.json.gz")
for k, day in (("a_0040", "2023-03-10"), ("b_0040", "2023-03-17")):
    t = dl("USDC", "Ethereum", day)
    row(f"{day} 발행량(minted)", t["minted"]["peggedUSD"], e[k]["totalSupply"] / 1e6)
    row(f"{day} 보관분(unreleased)", t["unreleased"]["peggedUSD"], e[k]["treasury"] / 1e6)
print("[USDC 아비트럼]")
a = g("USDC_arbitrum_supply.json.gz")["tokens"]["0xff970a61a04b1ca14834a43f5de4533ebddb5cc8"]
for hm_day, day in (("2023-03-10 00:40:24", "2023-03-10"), ("2023-03-17 00:40:24", "2023-03-17")):
    t = dl("USDC", "Arbitrum", day); row(f"{day} 00:40:24 브리지 USDC 공급량", t["circulating"]["peggedUSD"], a[hm_day]["raw"] / 1e6)
print("[USDC BSC]")
b = g("USDC_bsc_supply.json.gz")["tokens"]
for hm_day, day in (("2023-03-10 00:40:24", "2023-03-10"), ("2023-03-17 00:40:24", "2023-03-17")):
    t = dl("USDC", "BSC", day); br = t["bridgedTo"]["bridges"]
    s = {k[:8]: v[hm_day]["raw"] / 10 ** v[hm_day]["decimals"] for k, v in b.items()}
    names = {"0xB04906": "wormhole Ethereum", "0x91Ca57": "wormhole Solana", "0x672147": "wormhole Polygon", "0xc1F471": "wormhole Avalanche", "0x8AC76a": "bsc Ethereum"}
    dlv = {"0xB04906": br["wormhole"]["Ethereum"]["amount"], "0x91Ca57": br["wormhole"]["Solana"]["amount"], "0x672147": br["wormhole"]["Polygon"]["amount"], "0xc1F471": br["wormhole"]["Avalanche"]["amount"], "0x8AC76a": br["bsc"]["Ethereum"]["amount"]}
    for k in names: row(f"{day} {names[k]}", dlv[k], s[k])
    row(f"{day} 5개 합 대 bridgedTo", t["bridgedTo"]["peggedUSD"], sum(s.values()))
    row(f"{day} 5개 합 대 circulating", t["circulating"]["peggedUSD"], sum(s.values()))
if os.path.exists(os.path.join(RAW, "USDC_polygon_supply.json.gz")):
    print("[USDC 폴리곤]")
    p = g("USDC_polygon_supply.json.gz")["tokens"]
    for hm_day, day in (("2023-03-10 00:40:24", "2023-03-10"), ("2023-03-17 00:40:24", "2023-03-17")):
        t = dl("USDC", "Polygon", day); br = t["bridgedTo"]["bridges"]
        key = {"0x2791bca1f2de4661ed88a30c99a7a9449aa84174": ("polygon", "Ethereum"), "0x4318cb63a2b8edf2de971e2f17f77097e499459d": ("wormhole", "Ethereum"),
               "0x750e4c4984a9e0f12978ea6742bc1c5d248f40ed": ("axelar", "Ethereum"), "0x5bEF2617eCCA9a39924c09017c5F1E25Efbb3bA8": ("orbit", "Ethereum"), "0x576cf361711cd940cd9c397bb98c4c896cbd38de": ("wormhole", "Solana")}
        tot = 0
        for tok, (bn, src) in key.items():
            v = p[tok][hm_day]; x = v["raw"] / 10 ** v["decimals"]; tot += x
            row(f"{day} {bn} {src}", br[bn][src]["amount"], x)
        n = p["0x3c499c542cef5e3811e1192ce70d8cc03d5c3359"][hm_day]; print("   네이티브 USDC 계약(0x3c49...)", n.get("error") and "그 시점에 계약 없음" or n)
        row(f"{day} 5개 합 대 bridgedTo", t["bridgedTo"]["peggedUSD"], tot)
        row(f"{day} 5개 합 대 circulating", t["circulating"]["peggedUSD"], tot)
print("[USDC 트론] Mint - Burn 누적")
ev = g("tron_usdc_events.json.gz")["events"]
x = [(e["block_timestamp"], int(e["result"]["amount"])) for e in ev["Mint"]] + [(e["block_timestamp"], -int(e["result"]["amount"])) for e in ev["Burn"]]
for hm_day, day in (("2023-03-10 00:40:24", "2023-03-10"), ("2023-03-17 00:40:24", "2023-03-17")):
    t = dl("USDC", "Tron", day); row(f"{day} 발행량", t["minted"]["peggedUSD"], sum(a for ts, a in x if ts <= U(hm_day) * 1000) / 1e6)
print("[USDC 솔라나] 보관 지갑 토큰 계정 6개 합 (usdc_solana_analyze.py와 같은 방법)")
s = g("usdc_solana_txs.json.gz"); MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"; ev = []
for sg, t in s["txs"].items():
    if not t or t["meta"]["err"]: continue
    keys = [k["pubkey"] for k in t["transaction"]["message"]["accountKeys"]]
    for bb in t["meta"]["postTokenBalances"]:
        if keys[bb["accountIndex"]] in s["accts"] and bb["mint"] == MINT: ev.append((t["blockTime"], t["slot"], keys[bb["accountIndex"]], int(bb["uiTokenAmount"]["amount"])))
ev.sort()
def sol_at(ts):
    st = {}
    for bt, sl, a, v in ev:
        if bt > ts: break
        st[a] = v
    return sum(st.values()) / 1e6
for hm_day, day in (("2023-03-10 00:40:24", "2023-03-10"), ("2023-03-17 00:40:24", "2023-03-17")):
    t = dl("USDC", "Solana", day); row(f"{day} 보관분(unreleased)", t["unreleased"]["peggedUSD"], sol_at(U(hm_day)))
    print(f"   {day} DL 발행량 {t['minted']['peggedUSD']:,} (두 날 같음), DL circulating - (minted - unreleased) = {t['circulating']['peggedUSD'] - (t['minted']['peggedUSD'] - t['unreleased']['peggedUSD']):,}")

# 3. USDT
print("\n[USDT 이더리움]")
e = g("usdt_eth_supply.json.gz")
for k, day in (("a", "2022-05-11"), ("b", "2022-05-18")):
    t = dl("USDT", "Ethereum", day)
    row(f"{day} 발행량(minted, 00:00 UTC)", t["minted"]["peggedUSD"], e[k]["totalSupply"] / 1e6)
    row(f"{day} 보관분(unreleased)", t["unreleased"]["peggedUSD"], e[k]["treasury"] / 1e6)
print("[USDT 트론]")
ev = g("tron_usdt_events.json.gz")["events"]
x = [(e["block_timestamp"], int(e["result"]["amount"])) for e in ev["Issue"]] + [(e["block_timestamp"], -int(e["result"]["amount"])) for e in ev["Redeem"]] + [(e["block_timestamp"], -int(e["result"]["_balance"])) for e in ev["DestroyedBlackFunds"]]
for day, hm in (("2022-05-11", "23:59:59"), ("2022-05-18", "23:59:59")):
    t = dl("USDT", "Tron", day); row(f"{day} 발행량(Issue - Redeem - DestroyedBlackFunds)", t["minted"]["peggedUSD"], sum(a for ts, a in x if ts <= U(f"{day} {hm}") * 1000) / 1e6)
A = "TKHuVq1oKVruCGLvqVexFs6dawKv6fQgFs"
after = g("tron_usdt_treasury_after.json.gz"); win = g("tron_usdt_treasury_trc20.json.gz"); pre = g("tron_usdt_treasury_pre_trc20.json.gz")
sg = lambda r: (int(r["value"]) if r["to"] == A else -int(r["value"]) if r["from"] == A else 0) / 1e6
b_end = after["balance_after"] / 1e6 - sum(map(sg, after["rows"]))
tr = sorted((r["block_timestamp"], sg(r)) for r in pre["rows"] + win["rows"] + after["rows"])
t_end = U("2022-05-18 00:00:00") * 1000
def tbal(ts): return b_end - sum(s for t, s in tr if ts < t <= t_end)
print(f"   트론 보관 지갑 현재 잔액 {after['balance_after'] / 1e6:,.2f}, 2022-05-18 00:00 UTC 잔액(현재 잔액에서 이후 이체 {len(after['rows'])}건을 되돌림) {b_end:,.2f}")
for day, hh in (("2022-05-11", ["00:00:00", "12:00:00", "23:59:59"]), ("2022-05-18", ["00:00:00"])):
    t = dl("USDT", "Tron", day)
    for h in hh: row(f"{day} {h} 보관 지갑 잔액(unreleased)", t["unreleased"]["peggedUSD"], tbal(U(f"{day} {h}") * 1000))
for day in ["2022-05-12", "2022-05-14", "2022-05-15"]:
    t = dl("USDT", "Tron", day); print(f"   {day} DL unreleased {t['unreleased']['peggedUSD']:,}, 지갑 잔액 00:00 {tbal(U(day + ' 00:00:00') * 1000):,.0f} / 23:59:59 {tbal(U(day + ' 23:59:59') * 1000):,.0f}")
print("[USDT BSC]")
b = g("USDT_bsc_supply.json.gz")["tokens"]
for day in DAYS["USDT"]:
    t = dl("USDT", "BSC", day); br = t["bridgedTo"]["bridges"]; k = day + " 00:00:00"
    s = {kk[:8]: v[k]["raw"] / 10 ** v[k]["decimals"] for kk, v in b.items()}
    row(f"{day} 00:00 BSC-USD 계약(0x55d398) 공급량 대 bsc(Tron+Ethereum)", br["bsc"]["Tron"]["amount"] + br["bsc"]["Ethereum"]["amount"], s["0x55d398"])
    row(f"{day} wormhole Ethereum(0x524bC9)", br["wormhole"]["Ethereum"]["amount"], s["0x524bC9"])
    row(f"{day} wormhole Solana(0x49d5cC)", br["wormhole"]["Solana"]["amount"], s["0x49d5cC"])
    row(f"{day} wormhole Avalanche(0x2B90E0)", br["wormhole"]["Avalanche"]["amount"], s["0x2B90E0"])
    row(f"{day} 4개 합 대 circulating", t["circulating"]["peggedUSD"], sum(s.values()))
print("[USDT 폴리곤] (대상 밖, 받아 둔 값)")
p = g("USDT_polygon_supply.json.gz")["tokens"]
for day in DAYS["USDT"]:
    t = dl("USDT", "Polygon", day); k = day + " 00:00:00"
    tot = sum(v[k]["raw"] / 10 ** v[k]["decimals"] for v in p.values()); row(f"{day} 00:00 4개 합 대 circulating", t["circulating"]["peggedUSD"], tot)

# 4. 7일 변화 기여: 체인별 DL circulating 변화와 원자료로 바꾼 값의 변화
print("\n[7일 변화 기여] 원자료로 바꾼 부분만 교체, 나머지는 DL 값 그대로")
def chain_dl(coin, chain, day): return dl(coin, chain, day)["circulating"]["peggedUSD"]
def agg(coin):
    import csv
    rows = {r[0]: float(r[1]) for r in csv.reader(open(os.path.join(DL, "..", f"{coin}_circulating.csv"))) if r and r[0][:2] == "20" and r[1]}
    return rows
for coin in DAYS:
    a, b = DAYS[coin]; ag = agg(coin)
    chains = json.load(open(os.path.join(DL, {"USDC": "defillama_USDC_2.json", "USDT": "defillama_USDT_1.json"}[coin])))["chainBalances"]
    sa = sum(next((x for x in v["tokens"] if x["date"] == D(a)), {"circulating": {}})["circulating"].get("peggedUSD", 0) for v in chains.values())
    sb = sum(next((x for x in v["tokens"] if x["date"] == D(b)), {"circulating": {}})["circulating"].get("peggedUSD", 0) for v in chains.values())
    print(f"  {coin} 집계 계열 {ag[a]:,.0f} -> {ag[b]:,.0f} ({(ag[b] / ag[a] - 1) * 100:.4f}%), 체인 기록 합 {sa:,} -> {sb:,} ({(sb / sa - 1) * 100:.4f}%), 집계-체인합 {ag[a] - sa:,.0f} / {ag[b] - sb:,.0f}")

print("\n[USDC 아발란체]")
av = g("USDC_avalanche_supply.json.gz")["tokens"]
K = {"0xB97ef9ef8734C71904D8002F8b6Bc66Dd9c48a6E": "minted", "0xa7d7079b0fead91f3e65f86e8915cb59c1a4c664": ("avax", "Ethereum"), "0xfab550568c688d5d8a52c7d794cb93edc26ec0ec": ("axelar", "Ethereum"),
     "0xB24CA28D4e2742907115fECda335b40dbda07a4C": ("wormhole", "Ethereum"), "0x0950Fc1AD509358dAeaD5eB8020a3c7d8b43b9DA": ("wormhole", "Solana"), "0x6145E8a910aE937913426BF32De2b26039728ACF": ("wormhole", "BSC"), "0x543672E9CBEC728CBBa9C3Ccd99ed80aC3607FA8": ("wormhole", "Polygon")}
for hm_day, day in (("2023-03-10 00:40:24", "2023-03-10"), ("2023-03-17 00:40:24", "2023-03-17")):
    t = dl("USDC", "Avalanche", day); br = t["bridgedTo"]["bridges"]; tot = 0
    for tok, key in K.items():
        v = av[tok][hm_day]; x = v["raw"] / 10 ** v["decimals"]
        if key == "minted": row(f"{day} 발행량(minted)", t["minted"]["peggedUSD"], x); m = x
        else: row(f"{day} {key[0]} {key[1]}", br[key[0]][key[1]]["amount"], x); tot += x
    row(f"{day} 6개 합 대 bridgedTo", t["bridgedTo"]["peggedUSD"], tot)
    row(f"{day} 발행량 + 6개 합 대 circulating", t["circulating"]["peggedUSD"], m + tot)

print("\n[USDT 트론 분해] circulating = minted - 보관 지갑(unreleased) - BSC로 건너간 몫 - 그 밖의 브리지")
for day in DAYS["USDT"]:
    t = dl("USDT", "Tron", day); bs = dl("USDT", "BSC", day)["bridgedTo"]["bridges"]["bsc"]["Tron"]["amount"]
    mi, un, ci = t["minted"]["peggedUSD"], t["unreleased"]["peggedUSD"], t["circulating"]["peggedUSD"]
    print(f"   {day} DL minted {mi:,} - unreleased {un:,} - BSC의 'bsc: Tron' 몫 {bs:,} = {mi - un - bs:,}, DL circulating {ci:,}, 남는 차이 {ci - (mi - un - bs):,}")
tw = tbal(U("2022-05-11 23:59:59") * 1000); te = tbal(U("2022-05-18 00:00:00") * 1000)
mi0, mi1 = 42735602226.54486, 38735602226.54486
bs0, bs1 = 4479997922.17 - 1350000115, 4979997922.17 - 1350000115
print(f"   일관된 정의(지갑 잔액 빼기) 시작 {mi0 - tw - bs0:,.0f} 끝 {mi1 - te - bs1 - 4282510:,.0f}  변화 {(mi1 - te - bs1 - 4282510) - (mi0 - tw - bs0):,.0f}  (DL 변화 -7,428,088,402)")
d0 = 82690895711 - (39605604430 - (mi0 - tw - bs0)); d1 = 74235444120
print(f"   트론 시작값만 지갑 잔액 기준으로 바꾼 집계: {d0:,.0f} -> {d1:,} ({(d1 / d0 - 1) * 100:.2f}%)")
