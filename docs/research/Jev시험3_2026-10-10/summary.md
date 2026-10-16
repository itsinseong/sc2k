# Jev 시험 3 정답 세트 요약

통과 문항은 78건이고 제외 문항은 0건이다. 정답 세트는 goldset_hard3.json에 있다.

## 갈래별 문항 수

| 갈래 | 내용 | 통과 | 제외 |
|---|---|---|---|
| A | Jev 오답 재출제 | 20 | 0 |
| B | 빠진 자산 종류 | 8 | 0 |
| C | R15 어려운 아니오 | 11 | 0 |
| D | 한국어 원장 항목명 | 39 | 0 |

## 자산 종류별 문항 수

| 자산 종류 | 문항 수 |
|---|---|
| bank_deposit | 3 |
| term_deposit | 3 |
| treasury_bill | 3 |
| treasury_note | 5 |
| non_us_government_bill | 3 |
| reverse_repo_overnight | 2 |
| reverse_repo_term | 2 |
| government_mmf | 3 |
| corporate_bond | 2 |
| precious_metal | 4 |
| bitcoin | 2 |
| secured_loan | 4 |
| public_equity | 2 |
| other_investment | 4 |
| settlement | 3 |
| cash_equivalents_unsplit | 2 |

자산 문항은 모두 {sum(ac.values())}건이다.

## 예/아니오 규칙별 정답

| 규칙 | 예 | 아니오 |
|---|---|---|
| R11 | 5 | 0 |
| R12 | 5 | 0 |
| R15 | 13 | 8 |

## 제외 이유

제외 문항은 0건이다. 검증을 통과하지 못한 문항이 없었다.

## 못 찾은 것

- A: 입력 글이 보고서 한 건 전체라 각 문항의 input에 A_items.json의 실제 입력 글을 그대로 넣었다. Jev 오답 22건은 근거 쪽이 원 입력에 없던 경우라 그 쪽 하나를 tesseract 300dpi OCR 글로 채웠다.
- A: 자산 종류 오답 B16, B17, B23, B26, B49, B51, B54, B05, B15, B22와 R11-16, R11-22, R11-23, R11-25는 goldset_hard.json에 이미 있어 새로 넣지 않았다.
- A: 기준 문제 42건(RLUSD 정의 문장 21건, Paxos 계약 공급량 문장 21건)은 정답이 확정되지 않아 넣지 않았다. USDG 2026-01과 2026-02는 질문과 정답이 같아 한 문항씩 합쳤다.
- B: term_deposit 정기예금 실제 줄을 찾지 못했다. Tether 2023-03 각주 9의 Term Deposits는 Cash & Bank Deposits 한 줄에 합쳐져 있어 정답이 bank_deposit이다.
- B: treasury_note 직접 보유 줄은 Circle USDC 2023-04의 CUSIP 줄뿐이라 2건만 썼고 다른 발행사의 줄은 없다.
- B: precious_metal, secured_loan, other_investment는 Tether 외 발행사에 해당 줄이 없다.
- C: 경영진 서명이 없는 회계법인 보고서형 문서는 data/samples에 없다. 아니오 8건은 원본에서 서명 블록만 지운 합성 문항이고 서명이 있는 짝 3건(C-09, C-10, C-11)은 원본 그대로다.
- C: jev_known은 시험 3을 아직 돌리지 않아 비어 있다.
