"""TronGrid: 한 주소의 USDT(TRC20) 이체를 기간 안에서 모두 받는다. 사용: tron_trc20.py <이름> <주소> <계약> <시작> <끝>"""
import sys, os, json, time, urllib.request, urllib.error; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import utc, save_gz
name, addr, ctr, a, b = sys.argv[1:6]
def get(url):
    for i in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "curl/8.7.1"}), timeout=60) as r: return json.loads(r.read())
        except (urllib.error.URLError, TimeoutError): time.sleep(2 + 3 * i)
    raise RuntimeError(url)
rows = []; fp = None
while True:
    u = f"https://api.trongrid.io/v1/accounts/{addr}/transactions/trc20?only_confirmed=true&limit=200&contract_address={ctr}&min_timestamp={utc(a)*1000}&max_timestamp={utc(b)*1000-1}&order_by=block_timestamp,asc"
    if fp: u += "&fingerprint=" + fp
    d = get(u); rows += d.get("data", []); fp = (d.get("meta") or {}).get("fingerprint")
    print(len(rows), flush=True)
    if not fp or not d.get("data"): break
    time.sleep(0.3)
save_gz(f"{name}_trc20.json.gz", {"addr": addr, "contract": ctr, "from": a, "to": b, "rows": rows})
