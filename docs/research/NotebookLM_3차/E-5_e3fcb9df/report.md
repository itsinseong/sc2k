# E-5 발행사 약관 표

- 노트북: https://notebook.google.com/notebook/e3fcb9df-2d2b-442a-bc8c-9023a871cff2?authuser=1 (자동 제목 "스테이블코인 위기와 대응 현황")
- 보고서 제목: 주요 디지털 자산 및 스테이블코인 발행사별 상환 약관 분석 보고서
- 소스 30종(소스 31개), 보고서 참고 링크 27개, 채팅 답 1건, 본문 16979자
- 실행 방식: 채팅용 프롬프트. Deep Research 보고서 + 채팅 답 1건(질문은 프롬프트 원문)
- 수집: 2026-10-09 Aside repl, 원문 대조 전

---
# 주요 디지털 자산 및 스테이블코인 발행사별 상환 약관 분석 보고서

## 1. 개요 및 분석 프레임워크

디지털 자산 생태계에서 스테이블코인은 액면가(Par value) 상환 권리를 매개로 유동성을 공급하는 핵심 자산이다 [cite: 1]. 보증 자산의 종류나 시장 시세가 1달러 근방에서 형성되더라도, 발행사가 제공하는 1차 시장(Primary market)의 직접 상환 약관은 각 자산의 실제 신용 위험과 유동성 프리미엄을 결정짓는 근본적인 요소로 작용한다 [cite: 1]. 2차 시장(Secondary market) 거래자 대다수는 발행사와의 직접 상환 권리를 가지지 못하며, 고객 알기 제도(KYC/KYB) 및 화이트리스트 등록을 마친 기관급 거래 상대방만이 1차 발행 및 상환 창구에 접근할 수 있다 [cite: 1].

발행사별 직접 상환 약관은 최소 상환 금액, 수수료 체계, 처리 시간, 자금 동결 및 정지 사유 등에 따라 현저한 차이를 보인다 [cite: 1, 2, 3, 4]. 이러한 약관상 차이는 시장 위기 상황 발생 시 1차 창구의 유동성 병목 현상을 유발하거나, 2차 시장 가격과 1차 시장 상환 가치 간의 괴리(Depeg)를 확대하는 원인이 된다 [cite: 1]. 본 보고서는 검증된 출처 자료만을 근거로 하여 주요 디지털 자산 및 스테이블코인 발행사의 직접 상환 약관을 다각도로 비교 분석한다 [cite: 1, 2, 3, 4, 5, 6, 7].

---

## 2. 발행사별 상환 약관 종합 비교표

다음 표는 각 디지털 자산 발행사의 공식 약관 및 관련 문서에 명시된 직접 상환 요건을 정리한 것이다. 소스에 구체적 수치나 항목이 명시되지 않은 경우 '소스에 없음'으로 명확히 표기하였다 [cite: 1, 2, 3, 4, 5, 6, 7].

| 발행사 | 코인 | 직접 상환 자격 | 최소 금액 | 수수료 | 처리 시간 | 정지 사유 | 출처(소스 이름, 쪽) |
|---|---|---|---|---|---|---|---|
| Tether Operations, S.A. de C.V. | USDT (USD₮, MXN₮, CNH₮) | KYC 검증을 완료한 직접 고객 (Tether 승인 필요) [cite: 1, 2, 8] | 100,000 USD [cite: 1, 2, 9, 10] | $1,000 또는 0.1% 중 큰 금액 (계정 검증 보증금 150 USD₮ 별도, 환불 불가) [cite: 2, 9] | 수일 소요 (Can take several days) [cite: 2] | 발행사 독점 재량권, 약관 위반, 사기·자금세탁 조사, 법원 및 수사기관 요청, T3 파이낸셜 크라임 등 동결 조치 [cite: 2, 5, 11, 12, 13] | Tether Fees [cite: 2], Tether Terms [cite: 8], Eco Support [cite: 1], KuCoin Flash [cite: 12] |
| TG Commodities, S.A. de C.V. | XAUt (Tether Gold) | KYC 검증을 완료한 직접 고객 (금지 대상자 및 금지 거래상대방 엄격 금지) [cite: 5] | 소스에 없음 [cite: 5] | 소스에 없음 [cite: 5] | 영업일 기준 수일 소요 (Several business days) [cite: 5] | 금 준비금의 손실·비유동성·미보유, 법령 또는 정부 기관의 정당한 요청, 금지 대상자 거래, 계정 정보 위조 [cite: 5] | Tether Gold Fee Schedule & Legal Terms [cite: 5] |
| Circle Internet Financial | USDC | Circle Mint 계정 보유 및 KYB/KYC 검증 완료 고객 (18세 이상, 제재 대상자/지역 제외) [cite: 1, 3] | 소스에 없음 [cite: 1, 3] | 소스에 없음 [cite: 3] | 임계값 이상 시 동일 영업일 (Same business day) / 운영·기술 장애 시 지연 가능 [cite: 1, 3] | 계정 미보유/부적격, 약관 위반 및 금지 거래, 제재 대상자 지정, 정부·법원 명령, 온체인 블랙리스트 등록 [cite: 3] | Circle USDC Terms of Service [cite: 3], Eco Support [cite: 1] |
| Paxos Trust Company | USDP (Pax Dollar) / PYUSD / BUSD / USDG | Paxos 플랫폼에 등록 및 완전 검증(KYC)을 마친 직접 고객 [cite: 4, 14] | 100 USD [cite: 15] | 1:1 상환, 전환 수수료 0원 (은행 송금 비용 및 별도 플랫폼 커미션 발생 가능) [cite: 4, 15] | 은행 출금 시 최대 2일 (대액 출금 및 준법 검토 시 지연 가능) [cite: 4] | 계정 정지/해지, 약관 위반, 불법·제재 활동(자금 몰수), 보안 위협 시 스마트 계약 일시 정지(Pausable), 시스템 오류 [cite: 4, 15] | Paxos Stablecoin Terms [cite: 4], Bybit Learn [cite: 15] |
| Paxos Trust Company | PAXG (Pax Gold) | Paxos 플랫폼 계정을 보유한 완전 검증 고객 [cite: 16] | 소스에 없음 [cite: 16] | 소스에 없음 [cite: 16] | 영업일 기준 수일 소요 (Several business days) [cite: 16] | 합리적 거절 사유 존재 시, 블록체인 포크 발생 시 플랫폼 일시 정지, 불법 사용, 계정 정지 [cite: 16] | Paxos PAXG Terms & Conditions [cite: 16] |
| Gemini Trust Company / Gemini Payments | GUSD (Gemini Dollar) | Gemini 계정 보유 및 신원 확인(Identity Verification) 완료 고객 [cite: 7, 17, 18, 19] | 최소 금액 없음 [cite: 7, 18] | 계정 개설/운용 수수료 없음 (약관 해지 1년 경과 출금 등 특수 상황 제외) [cite: 7, 18] | 소스에 없음 [cite: 20] | 약관/법률 위반, AML/CTF 위반, 마이너스 잔액, 보안/비정상 활동, 다운타임 및 시장 통제 [cite: 7, 17, 18, 21] | Gemini User Agreement [cite: 7, 17, 18, 19, 20, 21] |
| Ethena BVI Limited | USDe | KYC/AML 통과 및 화이트리스트 등록 Mint User (Holding User 상환 불가) [cite: 1, 6, 22] | 소스에 없음 [cite: 1] | 블록체인 가스비 및 실행 수수료 등 실비 정산 비용 [cite: 6] | 당일 처리 (Same-day for whitelisted minters) [cite: 1] | 서비스 중단, 약관 위반(자산 몰수 가능), KYC/AML 미통과, 법적/규제 요구사항 [cite: 6] | Ethena USDe Terms & Conditions [cite: 6, 22], Eco Support [cite: 1] |
| Sky (구 MakerDAO) | USDS / DAI | PSM(Peg Stability Module) 온체인 스마트 계약 참여자 (화이트리스트 자산) [cite: 1, 23] | 최소 금액 없음 [cite: 1] | Sky.money 교환 시 0원 (PSM 자산별 수수료 부과 가능) [cite: 1, 23] | 온체인 원자적 즉시 처리 (Atomic) [cite: 1] | 소스에 없음 [cite: 1, 23] | Sky.money [cite: 23], Eco Support [cite: 1] |

---

## 3. 주요 발행사별 직접 상환 약관 상세 분석

### Tether (USDT)

Tether Operations, S.A. de C.V.는 글로벌 스테이블코인 시장에서 가장 높은 점유율을 차지하지만, 1차 시장의 직접 상환 창구에 엄격한 자격 요건 및 고비용 구조를 설정하고 있다 [cite: 1, 2, 9]. Tether로부터 USDT(USD₮, MXN₮, CNH₮ 등)를 달러 등 피아트 화폐로 직접 상환받기 위해서는 필수적인 KYC/AML 신원 검증 절차를 완료해야 한다 [cite: 2, 8]. 계정 신청 시 제출하는 150 USD₮ 상당의 검증 депози deposit은 환불되지 않는 비반환성 비용이며, Tether는 계정 승인에 대한 독점적 재량권을 행사한다 [cite: 2].

직접 상환을 실행하기 위한 최소 거래 금액은 100,000 USD로 설정되어 있어 기관급 수량 이하의 직접 상환을 차단한다 [cite: 1, 2, 9, 10]. 상환 수수료는 $1,000 또는 전체 상환 금액의 0.1% 중 더 큰 금액이 부과된다 [cite: 2, 9]. 인출 요청 시 실시간 정산이 지원되지 않으며 처리까지 수일(several days)이 소요될 수 있다 [cite: 2]. 또한 Tether는 지갑 기능을 제공하지 않으므로 자산 반환 및 인출 요청은 건별로 평가되며, 발행사의 재량권, 준법 조사, 법령 준수, 수사기관과의 협력 등에 따라 상환을 정지하거나 계정을 동결할 수 있다 [cite: 2, 5, 12].

### Circle (USDC)

Circle Internet Financial은 USDC 발행사로서 법인 중심의 준법 및 규제 준수 체계를 운용한다 [cite: 1, 3]. Circle과 직접 USDC를 민팅하거나 USD로 상환하려면 승인된 'Circle Mint' 계정을 보유해야 한다 [cite: 3]. 계정 개설 조건으로 만 18세 이상이어야 하며, 미국 OFAC, 미 국무부, 미 상무부 등 제재 기관의 'Restricted Person' 목록에 포함되지 않아야 하고 restricted territory(쿠바, 이란, 북한, 우크라이나 특정 지역 등)에 거주하지 않아야 한다 [cite: 3].

Circle Mint 계정을 통한 상환은 설정된 임계값 이상인 경우 동일 영업일(Same business day) 정산을 제공한다 [cite: 1]. 다만 구체적인 수수료 요율과 정확한 최소 금액은 서비스 약관 본문 서술에 구체적 수치로 적히지 않고 별도 정책 및 Circle Mint 가입 조건으로 위임되어 있다 [cite: 1, 3]. 약관 위반, 차압 및 정부 법원 명령, 온체인 블랙리스트 등록, 또는 자원 과부하 및 보안 공격 발생 시 Circle은 직접 상환 조치를 지연, 거절, 정지하거나 자금을 몰수할 수 있다 [cite: 3].

### Paxos (USDP, PYUSD, BUSD)

Paxos Trust Company는 뉴욕주 금융서비스청(NYDFS)의 감독을 받는 신탁 기관으로서 USDP, PYUSD, BUSD 등의 상환을 관제한다 [cite: 4, 24]. Paxos 플랫폼에 가입하여 KYC 검증을 완료한 고객만이 직접 1:1 패리티로 법정화폐 상환을 진행할 수 있다 [cite: 4, 14].

Bybit 데이터에 따르면 USDP의 최소 전환 및 상환 요구 금액은 100 USD이며, Paxos는 USDP 전환 및 상환에 대해 별도의 플랫폼 수수료를 부과하지 않는다 [cite: 15]. 다만 은행 송금 비용이나 개별 프라이싱 서플리먼트에 따른 수수료가 적용될 수 있다 [cite: 4]. 일반적인 USD 출금 정산 시간은 최대 2 영업일이 소요되며 대규모 출금 시 추가적인 시간이 필요할 수 있다 [cite: 4]. 시스템 오류, 계약 약관 위반, 불법 사용 검출, 법적 차압 조치, 또는 보안 위협 발생 시 OpenZeppelin의 Pausable 모듈을 통해 온체인 승인 및 전송을 일시 중지할 수 있다 [cite: 4, 15].

### Gemini (GUSD)

Gemini Trust Company 및 Gemini Payments는 GUSD(Gemini Dollar)의 발행 및 전자화폐 계정 운영을 담당한다 [cite: 7, 17, 19]. Gemini 플랫폼 이용자는 본인 확인 프로세스를 완료한 후 언제든지 인출 요청을 제출할 수 있다 [cite: 7, 18]. 전자화폐 계약 및 기본 플랫폼 이용약관에 의하면 출금을 위한 최소 금액 제한이 명시되어 있지 않아 사실상 제한 없이 인출이 가능하다 [cite: 7, 18].

계정의 개설 및 기본 상환 운용에는 일반 수수료가 부과되지 않으나, 계정 해지 후 1년이 지난 시점의 출금 요청 등 일부 예외적 상황에서는 처리 비용이 발생할 수 있다 [cite: 7]. 약관상 GUSD 법정화폐 인출의 표준 정산 시간에 대한 구체적 명시는 출처 본문에 기재되어 있지 않다 [cite: 20]. 이용 약관 위반, AML/CTF 규정 미달, 마이너스 잔액 발생, 이상 거래 탐지, 다운타임 시 Gemini는 거래 취소 및 계정 정지 권한을 행사한다 [cite: 7, 17, 18].

---

## 4. 귀금속 연동 및 합성/프로토콜 자산의 상환 메커니즘

### 귀금속 연동형 자산: Tether Gold (XAUt) 및 Pax Gold (PAXG)

실물 금 자산을 보증으로 하는 XAUt(TG Commodities 발행)와 PAXG(Paxos Trust 발행)는 법정화폐 연동 스테이블코인과 상이한 구조적 상환 조건을 지닌다 [cite: 5, 16].

- Tether Gold (XAUt): 검증된 고객에 한해 실물 런던 굿 딜리버리(London Good Delivery) 금 파인 트로이 온스 단위로 상환을 신청할 수 있다 [cite: 5]. 금지 대상자(Prohibited Persons)의 보유 및 거래는 엄격히 금지된다 [cite: 5]. 최소 상환 규모 조건 및 요금표 규정이 적용되나 구체적인 수치는 출처 문서 본문에 명시되어 있지 않다 [cite: 5]. 처리 기간은 영업일 기준 수일이 소요되며, 보관 금괴의 손실, 유동성 부족, 법령 준수 요청이 발생할 경우 상환이 연기될 수 있다 [cite: 5].

- Pax Gold (PAXG): Paxos 계정을 가진 검증 고객은 PAXG를 USD, 미할당 금(Unallocated Gold), 할당 금(Allocated Gold)으로 상환할 수 있다 [cite: 16]. 최소 전환 금액 규정 및 프라이싱 서플리먼트에 따른 커미션·보관 수수료가 존재하지만 구체적 요율 수치는 출처 본문에 기재되어 있지 않다 [cite: 16]. 정산에는 영업일 기준 수일이 소요되며, 프로토콜 포크(Fork) 발생 시 플랫폼 기능이 일시 중지될 수 있다 [cite: 16].

### 합성 및 프로토콜 기반 자산: Ethena (USDe) 및 Sky (USDS/DAI)

- Ethena (USDe): Ethena BVI Limited가 발행하는 USDe는 암호화폐 현물과 파생상품 숏 포지션을 결합한 합성 달러 자산이다 [cite: 6, 25]. USDe의 직접 상환권은 KYC/AML 검증을 완료하고 화이트리스트에 등록된 'Mint User'에게만 부여된다 [cite: 6, 22]. 일반 2차 시장 거래자인 'Holding User'는 Ethena BVI와 직접 상환할 권리를 갖지 못한다 [cite: 6]. 수수료는 블록체인 가스비 및 파생상품 실행 마찰 비용에 대한 실비 정산으로 충당되며 [cite: 6], Mint User의 상환은 당일(Same-day) 처리된다 [cite: 1].

- Sky (구 MakerDAO - USDS/DAI): Sky 프로토콜은 온체인 페그 안정성 모듈(PSM)을 통해 중개자 없는 스마트 계약 상환을 지원한다 [cite: 1, 23, 26]. Sky.money 내에서 USDC와 USDS 간 교환 수수료는 0원이며 [cite: 23], 수량 제한 없이 온체인상에서 원자적(Atomic)으로 즉시 정산된다 [cite: 1].

---

## 5. 동결 권한, 시장 파급력 및 규제 환경

발행사의 약관에 기재된 일방적 자금 동결 권한 및 계정 정지 조항은 2차 시장 거래자와 기관 재무 관리자 모두에게 실질적인 신용 및 유동성 위험을 발생시킨다 [cite: 1, 3, 12].

상환 권리의 접근 구조를 보면, 1차 시장(Direct Redemption Window)은 KYC/KYB 승인을 얻은 소수의 기관 및 화이트리스트 거래 상대방에게만 열려 있으며, 높고 엄격한 최소 거래 threshold와 수수료, 수일의 정산 소요 시간이 수반된다 [cite: 1, 2, 3]. 반면 대다수의 개인 및 미승인 법인이 참여하는 2차 시장(Secondary Venue)은 발행사에 대한 직접 상환 청구권이 부재하며, 순수하게 시장 유동성 및 오프체인/온체인 거래소의 일치 여부에 가격을 의존하게 된다 [cite: 1].

Tether의 경우 수사기관의 공식 법원 명령이 존재하지 않더라도 자체 T3 Financial Crimes 유닛 및 독자적 판단에 따라 특정 주소의 USDT를 동결하는 조치를 취해왔다 [cite: 12, 13]. 실제 사례로 2025년 9월, 결제 기업 Conduit Technology는 Tether가 법적 명령이나 정당한 사유 없이 자사 운영 지갑에 보관된 2.76백만 달러의 USDT를 1년 이상 동결했다며 뉴욕 남부 연방법원에 소송을 제기했다 [cite: 11, 12, 13]. Conduit 측은 브라질 경찰 수사 대상이었던 이전 고객(Onix)과 관련이 없는 시점에 지갑이 생성되었음에도 Tether가 일방적으로 유동화를 차단했다고 주장한다 [cite: 11, 12, 13].

이러한 발행사의 자의적 정지 권한 및 불투명한 상환 거부 조항은 미 연방 GENIUS Act 및 유럽연합 MiCA Article 49와 같은 최신 규제 입법의 핵심 통제 대상이 되고 있다 [cite: 1, 27]. 법제화안들은 1:1 예치금 보존 의무화와 더불어 사전에 공시된 상환 약관 준수, 수수료 사전 고지, 상환 조건 변경 시 최소 7일 전 사전 통지 의무 등을 강제함으로써 발행사의 일방적 권한 남용을 통제하는 방향으로 진화하고 있다 [cite: 27].

---

## 6. 결론 및 종합 제언

본 보고서의 분석 결과, 디지털 자산의 패리티(Parity)는 단순한 2차 시장 시세로 보장되지 않으며 발행사의 공식 약관에 명시된 1차 상환 창구의 가용성에 의존한다 [cite: 1].

Tether는 $100,000의 진입 장벽과 0.1% 상환 수수료를 통해 1차 창구를 엄격히 제한하는 반면 [cite: 1, 2, 10], Paxos와 Gemini는 상대적으로 낮은 최소 금액을 제시하거나 수수료를 면제하여 상환 접근성을 향상시키고 있다 [cite: 7, 15]. 한편 Ethena와 같은 합성 자산은 Mint User에게만 상환권을 국한하므로 일반 보유자는 secondary liquidity 고갈 시 직접 상환 권리를 통한 위험 회피가 불가능하다 [cite: 1, 6]. 기관 재무 관리자는 스테이블코인 보유 시 단순 시세 추이뿐만 아니라 약관상 동결 권한, T+1 이상의 정산 지연 위험, 최소 상환 금액 요구 조건을 다각도로 반영한 리스크 관리 체계를 구축해야 한다 [cite: 1, 3, 12].

---

- Stablecoin Redemption Rights: Gating and Timing | Support, https://eco.com/support/en/articles/15453948-stablecoin-redemption-rights-gating-and-timing

- Fees - Tether, https://tether.to/fees/

- USDC Terms - Circle, https://www.circle.com/legal/usdc-terms

- US Dollar-Backed Stablecoin Terms and Conditions - Paxos, https://www.paxos.com/terms-and-conditions/stablecoin-terms-conditions

- Fee Schedule - Tether Gold, https://gold.tether.to/legal/feeschedule

- USDe Terms and Conditions - Ethena Docs, https://docs.ethena.fi/resources/usde-terms-and-conditions

- Gemini Payments UK User Agreement, https://www.gemini.com/legal/gemini-europe

- Legal - Tether, https://tether.to/en/legal/?tab=risk-disclosure

- Circle raises fees despite rising stablecoin market competition - The Business Times, https://www.businesstimes.com.sg/companies-markets/banking-finance/circle-raises-fees-despite-rising-stablecoin-market-competition

- What are stablecoins, and how are they regulated? - Brookings Institution, https://www.brookings.edu/articles/what-are-stablecoins-and-how-are-they-regulated/

- Conduit sues Tether for freezing $2.76M without cause, impacting its business operations., https://pluang.com/en/news-feed/tether-digugat-atas-pembekuan-stablecoin-2-76-juta-dolar

- Conduit Sues Tether Over $2.76M USDT Freeze - KuCoin, https://www.kucoin.com/news/flash/conduit-sues-tether-over-2-76m-usdt-freeze

- Tether Hit With $2.76M Lawsuit as Conduit Challenges Year-Long USDT Freeze, https://bitcoinfoundation.org/news/stablecoins/tether-hit-with-2-76m-lawsuit-as-conduit-challenges-year-long-usdt-freeze/

- Trovata SAAS Services Agreement, https://trovata.io/ssa

- Pax Dollar (USDP): The World's Leading Fully Regulated Stablecoin - Bybit, https://www.bybit.com/en/learn/stablecoin/what-is-pax-dollar-usdp

- PAX Gold Terms and Conditions - Paxos, https://www.paxos.com/terms-and-conditions/pax-gold-terms-conditions

- Gemini Intergalactic UK User Agreement, https://www.gemini.com/legal/gemini-europe-services

- Gemini Payments Europe Limited User Agreement, https://www.gemini.com/legal/gemini-payments

- User Agreement - Gemini, https://www.gemini.com/legal/gemini-trust-user-agreement

- Gemini Asset Rewards, https://support.gemini.com/hc/en-us/articles/43974244954267-Gemini-Asset-Rewards

- [POST SUPPORT REQUESTS HERE] Gemini Support Megathread - November 2022, https://www.reddit.com/r/Gemini/comments/yj8ive/post_support_requests_here_gemini_support/

- USDe Mint User Agreement - Ethena Docs, https://docs.ethena.fi/resources/usde-mint-user-agreement

- Sky.money | Put Stablecoins to Work with sUSDS, Vaults & SKY, https://sky.money/

- Implementing the Federal Reserve Board's Responsibilities under the GENIUS Act, https://www.federalreserve.gov/newsevents/pressreleases/files/bcreg20260924a4.pdf

- Research Update: Sky Protocol Assigned 'B-' Rating; Outlook Stable - S&P Global, https://www.spglobal.com/ratings/en/regulatory/article/-/view/sourceId/101638334

- What are stablecoins? USDC, USDT, and DAI explained | QINV Blog, https://qinv.io/blog/what-are-stablecoins-usdc-usdt-dai

- What Is the GENIUS Act? Stablecoin Rules Explained - Paxos, https://www.paxos.com/blog/genius-act


## 참고 링크(보고서 끝 목록)

1. Stablecoin Redemption Rights: Gating and Timing | Support https://eco.com/support/en/articles/15453948-stablecoin-redemption-rights-gating-and-timing
2. Fees - Tether https://tether.to/fees/
3. USDC Terms - Circle https://www.circle.com/legal/usdc-terms
4. US Dollar-Backed Stablecoin Terms and Conditions - Paxos https://www.paxos.com/terms-and-conditions/stablecoin-terms-conditions
5. Fee Schedule - Tether Gold https://gold.tether.to/legal/feeschedule
6. USDe Terms and Conditions - Ethena Docs https://docs.ethena.fi/resources/usde-terms-and-conditions
7. Gemini Payments UK User Agreement https://www.gemini.com/legal/gemini-europe
8. Legal - Tether https://tether.to/en/legal/?tab=risk-disclosure
9. Circle raises fees despite rising stablecoin market competition - The Business Times https://www.businesstimes.com.sg/companies-markets/banking-finance/circle-raises-fees-despite-rising-stablecoin-market-competition
10. What are stablecoins, and how are they regulated? - Brookings Institution https://www.brookings.edu/articles/what-are-stablecoins-and-how-are-they-regulated/
11. Conduit sues Tether for freezing $2.76M without cause, impacting its business operations. https://pluang.com/en/news-feed/tether-digugat-atas-pembekuan-stablecoin-2-76-juta-dolar
12. Conduit Sues Tether Over $2.76M USDT Freeze - KuCoin https://www.kucoin.com/news/flash/conduit-sues-tether-over-2-76m-usdt-freeze
13. Tether Hit With $2.76M Lawsuit as Conduit Challenges Year-Long USDT Freeze https://bitcoinfoundation.org/news/stablecoins/tether-hit-with-2-76m-lawsuit-as-conduit-challenges-year-long-usdt-freeze/
14. Trovata SAAS Services Agreement https://trovata.io/ssa
15. Pax Dollar (USDP): The World's Leading Fully Regulated Stablecoin - Bybit https://www.bybit.com/en/learn/stablecoin/what-is-pax-dollar-usdp
16. PAX Gold Terms and Conditions - Paxos https://www.paxos.com/terms-and-conditions/pax-gold-terms-conditions
17. Gemini Intergalactic UK User Agreement https://www.gemini.com/legal/gemini-europe-services
18. Gemini Payments Europe Limited User Agreement https://www.gemini.com/legal/gemini-payments
19. User Agreement - Gemini https://www.gemini.com/legal/gemini-trust-user-agreement
20. Gemini Asset Rewards https://support.gemini.com/hc/en-us/articles/43974244954267-Gemini-Asset-Rewards
21. [POST SUPPORT REQUESTS HERE] Gemini Support Megathread - November 2022 https://www.reddit.com/r/Gemini/comments/yj8ive/post_support_requests_here_gemini_support/
22. USDe Mint User Agreement - Ethena Docs https://docs.ethena.fi/resources/usde-mint-user-agreement
23. Sky.money | Put Stablecoins to Work with sUSDS, Vaults & SKY https://sky.money/
24. Implementing the Federal Reserve Board's Responsibilities under the GENIUS Act https://www.federalreserve.gov/newsevents/pressreleases/files/bcreg20260924a4.pdf
25. Research Update: Sky Protocol Assigned 'B-' Rating; Outlook Stable - S&P Global https://www.spglobal.com/ratings/en/regulatory/article/-/view/sourceId/101638334
26. What are stablecoins? USDC, USDT, and DAI explained | QINV Blog https://qinv.io/blog/what-are-stablecoins-usdc-usdt-dai
27. What Is the GENIUS Act? Stablecoin Rules Explained - Paxos https://www.paxos.com/blog/genius-act


# 채팅 1

## 질문

소스만 근거로, 발행사별 상환 약관을 표로 정리해 줘.
열: 발행사 | 코인 | 직접 상환 자격 | 최소 금액 | 수수료 | 처리 시간 | 정지 사유 | 출처(소스 이름, 쪽)
소스에 없으면 '소스에 없음'으로 적어 줘.

## 답

| 발행사 | 코인 | 직접 상환 자격 | 최소 금액 | 수수료 | 처리 시간 | 정지 사유 | 출처(소스 이름, 쪽) |
|---|---|---|---|---|---|---|---|
| Tether Operations, S.A. de C.V. | USDT (USD₮, MXN₮, CNH₮) | KYC 검증을 완료한 직접 고객 (Tether의 승인 필요) [1] [2] [3] | 100,000 USD [1] [2] [4] | $1,000 또는 0.1% 중 큰 금액 (비환불성 계정 검증 수수료 150 USD₮ 별도) [2] | 수일 소요 (Can take several days) [2] | 독점적 재량권, 약관/금지 거래 위반, 사기·자금세탁 조사, 법원/수사기관 요청, T3 파이낸셜 크라임 등 동결 조치 [2] [5] [6] [7] | Fees - Tether [2], Legal - Tether [3] [6], Stablecoin Redemption Rights: Gating and Timing |
| TG Commodities, S.A. de C.V. | XAUt (Tether Gold) | KYC 검증을 완료한 직접 고객 (금지 대상자 및 금지 거래상대방 제외) [8] [9] [10] | 실물 금 인출 시 430 XAUt (구매 시 최소 50 XAUt) [11] (*보고서 출처상 소스에 없음 표기 [12]) | 0.25% + 실물 인도/브로커 수수료 (계정 검증 수수료 150 USDt 별도) [11] [13] (*보고서 출처상 소스에 없음 표기 [12]) | 영업일 기준 수일 소요 (Several business days) [8] [14] | 금 준비금의 손실·비유동성·미보유, 법령/정부기관 요청, 계정 정보 위조, 금지 대상자 거래 [8] [15] [16] | Fee Schedule - Tether Gold [11] [13], Legal Terms (Tether Gold) [14] [15], 주요 디지털 자산 및 스테이블코인 발행사별 상환 약관 분석 보고서 [12] |
| Circle Internet Financial | USDC | Circle Mint 계정 보유 및 KYB/KYC 검증 완료 고객 (만 18세 이상, 제재 대상자/지역 제외) [1] [17] [18] | 소스에 없음 [1] [12] [17] | 일일 $2M 초과 빠른 인출 시 0.03%~0.1% (일반 인출 시 무료) [1] [19] | 임계값 이상/Circle Mint 이용 시 동일 영업일 (Same business day), 무료 인출 시 최대 2일 소요 [1] [2] | 계정 미보유/부적격, 약관 위반 및 금지 거래, 제재 대상자 지정, 정부·법원 명령, 온체인 블랙리스트 등록 [17] [20] [21] [22] [23] | Circle raises fees despite rising stablecoin market competition - The Business Times [1] [2], USDC Terms - Circle [17] [18] [19] [21], 주요 디지털 자산 및 스테이블코인 발행사별 상환 약관 분석 보고서 [12] |
| Paxos Trust Company | USDP, PYUSD, BUSD, USDG | Paxos 플랫폼에 가입하여 완전 검증(KYC)을 마친 직접 고객 [24] [25] [26] | 100 USD (또는 은행 송금 최소 수수료 상당 금액) [24] [27] [28] | 1:1 전환/상환 수수료 0원 (단, 은행 송금 비용 및 파트너 커미션 별도 발생 가능) [24] [27] [29] | 은행 출금 시 최대 2일 (대액 출금 및 준법 검토 시 지연 가능) [24] [30] [31] | 계정 정지/해지, 약관 위반, 불법·제재 활동(자금 몰수), 보안 위협 시 Pausable 모듈 일시 정지, 시스템 오류 [24] [32] [33] [34] [35] | US Dollar-Backed Stablecoin Terms and Conditions - Paxos [24] [25] [29] [31], Pax Dollar (USDP): The World's Leading Fully Regulated Stablecoin - Bybit [27] [32], 주요 디지털 자산 및 스테이블코인 발행사별 상환 약관 분석 보고서 [12] |
| Paxos Trust Company | PAXG (Pax Gold) | Paxos 플랫폼 계정을 보유한 완전 검증 고객 [36] [37] | USD 전환 시 소스에 없음 / 실물 금 인출 시 최소 430 PAXG [36] [38] | 소스에 없음 (프라이싱 서플리먼트/User Guide 별도 위임, 보관 및 전환 수수료 존재) [39] [40] | 영업일 기준 수일 소요 (Several business days) [36] [41] | 합리적 거절 사유 존재 시, 블록체인 포크 발생 시 플랫폼 일시 정지, 불법 사용, 계정 정지, 법적 지시 [33] [37] [42] [43] | PAX Gold Terms and Conditions - Paxos [36] [37] [38] [41] [43], 주요 디지털 자산 및 스테이블코인 발행사별 상환 약관 분석 보고서 [12] |
| Gemini Trust Company / Gemini Payments | GUSD (Gemini Dollar) | Gemini 계정 보유 및 신원 확인(Identity Verification) 완료 고객 [44] [45] [46] | 최소 금액 없음 (단, 디지털 자산 인출 시 $1) [44] [47] | 계정 개설/운용 및 1:1 매매 수수료 없음 (단, 네트워크 가스비/휴면 계정 관리비 제외) [44] [48] [49] | 소스에 없음 (영업일 기준 은행 계좌 출금 처리) [44] [50] [51] | 약관/법률 위반, AML/CTF 위반, 마이너스 잔액, 보안/비정상 활동, 다운타임 및 시장 통제 [44] [46] [52] [53] [54] | User Agreement - Gemini [46] [47] [49] [50] [51] [54], 주요 디지털 자산 및 스테이블코인 발행사별 상환 약관 분석 보고서 [12] |
| Ethena BVI Limited | USDe | KYC/AML 통과 및 화이트리스트 등록 Mint User (Holding User는 직접 상환 불가) [1] [55] [56] [57] | 소스에 없음 [1] [55] | 블록체인 가스비 및 파생상품 실행 수수료 등 실비 정산 비용 [55] [58] [59] | 당일 처리 (Same-day for whitelisted minters) [1] | 서비스 중단, 약관 위반(자산 몰수 가능), KYC/AML 미통과, 법적/규제 요구사항, 이상 거래 탐지 [55] [60] [61] | USDe Terms and Conditions - Ethena Docs [55] [56] [57] [59] [61], Stablecoin Redemption Rights: Gating and Timing |
| Sky (구 MakerDAO) | USDS / DAI | PSM(Peg Stability Module) 온체인 스마트 계약 참여자 (화이트리스트 자산) [1] [62] [63] | 최소 금액 없음 [1] [63] | Sky.money 교환 시 0원 (단, PSM 온체인 자산별 수수료 설정 가능) [1] [62] [63] [64] | 온체인 원자적 즉시 처리 (Atomic) [1] [63] | 소스에 없음 (스마트 계약/거버넌스 파라미터를 통한 한도 조정 및 수수료 변경) [1] [65] | Sky.money |

### 보충 설명

- 1차 창구(Primary Market)와 2차 시장(Secondary Market)의 차이: 일반 개인 거래자는 바이낸스, 업비트 등 2차 시장(가상자산 거래소)에서 거래하며 발행사와 직접 상환 권리를 갖지 못합니다 [1]. 위 표의 약관은 KYC/KYB 승인을 얻은 승인 고객(Mint User 등)이 발행사로부터 법정화폐(USD 등)로 직접 상환받을 때 적용되는 조건입니다 [1] [3] [17] [55].

- 금 연동 토큰(XAUt, PAXG): 실물 금 인출 시 런던 굿 딜리버리(London Good Delivery) 금괴 단위(약 400~430 온스) 수량에 맞춰 최소 인출 단위가 설정되며, 실물 운송/보관/브로커 비용이 추가될 수 있습니다 [8] [11] [36] [38].

💡 특정 발행사의 동결 사례나 규제(GENIUS Act, MiCA 등)에 따른 약관 변화에 대해 더 자세한 보고서나 상세 분석이 필요하신가요?

## 인용 번호와 소스

- Circle raises fees despite rising stablecoin market competition - The Business Times: [1] [2]
- USDC Terms - Circle: [3] [4] [5] [8] [17] [18] [19] [20] [21] [22] [23] [24] [44] [55]
- Legal - Tether: [6] [7]
- Fee Schedule - Tether Gold: [9] [10] [11] [13] [14] [15] [16]
- 주요 디지털 자산 및 스테이블코인 발행사별 상환 약관 분석 보고서: [12]
- US Dollar-Backed Stablecoin Terms and Conditions - Paxos: [25] [26] [28] [29] [31] [34] [35]
- Pax Dollar (USDP): The World's Leading Fully Regulated Stablecoin - Bybit: [27] [32]
- PAX Gold Terms and Conditions - Paxos: [30] [33] [36] [37] [38] [39] [40] [41] [42] [43]
- User Agreement - Gemini: [45] [46] [47] [48] [49] [50] [51] [54]
- Gemini Intergalactic UK User Agreement: [52] [53]
- USDe Terms and Conditions - Ethena Docs: [56] [57] [59] [61]
- USDe Mint User Agreement - Ethena Docs: [58] [60]
- Sky.money | Put Stablecoins to Work with sUSDS, Vaults & SKY: [62] [64]
- Stablecoin Redemption Rights: Gating and Timing | Support: [63] [65]
