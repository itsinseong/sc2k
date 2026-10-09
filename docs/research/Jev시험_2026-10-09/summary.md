# Jev 글 항목 고르기 시험

- 날짜 2026-10-09, 모델 jev-1.13.0(TypeSafe), 주소 https://api.typesafe.ai/v1/systemone
- 정답 세트: goldset.json(자산 줄 57개, 보고서 34건). 원응답과 채점: results.json
- 코인별 자산 줄: USDC 12, EURC 4, PYUSD 6, USDP 5, USDG 5, RLUSD 7, GUSD 5, USDT 13. 코인별 보고서: USDC 5, EURC 5, PYUSD 5, USDP 5, USDG 5, RLUSD 3, GUSD 3, USDT 3.
- 자산 종류 정답은 파서 분류(holdings[].kind)다. 57줄 가운데 41줄은 그 달 자산 종류 목록 시험(tests/test_rule_inputs.py ASSET_TYPES)이 확인하고, 나머지(정산 줄, 펀드 안 줄)는 파서 분류만 있다.
- R08, R11, R12, R15 정답은 시험이 확인하는 값이다(goldset.json gold_source). 입력은 보고서 전체 pdftotext 글이다.

## 항목별 정확도

Noul(예/아니오) 확신값은 문서 Confidence 쪽의 식 |2p-1|로 셈했다. 확신 0.8 이상은 p가 0.9 이상이거나 0.1 이하인 경우다.

| 항목 | 맞은 수/전체 | 확신 0.8 이상 남는 비율 | 확신 0.8 이상 정확도 |
|---|---|---|---|
| 자산 종류(16종 중 하나) | 53/57 (93%) | 44/57 (77%) | 42/44 (95%) |
| R08 검증 종류 | 29/29 (100%) | 29/29 (100%) | 29/29 (100%) |
| R11 발행잔액 계산식 공개 | 29/34 (85%) | 14/34 (41%) | 14/14 (100%) |
| R12 보관 기관 공개 | 34/34 (100%) | 30/34 (88%) | 30/30 (100%) |
| R15 경영진 서명 | 31/31 (100%) | 25/31 (81%) | 25/25 (100%) |

## 확신값 분포

칸 값: 건수(그 가운데 맞은 수)

| 항목 | 0.5 미만 | 0.5 이상 0.8 미만 | 0.8 이상 0.95 미만 | 0.95 이상 |
|---|---|---|---|---|
| 자산 종류(16종 중 하나) | 5(4) | 8(7) | 4(2) | 40(40) |
| R08 검증 종류 | 0(0) | 0(0) | 0(0) | 29(29) |
| R11 발행잔액 계산식 공개 | 9(8) | 11(7) | 14(14) | 0(0) |
| R12 보관 기관 공개 | 0(0) | 4(4) | 26(26) | 4(4) |
| R15 경영진 서명 | 1(1) | 5(5) | 22(22) | 3(3) |

정답 값 구성: R08 examination 24, reasonable assurance 5, R11 아니오 11, 예 23, R12 아니오 26, 예 8, R15 예 31

## 틀린 사례

| 번호 | 항목 | 코인, 달 | 입력 | 정답 | Jev 답 | 확신값 | 까닭 |
|---|---|---|---|---|---|---|---|
| A01 | 자산 종류(16종 중 하나) | USDC 2023-01 | TOTAL CIRCLE RESERVE FUND ASSETS | government_mmf | cash_equivalents_unsplit (정답 확률 0.00) | 0.83 | Circle Reserve Fund가 정부 MMF라는 설명은 보고서 다른 곳에 있고 줄 이름에는 없다. |
| A07 | 자산 종류(16종 중 하나) | USDC 2023-04 | U.S. Treasury Securities Cusip 912828VB3 | treasury_note | treasury_bill (정답 확률 0.28) | 0.66 | 단기(bill)와 중기(note)는 CUSIP 앞자리로 가른다(scripts/parse_circle.py 121행). 줄 이름은 둘 다 U.S. Treasury Securities다. |
| A12 | 자산 종류(16종 중 하나) | USDC 2026-07 | U.S. Treasury Securities Cusip 912797US4 | treasury_bill | treasury_note (정답 확률 0.43) | 0.42 | 단기(bill)와 중기(note)는 CUSIP 앞자리로 가른다(scripts/parse_circle.py 121행). 줄 이름은 둘 다 U.S. Treasury Securities다. |
| A56 | 자산 종류(16종 중 하나) | USDT 2023-06 | Money Market Funds: Fair value of the US Treasuries bills indirect exposure | treasury_bill | government_mmf (정답 확률 0.07) | 0.93 | 줄 이름에 'indirect exposure'(MMF가 들고 있는 국채를 들여다본 금액)가 있어 government_mmf도 말이 되는 답이다. 정답 treasury_bill은 레포의 펀드 안 보유(fund_holdings) 관례를 따른 값이고, 질문에 이 관례 설명이 없어 문항이 모호하다. |
| D27-R11 | R11 발행잔액 계산식 공개 | RLUSD 2025-10 | data/samples/Ripple_RLUSD_Examination_2025-10.pdf | 예 | 아니오 (p=0.23) | 0.54 | 2025-08부터 정의 문장에서 "issued, outstanding and redeemable"이 빠지고 "currently present on ... blockchain networks"(체인 위 잔액)만 남았다. 옛 문장(D26 2024-12)은 맞혔다. 레포 메모는 RLUSD 모든 달에 계산식은 아니라고 적고 값은 예로 둔다(data/reports_ripple.json field_notes). |
| D28-R11 | R11 발행잔액 계산식 공개 | RLUSD 2026-08 | data/samples/Ripple_RLUSD_Examination_2026-08.pdf | 예 | 아니오 (p=0.24) | 0.52 | 2025-08부터 정의 문장에서 "issued, outstanding and redeemable"이 빠지고 "currently present on ... blockchain networks"(체인 위 잔액)만 남았다. 옛 문장(D26 2024-12)은 맞혔다. 레포 메모는 RLUSD 모든 달에 계산식은 아니라고 적고 값은 예로 둔다(data/reports_ripple.json field_notes). |
| D32-R11 | R11 발행잔액 계산식 공개 | USDT 2023-03 | data/samples/Tether_USDT_Assurance_2023-03.pdf | 예 | 아니오 (p=0.26) | 0.48 | "total digital tokens issued less digital tokens held by the group but not in its treasury wallet" 문장이 입력에 있다. 유통량이 아니라 발행 토큰 부채(liabilities)라는 말로 적혀 있다. |
| D33-R11 | R11 발행잔액 계산식 공개 | USDT 2024-12 | data/samples/Tether_USDT_Assurance_2024-12.pdf | 예 | 아니오 (p=0.17) | 0.66 | "total digital tokens issued less digital tokens held by the group but not in its treasury wallet" 문장이 입력에 있다. 유통량이 아니라 발행 토큰 부채(liabilities)라는 말로 적혀 있다. |
| D34-R11 | R11 발행잔액 계산식 공개 | USDT 2026-06 | data/samples/Tether_USDT_Assurance_2026-06.pdf | 예 | 아니오 (p=0.21) | 0.58 | "total digital tokens issued less digital tokens held by the group but not in its treasury wallet" 문장이 입력에 있다. 유통량이 아니라 발행 토큰 부채(liabilities)라는 말로 적혀 있다. |

확신 0.8 이상인데 틀린 문항: A01(0.83), A56(0.93).

## 선택지 순서

자산 종류 질문을 선택지 순서만 거꾸로 해 한 번 더 물었다(문서 'Choice option order' 확인 방법). 같은 답 55/57 (96%). 거꾸로 한 순서의 정확도 53/57 (93%).
- A12 USDC 'U.S. Treasury Securities Cusip 912797US4': 원래 순서 treasury_note(0.42), 거꾸로 treasury_bill(0.56), 정답 treasury_bill
- A27 USDP 'Repurchase agreements, at fair value': 원래 순서 reverse_repo_overnight(0.42), 거꾸로 reverse_repo_term(0.33), 정답 reverse_repo_overnight

## 비용과 속도

- 이번 실행: 요청 148건, 입력 247,979토큰, 출력 23,965토큰(무료). 입력 100만 토큰당 0.042달러로 0.0104달러.
- 이 시험 전체(형식 확인 호출 포함 2회 실행): 248,795토큰, 0.0104달러. 충전액 5달러.
- 금액은 응답 usage.input_tokens와 문서 요금으로 셈한 값이다. 콘솔 청구 화면과 맞춰 보지는 않았다.
- 요청 1건 응답 시간 가운데값 0.25초(네트워크 포함, 순차 호출).
- 응답 모델 이름: jev-1.13.0

## API

- POST /v1/systemone, 머리글 Authorization: Bearer 키. 본문은 state(글 또는 JSON), model, questions(choice, noul, score). 응답은 answers(choice는 choice, probabilities, confidence, noul은 noul 하나)와 usage(input_tokens, output_tokens).
- 요금은 입력 토큰에만 붙는다(100만 토큰당 0.042달러, 출력 무료). 입력은 글만 받는다(이미지, 소리, 영상 없음). 한 요청 64k 토큰, state와 가장 긴 질문 합 32k 토큰. 출처 docs.typesafe.ai/api, docs.typesafe.ai/models.
- GET /v1/models 상태 200, 목록 jev-latest, jev-preview. 요청 model은 jev-1.13.0로 고정했다(별칭 jev-latest는 새 판이 나오면 바뀐다).

## 정답 세트에서 뺀 것

- R14: 이용약관 원문이 레포에 없고, interest_paid는 264건 모두 null(not_in_report)이라 정답이 없다.
- R08(USDC): USDC attestation.type을 확인하는 시험이 없다(tests/test_parser.py는 서명일만 확인).
- 보고서 문항에서 USDG 15달, GUSD 2024-10, 2026-03이 빠졌다. USDG 15달 가운데 7달(2024-12, 2025-01, 02, 04, 06, 07, 08)은 R08 문구가 글자 층에 없어서 빠졌다. GUSD 두 달은 예 정답의 근거가 글자 층이 없는 쪽(파서가 OCR로 읽은 쪽)에 있어서 뺐다.
- R15는 서명 블록이 그림 쪽에만 있는 보고서에서 문항을 뺐다: USDG 2024-10, RLUSD 2025-10, RLUSD 2026-08.

## 읽을 때 주의

- 자산 종류 53/57은 쉬운 줄이 끌어올린 값이다. 줄 이름에 종류 말이 그대로 있는 41줄(예: Bitcoin, Term Reverse Repurchase Agreements, regulated financial institutions)은 41/41이고 모두 확신 0.8 이상이다. 가벼운 추론이 필요한 6줄(A08, A17, A20, A23, A26, A30)은 6/6이고 그중 확신 0.8 이상은 1줄이다. 줄 이름 밖 정보가 필요한 10줄(A01, A04, A07, A09, A12, A21, A22, A27, A32, A56)은 6/10이다. 이 10줄에서 맞은 6줄의 확신은 0.42~0.66이고, 확신 0.8 이상으로 답한 2줄(A01, A56)은 둘 다 틀렸다. 그래서 '확신 0.8 이상이면 맡겨도 된다'는 이 시험으로 말할 수 없다. 줄 나누기는 검증 단계에서 줄 이름을 보고 한 것이다.
- R08 29/29는 원문 문구 찾기에 가깝다. 보고서 글에 'We have examined', 'Our examination', 'reasonable assurance' 같은 문구가 있을 때만 문항에 넣었고, 질문 설명에도 같은 문구가 있다. 정답은 5종 가운데 2종(examination, reasonable assurance)만 나왔다.
- R11 오답 5건 가운데 D27, D28(RLUSD 2025-10, 2026-08)은 Jev 오답이라기보다 정답 기준이 엇갈린 사례다. 같은 성격인 USDG 2024-10~2025-12의 정의 문장은 레포 값이 아니오인데, RLUSD 2025-08 이후 문장은 예로 되어 있다. 두 발행사 가운데 어느 쪽에 맞출지 정해야 R11 정확도를 바르게 읽을 수 있다.
- 확신 0.8 경계에 걸린 문항이 많다. 확신이 정확히 0.80인 문항이 11개라 '0.8 초과'로 세면 남는 수가 줄어든다(자산 43, R11 9, R12 28, R15 22). 또 자산 종류(16지선다)의 0.8은 p 0.8125 이상이고, 예/아니오의 0.8은 p 0.9 이상 또는 0.1 이하라서 항목마다 기준의 엄격함이 다르다.
- 정답 세트가 쏠려 있다. 자산 57줄 가운데 34줄이 코인별 첫 달 줄이고, USDT 13줄 가운데 11줄이 2023-03 표 하나에서 나왔다. 종류는 bank_deposit 14, treasury_bill 12, settlement 10으로 셋이 63%이고 term_deposit은 없다. 보고서 문항은 Paxos 계열이 15/34다.
- R15 정답은 레포 264건 모두 예라서, 아니오 사례가 없다. R15 정확도는 예를 알아보는 비율만 보여 준다.
- 같은 발행사, 같은 시기 보고서는 서식과 문장이 거의 같다. 문항 수보다 서로 다른 서식 수가 적다.
- 자산 종류 입력은 줄 이름과 발행사, 코인 이름(Circle은 표 구역 이름도)이다. 각주나 만기 표는 넣지 않았다.
