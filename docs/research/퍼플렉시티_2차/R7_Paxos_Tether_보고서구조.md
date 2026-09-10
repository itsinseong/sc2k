완료됨
5 단계
아래는 두 번째 파서의 문서 분류·표 추출 규칙에 바로 쓸 수 있도록 Paxos(PYUSD·USDP·USDG)와 Tether의 공식 보고서 구조를 비교한 정리입니다. 핵심 차이는 Paxos는 월간 자체 Reserve Report와 별도 감사인 attestation을 병렬로 내며, 자산을 종목/CUSIP·수탁기관·만기 단위까지 세분한다는 점입니다. 반면 Tether는 분기별 BDO assurance 문서 안에서 자산을 대범주별 합계로 제시합니다.paxos+1
문서별 파서 구조
 | 발행사 | 문서 | 링크 | 행 항목 목록 | 기준일 표기 | 텍스트 추출 가능 여부
 | Paxos / PYUSD | 자체 월간 Reserve Report | 공식 PYUSD Transparency | 보통 Description 또는 자산 설명, Custodian, CUSIP, Maturity Date, Current Market Value/Fair Value로 구성. 대표 자산은 현금·은행예금, 익일물 미 국채 담보 역레포, 역레포 담보로 제공된 개별 미국 국채. | 대체로 As of [Month day, year] 또는 Reserve Assets ([date]). 보고서 말미/표 제목의 날짜를 우선 파싱. 자체 보고서는 일반적으로 월말 후 5영업일에 공개됨. | 가능성이 높음. 공식 PDF는 디지털 생성 표로 배포되어 텍스트 레이어가 있을 가능성이 높고, 검색 색인에도 CUSIP·Maturity Date·시장가치 열이 노출됨. 다만 셀 좌표·줄바꿈으로 인해 표 전용 추출기를 권장. paxos+1
 | Paxos / PYUSD | KPMG 월간 attestation / examination | 공식 PYUSD Transparency | Description, CUSIP, Maturity Date, Fair Value ($)가 중심. 역레포 및 담보 국채의 종목별 행, Total U.S. Government Guaranteed Debt Instruments Held Pursuant to Overnight Reverse Repurchase Agreements, Total U.S. Dollars Held, Total Fair Value of Redemption Assets 등 합계 행. 별도 표 또는 본문에 Total Token Liabilities Outstanding/발행량이 나타남. | 보통 특정 날짜·시간의 스냅샷. 예전 Paxos 양식은 두 개의 관찰 시점과 5:00 pm ET 같은 시간까지 기재한 사례가 있어, 날짜만이 아니라 as_of_datetime 필드를 두는 편이 안전함. | 가능. PDF 검색 결과에서 열명, CUSIP, 만기일, 금액이 직접 추출됨. 스캔 이미지형 문서로 볼 근거는 없음. KPMG 문서는 표 머리글 반복과 합계행 인식 규칙이 필요. paxos+2
 | Paxos / USDP | 월간 Reserve Report 및 독립 attestation | Paxos USDP 제품 페이지 / Paxos 투명성 안내 | 원칙적으로 PYUSD와 같은 Paxos 계열 구조: 적격 현금·현금성 자산, 역레포 및 해당 담보, 현금잔고, 자산 합계, 토큰부채/발행량 비교. 다만 해당 월의 실제 편입자산에 따라 CUSIP·만기 행 수와 현금/레포 비중은 달라짐. | 월말 또는 attestation이 명시하는 특정 보고일·시간. | 대체로 가능. 과거 USDP attestation PDF는 텍스트가 색인되어 있고, 복수 기준일·시간이 노출됨. 문서별로 날짜 파서가 단일 날짜를 강제하지 않도록 설계. paxos+1
 | Paxos / USDG | 월간 Reserve Report 및 독립 attestation | 공식 USDG Transparency | 상위 표 형태는 PYUSD와 유사한 월간 준비금/attestation 구조이나, 발행 법인·규제권역·감사기준이 다름. 자산 상세가 개별 증권 단위로 제시되는지 여부와 수탁기관 표기는 월별 PDF로 검사 필요. | 월간 기준일. 문서상 발행 법인 및 기준 시각을 함께 저장 권장. | 대체로 가능하되 검증 필요. 웹페이지의 보고서 링크가 동적 렌더링되어 있어 PDF 원문을 수집한 뒤 텍스트 레이어를 검사하는 것이 안전. USDG attestation은 2026-02-27 이후 KPMG 발행. paxos
 | Tether / USD₮ | BDO ISAE 3000R 분기 assurance — 2026-03-31 | 공식 BDO PDF | 자산 표의 대범주: Cash & Cash Equivalents & Other Short-Term Deposits, Corporate Bonds, Precious Metals, Bitcoin, Other Investments, Secured Loans. 첫 범주는 다시 U.S. Treasury Bills, Overnight Reverse Repurchase Agreements, Term Reverse Repurchase Agreements, Cash & Bank Deposits 등으로 분해. 부채는 Total Liabilities, 그중 Digital tokens issued가 별도 제시되며, Total Assets − Total Liabilities가 초과 준비금/순자본. | as at 31 March 2026이며, 보도자료 기준 스냅샷 시각은 11:59 PM UTC. 파서에는 as_of_date, as_of_time, timezone을 분리 저장 권장. | 가능. 검색 색인에서 자산범주, 금액, 총자산·총부채·초과액 문구가 직접 추출됨. 스캔 이미지 PDF가 아니라 선택 가능한 텍스트 기반 PDF로 판단됨. assets.ctfassets+2
 | Tether / USD₮ | BDO ISAE 3000R 분기 assurance — 2026-06-30 | 공식 BDO PDF | Q1과 같은 대범주 구조. 보고서 검색 결과상 준비금 총액은 US$187,751,426,411, 현금성·단기예치금 소계는 US$140,642,627,095, 기업채·귀금속 등 다음 대범주가 이어짐. 자산 종류별 집계금액이 핵심이며 개별 채권 CUSIP 또는 만기별 보유명세는 기본 표에 없음. | as at 30 June 2026 형식. 발행일·서명일은 기준일과 다른 메타데이터이므로 분리해야 함. | 가능. 공식 Contentful PDF의 검색 색인이 수치와 표 제목을 직접 노출함. 표 병합은 가능하지만 각주 번호·줄바꿈·소계 행을 보존해야 함. assets.ctfassets
Paxos PYUSD: 최근 3개월 수집 규칙
현재 기준일은 2026-09-04이므로, “최근 3개월”은 실무적으로 2026년 6월·7월·8월 기준월을 의미합니다. 다만 Paxos의 공식 페이지는 “View Reports” 영역을 동적으로 렌더링하므로, 페이지 텍스트 추출만으로는 각 월별 고정 PDF URL이 노출되지 않았습니다. 따라서 수집기는 공식 Transparency 페이지를 시작점으로 하되, 브라우저/HTML 렌더링 후 PDF 앵커를 수집하는 방식이 적절합니다. Paxos는 자체 보고서를 월말 후 5영업일에 먼저 공개하고, 독립 attestation을 별도 게시합니다.paxos
 | 기준월 | 자체 Reserve Report | KPMG attestation | 수집 시 판별 키
 | 2026-08 | PYUSD Transparency 공식 목록에서 2026-08 기준 Reserve Report PDF 선택 | 같은 목록에서 2026-08 기준 KPMG PDF 선택 | 파일명·표지·표 제목의 August 2026, As of August 31, 2026, Reserve Report 대 Examination/Attestation
 | 2026-07 | PYUSD Transparency 공식 목록에서 2026-07 기준 Reserve Report PDF 선택 | 같은 목록에서 2026-07 기준 KPMG PDF 선택 | July 2026, July 31, 2026, 문서종류
 | 2026-06 | PYUSD Transparency 공식 목록에서 2026-06 기준 Reserve Report PDF 선택 | 같은 목록에서 2026-06 기준 KPMG PDF 선택 | June 2026, June 30, 2026, 문서종류
PYUSD의 발행량 산식
파서의 기본 검증식은 다음처럼 두 레벨로 두는 것이 좋습니다.
Reserve coverage ratio=Total Fair Value of Redemption AssetsPYUSD Token Liabilities Outstanding\text{Reserve coverage ratio}
=
\frac{\text{Total Fair Value of Redemption Assets}}
{\text{PYUSD Token Liabilities Outstanding}}Reserve coverage ratio=PYUSD Token Liabilities OutstandingTotal Fair Value of Redemption Assets​
Reserve surplus=Total Fair Value of Redemption Assets−PYUSD Token Liabilities Outstanding\text{Reserve surplus}
=
\text{Total Fair Value of Redemption Assets}
-
\text{PYUSD Token Liabilities Outstanding}Reserve surplus=Total Fair Value of Redemption Assets−PYUSD Token Liabilities Outstanding
자체 Reserve Report: 개별 준비자산 시장가치의 합계가 준비금 총액입니다.
KPMG attestation: Total Fair Value of Redemption Assets를 준비금 총액으로, Total Token Liabilities Outstanding를 발행량의 달러상 부채로 저장합니다.
PYUSD의 상환 구조가 1:1 USD 기준이므로, 정상적으로는 token_liability_usd가 명목 PYUSD 발행량에 대응합니다. 다만 토큰 개수 필드가 문서에 따로 있으면 그 값을 우선하고, 달러 부채는 금액 필드로 유지하는 것이 안전합니다.
역레포의 경우, 경제적 준비금 노출을 이중계산하지 않도록 역레포 계약금액과 담보 국채의 개별 CUSIP 행을 관계형으로 연결해야 합니다. 담보 국채를 별도 독립 자산으로 다시 합산하면 총액이 과대계상될 수 있습니다. Paxos의 예시 표에는 overnight reverse repurchase agreements와 그에 따라 보유된 미국정부 보증채 합계가 함께 나타납니다.paxos
PYUSD 페이지 수
Paxos의 현재 PDF별 실제 페이지 수는 공식 페이지의 동적 링크가 노출되지 않아 여기서 확정할 수 없습니다. 따라서 문서 메타데이터로 다음을 별도 저장하세요.
pdf_page_count: PDF /Pages/Count 또는 렌더러 기준 실제 페이지 수
report_page_of_reserve_table: 준비금 표가 시작되는 페이지
report_page_of_liability_table: 발행량/부채 표가 시작되는 페이지
auditor_opinion_page: KPMG 결론 페이지
과거 공개된 PYUSD KPMG 문서는 자세한 CUSIP·만기·공정가치 표를 포함하는 전자문서형 PDF라는 점은 확인됩니다. 월별 페이지 수를 상수로 가정하는 것은 권장하지 않습니다.paxos
Tether: 표와 숫자
Tether는 분기마다 BDO Italia의 ISAE 3000R reasonable-assurance 문서를 공개하며, 최신 공개 투명성 페이지는 2026-03-31 보고서를 기준으로 표시합니다. 이 페이지는 총자산 191,767,741,495달러, 총부채 183,535,531,717달러, 순자본/초과 준비금 8,232,209,778달러를 제시합니다.tether
 | 항목 | 2026-03-31 | 2026-06-30 | 파싱 원칙
 | 기준일 | 2026-03-31 | 2026-06-30 | 문서 제목·as at 문구를 원천으로 사용
 | 통화 단위 | US$ / USD | US$ / USD | currency=USD, unit=1로 정규화. 백만 단위가 아니라 원단위 금액으로 보존
 | 총 준비자산 | 191,767,741,495달러 | 187,751,426,411달러 | total_assets
 | 총부채 | 183,535,531,717달러 | PDF 원문에서 추출 필요 | total_liabilities; 토큰 관련 부채는 하위 필드로 분리
 | 초과 준비금 | 8,232,209,778달러 | total_assets - total_liabilities로 검증 | excess_reserves 또는 net_equity
 | 자산 세부화 | 현금성·단기예치, 기업채, 귀금속, 비트코인, 기타 투자, 담보대출 | 동일한 범주 구조 | 상위 범주와 현금성 범주 하위 행을 모두 계층적으로 저장
Tether의 Q1 보고서에서 총부채 중 디지털 토큰 발행 관련 금액은 183,438,487,810달러로 따로 보도되었습니다. 따라서 total_liabilities와 digital_token_liabilities를 같은 값으로 처리하면 안 됩니다. 나머지는 기타 부채입니다.tether
통합 스키마와 매핑 불가 항목
세 발행사 표를 하나의 평면 테이블로 강제하면 정보가 손실됩니다. 권장 방식은 보고서 헤더 + 자산 행 + 부채 행 + 상품식별자 행의 4개 논리 엔터티로 나누는 것입니다.
 | 통합 필드 | Paxos / PYUSD·USDP | Paxos / USDG | Tether / USD₮ | 매핑 상태 및 설계
 | issuer | Paxos Trust Company 계열 | USDG 발행 법인 기준 | Tether International 등 해당 보고서 발행 법인 | 가능. 브랜드와 법적 발행 법인을 분리: brand, legal_issuer
 | report_type | self_report 또는 independent_attestation | 동일 개념이나 감사기준 차이 | reasonable_assurance / BDO Reserves Report | 가능. report_type, assurance_standard, assurance_provider 분리
 | as_of_date | 월별 월말 또는 특정 일자 | 월별 | 분기말 | 가능
 | as_of_time·timezone | 일부 문서에 5:00 pm ET 등 | 문서별 확인 | Q1에는 11:59 PM UTC 표기 | 부분 가능. 누락 허용 필드로 설계
 | asset_category | 현금, 역레포, 담보 국채 등 | 유사하되 실제 보유 내역별 상이 | 현금성·단기예치, 기업채, 귀금속, BTC, 기타 투자, 담보대출 | 가능하나 서로 다른 taxonomy를 보존해야 함. reported_category와 normalized_category를 병행
 | instrument_description | 개별 증권/역레포 설명 | 문서에 따라 가능 | 보통 범주명만 존재 | 비대칭. Tether에는 개별 종목 레벨 정보 없음
 | security_identifier | CUSIP 존재 가능 | 문서별 확인 | 없음 | 매핑 불가. nullable security_identifier_type, security_identifier 사용
 | maturity_date | 국채·레포 단위의 만기일 존재 가능 | 문서별 확인 | 대범주에 대해 일부 만기 성격만 설명될 수 있으나 개별 만기일 없음 | 매핑 불가. maturity_date를 nullable로, 범주 단위 tenor는 별도 maturity_bucket
 | custodian | 수탁기관·은행/상대방이 행/설명에 등장 가능 | 문서별 확인 | 범주 금액 중심; 자산별 수탁기관 테이블 없음 | 매핑 불가. 수탁기관을 억지로 Tether 범주에 붙이지 말 것
 | repo_collateral_link | 역레포와 담보 국채의 연결 필요 | 가능성 있음 | 범주 집계여서 해당 연결 없음 | 매핑 불가. 별도 관계 테이블 collateral_relationships
 | fair_value_usd | 개별 자산 및 합계 | 개별 또는 범주/합계 | 범주 및 합계 | 가능. 정밀도는 Decimal로 보존
 | issued_token_liability_usd | PYUSD 토큰부채/상환 의무 | USDG·USDP 토큰부채 | 디지털 토큰 관련 부채 | 가능하지만 Tether의 total_liabilities와 구분 필수
 | total_liabilities_usd | attestation 문서별 표현 확인 필요 | 문서별 확인 | 명시적 총부채 존재 | 부분 가능. Paxos에는 토큰 상환 부채 중심일 수 있어 정의 차이를 보존
 | excess_reserves_usd | 자산−토큰부채 또는 자산−총부채 | 동일 | 자산−총부채 = Net Equity | 비교 지표로 가능하나 분모가 같지 않을 수 있음. surplus_basis 필수
 | page_number | 표가 여러 페이지에 걸칠 수 있음 | 동일 | 표/각주가 여러 페이지 | 가능. 추출 provenance로 필수 저장
권장 최소 스키마
text
reports
- report_id
- brand
- legal_issuer
- token_symbol
- report_type
- assurance_provider
- assurance_standard
- publication_date
- as_of_date
- as_of_time
- timezone
- currency
- pdf_url
- pdf_page_count
- text_layer_detected
- source_hash
reserve_lines
- reserve_line_id
- report_id
- parent_line_id
- reported_category
- normalized_category
- instrument_description
- security_identifier_type
- security_identifier
- custodian
- counterparty
- maturity_date
- maturity_bucket
- amount_usd
- valuation_basis
- page_number
- table_name
- row_label_raw
liability_lines
- liability_line_id
- report_id
- reported_category
- normalized_category
- amount_usd
- page_number
- row_label_raw
collateral_relationships
- report_id
- repo_reserve_line_id
- collateral_reserve_line_id
- relationship_type
- included_in_total_reserves
두 번째 파서 판단 규칙
문서 유형부터 분류합니다.
Reserve Report만 있으면 Paxos 자체보고서, KPMG·Examination·Attestation이면 Paxos 독립 검증문서, BDO·ISAE 3000R·Financials Figures and Reserves Report이면 Tether assurance 문서로 분류합니다. Paxos는 두 문서를 모두 월별로 공개하고, Tether는 분기별 보고서를 공개합니다.paxos+1
Paxos에서는 세부 증권행을 보존합니다.
CUSIP와 만기일, 수탁기관, 공정가치가 있는 행은 개별 reserve_lines로 저장합니다. 합계행은 is_total=true 또는 상위 노드로 보존하고, 개별 행 합계와 대조합니다. CUSIP는 숫자로 캐스팅하면 선행 0 또는 체크문자 처리 문제가 생길 수 있으므로 문자열입니다.paxos
Tether에서는 범주행을 개별 보유종목으로 오인하지 않습니다.
Bitcoin, Precious Metals, Secured Loans 등은 하나의 투자종목이 아니라 공시상 자산 범주입니다. reported_category에 원문을 보존하고, 필요 시에만 normalized_category로 현금성·국채·디지털자산·귀금속·대출·기타로 매핑합니다.tether+1
초과 준비금의 정의를 명시합니다.
Tether의 초과분은 Total Assets − Total Liabilities이며, Q1 2026에는 82.322억 달러입니다. Paxos에서는 문서가 redemption assets와 token liabilities를 비교할 수 있으므로 같은 이름의 “excess reserves”라도 비교 기준이 다를 수 있습니다. surplus_basis = total_assets_minus_total_liabilities 또는 redemption_assets_minus_token_liabilities를 저장해야 교차 비교 오류를 막을 수 있습니다.tether+1
텍스트 PDF를 기본으로 하되 OCR 폴백을 둡니다.
조사된 PYUSD·USDP·Tether 문서는 모두 검색 엔진에서 열명·표 행·금액을 추출할 수 있어 텍스트 레이어형 PDF로 판단됩니다. 그러나 파서 런타임에서 페이지별 문자 수가 거의 0이거나, 추출된 숫자·표 헤더가 없으면 scan_suspected=true로 전환하고 OCR을 보조 경로로 두는 것이 좋습니다.paxos+4
Paxos USDG는 감사인·기준 체계가 PYUSD와 다름을 메타데이터에 반영합니다.
USDG도 월간 투명성·attestation 체계를 갖지만, 2026-02-27 이후 KPMG가 담당하고 ISCA 기준이 적용됩니다. 반면 PYUSD KPMG attestation은 AICPA attestation standards로 설명됩니다. 따라서 assurance_standard를 단순 “KPMG”로 뭉개지 않는 것이 좋습니다.paxos+1
35개 출처
PYUSD와 Tether USDT의 준비금 자산 구성 차이점
스테이블코인 감사 보고서 PDF 파싱 시 주의할 점
USDT 분기별 Assurance Report 구조와 BDO 양식
CUSIP 및 만기일 기준 채권 파서 구현 방안
Paxos 준비금 보고서 업데이트 주기 및 공시 일정
출처
35

--- 링크 ---
공식 PYUSD Transparency | https://www.paxos.com/pyusd-transparency
Paxos USDP 제품 페이지 | https://www.paxos.com/usdp
Paxos 투명성 안내 | https://www.paxos.com/regulation-and-transparency/
공식 USDG Transparency | https://www.paxos.com/usdg-transparency
공식 BDO PDF | https://assets.ctfassets.net/vyse88cgwfbl/6crn1tXbl6AtWZBWucZnfg/c4ff472d70c1b48c2f689f27b54c84f5/ISAE_3000R_-_Opinion_Tether_International_Financial_Figure_31-03-2026.pdf
공식 BDO PDF | https://assets.ctfassets.net/vyse88cgwfbl/2kYf7r64h3tzwiu6F0CbUB/2997abd2f11ecea74a21528048b50707/Opinion___Report_-_Tether_International_Financial_Figure_30-06-2026.pdf
paxos | https://paxos.com/wp-content/uploads/2024/05/PYUSD-Examination-April-2024-fully-executed.pdf
tether | https://tether.to/transparency/?tab=reports
tether | https://tether.io/news/tether-posts-1-04b-q1-2026-profit-despite-highly-volatile-global-markets-reaches-all-time-highs-8-23b-reserve-buffer-and-maintains-u-s-treasury-heavy-backing/