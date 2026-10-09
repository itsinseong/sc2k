"""레포 루트 .env.local의 Atlassian 값으로 Jira와 Confluence를 한 번씩 불러 되는지만 본다. 토큰과 이메일은 출력하지 않는다."""
import base64, json, pathlib, urllib.request, urllib.error

env = {}
for line in (pathlib.Path(__file__).resolve().parents[2] / '.env.local').read_text().splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.split('=', 1); env[k.strip()] = v.strip()
site, email, token = env.get('ATLASSIAN_SITE', ''), env.get('ATLASSIAN_EMAIL', ''), env.get('ATLASSIAN_API_TOKEN', '')
print('값:', {k: ('있음' if env.get(k) else '없음') for k in ('ATLASSIAN_SITE', 'ATLASSIAN_EMAIL', 'ATLASSIAN_API_TOKEN')})
auth = 'Basic ' + base64.b64encode(f'{email}:{token}'.encode()).decode()

def get(path):
    req = urllib.request.Request(site + path, headers={'Authorization': auth, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None

s, me = get('/rest/api/3/myself'); print('Jira 내 계정:', s, '(이름 있음)' if me and me.get('displayName') else '')
s, pr = get('/rest/api/3/project/search'); print('Jira 스페이스:', s, [p['key'] + ' ' + p['name'] for p in (pr or {}).get('values', [])])
s, sp = get('/wiki/api/v2/spaces?keys=SC2K'); print('Confluence SC2K:', s, [x.get('key', '') + ' ' + x.get('name', '') for x in (sp or {}).get('results', [])])
