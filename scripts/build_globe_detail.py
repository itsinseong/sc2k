#!/usr/bin/env python3
"""홍콩, 싱가포르, 한국 나라 화면용 고해상도 지도(site/data/world-detail.json) 생성.

Natural Earth 1:10m 국가 경계를 지역 상자로 잘라 둠. 50m 지도는 이 배율에서 너무 거칠다
(홍콩 40점, 싱가포르 9점). 상자는 globe.js의 나라 화면(상자 360x330, R = k*360, 시점, FY)이
보여 주는 범위에 여유를 더해 계산함. 사용: python3 scripts/build_globe_detail.py
"""
import json, math, os, tempfile, urllib.request
from pathlib import Path
from shapely.geometry import shape, box, mapping
from shapely.geometry.polygon import orient

URL = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson'
SRC = Path(os.environ.get('NE_CACHE') or Path(tempfile.gettempdir()) / 'ne_10m_admin_0_countries.geojson')
OUT = Path(__file__).resolve().parent.parent / 'site' / 'data' / 'world-detail.json'
W, H, FY = 360, 330, 0.34  # globe.js와 같은 값
# 지역: 시점(경도, 위도), k(구 반지름 / 상자 너비), 보이는 범위 양옆에 더하는 비율, 단순화 허용 오차(도).
# 한국은 한 점이 0.05도(1픽셀)라 0.005도로 줄여도 0.1픽셀 미만
REGIONS = {'hk': ((114.1, 22.35), 18, 0.5, 0.001), 'sg': ((103.82, 1.35), 20, 0.5, 0.001), 'kr': ((127.5, 36), 3, 0.2, 0.005)}
SHOW = {'hk': ['344', '446', '156'], 'sg': ['702', '458', '360'], 'kr': ['410', '408', '392']}


def visible_bbox(view, k, margin):
    """상자 둘레를 정사영 역변환해 경위도 범위를 얻고 margin 만큼 넓힘."""
    R, cx, cy = k * W, W / 2, FY * H
    lon0, lat0 = (math.radians(v) for v in view)
    cl, sl, cp, sp = math.cos(lon0), math.sin(lon0), math.cos(lat0), math.sin(lat0)
    lons, lats = [], []
    for i in range(41):
        t = i / 40
        for x, y in ((t * W, 0), (t * W, H), (0, t * H), (W, t * H)):
            sx, sy = (x - cx) / R, (cy - y) / R
            d = math.sqrt(max(0, 1 - sx * sx - sy * sy))
            X = -sl * sx - sp * cl * sy + cp * cl * d
            Y = cl * sx - sp * sl * sy + cp * sl * d
            Z = cp * sy + sp * d
            lons.append(math.degrees(math.atan2(Y, X))); lats.append(math.degrees(math.asin(Z)))
    w, e, s, n = min(lons), max(lons), min(lats), max(lats)
    dx, dy = (e - w) * margin, (n - s) * margin
    return [round(w - dx, 3), round(s - dy, 3), round(e + dx, 3), round(n + dy, 3)]


def main():
    if not SRC.exists():
        print('download', URL); SRC.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL, SRC)
    feats = json.loads(SRC.read_text())['features']
    geoms = []
    for f in feats:
        p = f['properties']; i = str(p.get('ISO_N3', '-99'))
        iso = i.zfill(3) if i not in ('-99', '') else p['ADM0_A3']
        g = shape(f['geometry'])
        geoms.append((iso, g if g.is_valid else g.buffer(0)))
    out = {}
    for name, (view, k, margin, tol) in REGIONS.items():
        bb = visible_bbox(view, k, margin); b = box(*bb); countries = {}
        for iso, g in geoms:
            if not g.intersects(b): continue
            c = g.intersection(b).simplify(tol, preserve_topology=True)
            rings = []
            for poly in getattr(c, 'geoms', [c]):
                if poly.geom_type != 'Polygon' or poly.is_empty: continue
                poly = orient(poly, 1.0)  # 바깥 고리와 구멍의 감는 방향을 반대로(nonzero 채우기용)
                for r in [poly.exterior, *poly.interiors]:
                    pts = [[round(x, 4), round(y, 4)] for x, y in r.coords[:-1]]  # 닫는 점 제외(decode와 같은 형식)
                    if len(pts) >= 3: rings.append(pts)
            if rings: countries.setdefault(iso, []).extend(rings)
        out[name] = {'bbox': bb, 'countries': countries}
        print(name, bb, {i: sum(len(r) for r in countries.get(i, [])) for i in SHOW[name]})
    OUT.write_text(json.dumps(out, separators=(',', ':')))
    print('wrote', OUT, OUT.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
