# C-1 국내 비슷한 제도의 기준값

- 노트북: https://notebook.google.com/notebook/c6cfd196-c876-4522-8621-8c0e69c6fca0?authuser=1 (자동 제목 "가상자산 이용자 보호 및 전자금융 규제법령")
- 보고서 제목: 원화 스테이블코인 준비금 공시 기준 제안 및 국내 자산 분리보관·유동성 규제 비교 연구
- 소스 34종, 보고서 참고 링크 26개, 본문 12146자
- 실행 방식: Deep Research
- 수집: 2026-10-06 Aside repl, 원문 대조 전

---
# 원화 스테이블코인 준비금 공시 기준 제안 및 국내 자산 분리보관·유동성 규제 비교 연구

## 서론 및 국회 계류 제정안(9건)의 입법 동향

가상자산 생태계의 고도화와 함께 법화에 연동하여 가치의 안정을 도모하는 스테이블코인(Stablecoin)의 시스템적 중요성이 증대하고 있다. 원화(KRW)에 연동되는 원화 스테이블코인의 경우, 발행 잔액에 상응하는 준비금(Reserve Assets)의 실재성, 유동성, 그리고 안전성을 확보하는 것이 상환 불능 리스크 및 금융 시스템으로의 위험 전이를 차단하기 위한 핵심 전제 조건이다. 이러한 요구에 부응하여 제22대 국회 정무위원회에는 가치안정형 또는 가치고정형 디지털자산의 발행 및 유통 체계를 규율하기 위한 제정 법률안 9건이 발의되어 계류 중이다 [cite: 1].

발의된 9건의 제정안은 민병덕의원 대표발의안(의안번호 2210736), 김은혜의원 대표발의안(의안번호 2211777, 가치고정형 디지털자산을 활용한 지급 혁신에 관한 법률안), 안도걸의원 대표발의안(의안번호 2211784, 가치안정형 디지털자산의 발행 및 유통에 관한 법률안), 김현정의원 대표발의안(의안번호 2212298, 가치안정형 디지털자산 발행업 등에 관한 법률안), 이강일의원 대표발의안(의안번호 2213166), 김재섭의원 대표발의안(의안번호 2213266), 최보윤의원 대표발의안(의안번호 2213449), 박상혁의원 대표발의안(의안번호 2214492), 그리고 김성원의원 대표발의안(의안번호 2218219)을 포함한다 [cite: 1].

해당 법안들의 입법 취지와 법문 구조를 종합적으로 분석하면, 원화 스테이블코인의 준비금 관리에 관하여 공통적으로 적용되는 입법적 지향점을 도출할 수 있다 [cite: 1]. 첫째, 스테이블코인 발행 잔액 대비 100% 이상의 준비금을 고유재산과 분리하여 공신력 있는 기관에 별도 관리해야 한다. 둘째, 준비금의 운용 수단은 국채, 지방채, 정부보증채권 및 금융기관 예치금 등 신용 리스크가 극히 낮은 고유동성 안전자산으로 한정된다. 셋째, 발행사의 파산이나 인가 취소 등 유사시 이용자가 준비금에 대해 우선변제권을 행사할 수 있도록 법적 보호 장치를 마련하고, 정기적인 외부 검증과 공시를 통해 투명성을 확보하도록 규정한다.

## 국내 주요 고객 자산 분리보관 및 유동성 규제 체계 상세 분석

원화 스테이블코인의 하위 감독규정 및 준비금 공시 기준을 수립하기 위해서는 국내 전통 금융권과 가상자산업권에서 이미 시행 중인 고객 자산 분리보관 및 유동성 규제 제도를 체계적으로 검토할 필요가 있다.

### 투자자예탁금 (자본시장과 금융투자업에 관한 법률)

자본시장법상 투자자예탁금 제도는 금융투자업자가 투자자로부터 받은 금전을 보호하기 위한 대표적인 자산 분리보관 장치다. 자본시장법 제74조제1항에 따라 Investment Broker나 Dealer 등 금융투자업자는 투자자예탁금을 자신의 고유재산과 엄격히 구분하여 증권금융회사(한국증권금융)에 예치하거나 신탁해야 한다 [cite: 2]. 동법 시행령 제74조제1항은 예치받은 증권금융회사가 해당 예탁금을 운용할 수 있는 금융기관의 범위를 은행, 한국산업은행, 중소기업은행, 보험회사, 금융투자업자 및 종합금융회사 등으로 한정하여 자산의 안전성을 도모하고 있다 [cite: 3, 4].

투자자예탁금의 반환 절차와 관련하여 자본시장법 제74조제5항 및 시행령 제73조제1항은 예치금융투자업자의 파산, 인가 취소, 영업정지 등의 사유가 발생한 경우 예치기관이 금융위원회의 통지를 받아 사유 발생일부터 2개월 이내에 지급공고를 실시하고, 투자자의 청구에 따라 예탁금을 직접 지급하도록 규정한다 [cite: 3, 4, 5, 6]. 불가피한 사유가 인정될 경우 금융위원회의 확인을 거쳐 1개월의 범위에서 지급공고 기한을 연장할 수 있다 [cite: 3, 4]. 반면, 자본시장법령 및 금융투자업규정상 투자자예탁금 자체의 별도 운용 비율, 자산 잔존만기 제한, 또는 현금성 자산 비율 기준 등은 명시적인 숫자로 제시되어 있지 않다 [cite: 7].

### 가상자산 이용자 예치금 (가상자산 이용자 보호 등에 관한 법률)

2024년 7월 19일부터 시행된 가상자산이용자보호법 제6조제1항은 가상자산사업자(VASP)가 이용자로부터 가상자산 매매 및 중개와 관련하여 예치받은 금전을 고유재산과 분리하여 「은행법」에 따른 은행, 농협은행, 수협은행, 중소기업은행 등 공신력 있는 관리기관에 예치하거나 신탁하도록 의무화하고 있다 [cite: 8]. 동법 시행령 제5조제3항에 따라 가상자산사업자가 관리기관에 예치·신탁해야 하는 금액은 이용자별 예치금 총액의 100분의 100 이상이어야 한다 [cite: 8, 9].

관리기관의 운용방법과 관련하여 관리기관은 국채증권 및 지방채증권의 매수 등 예치금의 안전한 운용을 해할 우려가 없는 방식으로 자금을 운용해야 한다 [cite: 10]. 가상자산업감독규정 제5조에 따라 가상자산사업자는 예치금의 운용수익과 발생비용을 고려하여 이용자에게 예치금이용료를 지급해야 하며, 국세청의 유권해석(2024년 7월 19일 회신)에 따라 가상자산사업자가 이용자에게 지급하는 예치금이용료는 소득세법 제16조제1항제12호에 따른 이자소득으로 과세된다 [cite: 8, 10]. 가상자산사업자의 인가 취소, 영업정지, 해산 또는 파산 등의 사유가 발생할 경우 관리기관은 예치금 총액 한도 내에서 이용자에게 예치금을 직접 우선 지급하며, 별도의 잔존만기 상한 규정은 명시되어 있지 않다 [cite: 9, 11].

### 선불충전금 (전자금융거래법)

개정 전자금융거래법 제25조의2(법률 제21205호, 2023년 9월 14일 신설, 2025년 12월 16일 시행) 및 동법 시행령 제13조의2(대통령령 제36281호, 2024년 9월 10일 신설 및 2026년 4월 28일 타법개정)는 선불충전금의 보호 체계를 대폭 강화하였다 [cite: 12, 13, 14, 15, 16]. 전자금융거래법 제25조의2제1항은 선불충전금의 100분의 50 이상에 해당하는 금액을 별도 관리하도록 법률상 최소 기준을 두고 있으나 [cite: 14, 15], 개정 시행령 제13조의2제2항 및 전자금융감독규정(2024년 9월 15일 시행)은 선불충전금 전액, 즉 100분의 100 이상을 신탁, 예치, 또는 지급보증보험의 방법으로 별도 관리하도록 규정하고 있다 [cite: 13, 16, 17].

별도 관리의 방법 중 신탁의 경우 「자본시장과 금융투자업에 관한 법률 시행령」 제103조제1호에 따른 특정금전신탁으로 한정되며 [cite: 13], 예치는 은행 및 체신관서로 제한된다 [cite: 17]. 운용 가능한 자산 범위는 은행·체신관서 예치, 국채증권 및 지방채증권 매수, 정부·지방자치단체 또는 은행이 지급을 보증한 채권 매수, 특수채(한국전력공사채 등) 매수, 은행이 발행한 양도성예금증서(CD) 매수, 후순위채와 주식관련채를 제외한 은행채 매수, 그리고 한국주택금융공사가 발행한 주택저당증권(MBS) 매수로 제한된다 [cite: 17]. 선불업자는 매 영업일 별도관리 금액의 적정성을 점검해야 하며, 등록 취소, 해산, 파산 등 사유 발생 시 관리기관이 이용자에게 선불충전금을 우선 지급하도록 규정되어 있다 [cite: 17].

### MMF (단기금융집합투자기구 - 자본시장법)

자본시장법 시행령 제80조제1항 및 금융투자업규정 제7-14조에 규정된 MMF(Money Market Fund)는 초단기 금융상품에 투자하는 집합투자기구로서 잔존만기 및 현금성 자산 비율에 대해 가장 구체적인 정량 기준을 적용받는다 [cite: 18, 19]. MMF가 편입할 수 있는 개별 채권 자산의 잔존만기 상한은 1년 이하이며, 국채증권의 경우 5년 이하까지 허용된다 [cite: 20]. 집합투자재산 전체의 가중평균잔존만기(WAM) 상한은 장부가평가 MMF의 경우 90일 이하로 제한된다 [cite: 18, 20].

2021년 3월 금융위원회 개정 금융투자업규정에 따라 법인형 MMF의 경우 자산 구성에 따라 규제가 차등화된다 [cite: 21]. 국채 및 통안채 편입 비율이 30% 이하인 시가평가 법인형 MMF는 가중평균잔존만기 한도가 120일 이하로 완화되는 반면, 국채 및 통안채 편입 비율이 30%를 초과하는 장부가평가 법인형 MMF는 가중평균잔존만기 규제가 60일 이하로 엄격히 단축된다 [cite: 21]. 또한 MMF는 대규모 환매 요구에 대응하기 위해 1일 및 7일 이내에 현금화할 수 있는 고유동성 자산 비율 기준을 준수해야 하며, 환매조건부채권(RP) 매수 및 운용 한도 통제를 받는다 [cite: 20, 21].

### 은행 유동성커버리지비율 (LCR - 은행업감독규정)

은행업감독규정 제26조제1항제2호 및 [별표 3의6]은 바젤 III 국제 금융 규범에 따라 은행의 단기 유동성 복원력을 측정하는 유동성커버리지비율(LCR) 기준을 명시한다 [cite: 22, 23]. LCR은 심각한 유동성 스트레스 시나리오 하에서 향후 30일간 예상되는 순현금유출액 대비 즉시 현금화할 수 있는 고유동성자산(HQLA)의 비율로서 100% 이상을 지속적으로 유지해야 한다 [cite: 22, 23, 24].

고유동성자산(HQLA)은 리스크와 유동성에 따라 3단계 구조로 구분된다 [cite: 23]. Level 1 자산은 현금, 중앙은행 지급준비금, 위험가중치 0%인 국가 및 중앙은행 발행 채권 등으로 구성되며, 할인율(Haircut) 0%가 적용되고 전체 HQLA 산정 시 편입 한도 제한이 없다 [cite: 23]. Level 2A 자산은 위험가중치 20%인 국가·공공기관 채권 및 우량 회사채 등으로 15%의 할인율이 적용되며 전체 HQLA의 최대 40%까지만 인정된다 [cite: 23]. Level 2B 자산은 적격 주택담보대출유동화증권(RMBS, 장기신용등급 AA 이상, 할인율 25%) 및 회사채/CP(장기신용등급 A+~BBB-, 할인율 50%)를 포함하며, 전체 HQLA의 최대 15% 한도로 제한되고 Level 2 전체 40% 한도에 포함된다 [cite: 23].

## 원화 스테이블코인 준비금 공시 체계 구축을 위한 종합 제언

국내 5개 자산 관리 및 유동성 제도의 분석 결과를 원화 스테이블코인 준비금 규제 체계에 적용할 경우, 발행사의 안정성과 유동성을 동시에 확보할 수 있는 3대 감독 기준을 정립할 수 있다.

첫째, 자산 분리보관 및 우선지급권 제도는 가상자산이용자보호법 및 전자금융거래법의 입법례를 준용하여 준비금의 100% 이상을 은행 예치, 특정금전신탁, 또는 지급보증보험으로 별도 관리하도록 의무화해야 한다 [cite: 8, 9, 13, 17]. 발행사의 영업정지, 파산 등 유사시 관리기관이 이용자에게 준비금을 직접 우선 지급하는 절차를 명확히 법제화함으로써 Credit Risk를 차단해야 한다 [cite: 9, 17].

둘째, 준비금 자산의 운용 범위와 만기 구조는 MMF 규제와 은행 LCR 자산 분류 체계를 결합하여 설계해야 한다. 전체 준비금 자산의 가중평균잔존만기(WAM)를 60일 이하로 제한하고 [cite: 21], 개별 자산의 잔존만기 상한을 1년(국채 5년) 이하로 통제해야 한다 [cite: 20]. 자산 구성 측면에서는 현금 및 중앙은행 예치금 등 Level 1 초고유동성 자산을 최소 30% 이상 유지하도록 강제하고, 1일 및 7일 이내 현금화 가능 자산 비율을 설정하여 뱅크런 발생 시의 환매 요구에 즉각 대응할 수 있도록 해야 한다 [cite: 20, 21, 23].

셋째, 공시의 주기와 검증 수준을 다층화해야 한다. 발행사는 매 영업일 기준 총 발행 잔액과 준비금 적립액, 그리고 초고유동성 자산 비중을 공시하고, 매월 독립된 회계법인의 준비금 검증 보고서(Attestation Report)를 제출받아 공시하도록 의무화함으로써 시장의 신뢰를 확보해야 한다.

## 국내 자산 분리보관 및 유동성 규제 종합 비교표

아래 표는 국내 5개 자산 분리보관 및 유동성 규제 제도의 원문 조문, 보관 방법, 운용 자산, 만기 및 현금성 비율 기준, 돌려주는 기한 및 원문 인용을 비교·정리한 결과다.

| 제도 | 조항 | 보관 방법 | 운용할 수 있는 자산 | 만기 제한 | 현금성 비율 기준 | 돌려주는 기한 | 원문 인용 |
|---|---|---|---|---|---|---|---|
| 투자자예탁금 | 자본시장법 제74조 [cite: 2, 5], 동법 시행령 제73조~제75조 [cite: 3, 4, 6], 금융투자업규정 제4-74조 [cite: 7] | 증권금융회사(한국증권금융) 예치 또는 신탁 [cite: 2] | 자본시장법 시행령 제74조제1항 각 호의 금융기관(은행, 한국산업은행, 중소기업은행, 보험회사, 투자매매·중개업자, 증권금융회사, 종합금융회사 등)에 대한 예치 [cite: 3, 4] | 확인 안 됨 | 확인 안 됨 | 예치금융투자업자의 파산, 인가취소 등 사유 발생일로부터 2개월 이내 지급공고(금융위원회 확인으로 1개월 연장 가능) 후 예치기관이 직접 지급 [cite: 3, 4, 5, 6] | 자본시장법 제74조제1항: "투자매매업자 또는 투자중개업자는 투자자예탁금을 고유재산과 구분하여 증권금융회사에 예치 또는 신탁하여야 한다." [cite: 2] / 동법 시행령 제73조제1항: "사유가 발생한 날부터 2개월... 1개월의 범위에서 그 기간을 연장할 수 있다." [cite: 3, 4] |
| 가상자산 이용자 예치금 | 가상자산 이용자 보호 등에 관한 법률 제6조 [cite: 8, 9], 동법 시행령 제5조·제8조 [cite: 8], 가상자산업감독규정 제5조 [cite: 8] | 은행, 농협은행, 수협은행, 중소기업은행 등 관리기관 예치 또는 신탁 [cite: 8] | 국채증권 매수, 지방채증권 매수 등 예치금의 안전한 운용을 해할 우려가 없는 방법 [cite: 10] | 확인 안 됨 | 이용자별 예치금 총액의 100분의 100 이상 [cite: 8, 9] | 가상자산사업자의 인가취소, 영업정지, 해산, 파산 등 사유 발생 시 관리기관에 예치·신탁되어 있는 예치금 총액 한도 내에서 이용자에게 직접 우선 지급 [cite: 9, 11] | 가상자산 이용자 보호 등에 관한 법률 제6조제1항: "가상자산사업자는 이용자의 예치금...을 고유재산과 분리하여 「은행법」에 따른 은행 등... 관리기관에 예치 또는 신탁하여 관리하여야 한다." [cite: 8] / 동법 시행령 제5조제3항: "예치 또는 신탁해야 하는 예치금은 이용자별 예치금... 총액의 100분의 100 이상으로 한다." [cite: 8, 9] |
| 선불충전금 | 전자금융거래법 제25조의2 [cite: 12, 13, 14, 15, 16], 동법 시행령 제13조의2 [cite: 13, 16, 25], 전자금융감독규정 [cite: 16] | 은행·체신관서 예치 [cite: 17], 신탁(자본시장법 시행령 제103조제1호 특정금전신탁) [cite: 13], 지급보증보험 가입을 통한 별도관리 [cite: 13, 15, 16, 17] | 은행·체신관서 예치, 국채·지방채 매수, 정부·지자체·은행 지급보증 채권 매수, 특수채(한전채 등) 매수, 은행 발행 양도성예금증서(CD) 매수, 은행채(후순위·주식관련채 제외), 한국주택금융공사 주택저당증권(MBS) 매수 [cite: 17] | 확인 안 됨 | 법률상 100분의 50 이상 [cite: 14, 15], 시행령상 선불충전금의 100분의 100 이상 별도관리 [cite: 16, 17] | 허가·등록 취소·말소, 해산의 결의, 파산선고, 전자금융업무 정지명령 등 지급 사유 발생 시 관리기관이 이용자에게 우선 지급 [cite: 17] | 전자금융거래법 제25조의2제1항: "선불충전금...의 100분의 50 이상에 해당하는 금액으로서... 별도관리하여야 한다." [cite: 14, 15] / 동법 시행령 제13조의2제2항: "선불충전금의 100분의 100 이상을 별도관리하도록 하고..." [cite: 17] |
| MMF (단기금융 집합투자기구) | 자본시장법 시행령 제80조 [cite: 18], 금융투자업규정 제7-14조 [cite: 19] | 집합투자재산 신탁업자 보관 | 잔존만기 1년 이하 채권(국채는 5년 이하), 단기금융상품 [cite: 20] | 개별 자산 잔존만기 1년 이하(국채 5년 이하) [cite: 20], 전체 가중평균잔존만기(WAM) 90일 이하 [cite: 18, 20] (시가평가 법인형 MMF 120일 이하, 장부가평가 법인형 MMF 60일 이하) [cite: 21] | 1일 및 7일 이내 현금화 가능 자산 비율 기준 적용 [cite: 20, 21], RP 운용 한도 규제 [cite: 20] | 확인 안 됨 | 금융투자업규정 제7-14조제2호: "'가중평균잔존만기'란 단기금융집합투자기구에서 운용하는 개별자산등..." [cite: 19] / 자본시장법 시행령 제80조제1항: "가중평균잔존만기 < 90일" [cite: 18, 20] |
| 은행 유동성 커버리지비율 (LCR) | 은행업감독규정 제26조제1항제2호, [별표 3의6] 유동성커버리지비율 산출 기준 [cite: 23] | 은행 자체 고유동성자산(HQLA) 보유 및 중앙은행 예치 [cite: 22, 23, 26] | Level 1 자산(현금, 중앙은행 예치금, 위험가중치 0% 국채 등) [cite: 23], Level 2A 자산(위험가중치 20% 채권, 우량 회사채 등) [cite: 23], Level 2B 자산(적격 RMBS, A+~BBB- 회사채/CP 등) [cite: 23] | 30일간 스트레스 상황 대비 유동성 관리 [cite: 22, 23, 26] | LCR= 향후 30일간 순현금유출액 고유동성자산(HQLA) ​ ≥100% [cite: 22, 24]; Level 2 자산 상한 40% [cite: 23], Level 2B 자산 상한 15% [cite: 23] | 해당 없음 | 은행업감독규정 [별표 3의6]: "'유동성커버리지비율 및 외화 유동성커버리지비율'은 향후 30일간 순현금유출액에 대한 고유동성 자산 보유규모 비율을 말한다." [cite: 23] |

---

- 제429회 국회(정기회) 제10차 정무위원회 [10:30] - YouTube, https://www.youtube.com/watch?v=Aa1rUBmgz8U

- 자산운용사의 정리제도에 대한 소고*, https://scc.sogang.ac.kr/Download?pathStr=NTIjIzUwIyM1MiMjMTI0IyMxMDQjIzExNiMjOTcjIzgwIyMxMDEjIzEwOCMjMTA1IyMxMDIjIzM1IyMzMyMjMzUjIzQ5IyMxMjQjIzEyMCMjMTAxIyMxMDAjIzExMCMjMTA1IyMzNSMjMzMjIzM1IyM1MSMjNTEjIzQ5IyM1MSMjNTcjIzU2IyMxMjQjIzEwMCMjMTA1IyMxMDcjIzExMg==&fileName=%EC%A0%9C13%EA%B6%8C1%ED%98%B8_04+%EC%A0%95%EB%AF%BC%ED%9D%AC.pdf&gubun=board

- 자본시장과 금융투자업에 관한 법률 시행령 - 국가법령정보센터, https://www.law.go.kr/lsInfoP.do?lsiSeq=208041

- 자본시장과 금융투자업에 관한 법률 시행령 - 국가법령정보센터, https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=91521

- 자본시장 제도동향, https://www.kcmi.re.kr/common/downloadw?fid=24512&fgu=002001004&fty=004003

- 자본시장과 금융투자업에 관한 법률 시행령 - 국가법령정보센터, https://www.law.go.kr/LSW//lsInfoP.do?lsId=010817&ancYnChk=0

- 행정규칙 > 금융투자업규정 - 국가법령정보센터, https://www.law.go.kr/admRulLsInfoP.do?admRulSeq=2100000222822

- [예규] 가상자산사업자가 이용자에게 지급하는 예치금이용료의 소득구분(서면, https://www.bkl.co.kr/law/insight/newsletter/5762

- 법령 > 본문 > 가상자산 이용자 보호 등에 관한 법률 시행령, https://www.law.go.kr/LSW//lsInfoP.do?lsiSeq=290171&chrClsCd=010202&urlMode=lsInfoP&efYd=20261002&ancYnChk=0

- [국세 예규] 가상자산사업자의 이용자 지급 예치금이용료....“이자소득에 해당” - 일간NTN, https://www.intn.co.kr/news/articleView.html?idxno=2037564

- 행정규칙 > 가상자산업감독규정 - 국가법령정보센터, https://www.law.go.kr/LSW//admRulInfoP.do?admRulSeq=2100000244180&chrClsCd=010201

- 전자금융거래법 개정안 살펴보기 - 법률사무소 인평, https://inpyeonglaw.com/archives/25100/

- 전자금융거래법 시행령 - 국가법령정보센터, https://www.law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1026222729

- 전자금융거래법 - 국가법령정보센터 | 변경조문, https://www.law.go.kr/LSW/lsSideInfoP.do?docCls=jo&joBrNo=02&joNo=0025&lsiSeq=280277&urlMode=lsScJoRltInfoR

- 전자금융거래법 - 국가법령정보센터, https://law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1025295349

- [금융규제] 개정 「전자금융거래법」 시행 - 법무법인 지평, https://www.jipyong.com/kr/board/news_view.php?seq=13382

- 전자금융거래법 시행령, https://www.fsc.go.kr/comm/getFile?srvcId=RULENOTICE&upperNo=3990&fileTy=ATTACH&fileNo=8

- 전체화면 | 모범규준 | 금융투자회사의 컴플라이언스 매뉴얼 Ⅲ편(자산운용), https://law.kofia.or.kr/service/law/lawFullScreen.do?seq=262&historySeq=756

- 금융투자회사의 컴플라이언스 매뉴얼 Ⅲ편(자산운용) | 규정내용, https://law.kofia.or.kr/service/law/lawFullScreenContent.do?seq=262&historySeq=755

- 투자전략 - 미래에셋증권, https://securities.miraeasset.com/bbs/board/message/view.do?messageId=2223981&messageNumber=201&messageCategoryId=0&startId=002lC%7E&startPage=191&curPage=199&searchType=2&searchText=&searchStartYear=2017&searchStartMonth=02&searchStartDay=12&searchEndYear=2018&searchEndMonth=02&searchEndDay=12&lastPageFlag=&categoryId=1167

- 시가평가에 환매제한까지…규제 거세지는 160조 MMF 시장 - 연합인포맥스, https://news.einfomax.co.kr/news/articleView.html?idxno=4189867

- 유동성커버리지비율 - 한경용어사전 - 한국경제, https://dic.hankyung.com/apps/economy.view?seq=11038

- 유동성커버리지비율 산출 기준, https://www.law.go.kr/LSW/flDownload.do?flSeq=138575461&flNm=%5B%EB%B3%84%ED%91%9C+3%EC%9D%986%5D+%EC%9C%A0%EB%8F%99%EC%84%B1%EC%BB%A4%EB%B2%84%EB%A6%AC%EC%A7%80%EB%B9%84%EC%9C%A8+%EC%82%B0%EC%B6%9C+%EA%B8%B0%EC%A4%80&bylClsCd=200201

- 미국, 유동성커버리지비율(LCR) 시행방안 확정과 시사점 - 보험연구원, https://www.kiri.or.kr/pdf/%EC%A0%84%EB%AC%B8%EC%9E%90%EB%A3%8C/KIRI_20141002_16338.pdf

- 전자금융거래법 시행령, http://mobile.yeslaw.com/lims/front/page/fulltext.html?pAct=view&pPromulgationNo=216798

- 유동성을 규제하는 이유는? | 경제로 세상 읽기 | KDI 경제교육·정보센터, https://eiec.kdi.re.kr/material/pageoneView.do?idx=1878

## 참고 링크(보고서 끝 목록)

1. 제429회 국회(정기회) 제10차 정무위원회 [10:30] - YouTube https://www.youtube.com/watch?v=Aa1rUBmgz8U
2. 자산운용사의 정리제도에 대한 소고* https://scc.sogang.ac.kr/Download?pathStr=NTIjIzUwIyM1MiMjMTI0IyMxMDQjIzExNiMjOTcjIzgwIyMxMDEjIzEwOCMjMTA1IyMxMDIjIzM1IyMzMyMjMzUjIzQ5IyMxMjQjIzEyMCMjMTAxIyMxMDAjIzExMCMjMTA1IyMzNSMjMzMjIzM1IyM1MSMjNTEjIzQ5IyM1MSMjNTcjIzU2IyMxMjQjIzEwMCMjMTA1IyMxMDcjIzExMg==&fileName=%EC%A0%9C13%EA%B6%8C1%ED%98%B8_04+%EC%A0%95%EB%AF%BC%ED%9D%AC.pdf&gubun=board
3. 자본시장과 금융투자업에 관한 법률 시행령 - 국가법령정보센터 https://www.law.go.kr/lsInfoP.do?lsiSeq=208041
4. 자본시장과 금융투자업에 관한 법률 시행령 - 국가법령정보센터 https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq=91521
5. 자본시장 제도동향 https://www.kcmi.re.kr/common/downloadw?fid=24512&fgu=002001004&fty=004003
6. 자본시장과 금융투자업에 관한 법률 시행령 - 국가법령정보센터 https://www.law.go.kr/LSW//lsInfoP.do?lsId=010817&ancYnChk=0
7. 행정규칙 > 금융투자업규정 - 국가법령정보센터 https://www.law.go.kr/admRulLsInfoP.do?admRulSeq=2100000222822
8. [예규] 가상자산사업자가 이용자에게 지급하는 예치금이용료의 소득구분(서면 https://www.bkl.co.kr/law/insight/newsletter/5762
9. 법령 > 본문 > 가상자산 이용자 보호 등에 관한 법률 시행령 https://www.law.go.kr/LSW//lsInfoP.do?lsiSeq=290171&chrClsCd=010202&urlMode=lsInfoP&efYd=20261002&ancYnChk=0
10. [국세 예규] 가상자산사업자의 이용자 지급 예치금이용료....“이자소득에 해당” - 일간NTN https://www.intn.co.kr/news/articleView.html?idxno=2037564
11. 행정규칙 > 가상자산업감독규정 - 국가법령정보센터 https://www.law.go.kr/LSW//admRulInfoP.do?admRulSeq=2100000244180&chrClsCd=010201
12. 전자금융거래법 개정안 살펴보기 - 법률사무소 인평 https://inpyeonglaw.com/archives/25100/
13. 전자금융거래법 시행령 - 국가법령정보센터 https://www.law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1026222729
14. 전자금융거래법 - 국가법령정보센터 | 변경조문 https://www.law.go.kr/LSW/lsSideInfoP.do?docCls=jo&joBrNo=02&joNo=0025&lsiSeq=280277&urlMode=lsScJoRltInfoR
15. 전자금융거래법 - 국가법령정보센터 https://law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1025295349
16. [금융규제] 개정 「전자금융거래법」 시행 - 법무법인 지평 https://www.jipyong.com/kr/board/news_view.php?seq=13382
17. 전자금융거래법 시행령 https://www.fsc.go.kr/comm/getFile?srvcId=RULENOTICE&upperNo=3990&fileTy=ATTACH&fileNo=8
18. 전체화면 | 모범규준 | 금융투자회사의 컴플라이언스 매뉴얼 Ⅲ편(자산운용) https://law.kofia.or.kr/service/law/lawFullScreen.do?seq=262&historySeq=756
19. 금융투자회사의 컴플라이언스 매뉴얼 Ⅲ편(자산운용) | 규정내용 https://law.kofia.or.kr/service/law/lawFullScreenContent.do?seq=262&historySeq=755
20. 투자전략 - 미래에셋증권 https://securities.miraeasset.com/bbs/board/message/view.do?messageId=2223981&messageNumber=201&messageCategoryId=0&startId=002lC%7E&startPage=191&curPage=199&searchType=2&searchText=&searchStartYear=2017&searchStartMonth=02&searchStartDay=12&searchEndYear=2018&searchEndMonth=02&searchEndDay=12&lastPageFlag=&categoryId=1167
21. 시가평가에 환매제한까지…규제 거세지는 160조 MMF 시장 - 연합인포맥스 https://news.einfomax.co.kr/news/articleView.html?idxno=4189867
22. 유동성커버리지비율 - 한경용어사전 - 한국경제 https://dic.hankyung.com/apps/economy.view?seq=11038
23. 유동성커버리지비율 산출 기준 https://www.law.go.kr/LSW/flDownload.do?flSeq=138575461&flNm=%5B%EB%B3%84%ED%91%9C+3%EC%9D%986%5D+%EC%9C%A0%EB%8F%99%EC%84%B1%EC%BB%A4%EB%B2%84%EB%A6%AC%EC%A7%80%EB%B9%84%EC%9C%A8+%EC%82%B0%EC%B6%9C+%EA%B8%B0%EC%A4%80&bylClsCd=200201
24. 미국, 유동성커버리지비율(LCR) 시행방안 확정과 시사점 - 보험연구원 https://www.kiri.or.kr/pdf/%EC%A0%84%EB%AC%B8%EC%9E%90%EB%A3%8C/KIRI_20141002_16338.pdf
25. 전자금융거래법 시행령 http://mobile.yeslaw.com/lims/front/page/fulltext.html?pAct=view&pPromulgationNo=216798
26. 유동성을 규제하는 이유는? | 경제로 세상 읽기 | KDI 경제교육·정보센터 https://eiec.kdi.re.kr/material/pageoneView.do?idx=1878
