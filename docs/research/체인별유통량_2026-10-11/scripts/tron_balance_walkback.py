"""TronGrid: Tether 트론 보관 지갑(TKHuVq...)의 USDT 현재 잔액과, 2022-05-18 00:00 UTC 이후 모든 이체를 받아 raw에 저장한다.
과거 시점 잔액 = 현재 잔액 - 그 이후 들어온 양 + 나간 양."""
import sys, os, json, time, urllib.request, urllib.error; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import utc, save_gz
A = "TKHuVq1oKVruCGLvqVexFs6dawKv6fQgFs"; C = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
def get(url):
    for i in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "curl/8.7.1"}), timeout=60) as r: return json.loads(r.read())
        except (urllib.error.URLError, TimeoutError): time.sleep(2 + 3 * i)
    raise RuntimeError(url)
def bal():
    d = get(f"https://api.trongrid.io/v1/accounts/{A}")["data"][0]
    return int(next(x[C] for x in d["trc20"] if C in x))
b0 = bal(); now = int(time.time() * 1000); rows = []; fp = None
while True:
    u = f"https://api.trongrid.io/v1/accounts/{A}/transactions/trc20?only_confirmed=true&limit=200&contract_address={C}&min_timestamp={utc('2022-05-18 00:00:00')*1000}&max_timestamp={now}&order_by=block_timestamp,asc"
    if fp: u += "&fingerprint=" + fp
    d = get(u); rows += d.get("data", []); fp = (d.get("meta") or {}).get("fingerprint"); print(len(rows), flush=True)
    if not fp or not d.get("data"): break
    time.sleep(0.3)
b1 = bal()
save_gz("tron_usdt_treasury_after.json.gz", {"addr": A, "contract": C, "balance_before": b0, "balance_after": b1, "max_timestamp": now, "rows": rows})
print("잔액", b0, b1)
