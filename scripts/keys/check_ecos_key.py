"""레포 루트 .env.local의 ECOS_API_KEY로 ECOS를 한 번 불러 키가 되는지만 확인한다. 키와 요청 주소는 출력하지 않는다."""
import json, pathlib, urllib.request

env = {}
for line in (pathlib.Path(__file__).resolve().parents[2] / '.env.local').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.split('=', 1); env[k.strip()] = v.strip()
key = env.get('ECOS_API_KEY', '')
print('ECOS_API_KEY', '있음' if key else '없음', f'(길이 {len(key)}자)' if key else '')
if key:
    # 한국은행 기준금리(722Y001, 항목 0101000) 2024-01~2025-08 월별 20건. 시험 키(sample)는 10건을 넘으면 오류가 난다.
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{key}/json/kr/1/20/722Y001/M/202401/202508/0101000'
    with urllib.request.urlopen(url, timeout=30) as r:
        d = json.loads(r.read().decode('utf-8'))
    if 'StatisticSearch' in d:
        rows = d['StatisticSearch']['row']
        print('응답 행', len(rows), '| 첫 행', rows[0]['TIME'], rows[0]['DATA_VALUE'], '| 마지막 행', rows[-1]['TIME'], rows[-1]['DATA_VALUE'])
    else:
        print('오류 응답:', json.dumps(d.get('RESULT', d), ensure_ascii=False)[:200])
print('TYPESAFE_API_KEY', '있음' if env.get('TYPESAFE_API_KEY') else '없음')
