#!/usr/bin/env python3
"""최악 7일 순감소율 원자료 대조 (DefiLlama 대 Etherscan).

사용: python3 -I check_7d.py fetch <PYUSD|USDP|USDT|USDC|small|probe>   Etherscan 호출, eth_raw/ 에 저장(있으면 건너뜀)
      python3 -I check_7d.py                                       계산, 화면 출력과 ../원자료대조.md 작성(호출 없음)
입력(읽기만): Claude웹_1차/data/raw/defillama_*.json.gz, eth_raw/*_mintburn_logs.json.gz (collect_eth.py 산출물)
Etherscan은 collect_eth.py 의 api()를 그대로 쓴다(V2, chainid=1, 무료 등급, 0.4초 간격, 키는 출력하지 않음).
eth_call은 과거 블록을 지정해도 최신 값을 돌려주므로 과거 공급량은 계약 생성부터의 이벤트를 모두 더해 구한다.
USDC는 기록이 수백만 건이라 최근 구간(수집 시점 totalSupply에서 거꾸로 뺌)과 collect_eth 대조 창(수준은 DefiLlama에 맞춤)만 쓴다.
"""
import bisect
import csv
import datetime as dt
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
RAW = OUT / "eth_raw"
DL = HERE.parents[1] / "Claude웹_1차" / "data" / "raw"
DLF = {"USDC": "USDC_2", "USDT": "USDT_1", "PYUSD": "PYUSD_120", "USDP": "USDP_11"}
ADDR = {"USDC": "0xA0b86991c6218b36c1d19D4a2e9eb0cE3606eB48", "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "PYUSD": "0x6c3ea9036406852006290770BEdFcAbA0e23A0e8", "USDP": "0x8E870D67F660D95d5be530380D0eC0bd388289E1"}
DEC = {"USDC": 6, "USDT": 6, "PYUSD": 6, "USDP": 18}
WIN = {"USDC": ("2023-03-10", "2023-03-17"), "USDT": ("2022-05-11", "2022-05-18"),
       "PYUSD": ("2024-02-27", "2024-03-05"), "USDP": ("2024-02-09", "2024-02-16")}  # 구조 문서 7일 구간
DOC = {"USDC": -15.17, "USDT": -10.23, "PYUSD": -33.17, "USDP": -38.97}  # 구조 문서 값(%)
# DefiLlama PYUSD 어댑터의 이더리움 unreleased 주소(첫 등록 6df6b948 2023-08-08부터 있었고 c7925306 2024-06-28에서 삭제)
PY_UNREL = ["0x264bd8291fae1d75db2c5f573b07faa6715997b5", "0xe25a329d385f77df5d4ed56265babe2b99a5436e"]
TR = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
USDT_EV = {"issue": "0xcb8241adb0c3fdb35b70c24ce35c5eb0c17af7431c99f827d44a445ca624176a",  # Issue(uint256)
           "redeem": "0x702d5967f45f6513a38ffc42d6ba9bf230bd40e8f53b16363c7eb4fd2deb9a44",  # Redeem(uint256)
           "dbf": "0x61e6e66b0d6339b2980aecc6ccc0039736791f0ccde9ed512e789a7fbdd698c6"}  # DestroyedBlackFunds(address,uint256)
USDT_INIT = 100_000_000_000  # 생성자 인자 _initialSupply(0x174876e800). 이벤트 없이 들어간 공급량
ZERO = "0x" + "0" * 64
DAY = 86400
USDC_RECENT_FROM = 26_082_465  # USDC 최근 확인 시작 블록(2026-09-29 무렵). DefiLlama 원응답 마지막 날(2026-10-05) 앞 엿새를 덮는다


def ts(d):
    return int(dt.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())


def utc(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def gz_load(p):
    with gzip.open(p, "rt") as f:
        return json.load(f)


def gz_save(p, obj):
    tmp = p.with_name(p.name + ".tmp")  # 중간에 끊겨도 반쯤 쓴 파일이 남지 않게
    with gzip.open(tmp, "wt") as f:
        json.dump(obj, f)
    tmp.replace(p)


def hx(x):
    return int(x, 16) if len(x) > 2 else 0  # Etherscan은 0을 "0x"로 줄 때가 있다


def compact(logs, word=0):
    """Etherscan 로그 -> [블록, 시각, logIndex, 금액(정수 문자열), from, to]. word는 data 안 금액 위치(32바이트 단위)."""
    out = []
    for l in logs:
        t = l["topics"]
        amt = int(l["data"][2 + 64 * word: 2 + 64 * (word + 1)], 16)
        f = "0x" + t[1][-40:] if len(t) > 1 else ("0x" + l["data"][26:66] if word else "")  # DestroyedBlackFunds는 data 첫 칸이 주소
        to = "0x" + t[2][-40:] if len(t) > 2 else ""
        out.append([hx(l["blockNumber"]), hx(l["timeStamp"]), hx(l["logIndex"]), str(amt), f, to])
    return out


# ---------- 수집 ----------
def scan(ce, addr, lo, hi, t0=TR, t1=None, t2=None):
    """getLogs를 블록 순서대로 이어 받는다. 1000건이 차면 마지막 블록 기록은 버리고 그 블록부터 다시 받는다.
    collect_eth.getlogs(반씩 나누기)는 1000건이 찬 응답을 버려 USDC처럼 기록이 많으면 호출이 몇 배로 늘어 이 방식을 쓴다."""
    p = dict(module="logs", action="getLogs", address=addr, toBlock=hi, topic0=t0, page=1, offset=1000)
    if t1:
        p.update(topic1=t1, topic0_1_opr="and")
    if t2:
        p.update(topic2=t2, topic0_2_opr="and")
    out, b = [], lo
    while b <= hi:
        r = ce.api(fromBlock=b, **p).get("result")
        if isinstance(r, str):
            if "No records" in r:
                break
            raise RuntimeError(f"getLogs {b}-{hi}: {r}")
        if len(r) < 1000:
            out += r
            break
        last = hx(r[-1]["blockNumber"])
        if last == b:
            raise RuntimeError(f"블록 {b} 하나에 기록 1000건 이상")
        out += [x for x in r if hx(x["blockNumber"]) < last]
        b = last
    return out


def fetch(c):
    sys.path.insert(0, str(HERE))
    import collect_eth as ce  # api(), ethcall(), blk() 재사용

    # USDC는 생성부터의 기록이 수백만 건이라 최근 구간만 받고, 수집 시점 totalSupply에서 거꾸로 빼서 공급량을 만든다
    p = RAW / (f"{c}_recent.json.gz" if c == "USDC" else f"{c}_lifetime.json.gz")
    if p.exists():
        print(c, "있음, 건너뜀", p.name)
    else:
        addr = ADDR[c]
        b0 = int(ce.api(module="proxy", action="eth_blockNumber")["result"], 16)
        supply = int(ce.ethcall(addr, "0x18160ddd"), 16)  # totalSupply(), latest
        b1 = int(ce.api(module="proxy", action="eth_blockNumber")["result"], 16)
        d = {"latest": {"block_before": b0, "block_after": b1, "totalSupply": str(supply)}, "logs": {}}
        if c == "USDC":
            lo = d["from_block"] = USDC_RECENT_FROM
        else:
            d["creation"] = ce.api(module="contract", action="getcontractcreation", contractaddresses=addr)["result"][0]
            lo = int(d["creation"]["blockNumber"])
        if c == "USDT":
            for k, t0 in USDT_EV.items():
                d["logs"][k] = compact(scan(ce, addr, lo, b1, t0), word=1 if k == "dbf" else 0)
        else:
            d["logs"]["mint"] = compact(scan(ce, addr, lo, b1, t1=ZERO))
            d["logs"]["burn"] = compact(scan(ce, addr, lo, b1, t2=ZERO))
        gz_save(p, d)
        print(c, "블록", lo, "~", b1, {k: len(v) for k, v in d["logs"].items()}, "호출", ce.ncalls[0], flush=True)
    if c == "PYUSD":
        q = RAW / "PYUSD_unreleased_addr_transfers.json.gz"
        if q.exists():
            print("PYUSD unreleased 주소 있음, 건너뜀")
            return
        lo = int(gz_load(p)["creation"]["blockNumber"])
        hi = gz_load(RAW / "PYUSD_mintburn_logs.json.gz")["blocks"][1]  # collect_eth 창 끝(2024-04-02)
        d = {"blocks": [lo, hi], "addrs": {}}
        for a in PY_UNREL:
            w = "0x" + "0" * 24 + a[2:]
            d["addrs"][a] = {"in": compact(scan(ce, ADDR[c], lo, hi, t2=w)), "out": compact(scan(ce, ADDR[c], lo, hi, t1=w))}
            print("PYUSD", a, {k: len(v) for k, v in d["addrs"][a].items()}, "호출", ce.ncalls[0], flush=True)
        gz_save(q, d)


# ---------- 계산 ----------
def g(x, k):
    return ((x or {}).get(k) or {}).get("peggedUSD")


def series(ev, base=0):
    """(시각, 블록, logIndex, 증감) 목록 -> (시각 목록, 그 시각 기록까지 더한 값 목록, 시작값)."""
    t, v, s = [], [], base
    for e in sorted(ev):
        s += e[3]
        if t and t[-1] == e[0]:
            v[-1] = s
        else:
            t.append(e[0])
            v.append(s)
    return t, v, base


def at(sr, T):
    """T 시각 직전 상태(블록 시각이 T보다 이른 기록만 더한 값)."""
    t, v, base = sr
    i = bisect.bisect_left(t, T)
    return v[i - 1] if i else base


def when(sr, target, T, dec, span=6 * 3600):
    """at(sr, T + s)가 target(DefiLlama 달러 정수)과 1달러 안으로 같은 s 구간 [(시작, 끝)) 목록. s는 T 기준 초, -span 이상 span 미만."""
    t, v, base = sr
    i = bisect.bisect_left(t, T - span)
    cur, start, out = (v[i - 1] if i else base), -span, []
    while i < len(t) and t[i] + 1 - T < span:
        end = t[i] + 1 - T  # t[i] 기록은 t[i] + 1초부터 반영된다(at 정의)
        if abs(cur / 10 ** dec - target) < 1:
            out.append((start, end))
        start, cur, i = end, v[i], i + 1
    if abs(cur / 10 ** dec - target) < 1:
        out.append((start, span))
    return out


def common_offset(ivs):
    """날짜별 구간 목록에서 가장 많은 날이 함께 들어가는 시각(00:00 UTC 기준 초, -1시간 ~ +2시간, 12초 간격). (날 수, 그 시각들)."""
    cnt = {s: sum(any(a <= s < b for a, b in iv) for iv in ivs) for s in range(-3600, 7200, 12)}
    top = max(cnt.values())
    return top, [s for s, k in cnt.items() if k == top]


def hm(sec):
    sign = "-" if sec < 0 else ""
    sec = abs(sec)
    return f"{sign}{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def clock(sec):
    """00:00 UTC 기준 초를 시각 글로. 음수는 전날 시각."""
    return hm(sec) if sec >= 0 else "전날 " + hm(DAY + sec)


def supply(c):
    """생성 블록부터 모든 발행, 소각을 더한 이더리움 공급량 계열(코인 최소 단위)."""
    d = gz_load(RAW / f"{c}_lifetime.json.gz")
    sign = {"mint": 1, "burn": -1, "issue": 1, "redeem": -1, "dbf": -1}
    ev = [(x[1], x[0], x[2], sign[k] * int(x[3])) for k, rows in d["logs"].items() for x in rows]
    return series(ev, USDT_INIT if c == "USDT" else 0), d


def usdc_window(eth):
    """USDC 대조 창 공급량 계열. collect_eth 창 안 건별 기록(시작값 0)에 DefiLlama minted에 맞춘 시작값을 더한다.
    시각 s(-1시간 ~ +2시간, 12초 간격)마다 날짜별 minted - 계열값을 달러로 반올림해, 1달러 안으로 모이는 날이 가장 많은 값과 그 s를 고른다.
    창 첫날은 앞 1시간이 창 밖이라 뺀다."""
    w = gz_load(RAW / "USDC_mintburn_logs.json.gz")
    sr0 = series([(hx(l["timeStamp"]), hx(l["blockNumber"]), hx(l["logIndex"]), s * int(l["data"], 16))
                  for k, s in (("mint", 1), ("burn", -1)) for l in w[k]])
    a, e = w["window_utc"]
    days = [dd for dd in sorted(eth) if a + 3600 <= ts(dd) and ts(dd) + 7200 <= e]
    best = (0, 0, 0)
    for s in range(-3600, 7200, 12):
        cnt = {}
        for dd in days:
            x = round(g(eth[dd], "minted") - at(sr0, ts(dd) + s) / 1e6)
            cnt[x] = cnt.get(x, 0) + 1
        base = max(cnt, key=cnt.get)
        k = sum(m for x, m in cnt.items() if abs(x - base) <= 1)
        if k > best[0]:
            best = (k, s, base)
    k, s, base = best
    t, v, _ = sr0
    return (t, [x + base * 10 ** 6 for x in v], base * 10 ** 6), {"days": len(days), "agree": k, "at": s, "base": base}


def usdc_recent(eth):
    """최근 구간 공급량 = 수집 시점 totalSupply - 그 뒤로 받은 발행, 소각. DefiLlama minted와 같아지는 시각을 날짜별로 찾는다."""
    r = gz_load(RAW / "USDC_recent.json.gz")
    assert r["latest"]["block_before"] == r["latest"]["block_after"]  # totalSupply를 읽은 블록이 기록 끝 블록과 같아야 거꾸로 뺄 수 있다
    ev = [(x[1], x[0], x[2], s * int(x[3])) for k, s in (("mint", 1), ("burn", -1)) for x in r["logs"][k]]
    sr = series(ev, int(r["latest"]["totalSupply"]) - sum(e[3] for e in ev))
    days = [dd for dd in sorted(eth) if ts(dd) - 6 * 3600 >= sr[0][0]]
    ivs = [(dd, when(sr, g(eth[dd], "minted"), ts(dd), 6)) for dd in days]
    cnt, offs = common_offset([iv for _, iv in ivs])
    return {"days": days, "ivs": ivs, "cnt": cnt, "offs": offs, "latest": r["latest"], "lo": r["from_block"],
            "counts": {k: len(v) for k, v in r["logs"].items()},
            "n00": sum(abs(g(eth[dd], "minted") - at(sr, ts(dd)) / 1e6) < 1 for dd in days),
            "per_day": len(ev) / ((sr[0][-1] - sr[0][0]) / DAY)}


def py_unrel():
    """PYUSD unreleased 두 주소 잔액 합 계열. 두 주소 사이 이체는 서로 지워진다."""
    d = gz_load(RAW / "PYUSD_unreleased_addr_transfers.json.gz")
    ev = [(x[1], x[0], x[2], s * int(x[3])) for a in d["addrs"].values() for k, s in (("in", 1), ("out", -1)) for x in a[k]]
    return series(ev), d


def defillama(c):
    d = gz_load(DL / f"defillama_{DLF[c]}.json.gz")
    assert all(x["date"] % DAY == 0 for x in d["tokens"] + d["chainBalances"]["Ethereum"]["tokens"])  # 날짜는 모두 00:00 UTC
    tot = {utc(x["date"])[:10]: g(x, "circulating") for x in d["tokens"]}
    ch = {k: {utc(x["date"])[:10]: x for x in v.get("tokens", [])} for k, v in d["chainBalances"].items()}
    return tot, ch


def rate(a, b):
    return (b / a - 1) * 100


def money(x, nd=2):
    return f"{x:,.{nd}f}"


def pp(x, nd=4):
    """%p 차이. 반올림해 0이면 부호를 떼고 0으로 쓴다."""
    t = f"{x:+.{nd}f}"
    return (t[1:] if float(t) == 0 else t) + "%p"


def selftest():
    sr = series([(10, 1, 0, 5), (10, 1, 1, -2), (20, 2, 0, 4)], base=100)
    assert sr == ([10, 20], [103, 107], 100)
    assert at(sr, 10) == 100 and at(sr, 11) == 103 and at(sr, 21) == 107
    # 값 103은 시각 11 ~ 20(at 기준). T=15 기준 s = -4 이상 6 미만
    assert when(sr, 103, 15, 0, span=30) == [(-4, 6)]
    assert all(at(sr, 15 + x) == 103 for x in range(-4, 6)) and at(sr, 15 - 5) == 100 and at(sr, 15 + 6) == 107
    assert common_offset([[(0, 60)], [(30, 90)], [(600, 700)]]) == (2, [36, 48])  # 30~59초가 두 날에 겹친다(12초 간격)
    assert hm(-150) == "-00:02:30" and hm(2460) == "00:41:00"
    assert pp(-0.00001) == "0.0000%p" and pp(8.214, 2) == "+8.21%p"
    assert clock(-144) == "전날 23:57:36" and clock(251) == "00:04:11"


def check(c):
    """코인 하나의 대조표 행과 본문용 값."""
    dec, (a, b) = DEC[c], WIN[c]
    Ta, Tb = ts(a), ts(b)
    per = f"{a} ~ {b[5:]}"
    tot, ch = defillama(c)
    eth = ch["Ethereum"]
    n = {}
    if c == "USDC":  # 생성부터 다시 더하지 않는다(usdc_window, usdc_recent 참고)
        sr, n["align"] = usdc_window(eth)
        n["recent"], life = usdc_recent(eth), {}
    else:
        sr, life = supply(c)
        lat = life["latest"]
        n["life"] = (sr[1][-1], int(lat["totalSupply"]), lat["block_before"], lat["block_after"],
                     int(life["creation"]["blockNumber"]), {k: len(v) for k, v in life["logs"].items()})
    n["sr"] = sr
    # DefiLlama 이더리움 minted 대 00:00 UTC 공급량: 전 기간(USDC 빼고), 수집 창(collect_eth 일별 CSV 날짜)
    full = [(dd, g(x, "minted") - at(sr, ts(dd)) / 10 ** dec) for dd, x in sorted(eth.items()) if g(x, "minted") is not None]
    rows_csv = list(csv.DictReader(open(OUT / "eth_out" / f"{c}_eth_daily.csv")))
    cdays = [r["date_utc"] for r in rows_csv]
    win = [(dd, df) for dd, df in full if cdays[0] <= dd <= cdays[-1]]
    if life:
        n["full"] = (len(full), sum(abs(df) < 1 for _, df in full), full[0][0], full[-1][0])
        years = {}
        for dd, df in full:
            if abs(df) >= 1:
                years[dd[:4]] = years.get(dd[:4], 0) + 1
        n["mis_years"] = years
    n["win"] = (len(win), sum(abs(df) < 1 for _, df in win), cdays[0], cdays[-1])
    n["per_day"] = sum(int(r["mint_n"]) + int(r["burn_n"]) for r in rows_csv) / len(rows_csv)
    col = "net_issue_redeem" if c == "USDT" else "net"
    n["csv_sum"] = csv_sum = sum(float(r[col]) for r in rows_csv if a <= r["date_utc"] < b)
    Sa, Sb = at(sr, Ta) / 10 ** dec, at(sr, Tb) / 10 ** dec
    Ma, Mb = g(eth[a], "minted"), g(eth[b], "minted")
    Ca, Cb = g(eth[a], "circulating"), g(eth[b], "circulating")
    n.update(Sa=Sa, Sb=Sb, Ma=Ma, Mb=Mb, Ca=Ca, Cb=Cb, Aa=tot[a], Ab=tot[b])
    n["chain_sum"] = {dd: sum(g(v.get(dd), "circulating") or 0 for v in ch.values()) for dd in (a, b)}
    n["first"] = {k: min(dd for dd, x in v.items() if (g(x, "circulating") or 0) > 0)
                  for k, v in ch.items() if any((g(x, "circulating") or 0) > 0 for x in v.values())}
    n["ch"], n["tot"] = ch, tot
    n["wev"] = sorted((x[1], k, int(x[3])) for k, v in life.get("logs", {}).items() for x in v if Ta <= x[1] < Tb)
    amt = lambda d: "일치" if abs(d) < 1 else "차이 있음"
    pct = lambda x, y: "일치" if f"{x:.2f}" == f"{y:.2f}" else "차이 있음"
    R = []
    supply_rows = [(c, "이더리움 공급량 7일 변화량(00:00 UTC 기준)", per, money(Mb - Ma, 0), money(Sb - Sa),
                    money(Sb - Sa - (Mb - Ma)), amt(Sb - Sa - (Mb - Ma))),
                   (c, "이더리움 공급량 7일 감소율(00:00 UTC 기준)", per, f"{rate(Ma, Mb):+.2f}%", f"{rate(Sa, Sb):+.2f}%",
                    pp(rate(Sa, Sb) - rate(Ma, Mb)), pct(rate(Ma, Mb), rate(Sa, Sb)))]
    if c in ("PYUSD", "USDP"):
        R.append((c, "7일 감소율: 이더리움 순변화(발행 - 소각) 기준", per, f"{DOC[c]:+.2f}% (구조 문서)",
                  f"{rate(Sa, Sb):+.2f}%", pp(rate(Sa, Sb) - DOC[c], 2), pct(DOC[c], rate(Sa, Sb))))
    else:
        R.append((c, "7일 감소율: 전체 체인 유통량", per, f"{DOC[c]:+.2f}% (구조 문서)", "이더리움 밖 체인은 받지 않음", "-", "대조 불가"))
    if c == "PYUSD":
        ur, ud = py_unrel()
        ivs = [(dd, when(ur, g(eth[dd], "unreleased"), ts(dd), 6)) for dd in cdays if g(eth.get(dd), "unreleased") is not None]
        cnt, offs = common_offset([iv for _, iv in ivs])
        off = offs[0]
        Ua, Ub = at(ur, Ta) / 1e6, at(ur, Tb) / 1e6
        sa2, sb2, ua2, ub2 = (at(x, T + off) / 1e6 for x, T in ((sr, Ta), (sr, Tb), (ur, Ta), (ur, Tb)))
        nu = len({(x[0], x[2]) for v in ud["addrs"].values() for k in ("in", "out") for x in v[k]
                  if ts(cdays[0]) <= x[1] < ts(cdays[-1]) + DAY})  # 두 주소가 낀 이체 건수(두 주소 사이 이체는 한 건)
        n.update(Ua=Ua, Ub=Ub, DUa=g(eth[a], "unreleased"), DUb=g(eth[b], "unreleased"), off=off, offs=offs, cnt=cnt, ivs=ivs,
                 u_per_day=nu / len(cdays), sa2=sa2, sb2=sb2, ua2=ua2, ub2=ub2, ublocks=ud["blocks"],
                 ucount={k: {kk: len(vv) for kk, vv in v.items()} for k, v in ud["addrs"].items()})
        R.append((c, "7일 감소율: DefiLlama와 같은 정의(공급량 - unreleased 두 주소 잔액), 00:00 UTC 기준", per, f"{DOC[c]:+.2f}% (구조 문서)",
                  f"{rate(Sa - Ua, Sb - Ub):+.2f}%", pp(rate(Sa - Ua, Sb - Ub) - DOC[c]), pct(DOC[c], rate(Sa - Ua, Sb - Ub))))
        R.append((c, f"같은 정의, DefiLlama 기록 시각({hm(off)} UTC, 아래 2 참고) 기준", per, f"{rate(tot[a], tot[b]):+.4f}%",
                  f"{rate(sa2 - ua2, sb2 - ub2):+.4f}%", pp(rate(sa2 - ua2, sb2 - ub2) - rate(tot[a], tot[b])),
                  pct(rate(tot[a], tot[b]), rate(sa2 - ua2, sb2 - ub2))))
        du = g(eth[b], "unreleased") - g(eth[a], "unreleased")
        R.append((c, f"unreleased 두 주소 잔액 7일 변화량(기록 시각 {hm(off)} UTC 기준)", per, money(du, 0), money(ub2 - ua2),
                  money(ub2 - ua2 - du), amt(ub2 - ua2 - du)))
        R += supply_rows
    elif c == "USDT":
        dbf, rdm, iss = ([x for x in life["logs"][k] if Ta <= x[1] < Tb] for k in ("dbf", "redeem", "issue"))
        n.update(dbf=dbf, rdm=rdm, iss=iss, tz=compact(gz_load(RAW / "USDT_mintburn_logs.json.gz")["burn"]))
        R.append((c, "이더리움 공급량 7일 변화량(Issue - Redeem만, 수집 보고 일별 CSV)", per, money(Mb - Ma, 0), money(csv_sum),
                  money(csv_sum - (Mb - Ma)), amt(csv_sum - (Mb - Ma))))
        R.append((c, "이더리움 공급량 7일 변화량(DestroyedBlackFunds 포함, 00:00 UTC 기준)", *supply_rows[0][2:]))
        R.append(supply_rows[1])
    elif c == "USDC":
        ivs = [(dd, when(sr, g(eth[dd], "minted"), ts(dd), dec)) for dd in cdays[1:] if dd in eth]  # 첫날은 6시간 앞이 창 밖이라 뺀다
        cnt, offs = common_offset([iv for _, iv in ivs])
        off = offs[0]
        xa, xb = at(sr, Ta + off) / 1e6, at(sr, Tb + off) / 1e6
        n.update(ivs=ivs, cnt=cnt, off=off, offs=offs, xa=xa, xb=xb)
        R.append(supply_rows[0])
        R.append((c, f"이더리움 공급량 7일 변화량(DefiLlama 기록 시각 {hm(off)} UTC 기준, 아래 2 참고)", per, money(Mb - Ma, 0), money(xb - xa),
                  money(xb - xa - (Mb - Ma)), amt(xb - xa - (Mb - Ma))))
        R.append(supply_rows[1])
        R.append((c, f"이더리움 공급량 7일 감소율(기록 시각 {hm(off)} UTC 기준)", per, f"{rate(Ma, Mb):+.4f}%", f"{rate(xa, xb):+.4f}%",
                  pp(rate(xa, xb) - rate(Ma, Mb)), pct(rate(Ma, Mb), rate(xa, xb))))
    else:
        R += supply_rows
    if c in ("USDC", "USDT"):
        R.append((c, "이더리움 유통량(DefiLlama circulating) 7일 감소율", per, f"{rate(Ca, Cb):+.2f}%",
                  "발행, 소각만으로는 만들 수 없음(아래 설명)", "-", "대조 불가"))
    return R, n


def main():
    selftest()
    rows, N = [], {}
    for c in ("PYUSD", "USDP", "USDC", "USDT"):
        r, N[c] = check(c)
        rows += r
    report(rows, N)


def report(rows, N):
    P, U, C, T = N["PYUSD"], N["USDP"], N["USDC"], N["USDT"]
    L = []
    o = L.append
    life_txt = []
    for c in ("PYUSD", "USDP", "USDT"):
        s, latest, b0, b1, cb, cnt = N[c]["life"]
        ok = "같다" if s == latest and b0 == b1 else f"다르다(차이 {s - latest} 최소 단위, 블록 {b0}, {b1})"
        names = {"mint": "발행", "burn": "소각", "issue": "Issue", "redeem": "Redeem", "dbf": "DestroyedBlackFunds"}
        life_txt.append(f"{c}(블록 {cb:,} ~ {b1:,}, " + ", ".join(f"{names[k]} {v:,}건" for k, v in cnt.items()) + f") {ok}")
    full_txt = ", ".join(f"{c} {N[c]['full'][0]:,}일 중 {N[c]['full'][1]:,}일" for c in ("PYUSD", "USDP", "USDT"))
    R_, A_ = C["recent"], C["align"]
    near = [[(x, y) for x, y in iv if -3600 <= x and y <= 7200] for _, iv in R_["ivs"]]
    r_all = all(near)
    r_lo, r_hi = min(x for iv in near for x, _ in iv), max(y - 1 for iv in near for _, y in iv)
    win_txt = ", ".join(f"{c} {N[c]['win'][0]}일 중 {N[c]['win'][1]}일({N[c]['win'][2]} ~ {N[c]['win'][3]})" for c in ("PYUSD", "USDP", "USDC", "USDT"))
    a, b = WIN["USDC"]
    pick = lambda iv, off: min(iv, key=lambda r: 0 if r[0] <= off < r[1] else min(abs(r[0] - off), abs(r[1] - off)))
    span_txt = lambda iv, off: (lambda r: f"{clock(r[0])}~{clock(r[1] - 1)}")(pick(iv, off)) if iv else "6시간 안에 없음"
    usdc_rec = ", ".join(f"{dd} {span_txt(iv, C['off'])}" for dd, iv in C["ivs"] if dd in (a, b))
    usdc_off_miss = [(dd, iv) for dd, iv in C["ivs"] if not any(x <= C["off"] < y for x, y in iv)]
    py_off_miss = [(dd, iv) for dd, iv in P["ivs"] if not any(x <= P["off"] < y for x, y in iv)]
    miss_txt = lambda xs, off: " (예외 " + ", ".join(f"{dd} {span_txt(iv, off)}" for dd, iv in xs) + ")" if xs else ""
    offs_txt = lambda n: clock(n["offs"][0]) if len(n["offs"]) == 1 else f"{clock(n['offs'][0])}~{clock(n['offs'][-1])}"
    ivs_txt = lambda n: f"{n['ivs'][0][0]} ~ {n['ivs'][-1][0]} {len(n['ivs'])}일"
    # 결론 문장이 표와 어긋나지 않게 판정을 확인한다
    assert all(r[6] == "일치" for r in rows if r[0] == "PYUSD" and "같은 정의" in r[1])
    assert all(r[6] == "일치" for r in rows if r[0] == "USDP")
    assert all(r[6] == "일치" for r in rows if r[0] == "USDC" and "기록 시각" in r[1])
    assert all(r[6] == "일치" for r in rows if r[0] == "USDT" and "DestroyedBlackFunds 포함" in r[1])
    assert all(N[c]["win"][0] == N[c]["win"][1] for c in ("PYUSD", "USDP", "USDT"))
    ta, tb = WIN["USDT"]
    tch = T["ch"]
    new_ch = sorted(((k, min(v)) for k, v in tch.items() if ta not in v and tb in v), key=lambda x: x[1])
    new_first = sorted({d for _, d in new_ch})
    new_sum = {k: g(tch[k][d], "circulating") or 0 for k, d in new_ch}
    big = sorted(new_sum.items(), key=lambda x: -x[1])[:2]
    bsc = U["ch"]["BSC"]
    d1 = utc(ts(ta) + DAY)[:10]
    allo = P["offs"] + C["offs"]
    rec = "~".join(dict.fromkeys((hm(min(allo))[:5], hm(max(allo))[:5])))
    ua, ub = WIN["USDP"]

    o("# 최악 7일 순감소율 원자료 대조 (2026-10-10)")
    o("")
    o("구조 문서(`Claude웹_1차/00_중간저장_2026-10-06.md` 3절)의 최악 7일 순감소율 4개를 Etherscan 이더리움 발행, 소각 기록과 맞춰 본 결과다. "
      "계산은 `scripts/check_7d.py`, 숫자는 DefiLlama 원응답(`Claude웹_1차/data/raw/`)과 Etherscan 원응답(`eth_raw/`)에서만 가져왔다.")
    o("")
    o("## 결론")
    o("")
    o(f"PYUSD({DOC['PYUSD']:.2f}%)와 USDP({DOC['USDP']:.2f}%)는 Etherscan 기록으로 같은 값이 다시 나와 '검증 전'을 뗄 수 있고"
      f"(PYUSD는 DefiLlama 유통량 정의 기준이며 발행과 소각만 보면 {rate(P['Sa'], P['Sb']):.2f}%), "
      f"USDC({DOC['USDC']:.2f}%)와 USDT({DOC['USDT']:.2f}%)는 이더리움 몫만 맞았고 전체 체인 값은 대조하지 못해 '검증 전'을 유지해야 한다.")
    o("")
    o("## 대조표")
    o("")
    o("기간 a ~ b는 DefiLlama 날짜 a 값과 날짜 b 값을 비교한 7일이다. Etherscan 값은 a일 00:00 UTC부터 b일 00:00 UTC 직전까지의 기록으로 쟀고, "
      "'기록 시각 기준' 행만 DefiLlama가 실제로 값을 기록한 시각(아래 2)에 맞춰 쟀다. 금액 단위는 달러(코인 단위). "
      "판정: 금액은 차이가 1달러 미만이면 일치(DefiLlama 값은 달러 정수), 비율은 구조 문서처럼 소수 둘째 자리까지 같으면 일치.")
    o("")
    o("| 코인 | 항목 | 기간 | DefiLlama 값 | Etherscan 값 | 차이 | 판정 |")
    o("|---|---|---|---|---|---|---|")
    for r in rows:
        o("| " + " | ".join(r) + " |")
    o("")
    o("## 확인한 내용")
    o("")
    o("### 1. Etherscan 공급량을 다시 만든 방법")
    o("")
    pr = gz_load(RAW / "eth_call_probe.json.gz")
    same = sum(x["value"] == pr[c]["latest"] for c in pr for x in pr[c]["past"])
    npast = sum(len(pr[c]["past"]) for c in pr)
    differ = sum(x["value"] != str(at(N[c]["sr"], ts(x["date"])))  for c in pr for x in pr[c]["past"])
    o(f"- Etherscan `eth_call`은 과거 블록 번호를 줘도 최신 값을 돌려준다. 코인마다 7일 구간 두 끝 블록({npast}곳)에 totalSupply를 물었더니 "
      f"{same}곳이 같은 조회의 최신 값과 같았고, {differ}곳이 그 시점 실제 공급량(아래 방법으로 다시 만든 값)과 달랐다(`eth_raw/eth_call_probe.json.gz`). "
      "그래서 PYUSD, USDP, USDT의 과거 시점 공급량은 계약 생성 블록부터 수집 시점까지 공급량을 바꾸는 기록을 모두 받아 더해서 구했다(USDC는 아래 따로).")
    o("- 발행, 소각 기준: PYUSD, USDP, USDC는 Transfer 이벤트 가운데 from 또는 to가 0 주소인 것, "
      "USDT는 Transfer가 아니라 Issue, Redeem, DestroyedBlackFunds 이벤트와 생성자 초기 공급 100,000 USDT(`_initialSupply` 0x174876e800).")
    o("- 다 더한 값과 수집 시점(2026-10-10) `totalSupply()`를 최소 단위까지 비교하면 " + "; ".join(life_txt) + ".")
    o(f"- USDC는 하루 발행, 소각이 수천 건(최근 구간 하루 평균 {R_['per_day']:,.0f}건)이라 생성부터 다시 더하지 않고 두 가지로 확인했다. "
      f"(1) 최근 구간: 블록 {R_['lo']:,}부터 수집 시점 블록 {R_['latest']['block_after']:,}까지 발행 {R_['counts']['mint']:,}건, 소각 {R_['counts']['burn']:,}건을 받아 "
      f"수집 시점 totalSupply에서 거꾸로 빼서 공급량을 만들었다(`eth_raw/USDC_recent.json.gz`). DefiLlama 원응답의 {R_['days'][0]} ~ {R_['days'][-1]} "
      f"{len(R_['days'])}일{' 모두' if r_all else ' 가운데 일부'} 이더리움 minted가 {clock(r_lo)}~{clock(r_hi)} UTC 사이 한 시점의 공급량과 1달러 안으로 같다"
      f"(하루 기록이 많아 00:00 UTC로는 {R_['n00']}일). 수준까지 Etherscan 값으로 만든 공급량이 DefiLlama minted와 맞는다는 뜻이다. "
      f"(2) 대조 창: 수집 보고 원응답(`eth_raw/USDC_mintburn_logs.json.gz`)의 건별 기록으로 변화량을 쟀고, 공급량 수준(감소율의 분모)은 DefiLlama minted에 맞췄다. "
      f"{A_['days']}일 중 {A_['agree']}일이 {clock(A_['at'])} UTC에서 하나의 시작값으로 맞는다. 그래서 USDC 표의 감소율은 변화량만 Etherscan 값이고 분모는 DefiLlama 수준이다.")
    o("- USDT 계약 소스(TetherToken, Etherscan 검증 소스)에서 `_totalSupply`를 바꾸는 곳은 생성자, `issue`, `redeem`, `destroyBlackFunds` 네 곳이고 "
      "어느 곳도 Transfer 이벤트를 내지 않는다(세 함수는 각각 Issue, Redeem, DestroyedBlackFunds만 낸다). "
      "`transfer`는 받는 주소가 0이어도 막지 않고 공급량도 줄이지 않는다.")
    o("")
    o("### 2. 날짜 경계와 소수 자리")
    o("")
    o("- DefiLlama 날짜는 모두 00:00 UTC 타임스탬프다. 날짜 D의 DefiLlama 이더리움 minted와 D일 00:00 UTC 공급량이 1달러 안으로 같은 날은 "
      f"전 기간으로 {full_txt}이다.")
    mis = {c: N[c]["mis_years"] for c in ("PYUSD", "USDP", "USDT")}
    assert all(WIN[c][0][:4] not in y for c, y in mis.items())  # 아래 문장: 다른 날은 모두 7일 구간과 다른 해
    o("- 1달러 넘게 다른 날은 " + ", ".join(f"{c} " + ", ".join(f"{y}년 {k}일" for y, k in sorted(v.items())) for c, v in mis.items())
      + "로 모두 7일 구간과 다른 해다. USDC는 생성부터 다시 더하지 않아 전 기간 비교가 없다.")
    o(f"- 수집 보고 대조 창 안에서는 {win_txt}이다.")
    o(f"- 실제 기록 시각은 00:00이 아니다. DefiLlama 값과 같아지는 시각을 하루씩 찾아 여러 날이 겹치는 시각을 골랐다. "
      f"PYUSD unreleased 두 주소는 하루 평균 {P['u_per_day']:.0f}건 이체가 있어 시각을 가려낼 수 있는데, {ivs_txt(P)} 중 "
      f"{P['cnt']}일의 DefiLlama 값이 {offs_txt(P)} UTC 잔액과 같다{miss_txt(py_off_miss, P['off'])}. "
      f"USDC 대조 창(하루 평균 발행, 소각 {C['per_day']:.0f}건, 공급량 수준은 DefiLlama에 맞춘 계열)도 {ivs_txt(C)} 중 {C['cnt']}일이 "
      f"{offs_txt(C)} UTC 값과 같다{miss_txt(usdc_off_miss, C['off'])}. 반면 USDC 최근 구간({R_['days'][0]} ~ {R_['days'][-1]})은 "
      f"{clock(r_lo)}~{clock(r_hi)} UTC 사이에서 맞아 기록 시각이 시기마다 다르다.")
    o(f"- 그래서 2023~2024년 대조 구간의 DefiLlama 날짜 D 값은 D일 {rec} UTC 무렵 체인 상태로 보는 것이 맞다(USDT 2022년 구간은 발행, 소각이 드물어 시각을 가려낼 수 없다). "
      "수집 보고 일별 CSV(00:00 UTC 경계)와는 그 사이 발행, 소각만큼 어긋난다. "
      f"PYUSD, USDP, USDT는 하루 평균 발행, 소각이 {P['per_day']:.1f}건, {U['per_day']:.1f}건, {T['per_day']:.1f}건이라 대조 창 안 모든 날이 00:00 기준으로도 같고, "
      f"USDC는 {C['win'][0]}일 중 {C['win'][0] - C['win'][1]}일이 어긋난다.")
    o("- 소수 자리: DefiLlama 값은 달러 정수라 1달러 미만 차이는 소수 자리 차이로 본다. decimals는 USDC, USDT, PYUSD 6, USDP 18이며 수집 보고 CSV와 같다.")
    o("")
    o("### 3. PYUSD")
    o("")
    o(f"- 2024-02~03에는 DefiLlama에 이더리움 기록만 있다(다른 체인 첫 기록은 Solana {P['first'].get('Solana')}). 그래서 전체 체인 값이 이더리움 값과 같다"
      f"({WIN['PYUSD'][0]} {P['Aa']:,}, {WIN['PYUSD'][1]} {P['Ab']:,}).")
    o("- DefiLlama 유통량 = minted - unreleased. unreleased는 DefiLlama 어댑터(GitHub DefiLlama/peggedassets-server `src/adapters/peggedAssets/paypal-usd/index.ts`)에 "
      f"첫 등록(2023-08-08 커밋 6df6b948)부터 적혀 있던 두 주소 잔액 합이다: `{PY_UNREL[0]}`(주석 없음), `{PY_UNREL[1]}`(주석 paxosTreasury). "
      "이 목록은 2024-06-28 커밋 c7925306에서 빠졌고 DefiLlama unreleased 값도 2024-06-28이 마지막이다.")
    o(f"- 두 주소의 PYUSD 이체를 생성 블록부터 {P['ublocks'][1]:,} 블록(2024-04-02)까지 받아 잔액을 다시 만들었다("
      + ", ".join(f"{k[:10]}... 들어옴 {v['in']:,}건, 나감 {v['out']:,}건" for k, v in P["ucount"].items()) + "). "
      f"00:00 UTC 잔액 합은 {WIN['PYUSD'][0]} {money(P['Ua'])}, {WIN['PYUSD'][1]} {money(P['Ub'])}(DefiLlama {P['DUa']:,}, {P['DUb']:,}), "
      f"{hm(P['off'])} UTC 잔액 합은 {money(P['ua2'])}, {money(P['ub2'])}로 DefiLlama 값과 같다.")
    o(f"- 정리하면 {DOC['PYUSD']:.2f}%는 공급량 감소 {money(P['Sb'] - P['Sa'])}({rate(P['Sa'], P['Sb']):.2f}%)에 unreleased 증가 {P['DUb'] - P['DUa']:+,}가 더해진 값이다. "
      "DefiLlama가 unreleased(아직 시장에 풀리지 않은 양)로 지정한 두 주소 잔액을 유통량에서 빼는 정의라서, 이 7일 동안 두 주소 잔액이 늘어난 만큼 "
      f"유통량 감소폭이 공급량 감소폭보다 커졌다. 이더리움 순변화(발행 - 소각)만 보면 {rate(P['Sa'], P['Sb']):.2f}%다.")
    o("- 수집 보고가 '소각 주소'로 본 `0xe25a...`는 이 unreleased 두 주소 가운데 하나다.")
    o("")
    o("### 4. USDP")
    o("")
    o(f"- DefiLlama 전체 체인 값은 이더리움 minted와 같다({ua} {U['Aa']:,}, {ub} {U['Ab']:,}). 이더리움 circulating({U['Ca']:,})은 minted에서 "
      f"BSC로 건너간 {g(bsc[ua], 'circulating'):,}를 뺀 값이고 BSC 몫이 다시 더해진다. BSC 몫은 {ua}와 {ub}에 모두 {g(bsc[ub], 'circulating'):,}라 7일 변화에 영향이 없다. unreleased 값은 없다.")
    uk = {k: [x for x in U["wev"] if x[1] == k] for k in ("mint", "burn")}
    o(f"- 7일 동안 소각 {len(uk['burn'])}건(" + ", ".join(f"{utc(t)[5:10]} {money(v / 1e18)}" for t, _, v in uk["burn"])
      + f"), 발행 {len(uk['mint'])}건. 합 {money(U['Sb'] - U['Sa'])}.")
    o("")
    o("### 5. USDC")
    o("")
    o(f"- 대조할 수 있는 것은 이더리움 몫뿐이다. {a} 이더리움 circulating은 전체의 {C['Ca'] / C['Aa'] * 100:.1f}%, 7일 감소분의 "
      f"{(C['Cb'] - C['Ca']) / (C['Ab'] - C['Aa']) * 100:.1f}%다. DefiLlama 전체 합과 체인별 기록 합의 차이는 "
      f"{C['Aa'] - C['chain_sum'][a]:,}({a}), {C['Ab'] - C['chain_sum'][b]:,}({b})로 작다.")
    o(f"- 00:00 UTC 경계로 잰 7일 순변화(수집 보고 일별 CSV 합과 같다)와 DefiLlama minted 변화를 비교하면 {money(C['Sb'] - C['Sa'])} 대 "
      f"{C['Mb'] - C['Ma']:,}, 차이 {money(C['Sb'] - C['Sa'] - (C['Mb'] - C['Ma']))}이다.")
    assert abs(C["csv_sum"] - (C["Sb"] - C["Sa"])) < 0.01
    o(f"- 원인은 날짜 경계다. 두 끝날 DefiLlama 값과 같아지는 시각은 {usdc_rec} UTC이고, {hm(C['off'])} UTC로 다시 재면 "
      f"{money(C['xb'] - C['xa'])}로 차이가 {money(C['xb'] - C['xa'] - (C['Mb'] - C['Ma']))}다.")
    o(f"- 이더리움 circulating 7일 감소율({rate(C['Ca'], C['Cb']):.2f}%)은 minted에서 unreleased(발행사 보관분)와 다른 체인으로 건너간 몫을 뺀 값이다"
      f"({a} minted {C['Ma']:,}, circulating {C['Ca']:,}). 그 주소들 잔액은 받지 않아 대조하지 않았다.")
    o("")
    o("### 6. USDT")
    o("")
    o(f"- 대조할 수 있는 것은 이더리움 몫뿐이다. {ta} 이더리움 circulating은 전체의 {T['Ca'] / T['Aa'] * 100:.1f}%, 7일 감소분의 "
      f"{(T['Cb'] - T['Ca']) / (T['Ab'] - T['Aa']) * 100:.1f}%다.")
    o("- 7일 동안 이더리움 공급량을 바꾼 기록: "
      + ", ".join(f"Redeem {money(int(x[3]) / 1e6)}({utc(x[1])} UTC)" for x in T["rdm"]) + ", "
      + ", ".join(f"DestroyedBlackFunds {money(int(x[3]) / 1e6)}({utc(x[1])} UTC, `{x[4]}`)" for x in T["dbf"])
      + f", Issue {len(T['iss'])}건.")
    o(f"- 수집 보고 일별 CSV는 Issue - Redeem만 세서 DestroyedBlackFunds 2건({money(sum(int(x[3]) for x in T['dbf']) / 1e6)})이 빠졌다. 넣으면 DefiLlama minted 변화와 1달러 안으로 같다.")
    o(f"- 수집 보고의 Transfer to 0 주소 {len(T['tz'])}건(합 {money(sum(int(x[3]) for x in T['tz']) / 1e6)})은 소각이 아니다. 위 계약 소스대로 공급량이 줄지 않고, "
      "이 건을 빼고 더한 공급량이 오늘 totalSupply와 같으며, 그날 DefiLlama minted도 줄지 않았다. 날짜는 "
      + ", ".join(sorted({utc(x[1])[:10] for x in T["tz"]})) + "로 모두 7일 구간 밖이다.")
    o(f"- DefiLlama 전체 체인 값의 경계 문제: {ta} 전체 합 {T['Aa']:,}은 체인별 기록 합 {T['chain_sum'][ta]:,}보다 {T['Aa'] - T['chain_sum'][ta]:,} 크고, "
      f"{', '.join(new_first)}부터 {len(new_ch)}개 체인 기록이 새로 시작된다(" + ", ".join(f"{k} {v:,}" for k, v in big) + " 등). "
      f"7일 구간 시작일이 이 경계 바로 전날이라 {DOC['USDT']:.2f}%는 DefiLlama 체인별 기록으로도 다시 맞출 수 없다. "
      f"구조 문서 계산 출력의 USDT 1일 최악({ta} ~ {d1[5:]}, {rate(T['tot'][ta], T['tot'][d1]):.2f}%)도 같은 경계에 걸린다.")
    o("")
    o("## 바뀔 것")
    o("")
    o("| 산출물 | 위치 | 지금 | 바꿀 것 |")
    o("|---|---|---|---|")
    o(f"| 구조 문서 | `Claude웹_1차/00_중간저장_2026-10-06.md` 3절 최악 순감소율 표 | 4개 코인 모두 '검증 전' | "
      f"PYUSD {DOC['PYUSD']:.2f}%, USDP {DOC['USDP']:.2f}% 7일 값은 '검증 전'을 뗀다. PYUSD에는 'DefiLlama 유통량(unreleased 차감) 기준, "
      f"발행과 소각만 보면 {rate(P['Sa'], P['Sb']):.2f}%'를 붙인다. USDC, USDT는 '검증 전'을 두고 '이더리움 몫만 Etherscan과 일치'를 붙인다 |")
    o("| 구조 문서 | 같은 절 첫 문단 | '유통량은 발행에서 상환을 뺀 순변화이고 체인 합계다' | "
      f"'DefiLlama circulating(발행량에서 unreleased와 다른 체인으로 건너간 몫을 뺀 값)의 체인 합계다'. PYUSD 7일 값은 unreleased 차감 때문에 순변화 기준과 "
      f"{abs(DOC['PYUSD'] - rate(P['Sa'], P['Sb'])):.2f}%p 다르다 |")
    o(f"| 구조 문서 | 같은 표 USDT 행 | {DOC['USDT']:.2f}% 설명 없음 | 7일 구간 시작일({ta})이 DefiLlama 체인별 기록이 새로 생기기 전날이라 전체 합 기준이 바뀌는 경계에 걸린다는 주석 |")
    o("| 수집 보고 일별 CSV | `eth_out/USDT_eth_daily.csv` | net_issue_redeem이 Issue - Redeem만 셈 | DestroyedBlackFunds를 빼야 공급량 변화와 맞는다(이 문서 계산은 `eth_raw/USDT_lifetime.json.gz` 사용) |")
    o("")
    o("## 수집 보고와 다른 점")
    o("")
    o("- USDT `owner()`를 기간 시작과 끝 블록에서 조회해 같았다는 확인은, `eth_call`이 과거 블록을 무시하므로 실제로는 최신 값을 두 번 본 것이다.")
    o("- USDT Transfer to 0 주소 7건은 DestroyedBlackFunds가 아니다(DestroyedBlackFunds는 Transfer를 내지 않는다). 기간 안 DestroyedBlackFunds는 따로 2건 있다.")
    o(f"- USDT 일별 CSV의 net_issue_redeem은 DestroyedBlackFunds를 빼서 " + ", ".join(sorted({utc(x[1])[:10] for x in T["dbf"]}))
      + f" 하루가 {money(sum(int(x[3]) for x in T['dbf']) / 1e6)} 어긋난다.")
    o("")
    o("## 못 구한 것, 하지 않은 것")
    o("")
    o("- USDC, USDT의 이더리움 밖 체인 발행, 소각은 받지 않았다. 그래서 전체 체인 7일 감소율은 대조하지 못했다.")
    o("- USDC, USDT 이더리움 circulating에 쓰이는 unreleased 주소와 브리지 주소 잔액은 받지 않았다.")
    o(f"- DefiLlama 기록 시각이 왜 시기마다 다른지(이번 대조 구간 {rec} UTC 무렵, 2026-10 USDC {clock(r_lo)}~{clock(r_hi)} UTC)는 확인하지 않았다. "
      "기록 시각은 값이 맞아떨어지는 시각으로 찾은 것이다.")
    o("- 구조 문서의 30일 값은 대조하지 않았다.")
    o("- PYUSD, USDP 낙폭이 상환 쏠림인지 고객 한 곳의 정리인지는 이 문서에서 다루지 않았다.")
    o("")
    o("## 파일")
    o("")
    o("- `scripts/check_7d.py`: `python3 -I check_7d.py fetch <코인|small|probe>`은 Etherscan 수집, 인자 없이 실행하면 이 문서를 다시 쓴다(호출 없음).")
    o("- `eth_raw/{PYUSD,USDP,USDT}_lifetime.json.gz`: 계약 생성부터 공급량을 바꾼 기록 전부와 수집 시점 totalSupply.")
    o("- `eth_raw/USDC_recent.json.gz`: USDC 최근 구간(블록 26,082,465부터 수집 시점까지) 발행, 소각 기록과 수집 시점 totalSupply.")
    o("- `eth_raw/PYUSD_unreleased_addr_transfers.json.gz`: PYUSD unreleased 두 주소의 이체 기록(생성부터 2024-04-02).")
    o("- `eth_raw/eth_call_probe.json.gz`: 과거 블록을 지정한 `eth_call` 결과와 같은 때의 최신 값.")
    text = "\n".join(L) + "\n"
    for bad in ("·", "완벽", "유일", "최대", "보장"):
        assert bad not in text, bad
    (OUT / "원자료대조.md").write_text(text, encoding="utf-8")
    print(text)


def probe():
    """eth_call에 과거 블록 번호를 줬을 때 무엇이 오는지 확인(7일 구간 두 끝 블록과 최신)."""
    sys.path.insert(0, str(HERE))
    import collect_eth as ce

    out = {}
    for c, (a, b) in WIN.items():
        past = []
        for d in (a, b):
            blk = ce.blk(ts(d) - 1, "before")  # d일 00:00 UTC 직전 마지막 블록
            past.append({"date": d, "block": blk, "value": str(int(ce.ethcall(ADDR[c], "0x18160ddd", hex(blk)), 16))})
        out[c] = {"past": past, "latest": str(int(ce.ethcall(ADDR[c], "0x18160ddd"), 16))}
        print(c, out[c], flush=True)
    gz_save(RAW / "eth_call_probe.json.gz", out)


if __name__ == "__main__":
    if sys.argv[1:2] == ["fetch"]:
        if sys.argv[2] == "probe":
            probe()
        for c in {"small": ["PYUSD", "USDP", "USDT"], "probe": []}.get(sys.argv[2], [sys.argv[2]]):
            fetch(c)
    else:
        main()
