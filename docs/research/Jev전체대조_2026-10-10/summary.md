# Jev 전체 대조: R11, R12, R15 레포 값과 Jev 답의 불일치 분류

- 날짜 2026-10-10. Jev 모델 jev-1.13.0. 입력은 results.json.gz(보고서 264건 중 Jev 답 258건, 글 층이 없어 건너뛴 6건). 스크립트 scripts/jev_compare.py.
- 레포 값: R11 circulation_formula_disclosed, R12 custodian_disclosure, R15 management_certification(data/reports*.json, 고치지 않았다). R11 레포 값 하나를 Jev의 넓게 질문 답과 좁게 질문 답에 각각 맞춰 봤다.
- Jev 답은 p(예일 확률) 0.5 이상이면 예로 셌다. 확신값은 |2p-1|이다(2차 시험 summary와 같은 정의). 확신 0.8은 p 0.9 이상 또는 0.1 이하다.
- 불일치 64건을 확신 높은 순으로 모두 원문과 대조했다. 글 층이 있는 쪽은 Jev 입력과 같은 pdftotext 글로, 글 층이 없거나 깨진 쪽은 300dpi 그림을 tesseract로 읽은 글로 확인했다. 그림 쪽 가운데 USDG 2025-03 6쪽, 2025-09 6쪽, 2026-05 7쪽(옆으로 놓인 표)은 그림을 눈으로도 봤다.
- 쪽 번호는 PDF 파일 안 순서다. 보고서에 인쇄된 쪽 번호와 다를 수 있다(예: USDG 2025-09 6쪽의 인쇄 번호는 4).

## 요점

- 일치율: R11 넓게 질문 235/258 (91.1%), R11 좁게 질문 232/258 (89.9%), R12 보관 기관 이름 253/258 (98.1%), R15 경영진 서명 248/258 (96.1%).
- 확신 0.99 이상 불일치: 0건. 확신값 |2p-1|이 0.99 이상인 답이 한 건도 없다(가장 높은 확신값 0.98, Jev p는 0.01 단위로 오고 범위가 0.06~0.99). p 자체를 0.99 이상 또는 0.01 이하로 잡아도 25건(R12 보관 기관 이름 p=0.99)이고 모두 레포와 같다.
- 불일치 64건 분류: Jev 오답 22건, 레포 값 오류 0건, 기준 문제 42건, 판단 불가 0건.
- Jev 오답 22건은 모두 근거 쪽이 Jev 입력에 없던 경우다(글 층 없는 그림 쪽 20건, 글 층이 깨진 글자인 쪽 2건). 레포 값은 원문과 맞고, 입력 글에 근거가 있는데 틀린 답은 없었다.
- R12, R15 불일치 15건이 모두 이 경우라, 근거 쪽 글이 Jev 입력에 들어간 보고서에서는 R12, R15가 모두 레포와 같았다.
- R11 기준 문제 42건: 레포 R11 값은 넓게도 좁게도 아닌 중간 기준이다. 정의 문장(RLUSD)은 예, Paxos 옛 형식의 계약 공급량 문장은 아니오로 센다. 그래서 좁게 질문과는 RLUSD 21건, 넓게 질문과는 Paxos 21건이 갈린다(아래 따로 묶음).
- 레포 값 오류(파서가 틀림) 후보: 0건. 판단 불가: 0건.

## 항목별 일치율

| 항목 | 답한 보고서 | 일치 | 불일치 | 레포 예일 때 일치 | 레포 아니오일 때 일치 |
|---|---|---|---|---|---|
| R11 넓게 질문 | 258 | 235/258 (91.1%) | 23 | 168/170 (98.8%) | 67/88 (76.1%) |
| R11 좁게 질문 | 258 | 232/258 (89.9%) | 26 | 144/170 (84.7%) | 88/88 (100.0%) |
| R12 보관 기관 이름 | 258 | 253/258 (98.1%) | 5 | 54/59 (91.5%) | 199/199 (100.0%) |
| R15 경영진 서명 | 258 | 248/258 (96.1%) | 10 | 248/258 (96.1%) | - |

코인별 불일치 건수(보고서 수 대비):

| 코인 | 보고서 | R11 넓게 질문 | R11 좁게 질문 | R12 보관 기관 이름 | R15 경영진 서명 |
|---|---|---|---|---|---|
| USDC | 44 | 0 | 0 | 0 | 0 |
| EURC | 43 | 0 | 0 | 0 | 0 |
| PYUSD | 36 | 7 | 0 | 0 | 0 |
| USDP | 44 | 13 | 0 | 0 | 0 |
| USDG | 17 | 3 | 5 | 3 | 8 |
| RLUSD | 21 | 0 | 21 | 0 | 0 |
| GUSD | 39 | 0 | 0 | 2 | 2 |
| USDT | 14 | 0 | 0 | 0 | 0 |

## 확신 구간별 일치율

칸 값: 레포와 같은 답 수/답 수. 확신값은 |2p-1|이다.

| 항목 | 0.5 미만 | 0.5~0.8 | 0.8~0.9 | 0.9~0.95 | 0.95 이상 |
|---|---|---|---|---|---|
| R11 넓게 질문 | 28/49 | 74/76 | 44/44 | 69/69 | 20/20 |
| R11 좁게 질문 | 20/20 | 35/50 | 90/101 | 87/87 | - |
| R12 보관 기관 이름 | 2/2 | 167/172 | 30/30 | 1/1 | 53/53 |
| R15 경영진 서명 | 3/3 | 9/9 | 56/66 | 148/148 | 32/32 |
| 네 항목 합 | 53/74 | 285/307 | 220/241 | 305/305 | 105/105 |

- 확신 0.8 이상 불일치 21건 가운데 Jev 오답(입력 누락) 12건, R11 기준 문제 9건이다. 확신값이 높아도 입력에 근거 쪽이 빠지면 틀린다.

## 0.99 기준 위 불일치

- 확신값 |2p-1| 0.99 이상: 답 0건, 불일치 0건. Jev p가 0.01 단위라 |2p-1|은 0.98(p 0.99 또는 0.01)이 가장 높다.
- p 0.99 이상 또는 0.01 이하로 읽으면: 답 25건(R12 보관 기관 이름), 불일치 0건.
- 그래서 이번 확인은 0.99 아래 불일치 64건을 확신 높은 순으로 모두 읽은 것이다(요청 30건 이상).

## 분류 표

| 항목 | 불일치 | Jev 오답 | 레포 값 오류 | 기준 문제 | 판단 불가 |
|---|---|---|---|---|---|
| R11 넓게 질문 | 23 | 2 | 0 | 21 | 0 |
| R11 좁게 질문 | 26 | 5 | 0 | 21 | 0 |
| R12 보관 기관 이름 | 5 | 5 | 0 | 0 | 0 |
| R15 경영진 서명 | 10 | 10 | 0 | 0 | 0 |
| 합 | 64 | 22 | 0 | 42 | 0 |

- Jev 오답: 원문에 근거가 있어 레포 값이 맞고 Jev 답이 틀렸다. 이번 건은 모두 근거 쪽이 Jev 입력에 없었다(원인 칸).
- 기준 문제: 원문 글은 확인됐고, 답이 갈린 까닭이 R11을 넓게 보느냐 좁게 보느냐의 차이다.
- 레포 값 오류, 판단 불가: 해당 없음.

## R11 기준 문제(따로 묶음)

레포 R11 값의 기준(site/화면문구.json R11 근거 설명과 같음): Circle, Tether와 Paxos 새 형식(PYUSD, USDP 2025-01부터, USDG 2026-01부터)은 계산식이 있어 예, Ripple은 유통량 정의 문장이 있어 예, Gemini는 출처만 적어 아니오, Paxos 옛 형식(2023~2024년 PYUSD, USDP와 2024-10~2025-12 USDG)은 계약 공급량 문장만 있어 아니오다. 넓게 질문은 정의만 있어도 예, 좁게 질문은 더하거나 뺀 토큰이 있어야 예다.

### R11 가: RLUSD 정의 문장 (21건, 좁게 질문 아니오, 레포 예)

- 달: RLUSD 2024-12, RLUSD 2025-01, RLUSD 2025-02, RLUSD 2025-03, RLUSD 2025-04, RLUSD 2025-05, RLUSD 2025-06, RLUSD 2025-07, RLUSD 2025-08, RLUSD 2025-09, RLUSD 2025-10, RLUSD 2025-11, RLUSD 2025-12, RLUSD 2026-01, RLUSD 2026-02, RLUSD 2026-03, RLUSD 2026-04, RLUSD 2026-05, RLUSD 2026-06, RLUSD 2026-07, RLUSD 2026-08
- Jev p 범위 0.09~0.23, 확신값 0.54~0.82.
- 원문 문장(이 묶음 안에서 문장 꼴이 달라질 때마다 첫 달 하나, 쪽은 PDF 순서, 계약 주소는 (주소)로 줄임):

  - RLUSD 2024-12 보고서 4쪽: "Total RLUSD outstanding is defined as the aggregate amount of RLUSD issued, outstanding and redeemable, and currently present on the XRP Ledger and Ethereum blockchain networks, at the Report Dates."
  - RLUSD 2025-08 보고서 2쪽: "Outstanding Stablecoin Units means the aggregate amount of RLUSD currently present on the XRP Ledger and Ethereum blockchain networks at the Report Dates."
  - RLUSD 2026-06 보고서 4쪽: "Outstanding Stablecoin Units means the aggregate amount of RLUSD currently on the NYDFS approved blockchain networks* at the Report Dates."

### R11 나: Paxos 계약 공급량 문장 (21건, 넓게 질문 예, 레포 아니오)

- 달: PYUSD 2024-05, PYUSD 2024-06, PYUSD 2024-08, PYUSD 2024-09, PYUSD 2024-10, PYUSD 2024-11, PYUSD 2024-12, USDG 2025-11, USDP 2023-12, USDP 2024-01, USDP 2024-02, USDP 2024-03, USDP 2024-04, USDP 2024-05, USDP 2024-06, USDP 2024-07, USDP 2024-08, USDP 2024-09, USDP 2024-10, USDP 2024-11, USDP 2024-12
- Jev p 범위 0.50~0.62, 확신값 0.00~0.24.
- 원문 문장(이 묶음 안에서 문장 꼴이 달라질 때마다 첫 달 하나, 쪽은 PDF 순서, 계약 주소는 (주소)로 줄임):

  - PYUSD 2024-05 보고서 6쪽: "The supply of PayPal USD tokens (“PYUSD”) as denoted under contracts (주소) on the Ethereum network and (주소) on the Solana network at the Report Dates and Times combined is 399,112,794 and 444,103,023, respectively."
  - USDG 2025-11 보고서 6쪽: "The supply of Global Dollar tokens (“USDG”) as denoted under contracts (주소) on the Ethereum network, (주소) on the Solana network, (주소) on the Ink Networkand (주소) on the X Layer Network at 5:00 pm SGT on the Report Dates and Times is 1,114,538,306 and 1,230,553,949, respectively."
  - USDP 2023-12 보고서 6쪽: "The total supply of Pax Dollar tokens (“USDP”) (which also represents the total circulating supply) as denoted under contracts (주소) and (주소) at the Report Dates and Times combined is 371,353,920.86 and 372,639,175.35 , respectively, as reported by the Ethereum block explorer and Solana block explorer."
  - USDP 2024-01 보고서 6쪽: "The supply of Pax Dollar tokens (“USDP”) as denoted under contracts (주소) on the Ethereum network and (주소) on the Solana network at the Report Dates and Times combined is 367,057,426 and 353,101,046, respectively."

- Paxos 옛 형식 보고서(49건, 레포 아니오)에 Jev 넓게 답 p는 0.10~0.62로 흩어져 있다. 같은 꼴의 문장인데 PYUSD는 2024-04까지 계약 하나("as denoted under contract")일 때 p 0.16~0.40(아니오), 2024-05부터 두 체인 계약을 합친 문장("on the Ethereum network and ... on the Solana network ... combined")에서 p 0.56~0.62(예)다. USDP 2023-12는 p 0.50, 확신 0.00이다. 이 문장에서 Jev 넓게 답은 확신이 낮아 기준 판단에 쓰기 어렵다.
- RLUSD 정의 문장에 Jev 좁게 답은 p 0.09~0.23(아니오), 넓게 답은 21/21건 예라 RLUSD는 넓게 기준이면 레포와 같다.

R11 기준을 하나로 정하면 바뀌는 레포 값(이번에는 고치지 않음):

| 정하는 기준 | 바뀌는 보고서 | 지금 → 바뀔 값 | 근거 |
|---|---|---|---|
| 넓게(정의만 있어도 예) | Paxos 옛 형식 중 Jev 입력 글에 계약 공급량 문장("as denoted under contract")이 있는 48건 (레포 아니오 49건 중. 나머지 USDG 2024-12(입력 글 7쪽뿐)은 문장이 그림 쪽에 있어 확인 못 함) | 아니오 → 예 | 이번 넓게 질문과 2차 시험 정답 세트(R11-22~25) |
| 좁게(더하거나 뺀 토큰이 있어야 예) | RLUSD 21건(Jev가 답한 RLUSD 전부) | 예 → 아니오 | 정의 문장만 있고 계산 없음 |

- 글 층이 없어 Jev가 건너뛴 6건(USDG 2025-01, USDG 2025-02, USDG 2025-04, USDG 2025-06, USDG 2025-07, USDG 2025-08)은 레포 R11 값이 아니오이고, 이번 대조에 들어가지 않았다. 넓게 기준으로 바꿀 때는 이 6건도 그림 쪽을 읽어 따로 봐야 한다.

## Jev 오답(근거 쪽이 Jev 입력에 없음)

레포 값이 원문과 맞는다. 인용은 그림 쪽을 OCR로 읽은 글이다(서명자 이름은 OCR이 서명 그림과 겹쳐 흐려 직함까지만 적었다).

| 항목 | 코인, 달 | 레포 | Jev 답(p) | 확신 | 근거 쪽 | 근거 | 원문 인용 | 원인 |
|---|---|---|---|---|---|---|---|---|
| R15 경영진 서명 | USDG 2025-12 | 예 | 아니오(0.06) | 0.88 | 6쪽 | 경영진 확인 문장과 서명 블록(이름, Executive Director) | "To the best of the knowledge and belief of the undersigned, the information contained in the Redemption Assets Report as of the Report Dates and Times at 5:00pm SGT is accurate and complete." | 6쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R15 경영진 서명 | USDG 2024-10 | 예 | 아니오(0.07) | 0.86 | 6쪽 | 경영진 확인 문장과 서명 블록(이름, Executive Director) | "To the best of the knowledge and belief of the undersigned, the information contained in the Redemption Assets Report as of the Report Dates and Times at 5:00pm SGT is accurate and complete." | 6쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R15 경영진 서명 | USDG 2024-12 | 예 | 아니오(0.07) | 0.86 | 6쪽 | 경영진 확인 문장과 서명 블록(이름, Executive Director) | "To the best of the knowledge and belief of the undersigned, the information contained in the Redemption Assets Report as of the Report Dates and Times at 5:00pm SGT is accurate and complete." | 6쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R15 경영진 서명 | USDG 2025-03 | 예 | 아니오(0.07) | 0.86 | 6쪽 | 경영진 확인 문장과 서명 블록(이름, Executive Director) | "To the best of the knowledge and belief of the undersigned, the information contained in the Redemption Assets Report as of the Report Dates and Times at 5:00pm SGT is accurate and complete." | 6쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R15 경영진 서명 | USDG 2025-09 | 예 | 아니오(0.07) | 0.86 | 6쪽 | 경영진 확인 문장과 서명 블록(이름, Executive Director) | "To the best of the knowledge and belief of the undersigned, the information contained in the Redemption Assets Report as of the Report Dates and Times at 5:00pm SGT is accurate and complete." | 6쪽 글 층이 깨진 글자라 Jev 입력에서 읽을 수 없었다 |
| R15 경영진 서명 | USDG 2025-10 | 예 | 아니오(0.07) | 0.86 | 6쪽 | 경영진 확인 문장과 서명 블록(이름, Executive Director) | "To the best of the knowledge and belief of the undersigned, the information contained in the Redemption Assets Report as of the Report Dates and Times at 5:00pm SGT is accurate and complete." | 6쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R15 경영진 서명 | USDG 2026-01 | 예 | 아니오(0.07) | 0.86 | 6쪽 | 경영진 확인 문장과 서명 블록(이름, Executive Director) | "To the best of the knowledge and belief of the undersigned, the information contained in the USDG Redemption Assets Report as of the Report Dates at 5:00pm United States Eastern Time is accurate and complete." | 6쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R11 좁게 질문 | USDG 2026-01 | 예 | 아니오(0.08) | 0.84 | 7쪽 | Exhibit A 표: (a) 발행 토큰에서 (b) 임시, (c) 영구 상환 불가 토큰을 빼 (d) 상환 가능 토큰 | "Exhibit A: Total USDG Natively Minted Tokens and Total USDG Redeemable Tokens Outstanding" | 7쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R11 좁게 질문 | USDG 2026-02 | 예 | 아니오(0.08) | 0.84 | 7쪽 | Exhibit A 표: (a) 발행 토큰에서 (b) 임시, (c) 영구 상환 불가 토큰을 빼 (d) 상환 가능 토큰 | "Exhibit A: Total USDG Natively Minted Tokens and Total USDG Redeemable Tokens Outstanding" | 7쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R15 경영진 서명 | GUSD 2024-10 | 예 | 아니오(0.08) | 0.84 | 4쪽 | 경영진 확인서 서명 블록(이름, 직함) | "CEO/President Gemini Trust Company, LLC" | 4쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R15 경영진 서명 | USDG 2026-02 | 예 | 아니오(0.08) | 0.84 | 6쪽 | 경영진 확인 문장과 서명 블록(이름, Executive Director) | "To the best of the knowledge and belief of the undersigned, the information contained in the USDG Redemption Assets Report as of the Report Dates at 5:00pm United States Eastern Time is accurate and complete." | 6쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R15 경영진 서명 | GUSD 2026-03 | 예 | 아니오(0.08) | 0.84 | 4쪽 | 경영진 확인서 서명 블록(이름, 직함) | "Interim Chief Financial Officer Gemini Space Station, Inc." | 4쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R12 보관 기관 이름 | USDG 2025-09 | 예 | 아니오(0.11) | 0.78 | 6쪽 | Note 5 보관 기관 이름 | "the Company custodied Redemption Assets at DBS Bank Ltd., Banking Circle S.A., and Dreyfus Asset Management, a subsidiary of Bank of New York Mellon." | 6쪽 글 층이 깨진 글자라 Jev 입력에서 읽을 수 없었다 |
| R12 보관 기관 이름 | USDG 2025-10 | 예 | 아니오(0.11) | 0.78 | 6쪽 | Note 5 보관 기관 이름 | "the Company custodied Redemption Assets at DBS Bank Ltd., Banking Circle S.A., Standard Chartered Bank (Singapore) Limited, and Dreyfus Asset Management, a subsidiary of Bank of New York Mellon." | 6쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R12 보관 기관 이름 | USDG 2025-12 | 예 | 아니오(0.11) | 0.78 | 6쪽 | Note 5 보관 기관 이름 | "the Company custodied Redemption Assets at DBS Bank Ltd., Banking Circle S.A., Standard Chartered Bank (Singapore) Limited, and Dreyfus Asset Management, a subsidiary of Bank of New York Mellon." | 6쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R12 보관 기관 이름 | GUSD 2024-10 | 예 | 아니오(0.13) | 0.74 | 4쪽 | 각주 2 예금 은행 이름 | "The Gemini dollar reserves are held and maintained as cash deposits at State Street Bank and Trust Company and BNY Mellon N.A.;" | 4쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R12 보관 기관 이름 | GUSD 2026-03 | 예 | 아니오(0.14) | 0.72 | 4쪽 | 각주 2 예금 은행 이름 | "The Gemini dollar reserves are held and maintained as cash deposits at State Street and Western Alliance Bank." | 4쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R11 좁게 질문 | USDG 2026-07 | 예 | 아니오(0.15) | 0.70 | 7쪽 | Exhibit A 표: (a) 발행 토큰에서 (b) 임시, (c) 영구 상환 불가 토큰을 빼 (d) 상환 가능 토큰 | "Exhibit A: Total USDG Natively Minted Tokens and Total USDG Redeemable Tokens Outstanding" | 7쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R11 좁게 질문 | USDG 2026-08 | 예 | 아니오(0.17) | 0.66 | 7쪽 | Exhibit A 표: (a) 발행 토큰에서 (b) 임시, (c) 영구 상환 불가 토큰을 빼 (d) 상환 가능 토큰 | "Exhibit A: Total USDG Natively Minted Tokens and Total USDG Redeemable Tokens Outstanding" | 7쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R11 좁게 질문 | USDG 2026-05 | 예 | 아니오(0.18) | 0.64 | 7쪽 | Exhibit A 표: (a) 발행 토큰에서 (b) 임시, (c) 영구 상환 불가 토큰을 빼 (d) 상환 가능 토큰 | "Exhibit A: Total USDG Natively Minted Tokens and Total USDG Redeemable Tokens Outstanding" | 7쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R11 넓게 질문 | USDG 2026-02 | 예 | 아니오(0.20) | 0.60 | 7쪽 | Exhibit A 표: (a) 발행 토큰에서 (b) 임시, (c) 영구 상환 불가 토큰을 빼 (d) 상환 가능 토큰 | "Exhibit A: Total USDG Natively Minted Tokens and Total USDG Redeemable Tokens Outstanding" | 7쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |
| R11 넓게 질문 | USDG 2026-01 | 예 | 아니오(0.22) | 0.56 | 7쪽 | Exhibit A 표: (a) 발행 토큰에서 (b) 임시, (c) 영구 상환 불가 토큰을 빼 (d) 상환 가능 토큰 | "Exhibit A: Total USDG Natively Minted Tokens and Total USDG Redeemable Tokens Outstanding" | 7쪽이 글 층 없는 그림이라 Jev 입력에 없었다 |

- 글 층 없는 쪽이 있는 보고서는 Jev가 답한 258건 중 12건이다(코인별: USDG 10, GUSD 2). 글 층이 깨진 글자인 쪽이 있는 보고서(USDG 2025-09)도 같은 처지다. 이 보고서들은 일치한 답도 입력에 없는 쪽을 보지 않고 낸 답이다.

## 레포 값 오류 후보

- 없음. 불일치 64건 가운데 원문과 레포 값이 어긋난 건은 없었다. Jev 오답 22건은 원문 그림 쪽에 레포 근거가 그대로 있고(위 표), 기준 문제 42건은 원문 문장이 레포 메모(field_notes)에 적힌 문장과 같다.
- 이 결론은 불일치 건에 한한다. Jev와 레포가 같은 답을 낸 건은 원문과 대조하지 않았다(둘 다 틀린 경우는 이 대조로 찾을 수 없다).

## 불일치 전체 목록(확신 높은 순)

| 순위 | 항목 | 코인, 달 | 레포 | Jev 답(p) | 확신 | 분류 | 근거 쪽 | 읽은 글 |
|---|---|---|---|---|---|---|---|---|
| 1 | R15 경영진 서명 | USDG 2025-12 | 예 | 아니오(0.06) | 0.88 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 2 | R15 경영진 서명 | USDG 2024-10 | 예 | 아니오(0.07) | 0.86 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 3 | R15 경영진 서명 | USDG 2024-12 | 예 | 아니오(0.07) | 0.86 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 4 | R15 경영진 서명 | USDG 2025-03 | 예 | 아니오(0.07) | 0.86 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 5 | R15 경영진 서명 | USDG 2025-09 | 예 | 아니오(0.07) | 0.86 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 6 | R15 경영진 서명 | USDG 2025-10 | 예 | 아니오(0.07) | 0.86 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 7 | R15 경영진 서명 | USDG 2026-01 | 예 | 아니오(0.07) | 0.86 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 8 | R11 좁게 질문 | USDG 2026-01 | 예 | 아니오(0.08) | 0.84 | Jev 오답 (입력 누락) | 7쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 9 | R11 좁게 질문 | USDG 2026-02 | 예 | 아니오(0.08) | 0.84 | Jev 오답 (입력 누락) | 7쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 10 | R15 경영진 서명 | GUSD 2024-10 | 예 | 아니오(0.08) | 0.84 | Jev 오답 (입력 누락) | 4쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 11 | R15 경영진 서명 | GUSD 2026-03 | 예 | 아니오(0.08) | 0.84 | Jev 오답 (입력 누락) | 4쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 12 | R15 경영진 서명 | USDG 2026-02 | 예 | 아니오(0.08) | 0.84 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 13 | R11 좁게 질문 | RLUSD 2025-09 | 예 | 아니오(0.09) | 0.82 | 기준 문제 (R11 가) | 2쪽 | 글 층(Jev 입력과 같은 글) |
| 14 | R11 좁게 질문 | RLUSD 2025-10 | 예 | 아니오(0.09) | 0.82 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 15 | R11 좁게 질문 | RLUSD 2026-01 | 예 | 아니오(0.09) | 0.82 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 16 | R11 좁게 질문 | RLUSD 2026-06 | 예 | 아니오(0.09) | 0.82 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 17 | R11 좁게 질문 | RLUSD 2026-08 | 예 | 아니오(0.09) | 0.82 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 18 | R11 좁게 질문 | RLUSD 2025-08 | 예 | 아니오(0.10) | 0.80 | 기준 문제 (R11 가) | 2쪽 | 글 층(Jev 입력과 같은 글) |
| 19 | R11 좁게 질문 | RLUSD 2025-12 | 예 | 아니오(0.10) | 0.80 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 20 | R11 좁게 질문 | RLUSD 2026-02 | 예 | 아니오(0.10) | 0.80 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 21 | R11 좁게 질문 | RLUSD 2026-07 | 예 | 아니오(0.10) | 0.80 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 22 | R11 좁게 질문 | RLUSD 2025-11 | 예 | 아니오(0.11) | 0.78 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 23 | R11 좁게 질문 | RLUSD 2026-03 | 예 | 아니오(0.11) | 0.78 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 24 | R12 보관 기관 이름 | USDG 2025-09 | 예 | 아니오(0.11) | 0.78 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 25 | R12 보관 기관 이름 | USDG 2025-10 | 예 | 아니오(0.11) | 0.78 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 26 | R12 보관 기관 이름 | USDG 2025-12 | 예 | 아니오(0.11) | 0.78 | Jev 오답 (입력 누락) | 6쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 27 | R11 좁게 질문 | RLUSD 2026-04 | 예 | 아니오(0.12) | 0.76 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 28 | R11 좁게 질문 | RLUSD 2026-05 | 예 | 아니오(0.12) | 0.76 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 29 | R12 보관 기관 이름 | GUSD 2024-10 | 예 | 아니오(0.13) | 0.74 | Jev 오답 (입력 누락) | 4쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 30 | R12 보관 기관 이름 | GUSD 2026-03 | 예 | 아니오(0.14) | 0.72 | Jev 오답 (입력 누락) | 4쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 31 | R11 좁게 질문 | USDG 2026-07 | 예 | 아니오(0.15) | 0.70 | Jev 오답 (입력 누락) | 7쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 32 | R11 좁게 질문 | RLUSD 2025-01 | 예 | 아니오(0.17) | 0.66 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 33 | R11 좁게 질문 | USDG 2026-08 | 예 | 아니오(0.17) | 0.66 | Jev 오답 (입력 누락) | 7쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 34 | R11 좁게 질문 | RLUSD 2025-04 | 예 | 아니오(0.18) | 0.64 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 35 | R11 좁게 질문 | RLUSD 2025-07 | 예 | 아니오(0.18) | 0.64 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 36 | R11 좁게 질문 | USDG 2026-05 | 예 | 아니오(0.18) | 0.64 | Jev 오답 (입력 누락) | 7쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 37 | R11 좁게 질문 | RLUSD 2025-02 | 예 | 아니오(0.19) | 0.62 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 38 | R11 넓게 질문 | USDG 2026-02 | 예 | 아니오(0.20) | 0.60 | Jev 오답 (입력 누락) | 7쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 39 | R11 좁게 질문 | RLUSD 2025-03 | 예 | 아니오(0.20) | 0.60 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 40 | R11 좁게 질문 | RLUSD 2025-05 | 예 | 아니오(0.20) | 0.60 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 41 | R11 좁게 질문 | RLUSD 2025-06 | 예 | 아니오(0.21) | 0.58 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 42 | R11 넓게 질문 | USDG 2026-01 | 예 | 아니오(0.22) | 0.56 | Jev 오답 (입력 누락) | 7쪽 | 그림 쪽 OCR(tesseract 300dpi) |
| 43 | R11 좁게 질문 | RLUSD 2024-12 | 예 | 아니오(0.23) | 0.54 | 기준 문제 (R11 가) | 4쪽 | 글 층(Jev 입력과 같은 글) |
| 44 | R11 넓게 질문 | PYUSD 2024-09 | 아니오 | 예(0.62) | 0.24 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 45 | R11 넓게 질문 | USDP 2024-01 | 아니오 | 예(0.61) | 0.22 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 46 | R11 넓게 질문 | USDP 2024-10 | 아니오 | 예(0.61) | 0.22 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 47 | R11 넓게 질문 | PYUSD 2024-06 | 아니오 | 예(0.60) | 0.20 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 48 | R11 넓게 질문 | USDP 2024-03 | 아니오 | 예(0.59) | 0.18 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 49 | R11 넓게 질문 | USDP 2024-08 | 아니오 | 예(0.59) | 0.18 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 50 | R11 넓게 질문 | USDP 2024-11 | 아니오 | 예(0.59) | 0.18 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 51 | R11 넓게 질문 | PYUSD 2024-05 | 아니오 | 예(0.58) | 0.16 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 52 | R11 넓게 질문 | PYUSD 2024-10 | 아니오 | 예(0.58) | 0.16 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 53 | R11 넓게 질문 | USDP 2024-04 | 아니오 | 예(0.58) | 0.16 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 54 | R11 넓게 질문 | USDP 2024-12 | 아니오 | 예(0.58) | 0.16 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 55 | R11 넓게 질문 | PYUSD 2024-08 | 아니오 | 예(0.57) | 0.14 | 기준 문제 (R11 나) | 7쪽 | 글 층(Jev 입력과 같은 글) |
| 56 | R11 넓게 질문 | PYUSD 2024-11 | 아니오 | 예(0.57) | 0.14 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 57 | R11 넓게 질문 | PYUSD 2024-12 | 아니오 | 예(0.56) | 0.12 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 58 | R11 넓게 질문 | USDP 2024-02 | 아니오 | 예(0.56) | 0.12 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 59 | R11 넓게 질문 | USDP 2024-07 | 아니오 | 예(0.56) | 0.12 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 60 | R11 넓게 질문 | USDG 2025-11 | 아니오 | 예(0.55) | 0.10 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 61 | R11 넓게 질문 | USDP 2024-09 | 아니오 | 예(0.55) | 0.10 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 62 | R11 넓게 질문 | USDP 2024-05 | 아니오 | 예(0.53) | 0.06 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 63 | R11 넓게 질문 | USDP 2024-06 | 아니오 | 예(0.53) | 0.06 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |
| 64 | R11 넓게 질문 | USDP 2023-12 | 아니오 | 예(0.50) | 0.00 | 기준 문제 (R11 나) | 6쪽 | 글 층(Jev 입력과 같은 글) |

## 읽을 때 주의

- 분류는 원문 글을 읽은 판단이다. 기준 문제 42건은 원문 문장이 그대로 확인됐고, 어느 쪽이 맞는지는 R11 기준을 정해야 갈린다.
- 그림 쪽 근거는 tesseract OCR 글로 확인했다. 그 인용의 철자는 OCR 판독이라 원문과 한두 글자 다를 수 있고, 숫자는 넣지 않았다.
- R15 레포 값은 264건 중 예 264건이다. 이번 대조로는 서명 없는 보고서를 Jev가 가려내는지 알 수 없다(2차 시험의 R15 아니오 문항은 다른 회사 문서였다).
- 확신 구간별 일치율은 레포 값과 같은지를 잰 것이고 정답률이 아니다. R11은 레포 기준이 중간이라 넓게, 좁게 질문 모두 기준 차이만큼 낮게 나온다.
