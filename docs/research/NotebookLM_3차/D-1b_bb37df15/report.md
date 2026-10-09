# D-1b 은행 발행 시 BIS 자본과 LCR 처리(두 번째 실행)

- 노트북: https://notebook.google.com/notebook/bb37df15-0c3f-4462-83bb-737182bffdff?authuser=1 (자동 제목 "대한민국 신탁법")
- 보고서 제목: 원화 스테이블코인 준비금 공시 기준 및 은행 건전성 규제(BCBS SCO60) 분석 보고서
- 소스 24종, 보고서 참고 링크 22개, 본문 14970자
- 실행 방식: Deep Research
- 수집: 2026-10-06 Aside repl, 원문 대조 전

---
# 원화 스테이블코인 준비금 공시 기준 및 은행 건전성 규제(BCBS SCO60) 분석 보고서

## 1. 서론 및 원화 스테이블코인 준비자산 규율의 필요성

가상자산이용자보호법이 본격적으로 시행된 이후, 대한민국 금융당국과 국율기구는 가상자산 시장의 입법적 완성도를 높이기 위해 가상자산 2단계 입법 추진을 서두르고 있다 [cite: 1, 2]. 2단계 입법의 핵심 과제는 가치안정형 디지털자산(스테이블코인)의 발행, 유통, 수탁, 공시 및 건전성 규율 체계를 확립하는 것이다 [cite: 2, 3]. 스테이블코인은 발행자가 제시하는 연동 자산(Pegging Asset)에 대한 신뢰를 바탕으로 가치 유지를 도모하므로, 준비자산(Reserve Assets)의 질적 우수성과 상환 유동성의 확보가 제도의 성패를 가르는 관건이 된다 [cite: 2, 4].

준비자산 관리 및 공시 제도의 미비는 스테이블코인의 가치 이탈(De-pegging)을 유발하며, 이는 가상자산 시장 내부의 충격을 넘어 전통 단기자금시장과 시중은행 유동성 리스크로 전이되는 코인런(Coin-run) 사태를 야기할 수 있다 [cite: 4]. 이에 본 보고서는 국회 정무위원회에 계류 중인 9건의 제정안에 포함된 준비자산 관련 규정을 정밀 비교하고, 바젤은행감독위원회(BCBS)의 암호자산 건전성 기준(SCO60) 상 1b그룹 조건과 유동성커버리지비율(LCR) 및 자본 규제를 종합 분석하여, 향후 원화 스테이블코인 준비금 공시 기준 제정을 위한 법적·제도적 시사점을 제공하고자 한다.

---

## 2. 국회 정무위원회 계류 제정안 9건 비교 및 준비자산 수치적 기준 분석

국회 정무위원회에는 원화 스테이블코인의 법적 지위 부여 및 규율을 위해 9건의 제정안이 계류되어 있다 [cite: 5, 6]. 발의된 안들은 법률의 형태에 따라 디지털자산 전반을 규율하는 기본법안 형태와 가치안정형 디지털자산만을 별도로 다루는 특별법안 형태로 대별된다 [cite: 6].

법안별 원문 및 검토보고서에서 확인되는 수치적 기준, 준비자산 적격 요건, 수탁 및 공시 의무를 정리하면 다음과 같다 [cite: 1, 4, 5].

| 의안번호 | 대표발의자 | 법률안명 | 자기자본 및 인가 요건 | 준비자산 상응 비율 및 구성 자산 | 독립 수탁 및 공시 규정 |
|---|---|---|---|---|---|
| 2210736 | 민병덕 | 디지털자산기본법안 | 자기자본 5억원 이상, 금융위원회 인가 (비은행 포함) [cite: 1, 4] | 발행 잔액 대비 1:1 이상 상응 비율 유지, 현금·예금 및 단기채권 등 고유동성 자산 [cite: 1, 5] | 제3기관(은행·신탁사) 독립 신탁 관리, 준비자산 부족 시 즉시 보충 및 당국 보고 의무 [cite: 1] |
| 2211777 | 김은혜 | 가치고정형디지털자산을활용한지급혁신에관한법률안 | 금융위원회 인가 요건 규정 [cite: 1, 5] | 1:1 가치 고정을 위한 법정화폐 및 안전자산 구성 [cite: 1, 5] | 제3자 수탁 의무화, 정기적 준비자산 검증 및 공시 |
| 2211784 | 안도걸 | 가치안정형 디지털자산의 발행 및 유통에 관한 법률안 | 발행업 인가제 도입 [cite: 5, 7] | 원화 법정화폐 및 고유동성 원화 안전자산으로 상응 [cite: 5] | 발행 잔액 및 준비자산 내역의 주기적 공시 [cite: 7] |
| 2212298 | 김현정 | 가치안정형 디지털자산 발행업 등에 관한 법률안 | 발행업 인가 요건 설정 [cite: 1, 6] | 1:1 상응 비율, 현금·예금 및 단기채권(93일 이하) 등 [cite: 5] | 독립적 수탁기관 신탁 관리 및 공시 의무화 [cite: 1] |
| 2213166 | 이강일 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |
| 2213266 | 김재섭 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |
| 2213449 | 최보윤 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |
| 2214492 | 박상혁 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |
| 2218219 | 김성원 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |

각 제정안에 명시되거나 입법 논의 과정에서 검토된 수치적 기준의 근거는 이용자 상환권의 완전한 보장과 단기 금융시장의 유동성 충격 방지에 두고 있다 [cite: 1, 4, 5]. 자기자본 5억원 이상 요건은 진입 장벽을 정립하면서도 다양한 핀테크 사업자의 참여를 유도하기 위한 최소한의 재무적 기틀로 제시되었으며 [cite: 4], 1:1 준비자산 유치 의무는 지급수단으로서의 신뢰 유지를 위한 필수 불가결한 조건이다 [cite: 1, 5].

준비자산의 구성 요건으로 현금, 은행 예금, 만기 93일 이하의 단기 국채·채권 등이 제시된 근거는, 시장 스트레스 상황에서 자산의 급매각(Fire sale)에 따른 가치 손실을 막기 위함이다 [cite: 1, 5]. 특히 93일(약 3개월) 이하의 만기 제한은 미국 파이낸셜 서비스 위원회의 스테이블코인 법안 및 미 연준의 단기 자금시장 유동성 기준과 정합성을 맞춘 결과다 [cite: 5]. 아울러 계열사가 아닌 제3의 은행이나 신탁회사에 독립 신탁하도록 한 것은 발행자의 파산 시 준비자산이 파산재단에 편입되지 않고 이용자에게 우선 변제되도록 법적 차단막(Bankruptcy-remoteness)을 치기 위함이다 [cite: 1, 8].

---

## 3. 바젤은행감독위원회(BCBS SCO60) 암호자산 건전성 규제 체계

국제결제은행(BIS) 산하 바젤은행감독위원회는 은행의 암호자산 익스포저 규제 표준인 'SCO60: Cryptoasset exposures'를 수립하여 2026년 1월 1일부터 공식 적용할 예정이다 [cite: 9, 10, 11]. SCO60 체계에서 스테이블코인은 적격 요건 충족 여부에 따라 가장 우호적인 자본 규제를 받는 1b그룹(Group 1b)과 고위험 자산으로 분류되는 2그룹(Group 2)으로 나뉜다 [cite: 12, 13, 14].

### 3.1. SCO60 Group 1b 분류 조건 및 상환 위험 시험(Redemption Risk Test)

스테이블코인이 Group 1b로 인정받기 위해서는 전통적 자산에 준하는 위험 관리가 가능함을 입증하는 5가지 기본 분류 조건과 엄격한 상환 위험 시험(Redemption Risk Test)을 통과해야 한다 [cite: 9, 12, 15, 16].

Group 1b 분류의 5가지 기본 조건은 첫째, 참조 자산의 정해진 수량으로 상시 상환되도록 설계될 것 [cite: 12, 16], 둘째, 가치 안정화 메커니즘이 시장 가치 변동을 최소화하도록 작동할 것 [cite: 12, 16], 셋째, 정교한 위험 관리가 가능할 만큼 충분한 데이터와 운용 경험이 축적될 것 [cite: 12, 16], 넷째, 준비자산의 소유권 및 관리 현황에 대한 검증 가능한 정보가 제공될 것 [cite: 12, 16], 다섯째, 발행인이 건전성 자본 및 유동성 규제를 적용받는 감독당국에 의해 감독될 것이다 [cite: 9, 12, 16].

#### 상환 위험 시험(Redemption Risk Test)의 세부 요건

상환 위험 시험은 극심한 금융 스트레스 상황에서도 발행 잔액 전체를 페그 가치(Peg value)대로 상환할 수 있는 세부 자산 요건을 다룬다 [cite: 9, 16].

- 준비자산 가치 및 초과담보: 준비자산의 순가치는 미상환 발행 잔액의 페그 가치 합계 이상이어야 한다 [cite: 16]. 준비자산 자체에 신용위험이나 시장위험이 존재하는 경우, 스트레스 하중을 반영한 후에도 페그 가치 이상이 유지되도록 초과담보(Overcollateralization)를 확보해야 한다 [cite: 15, 16].

- 자산 적격성(Asset Quality Criteria): 통화 연동 스테이블코인의 준비자산은 신용위험과 시장위험이 극히 적은 자산으로 한정된다 [cite: 9, 16]. 중앙은행 예치금, 고신용 정부·공공기관 발행 단기채권, 대규모로 거래되는 고유동성 자산만이 적격 자산으로 인정된다 [cite: 16].

- 통화 일치성(Currency Matching): 준비자산은 연동 대상 법정화폐와 동일한 통화로 표시되어야 한다 [cite: 16]. 운용상 불가피한 극소수(De minimis) 금액에 대해서만 타 통화 보유가 허용되며, 이 경우에도 환율 변동 위험이 헤지되어야 한다 [cite: 16].

- 베이시스 리스크 시험(Basis Risk Test): 은행은 최근 12개월간 해당 스테이블코인의 시장 거래 가격이 페그 가치에서 벗어난 횟수와 이탈 폭을 검증하는 통계적 베이시스 리스크 시험을 지속적으로 수행해야 한다 [cite: 8, 15].

### 3.2. 2025~2026년 BCBS 및 주요국 규제기관의 재검토 진행 상황

BCBS는 2022년 12월 최종 표준 발표 이후, 2024년 7월 정밀 개정을 실시하고 11월 기술적 수정안을 반영하여 최종 시행일을 2026년 1월 1일로 책정하였다 [cite: 10, 11]. 주요국 금융당국은 2025~2026년 본격 시행을 앞두고 국가별 구체적인 도입 하위 규정을 정립하고 있다 [cite: 9, 15].

- 싱가포르 통화청(MAS, 2025년 1월 컨설팅): Group 1b 스테이블코인 준비자산 포트폴리오 전체의 가중평균 잔존만기(Portfolio-weighted average residual maturity)를 3개월 이내로 제한하는 기준을 제안하였다 [cite: 15]. 또한, 현금 예치금을 보관하는 시중은행의 신용등급을 'A-' 이상으로 제한하는 절벽 효과(Cliff effect) 방지책을 함께 검토하고 있다 [cite: 15].

- 증권대차 및 환매조건부채권매매(Repo/SFT) 규제: 준비자산 부풀리기를 막기 위해, 발행자가 보유 채권을 리포로 매도하여 현금을 중복 계상하거나 저품질 자산을 일시적으로 교체하는 행위를 금지하는 엄격한 세부 검증 절차가 논의되고 있다 [cite: 15].

### 3.3. 은행 발행 스테이블코인(Group 1b)과 예금토큰(Group 1a)의 자본 처리 차이

은행이 분산원장기술(DLT)을 활용하여 발행하는 자산은 '예금토큰(Tokenized Deposits, Group 1a)'과 '스테이블코인(Group 1b)'으로 구분되며, 건전성 자본 규제 상 상이한 차등 처리를 받는다 [cite: 8, 10, 13].

| 구분 | 예금토큰 (Tokenized Claims on a Bank, Group 1a) | 은행 발행/보유 스테이블코인 (Group 1b) |
|---|---|---|
| 위험가중치 (Risk Weight) | 원본 전통 예금/채권에 적용되는 신용위험가중치 적용 (Look-through approach) [cite: 8, 13] | 발행인, 상환 이행자, 수탁 중개기관 및 참조자산 신용도를 종합 합산하여 가중치 산정 [cite: 8] |
| 적격 담보 인정 (Collateral) | 원본 자산이 적격 담보 요건 충족 시 담보 인정 [cite: 8, 10, 13] | 담보 인정 불가 (100% Haircut 적용) [cite: 14] |
| 익스포저 한도 (Exposure Limit) | 암호자산 전용 총량 제한 미적용 | Tier 1 자본의 1% 이내 제한 (최대 2%까지 허용되나, 2% 초과 시 전체 익스포저가 Group 2b로 재분류되어 자본 차감) [cite: 14] |
| 인프라 위험 추가자본 (Add-on) | 초기 0% 적용 (네트워크 결함 관찰 시 추가 자본 부과 가능) [cite: 13, 17] | 초기 0% 적용 (분산원장 인프라 취약점 관찰 시 regulatory add-on 제상) [cite: 13, 17] |

### 3.4. 유동성커버리지비율(LCR) 적용: HQLA 인정 여부 및 유출률 분석

유동성 위험 관리 프레임워크 상 예금토큰과 스테이블코인의 처리는 고유동성자산(HQLA) 적격성 및 유출률(Outflow rate) 산정에서 극명하게 갈린다 [cite: 10, 13, 14, 18].

#### 1. 고유동성자산(HQLA) 인정 여부

- Group 1a (예금토큰 및 토큰화 채권): 원본 전통 자산이 HQLA 조건을 만족하고, 결제 정시성 등 LCR operational requirements(LCR30)를 준수하면 HQLA 재고(Stock of HQLA)로 차용할 수 있다 [cite: 10, 13, 18].

- Group 1b (스테이블코인): HQLA로 인정받지 못한다 (SCO60.103) [cite: 10, 13, 14]. 비록 스테이블코인의 준비자산 전체가 중앙은행 예치금이나 국채 등 Level 1 HQLA로만 100% 구성되어 있다 할지라도, 스테이블코인 자체는 HQLA로 합산될 수 없다 [cite: 10, 18].

#### 2. LCR 유출률(Cash Outflow Rates) 산정

- 예금토큰 발행 잔액: 전통 은행 예금 규율을 준용하여 고객 성격에 따라 5%~10%(소매 안정적 예금) 내외의 낮은 유출률이 적용된다.

- 스테이블코인 발행 잔액: 24시간 365일 즉시 전송 및 대규모 동시 상환(Coin-run)이 가능한 특성으로 인해 매우 높은 유출률이 부여된다 [cite: 4, 10, 13]. 은행이 발행한 스테이블코인 부채는 소매 수신이라 하더라도 비안정적 수신으로 간주되어 100%에 근접하는 LCR 현금 유출률이 적용된다 [cite: 10, 13].

---

## 4. 국내 금융당국(금융위원회·금융감독원·한국은행)의 정책 방향

국내 관계 기관들은 가상자산 2단계 입법 과정에서 원화 스테이블코인의 도입 방안을 유동성 안정성과 금융시장의 주권 유지라는 틀 안에서 논의하고 있다 [cite: 1, 2, 3, 4, 19].

### 금융위원회 및 금융감독원 정책 구상

금융위원회는 가상자산 2단계 입법을 연내 국회 제출 목표로 준비 중이며, 스테이블코인을 지급결제 및 수탁 규율의 중심에 두고 있다 [cite: 2, 3, 20].

- 발행인 인가제 및 재무 건전성: 한국 법인으로서 엄격한 자기자본 요건과 내부통제 기준을 갖춘 경우에 한해 금융위원회 인가를 받아 발행할 수 있도록 설계한다 [cite: 1, 5].

- 준비자산 관리의 제3자 수탁 의무: 발행인의 영업 실패나 파산 시 위험 전이를 막기 위해 예금, 국채 등 안전자산 위주의 준비자산을 독립된 제3의 은행이나 신탁회사에 신탁 보관하도록 의무화한다 [cite: 1, 3].

- 은행 중심 컨소시엄 모델 (51% 지분 룰): 초기 시장의 난립을 방지하고 공적 신뢰를 확보하기 위해, 은행이 과반 지분(51% 이상)을 보유한 컨소시엄에 스테이블코인 발행을 우선적으로 허용하는 방안을 유력하게 다루고 있다 [cite: 2, 3, 20].

### 한국은행의 입장 및 금융안정 리스크 분석

한국은행은 '디지털 시대의 화폐, 혁신과 신뢰의 조화 - 원화 스테이블코인의 주요 이슈와 대응방안' 보고서(2025.10.27) 및 관련 발표를 통해 스테이블코인의 7대 리스크 요인을 제시하였다 [cite: 4, 19, 21, 22].

- 7대 핵심 리스크: 1) 디페깅 및 가치 미보장 위험 [cite: 4, 21], 2) 코인런 발생에 따른 단기자금시장 충격 및 금융안정 위협 [cite: 4, 21], 3) 소비자 보호 공백 [cite: 21], 4) 금산분리 원칙 상충 [cite: 21], 5) 자본유출입 및 외환 규제 우회 [cite: 4, 21], 6) 통화정책 유효성 제약 [cite: 4], 7) 통화 주권 약화 [cite: 4].

- 은행 중심 발행 원칙 강조: 한국은행은 민간 비은행 기업의 독자적 발행을 허용할 경우 통화제도의 신뢰가 흔들릴 수 있음을 지적하며, 은행이 직접 발행하거나 은행이 주도하는 컨소시엄 체계 형태만을 허용하여 중앙은행의 금융안정망 및 자본·외환 규제 틀 안에서 관리해야 함을 분명히 하고 있다 [cite: 3, 19].

---

## 5. 규제 문서 및 법령 원문 종합 정리 표

원화 스테이블코인 준비자산 공시 기준 설정 및 건전성 규제에 직접적인 가이드라인을 제공하는 국내외 핵심 1차 자료 규정 원문은 다음과 같다 [cite: 5, 10, 15, 16, 19].

| 문서(기관, 날짜) | 조항 | 내용 원문 | 원화 스테이블코인 준비자산 구성에 주는 영향 | 주소 |
|---|---|---|---|---|
| BCBS SCO60<br>(BIS, 2024.07.17) | SCO60.12 [cite: 16] | "To pass the redemption risk test, the bank must ensure that... The reserve assets must comprise assets with minimal market and credit risk where: (i) The reserve assets should consist mainly of assets with short-term maturities and high credit quality; and (ii) the reserve assets have a proven record of relative stability of market terms..." [cite: 16] | 준비자산 구성을 시장·신용위험이 최소화된 단기 국채 및 고신용 예치금으로 국한하며, 스트레스 상황 대비 초과담보 배정을 규무화함 [cite: 15, 16]. | https://www.bis.org/committees/bcbs/basel-framework/standard/sco/60/inforce/2026-01-01/published/2024-07-17 [cite: 16] |
| BCBS SCO60<br>(BIS, 2024.07.17) | SCO60.103 [cite: 10, 13] | "Group 1b and Group 2 crypto-assets, by contrast, should not be considered HQLA." [cite: 10, 13] | 스테이블코인 자체는 고유동성자산(HQLA)으로 인정받을 수 없어 보유 은행의 LCR 비율 산정 시 유동성 차감 요인으로 작동함 [cite: 10, 18]. | https://www.bis.org/committees/bcbs/basel-framework/standard/sco/60/inforce/2026-01-01/published/2024-07-17 [cite: 10] |
| MAS Consultation Paper<br>(MAS, 2025.01) | Section 2.9 [cite: 15] | "MAS proposes to specify a portfolio-weighted average residual maturity limit of three months on the reserve assets of a Group 1b cryptoasset." [cite: 15] | 준비자산 포트폴리오의 가중평균 잔존만기를 3개월 이내로 규정하여 금리 변동 위험을 완화하도록 구체적 운용 기준을 제시함 [cite: 15]. | https://www.mas.gov.sg/-/media/mas-media-library/publications/consultations/ppd/2025/consultation-on-the-prudential-treatment-of-cryptoassets-and-reqs-for-at1-and-t2-capital-instruments.pdf [cite: 15] |
| 가상자산 2단계 입법 검토보고서<br>(국회입법조사처, 2025) | 보고서 제15쪽 [cite: 5] | "과 비은행을 포함하는 발행인이 일정한 자본금 요건 등을 갖추어 금융위원회의 인가를 받도록 하며, 가치안정성 및 환급가능성을 담보하기 위하여 현금, 예금 및 단기채권(93일 이하) 등으로 구성된 준비자산을 갖출" [cite: 5] | 원화 스테이블코인 준비자산의 상응 자산 범위를 현금, 예금, 만기 93일 이하 단기 채권으로 제시하는 직접적 법제화 기준이 됨 [cite: 1, 5]. | https://www.nars.go.kr/fileDownload2.do?doc_id=1Phhetmq4PP&fileName= [cite: 5] |
| 디지털 시대의 화폐, 혁신과 신뢰의 조화<br>(한국은행, 2025.10.27) | 보고서 본문 [cite: 19] | "원화 스테이블코인이 발행된다면 은행이 중심이 되어야 함... 은행이 발행 등 주도적 역할을 책임지고 수행하는 은행권 중심의 컨소시엄을 통해 발행을 추진한다면... 현행 규제 체계에서 관리될 수 있음" [cite: 19] | 원화 스테이블코인 발행 주체를 은행 중심 컨소시엄으로 제한하고 준비자산을 은행 시스템 내부에서 안전하게 관리하도록 유도함 [cite: 2, 3, 19]. | https://eiec.kdi.re.kr/policy/domesticView.do?ac=0000199493 [cite: 19] |

---

## 6. 결론 및 원화 스테이블코인 준비금 공시 제언

본 연구 분석 결과, 원화 스테이블코인 준비금 공시 제도를 정립하기 위해 당국과 국회는 다음과 같은 네 가지 핵심 공시 및 규제 기준을 확립해야 한다.

첫째, 준비자산 포트폴리오의 잔존만기 및 적격성 제약: 준비자산은 현금, 한국은행 및 A- 이상 신용등급 시중은행의 예치금, 만기 93일 이하의 국채·통안채로 제한하고 [cite: 5, 15], 포트폴리오 가중평균 잔존만기를 3개월 이내로 유지하도록 공시 기준에 명시해야 한다 [cite: 15].

둘째, 제3자 독립 신탁 및 베이시스 리스크 공시: 준비자산의 100% 이상을 제3의 독립된 수탁기관에 신탁하도록 하고 [cite: 1, 3], 최근 12개월간 발생한 페그 이탈 횟수 및 최대 이탈 폭을 공시하도록 의무화하여 베이시스 리스크 시험 결과를 명확히 드러내야 한다 [cite: 15].

셋째, 실시간 온체인 잔액 매핑 공시: 준비자산의 정기적 제3자 회계감사 보고서 제출과 더불어, 블록체인상 발행된 코인 잔액과 수탁기관의 준비자산 잔액이 일치함을 증명하는 온체인 대사 공시 체계를 정착시켜야 한다 [cite: 1, 12, 16].

넷째, 은행 건전성 규제 정합성 확보: 은행이 스테이블코인 발행 또는 준비자산 보관에 참여할 경우, 해당 암호자산 익스포저가 HQLA로 인정되지 않고 높은 LCR 유출률 및 Tier 1 자본 대비 1% 한도 규제를 받음을 감안하여 [cite: 10, 14], 자본 적정성을 해치지 않는 건전성 구조를 사전 검증해야 한다 [cite: 13, 14].

---

- 가상자산 2단계 입법 속도…대선 앞두고 코인투자자 표심 경쟁 - 연합뉴스, https://www.yna.co.kr/view/AKR20250426055100002

- 스테이블코인 논쟁에 멈춘 가상자산 2단계 입법 - 한국보험신문, https://www.insnews.co.kr/news/articleView.html?idxno=88833

- 원화 스테이블코인, 제도권 진입?...정부·은행·플랫폼 '삼각구도' 본격화 - 조세일보, https://m.joseilbo.com/news/view.htm?newsid=560538

- 금융안정보고서 (2025년 6월) - 국가전략포털, https://nsp.nanet.go.kr/plan/subject/detail.do?nationalPlanControlNo=PLAN0000053645

- 스테이블코인 제도화, 무엇에 집중할 것인가 - 국회입법조사처, https://www.nars.go.kr/fileDownload2.do?doc_id=1Phhetmq4PP&fileName=

- 스테이블코인의 도입과 이용자 보호 - 자본시장연구원, https://www.kcmi.re.kr/publications/pub_detail_view?syear=2025&zcd=002001016&zno=1867&cno=6604

- Compliance Digest—August 2025 - Sumsub, https://sumsub.com/media/news/compliance-digest-august-2025/

- Bank Capital Standards for Cryptoasset Exposures Under the Basel Framework | Insights | Skadden, Arps, Slate, Meagher & Flom LLP, https://www.skadden.com/insights/publications/2024/08/bank-capital-standards-for-cryptoasset

- CBDCs, regulated stablecoins and tokenized traditional assets under the Basel Committee rules on cryptoassets - Emerald Publishing, https://www.emerald.com/jfrc/article/33/1/31/1243998/CBDCs-regulated-stablecoins-and-tokenized

- Cryptoasset exposures | Bank for International Settlements - the BIS, https://www.bis.org/committees/bcbs/basel-framework/standard/dis/55/inforce/2026-01-01/published/2024-07-17

- basel-framework.pdf - the BIS, https://www.bis.org/committees/bcbs/basel-framework/basel-framework.pdf

- Matthew Wholey, CFA Igor Glamazdin Anna Raab +1 202 505 3173 +1 301 605 4155 +1 847 648 6255 - PolicyPartner, https://policypartnerdc.com/wp-content/uploads/2024/07/Look-Ahead-Calendar-07.18.2024.pdf

- Capital and Liquidity Treatment of Crypto-asset Exposures (Banking) – Guideline (2027), https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/capital-liquidity-treatment-crypto-asset-exposures-banking-guideline-2027

- Guideline on capital and liquidity treatment of cryptoasset exposures - Autorité des marchés financiers, https://lautorite.qc.ca/fileadmin/lautorite/reglementation/lignes-directrices-assurance/2023-05-31_Ligne_directrice-LDEC-en.pdf

- Consultation Paper on the Prudential Treatment of Cryptoasset Exposures and Requirements for Additional Tier 1 and Tier 2 Capital Instruments for Banks - Monetary Authority of Singapore, https://www.mas.gov.sg/-/media/mas-media-library/publications/consultations/ppd/2025/consultation-on-the-prudential-treatment-of-cryptoassets-and-reqs-for-at1-and-t2-capital-instruments.pdf

- Basel Framework - Cryptoasset exposures | Bank for International Settlements, https://www.bis.org/committees/bcbs/basel-framework/standard/sco/60/inforce/2026-01-01/published/2024-07-17

- Proposed Guidelines on the regulatory capital and liquidity treatment of crypto asset exposures (Banking and Insurance) - Canadian Web3 Council, https://web3canada.ca/wp-content/uploads/2023/09/OSFI-Submission-September-20-2023.pdf

- Comments in Response to the Second Consultation on the Prudential Treatment of Cryptoasset Exposures The Global Financial Ma, https://www.icmagroup.org/assets/Joint-TA-response-to-BCBS-2nd-consultation-crypto-assets-30092022.pdf

- 디지털 시대의 화폐, 혁신과 신뢰의 조화 : 원화 스테이블코인의 주요 이슈와 대응방안 | 국내연구자료 | KDI 경제교육·정보센터, https://eiec.kdi.re.kr/policy/domesticView.do?ac=0000199493

- '스테이블코인, 돈이 될까?'...컨설팅 받고도 물음표 남긴 은행들 - 인베스트조선, https://www.investchosun.com/site/data/html_dir/2025/10/27/2025102780064.html

- BOK이슈해설 | 한국은행이 말하는 스테이블코인의 모든 것(A to Z), https://www.bok.or.kr/portal/bbs/B0000168/view.do?menuNo=200058&nttId=10094368

- BOK이슈해설ㅣ스테이블코인의 이해와 오해 | 영상보고서(상세) | 동영상 | 멀티콘텐츠 | 한국은행 홈페이지, https://www.bok.or.kr/portal/bbs/B0000168/view.do?menuNo=200058&nttId=10095130

## 참고 링크(보고서 끝 목록)

1. 가상자산 2단계 입법 속도…대선 앞두고 코인투자자 표심 경쟁 - 연합뉴스 https://www.yna.co.kr/view/AKR20250426055100002
2. 스테이블코인 논쟁에 멈춘 가상자산 2단계 입법 - 한국보험신문 https://www.insnews.co.kr/news/articleView.html?idxno=88833
3. 원화 스테이블코인, 제도권 진입?...정부·은행·플랫폼 '삼각구도' 본격화 - 조세일보 https://m.joseilbo.com/news/view.htm?newsid=560538
4. 금융안정보고서 (2025년 6월) - 국가전략포털 https://nsp.nanet.go.kr/plan/subject/detail.do?nationalPlanControlNo=PLAN0000053645
5. 스테이블코인 제도화, 무엇에 집중할 것인가 - 국회입법조사처 https://www.nars.go.kr/fileDownload2.do?doc_id=1Phhetmq4PP&fileName=
6. 스테이블코인의 도입과 이용자 보호 - 자본시장연구원 https://www.kcmi.re.kr/publications/pub_detail_view?syear=2025&zcd=002001016&zno=1867&cno=6604
7. Compliance Digest—August 2025 - Sumsub https://sumsub.com/media/news/compliance-digest-august-2025/
8. Bank Capital Standards for Cryptoasset Exposures Under the Basel Framework | Insights | Skadden, Arps, Slate, Meagher & Flom LLP https://www.skadden.com/insights/publications/2024/08/bank-capital-standards-for-cryptoasset
9. CBDCs, regulated stablecoins and tokenized traditional assets under the Basel Committee rules on cryptoassets - Emerald Publishing https://www.emerald.com/jfrc/article/33/1/31/1243998/CBDCs-regulated-stablecoins-and-tokenized
10. Cryptoasset exposures | Bank for International Settlements - the BIS https://www.bis.org/committees/bcbs/basel-framework/standard/dis/55/inforce/2026-01-01/published/2024-07-17
11. basel-framework.pdf - the BIS https://www.bis.org/committees/bcbs/basel-framework/basel-framework.pdf
12. Matthew Wholey, CFA Igor Glamazdin Anna Raab +1 202 505 3173 +1 301 605 4155 +1 847 648 6255 - PolicyPartner https://policypartnerdc.com/wp-content/uploads/2024/07/Look-Ahead-Calendar-07.18.2024.pdf
13. Capital and Liquidity Treatment of Crypto-asset Exposures (Banking) – Guideline (2027) https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/capital-liquidity-treatment-crypto-asset-exposures-banking-guideline-2027
14. Guideline on capital and liquidity treatment of cryptoasset exposures - Autorité des marchés financiers https://lautorite.qc.ca/fileadmin/lautorite/reglementation/lignes-directrices-assurance/2023-05-31_Ligne_directrice-LDEC-en.pdf
15. Consultation Paper on the Prudential Treatment of Cryptoasset Exposures and Requirements for Additional Tier 1 and Tier 2 Capital Instruments for Banks - Monetary Authority of Singapore https://www.mas.gov.sg/-/media/mas-media-library/publications/consultations/ppd/2025/consultation-on-the-prudential-treatment-of-cryptoassets-and-reqs-for-at1-and-t2-capital-instruments.pdf
16. Basel Framework - Cryptoasset exposures | Bank for International Settlements https://www.bis.org/committees/bcbs/basel-framework/standard/sco/60/inforce/2026-01-01/published/2024-07-17
17. Proposed Guidelines on the regulatory capital and liquidity treatment of crypto asset exposures (Banking and Insurance) - Canadian Web3 Council https://web3canada.ca/wp-content/uploads/2023/09/OSFI-Submission-September-20-2023.pdf
18. Comments in Response to the Second Consultation on the Prudential Treatment of Cryptoasset Exposures The Global Financial Ma https://www.icmagroup.org/assets/Joint-TA-response-to-BCBS-2nd-consultation-crypto-assets-30092022.pdf
19. 디지털 시대의 화폐, 혁신과 신뢰의 조화 : 원화 스테이블코인의 주요 이슈와 대응방안 | 국내연구자료 | KDI 경제교육·정보센터 https://eiec.kdi.re.kr/policy/domesticView.do?ac=0000199493
20. '스테이블코인, 돈이 될까?'...컨설팅 받고도 물음표 남긴 은행들 - 인베스트조선 https://www.investchosun.com/site/data/html_dir/2025/10/27/2025102780064.html
21. BOK이슈해설 | 한국은행이 말하는 스테이블코인의 모든 것(A to Z) https://www.bok.or.kr/portal/bbs/B0000168/view.do?menuNo=200058&nttId=10094368
22. BOK이슈해설ㅣ스테이블코인의 이해와 오해 | 영상보고서(상세) | 동영상 | 멀티콘텐츠 | 한국은행 홈페이지 https://www.bok.or.kr/portal/bbs/B0000168/view.do?menuNo=200058&nttId=10095130
