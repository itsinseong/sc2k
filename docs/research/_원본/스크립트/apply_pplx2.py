p='docs/매니페스트.md'
t=open(p,encoding='utf-8').read()
R=[]

# 0 header
R.append(("| 갱신 2026-09-03: 퍼플렉시티 리서치 1차 반영(§3, §6, §11, §13, §15, SW-PL-03/04, SW-TL-01)",
"| 갱신 2026-09-03: 퍼플렉시티 리서치 1차 반영(§3, §6, §11, §13, §15, SW-PL-03/04, SW-TL-01) / 2차 반영(§7 개정 근거, §14 KPI, SW-PL-07/08/09 소스, SW-VF-03 화면 요소, §16 원출처)"))

# 1 §3 한은 sentence
R.append(("- 한국은행은 가상자산사업자(VASP) 자료 제출을 받아 시장을 모니터링, 분석한다고 밝혔고, 원화 스테이블코인은 은행 중심 발행이 바람직하다는 입장을 공개했다. 금융위는 초기 발행자를 은행 지분 50%+1 컨소시엄으로 두는 안을 검토한 것으로 보도됐다. 즉 은행의 관심사는 가격이 아니라 발행 구조, 준비자산, AML, 환매 리스크다.",
"- 한국은행은 가상자산사업자(VASP) 자료 제출을 받아 시장을 모니터링, 분석한다고 밝혔고([한은 2025-09-19](https://www.bok.or.kr/eng/bbs/E0000866/view.do?nttId=10093606&oldMenuNo=400007&menuNo=400223&programType=newsDataEng&depth=400223&relate=Y)), 원화 스테이블코인 제도 논의를 다룬 공식 이슈해설을 냈다([한은 2026-02-20](https://www.bok.or.kr/portal/bbs/B0000168/view.do?menuNo=200058&nttId=10094368)). \"은행 중심 발행이 바람직하다\"는 입장은 보도로만 확인되고 직접 문서는 미확인. 금융위는 초기 발행자를 은행 지분 50%+1 컨소시엄으로 두는 안을 검토한 것으로 보도됐다([서울경제 2026-01-06](https://en.sedaily.com/finance/2026/01/06/korea-to-allow-won-stablecoin-issuance-by-bank-led), [조선비즈 2026-01-07](https://biz.chosun.com/en/en-finance/2026/01/07/3JECOJXMBRGPJMO2UVZKKRIXAI/)). 즉 은행의 관심사는 가격이 아니라 발행 구조, 준비자산, AML, 환매 리스크다."))

# 2 §3 append org limits + skills table
R.append(("- 해외 은행(JPMorgan Kinexys, Citi Digital Assets)은 NLP 뉴스 감성 분석 도구는 쓰지만, 문장 단위 참/거짓 판정 제품을 운영한다는 공개 근거는 없다.\n",
"""- 해외 은행(JPMorgan Kinexys, Citi Digital Assets)은 NLP 뉴스 감성 분석 도구는 쓰지만, 문장 단위 참/거짓 판정 제품을 운영한다는 공개 근거는 없다.
- 조직 정보의 한계(퍼플렉시티 ⑪): 은행들은 디지털자산 TF의 정식 조직명, 상설화 날짜, 전담 인원, 담당 임원, 내부 보고 주기를 공개하지 않는다. 채용공고 원문도 마감 후 사라져 2025~2026년 공고를 원문 URL과 함께 확보하지 못했다. 따라서 기획서에는 "전담 부서가 있다"가 아니라 "업무가 수탁, 지급결제, 규제대응, 인프라, AML, 신사업, 전략 조직에 분산돼 있다"로 쓴다. 공개 확인된 활동은 KB의 KODA 설립([BloomingBit](https://en.bloomingbit.io/feed/news/83346)), 신한과 NH의 KDAC 투자([Wowtale](https://en.wowtale.net/2025/11/26/232926/)), 우리의 쿠팡 PoC, 하나의 BitGo Korea 협력(보도) 정도다.

| 업무 모듈 | 실제 필요 역량 | 제품과의 연결 |
|---|---|---|
| 시장, 정책 모니터링 | 규제 공고 탐색, 뉴스 신뢰도 평가, 법안과 공시 읽기, 영어 원문 검토 | 주장별 원출처, 발행시점, 후속 정정, 규제 타임라인 |
| 상품, 신사업 | 지급결제, 전자금융, 토큰화, 지갑, 온/오프램프, 파트너 실사 | PoC, 제휴, 발행계획 주장의 단계별 검증 |
| AML, 컴플라이언스 | KYC, AML/CFT, 제재, Travel Rule, adverse media | 엔터티, 지갑, 규제 사건과 뉴스 주장 연결 |
| 수탁, 인프라 | 키관리, MPC/HSM, 온체인 리스크 | 지갑, 수탁, 해킹, 준비금 주장 검증 |
| 모델, 데이터 거버넌스 | 데이터 계보, 증거 보존, AI 검토, 재현성, 감사 로그 | 사람 승인과 반려 이력(SW-VF-03) |
"""))

# 3 §6 link pointer
R.append(("로 규정한다. 기획서에는 이 문장으로 쓴다.",
"로 규정한다. 기획서에는 이 문장으로 쓴다. 각 데이터셋의 논문과 저장소 링크는 §16 리서치 원출처."))

# 4 §7 revision block
R.append(("판정 등급은 코드 규칙으로 결정론적으로 게이팅하고, LLM은 후보 근거 수집·요약에만 관여한다(SW-VF-01의 설계 원칙 — 구체 게이팅 규칙은 §9 SW-VF-01).\n",
"""판정 등급은 코드 규칙으로 결정론적으로 게이팅하고, LLM은 후보 근거 수집·요약에만 관여한다(SW-VF-01의 설계 원칙 — 구체 게이팅 규칙은 §9 SW-VF-01).

### 개정 예정 — 2축 + 최종판정 구조(사용자 확정 대기. 근거: Codex 리뷰 2026-09-02, 퍼플렉시티 ⑧ 2026-09-03)

위 5단계는 "근거의 양"(복수/단일 보도)과 "주장의 성격"(예정/의견)을 한 축에 섞는다. 개정안은 세 층으로 나눈다. 선례는 FEVER의 3분류(SUPPORTS/REFUTES/NEI), AVeriTeC의 4분류(Supported/Refuted/Not Enough Evidence/Conflicting), 저널리즘의 1차 출처와 독립 복수 출처 원칙의 결합이다([AVeriTeC](https://proceedings.neurips.cc/paper_files/paper/2023/hash/cd86a30526cd1aff61d6f89f107634e4-Abstract-Datasets_and_Benchmarks.html), [FEVER](https://aclanthology.org/N18-1074.pdf)).

| 층 | 값 | 기준 |
|---|---|---|
| 주장 유형 | 수치 / 사건 / 예정 / 의견 | 수치=외부 데이터로 대조 가능. 사건=발생 여부 확인 가능(PoC 완료, 제휴, 발의, 제재, 발행 개시). 예정=계획, 검토, 목표, 협상 중. 의견="호재", "위기", "성공할 것" 같은 평가와 예측 |
| 근거 상태 | 공식 1차 자료 대조 확인 / 복수 독립 보도 / 단일 보도 / 상충 근거 / 근거 부족 | 1차 자료=규제기관, 법령과 관보, 국회, 발행사 공시, 기업 보도자료, attestation, 거래소 공식 API, 온체인. 상충=신뢰 가능한 근거끼리 주체, 범위, 시점, 수치가 충돌 |
| 최종 판정 | 확인됨 / 반박됨 / 부분 확인 / 판단보류 / 검증 대상 외 | 부분 확인=핵심은 맞으나 주체, 규모, 날짜, 범위가 과장 또는 생략. 판단보류=예정이거나 근거 불충분 또는 상충. 검증 대상 외=순수 의견과 전망 |

운영 규칙 세 가지.
- **시점 규칙(AVeriTeC)**: 주장 시점 이후에 나온 자료로 과거 주장을 사후 판정하지 않는다. 미입증은 거짓이 아니라 판단보류다. 예정과 의견은 AFP 관행대로 사실 판정 대상에서 제외하고, SNU팩트체크처럼 판단보류를 독립 결과로 화면에 노출한다. PolitiFact 기준으로 입증 책임은 발화자에게 있고 판정은 발언 당시 알려진 정보로 한다.
- **독립 출처 정의**: 동일한 보도자료, 통신사 송고, 익명 제보, 기업 브리핑, 다른 매체의 선행 보도에 실질적으로 의존하지 않고, 각자 별도의 1차 문서나 취재원으로 핵심 사실을 확인한 출처만 독립으로 센다. 복수 매체 게재는 복수 독립 출처가 아니다([Reuters 기준](https://reutersagency.com/about/standards-values/)).
- **계보 처리(SW-VF-01의 countCrossReports 규칙)**:

| 상황 | 독립 출처 수 | 처리 |
|---|---|---|
| 쿠팡 공식 보도자료 + 한경 + 이데일리 기사 | 1차 출처 1개 | 공식 1차 자료 대조 확인. 기사 수를 독립성으로 세지 않음 |
| Reuters 최초 기사 + Reuters를 인용한 15개 매체 | 1개 | 단일 보도 |
| 기자 A의 익명 취재원 보도 + 기자 B의 다른 익명 취재원 보도 | 최대 2개 | 인용문, 보도 시각, 문장 중복 검토. 동일 브리핑 가능성 높으면 1개 |
| 금융위 발표 + 국회 의안 원문 | 2개, 모두 1차 | 공식 1차 자료 대조 확인(독립 보도보다 상위) |
| 기업 보도자료 + 같은 기업 임원 인터뷰 | 1개 계보 | 같은 발행 주체의 반복. 독립 확인 아님 |
| 기업 보도자료 + 규제기관 공시 + 외부 감사보고서 | 3개 성격 다른 근거 | 강한 공식 1차 자료 대조 확인 |

키워드 겹침으로 세는 교차보도 건수는 후보 생성용이지 이 표를 대신하지 못한다. 확정되면 §7 표, SW-VF-01, §5 화면3 설명, eli5 아티팩트를 함께 갱신한다.
"""))

# 5 SW-PL-03 κ bullet
R.append(("- 2인 확보 시 20~30건을 중복 판정해 Cohen's κ를 보고한다(참고: FEVER Fleiss κ 0.684, FEVEROUS κ 0.65). 1인이면 κ 대신 판정 규칙 문서를 남긴다. 불일치는 합의로 정하되 최초 개별 판정도 보존.",
"""- 2인 확보 시 중복 판정해 Cohen's κ를 최종 판정, 주장 유형, 근거 상태 각각 따로 산출한다(2인 명목형에는 Cohen's κ가 기본, 3인 이상이면 Fleiss, 결측 있으면 Krippendorff α). 목표는 κ 0.61 이상(파일럿 기준, Landis-Koch의 substantial), 0.80 이상이면 고신뢰 운영 기준. 0.40 미만이면 클래스 정의를 재설계한다. 참고: FEVER Fleiss κ 0.684, FEVEROUS κ 0.65. 1인이면 κ 대신 판정 규칙 문서를 남긴다. 불일치는 합의로 정하되 최초 개별 판정도 감사 로그로 보존.
- 시점 규칙: 주장 시점 이후 자료로 판정하지 않는다(§7 개정안). 골드셋 필드의 "주장이 가리키는 시점"과 "근거 발행일"을 비교해 위반 건은 무효 처리."""))

# 6 SW-PL-04 rows
R.append(("| 금감원(대체) | DART 최근공시 RSS https://dart.fss.or.kr/api/todayRSS.xml | 금감원 보도자료 자체 RSS는 미발견. 기업공시 대조용 |\n| 한국은행 | RSS 미발견 → 보도자료 목록 HTML 수집 | 첨부(PDF/HWP) 파싱 별도 |",
"| 금감원(대체) | DART 최근공시 RSS https://dart.fss.go.kr/api/todayRSS.xml ([안내](https://dart.fss.or.kr/introduction/content6.do)) | 금감원 보도자료 자체 RSS는 미발견, 목록 URL도 미확정. DART는 회사, 공시일, 접수번호, 정정공시까지 구조화돼 감사추적 소스로 우선 |\n| 한국은행 | RSS 아이콘은 있으나 endpoint 미확정 → 목록 HTML 수집: [통화정책 보도자료](https://www.bok.or.kr/portal/main/contents.do?menuNo=200690), [뉴스와 의사록](https://www.bok.or.kr/portal/main/contents.do?menuNo=200038), [언론보도 해명](https://www.bok.or.kr/portal/bbs/P0000560/list.do?menuNo=200040) | 페이지 소스에서 RSS 링크 1회 추출해 고정 시도. 첨부(HWP/HWPX/PDF) 파싱 별도. 키워드에 CBDC, 토큰증권, 지급결제 추가 |"))

# 7 SW-PL-07 inputs
R.append(("**목적** 수치형 주장(109건, 15.6%)을 실제 시세·발행량과 대조할 외부 데이터 축. 둘 다 인증 불필요 공개 REST API라 빠르게 붙일 수 있다.\n",
"""**목적** 수치형 주장(109건, 15.6%)을 실제 시세·발행량과 대조할 외부 데이터 축. 둘 다 인증 불필요 공개 REST API라 빠르게 붙일 수 있다.

**입력(퍼플렉시티 ⑨ 2026-09-03 확인)**

| 소스 | 엔드포인트 | 제한 |
|---|---|---|
| DefiLlama(무료, 키 불필요) | https://api.llama.fi/stablecoins (목록과 유통량), /stablecoincharts/all (전체 역사 시총), /stablecoincharts/Ethereum (체인별), /stablecoin/1 (개별 자산), /stablecoinprices (역사 가격, 디페그 탐지) | 시총 정의가 거래소 표시와 다를 수 있음. 응답 timestamp를 반드시 저장 |
| CoinGecko Demo(무료 키) | /coins/markets?vs_currency=usd&category=stablecoins (현재), /coins/usd-coin/history?date=DD-MM-YYYY (특정일), /coins/usd-coin/market_chart?days=90&interval=daily (기간) | 월 10,000 호출, 분당 100. 키 없는 공개 호출은 분당 10~30. 과거 데이터는 1년 제한이라 그 이전 기준일은 자체 아카이빙 필요 |
| Circle 투명성 페이지 | https://www.circle.com/transparency | API 없음. 주간 준비금 보유내역과 월간 회계법인 examination report PDF |
| Tether 투명성 페이지 | https://tether.to/transparency/?tab=reports | API 없음. 유통량 일일, 준비금 보고와 BDO assurance는 분기 |

준비금 주장("USDC 준비금이 유통량을 초과")은 API가 아니라 해당 월 report date의 PDF 수치와 대조한다. 자동화 대상은 DefiLlama와 CoinGecko의 시총, 유통량, 가격이고, 준비금은 수작업 대조 필드로 둔다.
"""))

# 8 SW-PL-08
R.append(("**처리** 업비트/빗썸 공개 API로 원화 마켓 가격 조회 → SW-PL-07 데이터와 동일 형식 정규화(`market_data`에 currency='KRW' 행 추가).",
"""**입력(⑨ 확인)** 인증 없는 공개 시세 API. 업비트 https://api.upbit.com/v1/ticker?markets=KRW-USDT (현재가), /v1/trades/ticks?market=KRW-USDT&count=200 (체결), /v1/candles/minutes/1?market=KRW-USDT (분봉), wss://api.upbit.com/websocket/v1 (실시간). 빗썸 https://api.bithumb.com/v1/ticker?markets=KRW-USDT, /v1/market/all. 빗썸은 버전, 호출 제한, 체결 보관기간을 개발자센터에서 재확인.

**처리** 업비트/빗썸 공개 API로 원화 마켓 가격 조회 → SW-PL-07 데이터와 동일 형식 정규화(`market_data`에 currency='KRW' 행 추가). "USDT가 1,400원"(원화 시장 체결가, 김치 프리미엄 포함)과 "USDT가 1달러 페그 유지"(USD 페그)는 다른 주장이므로 화면에는 KRW 가격, USD 가격, USD/KRW 환율, 프리미엄을 분리해 표시."""))

# 9 SW-PL-09 timestamps
R.append(("**처리** 종목명이 명시된 발행량/시총 주장부터 자동 추출·대조 → 성공 시 \"수치로 확인됨\" 부여 → 실패(종목·시점 불특정) 시 자동 판정 포기, \"관련 시장 차트 병치\" 축소안 전환.",
"""**처리** 종목명이 명시된 발행량/시총 주장부터 자동 추출·대조 → 성공 시 "수치로 확인됨" 부여 → 실패(종목·시점 불특정) 시 자동 판정 포기, "관련 시장 차트 병치" 축소안 전환.

대조 시 네 시점을 분리 기록한다(⑨): 주장 발생시점(발화 시각), 기사 게시시점, 데이터 기준시점(API 응답 timestamp 또는 보고서 date), 검증 실행시점. "현재 시총 1,700억 달러"는 기사 게시 직전 값과, "어제 350억 돌파"는 어제의 종가와 장중 고점을 구분해, "페그 유지"는 대상 기간의 최저/최고와 대조한다. 어느 소스 기준인지(DefiLlama, CoinGecko, Circle 보고서)를 판정 화면에 항상 노출한다. 제공자마다 시총 산정법이 달라 값이 어긋날 수 있고, 그 차이 자체가 주장의 일부다."""))

# 10 SW-TL-01 seeds (replace block)
old_seed = t[t.index("초기 시드(퍼플렉시티 리서치 2026-09-03 기준. **배치 전 원출처 확인 필수**"):]
old_seed = old_seed[:old_seed.index("50%+1 요건이 법 본문인지 시행령 위임인지.\n")+len("50%+1 요건이 법 본문인지 시행령 위임인지.\n")]
R.append((old_seed,
"""초기 시드(퍼플렉시티 리서치 2026-09-03. 원출처가 붙은 건은 배치 가능, 나머지는 **배치 전 원출처 확인 필수**, 아래 큐레이션 게이트 적용):
- 미국: 2025-07 GENIUS Act 제정 / 2025-09-19 재무부 ANPRM(원출처 미확보) / 2026-02-25 OCC 이행 NPRM([OCC 보도자료](https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-9.html), [Bulletin 2026-3](https://occ.treas.gov/news-issuances/bulletins/2026/bulletin-2026-3.html)) / 2026-06-22 FinCEN, OCC, Fed, FDIC, NCUA 공동 BSA/CIP 제안([연방관보 91 FR 37234](https://www.occ.gov/news-issuances/federal-register/2026/91fr37234.pdf)) / 2026-08-18 재무부 발행, 제공, 판매 금지 및 해외 발행자 NPRM([연방관보](https://www.govinfo.gov/content/pkg/FR-2026-08-18/pdf/2026-16796.pdf), 의견 마감 10-19는 보도) / OCC 최종규칙 목표 2026-11(보도, 확정 아님). 현재 상태: 법은 있으나 핵심 하위규정은 제안, 의견수렴 단계 — "은행이 지금 자유롭게 발행 가능"은 오류.
- EU: 2023-06-29 MiCA 발효([EUR-Lex 원문](https://eur-lex.europa.eu/eli/reg/2023/1114/oj/eng)) / 2024-06-30 ART, EMT 조항 적용, 2024-12-30 전면 적용([EUR-Lex 요약](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=legissum:4626998)) / 2025-01-17 ESMA 비준수 ART, EMT 정리 지침([ESMA](https://www.esma.europa.eu/press-news/esma-news/esma-and-european-commission-publish-guidance-non-mica-compliant-arts-and-emts)). 현재 상태: 적용 완료. 남은 건 회원국별 CASP 전환기간 종료와 ESMA 등록부 대조.
- 한국: 디지털자산기본법 **미제정**(2026-09-03 기준. 정부안 또는 정부안 기반 의원발의의 의안번호와 접수는 의안정보시스템에서 미확인) / 2026-01-06 금융위 은행 50%+1 컨소시엄 우선안 보도([서울경제](https://en.sedaily.com/finance/2026/01/06/korea-to-allow-won-stablecoin-issuance-by-bank-led), [조선비즈](https://biz.chosun.com/en/en-finance/2026/01/07/3JECOJXMBRGPJMO2UVZKKRIXAI/)) / 2026-05-29 KB 중심 컨소시엄 논의 보도([매경 Pulse](https://pulse.mk.co.kr/news/english/12060921)) / 2026-08-25 정부안 국회 제출 전 단계, 9월 제출 가능성 보도([조선비즈](https://biz.chosun.com/en/en-finance/2026/08/25/EABN4LDGF5E4VPYHJG45VTBL6A/), [BloomingBit](https://en.bloomingbit.io/feed/news/119127), [서울경제 08-27](https://en.sedaily.com/finance/2026/08/27/korea-weighs-20-percent-ownership-cap-for-crypto-exchange)). 향후 6개월 관찰점: 정부안 기반 발의 접수 여부, 정기국회 소위 통과 여부, 50%+1 요건이 법 본문인지 시행령 위임인지.

한국 레인 표기 규칙(⑩): (1) 21대 국회 법안(가상자산업법안 2109935 등 8건)은 임기 종료로 폐기됐을 가능성이 높으니 22대 계류 목록은 [의안정보시스템](https://likms.assembly.go.kr/law/lawsNormInqyMain1010.do?mappingId=/lawsNormInqyMain1010.do&genActiontypeCd=2ACT1010)에서 재확인 후에만 배치. (2) 은행 50%+1, 준비금, 환매권은 보도된 정책 방향이지 법률 확정 조항이 아니므로 "제출 예정/보도 단계" 배지. (3) 은행별 "컨소시엄 참여"는 은행 보도자료로 확인된 게 없다. 공식 참여 발표 / 언론상 검토 / 기술 PoC(우리-쿠팡 07-27) / 수탁 인프라 투자(KB KODA, 신한과 NH KDAC)의 4개 배지를 구분한다.
"""))

# 11 SW-VF-03
R.append(("**처리** SW-VF-02 매칭 결과를 등급 배지(색상/라벨) + 근거 기사 목록(원문 링크) + 각 근거의 신뢰도 값으로 렌더.",
"""**처리** SW-VF-02 매칭 결과를 등급 배지(색상/라벨) + 근거 기사 목록(원문 링크) + 각 근거의 신뢰도 값으로 렌더.

화면 요소 5개(퍼플렉시티 ⑫, [Google Fact Check Explorer](https://toolbox.google.com/factcheck/explorer)와 [Full Fact](https://fullfact.org/ai/) 패턴): (1) 원자 주장 텍스트 (2) 판정과 판정일 (3) 근거 목록과 계보 표시(공식 1차 자료 / 독립 보도 / 단일 보도) (4) 시점 4종(주장, 기사, 근거 기준, 검증 실행) (5) 이력(AI 초안, 사람 판정, 정정). 판단보류는 SNU팩트체크처럼 독립 배지로 두고 등급 정의 팝오버를 붙인다.

출력 스키마는 schema.org [ClaimReview](https://developers.google.com/search/docs/appearance/structured-data/factcheck)에 맞춘다. 필수는 claimReviewed, reviewRating.alternateName(사람이 읽는 판정명), url. 여기에 내부 확장 필드 claim_type, evidence_status, verdict, claim_datetime, evidence_as_of, verification_datetime, source_lineage_id, human_review_status, correction_history를 둔다. claims.json이 이 스키마를 그대로 쓰면 화면 렌더와 외부 공개가 같은 데이터로 된다.

사람 개입은 서버 없이 골드셋 작업(SW-PL-03)에서 CSV로 한다. 행동은 승인 / 수정 승인 / 보류 / 반려 / 재검증 요청 5종이고, 승인 외 4종은 사유 필수. 화면에는 그 결과 이력만 표시한다. 감사 추적 최소 필드([SR 11-7](https://www.federalreserve.gov/boarddocs/srletters/2011/sr1107.pdf)의 모델 인벤토리, 독립 검증, effective challenge 원칙 적용): 입력 기사 스냅숏 hash, 추출 주장, 모델과 프롬프트 버전, 근거 URL과 인용 구절, 판정, reviewer, 변경 이력. 한국 전자금융감독규정이 AI 판정 로그를 직접 의무화하는지는 조문 미확인이라 "내부통제 관점에서 요구될 수 있다"로만 쓴다."""))
R.append(("**AC** 등급 시각 배지 구분 / 근거 원문 목록·링크 노출 / 근거별 신뢰도 표시 / 근거 없는 경우 정상 안내.",
"**AC** 등급 시각 배지 구분 / 근거 원문 목록·링크 노출 / 근거별 신뢰도 표시 / 근거 없는 경우 정상 안내 / 시점 4종과 근거 계보 표시 / claims.json이 ClaimReview 필수 3필드 충족."))

# 12 §14 KPIs
R.append(("| 발표 데모 완주 | \"삼성 발행 확정?\" 류 질의 → 30초 내 판정+근거 제시 완주 | 성공/실패(이진) |\n",
"""| 발표 데모 완주 | "삼성 발행 확정?" 류 질의 → 30초 내 판정+근거 제시 완주 | 성공/실패(이진) |
| 근거충족률 | 최종 판정 중 1차 자료 또는 독립 복수 근거가 연결된 비율(골드셋 50건 기준) | **[미기입 — 골드셋 후 결정]** |
| AI 수정률 | AI 초안 판정이 사람에 의해 바뀐 비율(골드셋 50건) | 측정값 보고(목표치 없음) |
| 보류 해소율 | 판단보류였던 주장이 후속 자료로 확인 또는 반박된 비율 | 측정값 보고 |
| 총 처리 리드타임 | 기사 수집부터 판정 또는 보류 상태까지 | 측정값 보고 |

주장 1건당 평균 검증 시간을 기관별로 공개한 외부 벤치마크는 없다(퍼플렉시티 ⑫). "사람보다 빠른 AI"라고 쓰지 말고 위 자체 지표로 말한다. 판정기 신뢰도의 일치율은 Cohen's κ와 함께 보고한다(SW-PL-03).
"""))

# 13 §15 replace URL item with new unknowns
R.append(("- 퍼플렉시티 리서치(2026-09-03) 반영분의 **원출처 URL 부착** — §3(한은 VASP 모니터링, 한은 은행 중심 발행 입장, 금융위 50%+1 보도, JPMorgan/Citi), §6(데이터셋 7종 논문 링크), §11(시장 규모 조사기관 4곳, 경쟁사 수치), SW-TL-01(마일스톤 전건). 퍼플렉시티 스레드에서 원출처 링크를 복사해 붙인다. 인용은 퍼플렉시티가 아니라 원출처로.",
"""- 한국은행 보도자료 RSS endpoint — 아이콘은 있으나 URL 미확정. 페이지 소스에서 1회 추출(SW-PL-04)
- 금융감독원 일반 보도자료 목록 URL과 pagination 구조 — 미확정(SW-PL-04)
- 22대 국회 계류 디지털자산 법안 목록과 정부안 접수 여부 — 의안정보시스템에서 9월 중 재확인(SW-TL-01)
- 은행별 컨소시엄 공식 참여 발표 — 은행 보도자료로 확인된 건 없음. 보도만 존재(SW-TL-01 한국 레인 배지 규칙)
- 은행권 디지털자산 채용공고 원문 2025~2026 — 확보 실패. 은행 채용 페이지와 아카이브 재조사(§3 페르소나, 커리어)
- 은행연합회, 금융연구원, 자본시장연구원 스테이블코인 보고서 목록과 인용 정보원 비율 — 원문 미확보. 확보 후 각주 코딩(규제기관/법령/중앙은행/국제기구/학술/공시/발행사/리서치사/언론)
- 전자금융감독규정에 AI 판정 로그 보관 의무 조문이 있는지 — 미확인. 법률 검토 전까지 단정 금지(SW-VF-03)
- 1차 출처 없음으로 확정된 2건: 한은 "은행 중심 발행" 직접 문서, JPMorgan Smart Buzz 제품 페이지 — 보도 기반으로만 인용"""))
R.append(("- 1차 사료 RSS 가용성 — SW-PL-04에 실측 반영(5곳 RSS 확인, 한은만 HTML).",
"- 1차 사료 RSS 가용성 — SW-PL-04에 실측 반영(5곳 RSS 확인, 한은만 HTML).\n- 퍼플렉시티 1차 반영분 원출처 URL — 2차 ⑦ 회수분을 §3, SW-TL-01에 인라인, 나머지는 §16 리서치 원출처에 부착. MarketsandMarkets, Moody's Grid 제품 페이지, DLT-Sentiment-News는 발행일 미확인."))

# 14 §16
R.append(("- **퍼플렉시티 리서치(2026-09-03)**: 프롬프트 6종(데이터 정당성, 은행 워크플로, 경쟁과 시장, 1차 사료 RSS, 규제 타임라인, 미확인 팩트체크). 결과는 퍼플렉시티 스레드에 있음 — 레포 저장 여부 미결\n",
"""- **퍼플렉시티 리서치(2026-09-03, 스레드 https://www.perplexity.ai/search/c983a5bc-3322-4f34-9249-7a03cf360ef6 )**: 1차 6종(데이터 정당성, 은행 워크플로, 경쟁과 시장, 1차 사료 RSS, 규제 타임라인, 미확인 팩트체크) + 2차 6종(원출처 회수, 골드셋 판정 가이드라인, 시장 데이터 소스, 한국 입법 원문, 은행 조직과 채용, 팩트체크 UI 표준). 레포 저장 여부 미결

### 리서치 원출처(⑦ 회수분, 인용은 이 링크로)

- 데이터셋: [FEVER 논문](https://aclanthology.org/N18-1074.pdf), [FEVER 데이터](https://fever.ai/dataset/fever.html), [AVeriTeC 논문](https://proceedings.neurips.cc/paper_files/paper/2023/hash/cd86a30526cd1aff61d6f89f107634e4-Abstract-Datasets_and_Benchmarks.html), [AVeriTeC 저장소](https://github.com/MichSchli/AVeriTeC), [MultiFC](https://aclanthology.org/D19-1475/), [Fin-Fact 논문](https://arxiv.org/html/2309.08793v2), [Fin-Fact 저장소](https://github.com/IIT-DM/Fin-Fact), [FINDVER](https://aclanthology.org/2024.emnlp-main.818/), [CryptoLin 논문](https://link.springer.com/article/10.1007/s10579-024-09743-x), [CryptoLin 저장소](https://github.com/manoelgadi/CryptoLin), [DLT-Corpus 논문](https://arxiv.org/html/2602.22045), [DLT-Sentiment-News](https://huggingface.co/datasets/ExponentialScience/DLT-Sentiment-News)
- 한국 기관: [한은 VASP 자료제출 모니터링 2025-09-19](https://www.bok.or.kr/eng/bbs/E0000866/view.do?nttId=10093606&oldMenuNo=400007&menuNo=400223&programType=newsDataEng&depth=400223&relate=Y), [한은 스테이블코인 이슈해설 2026-02-20](https://www.bok.or.kr/portal/bbs/B0000168/view.do?menuNo=200058&nttId=10094368), [금융위 50%+1 보도, 서울경제 2026-01-06](https://en.sedaily.com/finance/2026/01/06/korea-to-allow-won-stablecoin-issuance-by-bank-led), [조선비즈 2026-01-07](https://biz.chosun.com/en/en-finance/2026/01/07/3JECOJXMBRGPJMO2UVZKKRIXAI/), [KB KODA, BloomingBit 2025-02-14](https://en.bloomingbit.io/feed/news/83346), [신한과 NH KDAC, Wowtale 2025-11-26](https://en.wowtale.net/2025/11/26/232926/)
- 해외 은행: [JPMorgan Kinexys 대담](https://www.jpmorgan.com/insights/podcast-hub/making-sense/digital-assets-kinexys-and-regulatory-shifts), [JPMorgan 디지털자산 문서](https://www.jpmorgan.com/content/dam/jpm/cib/complex/content/securities-services/regulatory-solutions/evolution-of-digital-assets.pdf), [Citi Digital Assets](https://www.citigroup.com/global/about-us/strategy/digital-assets)
- 시장 규모와 경쟁: [MarketsandMarkets](https://www.marketsandmarkets.com/Market-Reports/regtech-market-63447434.html), [Future Market Insights](https://www.futuremarketinsights.com/reports/regtech-market), [360iResearch](https://www.360iresearch.com/library/intelligence/regtech), [FinTech Global 2026 보고서](https://fintech.global/about/wp-content/uploads/2026/06/The-Global-State-of-RegTech-2026-Full-Report.pdf), [Market Intelo adverse media](https://marketintelo.com/report/adverse-media-screening-market), [Moody's Grid 브로슈어 2026-05](https://www.moodys.com/web/en/us/site-assets/ma-kyc-grid-product-brochure-may2026.pdf), [ComplyAdvantage](https://complyadvantage.com/fincrime-risk-intelligence/negative-news-screening-tool/)
- 규제 원문: SW-TL-01 시드에 인라인 부착
- 판정 기준과 UI: [Reuters 기준](https://reutersagency.com/about/standards-values/), [Google Fact Check Explorer](https://toolbox.google.com/factcheck/explorer), [Google Fact Check markup](https://developers.google.com/search/docs/appearance/structured-data/factcheck), [Google Fact Check Tools API](https://developers.google.com/fact-check/tools/api/reference/rest/v1alpha1/claims), [Full Fact AI](https://fullfact.org/ai/), [Full Fact Stats Checker](https://fullfact.ai/blog/claim-challenge-update/), [SR 11-7](https://www.federalreserve.gov/boarddocs/srletters/2011/sr1107.pdf), [Circle 투명성](https://www.circle.com/transparency), [Tether 투명성](https://tether.to/transparency/?tab=reports), [DefiLlama API](https://api.llama.fi/stablecoins)
"""))

for i,(o,n) in enumerate(R):
    c=t.count(o)
    assert c==1, f"edit {i}: count={c} :: {o[:60]!r}"
    t=t.replace(o,n)
open(p,'w',encoding='utf-8').write(t)
print("ok",len(R),"edits")
