"""공용 함수: JSON-RPC 호출(재시도), 시각으로 블록 찾기, 과거 블록 eth_call."""
import functools, json, time, urllib.request, urllib.error, gzip, os, datetime

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
UA = {"User-Agent": "curl/8.7.1", "content-type": "application/json"}

def post(url, body, tries=6):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, json.dumps(body).encode(), UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            if "error" in d and d["error"]:
                last = d["error"]
                m = str(last)
                if "rate" in m.lower() or "limit" in m.lower() or "429" in m:
                    time.sleep(2 + 2 * i); continue
                raise RuntimeError(m)
            return d["result"]
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e; time.sleep(2 + 2 * i)
    raise RuntimeError(f"실패 {url} {body.get('method')}: {last}")

def rpc(url, method, params):
    return post(url, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params})

@functools.lru_cache(maxsize=None)
def block_ts(url, n):
    return int(rpc(url, "eth_getBlockByNumber", [hex(n), False])["timestamp"], 16)

import functools
@functools.lru_cache(maxsize=None)
def block_at(url, ts, hi=None):
    """ts 이하 시각의 마지막 블록 번호(이분 탐색)."""
    hi = hi or int(rpc(url, "eth_blockNumber", []), 16)
    lo = 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if block_ts(url, mid) <= ts: lo = mid
        else: hi = mid - 1
    return lo

def call_uint(url, to, data, block):
    r = rpc(url, "eth_call", [{"to": to, "data": data}, hex(block) if isinstance(block, int) else block])
    return int(r, 16)

def total_supply(url, token, block): return call_uint(url, token, "0x18160ddd", block)
def balance_of(url, token, owner, block):
    return call_uint(url, token, "0x70a08231" + owner.lower().replace("0x", "").rjust(64, "0"), block)

def utc(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp())

def save_gz(name, obj):
    with gzip.open(os.path.join(RAW, name), "wt") as f: json.dump(obj, f)
