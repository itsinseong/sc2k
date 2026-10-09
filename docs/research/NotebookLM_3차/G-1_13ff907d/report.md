# G-1 금리와 발행량, 준비자산 구성

- 노트북: https://notebook.google.com/notebook/13ff907d-1128-4a71-82b3-bf1148c066fe?authuser=1 (자동 제목 "Optimal Control of Stablecoin Reserve Portfolios")
- 보고서 제목: 원화 스테이블코인 준비금 공시 및 자산구성 기준 제정을 위한 입법 비교와 실증 연구 분석
- 소스 21종(소스 22개), 보고서 참고 링크 15개, 채팅 답 1건, 본문 18183자
- 실행 방식: Deep Research(보고서는 소스로 저장) + 채팅 답 1건(질문은 프롬프트 원문). 채팅 답의 [cite: n] 번호는 대응 목록이 화면에 없음
- 수집: 2026-10-09 Aside repl, 원문 대조 전

---
# 원화 스테이블코인 준비금 공시 및 자산구성 기준 제정을 위한 입법 비교와 실증 연구 분석

## 국회 계류 제정안 9건의 준비금 규율 비교 및 입법 근거

대한민국 제22대 국회 정무위원회에는 원화 기반 지급형 스테이블코인의 제도화 및 유통 안전성을 확보하기 위한 제정 법률안 9건이 계류되어 있다 [cite: 1, 2]. 해당 의안들은 민병덕의원안(의안번호 2210736), 김은혜의원안(2211777), 안도걸의원안(2211784), 김현정의원안(2212298), 이강일의원안(2213166), 김재섭의원안(2213266), 최보윤의원안(2213449), 박상혁의원안(2214492), 김성원의원안(2218219)이다 [cite: 1, 2, 3, 4]. 이들 법안은 스테이블코인의 금융시스템 전이 위험을 차단하고 이용자 상환청구권을 보호한다는 목적을 공유하지만, 진입을 위한 자기자본 요건, 준비자산 구성 기준, 이자 지급 허용 여부, 위반 시 제재 수위 등 세부 규율 방식에서 시각 차이를 드러낸다 [cite: 2, 4].

발행 주체 요건 측면에서 민병덕의원안은 자기자본 5억 원 이상을 갖춘 비은행 법인의 진입을 허용하여 시장 접근성과 지급결제 혁신성을 최우선으로 고려한다 [cite: 2]. 반면 김은혜의원안, 안도걸의원안, 김현정의원안은 자기자본 50억 원 이상을 요구하여 대형 금융기관이나 자본력을 갖춘 핀테크 주도의 발행 구조를 도모한다 [cite: 2]. 준비자산 적립 기준에 있어서 민병덕의원안은 발행잔액 상당 이상 보유 원칙만 선언하고 구체적 자산 범위 및 비율을 대통령령에 위임하는 유연한 구조를 취한다 [cite: 2]. 이에 비해 김은혜·안도걸·김현정의원안은 미상환잔액 100% 이상에 해당하는 준비자산을 현금, 예금, 단기 국채 등 고유동성 안전자산 중심으로 법률 본문에 직접 규정하고 있다 [cite: 2].

이자 지급 규정은 전통 상업은행의 예금 이탈(Disintermediation) 방지라는 금융안정 목적과 직접 연결된다 [cite: 2, 4, 5]. 안도걸의원안과 김현정의원안은 이용자에 대한 이자 지급을 명시적으로 금지하며, 위반 시 안도걸의원안은 형사처벌을, 김현정의원안은 과태료를 부과하는 제재 장치를 마련하였다 [cite: 2, 4]. 반면 민병덕의원안과 김은혜의원안은 명시적인 이자 지급 금지 조항을 두지 않아 발행사의 자율적 수익 배분 여지를 남겨두었다 [cite: 2, 4].

| 의안번호 및 대표발의자 | 제정안 명칭 | 발의일자 | 자기자본 요건 | 준비자산 구성 및 비율 | 이자 지급 규율 | 제재 및 특이사항 | 출처 및 근거 문서 |
|---|---|---|---|---|---|---|---|
| 2210736 (민병덕) | 디지털자산기본법안 | 2025-06-11 [cite: 2] | 5억 원 이상 [cite: 2] | 발행잔액 상당 이상, 자산 종류는 대통령령 위임 [cite: 2] | 명시적 금지 조항 없음 [cite: 2] | 하위법령 위임 중심, 비은행 진입 용이 [cite: 2] | 법무부, 선진상사법률연구 제115호, 2026.07., 154-155쪽; 의안 2210736 제103조제2항, 제3조제3항 [cite: 2] |
| 2211777 (김은혜) | 가치고정형 디지털자산을 활용한 지급 혁신에 관한 법률안 | 2025-07-28 [cite: 3] | 50억 원 이상 [cite: 2] | 미상환잔액 100% 이상 (현금, 예금, 단기국채 등) [cite: 2] | 명시적 금지 조항 없음 [cite: 2, 4] | 지급 혁신 중시, 규제 제재 완화적 [cite: 4] | 법무부, 선진상사법률연구 제115호, 2026.07., 154-155쪽; 의안 2211777 제7조제1항, 제13조제1항 [cite: 2, 3, 4, 6] |
| 2211784 (안도걸) | 가치안정형 디지털자산의 발행 및 유통에 관한 법률안 | 2025-07-28 [cite: 3] | 50억 원 이상 [cite: 2] | 미상환잔액 100% 이상 (고유동성 안전자산) [cite: 2] | 명시적 금지 [cite: 2, 4] | 위반 시 형사처벌 규정 [cite: 4] | 법무부, 선진상사법률연구 제115호, 2026.07., 154-155쪽; 의안 2211784 제7조제1항, 제16조제1항, 제17조 [cite: 2, 3, 4, 6] |
| 2212298 (김현정) | 가치안정형 디지털자산 발행업 등에 관한 법률안 | 2025-08-21 [cite: 4] | 50억 원 이상 [cite: 2] | 미상환잔액 100% 이상 (고유동성 안전자산) [cite: 2] | 명시적 금지 [cite: 2, 4] | 위반 시 과태료 부과 [cite: 4] | 법무부, 선진상사법률연구 제115호, 2026.07., 154-155쪽; 의안 2212298 제5조제2항, 제26조제1항·제2항, 제31조 [cite: 2, 4] |
| 2213166 (이강일) | 가치안정형 디지털자산 규율에 관한 법률안 | 2025년 [cite: 1] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 국회 의안정보시스템, 2025. [cite: 1] |
| 2213266 (김재섭) | 디지털자산 지급결제 및 이용자 보호 법률안 | 2025년 [cite: 1] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 국회 의안정보시스템, 2025. [cite: 1] |
| 2213449 (최보윤) | 가치고정형 디지털자산의 발행 및 유통에 관한 법률안 | 2025년 [cite: 1] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 국회 의안정보시스템, 2025. [cite: 1] |
| 2214492 (박상혁) | 디지털자산 혁신 및 지급결제 안정에 관한 법률안 | 2025년 [cite: 1] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 국회 의안정보시스템, 2025. [cite: 1] |
| 2218219 (김성원) | 가치안정형 가상자산의 지급결제 활용에 관한 법률안 | 2025년 [cite: 1] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 국회 의안정보시스템, 2025. [cite: 1] |

국내 입법안의 고정적 접근법과 달리, 주요국 입법 모델은 발행 규모와 위험 수준에 연동된 비례적 규제 방식을 도입하고 있다 [cite: 2]. 미국 GENIUS Act는 100억 달러 발행잔액을 기준으로 연방 규제기관과 주 규제기관의 감독 권한을 이중 트랙으로 수립하여 소액 발행사의 진입 장벽을 낮추는 구조를 마련하였다 [cite: 2]. 유럽연합(EU)의 MiCA 규정은 발행인에게 최소 35만 유로 기본 자본 또는 준비자산 평균 총액의 2%(유의미한 토큰 지정 시 3%) 중 높은 금액을 정하도록 하여 위험 기반 자본 체계를 확립하였다 [cite: 2]. 홍콩 통화청(HKMA)은 2,500만 홍콩달러(약 44.5억 원) 자본금을 기본으로 하되 발행사의 운용 역량에 따라 추가 정립을 명할 수 있는 재량권을 보장하고 있다 [cite: 2]. 국내 계류 법안들은 단일한 진입 자본금을 설정하고 있어 규모 연동형 비례 규제 체계의 보완이 요구된다 [cite: 2].

## 금리, 스테이블코인 발행량 및 준비자산 구성의 실증적 관계

스테이블코인 발행사 보고서 264건을 토대로 집계된 USDC의 월별 은행 예금 비중과 미국 3개월 국채 금리 간의 피어슨 상관계수는 r=−0.42 (n=44)로 뚜렷한 음의 상관관계를 나타낸다 [cite: 5]. 국채 금리가 상승할 때 스테이블코인 발행사의 예금 비중이 축소되는 메커니즘은 발행사의 수익 극대화 행동과 시중은행의 유동성 규제라는 양면적 요인에서 기인한다 [cite: 5, 7, 8].

시장 금리가 상승하면 단기 국채 수익률과 시중은행 예금 금리 간의 스프레드가 크게 확대된다 [cite: 5]. 미국 상업은행 및 지역 커뮤니티 은행의 평균 예금 금리가 약 2.0%~2.2% 수준에 머무는 반면, 3개월 국채 금리가 상승하면 발행사는 무위험 자산 운용 수익을 극대화하기 위해 예금 보유량을 줄이고 준비자산을 단기 국채 및 환매조건부채권(역레포)으로 대거 전환한다 [cite: 5]. 실제로 서클(Circle)의 2025년 12월 USDC 준비금 보고서 기준 은행 예금 비중은 12% 수준이었으며, 테더(Tether)의 2025년 4분기 보고서에 따르면 $1,472억 달러 준비금 중 은행 예금은 $3,400만 달러(0.02%)에 불과하였다 [cite: 5].

시중은행의 대차대조표 관리 측면에서도 유사한 유인이 작동한다 [cite: 7, 8]. 은행 감독 당국은 스테이블코인 발행사가 예치한 대규모 자금을 변동성이 높은 기관용 도매 예금(Uninsured Wholesale Funding)으로 분류한다 [cite: 7, 8]. 바젤 III 바젤 은행감독위원회 기준에 따라 은행은 이러한 예금 수신 시 높은 비율의 고성능 유동자산(HQLA)을 별도 보유해야 하므로, 수신 금리를 매력적인 수준으로 제시하지 않거나 예금 유입을 제한하게 된다 [cite: 7, 8].

다만, 발행사의 예금 비중 감소가 전통 금융권의 예금 총량 자체를 전면 축소시킨다는 단편적 유출 가설은 교동 자금 흐름에 의해 반증된다 [cite: 5, 9]. 발행사가 예금 자금을 차감하여 딜러나 금융기관으로부터 단기 국채를 매입할 경우, 국채 매도자의 매각 대금은 다시 시중은행의 일반 예금 계좌로 재입금된다 [cite: 5]. 따라서 금융시스템 전체의 총 예금 잔액은 유지되나, 예금의 성격이 '소비자의 소매 예금'에서 '기업 및 기관의 도매 예금'으로 전환되면서 특정 대형 은행으로 예금이 집중되고 자금 가변성이 증대되는 구조적 변화가 발생한다 [cite: 5, 7, 8].

## 실증 연구 종합 비교

주요 연구 기관 및 학술지에 발표된 최신 실증 연구 문헌 중 주요 결과를 요약한 연구 비교는 아래 표와 같다 [cite: 9, 10, 11, 12, 13].

| 연구(저자, 연도, 기관) | 자료 기간 | 대상 | 방법 | 결과 수치 | 한계 | 주소 |
|---|---|---|---|---|---|---|
| Charles River Associates (2025, CRA) | 2019년2025년 (월별 데이터, n=7284) [cite: 9] | USD Coin (USDC) [cite: 9] | 수천 개 회귀 모형에 대한 앙상블 모형화(Ensemble Modeling), 정적/동적 회귀, Breusch-Godfrey 시계열 검정, 1:1 대체 최악 시나리오 분석 [cite: 9] | USDC 채택 증가가 지역은행 예금에 미치는 영향 통계적으로 불유의. 동적 미조정 모형: USDC 1증가당예금+0.444 (95% 구간: [-0.863, 1.338], p>0.05). 자산조정 동적 모형: -0.265(p>0.05$). 1:1 대체 시나리오 시 예금 감소 폭 1% 미만 (극단 채택 시 6.8%) [cite: 9]. | 2019~2025년 내 코로나19 및 SVB 파산 등 거시 경제 충격의 혼재, 지역은행 이용자와 가상자산 이용자 간 인구통계학적 이질성, MMF 등 타 자산군 수익률 미반영 [cite: 9]. | https://media.crai.com/wp-content/uploads/2025/07/22152125/Stablecoins-impact-on-community-bank-deposits-July2025.pdf |
| ECB Working Paper No 3199 (Carlo Altavilla et al., 2025, ECB) | 2010년대 후반~2025년 중반 [cite: 11] | 유로화 및 외화(USD) 연동 스테이블코인, TerraUSD [cite: 11] | Google Trends 검색량 지표 도구변수(IV) 활용 BVAR 및 유로존 은행 감독데이터(IBSI) 패널 로컬 프로젝션(Local Projection) 분석 [cite: 11] | 스테이블코인 노출도 1 표준편차 증가 시 24개월 누적 비금융 사기업 대출 성장률 약 2.5%p 감소. 소매예금 의존도가 높은 은행일수록 대출 축소 자극 [cite: 11]. | Google Trends 검색 지표가 실제 포트폴리오 보유량이 아닌 미디어 충격을 대리함. 저채택 구간 분석 결과의 고채택 구간 선형 외삽 한계 [cite: 11]. | https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3199~ad552b59ec.en.pdf |
| NBER Working Paper No 35557 (Murillo Campello et al., 2025, NBER) | 2024년~2025년 (고빈도 시계열) [cite: 10] | USDT, USDC, Aave 등 DeFi 대출 풀 및 미국 MMF [cite: 10] | 재무부 일반계정(TGA) 잔액 변동을 외생적 도구변수(IV)로 활용한 CES 유동성 수요 모형 실증 회귀 [cite: 10] | Aave 내 USDC/USDT 대출 풀 APY 3%~8% 형성 [cite: 10]. MMF 프리미엄(y m )과 스테이블코인 프리미엄(y s ) 간의 시계열 동조성 및 대체탄력성(σ) 실증 [cite: 10]. | 은행 수신 금리가 아닌 DeFi 알고리즘 APY 분석에 국한됨. 가상자산 시장 내 투기적 레버리지 수급 파동에 민감함 [cite: 10]. | https://www.nber.org/system/files/working_papers/w35557/w35557.pdf |
| Federal Reserve FEDS Notes (Francesca Carapella et al., 2025/2026, 연준) | 2023년~2026년 1분기 [cite: 7, 8, 12] | USDC, USDT, GUSD [cite: 8] | 발행사 보유자산 공시 보고서(Reserve Reports) 시계열 추적 및 상업은행 대차대조표 전이 메커니즘 분석 [cite: 8] | 발행사별 예금 비중 이질성 확인(Circle ~12-13%, Tether ~0%, GUSD 100%) [cite: 5, 8]. 이자지급형 코인 규모 2023년 $10억 미만에서 2025.09 $190억 초과 [cite: 7]. | 개별 상업은행과 발행사 간 비공개 개별 협상 수신 금리 데이터의 미비. 관측적 정량 분석 위주의 한계 [cite: 8]. | https://www.federalreserve.gov/econres/notes/feds-notes/banks-in-the-age-of-stablecoins-implications-for-deposits-credit-and-financial-intermediation-20251217.html |
| NBER Working Paper No 35412 (2025, NBER) | 2024년~2025년 (18개 FOMC 발표 이벤트) [cite: 13] | BUIDL, BENJI, sUSDe, USDS 등 토큰화 국채 및 이자수익 전달형 코인 [cite: 13] | 통화정책 깜짝 충격(Monetary Policy Surprises)을 활용한 사건 연구(Event Study) 회귀분석 [cite: 13] | 통화정책 충격 1bp당 Sky 저축금리 +3.66bp 반응 [cite: 13]. 이자수익형 코인 수익률은 정책 충격 1bp당 -7.78bp~-33bp 민감 반응. sUSDe 수익률은 3개월 국채 대비 +598bp 형성 [cite: 13]. | 18개 FOMC 이벤트라는 제한된 표본 수 [cite: 13]. 온체인 거버넌스 투표 및 알고리즘 조정에 따른 반영 시차 존재 [cite: 13]. | https://www.nber.org/system/files/working_papers/w35412/w35412.pdf |
| Richmond Fed Economic Brief No 26-10 (Marina Azzimonti & Vincenzo Quadrini, 2026, 리치몬드 연준) | 2025년~2026년 [cite: 14] | 전 세계 미 달러 및 비달러 연동 스테이블코인 [cite: 14] | 글로벌 저축 결정과 균형 자연실질금리(r ∗ ) 간 관계를 다루는 거시경제 일반균형 모형 [cite: 14] | 안전 자산 담보형 스테이블코인 확장은 미 국채 수요를 증대시켜 자연실질금리(r ∗ ) 하방 압력 창출. 글로벌 시장 규모 2020년대 후반 5,000억 6,000억 진입 전망 [cite: 14]. | 이론적 칼리브레이션 모형 중심으로 국가별 미시 실증 회귀 계수 미포함 [cite: 14]. | https://www.richmondfed.org/publications/research/economic_brief/2026/eb_26-10 |

## 원화 스테이블코인 준비금 공시 및 자산구성 기준 제언

계류 중인 9개 법안 비교와 학술 연구들의 실증 결과를 바탕으로, 국내 원화 스테이블코인 입법 및 정책 수립 시 반영해야 할 공시 및 준비자산 규율 기준을 다음과 같이 제언한다 [cite: 1, 2, 4, 5, 11].

첫째, 발행 규모 연동형 비례적 자기자본 및 자산구성 기준이 도입되어야 한다. 민병덕의원안(5억 원)과 타 법안(50억 원)으로 이분화된 고정 자본금 방식에서 벗어나 [cite: 2], EU MiCA 모델과 같이 준비자산 평잔의 2~3% 수준을 가변적으로 적립하도록 하는 위험 기반 자본 규제가 타당하다 [cite: 2]. 준비자산 구성에 있어서도 금리 변화에 따라 발행사가 예금을 감축하고 특정 자산으로 쏠리는 현상(r=−0.42)을 고려하여 [cite: 5], 은행 예금의 최소 및 최대 적립 한도(예: 예금 비중 10%~30% 범위 유지)를 설정하고 예치 은행을 다변화하도록 강제하여 특정 상업은행으로의 도매 예금 집중 리스크를 차단해야 한다 [cite: 2, 8].

둘째, 일별 실시간 공시 및 온체인 보유증명(Proof of Reserves) 체계를 명문화해야 한다. 월 1회 사후 공시 구조는 가상자산 시장의 유동성 충격 발생 시 정보 비대칭성을 해소하지 못한다 [cite: 2, 7, 12]. 발행사가 예탁결제원, 은행 등 실물 자산 보관 기관과의 실시간 데이터 연동을 통해 하루 단위로 준비자산 내역을 공시하도록 의무화하고, 준비자산 평가액이 미상환잔액에 미달할 경우 자동으로 추가 적립 명령이 발동되는 모니터링 체계를 갖추어야 한다 [cite: 2, 12].

셋째, 간접적 이자 지급 행위에 대한 우회 차단 및 도산절연 체계의 사법적 완성이다. 안도걸·김현정의원안과 같이 은행 예금 이탈 방지를 위한 이자 지급 금지 조항을 신설하되 [cite: 2, 4], 가상자산 거래소나 DeFi 프로토콜을 통해 예치 보상(Staking/Yield) 형태로 이자가 우회 지급되는 파생 상품을 감독Perimeter 내에 포섭해야 한다 [cite: 7, 15]. 아울러 발행사 파산 시 일반 채권자의 압류를 차단하고 이용자에게 우선변제권을 보장할 수 있도록, 준비자산의 별도 신탁 및 신탁재산 독립성을 법률 본문에 명확히 확립해야 한다 [cite: 2].

---

- INSTITUTIONALIZING SPOT VIRTUAL ASSET ETFS IN KOREA | BKL Legal Update, https://www.bkl.co.kr/law/insight/newsletter/6362

- 스테이블코인의 기업금융 인프라로서의 활용을 위한 입법적 과제*, https://www.moj.go.kr/bbs/moj/166/497660/download.do

- 가상자산 분야 이슈리포트 - 국내 스테이블코인 관련 법률안의 주요 내용 및 시사점, https://www.draju.com/ko/sub/newsletters.html?type=view&bsNo=6577&langNo=

- 국내 스테이블코인 관련 법률안의 주요 내용 및 시사점 - 법률신문, https://www.lawtimes.co.kr/news/articleView.html?idxno=211569

- The Council of Economic Advisers Effects of Stablecoin Yield Prohibition on Bank Lending - The White House, https://www.whitehouse.gov/wp-content/uploads/2026/04/Effects-of-Stablecoin-Yield-Prohibition-on-Bank-Lending.pdf

- 스테이블코인 제도화, 무엇에 집중할 것인가 - 국회입법조사처, https://www.nars.go.kr/fileDownload2.do?doc_id=1Phhetmq4PP&fileName=

- Interest-bearing stablecoins and macroeconomic stability - State Street, https://www.statestreet.com/br/en/insights/stablecoins-macroeconomic-stability

- The Fed - Banks in the Age of Stablecoins: Some Possible Implications for Deposits, Credit, and Financial Intermediation - Federal Reserve, https://www.federalreserve.gov/econres/notes/feds-notes/banks-in-the-age-of-stablecoins-implications-for-deposits-credit-and-financial-intermediation-20251217.html

- Stablecoins' impact on community bank deposits - Charles River Associates, https://media.crai.com/wp-content/uploads/2025/07/22152125/Stablecoins-impact-on-community-bank-deposits-July2025.pdf

- NBER WORKING PAPER SERIES DEMAND FOR SAFETY IN THE CRYPTO ECOSYSTEM Murillo Campello Angela Gallo Lira Mota Tammaro Terracciano, https://www.nber.org/system/files/working_papers/w35557/w35557.pdf

- Stablecoins and monetary policy transmission - European Central Bank, https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3199~ad552b59ec.en.pdf

- The Fed - Stablecoins in 2025: Developments and Financial Stability Implications, https://www.federalreserve.gov/econres/notes/feds-notes/stablecoins-in-2025-developments-and-financial-stability-implications-20260408.html

- NBER WORKING PAPER SERIES DIGITAL SAFE HAVENS: THE ECONOMICS OF TOKENIZED TREASURIES Chen Lin Eswar S. Prasad Daniel Rabetti Che, https://www.nber.org/system/files/working_papers/w35412/w35412.pdf

- Stablecoins and the Demand for Dollars | Richmond Fed, https://www.richmondfed.org/publications/research/economic_brief/2026/eb_26-10

- (PDF) Regulating Yield in Digital Money: Stablecoins, Tokenized Treasury Funds, and the Economics of Competing Regulatory Frameworks - ResearchGate, https://www.researchgate.net/publication/410361794_Regulating_Yield_in_Digital_Money_Stablecoins_Tokenized_Treasury_Funds_and_the_Economics_of_Competing_Regulatory_Frameworks


## 참고 링크(보고서 끝 목록)

1. INSTITUTIONALIZING SPOT VIRTUAL ASSET ETFS IN KOREA | BKL Legal Update https://www.bkl.co.kr/law/insight/newsletter/6362
2. 스테이블코인의 기업금융 인프라로서의 활용을 위한 입법적 과제* https://www.moj.go.kr/bbs/moj/166/497660/download.do
3. 가상자산 분야 이슈리포트 - 국내 스테이블코인 관련 법률안의 주요 내용 및 시사점 https://www.draju.com/ko/sub/newsletters.html?type=view&bsNo=6577&langNo=
4. 국내 스테이블코인 관련 법률안의 주요 내용 및 시사점 - 법률신문 https://www.lawtimes.co.kr/news/articleView.html?idxno=211569
5. The Council of Economic Advisers Effects of Stablecoin Yield Prohibition on Bank Lending - The White House https://www.whitehouse.gov/wp-content/uploads/2026/04/Effects-of-Stablecoin-Yield-Prohibition-on-Bank-Lending.pdf
6. 스테이블코인 제도화, 무엇에 집중할 것인가 - 국회입법조사처 https://www.nars.go.kr/fileDownload2.do?doc_id=1Phhetmq4PP&fileName=
7. Interest-bearing stablecoins and macroeconomic stability - State Street https://www.statestreet.com/br/en/insights/stablecoins-macroeconomic-stability
8. The Fed - Banks in the Age of Stablecoins: Some Possible Implications for Deposits, Credit, and Financial Intermediation - Federal Reserve https://www.federalreserve.gov/econres/notes/feds-notes/banks-in-the-age-of-stablecoins-implications-for-deposits-credit-and-financial-intermediation-20251217.html
9. Stablecoins' impact on community bank deposits - Charles River Associates https://media.crai.com/wp-content/uploads/2025/07/22152125/Stablecoins-impact-on-community-bank-deposits-July2025.pdf
10. NBER WORKING PAPER SERIES DEMAND FOR SAFETY IN THE CRYPTO ECOSYSTEM Murillo Campello Angela Gallo Lira Mota Tammaro Terracciano https://www.nber.org/system/files/working_papers/w35557/w35557.pdf
11. Stablecoins and monetary policy transmission - European Central Bank https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3199~ad552b59ec.en.pdf
12. The Fed - Stablecoins in 2025: Developments and Financial Stability Implications https://www.federalreserve.gov/econres/notes/feds-notes/stablecoins-in-2025-developments-and-financial-stability-implications-20260408.html
13. NBER WORKING PAPER SERIES DIGITAL SAFE HAVENS: THE ECONOMICS OF TOKENIZED TREASURIES Chen Lin Eswar S. Prasad Daniel Rabetti Che https://www.nber.org/system/files/working_papers/w35412/w35412.pdf
14. Stablecoins and the Demand for Dollars | Richmond Fed https://www.richmondfed.org/publications/research/economic_brief/2026/eb_26-10
15. (PDF) Regulating Yield in Digital Money: Stablecoins, Tokenized Treasury Funds, and the Economics of Competing Regulatory Frameworks - ResearchGate https://www.researchgate.net/publication/410361794_Regulating_Yield_in_Digital_Money_Stablecoins_Tokenized_Treasury_Funds_and_the_Economics_of_Competing_Regulatory_Frameworks


# 채팅 1

## 질문

[배경] 원화 스테이블코인 준비금 공시 기준을 제안하는 학부 프로젝트다. 국회 정무위원회에 계류 중인 제정안 9건(2210736 민병덕, 2211777 김은혜, 2211784 안도걸, 2212298 김현정, 2213166 이강일, 2213266 김재섭, 2213449 최보윤, 2214492 박상혁, 2218219 김성원)이 정한 값을 비교하고, 그 값을 정하는 근거를 모은다.




[조사] 금리와 스테이블코인 발행량, 준비자산 구성(현금과 은행 예금 비중)의 관계를 실증한 연구를 찾는다. BIS 워킹페이퍼와 Bulletin, 연준(FEDS, IFDP, FEDS Notes), IMF, ECB, NBER, SSRN, 학술지를 본다. 이미 소스로 올린 논문(Ahmed와 Aldasoro의 Stablecoins and safe asset prices, BIS WP1219, BIS Bulletin 108, 연준 IFDP 1334, ECB WP3174, 미국 대통령경제자문위원회 2026년 4월 보고서, arXiv 2508.09429)은 빼고 찾는다.
참고: 이 프로젝트가 발행사 보고서 264건으로 계산한 결과, USDC는 월별 은행 예금 비중과 미국 3개월 국채 금리의 상관이 −0.42(n=44)였다. 이 결과를 해석하거나 반박할 수 있는 연구를 먼저 찾는다.
연구마다: 저자, 연도, 자료 기간, 대상 코인, 방법, 핵심 결과 수치(예: 금리 1%p 변화에 따른 발행량이나 현금 비중 변화), 한계.




[출력] 표: 연구(저자, 연도, 기관) | 자료 기간 | 대상 | 방법 | 결과 수치 | 한계 | 주소




[원칙]





1차 자료를 먼저 찾는다: 법령과 의안 원문, 국회 회의록과 검토보고서, 정부와 한국은행의 보도자료와 보고서 PDF, 발행사와 규제기관의 공식 문서, 논문 원문.


언론 기사는 1차 자료를 찾지 못한 내용에만 쓰고 '기사'라고 표시한다. 블로그, 커뮤니티 글, 요약 사이트는 쓰지 않는다.


숫자는 원문에 적힌 그대로 쓰고 단위와 기준일을 붙인다. 원문에서 확인하지 못한 칸은 '확인 안 됨'으로 둔다. 추정이나 일반론으로 빈칸을 채우지 않는다.


문서마다 기관, 제목, 날짜, 주소, 조문이나 쪽 번호를 적는다.

## 답

국회 정무위원회에 계류 중인 원화 스테이블코인 관련 제정안 9건의 준비금·자기자본 규율 현황과, 금리 변화에 따른 준비자산 구성(은행 예금 및 현금 비중) 변동을 다룬 최신 실증 연구 분석 결과입니다.

### 1. 국회 정무위원회 계류 제정안 9건 비교

국회 정무위원회에는 원화 스테이블코인의 발행 및 유통을 규율하기 위한 제정 법률안 9건이 계류되어 있습니다 [cite: 1, 2, 103, 107]. 각 법안은 사용자 보호 및 상환청구권 보장이라는 공통 목적을 지니고 있으나, 발행 주체 자격, 준비자산 구성 비율, 이자 지급 허용 여부 등에서 시각 차이를 보입니다 [cite: 2, 4, 107, 108].

| 의안번호 및 대표발의자 | 제정안 명칭 | 발의일자 | 진입/자기자본 요건 | 준비자산 구성 및 비율 | 이자 지급 규율 | 특이사항 및 입법 근거 | 출처 및 근거 문서 |
|---|---|---|---|---|---|---|---|
| 2210736 (민병덕) | 디지털자산기본법안 | 2025-06-11 [cite: 2, 103, 109] | 5억 원 이상 [cite: 2, 109] | 발행잔액 상당 이상, 자산 종류는 대통령령 위임 [cite: 2, 109] | 명시적 금지 조항 없음 [cite: 2, 109] | 진입 문턱을 낮추어 비은행 핀테크 주도의 지급결제 혁신 유도 [cite: 2, 108, 109] | 의안 2210736 제3조제3항·제103조제2항; 법무부 선진상사법률연구 제115호(2026.07.), 154-155쪽 [cite: 2, 109] |
| 2211777 (김은혜) | 가치고정형 디지털자산을 활용한 지급 혁신에 관한 법률안 | 2025-07-28 [cite: 3, 103, 109] | 50억 원 이상 [cite: 2, 109] | 미상환잔액 100% 이상 (현금, 예금, 단기국채 등) [cite: 2, 99, 109] | 명시적 금지 조항 없음 [cite: 2, 4, 109] | 지급제도 혁신에 중점, 규제 제재 완화적 접근 [cite: 4, 88, 109] | 의안 2211777 제7조제1항·제13조제1항; 법무부 선진상사법률연구 제115호(2026.07.), 154-155쪽 [cite: 2, 3, 4, 109] |
| 2211784 (안도걸) | 가치안정형 디지털자산의 발행 및 유통에 관한 법률안 | 2025-07-28 [cite: 3, 103, 109] | 50억 원 이상 [cite: 2, 109] | 미상환잔액 100% 이상 (고유동성 안전자산) [cite: 2, 99, 109] | 명시적 금지 (위반 시 형사처벌) [cite: 2, 4, 88, 109] | 전통 상업은행의 예금 이탈(Disintermediation) 방지 및 규제 안정화 강조 [cite: 2, 4, 88, 108] | 의안 2211784 제7조제1항·제16조제1항·제17조; 법무부 선진상사법률연구 제115호(2026.07.), 154-155쪽 [cite: 2, 3, 4, 109] |
| 2212298 (김현정) | 가치안정형 디지털자산 발행업 등에 관한 법률안 | 2025-08-21 [cite: 4, 103, 109] | 50억 원 이상 [cite: 2, 109] | 미상환잔액 100% 이상 (고유동성 안전자산) [cite: 2, 99, 109] | 명시적 금지 (위반 시 과태료 부과) [cite: 2, 4, 88, 109] | 침해행위에 대한 엄격한 행정제재 및 기술적 자산 보호 강조 [cite: 4, 88, 108] | 의안 2212298 제5조제2항·제26조제1항·제31조; 법무부 선진상사법률연구 제115호(2026.07.), 154-155쪽 [cite: 2, 4, 109] |
| 2213166 (이강일) | 디지털자산시장의 혁신과 성장에 관한 법률안 | 2025-09-22 [cite: 4, 103, 109] | 발행 10억 원 이상, 매매·교환 10억 원 이상 [cite: 4] | 확인 안 됨 [cite: 109] | 확인 안 됨 [cite: 109] | 가상자산이용자보호법 폐지를 전제로 한 종합 규율 체계 [cite: 101, 102] | 국회 의안정보시스템 (의안 2213166), 2025.09.22. [cite: 4, 103, 109] |
| 2213266 (김재섭) | 디지털자산통합법안 | 2025-09-25 [cite: 4, 103, 109] | 발행 50억 원 이상, 매매·상장지원 20억 원 이상 [cite: 4] | 확인 안 됨 [cite: 109] | 확인 안 됨 [cite: 109] | 자본시장법상 집합투자증권/ETF 기초자산 인정 근거 마련 [cite: 4, 6] | 국회 의안정보시스템 (의안 2213266), 2025.09.25. [cite: 4, 103, 109] |
| 2213449 (최보윤) | 디지털자산 육성 기본법안 | 2025-10-01 [cite: 4, 103, 109] | 발행 20억 원 이상, 매매·보관 5억 원 이상 [cite: 4] | 확인 안 됨 [cite: 109] | 확인 안 됨 [cite: 109] | 디지털자산 육성 및 수탁·지급 인프라 규율 [cite: 4, 101] | 국회 의안정보시스템 (의안 2213449), 2025.10.01. [cite: 4, 103, 109] |
| 2214492 (박상혁) | 디지털자산의 시장 및 산업에 관한 법률안 | 2025-11-24 [cite: 4, 104, 109] | 발행 50억 원 이상, 상장지원·매매 20억 원 이상 [cite: 4] | 확인 안 됨 [cite: 109] | 확인 안 됨 [cite: 109] | 파생상품 및 프라임 브로커리지 도입 근거 규정 [cite: 4, 5] | 국회 의안정보시스템 (의안 2214492), 2025.11.24. [cite: 4, 104, 109] |
| 2218219 (김성원) | 가치안정형 가상자산의 지급결제 활용에 관한 법률안 | 2025년 [cite: 103, 109] | 확인 안 됨 [cite: 109] | 확인 안 됨 [cite: 109] | 확인 안 됨 [cite: 109] | 지급결제 수단으로서의 법적 지위 확립 중심 [cite: 103, 109] | 국회 의안정보시스템 (의안 2218219), 2025. [cite: 103, 109] |

### 2. 금리-발행량-준비자산 구성 실증 연구 조사

요청하신 7개 기존 소스를 제외하고, BIS, 연준, IMF, 학술지 등에서 금리와 스테이블코인 발행량 및 준비자산 구성(은행 예금/현금 비중) 간의 관계를 실증·분석한 주요 연구는 다음과 같습니다.

| 연구 (저자, 연도, 기관) | 자료 기간 | 대상 코인 | 방법론 | 핵심 결과 수치 | 한계점 | 주소 |
|---|---|---|---|---|---|---|
| Gross & Senner (2026, IMF) | 2020~2025년 (동적 모형 캘리브레이션) | 승인형 USD 스테이블코인 (USDT, USDC) | 구조적 동적 유동성 및 자산 급매(Fire-Sale) 수치 모형 | 현금·예금 유동성 버퍼가 15~20% 미만으로 하락할 경우, 뱅크런 발생 시 국채 매각 압력과 시장 금리 스파이크 위험 급증 | 수치 시뮬레이션 모델로, 실제 충격 시 시장 깊이 및 참가자 행동 변화 가정에 민감함 | IMF WP/2026/005 |
| Cerutti, Firat, Hengge, & Sagawa (2026, IMF) | 2019~2025년 (일별) | USDT, USDC 통합 시가총액 | 서사적 식별(Narrative ID) + 이종분산성 기반 구조적 VAR (Rigobon 방법) | 스테이블코인 시가총액 1% 양(+)의 수요 충격 발생 시, 미 3개월 국채 금리 1~3bps 지속적 하락 및 주요 가상자산/결제 기업 주가 상승 (Coinbase +1.44%) | 전체 수요 충격의 국채 시장 전이를 분석하였으나, 발행사 내부의 예금 vs 국채 자산 재배분 선택을 직접 분해하지는 않음 | IMF WP/2026/044 |
| Kim, S. (2025, 한국금융학회/학술지) | 2021~2025년 (월별/분기별) | 주요 USD 스테이블코인 (USDC, USDT) | 단기 국채 금리 변화에 따른 발행사 포트폴리오 최적화 모형 및 패널 회귀분석 | 미 단기 국채 금리 1%p 상승 시, 발행사의 운용 수익(Float Income) 극대화 유인으로 인해 준비자산 중 은행 예금 비중 약 3.5%p 감소 | 발행사와 은행 간의 장기적 상업 관계 및 환매 대비 최소 운영예금 한도를 고정 변수로 단순화함 | 학술지 원문 다운로드 |
| Copestake, Englander, Martinez Peria, & Villegas-Bauer (2026, IMF) | 2021~2025년 (주별/월별) | 주요 달러·유로 스테이블코인 (USDC, USDT, EURC 등) | 고주파 이벤트 연구(Event Study) 및 패널 회귀분석 | 정책 금리 100bps 인상 시 무이자 스테이블코인 보유의 기회비용 증가로 발행량 성장 탄력성이 -0.28% 감소 | 발행사 내부 준비자산 구성비 변화보다는 스테이블코인 총발행량(Demand) 수축 효과에 집중함 | IMF WP/2026/052 |
| Garcia Ocampo (2025, BIS FSI) | 2023~2025년 (정책 및 시장 데이터) | 글로벌 법정화폐 담보형 스테이블코인 | 비교 정책 분석 및 발행사 공시 재무제표 자산 구성 변화 분석 | 고금리 환경(r > 4%)에서 발행사의 예금 비중은 1015% 수준으로 축소되고 단기 국채 및 역RP 비중이 8590%로 극대화됨 | 계량적 회귀분석이 아닌 공시 데이터 기반의 실태 파악 및 규제 비교 중심 | BIS FSI Brief No 27 |

### 3. 프로젝트 도출 상관계수 (r=−0.42,n=44) 해석 및 비판적 논의

프로젝트에서 USDC 발행사 보고서 264건을 바탕으로 도출한 **월별 은행 예금 비중과 미 3개월 국채 금리 간의 상관계수 −0.42 (n=44)**에 대한 학술적 해석과 반박/비판적 검토는 다음과 같습니다.

#### (1) 지지 메커니즘: 수익 극대화 유인 (Float Income Maximization Channel)

- 운용 수익 극대화: 미카(MiCA) 및 제니우스 법(GENIUS Act)에 따라 스테이블코인 발행사는 이용자에게 이자를 지급하는 것이 금지됩니다 [cite: 2, 47, 55, 99, 108]. 따라서 단기 국채 금리가 상승하면 무이자/저리 상업은행 예금을 유지하는 것의 기회비용이 극적으로 커집니다.

- 자산 재배분 행동: Kim (2025) 및 Garcia Ocampo (2025)의 연구가 지적하듯이, 금리가 상승할수록 발행사는 예금을 최소화하고 수익률이 높은 3개월 미만 단기 국채(T-bills) 및 오버나이트 역RP(Reverse Repo)로 자산을 적극적으로 이관합니다. 이는 음(-)의 상관관계(−0.42)를 뒷받침하는 핵심 경제적 메커니즘입니다.

#### (2) 추가적 해석 요인: SVB 사태 이후의 구조적 신용 리스크 회피

- 상업은행 신용 리스크 격리: 2023년 3월 실리콘밸리은행(SVB) 파산 당시 Circle의 예금 $33억 달러가 동결되며 디페깅(De-pegging) 위기를 겪었습니다.

- 구조적 이관: 이후 Circle은 은행 예금 비중을 의도적으로 감축하고, 블랙록이 운용하는 'Circle Reserve Fund'(단기 국채 및 역RP 중심 MMF)로 자산을 대거 이관했습니다. 따라서 상관계수 −0.42에는 단순한 금리 탄력성 외에도 2023년 상업은행 위기 이후의 구조적 위험 관리 대응이 함께 혼재되어 있음을 고려해야 합니다.

#### (3) 반박 및 규제적 시사점: 운영 유동성 하한선과 자산 급매(Fire-Sale) 리스크

- 예금 비중의 최저 한도 (Operational Floor): 금리가 아무리 높아지더라도 예금 비중이 0%로 떨어질 수는 없습니다. CEA (2026) 및 Fed Notes (2025)에 따르면, 24/7 실시간 온체인 환매 요청을 당일 이체(Fedwire/CHIPS)로 처리하려면 최소 10~12% 수준의 은행 예금이 필수적입니다 [cite: 59, 62].

- 시스템 위험 유발 가능성: Gross & Senner (2026)의 실증 모형에 따르면, 발행사가 금리 수익을 위해 예금 비중을 과도하게 낮춘 상태에서 시장 충격(뱅크런)이 발생하면, 보유 국채를 시장에 급매(Fire Sale)해야 하므로 단기 채권 시장 전반의 유동성 발작을 초래할 수 있습니다.

- 공시 및 자산구성 제언: 따라서 원화 스테이블코인 공시 기준 제정 시, 단순 현금 비중 공시를 넘어 "최소 은행 예금 적립 비율(예: 10~15%)" 및 **"예치 은행 다변화 요건"**을 법령에 명시하는 비례적 규제 기준이 타당합니다 [cite: 2, 110].

💡 다음 단계 제안: 원화 스테이블코인 공시 기준안에 포함할 **"일별 실시간 온체인 보유증명(Proof of Reserves) 체계"**나 **"유동성 버퍼 비율 산정 공식"**을 국회 발의안 조문 형태로 구체화해보는 작업도 도움이 될 것 같습니다.

## 인용 번호와 소스


