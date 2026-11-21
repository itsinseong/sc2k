#!/usr/bin/env python3
"""최종 발표 덱(~/HTML/미디어프로젝트_SC2K/발표/최종/SC2K_최종_발표.html)을 만든다.
틀은 2차 레퍼런스 덱(표지, 머리, CSS), 그림과 문구는 포스터(바밤바형)에서 가져온다.
목차는 혜인 최종 발표 구성(소개, 내용, 단계별 (1)~(5), 결과, 기대효과, 느낀점)을 따른다."""
import io
import re
import shutil
from pathlib import Path

import qrcode
import qrcode.image.svg

H = Path.home() / 'HTML/미디어프로젝트_SC2K'
REF = H / '발표/레퍼런스/SC2K_Reference_분석.html'
POSTER = H / '포스터/SC2K_포스터_바밤바형.html'
OUT_DIR = H / '발표/최종'
OUT = OUT_DIR / 'SC2K_최종_발표.html'
IMGS = ['s_hero.png', 's_kr.png', 's_flow.png', 's_reports.png', 's_rules.png', 's_us.png']

ref = REF.read_text('utf-8')
poster = POSTER.read_text('utf-8')

head = ref[:ref.find('</style>')].replace('<title>SC2K Reference 분석</title>', '<title>SC2K 최종 발표</title>')
cover = re.search(r'<section class="slide cover">.*?</section>', ref, re.S).group(0)
cover = cover.replace('<p class="kicker">2026-2 미디어프로젝트</p>', '<p class="kicker">2026-2 미디어프로젝트 24조</p>')
cover = cover.replace('<h1><span class="jost">Reference</span> 분석</h1>',
                      '<h1><span class="jost">Final</span> 프로젝트</h1><p class="sub1">원화 스테이블코인 준비금 공시 판정 체계</p>')
logos = re.search(r'<span class="lgm">.*?GPT-OSS-20B</span>', ref, re.S).group(0)  # Kanana, Gemma, GPT-OSS 로고 3개


def svg_at(marker, n=1):
    """포스터에서 marker 뒤 n번째 svg"""
    i = poster.find(marker)
    for _ in range(n):
        i = poster.find('<svg', i + 1)
    return poster[i:poster.find('</svg>', i) + 6]


arch = svg_at('<div class="dg fit"')
arch_inner = arch[arch.find('>') + 1:-6]
tech_icons = []
for m in re.finditer(r'<div class="hd">(.*?)<b>', poster, re.S):
    tech_icons.append(m.group(1))
mas_icon = svg_at('class="mas"')


def qr(url):
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=1)
    b = io.BytesIO()
    img.save(b)
    return re.sub(r'<\?xml.*?\?>', '', b.getvalue().decode())


STEPS = ['소개', '개발 과정', '결과', '기대효과']


def frame(cls, step, num, label, sub, body):
    steps = ''.join(f'<span{" class=\"on\"" if i == step else ""}><em>{s}</em></span>' for i, s in enumerate(STEPS))
    sub = f'<span class="sub2">{sub}</span>' if sub else ''
    return f'''<section class="slide {cls}">
  <div class="band"></div>
  <div class="steps">{steps}</div>
  <div class="tag"><span class="num jost">{num}</span><span class="label">{label}</span>{sub}</div>
{body}
</section>
'''


def lab(items):
    return '<div class="lb">' + ''.join(f'<div><p class="k">{k}</p><p class="v">{v}</p></div>' for k, v in items) + '</div>'


def ph(text):
    return f'<div class="ph"><span>작성 전</span>{text}</div>'


ICON = {  # 단계 아이콘: 선 그림 하나씩
    'collect': '<svg viewBox="0 0 48 48"><path d="M8 12h12l4 4h16v22H8z"/><path d="M16 26h16M16 32h10"/></svg>',
    'read': '<svg viewBox="0 0 48 48"><rect x="9" y="6" width="24" height="32" rx="2"/><path d="M15 14h12M15 20h12M15 26h7"/><circle cx="33" cy="33" r="7"/><path d="M38 38l5 5"/></svg>',
    'rule': '<svg viewBox="0 0 48 48"><circle cx="12" cy="12" r="4"/><circle cx="36" cy="12" r="4"/><circle cx="24" cy="36" r="4"/><path d="M15 14l7 18M33 14l-7 18M16 12h16"/></svg>',
    'loop': '<svg viewBox="0 0 48 48"><path d="M38 20a14 14 0 0 0-26-5"/><path d="M12 8v7h7"/><path d="M10 28a14 14 0 0 0 26 5"/><path d="M36 40v-7h-7"/></svg>',
    'model': '<svg viewBox="0 0 48 48"><rect x="8" y="10" width="32" height="22" rx="2"/><path d="M18 40h12M24 32v8"/><path d="M16 22l5 4 10-9"/></svg>',
}

FAV = 'img/fav/'  # 출처 파비콘(미리 받아 둠)


def fav(d):
    return f'<img class="fv" src="{FAV}{d}.png" alt="">'


def crop(x, y, w, h, cls=''):
    """포스터 구성도에서 한 부분만 잘라 남색 바탕용으로 그린다"""
    return f'<svg class="dg dk {cls}" viewBox="{x} {y} {w} {h}">{arch_inner}</svg>'


def svgs(block):
    return re.findall(r'<svg.*?</svg>', block, re.S)


slides = [cover]

# 01 프로젝트 소개
slides.append(frame('intro3', 0, '01', '프로젝트 소개', '', f'''  <div class="vid"><img src="img/s_hero.png" alt="SC2K 종합 판정 화면"></div>
  {lab([
    ('형식', '원화 스테이블코인 준비금 공시 판정 사이트<small>sc2k.kr</small>'),
    ('계기', '원화 스테이블코인 법안 10건이 발의됐지만 준비금 기준은 법안마다 다름. 미국, EU, 홍콩, 싱가포르, 일본은 규칙을 시행하거나 정함'),
    ('판정 대상', '8개 코인 준비금 검증 보고서 264건'),
    ('핵심 목표', '해외 5개 관할 규칙을 판정 규칙 15개로 정리하고, 한국 공시 기준의 후보값을 근거와 함께 제안'),
  ])}'''))

# 02 프로젝트 내용: 단계 5개
PIPE = [
    ('collect', '문서 수집과 유통량 대조', '발행사 공시, 법안 원문<br>체인 4종, 공공 데이터'),
    ('read', '보고서 읽기', 'PaddleOCR-VL, Jev<br>LLM(Claude, Gemini, GPT)'),
    ('rule', '규칙 판정', '온톨로지<br>규칙 R01~R15'),
    ('loop', '하네스', '정답 세트 채점<br>틀린 칸 고침'),
    ('model', '내부망 판정 모델', '공개 LLM 3종<br>LoRA 파인튜닝'),
]
pipe = ''.join(f'<div><i class="jost">0{i + 1}</i>{ICON[k]}<b>{n}</b><span>{t}</span></div>' for i, (k, n, t) in enumerate(PIPE))
slides.append(frame('pipe5', 1, '02', '프로젝트 내용', '', f'  <div class="pipe">{pipe}</div>'))

# 02 전체 구조: 외부망, 은행 내부망 한 장씩. 판은 남색 바탕에 그대로 얹는다
ZONES = [('공시 감시', 'OCI 서버가 발행사 공시와 법안을 5분, 30분마다 확인, 원문은 OCI 보관소, 웹 아카이브, Mac 세 곳에 저장'),
         ('온톨로지', '규칙 R01~R15, 자산 16종, 원문 근거. 바뀐 기준과 공개 자료 API의 영향 요인을 반영'),
         ('하네스 엔지니어링', '파서와 OCR, Jev와 Decisions, LLM(Claude, Gemini, GPT 중 하나)이 읽고 채점, 틀린 칸은 프롬프트와 컨텍스트를 고침'),
         ('배포와 알림', '확정 값은 GitHub를 거쳐 sc2k.kr에 배포, 판정 변화는 Jira 이슈와 Confluence로')]
zl = ''.join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in ZONES)
slides.append(frame('archs', 1, '02', '프로젝트 내용', '전체 구조, 외부망', f'''  {crop(-334, -503, 1714, 1286, 'a1')}
  <ol class="zones">{zl}</ol>'''))
slides.append(frame('archs', 1, '02', '프로젝트 내용', '전체 구조, 은행 내부망', f'  {crop(-334, 827, 1714, 829, "a2")}'))

# 02 (1) 문서 수집과 유통량 대조
COINS = [('circle.com', 'Circle USDC'), ('circle.com', 'Circle EURC'), ('paxos.com', 'Paxos PYUSD'), ('paxos.com', 'Paxos USDP'),
         ('paxos.com', 'Paxos USDG'), ('ripple.com', 'Ripple RLUSD'), ('gemini.com', 'Gemini GUSD'), ('tether.to', 'Tether USDT')]
API = [('문서와 법령', [('open.assembly.go.kr', '열린국회정보', '법안 원문'), ('law.go.kr', '법제처 국가법령정보', '법령'),
                     ('dart.fss.or.kr', 'OpenDART', '공시'), ('web.archive.org', 'Wayback Machine', '원문 보관')]),
       ('체인', [('etherscan.io', 'Etherscan', '발행, 소각 기록'), ('solscan.io', 'Solscan', '솔라나'), ('tronscan.org', 'TronGrid', '트론'),
               ('ethereum.org', '이더리움 RPC', 'dRPC, MEV Blocker'), ('defillama.com', 'DefiLlama', '일별 유통량')]),
       ('공공 데이터', [('ecos.bok.or.kr', '한국은행 ECOS', ''), ('fred.stlouisfed.org', 'FRED', ''),
                     ('fiscaldata.treasury.gov', '미국 재무부 FiscalData', ''), ('data.go.kr', '공공데이터포털', '채권기본정보')])]
api = ''.join(f'<div><h4>{g}</h4>' + ''.join(f'<p>{fav(d)}<b>{n}</b><span>{t}</span></p>' for d, n, t in rows) + '</div>' for g, rows in API)
slides.append(frame('det', 1, '02', '프로젝트 내용', '(1) 문서 수집과 유통량 대조', f'''  {lab([
    ('판정 대상', '<span class="coins">' + ''.join(f'<em>{fav(d)}{c}</em>' for d, c in COINS) + '</span>'),
    ('수집', '발행사 월별 준비금 검증 보고서 264건, 국회 법안 10건 원문'),
    ('감시', 'OCI 서버가 5분, 30분마다 확인하고 원문을 세 곳에 보관'),
  ])}
  <div class="vis">{crop(-300, -180, 1030, 330, 'cr1')}<div class="api3">{api}</div></div>'''))

# 02 (2) 보고서 읽기: 읽기 엔진 3개를 크게
p_icons, j_icons, c_icons = svgs(tech_icons[0]), svgs(tech_icons[1]), svgs(tech_icons[2])
GEMINI = '<svg viewBox="0 0 24 24"><path fill="#4E82EE" d="M12 0C12.6 6.4 17.6 11.4 24 12C17.6 12.6 12.6 17.6 12 24C11.4 17.6 6.4 12.6 0 12C6.4 11.4 11.4 6.4 12 0Z"/></svg>'
ENG = [(p_icons, ['규칙 파서', 'PaddleOCR-VL'], '문서 파서', '글은 정규식, 표는 OCR'),
       (j_icons, ['Jev', 'Decisions API'], '판정 모델', '자산 종류와 공개 항목 고르기'),
       (c_icons + [GEMINI, j_icons[-1]], ['Claude Opus 5.5', 'Gemini 4 Argon', 'GPT-6.1 Sol'], 'LLM 독자', '표를 따로 읽어 OCR과 대조, 셋 중 하나를 골라 씀')]
eng = ''.join('<div><p class="lg">' + ''.join(f'<span><i>{ic}</i>{nm}</span>' for ic, nm in zip(ics, names)) +
              f'</p><b>{t}</b><em>{d}</em></div>' for ics, names, t, d in ENG)
slides.append(frame('read2', 1, '02', '프로젝트 내용', '(2) 보고서 읽기', f'''  <div class="eng">{eng}</div>
  <div class="rd-b">
    <div class="st"><b class="jost">18<small>/21칸</small></b><span>그림 표를 두 독자가 따로 읽어 합의로 확정</span></div>
    <div class="st"><b class="jost">0<small>건</small></b><span>264건 다시 읽기에서 찾은 저장값 오류</span></div>
    {ph('Ripple 그림 표와 두 독자 판독 비교 캡처')}
  </div>'''))

# 02 (3) 규칙 판정: 온톨로지 그림, 판정 흐름, 규칙별 판정 화면
JUDGE = '''<div class="jg">
  <div class="in"><span>보고서 값</span><span>한국 후보값</span><span>해외 6곳 기준</span></div>
  <i class="ar"></i>
  <div class="eg"><b>판정 엔진</b><em>코드로 비교</em></div>
  <i class="ar"></i>
  <div class="out"><span class="y">충족</span><span class="w">주의</span><span class="n">미충족</span></div>
</div>'''
slides.append(frame('rule3', 1, '02', '프로젝트 내용', '(3) 규칙 판정', f'''  <div class="onto">{crop(-305, 185, 465, 565, 'cr3')}</div>
  <div class="r-r">
    <ul class="kv"><li><b>온톨로지</b>자산 16종, 규칙 R01~R15, 원문 근거를 잇는 근거 그래프</li><li><b>관할권 7종</b>미국, EU 일반, EU 중요, 홍콩, 싱가포르, 일본, 한국 후보값</li><li><b>판정은 코드만</b>모델은 값만 읽고, 충족 여부는 판정 엔진이 결정</li></ul>
    {JUDGE}
    <div class="shot2"><img src="img/s_rules.png" alt="규칙별 판정 화면"></div>
    <p class="note"><b class="jost">121<small>/140칸</small></b>10월 법안 9건 원문 대조에서 값 19개를 확인해 한국 기준 파일을 고침</p>
  </div>'''))

# 02 (4) 하네스: 구성도의 하네스 구역
slides.append(frame('det', 1, '02', '프로젝트 내용', '(4) 하네스', f'''  {lab([
    ('프롬프트', 'Jev 선택지를 온톨로지의 자산 16종과 원문 상태 4종에서 가져옴'),
    ('컨텍스트', '원문 조각, 발행사별 형식 메모, 자산 16종 정의를 질문과 함께 넘김'),
    ('하네스', '정답 세트로 채점하고 틀린 칸의 프롬프트와 컨텍스트를 고치는 루프'),
  ])}
  <div class="vis">{crop(225, 175, 690, 480, 'cr4')}<p class="cyc"><span>읽기</span><span>채점</span><span>틀린 칸 고침</span><span>다시 읽기</span></p></div>'''))


def chart():
    x = lambda v: 120 + (v - 300) * 10  # 300~335 -> 120~470
    ticks = ''.join(f'<line x1="{x(v)}" x2="{x(v)}" y1="20" y2="150" class="gr"/><text x="{x(v)}" y="170" class="tk">{v}</text>' for v in range(300, 340, 5))
    rows = ''
    for i, (name, a, b) in enumerate([('GPT-OSS-20B', 307, 324), ('Kanana-1.5-8B', 311, 324), ('Gemma 4 E4B', None, None)]):
        y = 45 + i * 40
        rows += f'<text x="0" y="{y + 5}" class="nm">{name}</text>'
        if a is None:
            rows += f'<text x="{x(300)}" y="{y + 5}" class="tk l">학습 대기 (RunPod)</text>'
            continue
        rows += (f'<line x1="{x(a)}" x2="{x(b) - 6}" y1="{y}" y2="{y}" class="bar"/>'
                 f'<circle cx="{x(a)}" cy="{y}" r="5" class="o"/><circle cx="{x(b)}" cy="{y}" r="6" class="f"/>'
                 f'<text x="{x(a)}" y="{y - 11}" class="tk">{a}</text><text x="{x(b)}" y="{y - 11}" class="vl">{b}</text>')
    refs = (f'<line x1="{x(329)}" x2="{x(329)}" y1="10" y2="150" class="rf jev"/><text x="{x(329)}" y="6" class="rl jev">Jev 329 (목표)</text>'
            f'<line x1="{x(334)}" x2="{x(334)}" y1="22" y2="150" class="rf"/><text x="{x(334)}" y="18" class="rl e">Decisions 334</text>')
    return f'<svg class="dumb" viewBox="0 -6 540 182" aria-label="검증 372문항 정답 수">{ticks}{refs}{rows}</svg>'


# 02 (5) 내부망 판정 모델: 위는 목표와 점수, 아래는 내부망 그림과 흐름
FLOW5 = [('판정 블록', 'Kanana, Gemma, GPT-OSS가 예/아니오로 답함'), ('판정 엔진', 'SC2K 묶음과 답을 코드로 판정'),
         ('글 모델', 'Value for Fable 구조를 대입해 빈칸 문장을 채움'), ('근거 검사', '통과하면 산출물, 2번 실패하거나 0.95 미만이면 사람 확인')]
f5 = ''.join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in FLOW5)
slides.append(frame('m5', 1, '02', '프로젝트 내용', '(5) 내부망 판정 모델', f'''  <div class="m5-t">{lab([
    ('목표', '은행 내부망에서 돌리는 로컬 판정 모델을 Jev 수준으로'),
    ('방법', f'공개 LLM 3종 LoRA 파인튜닝, 실제 자료에 합성 자료 추가<span class="lg3">{logos}</span>'),
  ])}</div>
  <div class="chartc"><p class="cap">검증 372문항 정답 수<small>○ 실제 자료 ● 합성 추가</small></p>{chart()}</div>
  {crop(-334, 827, 1714, 829, 'cr5')}
  <ol class="f5">{f5}</ol>'''))

# 03 프로젝트 결과 1: 판정 화면 흐름
FLOW = [('1', '보고서 고르기', '종합 판정', 's_hero'), ('2', '한국 기준 15개', '한국 화면', 's_kr'),
        ('4', '해외 기준과 잇기', '판정 흐름', 's_flow'), ('3', '264건 전체 비교', '보고서 비교', 's_reports')]
cell = lambda n, b, s, img: f'<div class="fs"><p><em>{n}</em><b>{b}</b><span>{s}</span></p><img src="img/{img}.png" alt="{s}"></div>'
slides.append(frame('res1', 2, '03', '프로젝트 결과', '판정 화면 흐름', f'''  <div class="flow4">
    {cell(*FLOW[0])}<span class="ar r"></span>{cell(*FLOW[1])}
    <span></span><span></span><span class="ar d"></span>
    {cell(*FLOW[2])}<span class="ar l"></span>{cell(*FLOW[3])}
  </div>'''))

# 03 프로젝트 결과 2: 숫자와 링크. GitHub 단추는 GitHub 화면 모양 그대로
gh_fork, gh_star = svgs(poster[poster.find('class="gh"'):poster.find('class="qr"')])
caret = '<svg class="ct" viewBox="0 0 16 16"><path d="M4.4 6.4h7.2L8 10z"/></svg>'
GH = f'''<span class="gh"><span class="btn"><span class="gm">{gh_fork}Fork<em>47</em></span>{caret}</span><span class="btn"><span class="gm">{gh_star}Starred<em>236</em></span>{caret}</span></span>'''
STATS = [('264', '건', '보고서 대조, 오류 0', '보고서 264건의 R11, R12, R15를 Jev로 다시 읽어 대조. 일치율 90~98%, 다른 64건도 원문 확인 결과 저장값 오류 0'),
         ('18', '/21칸', '두 독자 합의 확정', '그림으로 된 Ripple 표 21칸을 두 독자가 따로 읽어 18칸 확정, 3칸은 사람 확인'),
         ('121', '/140칸', '법안 원문으로 수정', '10월 법안 9건 원문 대조에서 값 19개를 확인해 한국 기준 파일과 다른 칸 140개를 찾고 121칸 수정')]
st = ''.join(f'<div><b class="jost">{a}<small>{u}</small></b><span>{l}</span><p>{d}</p></div>' for a, u, l, d in STATS)
slides.append(frame('res2', 2, '03', '프로젝트 결과', '결과와 링크', f'''  <div class="stats3">{st}</div>
  <div class="links">
    <div><span class="q">{qr("https://sc2k.kr")}</span><p><b>판정 사이트</b>sc2k.kr</p></div>
    <div>{ph('시연 영상 링크')}</div>
    <div><span class="q">{qr("https://github.com/itsinseong/value-for-fable")}</span><p><b>Value for Fable 시스템 프롬프트</b>github.com/itsinseong/value-for-fable{GH}</p></div>
  </div>'''))

# 04 기대효과 및 느낀점: 한 장
CARDS = [('MAS 의견서 제출', '싱가포르 통화청 규제 개정안(P015-2026)에 판정 결과를 근거로 21개 문항 답변, 2026-10-10'),
         ('발행사, 은행', '공시 전에 같은 기준으로 자기 보고서를 점검'),
         ('감독기관, 국회', '법안별 값 차이와 해외 기준을 한 화면에서 비교'),
         ('공시 감시', '공시가 바뀌면 원문 보관과 이슈 기록(설계)')]
cards = ''.join(f'<div{" class=\"me\"" if i == 0 else ""}>{mas_icon if i == 0 else ""}<i class="jost">0{i + 1}</i><b>{t}</b><p>{d}</p></div>' for i, (t, d) in enumerate(CARDS))
feel = ''.join(f'<li>{ph("느낀점 " + str(i))}</li>' for i in range(1, 5))
slides.append(frame('eff', 3, '04', '기대효과 및 느낀점', '', f'''  <p class="hd2 h1">기대효과</p><div class="cards4">{cards}</div>
  <p class="hd2 h2">느낀점</p><ol class="feel4">{feel}</ol>'''))

# 마지막
slides.append('''<section class="slide end">
  <p class="jost big">SC2K</p>
  <p class="t">원화 스테이블코인 준비금 공시 판정 체계</p>
  <p class="u jost">sc2k.kr</p>
</section>
''')

CSS = r'''
/* 최종 덱 */
.cover .sub1{position:absolute;left:6cqw;top:51cqw;font-size:1.5cqw;color:#6F768C}
.lb{position:absolute;left:4.2cqw;top:11.2cqw;width:38cqw;display:flex;flex-direction:column;gap:1.7cqw}
.intro3 .lb{left:60cqw;width:35.8cqw;top:11.8cqw}
.lb .k{display:inline-block;background:var(--accent);color:#141210;font-size:1.05cqw;font-weight:650;padding:.2cqw .7cqw;border-radius:.3cqw;margin-bottom:.6cqw!important}
.lb .v{font-size:1.4cqw;line-height:1.55;color:#E3E6EC;word-break:keep-all}
.lb .v small{display:block;font-family:"Jost",sans-serif;font-size:1.05cqw;color:var(--muted)}
.intro3 .vid{width:52cqw;top:11.8cqw;border-radius:.6cqw;overflow:hidden}
.fv{width:1.3cqw;height:1.3cqw;border-radius:.25cqw;background:#fff;object-fit:contain;flex:none}
.coins{display:flex;flex-wrap:wrap;gap:.5cqw}
.coins em{display:inline-flex;align-items:center;gap:.45cqw;font-style:normal;font-size:1.05cqw;padding:.25cqw .8cqw .25cqw .35cqw;border:1px solid rgba(255,255,255,.18);border-radius:2cqw;color:#CFD4E0}
.coins .fv{border-radius:50%}
.vis{position:absolute;left:46cqw;right:4.2cqw;top:11.2cqw;bottom:3.2cqw;display:flex;flex-direction:column;gap:1.2cqw}
.shot2{border:1px solid var(--line);border-radius:.6cqw;overflow:hidden;flex:none}
.shot2 img{display:block;width:100%}
.ph{flex:1;min-height:6cqw;border:1.5px dashed rgba(255,255,255,.22);border-radius:.6cqw;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.4cqw;font-size:1.1cqw;color:var(--muted)}
.ph span{font-size:.85cqw;font-weight:650;color:var(--accent);letter-spacing:.04em}
/* 02 단계 5개 */
.pipe{position:absolute;left:4.2cqw;right:4.2cqw;top:17.5cqw;display:grid;grid-template-columns:repeat(5,1fr);gap:2.4cqw}
.pipe div{display:flex;flex-direction:column}
.pipe i{font-style:normal;font-size:3.4cqw;font-weight:300;color:var(--accent);line-height:1;margin-bottom:2.6cqw}
.pipe svg{width:6.4cqw;height:6.4cqw;fill:none;stroke:var(--ink);stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;margin-bottom:2.2cqw}
.pipe b{display:block;padding-top:1.4cqw;border-top:1px solid rgba(255,255,255,.18);font-size:1.5cqw;font-weight:650;line-height:1.35;margin-bottom:.8cqw;word-break:keep-all}
.pipe span{font-size:1.1cqw;line-height:1.55;color:var(--muted)}
/* 구성도: 포스터 그림을 남색 바탕용 색으로 */
.dg text{font-family:"Pretendard Variable",Pretendard,sans-serif}
.dg .face-t{fill:#F2F4F7}
.dg .face-l,.dg .face-r{fill:#2B303D}
.dg .face-t,.dg .face-l,.dg .face-r{stroke:#C9CEDA;stroke-width:1.2;stroke-linejoin:round}
.dg .dt{fill:none;stroke:#2A2623;stroke-width:1.2;stroke-linecap:round;stroke-linejoin:round}
.dg .top-word{fill:#2A2623;font-weight:800;text-anchor:middle}
.dg .lab{fill:rgba(255,255,255,.06);stroke:rgba(255,255,255,.16);stroke-width:1}
.dg .lab-n{fill:#F2F4F7;font-size:17px;font-weight:700}
.dg .lab-badge{fill:#E3B341;font-size:13px;font-weight:700}
.dg .pill{fill:#1C202B;stroke-width:1.5}
.dg .pill-t{fill:#E3E6EC;font-size:14.5px;font-weight:600;text-anchor:middle}
.dg .zone-t{font-size:16.5px;font-weight:700;paint-order:stroke;stroke:#1A1D26;stroke-width:5px;stroke-linejoin:round}
.dg .net-t{fill:#F2F4F7;font-size:26px;font-weight:800;letter-spacing:-.02em}
.dg rect[rx="18"]{fill:rgba(255,255,255,.02);stroke:rgba(255,255,255,.16)}
.dg rect[fill="url(#grid_f)"]{fill:none;stroke:none}
.dg [fill="#000"],.dg [fill="#000000"],.dg [fill="#181717"],.dg [fill="#141210"]{fill:#E3E6EC}
.dg [stroke="#000"]{stroke:#E3E6EC}
.dg [fill="#4A8A2A"]{fill:#8CC56A}.dg [stroke="#4A8A2A"]{stroke:#8CC56A}
.dg [fill="#B07510"]{fill:#E2A93B}.dg [stroke="#B07510"]{stroke:#E2A93B}
.dg [fill="#6A3FC0"]{fill:#B79CF0}.dg [stroke="#6A3FC0"]{stroke:#B79CF0}
.dg [fill="#2F6FD6"]{fill:#6FA3F0}.dg [stroke="#2F6FD6"]{stroke:#6FA3F0}
.dg [fill="#3A1D1D"]{fill:#F2F4F7}
.dg path[transform="translate(-12,-12)"][fill="#2A2623"],.dg circle[r="10"][fill="#2A2623"]{fill:#E3E6EC}
.dg [fill="#736D68"]{fill:#9AA0B2}.dg [stroke="#736D68"]{stroke:#6F768C}
.archs .a1{position:absolute;left:3cqw;top:8.6cqw;height:46.4cqw;width:auto}
.archs .a2{position:absolute;left:4.2cqw;right:4.2cqw;top:9.6cqw;width:91.6cqw;height:auto}
.zones{position:absolute;left:68cqw;right:4.2cqw;top:13cqw;list-style:none;margin:0;padding:0;counter-reset:z;display:flex;flex-direction:column;gap:2.2cqw}
.zones li{counter-increment:z;display:grid;grid-template-columns:2.6cqw 1fr;row-gap:.4cqw}
.zones li:before{content:counter(z);grid-row:span 2;width:1.9cqw;height:1.9cqw;border-radius:50%;background:var(--accent);color:#141210;display:grid;place-items:center;font-size:1cqw;font-weight:700}
.zones b{font-size:1.35cqw;font-weight:650}
.zones span{font-size:1.1cqw;line-height:1.55;color:#CFD4E0;word-break:keep-all}
/* (1) 수집 */
.vis .cr1{width:100%;height:auto;flex:none}
.api3{display:grid;grid-template-columns:repeat(3,1fr);gap:1.4cqw;flex:1}
.api3 h4{margin:0 0 .8cqw;font-size:1.05cqw;font-weight:650;color:var(--accent);padding-bottom:.5cqw;border-bottom:1px solid rgba(255,255,255,.14)}
.api3 p{display:grid;grid-template-columns:1.7cqw 1fr;align-items:center;column-gap:.5cqw;margin:0 0 .75cqw!important}
.api3 .fv{grid-row:span 2}
.api3 b{font-size:1.05cqw;font-weight:600;line-height:1.3}
.api3 span{font-size:.88cqw;color:var(--muted);line-height:1.3}
/* (2) 읽기 엔진 */
.eng{position:absolute;left:4.2cqw;right:4.2cqw;top:11.6cqw;display:grid;grid-template-columns:repeat(3,1fr);gap:1.6cqw}
.eng>div{background:var(--surface);border-radius:1cqw;padding:2.2cqw 2.2cqw 2cqw;display:flex;flex-direction:column}
.eng .lg{display:flex;gap:1.6cqw;margin-bottom:2cqw!important}
.eng .lg span{display:flex;flex-direction:column;align-items:center;gap:.6cqw;font-size:1cqw;color:#CFD4E0}
.eng .lg i{width:5.4cqw;height:5.4cqw;border-radius:1cqw;background:#fff;display:grid;place-items:center}
.eng .lg svg{width:3.4cqw;height:3.4cqw}
.eng b{font-size:1.9cqw;font-weight:700;letter-spacing:-.02em;margin-bottom:.6cqw}
.eng em{font-style:normal;font-size:1.25cqw;color:#CFD4E0}
.rd-b{position:absolute;left:4.2cqw;right:4.2cqw;top:33cqw;bottom:3.2cqw;display:grid;grid-template-columns:1fr 1fr 2fr;gap:1.6cqw}
.rd-b .st{border-top:1px solid rgba(255,255,255,.14);padding-top:1.2cqw}
.rd-b .st b{display:block;font-size:4.2cqw;font-weight:300;color:var(--accent);line-height:1}
.rd-b .st b small{font-size:1.3cqw;color:var(--muted);margin-left:.3cqw}
.rd-b .st span{display:block;margin-top:.8cqw;font-size:1.15cqw;line-height:1.5;color:#CFD4E0;word-break:keep-all}
/* (3) 규칙 판정 */
.onto{position:absolute;left:3cqw;top:9cqw;bottom:1.6cqw;width:36cqw}
.onto svg{width:100%;height:100%}
.r-r{position:absolute;left:42cqw;right:4.2cqw;top:11cqw;bottom:2.6cqw;display:flex;flex-direction:column;gap:1.3cqw}
.kv{list-style:none;margin:0;padding:0}
.kv li{display:grid;grid-template-columns:10cqw 1fr;font-size:1.2cqw;line-height:1.45;padding:.55cqw 0;border-bottom:1px solid rgba(255,255,255,.08);color:#CFD4E0;word-break:keep-all}
.kv b{color:var(--ink);font-weight:650}
.jg{display:grid;grid-template-columns:auto 2.4cqw auto 2.4cqw auto;align-items:center;justify-content:start;gap:.6cqw}
.jg .in,.jg .out{display:flex;flex-direction:column;gap:.35cqw}
.jg .in span{font-size:1cqw;padding:.3cqw .8cqw;border:1px solid rgba(255,255,255,.18);border-radius:.4cqw;color:#CFD4E0}
.jg .eg{background:#EEF0F4;color:#1F232D;border-radius:.6cqw;padding:1cqw 1.6cqw;text-align:center}
.jg .eg b{display:block;font-size:1.3cqw;font-weight:700}.jg .eg em{font-style:normal;font-size:.95cqw;color:#565D70}
.jg .ar{position:relative;height:0;border-top:1.5px solid var(--accent)}
.jg .ar:after{content:"";position:absolute;right:-.2cqw;top:-.5cqw;border-left:.7cqw solid var(--accent);border-top:.42cqw solid transparent;border-bottom:.42cqw solid transparent}
.jg .out span{display:flex;align-items:center;gap:.5cqw;font-size:1.05cqw;font-weight:600}
.jg .out span:before{content:"";width:1cqw;height:1cqw;border-radius:.2cqw}
.jg .y:before{background:#3F6FD1}.jg .w:before{background:#2E6A63}.jg .n:before{background:#C0544A}
.note{display:flex;align-items:baseline;gap:1cqw;font-size:1.15cqw;color:#CFD4E0}
.note b{font-size:2.6cqw;font-weight:300;color:var(--accent)}.note b small{font-size:1.1cqw;color:var(--muted)}
/* (4) 하네스 */
.vis .cr4{width:100%;height:auto;flex:none}
.cyc{display:flex;justify-content:center;gap:2.6cqw;font-size:1.1cqw;color:#CFD4E0}
.cyc span{position:relative}
.cyc span:not(:last-child):after{content:"→";position:absolute;right:-1.9cqw;color:var(--accent)}
/* (5) 내부망 판정 모델 */
.m5 .lb{top:10.6cqw;gap:1.2cqw}
.lg3{display:flex;flex-wrap:wrap;gap:.6cqw;margin-top:.7cqw}
.lg3 .lgm{display:inline-flex;gap:.6cqw;flex-wrap:wrap;font-size:1.05cqw}
.chartc{background:var(--surface);border-radius:.8cqw;padding:1.4cqw 2cqw;display:flex;flex-direction:column;justify-content:center}
.m5 .chartc{position:absolute;left:46cqw;right:4.2cqw;top:9.8cqw;height:18.6cqw}
.chartc .cap{font-size:1.2cqw;font-weight:650;margin-bottom:.6cqw!important}
.chartc .cap small{margin-left:1cqw;font-size:.95cqw;color:var(--muted);font-weight:500}
.m5 .dumb{height:13cqw}
.m5 .cr5{position:absolute;left:3cqw;top:29.4cqw;width:54cqw;height:auto}
.f5{position:absolute;left:60cqw;right:4.2cqw;top:30.4cqw;list-style:none;margin:0;padding:0;counter-reset:f;display:flex;flex-direction:column;gap:1.1cqw}
.f5 li{counter-increment:f;display:grid;grid-template-columns:2.4cqw 1fr;row-gap:.2cqw}
.f5 li:before{content:counter(f);grid-row:span 2;width:1.7cqw;height:1.7cqw;border-radius:50%;background:var(--accent);color:#141210;display:grid;place-items:center;font-size:.95cqw;font-weight:700}
.f5 b{font-size:1.2cqw;font-weight:650}
.f5 span{font-size:1.02cqw;line-height:1.5;color:#CFD4E0;word-break:keep-all}
.dumb{width:100%}
.dumb text{font-family:"Pretendard Variable",sans-serif}
.dumb .gr{stroke:rgba(255,255,255,.07)}
.dumb .tk{fill:#9AA0B2;font-size:10px;text-anchor:middle}.dumb .tk.l{text-anchor:start;font-size:11px}
.dumb .nm{fill:#F2F4F7;font-size:12px;font-weight:650}
.dumb .bar{stroke:#B4D0E4;stroke-width:2}
.dumb .o{fill:#191C25;stroke:#B4D0E4;stroke-width:1.6}.dumb .f{fill:#B4D0E4}
.dumb .vl{fill:#B4D0E4;font-size:11px;font-weight:700;text-anchor:middle}
.dumb .rf{stroke:#9AA0B2;stroke-dasharray:3 3}.dumb .rf.jev{stroke:#E8A0B4}
.dumb .rl{font-size:10.5px;font-weight:700;text-anchor:middle;fill:#CFD4E0}.dumb .rl.jev{fill:#E8A0B4;text-anchor:end}.dumb .rl.e{text-anchor:start}
/* 03 결과 1: 화면 흐름 */
.flow4{position:absolute;left:13cqw;right:13cqw;top:9.4cqw;display:grid;grid-template-columns:1fr 4cqw 1fr;grid-template-rows:auto 2cqw auto;align-items:center}
.flow4 .fs p{display:flex;align-items:baseline;gap:.6cqw;margin-bottom:.5cqw!important;font-size:1.15cqw}
.flow4 .fs em{font-style:normal;width:1.7cqw;height:1.7cqw;border-radius:50%;background:var(--accent);color:#141210;display:inline-grid;place-items:center;font-size:.95cqw;font-weight:700;align-self:center}
.flow4 .fs b{font-weight:650}.flow4 .fs span{color:var(--muted);font-size:.95cqw}
.flow4 img{display:block;width:100%;border:1px solid var(--line);border-radius:.5cqw}
.flow4 .ar{position:relative;justify-self:center}
.flow4 .ar.r,.flow4 .ar.l{width:2.4cqw;border-top:1.5px solid var(--accent)}
.flow4 .ar.d{height:1.4cqw;border-left:1.5px solid var(--accent)}
.flow4 .ar:after{content:"";position:absolute;border:.4cqw solid transparent}
.flow4 .ar.r:after{right:-.5cqw;top:-.47cqw;border-left:.6cqw solid var(--accent);border-right:0}
.flow4 .ar.l:after{left:-.5cqw;top:-.47cqw;border-right:.6cqw solid var(--accent);border-left:0}
.flow4 .ar.d:after{bottom:-.5cqw;left:-.47cqw;border-top:.6cqw solid var(--accent);border-bottom:0}
/* 03 결과 2 */
.stats3{position:absolute;left:4.2cqw;right:4.2cqw;top:12cqw;display:grid;grid-template-columns:repeat(3,1fr);gap:3cqw}
.stats3 b{display:block;font-size:6cqw;font-weight:300;color:var(--accent);line-height:1}
.stats3 b small{font-size:1.5cqw;color:var(--muted);margin-left:.4cqw;font-weight:400}
.stats3 span{display:block;margin:.8cqw 0 1cqw;font-size:1.45cqw;font-weight:650}
.stats3 p{font-size:1.1cqw;line-height:1.6;color:#CFD4E0;word-break:keep-all}
.links{position:absolute;left:4.2cqw;right:4.2cqw;bottom:3.4cqw;height:12cqw;display:grid;grid-template-columns:1fr 1fr 1.4fr;gap:2cqw}
.links>div{display:flex;align-items:center;gap:1.4cqw;padding-top:1.6cqw;border-top:1px solid rgba(255,255,255,.12)}
.links .q{flex:none;width:8.6cqw;height:8.6cqw;background:#fff;border-radius:.4cqw;padding:.3cqw}
.links .q svg{width:100%;height:100%;display:block}
.links p{font-size:1.05cqw;line-height:1.5;color:#CFD4E0;font-family:"Jost","Pretendard Variable",sans-serif;word-break:break-all}
.links p b{display:block;font-family:"Pretendard Variable",sans-serif;font-size:1.3cqw;color:var(--ink);font-weight:650;margin-bottom:.3cqw}
.links .ph{height:100%}
/* GitHub 단추: GitHub 어두운 화면 모양 */
.gh{display:flex;gap:.7cqw;margin-top:.9cqw}
.gh .btn{display:inline-flex;align-items:stretch;background:#212830;border:1px solid #3D444D;border-radius:.45cqw;font-family:-apple-system,"Segoe UI","Pretendard Variable",sans-serif;font-size:1cqw;font-weight:600;color:#F0F6FC;overflow:hidden}
.gh .gm{display:inline-flex;align-items:center;gap:.45cqw;padding:.38cqw .7cqw}
.gh .gm svg{width:1.1cqw;height:1.1cqw}
.gh .gm svg path[fill="#57606A"]{fill:#9198A1}
.gh em{font-style:normal;background:#2F3742;border-radius:2cqw;padding:.05cqw .5cqw;font-size:.92cqw;margin-left:.15cqw}
.gh .ct{width:2cqw;padding:0 .5cqw;border-left:1px solid #3D444D;fill:#9198A1;box-sizing:content-box;height:auto}
/* 04 기대효과 및 느낀점 */
.hd2{position:absolute;left:4.2cqw;font-size:1.15cqw;font-weight:650;color:var(--accent)}
.hd2.h1{top:10cqw}.hd2.h2{top:34.6cqw}
.cards4{position:absolute;left:4.2cqw;right:4.2cqw;top:12.6cqw;height:19.6cqw;display:grid;grid-template-columns:repeat(4,1fr);gap:1.4cqw}
.cards4 div{position:relative;background:var(--surface);border-radius:1cqw;padding:1.8cqw 1.8cqw;display:flex;flex-direction:column}
.cards4 div.me{background:#EEF0F4;color:#1F232D}
.cards4 div>svg{position:absolute;right:1.8cqw;top:1.8cqw;width:2.6cqw;height:2.6cqw}
.cards4 i{font-style:normal;font-size:2.4cqw;font-weight:300;color:var(--accent);line-height:1}
.cards4 .me i{color:#3E6E96}
.cards4 b{display:block;margin:1.3cqw 0 .8cqw;font-size:1.45cqw;font-weight:700;letter-spacing:-.02em;word-break:keep-all}
.cards4 p{font-size:1.08cqw;line-height:1.55;color:#CFD4E0;word-break:keep-all}
.cards4 .me p{color:#565D70}
.feel4{position:absolute;left:4.2cqw;right:4.2cqw;top:37.2cqw;bottom:3.2cqw;list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:1.2cqw 1.4cqw}
.feel4 li{display:flex}
/* 마지막 */
.end{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.end .big{font-size:11cqw;font-weight:300;letter-spacing:.04em;line-height:1;color:var(--accent)}
.end .t{margin-top:2cqw!important;font-size:1.8cqw;font-weight:600}
.end .u{margin-top:1.2cqw!important;font-size:1.3cqw;color:var(--muted)}
'''

html = head + CSS + '</style>\n</head>\n<body>\n<main class="deck">\n\n' + '\n'.join(slides) + '\n</main>\n</body>\n</html>\n'
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / 'img').mkdir(exist_ok=True)
for n in IMGS:
    shutil.copy2(H / '포스터/assets' / n, OUT_DIR / 'img' / n)
OUT.write_text(html, 'utf-8')
print(OUT, len(slides), '장')
