"""TronGrid 이벤트를 계약 생성부터 지정 시각까지 모두 받아 raw에 저장한다(키 없이 동작).
사용: python3 -I tron_events.py <이름> <계약주소> <끝시각 UTC 'YYYY-MM-DD HH:MM:SS'> <이벤트명,이벤트명,...>"""
import sys, os, json, time, urllib.request, urllib.error; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import utc, save_gz
name, addr, end, evs = sys.argv[1:5]
maxts = utc(end) * 1000
def get(url):
    for i in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "curl/8.7.1"}), timeout=60) as r:
                return json.loads(r.read())
        except (urllib.error.URLError, TimeoutError) as e:
            time.sleep(2 + 3 * i)
    raise RuntimeError(url)
res = {}
for ev in evs.split(","):
    rows = []; fp = None
    while True:
        u = f"https://api.trongrid.io/v1/contracts/{addr}/events?only_confirmed=true&limit=200&order_by=block_timestamp,asc&event_name={ev}&max_block_timestamp={maxts}"
        if fp: u += "&fingerprint=" + fp
        d = get(u)
        rows += [{k: e[k] for k in ("block_number", "block_timestamp", "transaction_id", "event_index", "event_name", "result")} for e in d.get("data", [])]
        fp = (d.get("meta") or {}).get("fingerprint")
        if not fp or not d.get("data"): break
        time.sleep(0.3)
    res[ev] = rows; print(ev, len(rows), flush=True)
save_gz(f"{name}_events.json.gz", {"contract": addr, "end": end, "events": res})
