# D-2 공동 발행(컨소시엄)의 분담과 이탈 처리

- 노트북: https://notebook.google.com/notebook/1b01d074-fc33-40b1-8e56-4f506a17b3dd?authuser=1 (자동 제목 "대한민국 신탁법")
- 보고서 제목: 원화 스테이블코인 준비금 공시 및 자산 보호 체계 수립을 위한 법·제도적 비교 연구
- 소스 28종, 보고서 참고 링크 24개, 본문 15260자
- 실행 방식: Deep Research
- 수집: 2026-10-06 Aside repl, 원문 대조 전

---
# 원화 스테이블코인 준비금 공시 및 자산 보호 체계 수립을 위한 법·제도적 비교 연구

## 서론 및 연구 배경

글로벌 금융시장에서 달러 연동 스테이블코인을 중심으로 한 디지털 결제 인프라 확원이 급격히 진행됨에 따라, 국내에서도 원화 기반 스테이블코인(KRW Stablecoin)의 제도화 필요성이 강하게 제기되고 있다 [cite: 1, 2]. 미국은 2025년 5월 스테이블코인 연방 규제법안인 지니어스법(GENIUS Act)을 입법화하여 2026년 1월 시행을 앞두고 있으며 [cite: 1, 2], 유럽연합(EU) 또한 가상자산시장법(MiCA)을 통해 전자화폐토큰(EMT) 및 자산참조토큰(ART)의 발행과 준비자산 관리를 엄격히 규율하기 시작했다 [cite: 3]. 이러한 주요국의 선제적 입법은 가상자산을 투기의 대상에서 제도권 결제 및 정산 수단으로 전환하는 세계적 흐름을 반영한다 [cite: 2].

국내의 경우 원화 스테이블코인 도입을 둘러싸고 통화 주권 확립, 소상공인 결제 수수료 경감, K-콘텐츠 및 수출기업의 국경 간 결제 효율화라는 긍정적 기대와 [cite: 2], 통화정책 유효성 약화 및 금융 시스템 불안정성에 대한 우려가 상충하고 있다 [cite: 4, 5]. 현재 대한민국 국회 정무위원회에는 원화 스테이블코인의 규율 체계를 포함한 총 9건의 제정 법률안이 계류되어 있다 [cite: 4].

이와 함께 금융위원회, 한국은행 등 정책 당국과 정치권, 시중은행 및 핀테크 업계 간에는 스테이블코인의 발행 주체를 은행 중심으로 제한할 것인지, 아니면 민간 기술기업에 개방할 것인지에 대한 거버넌스 논쟁이 치열하게 전개되고 있다 [cite: 2, 5, 6]. 원화 스테이블코인이 국가 통화질서와 금융 시스템의 안정을 해치지 않으면서 혁신을 달성하기 위해서는 고도의 준비금 공시 기준, 수탁 기관 집중 위험 관리, 파산 절연(Bankruptcy Remoteness)을 포함한 이용자 자산 보호 장치가 정교하게 설계되어야 한다 [cite: 2, 7].

## 국회 계류 9개 제정안의 준비금 요건 및 공시·수탁 기준 산정 근거 비교

국회 정무위원회에 발의되어 소관위 심사 단계에 있는 9건의 제정안은 스테이블코인을 가치안정형, 가치고정형, 또는 디지털자산의 일종으로 정의하고 발행 자격, 준비자산 운용 요건, 공시 의무를 각기 다르게 규정하고 있다 [cite: 4, 8, 9, 10, 11, 12].

각 법안이 제시하는 숫자와 기준의 세부 내역은 다음과 같다.

민병덕 의원안(의안번호 2210736, 대표발의일 2025년 6월 11일, 디지털자산기본법안)은 국내 법인에 대해 최소 자기자본금 5억원 이상을 충족할 경우 스테이블코인 발행 자격을 부여하는 민간 개방형 모델을 제시하고 있다 [cite: 9, 13]. 해당 안은 준비자산을 통한 100% 환불 보장과 전산 안정성 확보를 의무화하며, 대통령 직속 디지털자산위원회를 신설하고 민간위원이 전체 위원의 3분의 2 이상이 되도록 구성하여 산업 육성과 감독의 균형을 도모한다 [cite: 2, 13].

김은혜 의원안(의안번호 2211777, 대표발의일 2025년 7월 28일, 가치고정형디지털자산을활용한지급혁신에관한법률안)은 용어를 '가치고정형 디지털자산'으로 정의하고 결제 혁신에 주력한다 [cite: 8, 11]. 안도걸 의원안과 달리 예비인가 제도나 이자 지급 금지 조항을 별도로 포함하지 않는 특성을 보인다 [cite: 11].

안도걸 의원안(의안번호 2211784, 대표발의일 2025년 7월 28일, 가치안정형 디지털자산의 발행 및 유통에 관한 법률안)은 금융위원회의 사전 인가를 필수 요건으로 정하고 발행자 자격을 금융기관 또는 상법상 주식회사(외국법인 포함)로 규정한다 [cite: 11, 14]. 지급준비금은 현금, 요구불예금, 잔존만기 1년 이내의 국채 및 지방채로 100% 보유해야 하며 발행자의 고유자산과 엄격히 분리 관리하도록 법제화했다 [cite: 11, 14].

김현정 의원안(의안번호 2212298, 대표발의일 2025년 7월 28일, 가치안정형 디지털자산 발행업 등에 관한 법률안)은 스테이블코인의 준비금 100% 적립을 명시하고, 이용자의 상환 청구권 보장 및 준비자산의 안전한 관리를 위한 세부 기준을 수립하고 있다 [cite: 4, 11, 15].

이강일 의원안(의안번호 2213166, 대표발의일 2025년 9월 22일, 디지털자산시장의혁신과성장에관한법률안), 김재섭 의원안(의안번호 2213266, 대표발의일 2025년 9월 25일, 디지털자산통합법안), 최보윤 의원안(의안번호 2213449, 대표발의일 2025년 10월 1일, 디지털자산육성기본법안), 박상혁 의원안(의안번호 2214492, 대표발의일 2025년 11월 24일, 디지털자산의시장및산업에관한법률안)은 해외 주요국의 규제 틀을 적극 반영하여 공시 의무, 준비금 독립 관리, 불공정거래행위 감독체계를 통합적으로 규율한다 [cite: 4, 10].

김성원 의원안(의안번호 2218219, 대표발의일 2026년 4월 9일, 가상자산기본법안)은 기존 특정금융정보법상의 가상자산사업자 신고제를 넘어 가상자산 시장 전반과 스테이블코인 발행자의 준비금 적립 및 수탁 의무를 포괄적으로 감독하는 법적 기반을 제공한다 [cite: 12, 16].

| 의안번호 | 대표발의자 | 제안일자 | 법률안명 | 주요 준비금 요건 및 발행 자격 기준 | 주체 및 수탁·공시 규정 |
|---|---|---|---|---|---|
| 2210736 | 민병덕 | 2025-06-11 | 디지털자산기본법안 | 국내 법인 자기자본 5억원 이상 [cite: 13], 준비금 100% 환불 보장 [cite: 13] | 민간 개방형, 대통령 직속 위원회(민간위원 2/3 이상) 설치 [cite: 2, 9, 13] |
| 2211777 | 김은혜 | 2025-07-28 | 가치고정형디지털자산을활용한지급혁신에관한법률안 | 지급 혁신 목적 설정 [cite: 8, 11], 이자지급 금지 조항 미포함 [cite: 11] | 가치고정형 디지털자산 발행자 규제 [cite: 8, 11] |
| 2211784 | 안도걸 | 2025-07-28 | 가치안정형 디지털자산의 발행 및 유통에 관한 법률안 | 현금·요구불예금·만기 1년 이내 국지채 100% 보유 [cite: 14] | 금융위 사전 인가, 금융기관 또는 상법상 주식회사 [cite: 14] |
| 2212298 | 김현정 | 2025-07-28 | 가치안정형 디지털자산 발행업 등에 관한 법률안 | 준비금 100% 적립 및 이용자 상환 안전망 구축 [cite: 11, 15] | 가치안정형 발행업자 사전 인가 및 감독 [cite: 4, 11] |
| 2213166 | 이강일 | 2025-09-22 | 디지털자산시장의혁신과성장에관한법률안 | 해외 주요국 정합성 반영, 준비금 공시 의무화 [cite: 4] | 시장 감독 및 불공정거래 규제 체계 정립 [cite: 4] |
| 2213266 | 김재섭 | 2025-09-25 | 디지털자산통합법안 | 통합적 자산 공시 및 준비자산 수탁 기준 [cite: 4, 10] | 통합 법률 체계에 따른 금융당국 감독 [cite: 4, 10] |
| 2213449 | 최보윤 | 2025-10-01 | 디지털자산육성기본법안 | 산업 육성 및 수탁 자산 안전성 확보 [cite: 4] | 육성 기본법상 규제 및 감독 체계 [cite: 4] |
| 2214492 | 박상혁 | 2025-11-24 | 디지털자산의시장및산업에관한법률안 | 준비자산 독립 관리 및 불공정거래 감독 [cite: 4] | 시장 및 산업 전반 규율 체계 [cite: 4] |
| 2218219 | 김성원 | 2026-04-09 | 가상자산기본법안 | 특금법 신고제 확장, 준비금 보관 및 관리 [cite: 12, 16] | 포괄적 가상자산 및 발행자 감독 [cite: 12, 16] |

## 국내 원화 스테이블코인 컨소시엄 구조 및 지분·수탁 관계

원화 스테이블코인 발행을 둘러싼 국내 정책 논의의 핵심 축은 '발행 권한을 누구에게 부여할 것인가'와 '발행 컨소시엄의 거버넌스를 어떻게 구성할 것인가'에 집중되어 있다 [cite: 2, 5, 6].

금융위원회와 한국은행은 통화 주권 확립과 지급결제 시스템의 안정을 이유로 은행권 중심의 발행 체계를 선호하고 있다 [cite: 4, 5]. 당국은 스테이블코인 발행 주체를 '은행이 과반 지분(50%+1주)을 보유한 컨소시엄'으로 제한하는 방안을 검토해 왔다 [cite: 6]. 이는 비은행 기업이 화폐 발행과 지급결제망을 독점할 경우 발생할 수 있는 시스템적 리스크를 차단하고, 기존 외환 관리 및 통화신용정책의 유효성을 유지하기 위한 조치이다 [cite: 4, 5]. 정부안 구상에 따르면 최소 자기자본은 전자화폐 발행업 수준인 50억원가량으로 설정되며, 한국은행과 금융위 등이 속한 관계 기관 협의체를 통해 총발행량을 관리하는 방식이다 [cite: 5].

반면 국회 디지털자산 TF(민병덕, 안도걸, 이강일, 김현정 의원 등)와 핀테크 업계는 '은행 50%+1주' 지분 요건이 글로벌 표준에 역행하고 민간의 기술 혁신을 가로막는 과도한 규제라고 비판한다 [cite: 2, 5]. 은행에 과반 지분을 강제할 경우 ICT 및 핀테크 기업은 단순한 기술 하청업체로 전락하게 되며, 미국 서클(USDC)이나 테더(USDT)와 같은 자본시장 기반의 글로벌 결제 혁신 모델이 탄생할 수 없다는 지적이다 [cite: 2, 5]. 민간 개방형 모델론자들은 발행 주체를 민간 기업에 열어주되, 발행된 스테이블코인의 준비자산을 100% 외부 시중은행에 예치·신탁하게 하면 한국은행이 실시간으로 통화량을 추적할 수 있어 안정성과 혁신성을 동시에 달성할 수 있다고 주장한다 [cite: 2, 5].

제도화 흐름에 맞추어 시중은행들은 직접 발행 외에도 글로벌 수탁은행 및 대형 플랫폼사와의 연합 체계를 모색하고 있다 [cite: 6, 17]. KB국민은행은 글로벌 최대 수탁은행 중 하나인 BNY메론과 디지털자산 결제 협력을 맺고, 카카오그룹과 스테이블코인 생태계 구축을 위한 실무 논의를 시작하였다 [cite: 17]. KB국민은행은 직접 발행의 위험을 떠안기보다 결제·송금 인프라, 준비자산 수탁 관리, 자금세탁방지(AML) 및 이상거래탐지(FTS) 시스템을 선점하는 전략을 취하고 있다 [cite: 17]. 신한은행 또한 디지털자산 셀(Cell)을 구성하여 원화 스테이블코인의 1:1 환급 구조, 준비자산의 질과 유동성 관리, 거버넌스 체계 구축 등 구체적인 리스크 관리 프레임워크를 설계하고 있다 [cite: 6].

## 참여사 이탈·파산 시 이용자 자산 보호의 법적 메커니즘

발행사가 준비자산을 자체 장부에 보유하지 않고 수탁기관(은행 또는 신탁회사)에 신탁하는 구조를 취할 때 신탁법 및 관련 금융법에 따른 도산격리(Bankruptcy Remoteness) 메커니즘이 발동한다 [cite: 2, 7, 18]. 이용자 자산 보호는 신탁재산의 독립성, 수탁자의 파산절연, 예금자보호법상 보장 한도의 세 가지 측면에서 정교하게 다루어진다.

첫째, 신탁법상 신탁재산의 독립성 원칙에 따라 신탁재산은 위탁자인 발행사 및 수탁자인 은행의 고유재산과 완전히 분리된다 [cite: 18]. 따라서 수탁자나 발행사가 파산하더라도 신탁재산은 파산재단(Insolvency estate)을 구성하지 않는다 [cite: 18]. 강제집행, 가압류, 가처분, 경매 등도 금지되며, 신탁회사는 스테이블코인의 준비자산을 제3자에게 담보로 제공할 수 없다 [cite: 18]. 이러한 법적 장치는 수탁 기관이나 발행사의 부실이 스테이블코인 보유자의 채권 상환으로 전이되지 않도록 차단한다 [cite: 7].

둘째, 공동수탁(Joint Custody) 구조를 채택할 경우 단일 수탁기관의 신용 위험 노출을 다변화할 수 있다. 발행사가 준비자산을 복수의 시중은행에 분산 신탁할 때, 특정 은행이 파산하더라도 남아있는 수탁기관들을 통해 스테이블코인의 상환 유동성을 지속적으로 확보할 수 있다.

셋째, 예금자보호법의 적용 한도 및 통과보호(Pass-Through Protection) 이슈이다. 준비자산이 은행의 예금 형태로 보관될 경우 현행 예금자보호법상 보호 한도는 예금자 1인당 최고 5,000만원으로 제한된다. 스테이블코인 발행사가 이용자 자금을 집합하여 발행사 단일 명의 계좌(Omnibus Account)로 예치하면 예금보험공사는 이를 발행사 1인의 예금으로 간주하여 계좌 전체에 대해 5,000만원 한도만 적용할 위험이 존재한다. 따라서 준비자산 예치금에 대한 실효적 보호를 위해서는 예금 명의자가 발행사라 할지라도 실질 소유자인 스테이블코인 이용자 개별로 예금보험 한도가 분산 적용되는 통과보호 규정이 법률 제정안에 명시되어야 한다.

## 해외 주요국의 복수 발행 및 준비자산 수탁 집중 한도 규제

세계 주요국은 스테이블코인의 100% 준비자산 적립, 제3자 수탁 분리, 특정 수탁기관으로의 과도한 리스크 집중을 방지하기 위한 집중 한도를 입법화하였다 [cite: 2, 3, 19].

유럽연합(EU)의 MiCA(Markets in Crypto-Assets) 규정은 전자화폐토큰(EMT) 및 자산참조토큰(ART) 발행에 대해 엄격한 기준을 적용한다 [cite: 3]. EMT는 오직 CRD IV/V에 따라 승인된 신용기관(Credit Institution) 또는 전자화폐지침(EMD2)에 따른 전자화폐기관(EMI)만 발행할 수 있다(Article 48) [cite: 3, 20]. 동일한 규격의 토큰이라 하더라도 각기 승인받은 복수의 EMI 또는 은행이 독립적인 발행 주체로서 참여할 수 있으며, 이 경우 각 발행자는 개별적으로 준비자산 분리 보관 및 자기자본 요건을 준수해야 한다 [cite: 3, 20].

MiCA의 준비자산 예치 비율 및 집중 한도(Concentration Limits) 규정은 매우 구체적이다. 일반 EMT 발행자는 준비자산의 최소 30%를 신용기관의 예금으로 예치해야 하며, EBA에 의해 '지정 토큰(Significant EMT)'으로 분류될 경우 신용기관 예치 의무 비율은 최소 60%로 상향된다 [cite: 3, 19, 21]. 나머지 준비자산은 잔존만기 3개월(지정 토큰은 1개월) 이내의 고유동성 자산, 즉 0% 위험가중치가 적용되는 EU 회원국의 단기 국채 및 MMF로만 운용할 수 있다 [cite: 3, 19]. 단일 신용기관에 대한 예치금 집중 한도는 전체 준비자산의 10%, 동일 금융그룹 합산 시 30%로 제한된다 [cite: 3, 19, 21]. EBA의 세부 기술표준(RTS)안에 따라 글로벌 시스템적 중요 은행(G-SII)이나 기타 시스템적 중요 은행(O-SII)에는 최대 25%까지 예치가 허용되나, 일반 대형 은행은 15%, 중소형 은행은 5%로 엄격히 제한된다 [cite: 19]. 또한 자기자본 버퍼로서 최소 350,000 유로 또는 직전 연도 평균 준비자산의 2%(지정 토큰은 3%) 중 큰 금액을 적립해야 한다 [cite: 3, 20, 22].

미국은 2025년 5월 지니어스법(GENIUS Act)을 입법화하여 2026년 1월 시행을 앞두고 있다 [cite: 1, 2]. 지니어스법은 발행사에 100% 준비금 보유, 투명한 외부 감사 및 실시간 공시를 의무화하며 [cite: 2], 준비자산을 현금, 요구불예금, 90일 이내 단기 미 국채 등으로 엄격히 제한하여 달러 패권을 디지털 영역으로 확충하고 있다 [cite: 2, 14].

홍콩 입법회는 2025년 5월 21일 법정화폐 기반 스테이블코인 발행업체 규제 법안을 통과시켰다 [cite: 23]. 홍콩 달러 등에 연동되는 스테이블코인 발행사에 사전 허가제, 준비자산 완전 담보 및 리스크 관리 체계 준수를 강제함으로써 디지털 금융 혁신과 시장 안정성을 동시에 도모하고 있다 [cite: 23].

## 종합 사례 및 제도 비교표

다음 표는 국내외 스테이블코인 사례, 제도, 입법안 및 수탁 메커니즘을 종합 정리한 자료이다. 원문에서 확증되지 않은 항목은 '확인 안 됨'으로 표기하였으며, 기사 출처인 경우 명확히 기재하였다.

| 사례 또는 제도 | 구조 | 참여사 분담과 책임 | 이탈과 파산 시 처리 | 원문 인용 | 주소 |
|---|---|---|---|---|---|
| EU MiCA (전자화폐토큰 EMT 규제) | 신용기관(은행) 및 전자화폐기관(EMI) 발행 허용. 일반 EMT는 준비자산의 최소 30%, 지정(Significant) EMT는 최소 60%를 은행 예금으로 보유 [cite: 3, 19, 21]. | 발행사: 1:1 무조건 상환권 보장 및 자기자본(최소 350,000 유로 또는 준비자산의 2~3%) 유지 [cite: 3]. 수탁은행: 단일 은행 예치 한도 10%~25%, 동일 그룹 30% 제한 준수 [cite: 3, 19]. | 준비자산은 발행사 파산재단과 분리(ring-fenced)되어 보유자 상환에 최우선 사용(제47조) [cite: 3]. 수탁자 파산 시 엄격 무과실 책임 적용 [cite: 24]. | "At least 30% of the reserve must be held as deposits at credit institutions for non-significant EMTs, rising to 60% for significant EMTs." "Article 47 establishes that... reserve assets are ring-fenced" [cite: 3] | European Commission / EBA, Regulation (EU) 2023/1114 (MiCA) Art 36, 47, 48, https://eco.com/support/en/articles/14796310-mica-reserve-and-authorization-rules [cite: 3] |
| 미국 GENIUS Act (지니어스법) | 2025년 5월 미 상·하원 가결 및 발효, 2026년 1월 시행 예정인 연방 규제 체계 [cite: 1, 2]. | 발행사에 100% 준비금 보유, 투명한 외부 감사 및 실시간 공시 의무 부과 [cite: 2]. 준비금은 현금, 요구불예금, 단기 국채로 제한 [cite: 2, 14]. | 확인 안 됨 | "지니어스법은... 발행사에 100% 준비금 보유와 투명한 외부 감사를 의무화함으로써 시장의 신뢰를 못 박는 동시에..." [cite: 2] | 포춘코리아, "스테이블코인 도입과 민생", 2026.05, https://www.fortunekorea.co.kr/news/articleView.html?idxno=52823 (기사) [cite: 2] |
| 홍콩 스테이블코인 법안 | 홍콩 입법회 통과 법안 (2025.05.21). 법정화폐 연동 스테이블코인 발행업체 규제 [cite: 23]. | 발행업체에 대한 사전 허가제, 준비자산 완전 담보 및 리스크 관리 의무 부여 [cite: 23]. | 확인 안 됨 | "...법정화폐 기반의 스테이블코인 법안 통과(홍콩 입법회, 2025.05.21.)" [cite: 23] | 여의도연구원, 전 세계 스테이블코인 제도화 동향 보고서, 2025.06, https://www.ydi.or.kr/board/download/1098 [cite: 23] |
| 정부·금융당국 검토안 (국내 은행 중심 모델) | 은행이 과반 지분(50%+1주)을 보유한 컨소시엄 구조. 발행사 최소 자기자본금 50억원 수준 검토 [cite: 5, 6]. | 은행: 결제안정성, 통화 정책 유효성 및 준비자산 관리 주도 [cite: 4, 5, 6]. 기술기업: 기술 제공 및 최대주주 참여 가능 [cite: 5]. | 확인 안 됨 | "정부와 여권이 스테이블코인 발행 주체를 은행이 과반 지분(50%+1주)을 보유한 컨소시엄으로 제한하는 방안을 검토하면서..." [cite: 6] | 바이트라인, "신한은행 디지털자산 셀장 인터뷰", 2026.02.26, https://byline.network/2026/02/0226-2/ (기사) [cite: 6] |
| KB국민은행-BNY메론-카카오 생태계 연합 | 은행 중심 결제·수탁 인프라 선점 구조 [cite: 17]. | KB국민은행: 수탁, 준비자산 관리, AML/FTS 담당 [cite: 17]. BNY메론/카카오: 글로벌 결제 연동 및 플랫폼 생태계 구축 [cite: 17]. | 확인 안 됨 | "KB국민은행이 글로벌 수탁은행 BNY와 디지털자산 결제 협력에 나선 데 이어 카카오그룹과도 관련 생태계 구축 논의를 시작했습니다." [cite: 17] | 경인방송, "KB국민은행 디지털 결제 협력", 2026.02, https://news.ifm.kr/news/articleView.html?idxno=480869 (기사) [cite: 17] |
| 국회 안도걸의원안 (2211784) | 금융위원회 사전 인가제, 100% 가치안정형 스테이블코인 법률안 (2025.07.28) [cite: 11, 14]. | 금융기관 또는 상법상 주식회사 발행 [cite: 14]. 현금·요구불예금·만기 1년 이내 국지채 100% 보유 및 분리 관리 [cite: 11, 14]. | 확인 안 됨 | "법률안에 따르면 스테이블코인을 발행하려는 발행자는 금융위원회의 사전 인가를 받아야 한다... 지급준비금은 현금·요구불예금·잔존만기 1년 이내 국채·지방채." [cite: 14] | 연합인포맥스, "안도걸 의원 스테이블코인 법안 발의", 2025.07.28, https://news.einfomax.co.kr/news/articleView.html?idxno=4366778 (기사) [cite: 14] |
| 국회 민병덕의원안 (2210736) | 원화 스테이블코인 민간 발행 허용 및 디지털자산위원회 신설 법안 (2025.06.11) [cite: 2, 9]. | 법인 자격 요건(최소 자기자본금 5억원 이상) [cite: 13]. 준비자산 분리 보관 및 실시간 공시 연계 [cite: 2, 13]. | 확인 안 됨 | "한국 법인이라면 5억원 이상의 자기자본금을 충족하면 스테이블코인을 발행할 수 있습니다. 전산안정성을 높이고 준비금을 통해 환불을 보장..." [cite: 13] | 뉴스토마토, "민병덕 디지털자산기본법 대표발의", 2025.06.11, https://www.newstomato.com/ReadNews.aspx?no=1264596 (기사) [cite: 13] |
| 신탁법상 준비자산 수탁 구조 (제도적 장치) | 발행사가 준비자산을 수탁회사(은행)에 신탁하여 분리 보관하는 구조 [cite: 2, 18]. | 수탁자: 신탁재산 독립성 유지 및 담보 제공 금지 의무 [cite: 18]. 위탁자: 고유자산과 신탁자산의 분리 관리. | 수탁자 파산 시 신탁재산은 파산재단 미산입. 위탁자 및 수탁자의 채권자에 의한 강제집행 금지. | "아울러 신탁회사는 스테이블코인의 준비자산을 담보로 제공할 수 없다." [cite: 18] | 법무부, 가상자산 관련 신탁법 및 이용자 보호 보고서, 2024, p.66, https://www.moj.go.kr/bbs/moj/166/471409/download.do [cite: 18] |

## 결론 및 정책적 제언

본 연구 분석 결과, 원화 스테이블코인 준비금 공시 및 이용자 보호 체계 구축을 위해서는 금융 안정성과 민간 혁신의 균형을 확보할 수 있는 다층적 규제 설계가 필수적이다 [cite: 2, 4, 5].

첫째, 발행 자격의 유연화와 수탁 규제의 엄격화 조화가 요구된다. 정부의 '은행 50%+1주' 과반 지분 강제안은 민간의 혁신 역량을 위축시킬 우려가 존재한다 [cite: 5]. EU MiCA 모델과 유사하게 일정 자기자본(예: 50억원)과 전산 역량을 갖춘 민간 핀테크 법인에 발행 자격을 부여하되, 발행된 원화 스테이블코인의 준비자산은 100% 외부 시중은행에 예치·신탁하도록 의무화하는 방식이 바람직하다 [cite: 2, 3, 5].

둘째, 준비자산 수탁 기관의 집중 위험 제한(Concentration Limits) 도입이 필요하다. 준비자금이 특정 시중은행에 과도하게 쏠릴 경우 발생할 수 있는 시스템적 리스크를 예방하기 위해 EU MiCA 표준을 참조하여 단일 은행에 대한 예치 한도를 전체 준비자산의 25% 이내, 동일 금융그룹 합산 30% 이내로 제약하는 입법적 보완이 시급하다 [cite: 3, 19].

셋째, 법적 도산격리(Bankruptcy Remoteness) 및 실시간 공시 체계의 완비이다. 신탁법 제24조에 의거하여 발행사 및 수탁자의 파산 시에도 준비자산이 파산재단에 산입되지 않고 스테이블코인 보유자에게 최우선 변제되도록 명시해야 한다 [cite: 7, 18]. 아울러 예금자보호법상 통과보호(Pass-Through Protection) 특례를 명확히 정립하고, 온체인 발행량과 오프라인 예치금 간의 일일 대사(Daily Reconciliation) 및 실시간 검증 공시 시스템을 제도화해야 한다 [cite: 2, 3]. 이러한 종합적 제도 정비는 원화 스테이블코인이 국가 결제 시스템의 안정성을 유지하면서 글로벌 디지털 금융 영토를 확장하는 기두보가 될 것이다 [cite: 2].

---

- 與 "스테이블코인 시장 주도권 잡아야"…하반기 기본법 통과 추진 - 지디넷코리아, https://zdnet.co.kr/view/?no=20260821152355

- “스테이블코인, 금융공학 아닌 절박한 민생 해법입니다” [Polinomics] - 포춘코리아, https://www.fortunekorea.co.kr/news/articleView.html?idxno=52823

- MiCA Reserve and Authorization Rules | Support - Eco, https://eco.com/support/en/articles/14796310-mica-reserve-and-authorization-rules

- 스테이블코인 제도화, 무엇에 집중할 것인가 - 국회입법조사처, https://www.nars.go.kr/fileDownload2.do?doc_id=1Phhetmq4PP&fileName=

- [한국형 스테이블코인] 법안 발의 임박…당정 '금산분리' 쟁점, https://news.einfomax.co.kr/news/articleView.html?idxno=4393298

- [원화스테이블코인과 은행①] 신한은행이 그리는 스테이블코인 청사진 - 바이라인네트워크, https://byline.network/2026/02/0226-2/

- 금융위, 원화 스테이블코인 입법에 한은·재경부 참여 추진…관계기관 협의체 구성 - 블루밍비트, https://bloomingbit.io/feed/news/121201

- 가치고정형 디지털자산을 활용한 지급 혁신에 관한 법률안(김은혜의원 등 10인) - 열려라국회, https://watch.peoplepower21.org/BillDetail/2211777

- 디지털자산기본법안(민병덕의원 등 37인) - 열려라국회, https://watch.peoplepower21.org/BillDetail/2210736

- 디지털자산시장통합법안(김재섭의원 등 10인) - 열려라국회, https://watch.peoplepower21.org/BillDetail/2213266

- 스테이블코인(Stablecoin) 관련 국내 산업 동향 및 기술적 과제, https://www.kisa.or.kr/post/fileDownload?menuSeq=20202&postSeq=452&attachSeq=1&lang_type=KO

- 가상자산기본법안(김성원의원 등 10인) - 열려라국회, https://watch.peoplepower21.org/BillDetail/2218219

- 민병덕 의원, 디지털자산기본법 대표발의…스테이블코인 법제화 시동 - 뉴스토마토, https://www.newstomato.com/ReadNews.aspx?no=1264596

- 與안도걸, 스테이블코인 법안 발의…"실물자산 준비금 보유해야" - 연합인포맥스, https://news.einfomax.co.kr/news/articleView.html?idxno=4366778

- 한국도 '스테이블코인 제도화' 시대 열리나⋯안도걸 "내주 법안 발의" - 뉴스웍스, https://www.newsworks.co.kr/news/articleView.html?idxno=804622

- 가상자산기본법안 - 국회입법현황, https://opinion.lawmaking.go.kr/gcom/nsmLmSts/out/2218219/detailRP

- 원화 스테이블코인 시대, 선점 나선 KB국민은행…BNY·카카오와 '결제 인프라' 구축, https://news.ifm.kr/news/articleView.html?idxno=480869

- 우리나라의 스테이블코인 규제 방안에 관한 연구, https://www.moj.go.kr/bbs/moj/166/471409/download.do

- Final Report on Guidelines on liquidity stress testing under MiCAR - European Banking Authority, https://www.eba.europa.eu/sites/default/files/2024-06/2bd7add3-35b1-40d7-9c45-67c8cccbe97a/Final%20report%20on%20Guidelines%20on%20liquidity%20stress%20testing%20under%20MiCAR.pdf

- Money or MiCA's stablecoin hybrid and the direction of the 2026 review credit? - SUERF, https://www.suerf.org/publications/suerf-policy-notes-and-briefs/money-or-micas-stablecoin-hybrid-and-the-direction-of-the-2026-review-credit/

- EBA/RTS/2024/10 — Report — Reserve Asset Liquidity [final draft submitted] | mica.wtf, https://www.mica.wtf/mica-level-2-and-level-3/technical-standards/final-reports/rts-on-liquidity-requirements-of-reserve-of-assets

- Targeted Consultation on the review of the regulation on the markets in crypto-assets (MiCA) - AFME, https://www.afme.eu/media/pdppcjvm/20260930_afme-mica-consultation-response_final.pdf

- 디지털자산과 금융 질서의 균형:, https://www.ydi.or.kr/board/download/1098

- Digital Asset Protection – A first look at client asset rules under MiCA - Freshfields, https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/digital-asset-protection-a-first-look-at-client-asset-rules-under-mica-102hyzl

## 참고 링크(보고서 끝 목록)

1. 與 "스테이블코인 시장 주도권 잡아야"…하반기 기본법 통과 추진 - 지디넷코리아 https://zdnet.co.kr/view/?no=20260821152355
2. “스테이블코인, 금융공학 아닌 절박한 민생 해법입니다” [Polinomics] - 포춘코리아 https://www.fortunekorea.co.kr/news/articleView.html?idxno=52823
3. MiCA Reserve and Authorization Rules | Support - Eco https://eco.com/support/en/articles/14796310-mica-reserve-and-authorization-rules
4. 스테이블코인 제도화, 무엇에 집중할 것인가 - 국회입법조사처 https://www.nars.go.kr/fileDownload2.do?doc_id=1Phhetmq4PP&fileName=
5. [한국형 스테이블코인] 법안 발의 임박…당정 '금산분리' 쟁점 https://news.einfomax.co.kr/news/articleView.html?idxno=4393298
6. [원화스테이블코인과 은행①] 신한은행이 그리는 스테이블코인 청사진 - 바이라인네트워크 https://byline.network/2026/02/0226-2/
7. 금융위, 원화 스테이블코인 입법에 한은·재경부 참여 추진…관계기관 협의체 구성 - 블루밍비트 https://bloomingbit.io/feed/news/121201
8. 가치고정형 디지털자산을 활용한 지급 혁신에 관한 법률안(김은혜의원 등 10인) - 열려라국회 https://watch.peoplepower21.org/BillDetail/2211777
9. 디지털자산기본법안(민병덕의원 등 37인) - 열려라국회 https://watch.peoplepower21.org/BillDetail/2210736
10. 디지털자산시장통합법안(김재섭의원 등 10인) - 열려라국회 https://watch.peoplepower21.org/BillDetail/2213266
11. 스테이블코인(Stablecoin) 관련 국내 산업 동향 및 기술적 과제 https://www.kisa.or.kr/post/fileDownload?menuSeq=20202&postSeq=452&attachSeq=1&lang_type=KO
12. 가상자산기본법안(김성원의원 등 10인) - 열려라국회 https://watch.peoplepower21.org/BillDetail/2218219
13. 민병덕 의원, 디지털자산기본법 대표발의…스테이블코인 법제화 시동 - 뉴스토마토 https://www.newstomato.com/ReadNews.aspx?no=1264596
14. 與안도걸, 스테이블코인 법안 발의…"실물자산 준비금 보유해야" - 연합인포맥스 https://news.einfomax.co.kr/news/articleView.html?idxno=4366778
15. 한국도 '스테이블코인 제도화' 시대 열리나⋯안도걸 "내주 법안 발의" - 뉴스웍스 https://www.newsworks.co.kr/news/articleView.html?idxno=804622
16. 가상자산기본법안 - 국회입법현황 https://opinion.lawmaking.go.kr/gcom/nsmLmSts/out/2218219/detailRP
17. 원화 스테이블코인 시대, 선점 나선 KB국민은행…BNY·카카오와 '결제 인프라' 구축 https://news.ifm.kr/news/articleView.html?idxno=480869
18. 우리나라의 스테이블코인 규제 방안에 관한 연구 https://www.moj.go.kr/bbs/moj/166/471409/download.do
19. Final Report on Guidelines on liquidity stress testing under MiCAR - European Banking Authority https://www.eba.europa.eu/sites/default/files/2024-06/2bd7add3-35b1-40d7-9c45-67c8cccbe97a/Final%20report%20on%20Guidelines%20on%20liquidity%20stress%20testing%20under%20MiCAR.pdf
20. Money or MiCA's stablecoin hybrid and the direction of the 2026 review credit? - SUERF https://www.suerf.org/publications/suerf-policy-notes-and-briefs/money-or-micas-stablecoin-hybrid-and-the-direction-of-the-2026-review-credit/
21. EBA/RTS/2024/10 — Report — Reserve Asset Liquidity [final draft submitted] | mica.wtf https://www.mica.wtf/mica-level-2-and-level-3/technical-standards/final-reports/rts-on-liquidity-requirements-of-reserve-of-assets
22. Targeted Consultation on the review of the regulation on the markets in crypto-assets (MiCA) - AFME https://www.afme.eu/media/pdppcjvm/20260930_afme-mica-consultation-response_final.pdf
23. 디지털자산과 금융 질서의 균형: https://www.ydi.or.kr/board/download/1098
24. Digital Asset Protection – A first look at client asset rules under MiCA - Freshfields https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/digital-asset-protection-a-first-look-at-client-asset-rules-under-mica-102hyzl
