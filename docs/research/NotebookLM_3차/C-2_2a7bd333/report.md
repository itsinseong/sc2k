# C-2 레포(RP) 운용의 국내외 기준

- 노트북: https://notebook.google.com/notebook/2a7bd333-9ed4-4440-b8b5-130b8094fdae?authuser=1 (자동 제목 "가상자산 이용자 보호법 시행령 및 감독규정")
- 보고서 제목: 원화 스테이블코인 준비금 공시 기준 및 환매조건부매매(Repo) 규율 체계에 관한 연구 보고서
- 소스 46종, 보고서 참고 링크 40개, 본문 21504자
- 실행 방식: Deep Research
- 수집: 2026-10-06 Aside repl, 원문 대조 전

---
# 원화 스테이블코인 준비금 공시 기준 및 환매조건부매매(Repo) 규율 체계에 관한 연구 보고서

## 서론 및 연구 배경

디지털 금융 생태계에서 특정 법정화폐와 가치가 1:1로 연동되는 스테이블코인(Stablecoin)은 가상자산 시장의 거래 매개체를 넘어 온체인 지급결제 인프라의 핵심 축으로 부상하고 있다 [cite: 1]. 스테이블코인의 건전성과 신뢰성을 담보하는 법적·제도적 프레임워크의 본질은 발행잔액에 상응하는 고유동성 준비자산(Reserve Assets)의 1:1 완전 적립(Full Reserve Backing)과 이용자의 즉각적인 액면가 상환 청구권(Par Redemption On Demand)을 보장하는 데 있다 [cite: 2, 3, 4]. 스테이블코인 발행업자는 상환 요구에 신속하게 응하기 위해 높은 유동성을 유지해야 하며, 이 과정에서 일시적인 유동성 불일치를 해소하고 준비자산의 안전 운용을 기하기 위해 환매조건부매매(Repo 및 Reverse Repo, 이하 RP)를 주요 자금 조달 및 유동성 관리 수단으로 활용하게 된다 [cite: 5, 6, 7].

대한민국 역시 「가상자산 이용자 보호 등에 관한 법률」(가상자산이용자보호법) 시행 이후, 원화 연동 스테이블코인(KRW Stablecoin)의 제도화와 준비자산 규율을 골자로 하는 가상자산 2단계 입법 논의가 국회 정무위원회를 중심으로 활발히 전개되고 있다 [cite: 8, 9, 10, 11]. 원화 스테이블코인 준비금의 공시 기준과 운용 범위를 정립하기 위해서는 국회에 계류 중인 관련 제정법안들의 입법 취지와 수치적 기준을 정교하게 비교·분석하고, 국내 자본시장(MMF, 투자자예탁금, 가상자산 예치금)의 RP 운용 규제 및 국내 RP 시장의 실제 거래 구조를 참조해야 한다 [cite: 11, 12, 13]. 나아가 미국, 유럽연합(EU), 홍콩, 싱가포르, 일본 등 주요 관할 구역 규제 당국의 1차 법령과 감독 지침에서 정한 레포 운용 조건을 종합적으로 비교함으로써, 향후 도입될 원화 스테이블코인의 준비금 공시 체계 및 RP 운용 가이드라인 제정을 위한 법제적 시사점을 도출하고자 한다.

---

## 국회 계류 스테이블코인 제정법안 9건 비교 및 법적 근거

대한민국 국회 의안정보시스템에 따르면, 제22대 국회 정무위원회에는 원화 스테이블코인 및 가치고정형·가치안정형 디지털자산의 발행, 유통, 준비자산 적립 의무 및 감독 체계를 규율하기 위한 제정 법안 9건이 상정되어 심사 중에 있다 [cite: 8, 9, 10, 14]. 이들 법안은 가상자산 시장의 규제 공백을 해소하고 이용자 자산을 보호한다는 공통된 입법 목적을 공유하지만, 발행 주체의 자격 요건, 최소 자기자본, 이자 지급 금지 여부, 대규모 인출 사태(코인런) 발생 시 상환 지원 체계, 그리고 감독 권한의 기관별 배분 방식에서 뚜렷한 제도적 시각 차이를 보이고 있다 [cite: 9, 10, 15].

국회 정무위원회에 계류 중인 스테이블코인 관련 제정안 9건의 구체적 현황과 규제 수치 및 주요 내용을 비교한 결과는 아래 표와 같다.

| 의안번호 | 대표발의자 | 법안 명칭 | 발의 일자 | 최소 자기자본 요건 | 이자 지급 금지 여부 | 과징금 및 유동성 지원 / 감독 특기 사항 |
|---|---|---|---|---|---|---|
| 2210736 | 민병덕 | 디지털자산 기본법안 | 2025년 6월 10일 [cite: 9] | 5억 원 이상 [cite: 9] | 확인 안 됨 | 포괄적 디지털자산 인가·등록·신고 및 감독 체계 구축 [cite: 9] |
| 2211777 | 김은혜 | 가치고정형 디지털자산을 활용한 지급 혁신에 관한 법률안 | 2025년 7월 28일 [cite: 9] | 50억 원 이상 [cite: 9] | 금지 조항 없음 [cite: 9] | 과징금 상한 20억 원, 은행 및 주식회사·금융기관 등 비은행 발행 허용 [cite: 9] |
| 2211784 | 안도걸 | 가치안정형 디지털자산의 발행 및 유통에 관한 법률안 | 2025년 7월 28일 [cite: 9, 14] | 50억 원 이상 [cite: 9] | 이자 지급 엄격 금지 [cite: 9] | 과징금 상한 50억 원, 한은 공동검사 참여권 및 한은·기재부 긴급조치명령 요청권 규정 [cite: 9, 10] |
| 2212298 | 김현정 | 가치안정형 디지털자산 발행업 등에 관한 법률안 | 2025년 8월 21일 [cite: 14] | 50억 원 이상 [cite: 9] | 이자 지급 금지 포함 [cite: 9] | 코인런 발생 시 예금보험공사가 준비자산 담보로 상환자금 지원 [cite: 9] |
| 2213166 | 이강일 | 가상자산 이용자 보호 및 가치연동형 자산 규율에 관한 법률안 | 2025년 [cite: 8] | 확인 안 됨 | 확인 안 됨 | 준비자산 별도 예치·신탁 및 건전성 규제 명시 |
| 2213266 | 김재섭 | 디지털자산시장통합법안 | 2025년 [cite: 8, 15] | 확인 안 됨 | 확인 안 됨 | 분산된 가상자산 규율을 단일 통합 기본법으로 일원화 [cite: 15] |
| 2213449 | 최보윤 | 디지털자산 거래 안전성 확보 및 스테이블코인에 관한 법률안 | 2025년 [cite: 8] | 확인 안 됨 | 확인 안 됨 | 준비자산 공시 주기 및 시가평가 의무화, 이용자 우선변제권 확보 |
| 2214492 | 박상혁 | 디지털자산 공정거래 및 이용자 자산 보호에 관한 법률안 | 2025년 [cite: 8] | 확인 안 됨 | 확인 안 됨 | 준비자산 재담보 금지 및 손해배상 책임 강화 |
| 2218219 | 김성원 | 가치고정형 디지털자산의 발행 및 건전성 감독에 관한 법률안 | 2025년 [cite: 8] | 확인 안 됨 | 확인 안 됨 | 금융위원회 인가 중심의 발행업 규율 및 재무건전성 감독 |

국회 정무위원회 검토보고서 및 관련 정책 토론회 자료에 드러난 제정안들의 세부 진입 요건과 입법 논리를 살펴보면 다음과 같은 핵심 쟁점들이 확인된다 [cite: 9, 10, 16].

가장 대표적인 수치적 차이는 최소 자기자본 요건이다 [cite: 9]. 민병덕 의원안(2210736)은 초기 핀테크 진입 촉진과 시장 혁신을 도모하기 위해 진입 문턱을 5억 원으로 설정한 반면 [cite: 9], 김은혜 의원안(2211777), 안도걸 의원안(2211784), 김현정 의원안(2212298)은 발행업자의 재무적 충격 흡수 능력과 신동성 확보를 위해 자기자본 요건을 50억 원 이상으로 크게 상향 조정하였다 [cite: 9]. 이는 원화 스테이블코인이 시중 통화량과 지급결제 시스템에 미치는 파급력을 고려하여, 발행 주체를 금융기관 수준의 엄격한 건전성 감독 하에 두어야 한다는 자본시장연구원 및 당국의 정책적 논리를 반영한 결과이다 [cite: 9, 16].

둘째, 이용자 대상 이자(Yield) 지급 금지 조항의 유무이다 [cite: 9]. 안도걸 의원안 및 김현정 의원안 등 야당 발의안은 스테이블코인 보유에 따른 이자 지급을 엄격히 금지하고 있다 [cite: 9]. 이는 스테이블코인이 이자를 제공할 경우 일반 은행의 예금 자금이 가상자산 시장으로 대거 이탈하는 예금 탈루(Disintermediation) 현상을 방지하고, 통화정책의 전달 경로 왜곡을 차단하기 위함이다 [cite: 9]. 반면 김은혜 의원안은 이자 지급 금지 조항을 명시하지 않음으로써 지급 수단으로서의 자율적 경쟁과 사용자 유인을 허용하는 입장을 취하고 있다 [cite: 9].

셋째, 대규모 인출 충격에 대응하기 위한 유동성 방어 및 예금보험공사의 지원 메커니즘이다 [cite: 9]. 김현정 의원안(2212298)은 코인런 사태 시 발행사의 일시적 유동성 경색이 연쇄 도산으로 이어지는 것을 막기 위해, 예금보험공사가 발행업자의 고유동성 국공채 등 준비자산을 담보로 취득하고 상환자금을 일시 지원하는 법적 근거를 신설하였다 [cite: 9].

넷째, 한국은행 및 기획재정부의 감독 관여권 범위에 관한 기관 간 대립이다 [cite: 10]. 안도걸 의원안 등은 통화신용정책 및 외환시장 안정을 책임지는 한국은행에 스테이블코인 발행사에 대한 공동 검사 참여 요구권을 부여하고, 한국은행과 기획재정부에 금융위원회를 상동으로 한 긴급조치명령 요청권을 규정하였다 [cite: 10]. 이에 대해 금융위원회는 국회 정무위원회 검토보고서(작성자: 정명호 수석전문위원)를 통해 "한국은행 부총재와 기획재정부 차관이 이미 금융위원회의 당연직 위원으로 논의에 참여하고 있으므로 별도의 긴급조치명령 요청권이나 별도 협의기구를 두는 것은 합의제 행정기구인 금융위원회의 설립 목적 및 고유 의결 권한과 상충될 수 있다"며 명확한 반대 의사를 표명하였다 [cite: 10].

---

## 국내 금융·가상자산 제도의 RP 운용 규율 및 시장 구조

스테이블코인 준비자산의 RP 운용 기준을 구체화하기 위해서는 국내 자본시장 법령에서 초단기 유동성 자산을 관리하는 법적 기준인 단기금융집합투자기구(MMF), 투자자예탁금, 가상자산 이용자 예치금의 RP 규율 체계와 실제 국내 RP 시장의 거래 구조를 파악해야 한다 [cite: 11, 12, 13].

### MMF의 RP 매수·매도 규정

자본시장과 금융투자업에 관한 법률(자본시장법) 및 「금융투자업규정」은 MMF가 수시 입출금식 단기 금융상품으로서 원금 안전성과 즉각적인 환금성을 유지하도록 RP 거래의 방향에 따라 엄격히 차등화된 한도와 만기 규정을 적용하고 있다 [cite: 12, 17].

첫째, RP 매도(환매조건부매도) 한도의 경우, 「금융투자업규정」 제7-15조제1항에 따라 일반 집합투자기구(펀드)의 RP 매도 한도는 보유 증권 총액의 50% 이내로 설정되어 있으나, MMF의 RP 매도 한도는 각 집합투자기구 보유 증권총액의 5% 이내로 극히 제한된다 [cite: 12, 18]. 이는 MMF가 자금을 차입하기 위해 보유 채권을 담보로 제공하는 과도한 레버리지 행위를 차단함으로써 시장 변동성 확대 시 유동성 위험이 증폭되는 것을 막기 위한 조치이다 [cite: 12, 18].

둘째, RP 매수(환매조건부매수) 한도 및 만기의 경우, 「금융투자업규정」 제7-16조, 제7-19조 및 관련 운용 규정에 의거하여 MMF가 여유 자금을 운용하기 위해 자금을 대여하고 채권을 담보로 수취하는 RP 매수 거래는 남은 만기(잔존만기)의 제한을 받지 아니한다 [cite: 17, 19]. RP 매수 거래는 대상 증권의 만기가 길더라도 매매 계약 자체의 약정 기간이 익일물 등 극초단기로 설정되어 언제든 현금화가 가능하다고 간주되기 때문이다 [cite: 17, 19]. 다만, RP 매수 대상 증권이 국채증권, 정부보증채, 지방채, 특수채이며 금융감독원장이 정하는 최소증거금률(Haircut) 이상을 확보하는 경우에 한하여 유동성 규제상의 예외 및 혜택이 적용된다 [cite: 17].

### 투자자예탁금 및 가상자산 이용자 예치금의 RP 운용 허용 여부

타인의 자금을 보관·관리하는 금융 및 가상자산 예치금 제도에서도 RP 운용은 원금 보전과 유동성 확보를 동시에 달성하는 수단으로 정비되어 있다 [cite: 11, 13].

첫째, 투자자예탁금은 자본시장법 제74조(투자자예탁금의 별도 예치)에 의거하여 증권사 등 금융투자업자가 자기 재산과 분리하여 한국증권금융 등 예치기관에 예치하거나 신탁해야 한다 [cite: 13]. 투자자의 매수 주문 전 일시적으로 발생하는 유동성 자금은 당행 예수금 외에도 특정금전신탁(MMT), MMF, 및 은행 RP 등으로 운용하는 것이 법적으로 허용되어 있다 [cite: 13].

둘째, 가상자산 이용자 예치금은 「가상자산 이용자 보호 등에 관한 법률」 제5조 및 동법 시행령, 감독규정에 따라 가상자산사업자가 이용자의 예치금을 관리기관인 은행에 별도 예치·신탁하여야 한다 [cite: 11, 20, 21]. 예치금을 수탁받은 은행은 이용자 자산의 안전한 관리를 위해 국공채·지방채 등 단기 안전자산 매입 또는 환매조건부채권(RP) 매수 방식으로 예치금을 운용하여 수익을 창출하고 이를 이용자 예치금 이용료로 지급한다 [cite: 11, 20, 21, 22].

### 국내 RP 시장의 기간별 거래 비중 및 통계 공시 기관

국내 기관 간 RP 시장은 만기 구조 면에서 극단적인 초단기 쏠림 현상을 보인다.

첫째, 기간별 거래 비중에서 익일물(Overnight, 1일물) 거래 비중은 전체 기관 간 RP 거래량의 90% 이상을 차지한다. 기일물(2일 이상) RP 거래는 비중이 매우 낮으며, 시장 참여 기관들은 일별 유동성 조율 및 자금 수급을 위해 대부분 익일물 RP 매매를 활용한다.

둘째, 기관 간 RP 금리 및 거래 통계를 공식 공개하는 주 기관은 한국은행과 한국예탁결제원이다.

- 한국은행(Bank of Korea): 단기금융시장 보고서 및 경제통계시스템(ECOS)을 통해 RP 시장의 총 거래량과 참가자별 매동을 공시하며, 국내 무위험지표금리(KOFR, Korea Overnight Financing Rate)의 관리기관으로서 매 영업일 실적 기반 익일물 RP 금리를 공시한다.

- 한국예탁결제원(KSD): 증권정보포털(SEIBro)을 통해 일별·기간별 기관 간 RP 거래 규모, 참가자 유형별(증권, 자산운용, 은행, 보험 등) 매수·매도 잔액, 담보증권 종류별(국채, 특수채, 금융채, 회사채 등) 거래 실적 통계를 실시간으로 제공한다.

---

## 해외 주요 관할 구역의 스테이블코인 준비자산 레포(Repo) 규제 비교

글로벌 주요국 규제 당국은 스테이블코인 준비자산의 1:1 완전 적립 원칙을 유지하면서도, 유동성 관리와 상환 대응을 위해 레포(Repo / Reverse Repo) 거래의 허용 요건, 잔존만기, 담보 자산의 질, 재담보(Rehypothecation) 제한에 대해 정교한 규율 체계를 확립하고 있다 [cite: 3, 4, 6, 23, 24, 25].

### 미국: GENIUS Act 제4조 및 OCC 시행규칙안

미국은 2025년 7월 18일 연방 스테이블코인 법안인 GENIUS Act(Guarding Enforcement and Fostering Innovation for Unprecedented Stablecoin Act of 2025, 12 U.S.C. 5901 et seq.)를 제정하였다 [cite: 5, 6, 26].

GENIUS Act Section 4(a)(1)(A)에 따르면 연방 또는 주 감독기관의 인가를 받은 지급 스테이블코인 발행인(Permitted Payment Stablecoin Issuer, PPSI)은 발행 잔액에 대해 최소 1:1 비율로 적격 준비자산을 유지해야 한다 [cite: 3, 27]. 적격 준비자산에는 현금, 현금성 예금, 미국 만기 90일 이하 국채(T-bills)와 함께 **환매조건부채권 매매계약(Repurchase Agreements / Reverse Repos)**이 포함된다 [cite: 3, 6, 26, 27].

Section 4(a)(1)(A) 및 관련 규정상 레포 거래의 담보 자산은 미국 국채 또는 연방정부 보증 유가증권이어야 한다 [cite: 3, 5]. 거래 방식은 (i) 삼자간 레포(Tri-party repo), (ii) SEC에 등록된 증권청산소(CCP)를 통한 청산 거래, 또는 (iii) 심각한 시장 스트레스 상황에서도 충분한 신용도를 갖춘 것으로 발행인이 평가한 단일 상대방과의 양자간(Bilateral) 거래로 한정된다 [cite: 3].

재담보(Rehypothecation)와 관련하여, Section 4(a)(2)는 원칙적으로 고객 준비자산의 재담보 및 재사용을 엄격히 금지한다 [cite: 3, 27]. 그러나 Section 4(a)(2)(C)에 의거하여 이용자의 상환 요구에 부응하기 위한 유동성 창출(Create Liquidity) 목적의 레포 차입(Repurchase Borrowing)은 예외적으로 허용된다 [cite: 6, 27].

미국 통화감독청(OCC)이 발표한 시행규칙안(OCC Notice of Proposed Rulemaking, 12 CFR Part 15 / § 15.10(c)(5), nr-occ-2026-9a, 2026년 1월)에 따르면, 발행인이 상환 청구 대응을 위해 준비자산인 국채를 담보로 제공하고 유동성을 차입하는 레포 거래의 만기는 **익일물(Overnight)**이어야 함을 명시하고 있다 [cite: 6].

### 유럽연합(EU): MiCA 및 EBA 규제기술기준(RTS)

유럽연합은 암호자산시장법(MiCA, Regulation (EU) 2023/1114) 제36조 및 제38조와 유럽은행감독청(EBA)의 규제기술기준(RTS)을 통해 레포 운용을 규율한다 [cite: 7, 23, 28].

MiCA Article 38(1) 및 EBA RTS(EBA/RTS/2024/11)에 따라, 자산참조토큰(ART) 및 전자화폐토큰(EMT) 발행인은 **EU 회원국의 적격 국채(Eligible Sovereign Debt)를 담보로 하는 역레포 거래(Reverse Repurchase Agreements)**에 준비자산을 투자할 수 있다 [cite: 7, 23].

준비자산 포트폴리오의 만기 상한(가중평균만기, WAM)은 비중요 토큰의 경우 최대 3개월, 중요 토큰(Significant EMTs/ARTs)의 경우 최대 1개월을 초과할 수 없다 [cite: 23]. 또한 EBA RTS(EBA/RTS/2024/10 및 EBA/Op/2025/13)의 유동성 조건에 따라, 역레포 및 현금 자산 중 최소 **20%는 1영업일 전 해제 통보(1 working day notice)**로 회수 가능해야 하며, 최소 30%(중요 토큰의 경우 60%)는 5영업일 이내에 해제할 수 있는 구조여야 한다 [cite: 28, 29]. 더불어 비중요 EMT 발행인은 준비자산의 최소 30%, 중요 EMT 발행인은 최소 60%를 신용기관 예치금(Bank Deposits)으로 보유해야 하는 강제 예치 비율을 적용받는다 [cite: 23, 28, 29].

### 홍콩: 금융관리국(HKMA) 스테이블코인 발행인 감독 지침

홍콩 금융관리국(HKMA)은 2025년 5월 통과되어 8월 1일 시행된 스테이블코인 조례(Stablecoins Ordinance, Cap. 656) 및 감독 지침(Guideline on Supervision of Licensed Stablecoin Issuers, 2025년 8월)을 통해 레포 기준을 규정하였다 [cite: 24, 30, 31, 32].

HKMA 지침 Paragraph 2.2.7 및 Schedule 2 Section 5(5)에 따른 적격 준비자산은 현금, 잔존만기 3개월 이하의 은행 예금, 잔존만기 1년 이하의 고품질 정부/중앙은행 채권, 그리고 신용 리스크가 최소화된 익일물 역레포 거래(Overnight Reverse Repurchase Agreements)의 현금 수취 채권으로 한정된다 [cite: 24, 33, 34].

역레포 거래의 만기 상한은 **익일물(Overnight)**에 한한다 [cite: 24, 33, 34]. 담보로 제공되는 유가증권은 정부, 중앙은행, 공공기관 또는 다자개발은행(MDB)이 발행·보증한 잔존만기 1년 이하의 고신용 채권이어야 한다 [cite: 24, 34]. 준비자산은 법적 신탁(Statutory Trust) 구조로 발행인의 고유자산과 분리 보관되어야 하며 재담보는 엄격히 금지된다 [cite: 24, 25, 30].

### 싱가포르: 통화청(MAS) 단일통화 스테이블코인(SCS) 체계

싱가포르 통화청(MAS)은 2023년 8월 지불서비스법(Payment Services Act) 하에서 단일통화 스테이블코인(Single-Currency Stablecoin, SCS) 최종 규제 프레임워크를 확정하였다 [cite: 4, 25, 35, 36].

MAS 프레임워크상 준비자산은 현금, 현금성 자산, 및 **잔존만기 3개월 이하(Residual maturity ≤ 3 months)**의 고유동성 채권으로 제한된다 [cite: 4, 25, 36]. 채권 발행 주체는 싱가포르 정부, MAS, 또는 AA- 이상 신용등급을 보유한 다자개발기관으로 한정된다 [cite: 25, 36]. 3개월 잔존만기 제한 범위 내의 초단기 채권 및 현금성 자산 범주 내에서 레포 운용을 허용하며, 발행인의 상환 이행 기간은 최대 5영업일(T+5) 이내로 규정되어 있다 [cite: 25, 36, 37].

### 일본: 자금결제법 및 내각부령

일본은 2023년 6월 개정 자금결제법(Payment Services Act)을 시행하여 스테이블코인을 '전자지급수단'으로 정의하고 규율하고 있다 [cite: 4].

발행 주체는 은행, 신탁회사, 등록 자금이체업자로 제한되며 [cite: 4], 준비자산은 은행 예금 및 신탁자산(Trust Assets) 형태로 신탁회사에 예치되어야 한다 [cite: 4]. 신탁자산의 원본 보전 및 100% 액면가 상환 의무가 법적으로 강제되므로, 준비자산의 고위험 자산 투자 및 재담보는 원칙적으로 금지된다 [cite: 4]. 세부 내각부령상 별도의 레포 전문 조항은 명시되지 않았으며 신탁계약상의 예금 및 국채 보관 규칙을 준용한다 [cite: 4].

---

## 국내외 관할 구역별 레포(Repo) 허용 조건 비교

아래 표는 각 관할 구역별 법령 원문 및 공식 규제 규정에 나타난 스테이블코인 준비자산 및 자본시장 자산의 레포(Repo / Reverse Repo) 허용 조건, 만기 상한, 담보 조건, 원문 인용 및 출처 주소를 비교·요약한 결과이다.

| 관할 | 문서와 조항 | 레포 허용 여부 | 만기 상한 | 담보 조건 | 원문 인용 | 주소 |
|---|---|---|---|---|---|---|
| 미국 | US Congress / OCC, GENIUS Act § 4(a)(1)(A), § 4(a)(2)(C) / 12 CFR Part 15 § 15.10(c)(5) (2026.01) [cite: 6, 26, 27] | 허용 | 익일물 (Overnight) [cite: 6] | 미국 국채(T-bills) 및 연방정부 보증 유가증권. 삼자간, SEC 등록 CCP 청산, 우수 상대방과의 양자간 거래 [cite: 3, 5] | "the maturity of the repurchase agreement would be overnight... prohibit rehypothecation except for the purpose of creating liquidity to meet reasonable expectations of requests for redemption." [cite: 6] | https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-9a.pdf [cite: 6] |
| 유럽연합 | EU Parliament / EBA, MiCA (Regulation (EU) 2023/1114) Art. 38 / EBA RTS (EBA/RTS/2024/11, EBA/Op/2025/13) (2024.06) [cite: 7, 28, 29] | 허용 | WAM 3개월 이내(비중요) / 1개월 이내(중요). 1영업일(20%), 5영업일(30%~60%) 해제 조건 [cite: 23, 28, 29] | 적격 EU 회원국 국채(Eligible Sovereign Debt) 등 최소 시장·신용·집중 리스크 자산 [cite: 7, 23] | "Repo agreements collateralized by eligible sovereign debt. The weighted average maturity of the instrument portfolio cannot exceed three months for non-significant EMTs and one month for significant EMTs." [cite: 23] | https://www.mica.wtf/mica-level-2-and-level-3/technical-standards/final-reports/rts-on-highly-liquid-financial-instruments-in-reserve-assets [cite: 7] |
| 홍콩 | HKMA, Stablecoins Ordinance Schedule 2 § 5(5) / Guideline on Supervision of Licensed Stablecoin Issuers Para 2.2.7 (2025.08) [cite: 24, 30, 31] | 허용 | 익일물 (Overnight) [cite: 24, 33, 34] | 정부, 중앙은행, 공공기관, MDB 발행·보증 고신용 채권(잔존만기 1년 이하) [cite: 24, 34] | "cash receivable from overnight reverse repurchase agreements with minimal counterparty risk, collateralised by assets referred to under 2 above" [cite: 24] | https://www.hkma.gov.hk/media/eng/doc/key-functions/ifc/stablecoin-issuers/Guideline_on_supervision_of_licensed_stablecoin_issuers_eng.pdf [cite: 31] |
| 싱가포르 | MAS, Regulatory Framework for Single-Currency Stablecoins Annex C (2023.08) [cite: 25, 38] | 제한적 허용 | 잔존만기 3개월 이내 (Residual maturity ≤ 3 months) [cite: 25, 36] | 싱가포르 정부, 중앙은행(MAS) 또는 AA- 이상 신용등급 다자개발기관 발행 채권 [cite: 25, 36] | "Reserves must consist solely of low-risk, highly liquid assets such as cash, cash equivalents, or debt securities with a residual maturity of no more than three months, issued by the Singapore government, its central bank, or supranational entities rated AA- or higher." [cite: 25] | https://www.mas.gov.sg/-/media/mas-media-library/publications/consultations/pd/2023/15aug2023_annex--submissions-to-consult-paper-on-stablecoins.pdf [cite: 38] |
| 일본 | FSA Japan, Payment Services Act (자금결제법 개정안) 및 금융청 내각부령 (2023.06) [cite: 4] | 불허 또는 확인 안 됨 | 확인 안 됨 | 신탁자산(Trust Assets) 형태의 예금 및 국채 보관. 원본 보전 및 재담보 금지 [cite: 4] | "Only licensed banks, trust companies, or registered money transfer agents can issue stablecoins. Stablecoins must be redeemable at face value. Issuers must maintain full reserve backing." [cite: 4] | https://medium.com/@alexmilleraa/every-major-stablecoin-regulation-in-the-world-right-now-explained-in-plain-english-0d9cb5e3e2e3 [cite: 4] |
| 대한민국 (MMF) | 금융위원회, 금융투자업규정 제7-15조제1항, 제7-16조, 제7-19조 (2023 개정) [cite: 12, 17] | 허용 (매수 허용, 매도 5% 제한) [cite: 12, 18] | RP 매수의 경우 남은 만기 제한 없음 [cite: 17, 19] | 국채, 정부보증채, 지방채, 특수채 (최소증거금률 적용) [cite: 17] | "다만, 환매조건부매수의 경우에는 남은 만기의 제한을 받지 아니한다." / "(단, MMF의 한도는 5% - 금융투자업규정 제7-15조제1항)" [cite: 12, 17] | https://law.kofia.or.kr/service/law/lawFullScreenContent.do?seq=262&historySeq=755 [cite: 12] |

---

## 결론 및 원화 스테이블코인 준비금 공시 기준 제안

국회에 계류 중인 9건의 제정안 분석과 국내외 레포 규제 체계 비교를 종합하면, 향후 원화 스테이블코인 제도화 과정에서 준비자산의 안전성과 유동성을 동시에 확보하기 위한 구체적인 공시 및 운용 기준을 도출할 수 있다 [cite: 3, 6, 9, 24].

첫째, 국채 담보 기반 익일물 역레포(Overnight Reverse Repo)의 명시적 허용이다. 미국 GENIUS Act(및 OCC 시행규칙)와 홍콩 HKMA 감독 지침이 입증하듯이, 스테이블코인의 즉시 상환 청구권(Par Redemption On Demand)을 보장하기 위해서는 준비자산 중 현금 및 단기 국채 외에도 대한민국 국채(T-bonds/T-bills) 및 통화안정증권을 담보로 하는 익일물 역레포 매매를 적격 자산으로 명시해야 한다 [cite: 6, 24]. 국내 기관 간 RP 시장의 90% 이상이 익일물로 거래되는 구조적 특성을 감안할 때, 익일물 역레포 허용은 발행사의 유동성 방어 능력을 크게 증대시킬 것이다.

둘째, 원칙적 재담보(Rehypothecation) 금지 및 예외적 유동성 차입 인용이다. 발행업자가 수익 극대화를 위해 고객의 준비자산을 제3자에게 재담보로 제공하는 행위는 엄격히 금지되어야 한다 [cite: 3, 27]. 다만, 대규모 인출 사태(코인런) 발생 시 이용자 상환금을 즉시 지급하기 위해 보유 중인 국채를 담보로 자금을 차입하는 익일물 레포 거래(Repurchase Borrowing)는 미국 OCC 규정 및 김현정 의원안(2212298)의 취지에 따라 제한적으로 허용하는 것이 바람직하다 [cite: 6, 9].

셋째, 공시 주기 체계화 및 시가평가 의무화이다. 발행업자는 월 1회 이상 외부 독립 감사인의 정기 검인을 받아 준비자산의 세부 구성 내역(현금, 예금, 국채, RP 잔액, 가중평균만기 WAM, 수탁기관 위치)을 공시해야 한다 [cite: 3, 26, 27]. 나아가 매 영업일 기준으로 발행 잔액과 준비자산 시가평가액(Mark-to-Market)의 1:1 충족 여부를 자사 웹사이트에 공개하도록 의무화하여 정보 비대칭성을 해소해야 한다 [cite: 30].

넷째, 한국은행 무위험지표금리(KOFR) 및 예탁결제원 전산망 연동이다. 준비자산의 RP 운용 투명성을 확보하기 위해 한국예탁결제원의 RP 결제 시스템 및 한국은행의 KOFR 데이터베이스와 연동되는 공시 모니터링 프레임워크를 구축해야 한다. 이는 가상자산 2단계 입법 과정에서 금융위원회의 감독 권한과 한국은행의 지급결제망 안정성 확보 요구 사이의 정책적 상충을 완화하는 실효성 있는 대안이 될 것이다 [cite: 10].

---

- 디지털자산과 금융 질서의 균형:, https://www.ydi.or.kr/board/download/1098

- 스테이블코인 제도 도입과 이용자 보호 강화 방향, https://www.kcmi.re.kr/common/downloadw?fid=28554&fgu=002002&fty=004003

- The GENIUS Act: A Comprehensive Guide to US Stablecoin Regulation | Paul Hastings LLP, https://www.paulhastings.com/insights/crypto-policy-tracker/the-genius-act-a-comprehensive-guide-to-us-stablecoin-regulation

- Every Major Stablecoin Regulation in the World Right Now, Explained in Plain English | by Alex Miller | Medium, https://medium.com/@alexmilleraa/every-major-stablecoin-regulation-in-the-world-right-now-explained-in-plain-english-0d9cb5e3e2e3

- The GENIUS Act of 2025 Stablecoin Legislation Adopted in the US - Latham & Watkins LLP, https://www.lw.com/en/insights/the-genius-act-of-2025-stablecoin-legislation-adopted-in-the-us

- Notice of proposed rulemaking: Implementing the Guiding and Establishing National Innovation for U.S. Stablecoins Act for the Is - OCC.gov, https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-9a.pdf

- EBA/RTS/2024/11 — Report — Highly Liquid Reserve Assets [final draft submitted] | mica.wtf, https://www.mica.wtf/mica-level-2-and-level-3/technical-standards/final-reports/rts-on-highly-liquid-financial-instruments-in-reserve-assets

- 스테이블코인 꽃필까…빅테크도 게임업도 사업진출 공식화 - 머니투데이, https://www.mt.co.kr/tech/2025/09/09/2025090818040889628

- 스테이블코인 법제화 답보…국내 시장 잠식 우려 - DFT 대한금융신문, https://www.kbanker.co.kr/news/articleView.html?idxno=221364

- 금융위 “한은 스테이블코인 긴급조치 요청권 등 실익 적어“ - 연합뉴스TV, https://www.yonhapnewstv.co.kr/news/AKR202511251615382sL

- 전체 제정·개정이유 - 국가법령정보센터, https://law.go.kr/LSW/lsRvsRsnListP.do?lsId=001565&chrClsCd=010202&lsRvsGubun=all

- 금융투자회사의 컴플라이언스 매뉴얼 Ⅲ편(자산운용) | 규정내용, https://law.kofia.or.kr/service/law/lawFullScreenContent.do?seq=262&historySeq=755

- 투자자예탁금제도, https://www.imbank.co.kr/cms/dev/prv/prv_isa08.html

- 가상자산 분야 이슈리포트 - 국내 스테이블코인 관련 법률안의 주요 내용 및 시사점, https://www.draju.com/ko/sub/newsletters.html?type=view&bsNo=6577&langNo=

- 올해 발의된 디지털자산 법안만 8건…'산업 육성'vs'이용자 보호' 엇갈려 - ZDNet Korea, https://zdnet.co.kr/view/?no=20251230095852

- 與안도걸 스테이블코인 법안 내주 발의…통화·외환 파장도 예의주시 - 한국경제, https://www.hankyung.com/article/202507237786g

- 신 탁 계 약 서 - 하나UBS 신종MMF(S-29호), http://money2.daishin.com/E5_Data/service/www/Agree/Fund/2023/6/81801_KR5102AG6370_R1_20230602_%ED%95%98%EB%82%98UBS%EC%8B%A0%EC%A2%85MMF(S-29%ED%98%B8)ClassC.pdf

- 전체화면 | 모범규준 | 금융투자회사의 컴플라이언스 매뉴얼 Ⅲ편(자산운용), https://law.kofia.or.kr/service/law/lawFullScreen.do?seq=262&historySeq=756

- 투자설명서 - NH-Amundi자산운용, https://www.nh-amundi.com/upload/fund/PrdtDoc/MN040%ED%88%AC%EC%9E%90%EC%84%A4%EB%AA%85%EC%84%9C_NH-Amundi%20%EB%B2%95%EC%9D%B8%EC%9A%A9%20%EB%8B%AC%EB%9F%AC%20MMF%201%ED%98%B8(USD)_241227.pdf

- 부록, https://www.bok.or.kr/portal/cmmn/file/fileDown.do?atchFileId=e17a3e9a750b63d0a1722d25bbd52037&fileSn=4

- 수익 – 포커스온경제 통합 검색, https://foeconomy.co.kr/news/search.php?q=%EC%88%98%EC%9D%B5&var=page0&page0=54&page0=52

- 고객서비스 > 업무안내가이드 > 예탁금이용료율안내 - KB증권, https://www.kbsec.com/go.able?linkcd=m06030010

- MiCA Reserve and Authorization Rules | Support - Eco, https://eco.com/support/en/articles/14796310-mica-reserve-and-authorization-rules

- HKMA Consultations – Obligations of Licensed Stablecoin Issuers - Charltons Law, https://www.charltonslaw.com/hkma-consultations-on-obligations-of-hkma-licensed-stablecoin-issuers/

- Global approaches to stablecoin regulation | EY, https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/industries/banking-capital-markets/documents/ey-gl-global-stablecoin-regulation-comparison-09-2025.pdf

- GENIUS Act Implementation - Federal Register, https://www.federalregister.gov/documents/2025/09/19/2025-18226/genius-act-implementation

- The GENIUS Act: A New Era of Stablecoin Regulation - Gibson Dunn, https://www.gibsondunn.com/the-genius-act-a-new-era-of-stablecoin-regulation/

- EBA/RTS/2024/10 — Report — Reserve Asset Liquidity [final draft submitted] | mica.wtf, https://www.mica.wtf/mica-level-2-and-level-3/technical-standards/final-reports/rts-on-liquidity-requirements-of-reserve-of-assets

- EBA/Op/2025/13 — Opinion — Reserve Liquidity RTS [published] | headlesslaw - mica.wtf, https://www.mica.wtf/mica/level-3/opinions/eba-op-2025-13-amendments-rts-reserve-liquidity-requirements

- HKMA Issues Guideline on Supervision of Stablecoin Issuers | Legalink, https://www.legalink.net/xms/files/hkma-issues-guideline-on-supervision-of-stablecoin-issuers.pdf

- STABLECOINS ORDINANCE - Hong Kong Monetary Authority, https://www.hkma.gov.hk/media/eng/doc/key-functions/ifc/stablecoin-issuers/Guideline_on_supervision_of_licensed_stablecoin_issuers_eng.pdf

- Hong Kong Stablecoin Ordinance Takes Effect August 2025 | Morgan Lewis, https://www.morganlewis.com/pubs/2025/06/hong-kongs-stablecoins-ordinance-to-take-effect-august-1-an-overview-of-the-regulatory-framework

- Key Points and Challenges for Hong Kong Stablecoin Issuer License Applications, https://www.hankunlaw.com/en/portal/article/index/cid/8/id/15890.html

- Hong Kong announces Stablecoin Consultation Conclusions and Sandbox Participants amid Web3 push | Global Regulation Tomorrow, https://www.regulationtomorrow.com/2024/07/hong-kong-announces-stablecoin-consultation-conclusions-and-sandbox-participants-amid-web3-push/

- The Impact of Distributed Ledger Technology in Capital Markets, https://www.gfma.org/wp-content/uploads/2025/08/1.-full-report-impact-of-dlt-in-cap-mkts-final-1.pdf

- FCA and MAS stablecoin frameworks: a comparative view | Insights - UK Finance, https://www.ukfinance.org.uk/news-and-insight/blog/fca-and-mas-stablecoin-frameworks-comparative-view

- Overview of Stablecoin Regulation - Binance, https://www.binance.com/en/research/analysis/overview-of-global-stablecoin-regulation

- Annex B: List of Respondents - Monetary Authority of Singapore, https://www.mas.gov.sg/-/media/mas-media-library/publications/consultations/pd/2023/15aug2023_annex--submissions-to-consult-paper-on-stablecoins.pdf

## 참고 링크(보고서 끝 목록)

1. 디지털자산과 금융 질서의 균형: https://www.ydi.or.kr/board/download/1098
2. 스테이블코인 제도 도입과 이용자 보호 강화 방향 https://www.kcmi.re.kr/common/downloadw?fid=28554&fgu=002002&fty=004003
3. The GENIUS Act: A Comprehensive Guide to US Stablecoin Regulation | Paul Hastings LLP https://www.paulhastings.com/insights/crypto-policy-tracker/the-genius-act-a-comprehensive-guide-to-us-stablecoin-regulation
4. Every Major Stablecoin Regulation in the World Right Now, Explained in Plain English | by Alex Miller | Medium https://medium.com/@alexmilleraa/every-major-stablecoin-regulation-in-the-world-right-now-explained-in-plain-english-0d9cb5e3e2e3
5. The GENIUS Act of 2025 Stablecoin Legislation Adopted in the US - Latham & Watkins LLP https://www.lw.com/en/insights/the-genius-act-of-2025-stablecoin-legislation-adopted-in-the-us
6. Notice of proposed rulemaking: Implementing the Guiding and Establishing National Innovation for U.S. Stablecoins Act for the Is - OCC.gov https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-9a.pdf
7. EBA/RTS/2024/11 — Report — Highly Liquid Reserve Assets [final draft submitted] | mica.wtf https://www.mica.wtf/mica-level-2-and-level-3/technical-standards/final-reports/rts-on-highly-liquid-financial-instruments-in-reserve-assets
8. 스테이블코인 꽃필까…빅테크도 게임업도 사업진출 공식화 - 머니투데이 https://www.mt.co.kr/tech/2025/09/09/2025090818040889628
9. 스테이블코인 법제화 답보…국내 시장 잠식 우려 - DFT 대한금융신문 https://www.kbanker.co.kr/news/articleView.html?idxno=221364
10. 금융위 “한은 스테이블코인 긴급조치 요청권 등 실익 적어“ - 연합뉴스TV https://www.yonhapnewstv.co.kr/news/AKR202511251615382sL
11. 전체 제정·개정이유 - 국가법령정보센터 https://law.go.kr/LSW/lsRvsRsnListP.do?lsId=001565&chrClsCd=010202&lsRvsGubun=all
12. 금융투자회사의 컴플라이언스 매뉴얼 Ⅲ편(자산운용) | 규정내용 https://law.kofia.or.kr/service/law/lawFullScreenContent.do?seq=262&historySeq=755
13. 투자자예탁금제도 https://www.imbank.co.kr/cms/dev/prv/prv_isa08.html
14. 가상자산 분야 이슈리포트 - 국내 스테이블코인 관련 법률안의 주요 내용 및 시사점 https://www.draju.com/ko/sub/newsletters.html?type=view&bsNo=6577&langNo=
15. 올해 발의된 디지털자산 법안만 8건…'산업 육성'vs'이용자 보호' 엇갈려 - ZDNet Korea https://zdnet.co.kr/view/?no=20251230095852
16. 與안도걸 스테이블코인 법안 내주 발의…통화·외환 파장도 예의주시 - 한국경제 https://www.hankyung.com/article/202507237786g
17. 신 탁 계 약 서 - 하나UBS 신종MMF(S-29호) http://money2.daishin.com/E5_Data/service/www/Agree/Fund/2023/6/81801_KR5102AG6370_R1_20230602_%ED%95%98%EB%82%98UBS%EC%8B%A0%EC%A2%85MMF(S-29%ED%98%B8)ClassC.pdf
18. 전체화면 | 모범규준 | 금융투자회사의 컴플라이언스 매뉴얼 Ⅲ편(자산운용) https://law.kofia.or.kr/service/law/lawFullScreen.do?seq=262&historySeq=756
19. 투자설명서 - NH-Amundi자산운용 https://www.nh-amundi.com/_upload/fund/PrdtDoc/MN040_%ED%88%AC%EC%9E%90%EC%84%A4%EB%AA%85%EC%84%9C_NH-Amundi%20%EB%B2%95%EC%9D%B8%EC%9A%A9%20%EB%8B%AC%EB%9F%AC%20MMF%201%ED%98%B8(USD)_241227.pdf
20. 투자설명서 - NH-Amundi자산운용 https://www.nh-amundi.com/_upload/fund/PrdtDoc/MN040_%ED%88%AC%EC%9E%90%EC%84%A4%EB%AA%85%EC%84%9C_NH-Amundi%20%EB%B2%95%EC%9D%B8%EC%9A%A9%20%EB%8B%AC%EB%9F%AC%20MMF%201%ED%98%B8(USD)_241227.pdf
21. 투자설명서 - NH-Amundi자산운용 https://www.nh-amundi.com/_upload/fund/PrdtDoc/MN040_%ED%88%AC%EC%9E%90%EC%84%A4%EB%AA%85%EC%84%9C_NH-Amundi%20%EB%B2%95%EC%9D%B8%EC%9A%A9%20%EB%8B%AC%EB%9F%AC%20MMF%201%ED%98%B8(USD)_241227.pdf
22. 부록 https://www.bok.or.kr/portal/cmmn/file/fileDown.do?atchFileId=e17a3e9a750b63d0a1722d25bbd52037&fileSn=4
23. 수익 – 포커스온경제 통합 검색 https://foeconomy.co.kr/news/search.php?q=%EC%88%98%EC%9D%B5&var=page0&page0=54&page0=52
24. 고객서비스 > 업무안내가이드 > 예탁금이용료율안내 - KB증권 https://www.kbsec.com/go.able?linkcd=m06030010
25. MiCA Reserve and Authorization Rules | Support - Eco https://eco.com/support/en/articles/14796310-mica-reserve-and-authorization-rules
26. HKMA Consultations – Obligations of Licensed Stablecoin Issuers - Charltons Law https://www.charltonslaw.com/hkma-consultations-on-obligations-of-hkma-licensed-stablecoin-issuers/
27. Global approaches to stablecoin regulation | EY https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/industries/banking-capital-markets/documents/ey-gl-global-stablecoin-regulation-comparison-09-2025.pdf
28. GENIUS Act Implementation - Federal Register https://www.federalregister.gov/documents/2025/09/19/2025-18226/genius-act-implementation
29. The GENIUS Act: A New Era of Stablecoin Regulation - Gibson Dunn https://www.gibsondunn.com/the-genius-act-a-new-era-of-stablecoin-regulation/
30. EBA/RTS/2024/10 — Report — Reserve Asset Liquidity [final draft submitted] | mica.wtf https://www.mica.wtf/mica-level-2-and-level-3/technical-standards/final-reports/rts-on-liquidity-requirements-of-reserve-of-assets
31. EBA/Op/2025/13 — Opinion — Reserve Liquidity RTS [published] | headlesslaw - mica.wtf https://www.mica.wtf/mica/level-3/opinions/eba-op-2025-13-amendments-rts-reserve-liquidity-requirements
32. HKMA Issues Guideline on Supervision of Stablecoin Issuers | Legalink https://www.legalink.net/xms/files/hkma-issues-guideline-on-supervision-of-stablecoin-issuers.pdf
33. STABLECOINS ORDINANCE - Hong Kong Monetary Authority https://www.hkma.gov.hk/media/eng/doc/key-functions/ifc/stablecoin-issuers/Guideline_on_supervision_of_licensed_stablecoin_issuers_eng.pdf
34. Hong Kong Stablecoin Ordinance Takes Effect August 2025 | Morgan Lewis https://www.morganlewis.com/pubs/2025/06/hong-kongs-stablecoins-ordinance-to-take-effect-august-1-an-overview-of-the-regulatory-framework
35. Key Points and Challenges for Hong Kong Stablecoin Issuer License Applications https://www.hankunlaw.com/en/portal/article/index/cid/8/id/15890.html
36. Hong Kong announces Stablecoin Consultation Conclusions and Sandbox Participants amid Web3 push | Global Regulation Tomorrow https://www.regulationtomorrow.com/2024/07/hong-kong-announces-stablecoin-consultation-conclusions-and-sandbox-participants-amid-web3-push/
37. The Impact of Distributed Ledger Technology in Capital Markets https://www.gfma.org/wp-content/uploads/2025/08/1.-full-report-impact-of-dlt-in-cap-mkts-final-1.pdf
38. FCA and MAS stablecoin frameworks: a comparative view | Insights - UK Finance https://www.ukfinance.org.uk/news-and-insight/blog/fca-and-mas-stablecoin-frameworks-comparative-view
39. Overview of Stablecoin Regulation - Binance https://www.binance.com/en/research/analysis/overview-of-global-stablecoin-regulation
40. Annex B: List of Respondents - Monetary Authority of Singapore https://www.mas.gov.sg/-/media/mas-media-library/publications/consultations/pd/2023/15aug2023_annex--submissions-to-consult-paper-on-stablecoins.pdf
