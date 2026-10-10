#!/usr/bin/env python3
"""은행 예금 비중(cash / fair_value)과 미국 3개월 국채 금리(DTB3) 월별 상관 점검.

실행: python3 corr_check.py        (표준 라이브러리만, Python 3.12 이상)
입력(읽기만): docs/research/Claude웹_1차/data/corr_inputs.csv, fred_monthend.csv (compute.py 산출물)
             대조용 data/reports*.json (corr_inputs.csv 값이 지금 보고서 값과 같은지만 본다)
출력: 화면(상관확인.md 표의 원본). 부트스트랩은 시드를 고정해 같은 입력이면 같은 숫자가 나온다.
"""
import csv
import json
import math
import random
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]  # 레포 루트 (scripts, 상관관계_2026-10-10, research, docs 순으로 올라간다)
DATA = ROOT / "docs" / "research" / "Claude웹_1차" / "data"
COINS = ("USDC", "PYUSD", "USDP", "GUSD")
DOC = {"USDC": (-0.421, -0.573), "PYUSD": (-0.254, -0.431), "USDP": (-0.495, -0.357), "GUSD": (-0.782, -0.838)}  # 구조 문서 표
SVB = 2023 * 12 + 2  # 2023-03의 월 번호. 전 = 2023-02까지, 후 = 2023-04부터, 2023-03은 사건 달이라 양쪽에서 뺀다
GUSD_SWITCH = 2024 * 12 + 9  # 2024-10: GUSD 정부 MMF가 0이 되고 준비자산이 전부 cash가 된 달(reports_gemini.json components)
LAGS = (1, 2, 3)
B, BLOCKS, SEED = 10_000, (3, 6, 12), 20261010  # 부트스트랩 반복 수, 블록 길이(개월), 시드
NORM = statistics.NormalDist()
Z = NORM.inv_cdf(0.975)


def mi(m):
    """'2023-03' -> 월 번호(연 x 12 + 월 - 1). 빠진 달을 알아보려고 쓴다."""
    y, mo = map(int, m.split("-"))
    return y * 12 + mo - 1


def ym(t):
    return f"{t // 12}-{t % 12 + 1:02d}"


# ---------- 입력 ----------
def load():
    """코인별 [(월 번호, 비중, DTB3)] 월 오름차순, 월 번호별 DTB3 전체, corr_inputs.csv와 원천이 어긋난 행 수."""
    with open(DATA / "fred_monthend.csv", encoding="utf-8") as f:
        rate = {mi(r["month"]): float(r["DTB3_pct"]) for r in csv.DictReader(f)}
    rep = {}
    for p in sorted((ROOT / "data").glob("reports*.json")):
        for r in json.loads(p.read_text(encoding="utf-8"))["reports"]:
            cash, fv = r["components"].get("cash"), r["fair_value"]
            if r["token"] in COINS and cash is not None and fv:
                rep[(r["token"], mi(r["month"]))] = cash / fv
    rows, bad = {c: [] for c in COINS}, 0
    with open(DATA / "corr_inputs.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["coin"] in rows:
                t, sh, y = mi(r["month"]), float(r["cash_share"]), float(r["DTB3_pct"])
                bad += y != rate[t] or not abs(sh - rep.pop((r["coin"], t), math.nan)) <= 1e-12
                rows[r["coin"]].append((t, sh, y))
    for c in COINS:
        rows[c].sort()
        assert len({t for t, _, _ in rows[c]}) == len(rows[c])  # 월 중복 없음
    return rows, rate, bad + len(rep)  # rep에 남은 것 = 보고서에는 있는데 corr_inputs.csv에 없는 달


# ---------- 계산 ----------
def corr(x, y):
    """(피어슨, 스피어먼). n<3 이거나 한쪽이 상수면 None."""
    if len(x) < 3:
        return None, None
    try:
        return statistics.correlation(x, y), statistics.correlation(x, y, method="ranked")
    except statistics.StatisticsError:
        return None, None


def diffs(rows, rate, lag=0):
    """[(월 번호, 비중 변화, DTB3 변화)]. 비중 변화는 바로 앞 달 관측이 있을 때만(빠진 달을 건너뛴 변화는 뺀다).
    DTB3 변화는 lag개월 앞 달의 변화(lag=0이면 같은 달)이고 금리는 빠진 달이 없다."""
    return [(t, s - s0, rate[t - lag] - rate[t - lag - 1])
            for (t0, s0, _), (t, s, _) in zip(rows, rows[1:]) if t - t0 == 1]


def resid(t, v):
    """월 번호에 대한 직선 회귀 잔차(직선 추세를 뺀 값)."""
    a = statistics.linear_regression(t, v)
    return [b - (a.slope * x + a.intercept) for x, b in zip(t, v)]


def detrend(part):
    """[(월 번호, 비중, 금리)] -> 같은 모양으로 비중과 금리를 각각 직선 추세 뺀 값."""
    t, x, y = zip(*part)
    return list(zip(t, resid(t, x), resid(t, y)))


def ac1(t, v):
    """1개월 자기상관. 정확히 1개월 떨어진 짝의 편차 곱 평균 / 분산. 빠진 달이 있어도 짝 수로 나눠 아래로 치우치지 않게 한다."""
    m = statistics.fmean(v)
    prods = [(a - m) * (b - m) for t0, t1, a, b in zip(t, t[1:], v, v[1:]) if t1 - t0 == 1]
    return statistics.fmean(prods) / statistics.pvariance(v, m)


def n_eff(n, r1x, r1y):
    """실효 표본 수, AR(1) 근사(Bretherton 외 1999): n(1 - r1x r1y) / (1 + r1x r1y). n을 넘지 않게 자른다."""
    return min(n, n * (1 - r1x * r1y) / (1 + r1x * r1y))


def fisher(r, ne):
    """실효 표본 수로 낸 (95% 하한, 상한, 양측 p). 피셔 z 정규 근사. 실효 표본 3 이하면 None."""
    if r is None or ne <= 3:
        return None
    z, se = math.atanh(r), 1 / math.sqrt(ne - 3)
    return math.tanh(z - Z * se), math.tanh(z + Z * se), 2 * (1 - NORM.cdf(abs(z) / se))


def block_ci(x, y, L, seed=SEED):
    """이동 블록 부트스트랩 95% 백분위 구간(피어슨). (비중, 금리) 짝을 L개월 묶음째 다시 뽑아 n개를 채운다.
    한쪽이 상수가 된 표본은 버리고 그 수를 같이 돌려준다. 계열이 정상(평균, 분산 일정)이라고 가정하는 방법이다.
    ponytail: 블록 길이는 3, 6, 12개월 고정 비교. 자동 선택(Politis-White)은 이 비교로 부족할 때 붙인다."""
    n, rnd, rs = len(x), random.Random(seed), []
    if n < 2 * L:
        return None
    for _ in range(B):
        idx = []
        while len(idx) < n:
            s = rnd.randrange(n - L + 1)
            idx += range(s, s + L)
        try:
            rs.append(statistics.correlation([x[i] for i in idx[:n]], [y[i] for i in idx[:n]]))
        except statistics.StatisticsError:
            pass
    q = statistics.quantiles(rs, n=40, method="inclusive")
    return q[0], q[-1], B - len(rs)


def adj(t, x, y):
    """(n, 피어슨, 비중 1개월 자기상관, 금리 1개월 자기상관, 실효 표본, 피셔 결과). 상관을 낼 수 없으면 n 뒤가 모두 None."""
    r = corr(x, y)[0]
    if r is None:
        return len(x), None, None, None, None, None
    a, b = ac1(t, x), ac1(t, y)
    ne = n_eff(len(x), a, b)
    return len(x), r, a, b, ne, fisher(r, ne)


def loo(d):
    """[(월 번호, x, y)]에서 한 달을 뺐을 때 피어슨이 가장 많이 바뀌는 달과 그때의 피어슨."""
    base = corr([v[1] for v in d], [v[2] for v in d])[0]
    alt = [(corr([v[1] for v in d if v is not w], [v[2] for v in d if v is not w])[0], w) for w in d]
    r, w = max(alt, key=lambda a: abs(a[0] - base))
    return w, r


def selftest():
    rate = {0: 1.0, 1: 2.0, 2: 4.0, 3: 7.0}
    # 빠진 달(2)을 건너뛴 변화는 빠지고, lag=1이면 한 달 앞 금리 변화와 짝짓는다
    assert diffs([(0, 1, 1), (1, 3, 2), (3, 4, 7)], rate) == [(1, 2, 1.0)]
    assert diffs([(1, 1, 2), (2, 3, 4)], rate, lag=1) == [(2, 2, 1.0)]
    # 직선 추세 잔차는 합이 0이고 시간과 직교한다
    e = resid([0, 1, 2, 3, 4], [1, 3, 2, 5, 9])
    assert abs(sum(e)) < 1e-9 and abs(sum(i * v for i, v in enumerate(e))) < 1e-9
    # 번갈아 움직이는 계열의 1개월 자기상관은 -1, 빠진 달이 끼면 그 짝만 뺀다
    assert ac1([0, 1, 2, 3], [1, -1, 1, -1]) == -1 and ac1([0, 1, 5, 6], [1, -1, 1, -1]) == -1
    # 자기상관이 없으면 실효 표본 = n, 둘 다 0.5면 0.6n
    assert n_eff(40, 0, 0.9) == 40 and abs(n_eff(40, 0.5, 0.5) - 24) < 1e-12
    # 상관 0이면 p=1이고 구간이 0을 가운데 둔다
    lo, hi, p = fisher(0.0, 28)
    assert abs(lo + hi) < 1e-12 and abs(p - 1) < 1e-12 and fisher(0.5, 3) is None


# ---------- 표시 ----------
def r3(x):
    return "계산 불가" if x is None else f"{x:+.3f}"


def pair(x):
    p, s = x
    return "계산 불가" if p is None else f"{p:+.3f} ({s:+.3f})"


def ci(c):
    return "계산 불가" if c is None else f"{c[0]:+.3f} ~ {c[1]:+.3f}"


def pv(f):
    return "계산 불가" if f is None else f"{f[2]:.3f}"


def main():
    selftest()
    rows, rate, bad = load()
    print(f"입력 대조: corr_inputs.csv 4개 코인 {sum(map(len, rows.values()))}행 중 data/reports*.json의 cash/fair_value "
          f"또는 fred_monthend.csv의 DTB3와 다르거나 한쪽에만 있는 행 = {bad}")
    print()

    print("## 1. 수준 상관 재현")
    print("| 코인 | n | 기간 | 빠진 달 | 피어슨 | 스피어먼 | 구조 문서(피어슨, 스피어먼) | 소수 셋째 자리까지 같은가 |")
    print("|---|---|---|---|---|---|---|---|")
    for c in COINS:
        t, x, y = zip(*rows[c])
        p, s = corr(x, y)
        miss = ", ".join(ym(m) for m in range(t[0], t[-1] + 1) if m not in t) or "없음"
        same = round(p, 3) == DOC[c][0] and round(s, 3) == DOC[c][1]
        print(f"| {c} | {len(t)} | {ym(t[0])} ~ {ym(t[-1])} | {miss} | {r3(p)} | {r3(s)} | {DOC[c][0]:+.3f}, {DOC[c][1]:+.3f} | "
              f"{'같음' if same else '다름'} |")
    print()

    # 코인별 계열: 이름 -> [(월 번호, 비중 또는 그 변화, DTB3 또는 그 변화)]
    ser = {}
    for c in COINS:
        r = rows[c]
        post = [v for v in r if v[0] > SVB]
        d = diffs(r, rate)
        ser[c] = {
            "수준": r,
            "월별 변화": d,
            "SVB 전 수준": [v for v in r if v[0] < SVB],
            "SVB 후 수준": post,
            "SVB 후 월별 변화": [v for v in d if v[0] > SVB + 1],  # 두 달 모두 2023-04 이후인 변화만
            "직선 추세 뺀 수준": detrend(r),
            "SVB 후 직선 추세 뺀 수준": detrend(post),
        }
    same_as_all = {c: len(ser[c]["SVB 후 수준"]) == len(rows[c]) for c in COINS}  # SVB 전 관측이 없는 코인
    names = [k for k in ser[COINS[0]] if k != "SVB 전 수준"]

    def cols(part):
        return [v[1] for v in part], [v[2] for v in part]

    def skip(c, name):
        return name.startswith("SVB 후") and same_as_all[c]

    print("## 2. 방식별 상관 (피어슨, 괄호 안 스피어먼)")
    print("| 코인 | " + " | ".join(ser[COINS[0]]) + " |")
    print("|---|" + "---|" * len(ser[COINS[0]]))
    for c in COINS:
        print(f"| {c} | " + " | ".join("전체와 같음" if skip(c, k) else f"{pair(corr(*cols(v)))}, n={len(v)}"
                                       for k, v in ser[c].items()) + " |")
    print("SVB 전 관측이 없는 코인의 SVB 후 칸은 '전체와 같음'(PYUSD는 2023-08부터)")
    print()

    print("## 3. 자기상관을 고려한 유의성: 실효 표본 (피어슨). 실효 표본은 AR(1) 근사, 구간과 p는 피셔 z 정규 근사")
    print("| 코인 | 계열 | n | 피어슨 | 1개월 자기상관(비중, 금리) | 실효 표본 | 95% 구간 | p |")
    print("|---|---|---|---|---|---|---|---|")
    n_tests = 0
    for c in COINS:
        for k in names:
            if skip(c, k):
                continue
            n, r, a, b, ne, f = adj([v[0] for v in ser[c][k]], *cols(ser[c][k]))
            n_tests += f is not None
            print(f"| {c} | {k} | {n} | {r3(r)} | {a:+.2f}, {b:+.2f} | {ne:.1f} | {ci(f)} | {pv(f)} |")
    print()

    print(f"## 4. 자기상관을 고려한 유의성: 이동 블록 부트스트랩 95% 구간 (피어슨, {B:,}회, 시드 {SEED})")
    print("| 코인 | 계열 | " + " | ".join(f"{L}개월 블록" for L in BLOCKS) + " |")
    print("|---|---|" + "---|" * len(BLOCKS))
    dropped = 0
    for c in COINS:
        for k in names:
            if skip(c, k):
                continue
            res = [block_ci(*cols(ser[c][k]), L) for L in BLOCKS]
            dropped += sum(x[2] for x in res if x)
            print(f"| {c} | {k} | " + " | ".join(ci(x) for x in res) + " |")
    print(f"한쪽이 상수가 되어 버린 부트스트랩 표본 수 합계: {dropped}")
    print()

    print("## 5. 차분 검정력: 수준 상관의 기울기가 월별 변화에도 그대로 있었다면 나왔을 차분 상관")
    print("기대 차분 상관 = 수준 기울기 x 금리 변화 표준편차 / 비중 변화 표준편차. 실제 차분 상관의 95% 구간(실효 표본)이 이 값을 포함하면 "
          "월별 변화로는 '관계 없음'과 '수준 기울기 그대로'를 가를 수 없다.")
    print("| 코인 | 구간 | 수준 기울기(금리 1%p당 비중 %p) | 기대 차분 상관 | 실제 차분 상관 | 95% 구간 | 기대값을 포함하는가 |")
    print("|---|---|---|---|---|---|---|")
    for c in COINS:
        for label, lv, dv in (("전체", "수준", "월별 변화"), ("SVB 후", "SVB 후 수준", "SVB 후 월별 변화")):
            if skip(c, lv):
                continue
            sx, sy = cols(ser[c][lv])
            dx, dy = cols(ser[c][dv])
            slope = statistics.linear_regression(sy, sx).slope
            expect = slope * statistics.stdev(dy) / statistics.stdev(dx)
            _, r, _, _, _, f = adj([v[0] for v in ser[c][dv]], dx, dy)
            print(f"| {c} | {label} | {slope * 100:+.2f} | {expect:+.4f} | {r3(r)} | {f[0]:+.4f} ~ {f[1]:+.4f} | "
                  f"{'포함' if f[0] <= expect <= f[1] else '밖'} |")
    print()

    print("## 6. 보조: 금리 변화가 앞설 때의 월별 변화 상관. k개월 = 비중 변화를 k개월 앞 달의 금리 변화와 짝지음")
    print("SVB 후 = 비중 변화의 두 달이 모두 2023-04 이후. p는 실효 표본 기준 피셔 z, 스피어먼 p는 분산을 1.06배로 둔 근사(Fieller 외 1957).")
    print("| 코인 | 구간 | k | n | 피어슨 | p | 스피어먼 | p | 피어슨을 가장 많이 바꾸는 달(비중 변화, 금리 변화) | 그 달을 뺀 피어슨 | p |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in COINS:
        for label, keep in (("전체", lambda t: True), ("SVB 후", lambda t: t > SVB + 1)):
            if label == "SVB 후" and same_as_all[c]:
                continue
            for k in (0, *LAGS):
                d = [v for v in diffs(rows[c], rate, k) if keep(v[0])]
                n, r, _, _, ne, f = adj([v[0] for v in d], *cols(d))
                rs = corr(*cols(d))[1]
                n_tests += k > 0 and f is not None  # k=0은 표 3의 월별 변화, SVB 후 월별 변화와 같은 검정
                w, rw = loo(d)
                dw = [v for v in d if v is not w]
                print(f"| {c} | {label} | {k} | {n} | {r3(r)} | {pv(f)} | {r3(rs)} | {pv(fisher(rs, 3 + (ne - 3) / 1.06))} | "
                      f"{ym(w[0])} ({w[1] * 100:+.2f}%p, {w[2]:+.2f}%p) | {r3(rw)} | {pv(adj([v[0] for v in dw], *cols(dw))[5])} |")
    print(f"피어슨 p를 낸 검정 수(표 3, 표 6의 k=1~3): {n_tests}. 0.05를 검정 수로 나눈 기준: {0.05 / n_tests:.5f}")
    print()

    print("## 7. 구간별 범위와 구간 안 상관 (피어슨, 괄호 안 스피어먼)")
    print("| 코인 | 구간 | n | 비중 범위 | DTB3 범위(%) | 상관 | 실효 표본 | p | 구간 안 직선 추세 뺀 피어슨 | p |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    segs = [("SVB 전(2023-02까지)", lambda t: t < SVB), ("2023-03", lambda t: t == SVB), ("SVB 후(2023-04부터)", lambda t: t > SVB)]
    gusd = [("2023-04 ~ 2024-09", lambda t: SVB < t < GUSD_SWITCH), ("2024-10부터", lambda t: t >= GUSD_SWITCH)]
    for c in COINS:
        for label, sel in segs + (gusd if c == "GUSD" else []):
            part = [v for v in rows[c] if sel(v[0])]
            if not part:
                continue
            sh, y = cols(part)
            t = [v[0] for v in part]
            n, r, _, _, ne, f = adj(t, sh, y)
            _, rd, _, _, _, fd = adj(t, resid(t, sh), resid(t, y)) if n >= 3 else (n, None, None, None, None, None)
            print(f"| {c} | {label} | {n} | {min(sh) * 100:.1f}% ~ {max(sh) * 100:.1f}% | {min(y)} ~ {max(y)} | "
                  f"{pair(corr(sh, y))} | {'계산 불가' if ne is None else f'{ne:.1f}'} | {pv(f)} | {r3(rd)} | {pv(fd)} |")


if __name__ == "__main__":
    main()
