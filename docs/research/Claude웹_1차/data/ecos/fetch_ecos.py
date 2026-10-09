"""한국은행 ECOS에서 R03, R04, R05 근거 계열을 정식 키로 받아 CSV로 저장한다.
키는 레포 루트 .env.local의 ECOS_API_KEY. 키와 요청 주소는 출력하지 않는다.
사용: python3 fetch_ecos.py   (결과는 이 폴더에 저장)"""
import csv, json, pathlib, urllib.request

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[4]
KEY = next(l.split('=', 1)[1].strip() for l in (ROOT / '.env.local').read_text().splitlines() if l.startswith('ECOS_API_KEY='))

# (주기, 표, 항목 코드들, 열 이름) — 표와 항목은 2026-10-09 ECOS 표 찾기 결과에서 확인된 것
SERIES = [
    ('M', '191Y001', ['0200000', '4'], '국고채_잔액'),
    ('M', '191Y001', ['0200000', '3'], '국고채_발행액'),
    ('M', '191Y001', ['0800000', '4'], '통안증권_잔액'),
    ('M', '191Y001', ['0800000', '3'], '통안증권_발행액'),
    ('M', '103Y002', ['BCAA215'], '통안증권_한은계정_말잔'),
    ('M', '103Y002', ['BCAA117'], '한은_RP매입_말잔'),
    ('M', '103Y002', ['BCAA216'], '한은_RP매각_말잔'),
    ('M', '104Y013', ['BCB6'], '예금은행_RP매도_말잔'),
    ('M', '901Y056', ['S23C'], '금투협_RP'),
    ('M', '121Y013', ['BEABAB2122'], '은행_RP매도_금리_잔액기준'),
    ('M', '121Y002', ['BEABAA222'], '은행_RP매도_금리_신규'),
    ('M', '104Y015', ['BDAA1'], '예금은행_총예금_말잔'),
    ('M', '104Y015', ['BDAA2'], '예금은행_요구불예금_말잔'),
    ('M', '104Y009', ['1040100'], '요구불예금_가계'),
    ('M', '104Y009', ['1040200'], '요구불예금_기업'),
    ('M', '161Y004', ['BBKA00'], 'M1_말잔_원계열'),
    ('M', '161Y008', ['BBGA00'], 'M2_말잔_원계열'),
    ('M', '161Y001', ['BBLS00'], 'M1_평잔_계절조정'),
    ('M', '161Y005', ['BBHS00'], 'M2_평잔_계절조정'),
    ('M', '722Y001', ['0101000'], '기준금리'),
    ('Q', '282Y001', ['A121', 'D01'], '중앙정부_단기_명목'),
    ('Q', '282Y001', ['A121', 'D021'], '중앙정부_잔존1년이하_명목'),
    ('Q', '282Y001', ['A111', 'D01'], '한국은행_단기_명목'),
    ('Q', '282Y001', ['A111', 'D021'], '한국은행_잔존1년이하_명목'),
    ('Q', '282Y002', ['A121', 'D01'], '중앙정부_단기_시가'),
    ('Q', '282Y002', ['A121', 'D021'], '중앙정부_잔존1년이하_시가'),
    ('Q', '282Y002', ['A111', 'D01'], '한국은행_단기_시가'),
    ('Q', '282Y002', ['A111', 'D021'], '한국은행_잔존1년이하_시가'),
    ('D', '817Y002', ['010101000'], '콜금리_1일'),
    ('D', '817Y002', ['010502000'], 'CD_91일'),
    ('D', '817Y002', ['010400000'], '통안증권_91일'),
    ('D', '817Y002', ['010400001'], '통안증권_1년'),
    ('D', '817Y002', ['010190000'], '국고채_1년'),
    ('D', '817Y002', ['010901000'], 'KOFR'),
]
PERIOD = {'M': ('202301', '202612'), 'Q': ('2023Q1', '2026Q4'), 'D': ('20230101', '20261231')}
NAME = {'M': '월별', 'Q': '분기별', 'D': '일별'}


def fetch(cycle, stat, items):
    a, b = PERIOD[cycle]
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{KEY}/json/kr/1/100000/{stat}/{cycle}/{a}/{b}/' + '/'.join(items) + '/'
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            d = json.loads(r.read().decode('utf-8'))
    except Exception as e:  # 예외 문자열에 주소(키)가 섞일 수 있어 종류만 남긴다
        return [], type(e).__name__
    if 'StatisticSearch' not in d:
        return [], json.dumps(d.get('RESULT', d), ensure_ascii=False)[:120]
    return d['StatisticSearch']['row'], ''


def main():
    raw, tables, log = {}, {c: {} for c in NAME}, []
    for cycle, stat, items, col in SERIES:
        rows, err = fetch(cycle, stat, items)
        r0 = rows[0] if rows else {}
        raw[col] = {'stat': stat, 'stat_name': r0.get('STAT_NAME', ''), 'items': items,
                    'item_names': [r0.get(f'ITEM_NAME{i}', '') for i in range(1, len(items) + 1)],
                    'unit': r0.get('UNIT_NAME', '').strip(), 'cycle': cycle, 'rows': [[r['TIME'], r['DATA_VALUE']] for r in rows]}
        unit = rows[0].get('UNIT_NAME', '') if rows else ''
        for r in rows:
            tables[cycle].setdefault(r['TIME'], {})[f'{col}({unit.strip()})' if unit else col] = r['DATA_VALUE']
        log.append(f'{cycle} {stat} {"/".join(items)} {col}: {len(rows)}행' + (f' {rows[0]["TIME"]}~{rows[-1]["TIME"]}' if rows else '') + (f' 오류 {err}' if err else ''))
    (HERE / 'ecos_정식키_raw.json').write_text(json.dumps(raw, ensure_ascii=False, indent=1))
    for cycle, t in tables.items():
        cols = sorted({k for v in t.values() for k in v}, key=lambda k: [s[3] for s in SERIES].index(k.split('(')[0]))
        times = sorted(t)
        if not times: continue
        with open(HERE / f'ecos_{NAME[cycle]}_{times[0]}_{times[-1]}.csv', 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['시점'] + cols)
            for tm in times: w.writerow([tm] + [t[tm].get(c, '') for c in cols])
    print('\n'.join(log))


if __name__ == '__main__':
    main()
