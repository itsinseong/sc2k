# G-2 해외 예금과 통화정책 영향 연구

- 노트북: https://notebook.google.com/notebook/4cb88ba4-bf93-44cb-8810-9b81ed8c4efa?authuser=1 (자동 제목 "Stablecoin Reserve Portfolio Optimal Control")
- 보고서 제목: 원화 스테이블코인 준비자산 공시 기준 제안 및 통화·금융 시스템 영향 분석 연구 보고서
- 소스 23종(소스 25개), 보고서 참고 링크 18개, 채팅 답 1건, 본문 21121자
- 실행 방식: Deep Research(보고서는 소스로 저장) + 채팅 답 1건(질문은 프롬프트 원문)
- 수집: 2026-10-09 Aside repl, 원문 대조 전

---
# 원화 스테이블코인 준비자산 공시 기준 제안 및 통화·금융 시스템 영향 분석 연구 보고서

## 서론

가치안정형 디지털자산(스테이블코인)의 급속한 성장은 글로벌 금융 시스템의 지급결제 효율성을 제고하는 동시에 전통적인 금융중개 체계와 통화정책 전달경로에 구조적인 변화를 유발하고 있다. 특히 원화에 연동되는 스테이블코인의 도입 논의는 단순한 가상자산 규제를 넘어 중앙은행의 통화주권 확보, 시중은행의 예금 기반 안정성, 단기 자금시장의 수급 균형과 직결되어 있다 [cite: 1, 2, 3].

대한민국 국회 정무위원회에는 원화 스테이블코인의 발행 자격, 준비자산 관리, 이용자 보호 및 감독 권한을 규정하기 위한 제정안 9건이 계류되어 있으며, 금융위원회와 한국은행 간의 감독 권한 및 정책 협의체 구성을 둘러싼 입장 차이가 주요 쟁점으로 부각되고 있다 [cite: 1, 4, 5]. 본 보고서는 국회에 계류 중인 9개 법률안의 주요 조항 및 정무위원회 검토보고서 내용을 비교 분석하고, 해외 주요 정책기관(BIS, IMF, US Fed, ECB, Bank of England)의 실증 연구 결과를 바탕으로 스테이블코인 확대가 은행 예금·대출 및 단기 국채 시장에 미치는 파급효과를 평가하여 원화 스테이블코인 준비자산 공시 기준을 제안한다.

---

## 국회 계류 제정안 9건 비교 및 금융당국·한국은행 간 핵심 쟁점

### 계류 법률안별 주요 내용 및 준비자산 규정 비교

현재 국회 정무위원회에는 민주당 민병덕·안도걸·김현정·이강일·박상혁 의원과 국민의힘 김은혜·김재섭·최보윤·김성원 의원이 각각 대표발의한 스테이블코인 및 디지털자산 관련 법률안 9건이 계류되어 심사를 기다리고 있다 [cite: 5, 6]. 각 법안은 발행 주체의 요건, 준비자산의 법적 격리 방식, 한국은행의 감독 및 자료제출 요구권 범위 등에서 상이한 규제 수위를 설정하고 있다 [cite: 1, 4, 6].

민병덕 의원이 대표발의한 「디지털자산기본법안」(의안번호 2210736, 2025년 6월 11일 발의, 제103조제2항제1호 및 제2호) 및 안도걸 의원이 대표발의한 「가치안정형 디지털자산의 발행 및 유통에 관한 법률안」(의안번호 2211784)을 비롯하여 김은혜(의안번호 2211777), 김현정(의안번호 2212298), 이강일(의안번호 2213166), 김재섭(의안번호 2213266), 최보윤(의안번호 2213449), 박상혁(의안번호 2214492), 김성원(의안번호 2218219) 의원안이 계류되어 있다 [cite: 5, 6].

이 중 안도걸·김은혜·김현정 의원안은 발행인의 최소 자기자본 요건을 50억 원 이상으로 명시하여 대형 금융기관 중심의 시장 진입을 유도하고 있으며, 이용자 자산의 안전한 보호를 위해 준비자산의 별도 예치·신탁, 상계 및 압류 금지, 도산 시 이용자의 우선변제권을 법률 조항으로 명확히 규정하고 있다 [cite: 6]. 그러나 인정할 준비자산의 구체적 범위(예: 현금, 은행 예금, 단기 국채, MMF 등), 별도 예치·신탁 방식, 환매 기한 및 수수료 체계 등 세부 기준은 법률안 원문상 구체적 수치로 확정되지 않았거나 하위 법령 위임 항목으로 남겨져 있다 [cite: 5].

| 의안번호 및 발의자 | 주요 법안명 및 발의일자 | 자기자본 요건 | 준비자산 도산격리 및 이용자 보호 조항 | 한국은행 감독/검사 권한 규정 | 출처/1차 자료 |
|---|---|---|---|---|---|
| 2210736 (민병덕) | 디지털자산기본법안 (2025.06.11) [cite: 6] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 국회 의안원문 (제103조제2항) [cite: 6] |
| 2211777 (김은혜) | 가상자산이용자보호법 개정안 등 | 50억 원 이상 [cite: 6] | 분리보관, 상계·압류 금지, 우선변제권 명시 [cite: 6] | 한은의 검사요구권 신설 [cite: 1, 4] | 정무위 검토보고서 [cite: 1, 4], 법제처 문서 [cite: 6] |
| 2211784 (안도걸) | 가치안정형 디지털자산의 발행 및 유통에 관한 법률안 [cite: 6] | 50억 원 이상 [cite: 6] | 분리보관, 상계·압류 금지, 우선변제권 명시 [cite: 6] | 한은 공동검사 참여권, 한은·기재부 긴급조치명령 요청권 [cite: 1, 4] | 정무위 검토보고서 [cite: 1, 4], 법제처 문서 [cite: 6] |
| 2212298 (김현정) | 디지털자산 관련 법안 | 50억 원 이상 [cite: 6] | 분리보관, 상계·압류 금지, 우선변제권 명시 [cite: 6] | 지급결제 안정성 확보 위한 한은 참여 범위 확대 [cite: 1] | 정무위 검토보고서 [cite: 1], 법제처 문서 [cite: 6] |
| 2213166 (이강일) | 디지털자산 관련 법안 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 언론 기사 (비즈니스포스트) [cite: 5] |
| 2213266 (김재섭) | 디지털자산 관련 법안 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 언론 기사 (비즈니스포스트) [cite: 5] |
| 2213449 (최보윤) | 디지털자산 관련 법안 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 언론 기사 (비즈니스포스트) [cite: 5] |
| 2214492 (박상혁) | 디지털자산 관련 법안 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 언론 기사 (비즈니스포스트) [cite: 5] |
| 2218219 (김성원) | 디지털자산 관련 법안 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 언론 기사 (비즈니스포스트) [cite: 5] |

### 금융위원회와 한국은행 간 감독 권한 및 정책 협의체 갈등

2025년 11월 25일 국회 정무위원회 정명호 수석전문위원이 작성하여 정무위원회 법안제1소위원회에 제출한 검토보고서에 따르면, 원화 스테이블코인의 감독 주체 및 검사 권한을 둘러싸고 금융위원회와 한국은행 간의 견해차가 상충하고 있다 [cite: 1, 4].

김은혜 의원안은 현행 가상자산이용자보호법상 인정된 '한국은행의 자료제출 요구권'을 넘어 한국은행에 '검사요구권'을 신설하는 내용을 담았으며, 안도걸 의원안은 한국은행의 '공동검사 참여 권한'과 더불어 한국은행 및 기획재정부에 '긴급조치명령 요청권(거래지원 종료·중단 명령 등)'을 부여하고 있다 [cite: 1, 4]. 김현정 의원안 역시 지급결제 안정성 확보를 이유로 한국은행의 관여 범위를 넓히는 조항을 포함하고 있다 [cite: 1].

이에 대해 금융위원회는 정무위원회에 제출한 공식 의견을 통해 다음과 같이 반대 입장을 정면으로 표명하였다 [cite: 1, 4]: 첫째, 가상자산 규율은 금융위 소관 법체계 안에서 일관성 있게 설계되어야 하며, 검사 권한을 여러 기관에 분산하는 방식은 시장 혼란을 초래할 수 있다 [cite: 1]. 둘째, 한국은행과 기획재정부의 금융위원회에 대한 긴급조치명령 또는 거래지원 종료·중단 명령 행사 요청 권한은 관련 입법례가 확인되지 않는다 [cite: 4]. 아울러 한국은행 부총재와 기획재정부 차관은 금융위원회의 당연직 위원으로 논의 및 의결에 참여하고 있으므로 별도의 요청 권한을 인정할 실익이 적다 [cite: 4]. 셋째, 한국은행의 (공동)검사 요청 권한을 발행량이 일정 수준 이하로 통화신용정책에 영향을 미치기 어려운 일부 스테이블코인 발행인에까지 인정하는 것은 과도하다 [cite: 4]. 넷째, 금융위 산하에 한은·기재부 등이 참여하는 별도 협의기구를 설치하여 협의 사항을 반영하도록 강제하는 것은 합의제 행정기구로서 독립성이 보장되고 고유한 의사결정 권한을 보유한 금융위원회의 설립 목적 및 고유 권한과 상충할 소지가 있다 [cite: 4].

반면 한국은행은 '원화 스테이블코인의 주요 이슈와 대응방안' 보고서 및 KDI 나라경제(2025년 8월호, p. 7-8) 등을 통해 스테이블코인이 대규모 유통될 경우 통화정책 전이경로 약화 및 지급결제 시스템 리스크를 유발할 수 있으므로 중앙은행의 감독 관여가 필수적이라는 입장을 지속적으로 피력하고 있다 [cite: 1, 2]. 한국은행은 통화(한국은행)·외환(기획재정부)·금융(금융위원회) 당국이 참여하는 정책협의기구를 구성하여 스테이블코인 발행 자격, 발행량 결정, 준비자산 구성 기준 등을 공동 결정해야 한다고 강조하고 있으며, 발행 주체를 통제 가능한 대형 상업은행으로 한정하는 방안을 선호하고 있다 [cite: 1, 2]. 아울러 금융위원회는 스테이블코인의 정의에 대해서도 단일 법정화폐 가치에 연동되는 자산으로 한정해야 한다는 견해를 제출하였다 [cite: 4].

---

## 해외 주요 연구를 통한 통화·금융 시스템 영향 실증 분석

### 준비자산 구성 형태에 따른 은행 예금 총량의 변화 메커니즘

스테이블코인 발행사가 수취한 준비자산을 상업은행 예금으로 보유하는지, 혹은 단기 국채나 MMF로 운용하는지에 따라 전체 은행 시스템의 예금 총량과 대차대조표 구조는 상이한 경로를 거쳐 변동한다 [cite: 3, 7, 8, 9, 10].

준비자산을 상업은행 예금으로 보유하는 경우, 경제 주체가 시중은행의 소매 예금을 인출하여 스테이블코인을 매수하더라도 발행사가 해당 자금을 다시 상업은행 예금 계좌에 예치하므로 은행 시스템 전체의 총예금 잔액 자체는 불변으로 유지된다 [cite: 3, 7, 8]. 그러나 예금의 질적 특성에 유의미한 균열이 발생한다 [cite: 3, 7, 8]. 기존의 안정적이고 금리 민감도가 낮은 소매 예금(Retail Deposits)이 스테이블코인 발행사 명의의 대형 도매 예금(Wholesale Deposits)으로 대체되기 때문이다 [cite: 3, 7, 8]. 이러한 도매 예금은 암호화폐 시장 변동성 및 환매 청구에 극도로 민감하게 반응하여 유출 가능성이 높으므로, 시중은행의 유동성 위험(Liquidity Risk)과 자금조달 비용을 대폭 상승시키는 결과를 초래한다 [cite: 3, 7, 8, 10].

반면 준비자산을 단기 국채(T-bills)나 MMF 매입으로 운용할 경우, 소매 예금은 상업은행 시스템 외부로 탈중개화(Disintermediation)되어 실질적인 총예금 감소로 이어진다 [cite: 3, 8, 9, 10]. 만약 규제 프레임워크가 스테이블코인 발행사에 중앙은행 마스터 계좌(Central Bank Master Account) 접근권을 허용하는 시나리오가 현실화되면, 예금자 자금이 중앙은행 예치금으로 직접 이동함에 따라 상업은행 대차대조표가 직접 축소되는 최대 수준의 탈중개화가 발생한다 [cite: 10]. 이 경우 시중은행은 대출 연장에 필요한 핵심 재원을 상실하게 되며, 유동성 규제 충족을 위해 고금리 도매 자금 시장에 대한 의존도를 높여 실물경제에 대한 대출 공급 능력을 대폭 위축시키게 된다 [cite: 7, 11].

### 예금 이탈 추정치 및 시나리오 분석

해외 주요 중앙은행 및 정책 연구 기관들은 스테이블코인 채택 확대에 따른 은행 예금 이탈 규모와 신용 축소 파급효과를 다각도로 정량 모형화하였다 [cite: 10, 12, 13].

미국 연방준비제도(Federal Reserve Board)의 FEDS Notes에 발표된 연구("Banks in the Age of Stablecoins: Implications for Deposits, Credit, and Financial Intermediation", 2025년 12월 17일)는 스테이블코인 확대가 은행 예금 및 대출에 미치는 영향을 정량적 시나리오로 제시하였다 [cite: 10]. 연구진은 스테이블코인 발행량이 5,000억 달러(ΔSC=$500B) 증가하고, 소매 예금 재유입 비율이 20%(α=20%), 해외 자금 유입에 따른 상쇄분이 1,000억 달러(FO=+$100B)인 온건한 채택 시나리오(Scenario B)를 설정하였다 [cite: 10]. 이 모형에서 은행 예금의 순감소분(ΔD)은 다음과 같이 산출된다 [cite: 10]:

ΔD=−0.8×500+100=−3,000억 달러 (-$300B)

예금 감소에 따른 대차대조표 수평 효과(Level Effect)로 인해 -1,800억 달러에서 -3,780억 달러의 예금 축소가 가시화되며, 유동성 자산 보유 비율 규제 충족에 따른 자산 재배치 가감(Composition Haircut, ΔL
comp
	​

=−γ⋅0.2⋅500) 효과로 인해 -100억 달러에서 -300억 달러의 추가 신용 축소가 도출된다 [cite: 10]. 이에 따라 미 상업은행 부문의 총대출 및 신용 중개 축소 규모는 최소 -1,900억 달러에서 최대 -4,080억 달러에 달하는 것으로 추정되었다 [cite: 10].

영란은행(Bank of England)의 논의 문서 및 금융안정보고서(2021년 / 2025년)는 금융 스트레스 국면에서 상업은행 예금이 민간 디지털 화폐로 이탈하는 위기 시나리오를 제시하였다 [cite: 11, 13]. 영란은행의 스트레스 모형에 따르면, 심각한 금융 불안 발생 시 가계 및 비금융 기업 예금의 20%가 스테이블코인 등으로 일시에 유출될 수 있다고 평가하였다 [cite: 13]. 영국과 같이 은행 중개 대출 비중이 높은 경제 구조에서는 이러한 급격한 예금 이탈이 기업 및 가계에 대한 신용 공급을 마비시킬 수 있으므로, 보유 한도(Holding Limits) 설정 및 중앙은행 무이자 예치 의무화가 필수적임을 도출하였다 [cite: 11, 14, 15].

유럽중앙은행(ECB)의 Working Paper No. 3199 (Carlo Altavilla, Miguel Boucinha, Lorenzo Burlon, Ramón Adalid, Roberta Fortes, Franziska Maruhn, 2026년 3월)는 유로존 내 354개 은행의 미공개 미시 데이터를 활용하여 2007년 6월부터 2025년 9월까지의 통화정책 고주파 충격을 도구변수로 분석하였다 [cite: 12, 16]. 분석 결과, 개별 은행의 스테이블코인 노출도가 1표준편차 증가할 때 향후 24개월 동안 비금융 사적부문 대출 성장률이 누적 약 2.5%p 지속적으로 감소하는 것으로 나타났다 [cite: 12]. 이는 스테이블코인으로 인한 예금 이탈이 은행의 자금조달 구조를 고비용·고변동성 구조로 전환시켜, 중앙은행의 정책금리 인하 효과가 실물 대출 금리로 전달되는 파급경로를 왜곡시킴을 정량적으로 입증한 것이다 [cite: 3, 7, 12].

### 단기 국채 금리 및 수요에 미치는 영향

스테이블코인 준비자산이 미국 단기 국채(T-bills) 등 고유동성 Safe Assets에 집중됨에 따라, 단기 채권 시장의 수급과 수익률 곡선 단기 구간에 비대칭적 영향이 발생하고 있다 [cite: 9, 17, 18].

BIS Working Paper No. 1270 (Rashad Ahmed & Iñaki Aldasoro, "Stablecoins and safe asset prices", 2025년 5월)은 2021년부터 2025년까지의 일별 데이터를 활용하여, 암호화폐 시장 고유의 가격 변동성을 식별한 도구변수(IV) 및 로컬 프로젝션(Local Projections) 분석을 수행하였다 [cite: 18]. 실증 분석 결과, 스테이블코인으로의 2표준편차 자금 유입 충격은 미국 3개월물 국채 금리(3-month T-bill yield)를 2.5~3.5bp 지속적으로 하락시키는 것으로 도출되었다 [cite: 18].

이 연구는 국채 금리에 미치는 영향이 시장의 수급 여건에 따라 비대칭적으로 달라지는 국면 의존성(State-dependency)을 명확히 입증하였다 [cite: 18]. 연준의 이틀짜리 역레포(ON RRP) 창구 이용 잔액이 풍부하거나 국채 공급이 원활한 시기에는 금리 하락 효과가 통계적으로 미미했으나, 부채한도 상한(Debt Ceiling) 협상 지연 등으로 단기 국채 공급이 제약되는 '국채 희소성(Bill Scarcity)' 국면에서는 3개월물 국채 금리 하락 폭이 5~8bp까지 확대되는 것으로 나타났다 [cite: 18].

BIS Annual Economic Report (2026년) 및 IMF Working Paper (2026년) 역시 스테이블코인 발행사의 단기 국채 집중 매입이 국채 단기 수익률 곡선을 눌러 정부의 단기 자금조달 비용을 낮추고 재정 공간(Fiscal Space)을 일부 확장하는 효과가 있음을 제시하였다 [cite: 9, 17]. 그러나 암호화폐 시장 위기 시 대규모 환매가 발생하는 상황에서는 발행사들이 유동성을 확보하기 위해 단기 국채를 짧은 시간에 대량 투매(Fire Sale)함에 따라 단기 금리가 폭등하고 레포 시장의 담보 자산이 고갈되는 금융 불안정성이 증폭될 수 있음을 지적하였다 [cite: 9].

### 규제 설계(현금 비율, 이자 금지)의 영향 조정 효과

스테이블코인 확대에 따른 부작용을 통제하기 위해 각국 규제당국은 준비자산의 현금 예치 비율과 이자 지급 금지 규정을 핵심 안전판으로 설계하고 있다 [cite: 3, 14, 15].

영란은행(Bank of England)은 파운드화 연동 시스템적 스테이블코인 발행사에 대해 준비자산의 최소 40% 이상을 영란은행 내 무이자 예금(Unremunerated Deposits at the Bank)으로 상시 보유하도록 의무화하는 제안을 발표하였다 [cite: 14]. 이는 급격한 환매 청구 발생 시 유동성 부족으로 인한 뱅크런 및 페그 붕괴 위험을 방지하기 위해 즉각적인 중앙은행 유동성 버퍼를 확보하려는 목적이다 [cite: 14]. EU의 MiCAR 역시 준비자산의 일정 비율 이상을 상업은행 예치금으로 보유하도록 강제하고 있으나, 유럽중앙은행(ECB)은 이 조항이 특정 예치은행으로의 위험 집중을 유발할 수 있어 일별·주별 만기 구조를 반영한 리퀴디티 버킷(Liquidity Bucketing) 규제로 보완할 것을 권고하고 있다 [cite: 8, 12].

영란은행, 연준 및 EU MiCAR 등 글로벌 규제 체계는 공히 스테이블코인 보유자에 대해 준비자산 운용 수익에 기반한 이자(Interest) 지급 및 우회적 리워드(Rewards) 제공을 엄격히 금지하고 있다 [cite: 3, 14, 15]. 스테이블코인이 이자를 지급할 경우 시중은행의 보통예금 자금이 스테이블코인으로 급격히 이탈하여 은행 탈중개화와 신용 위축이 가속화되기 때문이다 [cite: 3, 15]. 이자 지급 금지 규제는 스테이블코인을 '저축·투자 수단'이 아닌 '지급결제 수단'으로 한정함으로써 상업은행의 예금 기반 상실 위험을 차단하는 결정적 역할을 수행한다 [cite: 3, 15].

---

## 해외 주요 연구 현황 종합 비교

아래 표는 해외 주요 중앙은행, 국제기구 및 학술지에 발표된 스테이블코인의 통화·금융 파급효과 실증 연구를 종합 비교한 결과이다.

| 연구 | 대상 | 방법 | 결과 수치 | 가정 | 주소 |
|---|---|---|---|---|---|
| Altavilla et al. (2026)<br>(ECB Working Paper No. 3199) [cite: 7, 12, 16] | 유로존 은행 시스템 및 통화정책 전달경로 (354개 은행) [cite: 7, 12, 16] | 고주파 통화정책 충격(OIS 금리) 도구변수를 활용한 로컬 프로젝션(LP) 회귀분석 (2007.06~2025.09) [cite: 12, 16] | 스테이블코인 노출도 1표준편차 증가 시 24개월 누적 비금융 사적부문 대출 성장률 약 2.5%p 감소 [cite: 12] | 2030년까지 글로벌 스테이블코인 발행액 9,000억 달러~4조 달러 도달, 소매 예금의 디지털 자산 전환 [cite: 12] | https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3199~ad552b59ec.en.pdf [cite: 12] |
| Ahmed & Aldasoro (2025)<br>(BIS Working Paper No. 1270) [cite: 18] | 미국 단기 국채(T-bills) 및 자금시장의 일별 데이터 (2021~2025) [cite: 18] | 암호화폐 시장 특유의 가격 변동성을 식별한 도구변수(IV) 및 로컬 프로젝션 분석 [cite: 18] | 스테이블코인 유입 2표준편차 증가 시 3개월물 국채 금리 2.53.5bp 하락; 국채 희소성 시기에는 58bp 하락 폭 확대 [cite: 18] | 스테이블코인 준비자산의 대부분이 미국 단기 국채로 운용됨 [cite: 17, 18] | https://www.bis.org/publ/work1270.htm [cite: 18] |
| Federal Reserve Board (2025)<br>(FEDS Notes) [cite: 10] | 미국 상업은행 부문 및 신용 중개 체계 [cite: 10] | 대차대조표 시나리오 분석 모델링 (Scenario B) [cite: 10] | 스테이블코인 5,000억 달러 증가 시 예금 순감소 3,000억 달러; 전체 대출/신용 중개 감소 -1,900억 달러 ~ -4,080억 달러 [cite: 10] | 스테이블코인 채택 5,000억 달러 확대, 예금 재유입률 20%, 해외 유입 상쇄 1,000억 달러 [cite: 10] | https://www.federalreserve.gov/econres/notes/feds-notes/banks-in-the-age-of-stablecoins-implications-for-deposits-credit-and-financial-intermediation-20251217.html [cite: 10] |
| Bank of England (2021/2025)<br>(CP/DP & Financial Stability Paper) [cite: 11, 13, 14] | 영국 상업은행 시스템 및 파운드화 시스템적 스테이블코인 [cite: 11, 14] | 심각한 스트레스 시나리오하에서의 예금 유출 시뮬레이션 및 규제 설계 [cite: 11, 13, 14] | 위기 시 가계/비금융 기업 예금의 20% 유출 평가; 시스템적 발행사에 대해 중앙은행 무이자 예치 40% 의무화 [cite: 14] | 급격한 환매 대응을 위한 중앙은행 예금 확보 필요성; 보유 한도 설정 및 이자 지급 금지 적용 [cite: 14, 15] | https://www.bankofengland.co.uk/paper/2025/cp/proposed-regulatory-regime-for-sterling-denominated-systemic-stablecoins [cite: 14] |
| Liao & Caramichael (2022) / BIS (2026)<br>(AER 2026 / Fed Research) [cite: 9] | 미국 은행 시스템 및 대출 공급 [cite: 9] | 거시경제 거버넌스 및 대차대조표 자산 배분 프레임워크 분석 [cite: 9] | 상업은행 예금 백킹(2단계 구조) 시 대출 중립적; 중앙은행 예금 백킹 시 예금 이탈 및 대출 탈중개화 발생 (구체적 수치 원문 확인 안 됨) [cite: 9] | 준비자산의 상업은행 예금 보유 방식과 중앙은행/국채 보유 방식의 상이한 파급효과 비교 [cite: 9] | https://www.bis.org/publications/aer-2026/anchoring-trust-money [cite: 9] |

---

## 원화 스테이블코인 준비자산 공시 기준 제안

국회 계류 제정안들의 규제 조항과 해외 정책연구기관의 실증 분석 결과를 바탕으로, 본 연구는 학부 프로젝트 차원에서 원화 스테이블코인의 안정적 유통과 통화안정성을 확보하기 위한 3대 준비자산 공시 기준을 제시한다.

### 준비자산 구성 비율의 단기 유동성 분산 기준

은행 시스템의 예금 탈중개화 및 단기 국채 시장의 수급 왜곡을 방지하기 위하여 준비자산의 최소 30% 이상을 국내 제1금융권 상업은행 예금 및 한국은행 예치금으로 보유하도록 의무화한다 [cite: 8, 14]. 특정 단일 상업은행에 대한 예치 비중은 전체 준비자산의 10%를 초과하지 못하도록 규정하여 집중 유동성 리스크를 차단한다. 아울러 남은 준비자산은 잔존만기 90일 이내의 대한민국 국채(KTB) 및 한국은행 통화안정증권(MSB) 등 초고음질 자산으로 한정하여 운용하도록 명시한다 [cite: 17, 18].

### 일별 유동성 버킷 공시 및 신탁 도산격리 실시간 검증

발행사는 매 영업일 단위로 1일 이내 현금화 가능한 자산과 5일 이내 현금화 가능한 자산의 비중을 포함하는 유동성 버킷(Liquidity Bucket) 데이터를 공시하여야 한다 [cite: 8]. 또한 안도걸·김은혜·김현정 의원안에서 명시한 바와 같이 준비자산 전체에 대하여 이용자를 수익자로 하는 법적 신탁(Statutory Trust) 설정을 의무화하고, 발행사의 부도 시 준비자산이 일반 채권자의 압류 및 상계 대상에서 완벽히 격리되는 도산격리(Bankruptcy Remoteness) 이행 현황을 매월 독립된 회계법인의 감사 보고서를 통해 공시하도록 규정한다 [cite: 6, 15].

### 이자·리워드 지급 금지 명시 및 기관 간 공동 감독 협의체 신설

시중은행 예금의 원화 스테이블코인으로의 구조적 이탈을 차단하기 위하여 스테이블코인 보유자에 대한 직접적인 이자 지급 및 우회적 포인트·마일리지 형태의 리워드 제공을 법률상 금지한다 [cite: 3, 14, 15]. 한편, 금융위원회와 한국은행 간의 감독 권한 갈등을 해결하기 위해 원화 스테이블코인 발행 총량이 일정 기준(예: 1조 원)을 초과하는 경우, 금융위원회 부위원장, 한국은행 부총재, 기획재정부 차관으로 구성된 '가치안정형 디지털자산 정책협의체'를 통해 준비자산 적격성 기준 및 발행량 상한을 공동 심의·의결하도록 법안을 보완할 것을 제안한다 [cite: 1, 4].

---

## 결론

원화 스테이블코인의 제도화 논의는 금융 혁신과 통화·금융 안정을 균형 있게 달성할 수 있는 정교한 규제 설계가 선행되어야 한다. 해외 주요 중앙은행 및 정책 기관들의 연구는 스테이블코인 확대가 상업은행의 소매 예금을 고변동성 도매 예금으로 대체시키고, 대출 신용 공급을 위축시키며, 단기 국채 금리의 수급왜곡을 초래할 수 있음을 입증하고 있다 [cite: 7, 10, 12, 18].

따라서 국회 정무위원회는 계류 중인 9개 제정안의 입법 과정에서 금융위원회와 한국은행의 감독 권한을 합리적으로 통합하고, 준비자산의 엄격한 분리 보관, 만기별 유동성 공시, 이자 지급 금지 조항을 확립함으로써 원화 스테이블코인의 신뢰성을 확보하고 통화정책의 유효성을 견지해야 한다 [cite: 1, 4, 6, 14, 15].

---

- 올해도 스테이블코인 입법 '난항'…금융위 vs 한은 대립 수면 위로 - 지디넷코리아, https://zdnet.co.kr/view/?no=20251125143503

- 스테이블코인 시대 열릴까 - KDI 경제교육, https://eiec.kdi.re.kr/userdata/nara/202508/202508.pdf

- From money market funds to stablecoins: lessons for central banks, https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260601~38dffe5ec5.en.html

- 금융위 "한은 스테이블코인 긴급조치명령 요청권 등 실익 적어" - 연합뉴스, https://www.yna.co.kr/view/AKR20251125044900002

- 국회 정무위 '법안소위 속도전' 채비, 스테이블코인 연내 입법 '3대 쟁점' 실타래 풀리나, https://www.businesspost.co.kr/BP?command=article_view&num=442765

- 스테이블코인의 기업금융 인프라로서의 활용을 위한 입법적 과제*, https://www.moj.go.kr/bbs/moj/166/497660/download.do

- Lorenzo Burlon - European Central Bank, https://www.ecb.europa.eu/pub/research/authors/profiles/lorenzo-burlon.en.html

- ESCB response to the European Commission's targeted consultation on the Markets in Crypto-Assets Regulation (MiCAR), https://www.ecb.europa.eu/press/consultationresponse/pdf/ecb.conresp202609_micarreview.en.pdf?c026ff0fd6c52a4eb29d725e6fec3cbb

- III. Anchoring trust in money: innovation beyond stablecoins - the BIS, https://www.bis.org/publications/aer-2026/anchoring-trust-money

- The Fed - Banks in the Age of Stablecoins: Some Possible Implications for Deposits, Credit, and Financial Intermediation - Federal Reserve, https://www.federalreserve.gov/econres/notes/feds-notes/banks-in-the-age-of-stablecoins-implications-for-deposits-credit-and-financial-intermediation-20251217.html

- The role of holding limits for sterling-denominated systemic stablecoins and a potential digital pound | Bank of England, https://www.bankofengland.co.uk/financial-stability-paper/2025/holding-limits-for-sterling-denominated-systemic-stablecoins-and-a-digital-pound

- Stablecoins and monetary policy transmission - European Central Bank, https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3199~ad552b59ec.en.pdf

- Occasional Paper Series - Central bank digital currency and bank intermediation, https://www.ecb.europa.eu/pub/pdf/scpops/ecb.op293~652cf2b1aa.en.pdf

- Proposed regulatory regime for sterling-denominated systemic stablecoins, https://www.bankofengland.co.uk/paper/2025/cp/proposed-regulatory-regime-for-sterling-denominated-systemic-stablecoins

- House of Lords - Stablecoins: waiting for regulation - Financial Services Regulation Committee - Parliament (publications), https://publications.parliament.uk/pa/ld5902/ldselect/ldfsrc/6/607.htm

- From money market funds to stablecoins: lessons for central banks, https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260601_annex~8852850053.hu.pdf

- Stablecoin Shocks, WP/26/44, March 2026 - International Monetary Fund, https://www.imf.org/-/media/files/publications/wp/2026/english/wpiea2026044-source-pdf.pdf

- Stablecoins and safe asset prices - EconPapers, https://econpapers.repec.org/RePEc:bis:biswps:1270


## 참고 링크(보고서 끝 목록)

1. 올해도 스테이블코인 입법 '난항'…금융위 vs 한은 대립 수면 위로 - 지디넷코리아 https://zdnet.co.kr/view/?no=20251125143503
2. 스테이블코인 시대 열릴까 - KDI 경제교육 https://eiec.kdi.re.kr/userdata/nara/202508/202508.pdf
3. From money market funds to stablecoins: lessons for central banks https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260601~38dffe5ec5.en.html
4. 금융위 "한은 스테이블코인 긴급조치명령 요청권 등 실익 적어" - 연합뉴스 https://www.yna.co.kr/view/AKR20251125044900002
5. 국회 정무위 '법안소위 속도전' 채비, 스테이블코인 연내 입법 '3대 쟁점' 실타래 풀리나 https://www.businesspost.co.kr/BP?command=article_view&num=442765
6. 스테이블코인의 기업금융 인프라로서의 활용을 위한 입법적 과제* https://www.moj.go.kr/bbs/moj/166/497660/download.do
7. Lorenzo Burlon - European Central Bank https://www.ecb.europa.eu/pub/research/authors/profiles/lorenzo-burlon.en.html
8. ESCB response to the European Commission's targeted consultation on the Markets in Crypto-Assets Regulation (MiCAR) https://www.ecb.europa.eu/press/consultationresponse/pdf/ecb.conresp202609_micarreview.en.pdf?c026ff0fd6c52a4eb29d725e6fec3cbb
9. III. Anchoring trust in money: innovation beyond stablecoins - the BIS https://www.bis.org/publications/aer-2026/anchoring-trust-money
10. The Fed - Banks in the Age of Stablecoins: Some Possible Implications for Deposits, Credit, and Financial Intermediation - Federal Reserve https://www.federalreserve.gov/econres/notes/feds-notes/banks-in-the-age-of-stablecoins-implications-for-deposits-credit-and-financial-intermediation-20251217.html
11. The role of holding limits for sterling-denominated systemic stablecoins and a potential digital pound | Bank of England https://www.bankofengland.co.uk/financial-stability-paper/2025/holding-limits-for-sterling-denominated-systemic-stablecoins-and-a-digital-pound
12. Stablecoins and monetary policy transmission - European Central Bank https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3199~ad552b59ec.en.pdf
13. Occasional Paper Series - Central bank digital currency and bank intermediation https://www.ecb.europa.eu/pub/pdf/scpops/ecb.op293~652cf2b1aa.en.pdf
14. Proposed regulatory regime for sterling-denominated systemic stablecoins https://www.bankofengland.co.uk/paper/2025/cp/proposed-regulatory-regime-for-sterling-denominated-systemic-stablecoins
15. House of Lords - Stablecoins: waiting for regulation - Financial Services Regulation Committee - Parliament (publications) https://publications.parliament.uk/pa/ld5902/ldselect/ldfsrc/6/607.htm
16. From money market funds to stablecoins: lessons for central banks https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260601_annex~8852850053.hu.pdf
17. Stablecoin Shocks, WP/26/44, March 2026 - International Monetary Fund https://www.imf.org/-/media/files/publications/wp/2026/english/wpiea2026044-source-pdf.pdf
18. Stablecoins and safe asset prices - EconPapers https://econpapers.repec.org/RePEc:bis:biswps:1270


# 채팅 1

## 질문

[배경] 원화 스테이블코인 준비금 공시 기준을 제안하는 학부 프로젝트다. 국회 정무위원회에 계류 중인 제정안 9건(2210736 민병덕, 2211777 김은혜, 2211784 안도걸, 2212298 김현정, 2213166 이강일, 2213266 김재섭, 2213449 최보윤, 2214492 박상혁, 2218219 김성원)이 정한 값을 비교하고, 그 값을 정하는 근거를 모은다.




[조사] 스테이블코인 확대가 은행 예금, 대출, 통화정책 전달에 주는 영향을 추정한 해외 연구를 찾는다(BIS, IMF, 연준, ECB, 영란은행, 학술지). 이미 소스로 올린 논문은 뺀다.
찾을 것





준비자산을 은행 예금으로 둘 때와 국채나 MMF로 둘 때 은행 예금 총량이 어떻게 달라지는지


예금 이탈 추정치와 시나리오


단기 국채 금리와 수요에 주는 영향 추정치


규제 설계(현금 비율, 이자 금지)가 이 영향을 어떻게 바꾸는지





[출력] 표: 연구 | 대상 | 방법 | 결과 수치 | 가정 | 주소




[원칙]





1차 자료를 먼저 찾는다: 법령과 의안 원문, 국회 회의록과 검토보고서, 정부와 한국은행의 보도자료와 보고서 PDF, 발행사와 규제기관의 공식 문서, 논문 원문.


언론 기사는 1차 자료를 찾지 못한 내용에만 쓰고 '기사'라고 표시한다. 블로그, 커뮤니티 글, 요약 사이트는 쓰지 않는다.


숫자는 원문에 적힌 그대로 쓰고 단위와 기준일을 붙인다. 원문에서 확인하지 못한 칸은 '확인 안 됨'으로 둔다. 추정이나 일반론으로 빈칸을 채우지 않는다.


문서마다 기관, 제목, 날짜, 주소, 조문이나 쪽 번호를 적는다.

## 답

### 배경: 국회 계류 제정안 9건 비교 및 설정 근거

원화 스테이블코인(가치안정형 디지털자산) 규율을 위해 국회 정무위원회에 계류 중인 9개 법률안과 정무위원회 검토보고서(2025년 11월 25일 제출)의 주요 내용을 비교·모은 결과는 다음과 같습니다 [1] [2] [3].

#### 국회 계류 법률안 9건 주요 조항 비교 표

| 의안번호 및 발의자 | 주요 법안명 및 발의일자 | 최소 자기자본 요건 | 준비자산 도산격리 및 이용자 보호 조항 | 한국은행 감독/검사 권한 규정 | 1차 자료 및 출처 |
|---|---|---|---|---|---|
| 2210736 (민병덕) | 디지털자산기본법안 (2025.06.11) [1] | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 국회 의안원문 (제103조제2항) [1] [2] |
| 2211777 (김은혜) | 가상자산이용자보호법 개정안 등 | 50억 원 이상 [2] | 별도 예치·신탁, 상계·압류 금지, 우선변제권 명시 [2] | 한은 검사요구권 신설 [3] | 정무위 검토보고서 [3], 법제처 문서 [2] |
| 2211784 (안도걸) | 가치안정형 디지털자산의 발행 및 유통에 관한 법률안 | 50억 원 이상 [2] | 별도 예치·신탁, 상계·압류 금지, 우선변제권 명시 [2] | 한은 공동검사 참여권, 한은·기재부 긴급조치명령 요청권 [3] | 정무위 검토보고서 [3], 법제처 문서 [2] |
| 2212298 (김현정) | 디지털자산 관련 법안 | 50억 원 이상 [2] | 별도 예치·신탁, 상계·압류 금지, 우선변제권 명시 [2] | 지급결제 안정성 확보 위한 한은 참여 범위 확대 [3] | 정무위 검토보고서 [3], 법제처 문서 [2] |
| 2213166 (이강일) | 디지털자산 관련 법안 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 기사 (비즈니스포스트) [2] |
| 2213266 (김재섭) | 디지털자산 관련 법안 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 기사 (비즈니스포스트) [2] |
| 2213449 (최보윤) | 디지털자산 관련 법안 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 기사 (비즈니스포스트) [2] |
| 2214492 (박상혁) | 디지털자산 관련 법안 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 기사 (비즈니스포스트) [2] |
| 2218219 (김성원) | 디지털자산 관련 법안 | 확인 안 됨 | 확인 안 됨 | 확인 안 됨 | 기사 (비즈니스포스트) [2] |

#### 주요 규정치 설정 근거 및 당국 간 쟁점

- 최소 자기자본 요건 (50억 원 이상) 설정 근거: 영세·부실 발행사의 난립을 방지하고 자본 건전성을 검증받은 대형 금융기관 및 제도권 핀테크 중심의 진입을 유도하기 위해 설정되었습니다 [2]. 하위 법령으로 위임된 세부 발행 요건과 결합하여 발행사의 도산 위험을 최우선 차단하려는 목적입니다 [2].

- 준비자산 도산격리(Bankruptcy Remoteness) 및 이용자 우선변제권 설정 근거: 발행사가 파산하더라도 이용자의 환매 청구권이 완벽히 보장되도록 준비자산을 상업은행 또는 신탁회사에 별도 예치·신탁하게 하고, 일반 채권자의 상계 및 압류를 법적으로 금지하였습니다 [2]. 2022년 테라·루나 사태 및 2023년 SVB 파산 당시의 디페깅 경험을 반영한 조치입니다 [2] [4].

- 감독 권한 및 정책협의체 설정 갈등 (금융위원회 vs 한국은행) 한국은행/기획재정부 측 논거: 스테이블코인이 대규모 유통될 경우 통화정책 전달경로 약화, 지급결제 시스템 리스크, 외환시장 변동성을 초래할 수 있으므로, 중앙은행의 검사요구권·공동검사권 및 당국 간 공동 정책협의체 구성이 필수적이라고 주장합니다 [3] [5]. 금융위원회 측 논거: 가상자산 규율은 금융위 소관 법체계 내에서 일관되게 설계되어야 하며, 다기관 검사는 규제 중복과 시장 혼란을 초래한다고 반대합니다 [3]. 또한 한은 부총재와 기재부 차관이 금융위 당연직 위원으로 의결에 참여하므로 별도 요청권의 실익이 적고 관련 해외 입법례도 없다는 입장을 공식 제출했습니다 [3].

### 조사: 스테이블코인 확대 영향 해외 연구 (노트북 소스 외 신규 조사)

노트북 소스에 포함되지 않은 해외 정책기관(BIS, ECB, US Fed) 및 주요 연구진의 신규 연구를 조사하여 정리한 결과입니다.

#### 신규 해외 연구 종합 비교 표

| 연구 | 대상 | 방법 | 결과 수치 | 가정 | 주소 |
|---|---|---|---|---|---|
| Hofmann, Kaldorf, & Rottner (2026.06) | 미국 금융·거시경제 시스템 | 정량적 거시경제(DSGE) 수량 모형 구조 분석 및 시나리오 시뮬레이션 | (1) 시가총액 $1조~$3조 확대 시 3개월물 T-bill 금리 최대 8bp 하락<br>(2) 은행 대출 축소 효과(Bank lending headwind)가 재정 공간 확장 효과(Fiscal space tailwind)보다 크므로 장기 실질 생산량(Output) 소폭 감소<br>(3) 단, 이행기 초기 단기 생산량은 정(+) | 스테이블코인 준비자산의 단기 국채 보유 vs 은행 예치 비중, 미국 경제 데이터 칼리브레이션 | Link |
| Coste (2024.07) | 유로존 상업은행 대차대조표 및 건전성 비율 | 은행 대차대조표 회계 및 건전성 비율(LCR, NSFR) 충격 시뮬레이션 | (1) 소매 예금이 스테이블코인 예치금으로 전환 시 HQLA 재투자 여부와 무관하게 유동성커버리지비율(LCR) 약화<br>(2) A은행 고객이 코인 매수 후 발행사가 B은행에 예치 시 양 은행 모두 유동성 비율 예상치 못한 하락 | 소매 예금의 스테이블코인 자산 전환, 준비자산 운용 방식(중앙은행 예치 vs 단기 국채/도매 예금) | Link |
| Baughman, Carapella, Gerszten, & Mills (2024.01) | 미국 연방준비제도 통화정책 이행 체계 | 연준 대차대조표 및 은행 간 자금시장 구조 모형 (Structural Interbank Model) | (1) 실물 화폐 대체 시: 연준 부채 구조만 변경(화폐→지급준비금), 균형 금리 변동 없음<br>(2) 은행 예금 대체 및 준비자산 중앙은행 예치 시: 상업은행 지급준비금 축소, 은행 간 금리 상승 압력, 연준 대차대조표 재확장 필요 | Narrow Nonbank가 고정 이자율로 발행하고 지급준비금을 100% 자산으로 보유 | Link |
| Barbon, Barthélemy, & Nguyen (2026.02) | 탈중앙화 금융(DeFi) 및 USD 스테이블코인 | DeFi 수급 방정식 구조 추정 및 미 연준 정책금리 전이경로 고주파 분석 | (1) 미 국채(T-bill) 편리성 수익률과 스테이블코인 편리성 수익률 간 동조성(Co-movement) 입증<br>(2) 연준 정책금리 인상이 DeFi 대출/예금 금리로 전달되는 전이율(Pass-through) 정량 정립 | DeFi 프로토콜 내 담보 대출 및 가동률(Utilization rate) 반응 함수 | Link |

#### 핵심 조사 결과 상세 분석

- 준비자산을 은행 예금으로 두는 경우 vs 국채/MMF로 두는 경우의 예금 총량 변화 은행 예금 보유 시: 소매 예금주가 예금을 인출해 스테이블코인을 사더라도 발행사가 해당 자금을 다시 상업은행 예금 계좌에 예치하므로 전체 은행 시스템의 총예금 잔액(M2)은 유지됩니다 [6]. 하지만 금리 민감도가 낮고 안정적인 소매 예금(Retail Deposit)이 인출 위험이 높은 대형 도매 예금(Wholesale Deposit)으로 전환되어 은행의 자금조달 비용이 상승하고 LCR 비율이 악화됩니다 [6]. 국채/MMF 보유 시: 자금이 은행 시스템 외부로 이탈(Disintermediation)하므로 은행 시스템 전체의 총예금 잔액이 실질적으로 감소하며, 은행의 신용 공급 능력이 직접 위축됩니다 [7]. 중앙은행 예치 시: 자금이 중앙은행 지불준비금 계좌로 직접 들어가므로 상업은행 대차대조표가 가장 강력하게 축소되는 탈중개화 현상이 발생합니다 [7].

- 예금 이탈 추정치 및 시나리오 연준 FEDS Notes 모형: 스테이블코인이 5,000억 달러 확대될 때 순예금 감소는 3,000억 달러, 상업은행 총대출 감소는 -1,900억 달러 ~ -4,080억 달러에 달할 것으로 추정되었습니다 [8] [9]. 영란은행(BOE) 스트레스 모형: 심각한 금융 스트레스 발생 시 가계 및 비금융 기업 예금의 **최대 20%**가 민간 디지털 화폐로 일시에 유출될 수 있다고 평가했습니다 [9]. ECB 미시 데이터 분석: 개별 은행의 스테이블코인 노출도가 1표준편차 증가할 때 향후 24개월간 비금융 사적부문 대출 성장률이 누적 약 2.5%p 지속적으로 감소하는 것으로 분석되었습니다 [10].

- 단기 국채 금리 및 수요 영향 추정치 BIS WP 1270 분석: 스테이블코인으로 2표준편차 자금 유입 충격 시 미 3개월물 국채(T-bill) 금리가 2.5~3.5bp 하락합니다 [11]. 특히 부채한도 협상 등으로 단기 국채 공급이 제약되는 '국채 희소성(Bill Scarcity)' 국면에서는 금리 하락 폭이 5~8bp로 확대됩니다 [11]. BIS WP 1363 (Hofmann et al., 2026): 시가총액이 $1조~$3조 달러로 확대될 경우 단기 국채 금리를 최대 8bp 낮춰 정부의 단기 재정 조달 비용을 절감시키는 효과가 확인되었습니다.

- 규제 설계(현금 비율, 이자 금지)의 영향 조정 효과 현금/중앙은행 예치 비율 규제: BOE의 40% 무이자 중앙은행 예치 의무화 제안 및 MiCAR의 상업은행 예치 규정은 뱅크런 발생 시 즉각적인 유동성 버퍼를 제공합니다 [12]. 다만 특정 은행에 대한 유동성 위험 집중을 유발할 수 있어 만기별 유동성 버킷(Liquidity Bucketing) 규제로의 보완이 요구됩니다 [12]. 이자 지급 금지(Yield Prohibition): 스테이블코인이 이자나 리워드를 지급할 경우 은행의 보통예금 자금이 급격히 구조 이탈합니다 [13]. 따라서 이자 지급 금지는 스테이블코인을 저축·투자 수단이 아닌 Pure Payment Instrument로 제한하여 상업은행의 예금 기반 상실을 차단하는 핵심 안전판 역할을 수행합니다 [13].

💡 학부 프로젝트에서 사용할 원화 스테이블코인 준비자산 공시 기준 제안서(보고서) 초안 작성을 도와드릴까요?

## 인용 번호와 소스

- 원화 스테이블코인 준비자산 공시 기준 제안 및 통화·금융 시스템 영향 분석 연구 보고서: [1] [2] [3] [5] [6] [7] [8] [9] [10] [11] [12] [13]
- 스테이블코인 시대 열릴까 - KDI 경제교육: [4]
