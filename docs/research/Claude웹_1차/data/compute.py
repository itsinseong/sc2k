#!/usr/bin/env python3
"""D01 스테이블코인 유통량 감소, 금리, 은행 예금 비중 계산.

실행: python3 compute.py        (표준 라이브러리만, Python 3.12 이상)
입력: raw/ 아래 원응답. 없는 파일만 새로 받는다(DefiLlama, FRED). 같은 raw로 돌리면 같은 숫자가 나온다.
      새로 받으려면 raw/ 의 해당 파일을 지우고 다시 실행한다(마지막 날짜가 늘어 숫자가 달라진다).
출력: 화면, compute_output.txt, {코인}_circulating.csv, fred_monthend.csv, corr_inputs.csv
"""
import csv
import json
import statistics
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]  # 레포 루트 (data, Claude웹_1차, research, docs 순으로 올라간다)
RAW = HERE / "raw"
COINS = {"USDT": 1, "USDC": 2, "PYUSD": 120, "USDP": 11, "GUSD": 19, "RLUSD": 250, "USDG": 286, "EURC": 50}
WINDOWS = (1, 3, 5, 7, 30)
START = date(2022, 1, 1)  # 창 시작일 하한
MIN_START = 10_000_000  # 점검용: 창 시작 유통량 하한(코인 자체 단위). 출시 직후 소액 구간이 결과를 흔드는지 보는 임의 값
TOP_N = 5
DAY = timedelta(days=1)

LINES = []


def out(s=""):
    print(s)
    LINES.append(s)


# ---------- 입력 ----------
def fetch(url, path):
    if path.exists() and path.stat().st_size > 0:
        return
    RAW.mkdir(exist_ok=True)
    # FRED는 브라우저형 User-Agent 요청에 응답하지 않아(타임아웃) curl 값을 쓴다
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.7.1"})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read()
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(body)
    tmp.replace(path)


def load_coin(sym, cid):
    """(단위, 일별 circulating, 일별 unreleased, 응답의 price). unreleased는 값이 있는 날만 담는다."""
    p = RAW / f"defillama_{sym}_{cid}.json"
    fetch(f"https://stablecoins.llama.fi/stablecoin/{cid}", p)
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["symbol"] == sym and d["id"] == str(cid), (sym, d["symbol"], d["id"])
    unit = d["pegType"]  # peggedUSD 또는 peggedEUR. circulating 안의 키와 같다
    s, u = {}, {}
    for t in d["tokens"]:
        day = datetime.fromtimestamp(t["date"], timezone.utc).date()
        if t["circulating"].get(unit) is not None:
            s[day] = t["circulating"][unit]
        if (t.get("unreleased") or {}).get(unit) is not None:
            u[day] = t["unreleased"][unit]
    return unit, s, u, d.get("price")


def load_fred(sid):
    p = RAW / f"fred_{sid}.csv"
    fetch(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", p)
    rows = list(csv.reader(p.read_text(encoding="utf-8").splitlines()))[1:]
    return sorted((date.fromisoformat(d), float(v)) for d, v in rows if v not in ("", "."))


def month_ends(obs):
    me = {}
    for d, v in obs:  # 날짜 오름차순이라 달마다 마지막 관측이 남는다
        me[d.strftime("%Y-%m")] = (d, v)
    return me


def load_reports():
    by = {}
    for p in sorted((ROOT / "data").glob("reports*.json")):
        for r in json.loads(p.read_text(encoding="utf-8"))["reports"]:
            by.setdefault(r["token"], []).append(r)
    return by


# ---------- 계산 ----------
def windows(s, k, floor=0):
    """k일 창 목록 (변화율, 시작일, 종료일, 시작값, 종료값).
    시작일이 START 이후이고 시작일과 종료일 관측이 모두 있으며 시작값이 floor 이상인 창만 쓴다. 빠진 날은 채우지 않는다."""
    out_ = []
    for d, a in s.items():
        if d < START or a <= 0 or a < floor:
            continue
        b = s.get(d + timedelta(days=k))
        if b is not None:
            out_.append((b / a - 1, d, d + timedelta(days=k), a, b))
    return out_


def top_declines(s, k=7, n=TOP_N, floor=0):
    """감소가 큰 순서로 고르되 앞서 고른 창과 시작일 간격이 k일 이상인 창만 받는다(끝점 공유는 허용).
    ponytail: 탐욕 선택이라 구간 합을 최적화하지는 않는다. 상위 n개 겹치지 않는 구간이라는 뜻에는 충분하다."""
    picked = []
    for w in sorted(windows(s, k, floor)):
        if w[0] >= 0:
            break
        if all(abs((w[1] - p[1]).days) >= k for p in picked):
            picked.append(w)
            if len(picked) == n:
                break
    return picked


def smooth(s):
    """3일 중앙값. 앞뒤 날 관측이 모두 있는 날만 남긴다. 하루짜리 튐은 사라지고 이틀 이상 이어진 변화는 남는다."""
    return {d: statistics.median((s[d - DAY], v, s[d + DAY])) for d, v in s.items() if d - DAY in s and d + DAY in s}


def base_ratio(s, d0, b):
    """종료값 / (시작일 포함 직전 30일 중 가장 낮은 값). 1 이상이면 창 안의 감소가 직전 증가를 되돌린 데 그쳤을 수 있다."""
    return b / min(v for j in range(31) if (v := s.get(d0 - timedelta(days=j))) is not None)


def d_unreleased(u, d0, d1):
    """종료일 unreleased - 시작일 unreleased. 두 날 모두 값이 있을 때만(없는 날은 0이 아니라 알 수 없음)."""
    return u[d1] - u[d0] if d0 in u and d1 in u else None


def corr(x, y):
    """(피어슨, 스피어먼). 스피어먼은 statistics ranked(동점은 평균 순위). 계산 불가면 None.
    ponytail: p값은 계산하지 않는다. 표본 크기 표시로 갈음한다."""
    if len(x) < 3:
        return None, None
    res = []
    for m in ("linear", "ranked"):
        try:
            res.append(statistics.correlation(x, y, method=m))
        except statistics.StatisticsError:  # 한쪽이 상수
            res.append(None)
    return tuple(res)


def selftest():
    d0 = date(2022, 1, 1)
    # 1일 창: 70 -> 20 이 가장 크게 줄어든다(-71.43%), 시작일 2022-01-09
    s = {d0 + timedelta(days=i): v for i, v in enumerate([100, 90, 95, 50, 60, 55, 70, 70, 70, 20])}
    w = min(windows(s, 1))
    assert w[1] == date(2022, 1, 9) and abs(w[0] - (20 / 70 - 1)) < 1e-12
    # 7일 창: 시작일이 2일 간격인 창끼리는 겹치므로 하나만 남는다
    assert [x[1] for x in top_declines(s, 7)] == [date(2022, 1, 3)]
    # 시작일 간격이 정확히 7일이면 겹치지 않는 것으로 본다(0일 시작 -50%, 7일 시작 -80%)
    vals = [100] * 7 + [50] + [50] * 6 + [10]
    s2 = {d0 + timedelta(days=i): v for i, v in enumerate(vals)}
    assert [x[1] for x in top_declines(s2, 7)] == [date(2022, 1, 8), date(2022, 1, 1)]
    # 시작 유통량 하한: 하한 아래에서 시작하는 창은 빠진다
    assert not windows(s2, 7, floor=1000)
    # 하루짜리 튐은 3일 중앙값에서 사라진다
    s3 = {d0 + timedelta(days=i): v for i, v in enumerate([100, 100, 50, 100, 100])}
    assert smooth(s3)[d0 + 2 * DAY] == 100 and d0 not in smooth(s3)
    # 기준선 대비: 직전 30일 최저 50, 종료값 100이면 2배
    assert base_ratio(s3, d0 + 3 * DAY, 100) == 2
    # unreleased 변화는 두 날 모두 있을 때만
    assert d_unreleased({d0: 5, d0 + DAY: 8}, d0, d0 + DAY) == 3 and d_unreleased({d0: 5}, d0, d0 + DAY) is None
    # 스피어먼 동점 처리: 평균 순위로 계산한 피어슨과 같아야 한다
    sp = corr([1, 2, 3, 4, 5], [5, 6, 7, 8, 7])[1]
    assert abs(sp - 8 / 95**0.5) < 1e-12
    # 상수 입력은 None
    assert corr([1, 2, 3], [4, 4, 4]) == (None, None)


# ---------- 표시 ----------
def pct(x):
    return f"{x * 100:+.2f}%"


def num(x):
    return f"{x:,.0f}"


def r3(x):
    return "계산 불가" if x is None else f"{x:+.3f}"


def size_flag(n):
    return "매우 작음(n<10)" if n < 10 else "작음(n<30)" if n < 30 else "30 이상"


def window_row(sym, label, w, s, u):
    r, d0, d1, a, b = w
    du = d_unreleased(u, d0, d1)
    return (f"| {sym} | {label} | {d0} | {d1} | {num(a)} | {num(b)} | {pct(r)} | {b - a:+,.0f} | "
            f"{base_ratio(s, d0, b) * 100:.1f}% | {'-' if du is None else f'{du:+,.0f}'} |")


WIN_HEAD = ["| 코인 | {} | 시작일 | 종료일 | 시작 유통량 | 종료 유통량 | 순변화율 | 순변화량 | 종료값 / 직전 30일 최저값 | unreleased 변화 |",
            "|---|---|---|---|---|---|---|---|---|---|"]


def main():
    selftest()
    reports = load_reports()
    coins, unrel, prices = {}, {}, {}
    for sym, cid in COINS.items():
        unit, s, u, price = load_coin(sym, cid)
        coins[sym], unrel[sym], prices[sym] = (unit, s), u, price
        with open(HERE / f"{sym}_circulating.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["date", f"circulating_{unit}", f"unreleased_{unit}"])
            w.writerows((d.isoformat(), v, u.get(d, "")) for d, v in sorted(s.items()))
    dtb3_obs, effr_obs = load_fred("DTB3"), load_fred("EFFR")
    dtb3, effr = month_ends(dtb3_obs), month_ends(effr_obs)
    with open(HERE / "fred_monthend.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["month", "DTB3_obs_date", "DTB3_pct", "EFFR_obs_date", "EFFR_pct"])
        for m in sorted(dtb3):
            if m >= "2021-12":
                e = effr.get(m, ("", ""))
                w.writerow([m, dtb3[m][0].isoformat(), dtb3[m][1], e[0] and e[0].isoformat(), e[1]])

    asof = max(max(s) for _, s in coins.values())
    last_full = asof if (asof + DAY).day == 1 else asof.replace(day=1) - DAY

    out("# D01 계산 출력")
    out("순변화(발행에서 상환을 뺀 값)이고 체인 합계다. DefiLlama stablecoin/{id}의 tokens 배열, circulating의 pegged 값을 쓴다.")
    out(f"창 시작일은 {START.isoformat()} 이후. 변화율은 창 시작 대비이고 음수가 감소다. 빠진 날은 채우지 않고 그 날이 낀 창은 뺀다.")
    out("")

    # 0. 입력 요약
    out("## 0. 입력 요약")
    out("| 코인 | id | 단위 | 관측일수 | 첫 날짜 | 마지막 날짜 | 마지막 값 | 빠진 날수 | 보고서 첫 월 |")
    out("|---|---|---|---|---|---|---|---|---|")
    for sym, cid in COINS.items():
        unit, s = coins[sym]
        ds = sorted(s)
        gaps = (ds[-1] - ds[0]).days + 1 - len(ds)
        out(f"| {sym} | {cid} | {unit} | {len(ds)} | {ds[0]} | {ds[-1]} | {num(s[ds[-1]])} | {gaps} | "
            f"{min(r['month'] for r in reports[sym])} |")
    out("")
    for name, obs in (("DTB3", dtb3_obs), ("EFFR", effr_obs)):
        out(f"FRED {name}: 관측 {len(obs)}건, 첫 {obs[0][0]}, 마지막 {obs[-1][0]} = {obs[-1][1]}%. 월말 값은 달마다 마지막 관측(영업일).")
    out(f"가장 최근 완결 월: {last_full.strftime('%Y-%m')} (DefiLlama 마지막 날짜 {asof}는 월말이 아님)")
    out("")

    # 1. 단위 점검
    out("## 1. 단위 점검: DefiLlama 유통량 / 발행사 보고서 유통량(보고서 기준일 같은 날)")
    out("보고서는 미발행 허용 토큰과 접근 제한 토큰 등을 빼고 기준시각도 달라 두 값은 같지 않다. 단위와 크기 점검용이며 커버리지 계산에는 쓰지 않는다.")
    out("| 코인 | 보고서 통화 | DefiLlama 단위 | 대조 건수 | 비율 중앙값 | 비율 가장 작은 값 | 비율 가장 큰 값 | 최근 3개 보고월 비율(월: 비율) |")
    out("|---|---|---|---|---|---|---|---|")
    for sym in COINS:
        unit, s = coins[sym]
        rs = sorted(reports[sym], key=lambda r: r["month"])
        pairs = []
        for r in rs:
            v = s.get(date.fromisoformat(r["as_of"]))
            if v and r["circulation"]:
                pairs.append((r["month"], v / r["circulation"]))
        ratios = [v for _, v in pairs]
        recent = ", ".join(f"{m}: {v:.3f}" for m, v in pairs[-3:])
        out(f"| {sym} | {rs[0]['reserve_currency']} | {unit} | {len(ratios)} | {statistics.median(ratios):.3f} | "
            f"{min(ratios):.3f} | {max(ratios):.3f} | {recent} |")
    out(f"EURC: DefiLlama pegType={coins['EURC'][0]}, 응답의 price(미국 달러 환산 가격)={prices['EURC']}. "
        "비율이 1에 가까우면 유로 토큰 수량 단위이고, 달러로 환산한 값이면 이 price 배(약 1.1배)로 벌어진다.")
    out("")

    # 2. 최악 순변화율
    out("## 2-A. 창 길이별 최악 순변화율 (요청 사양 그대로, 원자료)")
    out("종료값 / 직전 30일 최저값: 종료일 유통량을 시작일 포함 직전 30일 중 가장 낮은 유통량으로 나눈 값. 100% 이상이면 창 안의 감소가 직전 증가를 되돌린 데 그쳤을 수 있다.")
    out("unreleased 변화: 종료일 unreleased 에서 시작일 unreleased 를 뺀 값(두 날 모두 값이 있을 때만, 없으면 -). 양수면 감소분 일부가 circulating에서 unreleased로 옮겨 간 것일 수 있다.")
    out(WIN_HEAD[0].format("창"))
    out(WIN_HEAD[1])
    for sym in COINS:
        for k in WINDOWS:
            ws = windows(coins[sym][1], k)
            out(window_row(sym, f"{k}일", min(ws), coins[sym][1], unrel[sym]) if ws else f"| {sym} | {k}일 | 해당 창 없음 | | | | | | | |")
    out("")

    out("## 2-B. 점검: 3일 중앙값으로 하루짜리 튐을 없앤 계열의 최악 순변화율")
    out("원자료 값이 하루만 튀었다가 돌아온 경우 2-A와 2-B가 크게 갈린다. 2-B의 종료일 쪽 값은 평활값이다.")
    out("| 코인 | 창 | 2-A 순변화율 | 2-B 순변화율 | 2-B 시작일 | 2-B 종료일 |")
    out("|---|---|---|---|---|---|")
    for sym in COINS:
        sm = smooth(coins[sym][1])
        for k in WINDOWS:
            ra, rb = min(windows(coins[sym][1], k)), min(windows(sm, k))
            out(f"| {sym} | {k}일 | {pct(ra[0])} | {pct(rb[0])} | {rb[1]} | {rb[2]} |")
    out("")

    # 3. 겹치지 않는 7일 상위 감소 구간
    out(f"## 3. 7일 창 기준 겹치지 않는 상위 {TOP_N}개 감소 구간 (원자료)")
    out("겹침 기준: 시작일 간격이 7일 미만이면 겹침. 간격이 정확히 7일이면 끝점만 공유해 허용. 뒤의 두 열은 2-A와 같은 뜻.")
    out(WIN_HEAD[0].format("순위"))
    out(WIN_HEAD[1])
    top_all, ws_all = {}, {}
    for sym in COINS:
        s = coins[sym][1]
        top = top_all[sym] = top_declines(s)
        if not top:
            out(f"| {sym} | 해당 구간 없음 | | | | | | | | |")
            continue
        assert top[0] == min(windows(s, 7))  # 2-A의 7일 최악과 같아야 한다
        for i, w in enumerate(top, 1):
            out(window_row(sym, i, w, s, unrel[sym]))
    out("")

    # 점검: 소액 구간 영향
    diff = total = 0
    for sym in COINS:
        s = coins[sym][1]
        for k in WINDOWS:
            diff += min(windows(s, k)) != min(windows(s, k, MIN_START), default=None)
            total += 1
        diff += len(set(top_all[sym]) - set(top_declines(s, floor=MIN_START)))
        total += len(top_all[sym])
    out(f"점검: 창 시작 유통량 {MIN_START:,} 단위 이상으로 제한해 다시 계산했을 때 2-A와 3에서 달라지는 행 수 = {diff} (전체 {total}행)")
    out("")

    # 4. 월말 금리
    out("## 4. FRED 월말 값 (전체는 fred_monthend.csv, 2021-12부터)")
    out("| 월 | DTB3 관측일 | DTB3(%) | EFFR 관측일 | EFFR(%) |")
    out("|---|---|---|---|---|")
    for m in sorted(dtb3)[-6:]:
        e = effr.get(m)
        out(f"| {m} | {dtb3[m][0]} | {dtb3[m][1]} | {e[0] if e else ''} | {e[1] if e else ''} |")
    since = [(m, v[1]) for m, v in sorted(dtb3.items()) if m >= "2022-01"]
    lo, hi = min(since, key=lambda x: x[1]), max(since, key=lambda x: x[1])
    out(f"2022-01 이후 DTB3 월말 값: 가장 낮은 값 {lo[1]}% ({lo[0]}), 가장 높은 값 {hi[1]}% ({hi[0]}), 월 수 {len(since)}")
    out("")

    # 5. 은행 예금 비중 상관
    out("## 5. 은행 예금 비중(components.cash / fair_value)과 그 달 월말 DTB3의 상관")
    out("cash가 null인 달은 제외. 월 단위 시계열이라 추세가 있는 두 계열의 수준 상관이며 실효 표본은 n보다 작다. 인과를 뜻하지 않는다.")
    out("비중이 100%를 넘는 달은 other(정산 차액)가 음수여서 cash가 fair_value보다 큰 달이다. 유통량은 보고서의 circulation.")
    out("cash의 뜻은 발행사 보고서마다 다르다(data/reports*.json의 note): USDC, EURC, GUSD, RLUSD는 규제 금융기관 예치 현금, "
        "USDT는 Cash & Bank Deposits, USDP와 PYUSD는 Cash 또는 Total U.S. Dollars Held. USDG는 2024-10부터 2025-12까지 한 줄(Total Cash and Cash Equivalents)이라 cash=null.")
    out("| 코인 | n | 기간 | 비중 범위 | DTB3 범위(%) | 비중 vs DTB3 피어슨 | 스피어먼 | 비중 vs 유통량 피어슨 | 스피어먼 | 표본 크기 | 제외 건수 |")
    out("|---|---|---|---|---|---|---|---|---|---|---|")
    rows = []
    for sym in COINS:
        rs, skipped = [], 0
        for r in sorted(reports[sym], key=lambda r: r["month"]):
            cash, fv = r["components"].get("cash"), r["fair_value"]
            if cash is None or not fv or r["month"] not in dtb3:
                skipped += 1
                continue
            rs.append((r["month"], r["as_of"], cash, fv, cash / fv, r["circulation"], dtb3[r["month"]][0], dtb3[r["month"]][1]))
        assert len({x[0] for x in rs}) == len(rs)  # 월 중복 없음
        rows += [(sym, *x) for x in rs]
        share, circ, rate = [x[4] for x in rs], [x[5] for x in rs], [x[7] for x in rs]
        rp, rs_ = corr(share, rate)
        cp, cs = corr(share, circ)
        out(f"| {sym} | {len(rs)} | {rs[0][0]} ~ {rs[-1][0]} | {min(share) * 100:.1f}% ~ {max(share) * 100:.1f}% | "
            f"{min(rate)} ~ {max(rate)} | {r3(rp)} | {r3(rs_)} | {r3(cp)} | {r3(cs)} | {size_flag(len(rs))} | {skipped} |")
    with open(HERE / "corr_inputs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["coin", "month", "as_of", "cash", "fair_value", "cash_share", "circulation", "DTB3_obs_date", "DTB3_pct"])
        for sym, m, as_of, cash, fv, sh, circ, dd, dv in rows:
            w.writerow([sym, m, as_of, cash, fv, repr(sh), circ, dd.isoformat(), dv])
    out("")

    # 6. 은행 예금 1%p당 연 이자 상한
    out("## 6. 은행 예금 비중 1%p당 발행사가 잃는 연 이자 상한 = 유통량 x 1% x DTB3 (은행 예금 이자율은 0으로 둔 상한값)")
    out(f"방식 A: DefiLlama {last_full} 유통량 x 1% x 같은 달({last_full.strftime('%Y-%m')}) 월말 DTB3")
    out("방식 B: 코인별 가장 최근 보고서 월의 보고서 유통량 x 1% x 그 달 월말 DTB3")
    out("금액 단위는 코인 단위(USD 코인은 달러, EURC는 유로). EURC에 미국 DTB3를 쓴 것은 근사다.")
    out("| 코인 | A 유통량 | A DTB3(%) | A 연 이자 상한 | B 보고서 월 | B 유통량 | B DTB3(%) | B 연 이자 상한 |")
    out("|---|---|---|---|---|---|---|---|")
    ma = last_full.strftime("%Y-%m")
    for sym in COINS:
        ca = coins[sym][1][last_full]
        ra = dtb3[ma][1]
        r = max(reports[sym], key=lambda r: r["month"])
        rb = dtb3[r["month"]][1]
        out(f"| {sym} | {num(ca)} | {ra} | {num(ca * 0.01 * ra / 100)} | {r['month']} | {num(r['circulation'])} | {rb} | "
            f"{num(r['circulation'] * 0.01 * rb / 100)} |")
    out("")
    out("저장 파일: compute_output.txt, {코인}_circulating.csv 8개, fred_monthend.csv, corr_inputs.csv, raw/ 원응답")

    (HERE / "compute_output.txt").write_text("\n".join(LINES) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
