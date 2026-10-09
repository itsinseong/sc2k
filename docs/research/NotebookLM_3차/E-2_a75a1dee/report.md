# E-2 해외 규정에서 비어 있는 조항

- 노트북: https://notebook.google.com/notebook/a75a1dee-580a-4f37-956b-3c0efd02dde1?authuser=1 (자동 제목 "실리콘밸리은행 사태와 USDC 준비금 현황 보고")
- 보고서 제목: 원화 스테이블코인 준비금 공시 및 규제 체계 수립을 위한 비교 연구 보고서: 국내 발의 법안과 주요국(미국·EU·홍콩·싱가포르·일본) 법제 비교를
- 소스 28종, 보고서 참고 링크 29개, 본문 19594자
- 실행 방식: Deep Research
- 수집: 2026-10-06 Aside repl, 원문 대조 전

---
# 원화 스테이블코인 준비금 공시 및 규제 체계 수립을 위한 비교 연구 보고서: 국내 발의 법안과 주요국(미국·EU·홍콩·싱가포르·일본) 법제 비교를 중심으로

## 서론 및 국내 입법 동향 분석

디지털 자산 시장의 고도화와 함께 통화가치의 안정성을 보장하며 지급결제 수단으로 활용되는 스테이블코인(Stablecoin)의 제도화 논의가 전 세계 금융 규제 당국의 핵심 과제로 부상하였다 [cite: 1, 2, 3]. 국내에서도 중앙은행 디지털통화(CBDC)와의 상호운용성 확보 및 민간 자율 혁신 촉진, 그리고 이용자 자산 보호를 달성하기 위해 국회 정무위원회를 중심으로 원화 및 법정화폐 연동 스테이블코인의 발행·유통·준비자산 관리를 규율하는 9건의 제정법안이 발의되어 계류 중이다 [cite: 4, 5, 6].

국내 계류 법안들은 스테이블코인의 법적 성격 정의부터 시장 진입을 위한 최소 자기자본 요건, 보유자 상환 청구 시 이행 기한, 준비자산으로 인정되는 안전자산의 허용 범위, 정기 공시 및 외부 회계감사 주기 등 핵심 건전성 지표에서 상당한 정책적 시각차를 드러내고 있다 [cite: 5, 6, 7].

| 의안번호 및 제안자 | 법안명 | 주요 용어 정의 | 최소 자기자본 / 진입 규제 | 상환 기한 | 준비자산 허용 범위 | 공시 및 외부검사 주기 | 이자 지급 금지 여부 |
|---|---|---|---|---|---|---|---|
| 2210736 (민병덕 의원 등 37인, 2025.06.11.) [cite: 6, 7] | 디지털자산기본법안 [cite: 7] | 자산연동형 디지털자산 [cite: 6] | 5억 원 이상 (발행업 인가/등록) [cite: 6] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |
| 2211777 (김은혜 의원 대표발의, 2025.07.28.) [cite: 5] | 가치고정형 디지털자산을 활용한 지급 혁신에 관한 법률안 [cite: 5] | 가치고정형 디지털자산 [cite: 5] | 500억 원 이상 (금융위원회 인가) [cite: 5] | 10일 이내 [cite: 5] | 연동 통화 100% 상당 현금, 요구불예금 [cite: 5] | 매 분기 외부감사 [cite: 5] | 금지 [cite: 5] |
| 2211784 (안도걸 의원 대표발의, 2025.07.28.) [cite: 5] | 가치안정형 디지털자산의 발행 및 유통에 관한 법률안 [cite: 5] | 가치안정형 디지털자산 [cite: 5] | 500억 원 이상 (금융위원회 인가) [cite: 5] | 3영업일 이내 [cite: 5] | 미상환잔액 이상 현금 및 예금 등 안전자산 [cite: 5] | 매 분기 회계법인 검토, 매년 스트레스 테스트 [cite: 5] | 금지 [cite: 5] |
| 2212298 (김현정 의원 대표발의, 2025.08.21.) [cite: 4, 5] | 가치안정형 디지털자산 발행업 등에 관한 법률안 [cite: 4, 5] | 가치안정형 디지털자산 [cite: 5] | 확인 안 됨 (금융위원회 인가) [cite: 5] | 확인 안 됨 | 총 발행 금액 이상 현금, 국채, 지방채 등 [cite: 5] | 반기 외부감사 [cite: 5] | 확인 안 됨 |
| 2213166 (이강일 의원 등 11인, 2025.09.22.) [cite: 4, 6] | 디지털자산시장의 혁신과 성장에 관한 법률안 [cite: 4] | 가치안정형 디지털자산 [cite: 6] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |
| 2213266 (김재섭 의원 등 10인, 2025.09.25.) [cite: 4, 6] | 디지털자산통합법안 [cite: 4] | 고정가치형 디지털자산 [cite: 6] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |
| 2213449 (최보윤 의원 등 10인, 2025.10.01.) [cite: 4, 6] | 디지털자산육성기본법안 [cite: 4] | 가치연계형 디지털자산 [cite: 6] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |
| 2214492 (박상혁 의원 등 10인, 2025.10.23.) [cite: 4, 6] | 디지털자산의 시장 및 산업에 관한 법률안 [cite: 4] | 가치안정형 디지털자산 [cite: 6] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |
| 2218219 (김성원 의원 등 10인, 2026.04.09.) [cite: 8] | 가상자산기본법안 [cite: 8] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 |

국내 발의 법안들을 구체적으로 비교 분석하면, 진입 장벽과 운용 안전성 측면에서 명확한 스펙트럼이 형성되어 있음을 알 수 있다. 김은혜 의원안(2211777)과 안도걸 의원안(2211784)은 스테이블코인 발행 주체에게 500억 원 이상의 대규모 최소 자기자본 요건을 요구함으로써 부실 발행사의 시장 진입을 원천 차단하고 기존 금융회사 수준의 건전성을 확보하려는 기조를 보인다 [cite: 5]. 상환 기한의 경우 안도걸 의원안은 '3영업일 이내'의 신속한 상환을 의무화하는 반면, 김은혜 의원안은 '10일 이내'로 설정하여 유동성 충격 시 발행사의 조율 시한을 다소 넓게 보장하고 있다 [cite: 5].

준비자산 관리범위에 대해서도 김은혜 의원안은 연동 통화의 100% 상당을 오직 현금 및 요구불예금으로 제한하는 보수적 접근을 취하는 반면 [cite: 5], 안도걸 의원안과 김현정 의원안(2212298)은 국채, 지방채 등 고유동성 안전자산까지 인정함으로써 발행사의 수익성과 유동성 관리의 자율성을 부여하고 있다 [cite: 5]. 그러나 제휴 거래소나 관계사를 통한 이자 지급 우회 수단 차단, 예금보험 미적용 명시 규정, 준비자산 재담보 금지의 예외 조건 등 세부적인 운용 프레임워크에 대해서는 국내 법안 다수가 규정 공백 상태에 놓여 있어 해외 주요국의 선진 규제 체계에 대한 구체적 참조가 시급한 시점이다 [cite: 5, 9, 10, 11].

---

## 주요국 스테이블코인 핵심 규제 조항 심층 분석

### 1. 미국: GENIUS Act (Pub. L. 119-27) 및 연방 규제기관(OCC·FDIC·Fed) 시행규칙안

미국은 2025년 7월 18일 도널드 트럼프 대통령의 서명으로 '지급용 스테이블코인 국가지원 및 혁신 확립법(GENIUS Act, Pub. L. 119-27)'을 제정하며 가상자산 역사상 최초의 연방 차원 스테이블코인 규제 체계를 출범시켰다 [cite: 1, 12, 13, 14]. 이에 맞춰 통화감독청(OCC), 연방예금보험공사(FDIC), 연방준비제도이사회(FRB)는 각각 2026년 상반기 시행규칙안(NPRM)을 연방관보(Federal Register)에 공고하여 세부 집행 기준을 입법화하였다 [cite: 9, 10, 13, 14].

#### 가. 준비자산 재담보 금지(Rehypothecation Prohibition) 및 예외

GENIUS Act Section 4(a)(2) (12 U.S.C. § 5903(a)(2))는 승인된 지급용 스테이블코인 발행자(PPSI)가 고객의 상환권을 보장하기 위해 유지하는 준비자산에 대해 질권 설정(pledging), 재담보 제공(rehypothecation), 재사용(reuse) 행위를 전면 금지하고 있다 [cite: 11, 14, 15, 16]. 이는 암호화폐 생태계 내 레버리지의 과도한 누적과 준비자산의 이중 담보화를 차단하기 위한 목적이다 [cite: 16].

다만 연방준비제도이사회(FRB)의 시행규칙안(12 CFR § 247.10(c)(5)) 및 FDIC 시행규칙안(12 CFR § 350.3(b)(5))은 준비자산의 고유 유동성 운용을 지원하기 위해 명확한 예외 범위를 설정하였다 [cite: 14, 15]. 준비자산 자체의 법적 매입 대상인 잔존만기 93일 이하의 미국 단기국채(Treasury bills, notes, bonds) 보유 및 PPSI가 수취인으로 참여하는 환매조건부채권매입(Reverse Repurchase Agreements) 거래는 재담보 금지 조항의 구속을 받지 아니하며 정당한 준비자산 운용 형태로서 인정된다 [cite: 14].

#### 나. '연방예금보험 대상 아님(Not FDIC Insured)' 고지 문구 및 위치

GENIUS Act Section 4(a)(9) (12 U.S.C. § 5903(a)(9)) 및 미국 재무부 규칙안(31 CFR § 1521.4(h)(3))은 PPSI가 스테이블코인을 발행·마케팅할 때 연방정부의 보증이나 연방예금보험공사(FDIC)의 예금보험이 적용되는 안전 자산인 것처럼 오인시키는 기만적 명칭 및 표기 행위를 엄금한다 [cite: 1, 11, 17].

FDIC의 시행규칙안(12 CFR Part 330 및 Part 350, 91 FR 18534)은 통과예금보험(Pass-through deposit insurance)의 적용 가능성을 명확히 차단하였다 [cite: 10, 15, 18]. IDI(예금보험 가입 금융기관)에 예치된 스테이블코인 준비자산 예금은 오직 발행자(PPSI) 법인의 법인 예금으로서만 보호를 받을 뿐, 스테이블코인을 구매하여 보유하는 최종 이용자(Holders)에게 예금보험 한도가 통과되어 개별 적용되지 않는다 [cite: 10, 18]. 이에 따라 PPSI 및 모든 판매 중개업자는 제품 설명서, 백서, 고객 계약서, 마케팅 자료 및 모바일 애플리케이션의 유저 인터페이스(UI) 상에 "본 지급용 스테이블코인은 연방예금보험공사(FDIC)의 예금보험 대상이 아니며 미국 정부가 가치를 보증하지 않는다"는 경고 문구를 명시적으로 게시해야 한다 [cite: 1, 17].

#### 다. 이자 지급 금지 및 제휴사·거래소 리워드 우회 차단

GENIUS Act Section 4(a)(11) (12 U.S.C. § 5903(a)(11))은 PPSI 및 국외 승인 발행자가 스테이블코인의 보유, 사용, 유지 대가로 보유자에게 어떠한 형태의 이자(interest)나 수익률(yield)도 직접 지급하는 것을 전면 금지한다 [cite: 1, 9, 19].

규제 회피 수단을 차단하기 위해 OCC 시행규칙안(12 CFR § 15.13(a)(3)(i))과 FDIC 시행규칙안(12 CFR § 350.3(b)(4))은 '반박 가능한 추정(Rebuttable Presumption)' 규정을 규제 체계에 도입하였다 [cite: 9, 10, 13, 15]. 만약 PPSI가 자회사, 계열사(affiliate) 또는 제휴 가상자산 거래소 등 제3자와 계약을 체결하고, 해당 제3자가 스테이블코인 보유자에게 보유 기간이나 잔액에 비례하여 현금, 토큰, 수수료 감면 등 어떠한 형태든 경제적 대가를 지급하는 경우, 규제 당국은 이를 발행자가 이자 지급 금지 의무를 직접 위반한 것으로 법적 추정한다 [cite: 9, 10, 13].

단, 법안 Section 404는 스테이블코인의 순수한 보유 대가가 아닌, 실질적인 결제 및 거래 행위에 연동된 정당한 마케팅 리워드(Activity-based or transaction-based rewards and incentives, 예: 결제 이용 건당 캐시백, 신규 가입 이벤트)에 한해 이자 지급 금지 규제 대상에서 예외적으로 제외하도록 규정하고 있다 [cite: 18].

---

### 2. EU: MiCA (Regulation (EU) 2023/1114) 및 EBA 규제기술기준(RTS)

유럽연합은 2024년부터 전면 시행된 암호자산시장법(MiCA) 및 유럽은행감독청(EBA)의 규제기술기준(RTS)을 통해 전자화폐토큰(EMT)과 자산연동토큰(ART)의 건전성을 규율하고 있다 [cite: 20, 21].

#### 가. 중요 전자화폐토큰(Significant EMT) 지정 기준값

MiCA Article 56 및 57에 의거하여 EBA는 유럽 금융시스템 내 파급력이 큰 토큰을 '중요 전자화폐토큰(Significant EMT)' 또는 '중요 자산연동토큰(Significant ART)'으로 지정하며, 다음 5가지 수량적 기준 항목 중 최소 3개 이상을 충족할 때 지정이 이루어진다 [cite: 17, 20]:

- 이용자 수: 토큰을 보유한 순수 고객/보유자 수 10,000,000명(1,000만 명) 초과 [cite: 17, 20].

- 발행 규모 및 시가총액: 발행된 토큰의 총 시가총액 EUR 5,000,000,000(50억 유로) 초과 [cite: 17, 20].

- 일일 거래 건수: 일평균 지급결제 및 이체 거래 건수 2,500,000건(250만 건) 초과 [cite: 17, 20].

- 일일 거래 금액: 일평균 거래 총금액 EUR 500,000,000(5억 유로) 초과 [cite: 17, 20].

- 준비자산 규모: 발행자가 보유한 준비자산의 총평가액 EUR 5,000,000,000(50억 유로) 초과 [cite: 17, 20].

#### 나. 중요 토큰에 추가되는 유동성과 준비자산 요건

중요 EMT로 지정된 발행자는 일반 EMT 발행자에 비해 대폭 강화된 자본 및 유동성 규제를 받는다 [cite: 17]:

- 최소 자기자본 비율 상향: 자기자본 보유 의무 기준이 일반 발행자(준비자산 평균 잔액의 2%)에서 준비자산 평균 잔액의 3%로 1.5배 증액된다 [cite: 17].

- 신용기관 예치 비율 확대: 준비자산 중 시중 은행(신용기관) 요구불예금으로 즉시 현금화할 수 있게 예치해야 하는 최소 비율이 대폭 상향 설정되며, 단일 금융기관에 대한 준비자산 집중 위험 통제 기준이 강력히 적용된다 [cite: 17].

- 상시 유동성 스트레스 테스트: EBA의 감독 하에 정기적인 유동성 스트레스 테스트를 수행하고, 위기 상황 시 즉시 가동할 수 있는 회복 및 정리 계획(Recovery and Wind-down plans)을 매년 수립·보고해야 한다 [cite: 17, 20].

#### 다. 예금보증제도(DGS) 미적용 고지 의무

MiCA Article 48 및 Article 51에 따라 EMT 발행자 및 암호자산서비스제공자(CASP)는 이용자에게 해당 토큰이 EU 예금보증지침(Directive 2014/49/EU)에 따른 예금보증제도(Deposit Guarantee Schemes, DGS)의 보호 대상이 아니라는 사실을 명확히 공시해야 한다 [cite: 17, 20]. 발행자는 백서(Whitepaper)의 최상단 요약문 및 마케팅 매체에 "본 토큰은 예금이 아니며 예금보증제도의 보호를 받지 않는다"는 경고 문구를 필수로 포함해야 한다 [cite: 17, 20].

---

### 3. 아시아 주요국(홍콩·싱가포르·일본)의 예금보험 및 이자 지급 규제

#### 가. 홍콩 (Hong Kong)

홍콩금융관리국(HKMA)은 '스테이블코인 조례(Stablecoins Ordinance, Cap. 656)'(2025년 5월 21일 입법회 통과, 2025년 8월 1일 시행)를 수립하여 법정화폐 연동 스테이블코인(FRS) 라이선스 제도를 운영하고 있다 [cite: 2, 3, 22]. HKMA 가이드라인 및 조례에 따라 라이선스 취득 주체는 토큰 보유자에게 이자나 이자와 동등한 경제적 수익(interest-like incentives)을 지급하는 것이 금지된다 [cite: 20, 22, 23]. 또한 FRS는 홍콩 예금보호제도(Deposit Protection Scheme, DPS)에 따른 보호 대상 예금이 아니라는 사실을 고객 대상 설명서에 필수적으로 명시해야 한다 [cite: 17, 20].

#### 나. 싱가포르 (Singapore)

싱가포르통화청(MAS)은 지불서비스법(Payment Services Act 2019) 개정안(2026년 9월 1일 공개 입법협의안)을 통해 단일통화 스테이블코인(MAS-regulated SCS) 규제 프레임워크를 법제화하고 있다 [cite: 24, 25, 26]. MAS-SCS 발행자는 토큰 보유량이나 보유 기간에 비례하는 이자, 수익 환원, 기타 경제적 이익을 제공하는 것이 전면 금지된다 [cite: 27, 28]. 아울러 해당 스테이블코인은 싱가포르 예금보험제도(Singapore Deposit Insurance Scheme, SDIS)의 보호 대상이 아니며 가치 변동 위험이 존재한다는 사실을 디지털 자산 서비스 제공자(DPTS)가 리테일 고객에게 명확히 고지해야 한다 [cite: 25, 28].

#### 다. 일본 (Japan)

일본은 자금결제에 관한 법률(자금결제법) 개정을 통해 스테이블코인을 '전자결제수단(電子決済手段)'으로 포섭하여 규제하고 있다 [cite: 7, 29]. 자금결제법 및 금융청(FSA) 시행규칙에 따라 발행자 및 전자결제수단 거래업자가 토큰 보유자에게 직접 이자나 이율을 부여하는 이른바 '수익 환원형 스테이블코인' 발행 및 유통은 엄격히 금지된다 [cite: 29]. 또한 마케팅 과정에서 "일본 정부가 가치를 보증한다"거나 "예금보험공사(FDIC 등)의 예금보험 대상에 해당한다"는 오인을 유발하는 표시·광고 행위를 철저히 금지하고 있다 [cite: 29].

---

## 해외 주요국 규정 비교 총괄표

아래 표는 각 관할 구역의 1차 법령, 연방관보(Federal Register), 규제기관 공식 공고문 및 가이드라인에 규정된 핵심 조항 원문과 정량적 기준값을 체계적으로 비교·정정한 종합 자료다.

| 관할 | 문서와 조항 | 주제 | 요건 원문 | 값(비율, 금액, 일수) | 주소 |
|---|---|---|---|---|---|
| 미국 | GENIUS Act Sec. 4(a)(2) (12 U.S.C. § 5903(a)(2)) [cite: 11, 14, 16] | 준비자산 재담보 금지 [cite: 15, 16] | "prohibition on pledging, rehypothecating, or reusing reserve assets" [cite: 11, 14, 15, 16] | 재담보 허용 비율: 0% [cite: 11, 15, 16] | https://www.federalreserve.gov/newsevents/pressreleases/files/bcreg20260924a4.pdf [cite: 14] |
| 미국 | FRB Proposed 12 CFR § 247.10(c)(5) / FDIC Proposed 12 CFR § 350.3(b)(5) [cite: 14, 15] | 재담보 금지의 예외 (허용 준비자산) [cite: 14, 15] | "does not apply to reserve assets that are specifically permitted... Treasury bills, Treasury notes, or Treasury bonds with a remaining maturity of 93 days or less... money received under repurchase agreements" [cite: 14] | 국채 잔존만기: 93일 이하 [cite: 14] | https://www.federalreserve.gov/newsevents/pressreleases/files/bcreg20260924a4.pdf [cite: 14] |
| 미국 | GENIUS Act Sec. 4(a)(11) (12 U.S.C. § 5903(a)(11)) / OCC Proposed 12 CFR § 15.13(a)(3)(i) [cite: 1, 9, 13, 19] | 이자 지급 금지 및 관계사 우회 차단 [cite: 9, 13] | "prohibits permitted payment stablecoin issuers... from paying interest or yield in any form to the holder... OCC presumes that a permitted payment stablecoin issuer is paying interest or yield if the issuer has a contract/arrangement with an affiliate or related third party to pay interest to the holder" [cite: 1, 13] | 이자율: 0% (우회 구조 법적 추정 적용) [cite: 1, 9, 13] | https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-9a.pdf [cite: 13] |
| 미국 | FDIC Proposed 12 CFR Parts 330 & 350 (91 FR 18534, 2026.04.10) [cite: 10, 15] | 예금보험 미적용 (통과예금보험 불가) 고지 [cite: 10, 18] | "deposits held as reserves backing a payment stablecoin would be insured to the PPSI under corporate deposit rules, but would not be insured to payment stablecoin holders... not eligible for pass-through deposit insurance" [cite: 10, 18] | 개인 보유자 대상 통과예금보험 보증액: 0달러 [cite: 10, 18] | https://www.fdic.gov/board/federal-register-notice-genius-act-requirements-and-standards-fdic-supervised-permitted [cite: 10] |
| EU | MiCA (Regulation (EU) 2023/1114) Art. 56 [cite: 17, 20] | 중요 전자화폐토큰(Significant EMT) 지정 기준 [cite: 17, 20] | "number of holders is大于 10,000,000; value of tokens issued is大于 EUR 5,000,000,000; number of daily transactions is大于 2,500,000; value of daily transactions is大于 EUR 500,000,000" [cite: 17, 20] | 이용자 1,000만 명, 발행액 50억 유로, 일 거래 250만 건, 일 거래액 5억 유로 [cite: 17, 20] | https://www.globallegalinsights.com/practice-areas/blockchain-cryptocurrency-laws-and-regulations/stablecoin-use-cases-and-regulations/ [cite: 20] |
| EU | MiCA Art. 40, Art. 50, Art. 48 [cite: 20] | 이자 지급 금지 및 DGS 미적용 고지 [cite: 17, 20] | "prohibited from paying interest to holders of ARTs or EMTs... disclosures should make clear that EMTs/ARTs are not covered by deposit guarantee schemes under Directive 2014/49/EU" [cite: 17, 20] | 이자율: 0%, DGS 보증액: 0유로 [cite: 17, 20] | https://www.globallegalinsights.com/practice-areas/blockchain-cryptocurrency-laws-and-regulations/stablecoin-use-cases-and-regulations/ [cite: 20] |
| 홍콩 | Stablecoins Ordinance (Cap. 656) / HKMA Guidelines (2025.08.01 시행) [cite: 20, 22] | 이자 지급 금지 및 예금보호 미적용 고지 [cite: 17, 20, 22] | "Licensees are prohibited from paying interest or interest-like incentives in any form to stablecoin holders... disclosures should clarify FRS are not protected deposits under the Deposit Protection Scheme" [cite: 17, 20] | 이자율: 0%, DPS 보증액: 0홍콩달러 [cite: 17, 20] | https://academic.oup.com/tandt/article/31/9/447/8248855 [cite: 22] |
| 싱가포르 | Payment Services Act 개정안 (MAS 2026.09.01 Consultation) [cite: 24, 25, 26] | 이자 지급 금지, SDIS 미적용, 준비자산 비율 [cite: 27, 28] | "barred from paying interest, return, or any benefit tied to holding a stablecoin... not insured under Singapore Deposit Insurance Scheme... reserves equal to at least 100% of par value at all times" [cite: 27, 28] | 준비자산 유지 비율: 100% 이상, 이자율: 0% [cite: 27] | https://www.trmlabs.com/resources/blog/singapores-proposed-stablecoin-rules-what-the-issuers-exchanges-and-banks-need-to-know [cite: 27] |
| 일본 | 자금결제에 관한 법률(자금결제법) 전자결제수단 조항 [cite: 7, 29] | 이자 지급 금지 및 예금보험 미적용 오인 금지 [cite: 29] | "発行者自身による利払い（利息やイールドの付与）は禁止... FDIC保険や政府保証が付保されているといった誤解を招く表示の禁止" [cite: 29] | 이자율: 0%, 예금보험 보증액: 0엔 [cite: 29] | https://www.morihamada.com/ja/insights/newsletters/128971 [cite: 29] |

---

## 원화 스테이블코인 준비금 공시 및 제도적 설계에 대한 정책적 시사점

해외 주요국의 스테이블코인 입법 사례 분석은 향후 국회 정무위원회에서 통합 원화 스테이블코인 법안을 마련할 때 반영해야 할 입법적·정책적 시사점을 제공한다.

첫째, 준비자산 재담보 금지의 원칙적 입법화와 현실적인 예외 인정의 조화다. 미국 GENIUS Act 프레임워크가 보여주듯, 준비자산의 재담보 및 질권 설정은 0%로 엄격히 금지하되, 한국은행의 환매조건부채권(Repo) 매매 대상이 되는 잔존만기 90일 안팎의 초단기 대한민국 국채 매입이나 역RP 거래는 재담보 금지의 예외로 명확히 지정할 필요가 있다 [cite: 4, 14, 15]. 이를 통해 발행사의 유동성 경색 위험을 완화함과 동시에 단기 자금 시장과의 충격을 최소화할 수 있다 [cite: 4].

둘째, 가상자산 거래소 및 관계사를 통한 '이자 지급 우회 회피'에 대한 반박 가능한 추정(Rebuttable Presumption) 제도의 도입이다. 국내 가상자산 거래소 환경에서는 발행사가 이자를 직접 지급하지 않더라도, 제휴 거래소의 스테이킹이나 예치 상품 형태를 빌려 사실상의 이율을 제공하는 편법이 우려된다 [cite: 9, 13]. 미국 OCC 및 FDIC의 법제처럼 발행사와 계약 관계에 있는 제3자가 보유자에게 경제적 대가를 제공할 경우 이를 발행자의 직접적인 이자 지급으로 규정하는 강력한 법적 추정 장치를 마련해야 스테이블코인이 시중은행 예금을 대체하여 통화정책 유효성을 저해하는 부작용을 막을 수 있다 [cite: 4, 9, 13, 29].

셋째, 예금자보호법상 '통과 예금보험 불가' 규정의 명시적 공시다. 스테이블코인 준비자산이 예금보험 가입 금융기관에 요구불예금으로 예치되더라도, 예금보험 한도는 법인 발행사 1인에게만 적용될 뿐 각 개인 보유자에게 개별적으로 전달되지 않는다는 점을 명확히 해야 한다 [cite: 10, 18]. 따라서 모든 마케팅 매체, 가상자산 백서, 거래소 UI 상에 "원화 스테이블코인은 예금자보호법에 따른 예금보험 대상이 아니며 정부가 가치를 보증하지 않는다"는 문구를 표준화하여 표시하도록 의무화해야 한다 [cite: 1, 17, 29].

넷째, 발행 규모와 시장 파급력에 따른 차등적 공시 및 건전성 규제 체계 도입이다. EU MiCA의 중요 EMT 지정 기준(이용자 수, 발행액, 일일 거래액/건수)을 본받아 [cite: 17, 20], 일정 기준 이하의 중소형 스테이블코인 발행사에 대해서는 자율성을 부여하되, 일정 임계치를 초과하는 원화 스테이블코인에 대해서는 자기자본 비율 상향, 한국은행 및 금융감독원 대상 정기 스트레스 테스트 보고, 매월 외부 회계법인의 준비자산 검증 보고서 공시를 의무화하는 입법적 정교함이 요구된다 [cite: 5, 16, 17, 20].

---

- The GENIUS Act: A Framework for U.S. Stablecoin Issuance | Insights | Sidley Austin LLP, https://www.sidley.com/en/insights/newsupdates/2025/07/the-genius-act-a-framework-for-us-stablecoin-issuance

- PwC Global Crypto Regulation Report 2026, https://www.pwc.de/de/unterlagen/pwc-global-crypto-regulation-report-2026.pdf

- Global Crypto Policy Review Outlook 2025/26 Report - TRM Labs, https://www.trmlabs.com/reports-and-whitepapers/global-crypto-policy-review-outlook-2025-26

- 스테이블코인 제도화, 무엇에 집중할 것인가 - 국회입법조사처, https://www.nars.go.kr/fileDownload2.do?doc_id=1Phhetmq4PP&fileName=

- 국내 스테이블코인 관련 법률안의 주요 내용 및 시사점, https://www.draju.com/_wp/app/bbs/down.php?bsCode=m03&bsNo=6577&fileNum=1

- 가상자산 현물 ETF · 파생상품 제도화 관련 법안과 쟁점 - 법률신문, https://www.lawtimes.co.kr/news/articleView.html?idxno=214367

- 일본의 암호자산 규제 동향 - 자본시장연구원, https://www.kcmi.re.kr/common/downloadw?fid=28183&fgu=002001&fty=004003

- 가상자산기본법안(김성원의원 등 10인) - 열려라국회, https://watch.peoplepower21.org/BillDetail/2218219

- OCC Proposes Comprehensive Stablecoin Regulatory Framework to Implement the GENIUS Act - Gibson Dunn, https://www.gibsondunn.com/occ-proposes-comprehensive-stablecoin-regulatory-framework-to-implement-the-genius-act/

- Federal Register/Vol. 91, No. 69/Friday, April 10, 2026/Proposed Rules - FDIC, https://www.fdic.gov/board/federal-register-notice-genius-act-requirements-and-standards-fdic-supervised-permitted

- GENIUS Act Broad-Based Principles for Determining Whether a State-level Regulatory Regime Is Substantially Similar to the Federal Regulatory Framework - Regulations.gov, https://www.regulations.gov/document/TREAS-DO-2026-0232-0001

- The GENIUS Act of 2025 Stablecoin Legislation Adopted in the US - Latham & Watkins LLP, https://www.lw.com/en/insights/the-genius-act-of-2025-stablecoin-legislation-adopted-in-the-us

- Notice of proposed rulemaking: Implementing the Guiding and Establishing National Innovation for U.S. Stablecoins Act for the Is - OCC.gov, https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-9a.pdf

- Implementing the Federal Reserve Board's Responsibilities under the GENIUS Act, https://www.federalreserve.gov/newsevents/pressreleases/files/bcreg20260924a4.pdf

- GENIUS Act Requirements and Standards for FDIC-Supervised Permitted Payment Stablecoin Issuers and Insured Depository Institutions - Federal Register, https://www.federalregister.gov/documents/2026/04/10/2026-06974/genius-act-requirements-and-standards-for-fdic-supervised-permitted-payment-stablecoin-issuers-and

- GENIUS Act Ushers in Comprehensive Federal Regulation of Payment Stablecoins, https://www.paulweiss.com/insights/client-memos/genius-act-ushers-in-comprehensive-federal-regulation-of-payment-stablecoins

- Global Stablecoin Regulatory Playbook | HKDCA, https://www.hkdca.com/wp-content/uploads/2026/02/global-stablecoin-regulatory-playbook-gdf.pdf

- Digital Assets Recent Updates – April 2026 - Gibson Dunn, https://www.gibsondunn.com/digital-assets-recent-updates-april-2026/

- The GENIUS Act: A Comprehensive Guide to US Stablecoin Regulation | Paul Hastings LLP, https://www.paulhastings.com/insights/crypto-policy-tracker/the-genius-act-a-comprehensive-guide-to-us-stablecoin-regulation

- Stablecoin use cases and regulations - Global Legal Insights, https://www.globallegalinsights.com/practice-areas/blockchain-cryptocurrency-laws-and-regulations/stablecoin-use-cases-and-regulations/

- Thematic Review on FSB Global Regulatory Framework for Crypto-asset Activities: Peer review report - Financial Stability Board, https://www.fsb.org/uploads/P161025-1.pdf

- Trusts, trustees, and stablecoins: an analysis of Hong Kong's Stablecoins Ordinance and its implications for trust law - Oxford Academic, https://academic.oup.com/tandt/article/31/9/447/8248855

- Hong Kong Stablecoins Ordinance: the HKMA Issuer Licence, https://wiki.private.law/en/hk-stablecoin-ordinance

- MAS Charts the Next Phase of Stablecoin Regulation in Singapore | Insights - Sidley, https://www.sidley.com/en/insights/newsupdates/2026/09/mas-charts-the-next-phase-of-stablecoin-regulation-in-singapore

- Singapore's Stablecoin Regulatory Regime, https://www.simmons-simmons.com/en/publications/cmualdwdj006outc4asaud6cw/mas-proposed-amendments-to-the-payment-services-act

- MAS Consults on Legislative Amendments to Implement Stablecoin Regulatory Framework - Monetary Authority of Singapore, https://www.mas.gov.sg/news/media-releases/2026/mas-consults-on-legislative-amendments-to-implement-stablecoin-regulatory-framework

- Singapore's Proposed Stablecoin Rules: What the MAS Consultation Means for Issuers, Exchanges, and Banks | TRM Labs, https://www.trmlabs.com/resources/blog/singapores-proposed-stablecoin-rules-what-the-mas-consultation-means-for-issuers-exchanges-and-banks

- Response to Public Consultation on Proposed Regulatory Approach for Stablecoin-related Activities - Monetary Authority of Singapore, https://www.mas.gov.sg/-/media/mas-media-library/publications/consultations/pd/2023/response-to-consultation-on-stablecoins-regulation_15aug2023.pdf

- GENIUS法の成立と日系企業への影響, https://www.morihamada.com/ja/insights/newsletters/128971

## 참고 링크(보고서 끝 목록)

1. The GENIUS Act: A Framework for U.S. Stablecoin Issuance | Insights | Sidley Austin LLP https://www.sidley.com/en/insights/newsupdates/2025/07/the-genius-act-a-framework-for-us-stablecoin-issuance
2. PwC Global Crypto Regulation Report 2026 https://www.pwc.de/de/unterlagen/pwc-global-crypto-regulation-report-2026.pdf
3. Global Crypto Policy Review Outlook 2025/26 Report - TRM Labs https://www.trmlabs.com/reports-and-whitepapers/global-crypto-policy-review-outlook-2025-26
4. 스테이블코인 제도화, 무엇에 집중할 것인가 - 국회입법조사처 https://www.nars.go.kr/fileDownload2.do?doc_id=1Phhetmq4PP&fileName=
5. 국내 스테이블코인 관련 법률안의 주요 내용 및 시사점 https://www.draju.com/_wp/app/bbs/down.php?bsCode=m03&bsNo=6577&fileNum=1
6. 가상자산 현물 ETF · 파생상품 제도화 관련 법안과 쟁점 - 법률신문 https://www.lawtimes.co.kr/news/articleView.html?idxno=214367
7. 일본의 암호자산 규제 동향 - 자본시장연구원 https://www.kcmi.re.kr/common/downloadw?fid=28183&fgu=002001&fty=004003
8. 가상자산기본법안(김성원의원 등 10인) - 열려라국회 https://watch.peoplepower21.org/BillDetail/2218219
9. OCC Proposes Comprehensive Stablecoin Regulatory Framework to Implement the GENIUS Act - Gibson Dunn https://www.gibsondunn.com/occ-proposes-comprehensive-stablecoin-regulatory-framework-to-implement-the-genius-act/
10. Federal Register/Vol. 91, No. 69/Friday, April 10, 2026/Proposed Rules - FDIC https://www.fdic.gov/board/federal-register-notice-genius-act-requirements-and-standards-fdic-supervised-permitted
11. GENIUS Act Broad-Based Principles for Determining Whether a State-level Regulatory Regime Is Substantially Similar to the Federal Regulatory Framework - Regulations.gov https://www.regulations.gov/document/TREAS-DO-2026-0232-0001
12. The GENIUS Act of 2025 Stablecoin Legislation Adopted in the US - Latham & Watkins LLP https://www.lw.com/en/insights/the-genius-act-of-2025-stablecoin-legislation-adopted-in-the-us
13. Notice of proposed rulemaking: Implementing the Guiding and Establishing National Innovation for U.S. Stablecoins Act for the Is - OCC.gov https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-9a.pdf
14. Implementing the Federal Reserve Board's Responsibilities under the GENIUS Act https://www.federalreserve.gov/newsevents/pressreleases/files/bcreg20260924a4.pdf
15. GENIUS Act Requirements and Standards for FDIC-Supervised Permitted Payment Stablecoin Issuers and Insured Depository Institutions - Federal Register https://www.federalregister.gov/documents/2026/04/10/2026-06974/genius-act-requirements-and-standards-for-fdic-supervised-permitted-payment-stablecoin-issuers-and
16. GENIUS Act Ushers in Comprehensive Federal Regulation of Payment Stablecoins https://www.paulweiss.com/insights/client-memos/genius-act-ushers-in-comprehensive-federal-regulation-of-payment-stablecoins
17. Global Stablecoin Regulatory Playbook | HKDCA https://www.hkdca.com/wp-content/uploads/2026/02/global-stablecoin-regulatory-playbook-gdf.pdf
18. Digital Assets Recent Updates – April 2026 - Gibson Dunn https://www.gibsondunn.com/digital-assets-recent-updates-april-2026/
19. The GENIUS Act: A Comprehensive Guide to US Stablecoin Regulation | Paul Hastings LLP https://www.paulhastings.com/insights/crypto-policy-tracker/the-genius-act-a-comprehensive-guide-to-us-stablecoin-regulation
20. Stablecoin use cases and regulations - Global Legal Insights https://www.globallegalinsights.com/practice-areas/blockchain-cryptocurrency-laws-and-regulations/stablecoin-use-cases-and-regulations/
21. Thematic Review on FSB Global Regulatory Framework for Crypto-asset Activities: Peer review report - Financial Stability Board https://www.fsb.org/uploads/P161025-1.pdf
22. Trusts, trustees, and stablecoins: an analysis of Hong Kong's Stablecoins Ordinance and its implications for trust law - Oxford Academic https://academic.oup.com/tandt/article/31/9/447/8248855
23. Hong Kong Stablecoins Ordinance: the HKMA Issuer Licence https://wiki.private.law/en/hk-stablecoin-ordinance
24. MAS Charts the Next Phase of Stablecoin Regulation in Singapore | Insights - Sidley https://www.sidley.com/en/insights/newsupdates/2026/09/mas-charts-the-next-phase-of-stablecoin-regulation-in-singapore
25. Singapore's Stablecoin Regulatory Regime https://www.simmons-simmons.com/en/publications/cmualdwdj006outc4asaud6cw/mas-proposed-amendments-to-the-payment-services-act
26. MAS Consults on Legislative Amendments to Implement Stablecoin Regulatory Framework - Monetary Authority of Singapore https://www.mas.gov.sg/news/media-releases/2026/mas-consults-on-legislative-amendments-to-implement-stablecoin-regulatory-framework
27. Singapore's Proposed Stablecoin Rules: What the MAS Consultation Means for Issuers, Exchanges, and Banks | TRM Labs https://www.trmlabs.com/resources/blog/singapores-proposed-stablecoin-rules-what-the-mas-consultation-means-for-issuers-exchanges-and-banks
28. Response to Public Consultation on Proposed Regulatory Approach for Stablecoin-related Activities - Monetary Authority of Singapore https://www.mas.gov.sg/-/media/mas-media-library/publications/consultations/pd/2023/response-to-consultation-on-stablecoins-regulation_15aug2023.pdf
29. GENIUS法の成立と日系企業への影響 https://www.morihamada.com/ja/insights/newsletters/128971
