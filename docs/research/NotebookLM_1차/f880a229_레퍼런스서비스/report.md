# Deep Research 보고서 원문

- 노트북: "AI 에이전트 결제와 블록체인 인프라" https://notebook.google.com/notebook/f880a229-bb7e-4530-a517-c5e8f53315e8?authuser=1
- 보고서 제목: 글로벌 디지털 자산 규제 조문에 따른 스테이블코인 준비금 검증(Attestation) 도구·상용 서비스 및 한국 원화(KRW) 스테이블코인 기준 분석 보고서
- 수집일: 2026-10-04
- 수집 방법: Aside 브라우저, 소스 화면 document.body.innerText 원문(가공 없음), 참고 문헌 주소는 링크 href
- 주의: 수식(KaTeX) 부분은 innerText에 글자가 비어 나와 원문에서 빠져 있음(예: "준비금 충당 비율() 및"). 확인 불가.

## 소스 가이드(노트북이 자동 생성한 요약과 주제 칩)


본 보고서는 디지털 자산 규제 조문에 발맞추어, 전통적인 사후 검증 방식의 한계를 극복하는 프로그래머블 온체인 준비금 검증 인프라의 필요성과 주요 기술들을 다루고 있습니다. 미국, EU, 홍콩 등 글로벌 주요국의 입법 동향을 분석하는 동시에, Tessera, FeedOracle, Veris 같은 실시간 오라클 및 AI 에이전트 연동 검증 서비스들의 작동 원리와 표준을 상세히 소개합니다. 나아가 이러한 글로벌 기준을 바탕으로 한국 원화(KRW) 스테이블코인이 지녀야 할 적격 준비금 산정 기준 및 이중 트랙 거버넌스 체계를 체계적으로 제안하고 있습니다.

글로벌 스테이블코인 규제

실시간 준비금 검증

오라클 및 상용 서비스

원화 스테이블코인 기준

온체인 정산 인프라


## 보고서 본문

글로벌 디지털 자산 규제 조문에 따른 스테이블코인 준비금 검증(Attestation) 도구·상용 서비스 및 한국 원화(KRW) 스테이블코인 기준 분석 보고서
서론 및 주요국 규제 프레임워크 비교 분석
스테이블코인 시장이 전통 금융 시스템 및 분산형 금융 생태계의 핵심 정산 수단으로 급부상함에 따라, 글로벌 주요국 금융 당국은 준비금의 미달이나 불투명한 자산 운용에 따른 시스템적 리스크를 방지하기 위해 엄격한 법적·제도적 프레임워크를 수립하고 있다 [cite: 1, 2]. 과거 스테이블코인 발행사들이 전통 회계법인을 통해 사후적으로 발행하던 정적(Static) PDF 형태의 월별 또는 분기별 검증보고서(Attestation Report)는 실시간 자산 변동성 대응 및 실시간 온체인 정산 시스템과의 상호운용성 측면에서 한계를 노출하였다 [cite: 3, 4]. 이에 따라 실시간 자산 검증, 인공지능(AI) 에이전트 및 머신 러닝 연동, 암호학적 증명(Zero-Knowledge Proof 및 타임스탬프 기반 ECDSA/양자 저항 서명)을 결합한 프로그래머블 온체인 준비금 검증 인프라의 도입이 가속화되고 있다 [cite: 5, 6, 7].
미국의 GENIUS법(Guiding and Establishing National Innovation for U.S. Stablecoins Act), 유럽연합의 MiCA(Markets in Crypto-Assets), 홍콩의 스테이블코인 조례(Stablecoins Ordinance), 싱가포르 MAS 가이드라인, 그리고 대한민국에서 추진 중인 가상자산 2단계 입법안 등 주요 규제 체계는 스테이블코인 발행사에 대해 명확한 준비금 자격 요건과 지속적인 제3자 검증을 법적 의무로 규정하고 있다 [cite: 1, 2, 8].
규제 구획
	
관련 법안 및 핵심 조문
	
준비금 인정 자산 요건
	
검증 보고서 및 감사 요구사항
	
주요 금지 및 제약 사항


미국 (US)
	
GENIUS Act (2025년 7월 제정, FDIC Proposed Part 350) [cite: 1, 9]
	
미국 통화·주화, FDIC 부고예금, 만기 93일 이하 미 재무부 단기채(T-Bills), 만기 7일 이하 환매조건부채권(Repo), 정부 MMF [cite: 1, 10]
	
PCAOB 등록 독립 회계법인의 월별 검증보고서 제출, CEO/CFO 정합성 서명 인증, $500억 이상 발행 시 연차 감사보고서 [cite: 1, 3, 11]
	
상업어음(CP) 인정 불가, 알고리즘 민팅 금지, 직접 이자/수익 지급 금지, 준비금 재유용 금지 [cite: 9, 10]


유럽연합 (EU)
	
MiCA (Article 25, 35, 36) [cite: 12, 13]
	
최소 100% 이상의 격리된 고액 유동성 자산(자국 통화 예치금, 고성능 국채 등), 질적 리스크 평가 충족 자산 [cite: 13]
	
독립된 제3자 기관에 의한 지속적 준비금 품질 검증(ReserveOracle 등 체계) 및 당국 보고서 제출 [cite: 13]
	
자산의 완전 분리 보관 의무화, 승인되지 않은 자산군으로의 준비금 재hypothecation 엄격 제한 [cite: 9, 10]


홍콩 (HK)
	
Stablecoins Ordinance (2025년 8월 시행) [cite: 2]
	
유통량 대비 최소 100% 이상의 격리된 자격 갖춘 준비자산(Qualified Reserves) 보유 [cite: 2]
	
HKMA 라이선스 요건에 따른 주기적 준비금 증명 및 독립 외부 감사 [cite: 2]
	
과소담보화(Undercollateralization) 엄격 금지, 발행사 자산과의 혼장 보관 금지 [cite: 2]


싱가포르 (SG)
	
MAS Stablecoin Regulatory Framework
	
현금, 국채 등 극소 위험 자산, 매일 시가평가(Mark-to-Market) 적용 자산
	
독립적 외부 감사인에 의한 월별 검증 보고서 공시 및 당국 제출
	
최소 기준 자본금 유치 의무, 법정화폐 환급 청구권 보장 (Par value redemption)


한국 (KR)
	
가상자산 2단계 입법 및 원화 스테이블코인 정책 제안 [cite: 8, 14]
	
100% 이상의 원화 현금, 시중은행 요구불예금, 만기 90일 이하 국고채 및 통화안정증권(MSB) [cite: 8]
	
공인회계사(CPA) 및 외부 전문기관의 월별 준비금 검증보고서 공시, 실시간 온체인 오라클 연동 권고 [cite: 8, 14]
	
알고리즘 및 암호자산 담보 금지, 준비금 재유용 금지, 발행사의 직접 이자 지급 금지 [cite: 8, 10]
글로벌 규제 조문들은 준비금의 100% 이상 초과 담보 유지, 파산 격리(Bankruptcy Remote) 구조 확보, 그리고 자율 구동형 모니터링 체계 구축을 공통적으로 지향한다 [cite: 1, 2, 10]. 이러한 법적 요구사항을 기계 판독 가능한(Machine-readable) 규제 준수 로직으로 전환하여 온체인 정산 환경에 공급하는 기술적 서비스가 필수 인프라로 안착하고 있다 [cite: 13, 15].
--------------------------------------------------------------------------------
주요 공개 도구 및 상용 서비스 상세 분석
Tessera 및 ProofLayer (tessera.financial / ProofLayer)
Tessera 및 ProofLayer 생태계는 Layer 1 블록체인인 Casper Network의 무결성 증명 인프라를 기반으로 작동하는 모듈형 검증 솔루션이다 [cite: 6]. 초기에는 실물 연계 자산(RWA)의 현금흐름 증명에 주력하였으나, 최근에는 csprUSD 등 규제 준수형 스테이블코인의 담보증명 및 AI 에이전트 정산 규격(x402 프로토콜)의 검증 레이어로 범위를 확장하였다 [cite: 16, 17, 18].
기술적 구현 관점에서 ProofLayer는 신뢰 실행 환경(TEE, Trusted Execution Environment) 내에서 금융기관 API, 수탁 은행 데이터베이스, 수입 피드를 암호학적으로 서명한다 [cite: 6]. 이후 생성된 영지식 증명(ZKP) 및 Cryptographic Receipts를 Casper 네트워크의 결정론적 블록체인에 타임스탬프와 함께 앵커링(Anchoring)함으로써 오프체인 달러 담보의 실제 존재 여부와 발행 및 상환 이력을 검증 가능하게 만든다 [cite: 6, 16].
개발자 및 시스템 연동을 위해 제공되는 @agentutility/mcp-prooflayer 패키지는 에이전트 기반 인프라에 인라인(Inline) 검증 기능을 탑재한다 [cite: 18]. Base 네트워크상의 USDC를 이용한 호출당 결제(x402 Pay-per-call) 방식을 채택하여 고정 구독료나 API 키 발급 없이도 자산 안전성, 프롬프트 주입 방지, 가용 준비금 수치를 검증할 수 있다 [cite: 18]. 또한 ERC-8263 온체인 증명 레이어 규격 및 ISO 42001, SOC 2 표준을 충족하여 regulatory audit 시 암호화된 타임스탬프 증적을 제출할 수 있는 환경을 지원한다 [cite: 19, 20].
FeedOracle (feedoracle.io / feedoracle-mcp)
FeedOracle은 AI 에이전트 및 기관용 금융 시스템을 위해 설계된 규제 준수 MCP(Model Context Protocol) 서버이자 탈중앙화 오라클 메시(OracleNet) 인프라이다 [cite: 13]. 스테이블코인의 미할당 발행, 페깅 변동성, 준비금 표류(Reserve Drift)를 실시간 감지하여 검증된 서명 객체(Signed Evidence Object) 형태로 반환한다 [cite: 12, 13].
FeedOracle은 공유 오라클 네트워크 전반에 걸친 549개 도구 중 6개의 전용 브랜드 서버(총 149개 도구)를 통해 구체적인 규제 검증 기능을 제공한다 [cite: 13].
ReserveOracle (11개 도구): EU MiCA Article 36 규정을 직접 조준하여 준비금 자산의 품질 평가, 시점별 담보 비율 검증, 외부 회계 검증 보고서와의 오차 분석을 자동 수행한다 [cite: 13].
MiCAOracle (24개 도구): EU 내 스테이블코인 인가 상태, 디페깅 위험도, 준비금의 계좌 격리 상태를 모니터링한다 [cite: 13].
RiskOracle (7개 도구): RLUSD, USDT, USDC, EURC 등 주요 스테이블코인 및 RWA 자산의 운영 리스크 스코어링을 수행하고, SAFE, CAUTION, AVOID 등 3단계 정산 판정을 산출한다 [cite: 12, 13].
FeedOracle Compliance (29개 도구): 사전 검증(Preflight) 준수 여부 점검, 감사 증적 패키지 생성 및 AMLR/DORA 법안 규격과의 상호 대조를 실행한다 [cite: 13].
AmpelOracle (50개 도구) 및 PredictionGuard (28개 도구): DORA 운영 리스크 점검 및 컴플라이언스 AI 에이전트의 환각 방지 정책을 집행한다 [cite: 13].
FeedOracle이 반환하는 데이터는 ECDSA, ES256K 및 양자 저항 암호화 규격인 ML-DSA-65로 서명되며, NIST 및 CURBy 무작위성 비콘과 동기화된다 [cite: 5, 13]. 사용자는 https://feedoracle.io/.well-known/jwks.json 경로를 통해 수신된 데이터의 위변조 여부를 독립적으로 검증할 수 있으며, 결제 시스템은 Stripe 및 Base 네트워크 USDC 기반 x402 프로토콜을 모두 지원한다 [cite: 13].
Veris (docs.useveris.finance / Veris MCP)
Veris는 가상자산 및 스마트 계약 시스템의 행동 검증(Behavioral Verification) 인프라로, 자산 운영 로직이 법적 규제 조건에서 이탈하는 현상(System Drift)을 원천 차단하는 도구이다 [cite: 21, 22].
Veris는 17개의 MCP 도구를 기반으로 자산의 입출금 및 온체인 준비금 락업(Lock-up) 로직에 대한 실행 그래프를 작성하고, 의미론적 워크플로우 클러스터링(Semantic Workflow Grouping)을 수행한다 [cite: 21, 22]. 스테이블코인 발행 시스템에 적용될 경우, Veris는 스마트 계약 내 발행(Mint) 함수가 호출될 때 준비금 오라클의 조건 판정을 거치지 않고 직접 실행되는 무단 민팅 백도어나 로직 오류를 실시간 탐지한다 [cite: 21, 23]. 규제 프레임워크상 요구되는 서킷 브레이커(Circuit Breakers) 조항이 코드 수준에서 일관되게 유지되는지를 역으로 추적하는 검증 성능을 발휘한다 [cite: 21, 23].
검증 플랫폼
	
핵심 기술 및 검증 메커니즘
	
목표 규제 및 준수 표준
	
지원 토큰 및 자산 범위
	
인터페이스 및 결제 구조


ProofLayer (Tessera) [cite: 6, 18]
	
TEE 기반 데이터 서명, Casper L1 타임스탬프 앵커링, ZKP 증명 [cite: 6]
	
US GENIUS Act, ISO 42001, SOC 2, ERC-8263 [cite: 19, 20]
	
USD 예금, RWA 현금흐름, csprUSD [cite: 6, 16]
	
x402 Protocol (USDC on Base), REST API, MCP [cite: 18]


FeedOracle [cite: 13]
	
암호화 서명 객체(ES256K, ML-DSA-65), OracleNet 메시 검증 [cite: 5, 13]
	
EU MiCA (Art. 36), DORA, AMLR [cite: 13]
	
RLUSD, USDT, USDC, EURC 등 105+ 토큰 [cite: 5, 12]
	
MCP (HTTP/JSON-RPC), x402, Stripe [cite: 13]


Veris [cite: 21, 22]
	
코드 행동 그래프 분석, 실행 워크플로우 이탈 감지 [cite: 21, 22]
	
스마트 계약 안전 표준, 규제적 드리프트 모니터링
	
온체인 민팅 계약, 오라클 연결 실행 로직 [cite: 21, 23]
	
MCP, JS/TS 개발 프레임워크 연동 [cite: 21, 22]
--------------------------------------------------------------------------------
신규 및 확장 검증 서비스 생태계 동향
스테이블코인 규제 체계의 법제화와 발맞추어 준비금의 오프체인 잔액과 온체인 유통량 간 괴리를 막기 위한 검증 서비스 인프라가 급격히 확장되고 있다 [cite: 12, 24].
Chainlink Proof of Reserve (PoR) 및 NAVLink 체계는 온체인 토큰 발행과 오프체인 수탁 기관의 잔액을 실시간 직접 결합하는 대표적 오라클 솔루션이다 [cite: 23, 24, 25]. BNY Mellon, Crypto Finance 등 제1금융권 수탁 기관의 잔액 데이터를 탈중앙화 노드가 직접 수집하여 스마트 계약의 latestRoundData() 피드로 공급한다 [cite: 23, 26]. 이 과정에서 준비금 자산 비율이 유통량 대비 100% 미만으로 감소할 경우 신규 토큰 민팅을 물리적으로 즉시 차단하는 원자적(Atomic) 서킷 브레이커 기능을 제공하며, ISO 27001 및 SOC 2 Type 1 인증을 확보하여 기관급 준수 요건을 이행한다 [cite: 23, 25].
아울러 Achivx의 StableScan (com.achivx/stablescan) 및 OceanAlt AML 서비스는 7개 이상의 주요 블록체인 네트워크에 유통되는 스테이블코인의 준비금 편차(Reserve Drift), 디페깅 확률, 동결(Freeze) 상태 및 OFAC 제재 계좌 노출도를 모니터링한다 [cite: 12]. 이는 에이전트 간 정산 이전에 준수 여부를 사전 평가하여 안전성 신호를 전송하는 정밀한 사전 검증 인프라로 작동한다 [cite: 12].
자동화된 온체인 준비금 검증 및 정산 제어 파이프라인은 4단계의 고도화된 레이어로 수직 통합되어 구동된다.
수탁 자산 데이터 레이어: 제1금융권 은행, 중앙은행 예치금, 국채 및 통안채 수탁 계좌에서 생성되는 오프체인 실시간 잔액 데이터를 추출한다 [cite: 1, 23, 24].
실시간 검증 엔진 레이어: Chainlink PoR 노드, FeedOracle(ReserveOracle), ProofLayer TEE 시스템이 오프체인 데이터를 암호화 서명 객체(ECDSA/ML-DSA-65)로 변환하고 타임스탬프를 부여한다 [cite: 5, 6, 13, 23].
컴플라이언스 평가 레이어: Achivx StableScan, Veris, FeedOracle Risk MCP가 준비금 비율(R
ratio
	​

≥100%) 준수 여부, 미인가 민팅 백도어 존재 여부, 디페깅 및 제재 위험도를 종합 평가한다 [cite: 12, 13, 21].
온체인 정산 및 집행 레이어: 스마트 계약 내 원자적 민팅 제어기(Atomic Mint Controller)가 가용 준비금을 초과하는 민팅 요청을 자동 거부하고, 실시간 검증 데이터를 규제 당국 및 감사인 전용 온체인 대시보드로 실시간 전달한다 [cite: 7, 11, 23].
--------------------------------------------------------------------------------
한국 원화(KRW) 스테이블코인 준비금 가이드라인 및 기준값 제안
한국은행, 금융위원회, 금융감독원, 한국금융연구원(KIF), 자본시장연구원 및 DAXA의 연구 보고서와 글로벌 규제 법안을 종합할 때, 원화(KRW) 연동 스테이블코인의 신뢰성 확보와 금융 시스템으로의 리스크 전이 방지를 위한 준비금 산정 기준 체계가 정립된다 [cite: 8, 14].
적격 준비금 자산 구성 및 인정 자격 요건
원화 스테이블코인 발행사는 온체인에 유통되는 토큰 총 유통량 대비 최소 100% 이상의 적격 고유동성 자산(HQLA)을 보유해야 하며, 자산군은 다음 항목으로 엄격히 제한된다 [cite: 8].
원화 현금 및 한국은행 예치금: 한국은행의 당좌 예금 계좌 및 예금자 보호법 또는 별도 신탁 계약을 통해 파산 격리(Bankruptcy Remoteness)가 완료된 시중 은행(제1금융권)의 요구불 예금 [cite: 8, 10].
초단기 국공채: 잔존 만기 90일 이하의 대한민국 정부 발행 국고채권(KTB) 및 한국은행 발행 통화안정증권(MSB) [cite: 8].
환매조건부채권(Repo) 매수금: 국고채를 담보로 하며, 잔존 만기 7일 이하의 초단기 매수 RP [cite: 1, 10].
엄격 금지 자산 (Unqualified Assets): 상업어음(CP), 회사채, 부동산 담보대출 채권, 비트코인·에더 등 가상자산 담보, 알고리즘 기반 자동 가치 조절 메커니즘, 주식 및 영구채 [cite: 8, 10, 27].
원화 스테이블코인 준비금 충당 비율의 수학적 정의
준비금 자산의 적격성은 시가평가(Mark-to-Market) 기준으로 매일 산출되어야 하며, 유통되는 토큰의 총액을 완벽히 상회해야 한다 [cite: 2, 3]. 준비금 충당 비율(R
ratio
	​

) 및 자산 산출 구조는 다음과 같은 mathematical formulation으로 정의된다.
R
ratio
	​

=
S
circulating
	​

V
cash
	​

+V
dep
	​

+∑MTM(KTB
≤90d
	​

)+∑MTM(MSB
≤90d
	​

)+V
repo
	​

	​

×100%
여기서 V
cash
	​

는 원화 현금 및 한국은행 예치금, V
dep
	​

는 제1금융권 요구불예금, MTM(KTB
≤90d
	​

) 및 MTM(MSB
≤90d
	​

)는 잔존만기 90일 이하 국고채 및 통통채의 실시간 시가평가액, V
repo
	​

는 7일 이하 국채 RP 매수금액을 의미하며, S
circulating
	​

은 온체인상 발행된 원화 스테이블코인의 총 유통량이다. 규제 기준상 상시 준수 요건은 R
ratio
	​

≥100%로 고정된다.
자산 항목
	
최고 인정 만기
	
시가평가(MTM) 주기
	
법적 분리 보관 의무
	
비고 및 제약 사항


원화 현금 및 BOK 예치금
	
즉시 현금화
	
실시간 (1:1 고정)
	
신탁 계좌 필수 분리 [cite: 8, 10]
	
한국은행 소급 결제 인프라 연동 권고


시중은행 요구불예금
	
즉시 현금화
	
일간 (Daily)
	
파산격리 신탁 계약 [cite: 8, 10]
	
제1금융권 한정, 특정 은행 집중도 제한


국고채권 (KTB)
	
만기 90일 이하 [cite: 8]
	
매일 시가평가
	
외부 수탁기관 보관 [cite: 9]
	
평가 손실 발생 시 즉시 현금 충당 의무


통화안정증권 (MSB)
	
만기 90일 이하 [cite: 8]
	
매일 시가평가
	
외부 수탁기관 보관 [cite: 9]
	
한국은행 발행 채권에 한정 [cite: 8]


국채 담보 RP 매수
	
만기 7일 이하 [cite: 1, 10]
	
일간 (Daily)
	
외부 수탁기관 보관 [cite: 9]
	
재담보 제공(Rehypothecation) 엄격 금지 [cite: 9, 10]
검증 및 거버넌스 준수 체계
원화 스테이블코인 발행사는 온체인 실시간 검증과 오프체인 회계 검증이 결합된 이중 트랙(Dual-Track) 거버넌스를 구축해야 한다 [cite: 1, 3, 23].
온체인 검증 영역에서는 Chainlink PoR 또는 FeedOracle ReserveOracle 인프라를 연결하여 은행 수탁 잔액 데이터 피드를 스마트 계약으로 실시간 수신받아야 한다 [cite: 13, 23]. 준비금 비율이 100% 미만으로 하락할 경우 추가 민팅을 자동 정지하는 서킷 브레이커 로직을 필수적으로 탑재해야 한다 [cite: 23].
오프체인 검증 영역에서는 공인회계사법에 따라 인가된 회계법인으로부터 월 1회 이상의 준비금 검증보고서(Attestation Report)를 발급받아 금융당국 제출 및 공시를 이행해야 한다 [cite: 1, 3, 11]. 발행사의 대표이사(CEO) 및 최고재무책임자(CFO)는 공시 보고서의 정확성에 관해 정합성 인증 서명을 완료해야 하며, 발행사의 파산 시 스테이블코인 보유자가 준비금 자산에 대해 최우선 변제권(Super-priority Claim)을 가짐을 법적으로 명시해야 한다 [cite: 1, 3, 11].
--------------------------------------------------------------------------------
결론 및 정책적·기술적 제언
글로벌 스테이블코인 준비금 검증 체계는 정적인 문서 형태에서 벗어나, 암호화 서명, AI 에이전트 인터페이스, 온체인 오라클이 결합된 프로그래머블 실시간 검증 인프라로 진화하고 있다 [cite: 4, 5, 7, 13]. 미국의 GENIUS법 및 EU MiCA 등 글로벌 규제 가이드라인은 준비금의 완전 분리 보관, 고유동성 자산 제한, 그리고 엄격한 제3자 검증을 제도화하고 있다 [cite: 1, 3, 10, 13].
국내 원화 스테이블코인 생태계 수립 시에도 전통 회계법인의 월별 서면 검증에만 의존하는 방식에서 벗어나, FeedOracle, ProofLayer, Chainlink PoR과 같은 실시간 온체인 오라클 인프라를 제도적으로 수용해야 한다 [cite: 6, 13, 23]. 원화 현금, 초단기 국고채 및 통안채 중심의 100% 이상 시가평가 준비금 충당 산출식을 법제화하고, 오라클 기반 자동 차단 장치(Circuit Breaker)를 결합함으로써 금융 시스템으로의 리스크 전이를 원천적으로 차단하는 기술적·제도적 거버넌스를 구축해야 한다 [cite: 8, 23].
--------------------------------------------------------------------------------

## 참고 문헌

1. What Is the GENIUS Act? Stablecoin Rules Explained - Paxos, https://www.paxos.com/blog/genius-act
2. Hong Kong Stablecoin Regulation: HKMA Licensing Framework in 2026 - Sumsub, https://sumsub.com/blog/hong-kong-stablecoin-regulation/
3. Stablecoin Reserve Attestations: Key Considerations for Compliance | Forvis Mazars US, https://www.forvismazars.us/forsights/2025/11/stablecoin-reserve-attestations-key-considerations-for-compliance
4. Real-Time Asset Verification and On-Chain Audit Services - LedgerLens, https://ledgerlens.io/resources/news-insights/real-time-asset-verification-and-on-chain-audit-services/
5. Blockchain MCP Connectors - Glama, https://glama.ai/mcp/connectors?query=Blockchain
6. ProofLayer - Casper Network, https://www.casper.network/prooflayer
7. Compliance Attestation: Onchain Verification and Standards - Chainlink, https://chain.link/article/compliance-attestation
8. 디지털자산과 금융 질서의 균형:, https://www.ydi.or.kr/board/download/1098
9. GENIUS Act Requirements and Standards for FDIC-Supervised Permitted Payment Stablecoin Issuers and Insured Depository Institutions - Federal Register, https://www.federalregister.gov/documents/2026/04/10/2026-06974/genius-act-requirements-and-standards-for-fdic-supervised-permitted-payment-stablecoin-issuers-and
10. What Is the GENIUS Act of 2025? Rules for Stablecoin Issuers | Cherry Bekaert, https://www.cbh.com/insights/articles/genius-act-new-rules-for-stablecoin-issuers/
11. What Does the GENIUS Act Require of Accountants? - The Center for Audit Quality, https://www.thecaq.org/audit-in-action-what-does-the-genius-act-require-of-accountants
12. Stablecoin Scanner - MCP Connector - Glama.ai, https://glama.ai/mcp/connectors/com.achivx/stablescan
13. feedoracle/feedoracle-mcp: Regulatory compliance MCP server for AI agents - GitHub, https://github.com/feedoracle/feedoracle-mcp
14. 스테이블코인과 보험산업 과제, https://www.kiri.or.kr/community/boardDownloadFile.do?bid=209294&seq=2
15. Casper CSPR Kucoin AMA, https://www.casper.network/news/casper-cspr-kucoin-ama
16. csprUSD Revival: Why It Matters for Casper - Sarson Funds | Cryptocurrency & Blockchain Investment Funds, https://sarsonfunds.com/csprusd-revival-why-it-matters-for-casper/
17. AI agents can browse the web. Now they need a way to pay for it. - TNW, https://thenextweb.com/news/ai-agents-browse-web-need-way-to-pay
18. @agentutility/mcp-prooflayer - npm, https://www.npmjs.com/package/@agentutility/mcp-prooflayer
19. ProofLayer: AI Red Teaming & MCP Security, https://www.proof-layer.com/
20. ERC-8263: Onchain Proof Layer for AI Agents - Ethereum Magicians, https://ethereum-magicians.org/t/erc-8263-onchain-proof-layer-for-ai-agents/28577
21. awesome-mcp-servers/README.md at main - GitHub, https://github.com/punkpeye/awesome-mcp-servers/blob/main/README.md
22. Changelog · Directories by Enterprise DNA, https://enterprisedna.co/directories/changelog/
23. Proof of Reserve | Blockchain Security Glossary - Zealynx, https://www.zealynx.io/glossary/proof-of-reserve
24. Chainlink (LINK) Price Prediction 2026-2030 - Coincub, https://coincub.com/price-prediction/chainlink-link-price-prediction-2026/
25. Chainlink Services Achieve ISO 27001 & SOC 2 Compliance, https://chain.link/blog/chainlink-achieves-iso-soc-2-certifications
26. Crypto Finance is Now Live With Chainlink Proof of Reserve To Bring Trust and Transparency to nxtAssets' Digital Asset ETPs, https://www.crypto-finance.com/crypto-finance-is-now-live-with-chainlink-proof-of-reserve-to-bring-trust-and-transparency-to-nxtassets-digital-asset-etps/
27. Stablecoins and the GENIUS Act: What Advisors Should Know | The Specialist's Desk, https://icfs.com/specialists-desk/stablecoins-genius-act
