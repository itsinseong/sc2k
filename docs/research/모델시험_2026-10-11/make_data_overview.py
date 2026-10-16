"""현황판 '자료' 탭 본문(수집, 학습 자료, 이전 파인튜닝, 합성 계획, 학습 환경). 숫자는 파일에서 센다. make_status2.py가 불러 쓴다."""
import csv, html, json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
FT = HERE.parent / '파인튜닝_2026-10-11'
CSS = pathlib.Path.home() / '.claude/skills/doc-html/두리번.css'
E = html.escape


def rows(p):
    p = FT / p
    return sum(1 for _ in csv.DictReader(open(p, encoding='utf-8'))) if p.exists() else 0


def jl(p):
    p = FT / p
    return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()] if p.exists() else []


def table(head, body, cls='mx'):
    h = ''.join(f'<th{" class=\"c\"" if i else ""}>{E(x)}</th>' for i, x in enumerate(head))
    b = ''.join('<tr>' + ''.join(f'<td{" class=\"rw\"" if i == 0 else " class=\"c\"" if isinstance(x, int) else ""}>{x if isinstance(x, str) and x.startswith("<") else E(str(x))}</td>'
                                 for i, x in enumerate(r)) + '</tr>' for r in body)
    return f'<div class="tw"><table class="{cls}"><tr>{h}</tr>{b}</table></div>'


tag = lambda t, kind='': f'<span class="tag{(" " + kind) if kind else ""}">{E(t)}</span>'
TBD = '<span class="tbd">미정</span>'
DONE, WAIT, NEVER = tag('학습 자료', 'a'), tag('아직 안 넣음'), '<span class="tag x">학습 금지(시험용)</span>'
REAL, SYN = '<span class="kind real">실제</span>', '<span class="kind syn">합성</span>'


def sections():
    tv2, tv3, tv4 = jl('sets/train_v2.jsonl'), jl('sets/train_v3.jsonl'), jl('sets/train_v4.jsonl')
    val, fin = jl('sets/valid_v3.jsonl'), jl('sets/final_v1.jsonl')
    asset_share = sum(r['task'] == 'asset' for r in tv3)

    # 1. 흐름
    flow = ('<div class="tl"><div class="A" style="flex:1">실제 문서 수집</div><div class="A" style="flex:1">AI 두 독자 라벨</div>'
            '<div class="A" style="flex:1">학습 자료</div><div class="A" style="flex:1">파인튜닝</div>'
            '<div class="B" style="flex:1">검증 세트</div><div class="B" style="flex:1">최종 시험(한 번)</div></div>'
            '<div class="tll"><span style="flex:1">공개 PDF, 웹, DART</span><span style="flex:1">Sonnet 첫 라벨, Opus 대조, 일치만</span>'
            '<span style="flex:1">지금까지 실제, 앞으로 합성</span><span style="flex:1">데스크톱, RunPod</span>'
            '<span style="flex:1">모델 고르기, 기준 정하기</span><span style="flex:1">실제 문서만, 학습과 회사 분리</span></div>')

    # 2. 수집
    col = [
        ('학습용 준비금 보고서(1차)', rows('manifest/rep-a.csv') + rows('manifest/rep-b.csv'), DONE, '문항 만들어 v2부터 사용'),
        ('학습용 준비금 보고서(같은 회사 다른 달)', rows('manifest/rep-c.csv'), WAIT, '문항은 만들었고 v4에만 들어감'),
        ('학습용 자산 표(펀드, 은행, 증권사)', rows('manifest/asset-mmf.csv') + rows('manifest/asset-mmf_kr_terms.csv'), DONE, 'v2부터 사용'),
        ('학습용 약관, 백서(R14)', rows('manifest/terms.csv'), DONE, 'v2부터 사용'),
        ('학습용 긴 문서(12,000자 초과)', 17, WAIT, '라벨 끝, 조각 114개 준비'),
        ('학습용 새 문서(2차 조사 + 다른 양식)', rows('manifest/rep-d.csv'), WAIT, '받음, 라벨 전'),
        ('검증, 최종 시험 문서(영어)', rows('manifest_eval/eval-a.csv') + rows('manifest_eval/eval-b.csv') + rows('manifest_eval/eval-terms.csv'), NEVER, '고정'),
        ('검증 보충 문서(Wenia, Kinesis, Coins.ph)', rows('manifest_eval/eval-c.csv'), NEVER, '라벨 끝, 두 독자 일치 68문항'),
        ('한국어 DART 감사보고서', rows('build/dart_raw_manifest.csv'), NEVER, '받음, 라벨 전'),
        ('한국어 선불충전금, 정산자금 공시', rows('build/ko_notice_manifest.csv'), NEVER, '받음, 라벨 전'),
    ]
    t_col = table(['묶음', '종류', '문서 수', '학습에', '상태'], [(a, REAL, b, c, d) for a, b, c, d in col])

    # 3. 학습 자료
    t_train = table(['판', '종류', '문항 수', '학습에', '구성'], [
        ('v2', REAL, len(tv2), DONE, '실제 문서. 자산 줄, 보고서 문항, 약관'),
        ('v3', REAL, len(tv3), DONE, 'v2와 같은 문서. R11 넓게 아니오 12개를 3번씩 반복해 24행 추가(새 문서 없음)'),
        ('v4', REAL, len(tv4), WAIT, f'v3 고유 1,025 + 새 {len({r["id"] for r in tv4} - {r["id"] for r in tv3})}문항(다른 달 보고서, 옛 검증 문항). 예 쪽 쏠림'),
        ('긴 문서 조각', REAL, len(jl('build/long_chunks_candidate_cap2.jsonl')), WAIT, '12,000자 넘는 학습 문서 17건을 조각냄'),
        ('합성 ①(syn_v1)', SYN, len(jl('sets/syn_v1.jsonl')), DONE, f'실제 학습 문서에서 한 군데만 고친 문서. 만든 {sum(len(jl(f"items_syn/{n}.jsonl")) for n in ("syn-a", "syn-b", "syn-c", "syn-d"))}개 중 Opus 확인 통과분'),
    ])

    # 3-2. 학습 파일 구성(질문 종류별 문항 수)
    syn = jl('sets/syn_v1.jsonl')
    ko = lambda rs: sum(any('가' <= ch <= '힣' for ch in str(r['state'])) for r in rs)

    def cell(rs, task):
        g = [r['gold'] for r in rs if r['task'] == task]
        if not g:
            return '<span class="mut">0</span>'
        if task in ('asset', 'R08'):
            return f'<span>{len(g)}<span class="mut"> ({len(set(g))}종)</span></span>'
        return f'예 {g.count("true")}, 아니오 {g.count("false")}'
    kinds = [('asset', '자산', '준비금 표의 한 줄이 무슨 자산인지 고르기(국채, 예금, MMF 등)'),
             ('R08', 'R08 감사 종류', '회계사 확인이 검토, 정식 확인, 합의 절차 중 무엇인지, 확인이 없는지 고르기'),
             ('R11_broad', 'R11 넓게', '유통량이 무엇을 세는지 문서가 밝혔는가'),
             ('R11_narrow', 'R11 좁게', '유통량 계산식(발행 − 소각 − 발행사 보유분)을 보였는가'),
             ('R12', 'R12', '준비금을 맡은 은행, 수탁 기관 이름이 있는가'),
             ('R14', 'R14', '보유자에게 이자를 주지 않는다는 문구가 있는가'),
             ('R15', 'R15', '경영진이 이름과 직함으로 서명했는가')]
    sets = [tv2, tv3, tv4, syn]
    t_comp = table(['질문 종류', '묻는 것', 'v2', 'v3', 'v4', '합성 ①'],
                   [(n, d, *(cell(rs, k) for rs in sets)) for k, n, d in kinds]
                   + [('합계', '', *(f'<b>{len(rs)}</b>' for rs in sets)),
                      ('한국어 문항', '', *(str(ko(rs)) for rs in sets))], cls='mx comp')

    trained = rows('manifest/rep-a.csv') + rows('manifest/rep-b.csv') + rows('manifest/asset-mmf.csv') + rows('manifest/asset-mmf_kr_terms.csv') + rows('manifest/terms.csv')
    waiting = rows('manifest/rep-c.csv') + 17 + rows('manifest/rep-d.csv')
    never = sum(rows(f) for f in ('manifest_eval/eval-a.csv', 'manifest_eval/eval-b.csv', 'manifest_eval/eval-terms.csv', 'manifest_eval/eval-c.csv', 'build/dart_raw_manifest.csv', 'build/ko_notice_manifest.csv'))
    buckets = (f'<div class="three"><div class="tile"><div class="v">{trained}</div><div class="l">{DONE} 학습에 쓴 문서</div><div class="s">v2, v3 학습 자료가 된 문서</div></div>'
               f'<div class="tile"><div class="v">{waiting}</div><div class="l">{WAIT} 학습 후보</div><div class="s">받았거나 문항까지 만들었지만 아직 학습 안 함</div></div>'
               f'<div class="tile"><div class="v">{never}</div><div class="l">{NEVER}</div><div class="s">검증, 최종 시험, 한국어 시험 재료. 학습에 절대 안 씀</div></div></div>')

    # 5. 시험지
    t_test = table(['시험지', '문항', '회사', '상태', '쓰는 법'], [
        ('처음 시험', 277, '-', '여러 번 봄', '참고값'),
        ('검증 세트', len(val), '13', '고정, 쏠림 있음(BRLA 43%)', '모델 고르기, 기준 정하기'),
        ('검증 판단용', 245, '13', '고정(회사당 6건 상한)', '공식 비교'),
        ('검증 보충', 68, '3', '두 독자 일치분 확정(84문항 중 68)', 'BRLA 쏠림 줄이기(효과는 작음)'),
        ('최종 시험(영어)', len(fin), '26', '고정, 자산 문항 점검 예정', '마지막에 한 번'),
        ('한국어 검증', '만들 예정', '2', '빗썸(거래소, 감사보고서 5), NHN페이코(선불, 감사보고서 9 + 공시 7)', '한국어 판단'),
        ('한국어 최종 시험', '만들 예정', '20', '나머지 회사 전부(감사보고서 165 + 공시 100)', '마지막에 한 번'),
    ])

    # 6. 합성 계획
    t_syn = table(['과제', '고치는 것', '정답'], [
        ('R11 넓게', '유통량이 무엇을 세는지 밝힌 문장 넣기, 빼기', '예, 아니오'),
        ('R11 좁게', '발행 − 소각 − 발행사 보유분 = 유통량 같은 계산 줄 넣기, 빼기', '예, 아니오'),
        ('R12', '준비금을 맡은 은행, 수탁 기관 이름 넣기, 빼기', '예, 아니오'),
        ('R14', '이자 없음 문구 넣기, 빼기', '예, 아니오'),
        ('R15', '경영진 서명란의 이름과 직함 넣기, 빼기, 감사인만 서명', '예, 아니오'),
    ])

    t_env = table(['모델', '학습', '정밀도', '시간당', '근거'], [
        ('Kanana 1.5 8B', '데스크톱 RTX 2070 SUPER(8GB)', 'fp16, GradScaler 추가', '0', 'v3 학습을 이 장비에서 끝까지 마친 적 있음. 이 장비는 bf16을 지원하지 않음'),
        ('Gemma 4 E4B', 'RunPod RTX 4090(24GB)', 'bf16', '약 0.34달러', '데스크톱 8GB에서 못 올림'),
        ('GPT-OSS-20B', 'RunPod RTX 4090(24GB), 부족하면 A6000(48GB)', 'bf16', '약 0.34달러, 0.49달러', 'T4 15GB에서 메모리 부족. fp16에서는 전문가층 값이 넘쳐 발산할 수 있음'),
        ('채점(세 모델)', 'RunPod 한 곳', '모델별 학습과 같음', '', 'GPT-OSS가 데스크톱에 안 올라감. 같은 곳, 같은 코드로 채점'),
    ])
    return f'''

<section><h2>1. 흐름</h2><p class="sub">{REAL} 공개 문서에서 그대로 만든 자료 &nbsp; {SYN} 실제 학습 문서를 한 군데만 고쳐 만든 자료(학습에만 씀)</p>{flow}
{buckets}
</section>

<section><h2>2. 수집한 실제 문서 {REAL}</h2>{t_col}
<p class="cav">학습 쪽과 시험 쪽은 회사가 겹치지 않는다. 처음 시험(277문항)에 쓴 회사는 어디에도 쓰지 않는다. 문서마다 출처 주소가 있다.</p></section>

<section><h2>3. 학습 자료</h2>{t_train}
<ul><li>v2, v3는 전부 실제 문서다. 라벨은 AI 두 독자가 일치한 것만 썼다.</li>
<li>v3의 {asset_share}/{len(tv3)}문항이 자산 줄이고, 대부분 일반 펀드, ETF 보유 표에서 왔다.</li></ul>
<h3>학습 파일 구성</h3>
<p class="sub">'예 44, 아니오 12'는 정답이 예인 문항 44개, 아니오인 문항 12개라는 뜻이다. 한쪽이 많으면 모델이 그쪽으로 답하는 버릇을 배운다. 자산과 R08은 예, 아니오가 아니라 보기 중 하나를 고르는 문항이다.</p>
{t_comp}
<ul><li><b>v2</b>: 실제 문서로 만든 첫 정식 학습 파일. 문항의 {round(asset_share / len(tv3) * 100)}%가 자산이다. 한국어는 자산 줄 일부뿐이다.</li>
<li><b>v3</b>: v2와 문서가 같다. R11 넓게의 아니오 12개를 3번씩 넣어 24행이 늘었다. 고유 문항은 {len({r['id'] for r in tv3})}개로 v2와 같다.</li>
<li><b>v4</b>: 같은 회사의 다른 달 보고서를 더했다. 문항은 늘었지만 R11 넓게, R15에서 예가 많아져 넣지 않는다.</li>
<li><b>합성 ①</b>: v3에 부족한 쪽(R11 넓게 아니오, R11 좁게 예, R15 아니오 등)을 채운다. 자산, R08, 한국어 문항은 없다. ②에서 v3에 더해 {len(tv3) + len(syn)}문항으로 학습한다.</li></ul></section>

<section><h2>4. 합성 데이터 계획 {SYN}</h2>{t_syn}
<ul><li>재료는 학습 쪽 실제 문서뿐이다. 검증, 최종 시험 문서는 쓰지 않는다.</li>
<li>Sonnet이 만들고, Opus가 목표 정답을 모른 채 다시 판정해 같고 자연스러운 것만 쓴다. 만든 276개 중 186개가 통과했다.</li>
<li>R11 좁게 '아니오'와 R15 '예'는 합성으로 만들기 어려워 실제 자료로 채운다(실제 학습 자료에 각각 67개, 76개).</li><li>실제 검증 세트에서 나아지지 않으면 버린다.</li>
<li>체인별 합계 경계는 A(계산 아님)로 정했다. B로 했을 때 점수도 함께 본다.</li>
<li>비교: 같은 GPU에서 A(실제 v3만)와 B(실제 v3 + 합성 186개)를 학습해 검증 세트로 비교한다.</li></ul></section>

<section><h2>5. 학습 환경</h2>
<p class="sub">GPU 한 대로 모델을 차례로 돌린다. 여러 대를 동시에 빌리면 빨리 끝날 뿐 총비용은 비슷하다.</p>
{t_env}
<ul><li>가격은 2026년 중반 커뮤니티 클라우드 기준이다. 결제 전에 RunPod 화면 값으로 확인한다.</li>
<li>한 모델 안에서는 장비와 정밀도를 바꾸지 않는다. 모델끼리는 달라도 되고 결과표에 적는다.</li>
<li>RunPod 저장 공간은 Pod를 멈춰도 과금된다. 쓰지 않을 때는 지운다.</li></ul></section>

'''


EXTRA_CSS = '.tiles{margin-top:18px}table.mx td{white-space:normal}.tag.x{border-color:#111;background:#111;color:#fff}h2 .kind{font-size:13px;margin-left:6px}.three{margin-top:18px}.mut{color:#85857f}table.comp td:nth-child(n+3){white-space:nowrap}table.comp td.rw{width:12%}table.comp td:nth-child(2){width:34%}.tile .l .tag{margin-right:6px}'
