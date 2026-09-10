오후 1:46
완료됨
8 단계
조사 결론부터 말하면, 실제로 기계 처리에 가장 적합한 원천은 BlackRock USDXX의 일별 holdings 다운로드입니다. Circle 자체 투명성 페이지의 주간 보유·발행/상환 데이터는 현재 공개 웹 화면에서 제공되지만, 문서화된 공개 API나 정형 파일 다운로드 링크는 확인되지 않았습니다. Circle의 월간 보고서는 PDF이고, Paxos PYUSD도 월간 PDF 중심이며, Tether는 분기별 PDF입니다.circle+1
1. BlackRock Circle Reserve Fund (USDXX)
실제 원본 페이지와 파일 형식
펀드/보유내역 페이지: BlackRock Circle Reserve Fund — USDXX
상품 식별: Circle Reserve Fund, Institutional Shares, ticker USDXX, CUSIP 09261A870
다운로드 기능: Holdings 섹션에 실제로 “Download Holdings”가 표시됩니다. BlackRock의 이 계열 holdings 다운로드는 일반적으로 CSV로 내려받는 구조입니다. XLSX 다운로드는 확인되지 않았습니다.
갱신 주기: Circle과 BlackRock의 설명상 포트폴리오 보고는 daily / 일별입니다. 즉, 같은 다운로드 URL 또는 다운로드 동작을 매일 호출·보관하는 방식이 실무적으로 적합합니다.circle+2
공개 표의 원문 열 이름
BlackRock USDXX 보유내역 표에서 확인되는 열 이름은 다음과 같습니다.
 | 원문 열 이름 | 의미
 | Position Description | 종목/계약 설명
 | %Par | 액면 기준 비중
 | Par | 액면금액
 | Identifier | 증권 식별자. Treasury의 경우 통상 CUSIP
 | Final Maturity | 최종 만기일
 | Maturity/Reset | 만기 또는 리셋일
 | Yield/Coupon | 수익률 또는 쿠폰
주의할 점은 USDXX의 화면 원문 표에는 Market Value라는 열이 확인되지 않는다는 점입니다. Circle의 월간 PDF에는 Fair Value ($)가 있지만, BlackRock의 USDXX holdings 공개 열은 위와 같이 Par 및 %Par 중심입니다.blackrock
최근 예시 행 3개
검색 인덱스가 BlackRock의 동적 테이블 실제 행을 노출하지 않아, 가장 최근의 Circle 원문 월간 examination report에서 확인되는 USDXX 편입 Treasury 예시 3행을 병기합니다. 이는 BlackRock 다운로드 열의 Identifier / Final Maturity / Par에 대응시키기 위한 예시이며, 아래 값의 금액 열은 Circle PDF의 Fair Value ($)입니다.
 | Identifier / Cusip | Final Maturity / Maturity Date | Fair Value ($)
 | 912797RF6 | 07/09/26 | 1,079,610,000
 | 912797SG3 | 01/20/26 | 808,835,000
 | 912797PD3 | 01/22/26 | 54,575,151
첫 행은 2026년 7월 Circle 보고서의 7월 8일 기준 자산 목록, 나머지 두 행은 2026년 1월 보고서의 1월 16일 기준 목록에서 확인됩니다. 이는 “최근 BlackRock CSV의 그대로인 3행”으로 간주하면 안 되며, 해당 날짜의 PDF 기반 검증 표본입니다. 동적 BlackRock 다운로드의 실제 최신 행은 다운로드 시점에 따라 달라집니다.6778953.fs1.hubspotusercontent-na1+1
실무적 수집 방식
USDXX 펀드 페이지에서 매일 Download Holdings를 내려받습니다.
파일 수집 시각, BlackRock의 as-of date, 원본 파일 해시를 함께 저장합니다.
Identifier, Final Maturity, Par, Yield/Coupon을 표준화합니다.
Circle 월간 PDF의 Cusip, Maturity Date, Fair Value ($)와 대조합니다.
%Par는 비중 검증용으로 사용하고, 시장가치가 필요하면 PDF의 Fair Value ($) 또는 별도 NAV/보유가치 자료와 결합합니다.
2. Circle transparency: 주간 holdings와 mint/burn
제공 방식
Circle의 Transparency & Stability 페이지는 다음을 웹 화면의 동적 표/대시보드 형태로 제공합니다.
준비금 구성:
Other Bank Deposits
Deposits at Systemically Important Institutions
Overnight Reverse Treasury Repo
<3-Month Treasuries
발행·상환:
7 Day Change
30 Day Change
365 Day Change
Issued
Redeemed
change in circulation
Circle은 USDC 준비금 보유내역을 주간 단위로, 관련 mint/burn flows와 함께 공개한다고 명시합니다. 그러나 현재 공개 페이지와 검색 가능한 소스에서는 해당 주간 데이터를 내려받는 공식 CSV/XLSX 링크는 확인되지 않았습니다.circle
API
공식·문서화된 공개 API 엔드포인트: 없음
공식 다운로드 파일 링크: 없음
화면 표: 있음
월간 PDF 다운로드: 있음 — 아래 3절 참조
즉, 이 페이지의 수치를 자동 수집하려면 브라우저가 페이지 로드 중 호출하는 내부 JSON/XHR 요청을 별도로 관찰해야 합니다. 다만 이는 Circle이 공개 문서로 안정성을 보장한 API가 아니므로, 운영 데이터 파이프라인의 공식 원천으로 단정하기 어렵습니다. 공개적으로 재현·감사 가능한 정형 보유내역 원천은 USDXX의 BlackRock holdings 다운로드가 더 적합합니다.circle+1
3. Circle 월간 examination report
URL 규칙 및 폴더 구조
2026년 Circle USDC examination report의 확인된 URL 구조는 다음과 같습니다.
text
https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/USDCAttestationReports/{YYYY}/{YYYY}%20USDC_Examination%20Report%20{Month}%2026.pdf
예를 들면 2026년 1월은 다음 형식입니다.
text
.../USDCAttestationReports/2026/2026%20USDC_Examination%20Report%20January%2026.pdf
2026년 7월은 파일명 끝에 (1)이 붙은 실제 변형이 확인됩니다. 따라서 URL을 단순 규칙으로 합성하기보다는, 각 월 파일의 실제 링크를 보관하는 편이 안전합니다.6778953.fs1.hubspotusercontent-na1+1
2026년 1월~8월 링크
 | 월 | 실제/확인 링크 | 상태
 | 1월 | 2026 USDC Examination Report January 26 | 확인
 | 2월 | 없음 | 이 조사에서 실제 파일 링크 미확인
 | 3월 | 2026 USDC Examination Report March 26 | 확인
 | 4월 | 2026 USDC Examination Report April 26 | 확인
 | 5월 | 없음 | 이 조사에서 실제 파일 링크 미확인
 | 6월 | 없음 | 이 조사에서 실제 파일 링크 미확인
 | 7월 | 2026 USDC Examination Report July 26 (1) | 확인
 | 8월 | 없음 | 2026-09-04 기준 이 조사에서 실제 파일 링크 미확인
“없음”은 해당 보고서가 존재하지 않는다는 단정이 아니라, 이번 조사에서 원문 파일 URL을 검증하지 못했다는 뜻입니다. 특히 Circle의 투명성 페이지는 월별 보고서 선택 UI를 제공하지만, 동적 렌더링 때문에 검색 색인으로 모든 실제 파일 URL이 노출되지 않았습니다.circle+4
Circle PDF의 기계 판독 가능한 표
Circle의 monthly examination PDF는 PDF지만 표 구조가 반복적이어서 추출 가능합니다. 원문상 주요 열은 다음과 같습니다.
 | 표 구역 | 원문 열 이름
 | U.S. Treasury Securities | Cusip
 | U.S. Treasury Securities | Maturity Date
 | U.S. Treasury Securities | Fair Value ($)
 | 상단 잔액 비교 | USDC in Circulation
 | 상단 잔액 비교 | Fair Value of Assets Held in USDC Reserve
추가로 PDF에는 아래 집계 행이 등장합니다.
TOTAL U.S. TREASURY SECURITIES
Cash held in Circle Reserve Fund
Cash due to/(owed by) Circle Reserve Fund due to timing and settlement differences, net
TOTAL CIRCLE RESERVE FUND ASSETS
TOTAL OTHER USDC RESERVE ASSETS
TOTAL USDC RESERVE ASSETS6778953.fs1.hubspotusercontent-na1+1
4. Circle 검증기관: Deloitte vs Grant Thornton
2026년에 바꾼 것이 아닙니다. Circle의 현재 투명성 페이지 원문은 Deloitte & Touche LLP가 Circle의 독립 감사인으로서 2022 회계연도부터 재무제표를 감사해 왔고, 그 이전에는 Grant Thornton LLP가 2015년부터 독립 감사인이었다고 명시합니다.circle
2026년의 확인 가능한 보고서들은 Deloitte 체계입니다.
 | 보고서 | 원문 확인 결과
 | 2026년 1월 | Deloitte 체계의 USDC examination report로 공개
 | 2026년 3월 | Circle Internet Group, Inc.의 management assertion에 대한 examination report
 | 2026년 4월 | 동일한 Circle Group 및 USDC Reserve Report 구조
 | 2026년 7월 | Deloitte 서명/검증 보고서로 공개
따라서 “2026년 7월은 Deloitte인데 일부 자료가 Grant Thornton이라고 한다”는 불일치는, 대체로 과거 Circle USDC attestation 자료 또는 구(舊) 설명을 최신 2026년 자료에 잘못 적용한 것으로 보입니다. Circle은 2022년 12월에도 Grant Thornton의 월간 attestation을 공개했지만, 이는 당시 자료입니다. 2026년에 Grant Thornton에서 Deloitte로 변경된 것이 아니라, 전환은 2022 회계연도부터 이미 이루어진 것입니다.circle+3
5. Paxos PYUSD 및 Tether
Paxos PYUSD: 월간 reserve report
Paxos의 PYUSD Transparency Reports 페이지는 매월 두 종류의 문서를 제공한다고 밝힙니다.
Paxos Reports: 월말 후 5영업일 내의 자체 보고 포트폴리오 구성. 독립 검토 대상이 아님
Attestations: 독립 회계법인의 월간 검증 문서
2025년 2월 28일 이후 attestation 제공기관: KPMG LLP
그 이전: WithumSmith+Brown, PCpaxos
URL 규칙 및 최근 3개월 PDF
고정적·예측 가능한 공개 PDF URL 규칙: 없음
2026년 최근 3개월의 Paxos 공식 PYUSD PDF 직접 링크: 없음 — 이번 조사에서는 Paxos 투명성 페이지의 동적 UI 뒤에 있는 각 PDF 원본 URL을 원문으로 검증하지 못했습니다.
공식 허브 링크: PYUSD Transparency Reports
외부에서 색인된 2026년 5월의 제3자 보관 원본은 아래와 같지만, Paxos 공식 도메인이 아니므로 Paxos 공식 파일 링크로 분류하지 않습니다.
PYUSD Reserve Reconciliation — 2026-05tessera
PYUSD Reserve Report의 표 항목
이번에 원문 PDF 전체를 Paxos 공식 서버에서 확보하지 못했으므로 “표 항목 전체”를 공식 PDF 원문 그대로 확정할 수는 없습니다. 확인된 2026년 5월 원본 보관본에서 보이는 열은 다음과 같습니다.
 | 원문 열 이름
 | Description
 | Custodian
 | Class
 | USD
 | Page
 | Conf.
동 보고서의 확인 가능한 자산 분류/행 예시는 다음과 같습니다.
Cash — FBO authorized token holders
Commercial banks (FDIC-insured accounts)
cash
overnight_repo
Total reservestessera
Paxos의 공개 설명은 PYUSD 준비금이 U.S. dollar deposits, U.S. Treasuries, cash equivalents로 구성된다고 설명하며, 각 월말 후 5영업일에 자체 보고가 게시된다고 밝힙니다. 다만 이 설명만으로 PDF의 모든 테이블 헤더가 매월 동일하다고 단정할 수는 없습니다.paxos+1
Tether: 최근 2개 분기 보고서
Tether는 준비금 보고서를 분기별로 공개합니다. 공식 transparency 페이지의 reports 탭에서 각 assurance report에 접근하는 방식이며, URL은 Contentful 자산 해시를 사용하므로 규칙적으로 합성하기 어렵습니다.tether+1
 | 기준일 | 실제 PDF 링크 | 검증기관
 | 2026-06-30 | Tether Financial Figures and Reserves Report — 30 June 2026 | BDO Advisory Services S.r.l.
 | 2026-03-31 | Tether Financial Figures and Reserves Report — 31 March 2026 | BDO Advisory Services S.r.l.
2026년 6월 30일 보고서는 준비금 자산을 US$187,751,426,411, 초과 준비금을 US$4,109,529,196으로 제시합니다. 2026년 3월 31일 보고서는 준비금 자산이 부채를 US$8,232,209,778 초과한다고 명시합니다.ctfassets+1
Tether 표 항목
Tether PDF는 단순한 종목별 CSV형 holdings가 아니라, Financial Figures 및 Reserves Report의 자산·부채·준비금 범주형 표입니다. 이번 검색 원문에서 확인 가능한 표/보고 항목은 다음과 같습니다.
Financial Figures and Reserves Report
Reserves for Tether tokens in circulation
value of the assets composing the Reserves
liabilities of the Company issuing fiat-denominated Tether tokens
assets above liabilities 또는 초과 준비금에 해당하는 차액
준비금 구성의 자산군별 breakdown
발행 Tether token의 계약상 상환가치에 관한 항목
다만 검색 인덱스가 두 PDF의 전체 표를 완전한 텍스트로 노출하지 않아, 원문 PDF 안의 전체 열 이름을 정확히 전부 열거하는 것은 불가합니다. 따라서 요청 기준상 전체 열 이름은 없음(이번 조사에서 완전 추출·검증 불가)로 처리하는 것이 정확합니다. Tether는 정형 holdings CSV를 제공하는 것이 아니라, 분기 PDF의 범주형 준비금 공시를 제공하는 구조입니다.tether+2
데이터 소스별 판정
 | 대상 | 기계판독 적합도 | 실제 제공 형태 | 공개 API | 권장 사용
 | BlackRock USDXX | 매우 높음 | 일별 holdings 다운로드, CSV | 별도 공식 API 확인 안 됨 | 개별 보유종목·CUSIP·만기 추적
 | Circle transparency | 중간 | 동적 화면 표 | 없음 | 총액, 준비금 구성, 7/30/365일 mint/burn
 | Circle examination | 중간 | 월간 PDF | 없음 | Circle 잔액·공정가치·CUSIP 검증
 | Paxos PYUSD | 낮음~중간 | 월간 보고서/attestation PDF | 없음 | 월말 구성·보증 확인
 | Tether | 낮음 | 분기 assurance PDF | 없음 | 분기별 범주형 준비금과 초과준비금 확인
가장 재현성 높은 조합은 BlackRock USDXX 일별 CSV + Circle 월간 PDF + Circle transparency 화면 수치 스냅샷입니다. 이 조합은 개별 Treasury 식별자와 만기, Circle이 보고한 준비금 총액, 단기 발행·상환 흐름을 서로 교차 검증할 수 있습니다.circle+2
72개 출처
BlackRock USDXX CSV 자동 다운로드 방법 및 URL 구조
Circle 투명성 페이지 웹 스크래핑 시 유의사항
USDXX holdings 데이터의 CUSIP별 액면가와 시가 평가액 차이
USDC 월간 Grant Thornton attestation PDF 파싱 팁
Circle Reserve Fund와 직접 보유 Treasuries의 비율 변화 추이
출처
72

--- 링크 ---
BlackRock Circle Reserve Fund — USDXX | https://www.blackrock.com/cash/en-us/products/329365/circle-reserve-fund
Transparency & Stability 페이지 | https://www.circle.com/transparency
2026 USDC Examination Report January 26 | https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/USDCAttestationReports/2026/2026%20USDC_Examination%20Report%20January%2026.pdf
2026 USDC Examination Report March 26 | https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/USDCAttestationReports/2026/2026%20USDC_Examination%20Report%20March%2026.pdf
2026 USDC Examination Report April 26 | https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/USDCAttestationReports/2026/2026%20USDC_Examination%20Report%20April%2026.pdf
2026 USDC Examination Report July 26 (1) | https://6778953.fs1.hubspotusercontent-na1.net/hubfs/6778953/USDCAttestationReports/2026/2026%20USDC_Examination%20Report%20July%2026%20(1).pdf
PYUSD Transparency Reports | https://www.paxos.com/pyusd-transparency
PYUSD Reserve Reconciliation — 2026-05 | https://tessera.financial/PYUSD_2026-05/original/report.pdf
Tether Financial Figures and Reserves Report — 30 June 2026 | https://assets.ctfassets.net/vyse88cgwfbl/2kYf7r64h3tzwiu6F0CbUB/2997abd2f11ecea74a21528048b50707/Opinion___Report_-_Tether_International_Financial_Figure_30-06-2026.pdf
Tether Financial Figures and Reserves Report — 31 March 2026 | https://assets.ctfassets.net/vyse88cgwfbl/6crn1tXbl6AtWZBWucZnfg/c4ff472d70c1b48c2f689f27b54c84f5/ISAE_3000R_-_Opinion_Tether_International_Financial_Figure_31-03-2026.pdf