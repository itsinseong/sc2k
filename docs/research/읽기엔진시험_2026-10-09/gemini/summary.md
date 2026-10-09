# Gemini(GUSD) OCR 쪽을 PaddleOCR-VL과 Claude Opus 5.5로 읽기 (2026-10-09)

대상: `data/reports_gemini.json`에서 `flags.ocr_pages`가 있는 2건, 2024-10과 2026-03의 4쪽(PDF 4쪽 전체가 그림).
그림: `pdftoppm -r 200` → `gemini_<달>_p4.png`(1700x2200).
정답: `data/reports_gemini.json`(2026-10-05 Vision 판독).

## 결론

- 파서에 들어가는 줄(보고 날짜, 표 5줄, 서명 블록 4줄, 각주 1~3)은 두 독자가 두 달 모두 글자까지 같게 읽었다.
- `parse_gemini`를 import하고 이 실행 안에서만 `text_of`와 `ocr_boxes`를 바꿔 `parse(pdf)`를 불렀다. 두 독자, 두 달 모두 `ok=True`다. 유통량, 준비금, 구성, holdings, 보관 기관, 서명자, 보고 날짜 등 값 필드는 정답과 모두 같다.
- 정답과 다른 곳은 두 종류다.
  1. 인용 줄 번호(`sources.*.line`, `holdings[].where.line`, `field_notes.*.where.line`): 2024-10은 10개, 2026-03은 13개 필드가 다르다. 줄 나누는 방식이 달라서다(새 독자는 문단 하나, 두 줄로 꺾인 표 라벨 하나를 한 줄로 낸다). 쪽 번호는 같다.
  2. 2024-10 `field_notes.circulation_formula_disclosed`의 note와 where: 정답은 'Etherscan'(0), where=None이고, 두 독자는 'Etherscan'(2), where=4쪽 'Per the Etherscan.io website'다. 정답 39건 중 'Etherscan'(0)인 달은 2024-10 하나뿐이고 나머지 38건은 모두 (2)다. 그래서 정답(Vision)이 이 달 각주 1을 놓친 것으로 본다. 값 `circulation_formula_disclosed=false`는 같다.
- 서명 위치(`parse_gemini.py` 215행 근처 `ocr_boxes`): PaddleOCR JSON의 블록 좌표로 대신할 수 있다. 잉크 수가 정답과 같다(917, 876). Claude는 좌표를 주지 않아서 단독으로는 대신할 수 없다.
- 조건이 셋 있다. (a) PaddleOCR는 마크다운이 아니라 JSON(`parsing_res_list`)을 써야 한다. 마크다운은 각주 블록을 빼서 파서가 "각주 2에서 기관 이름을 못 찾음"으로 실패한다(두 달 모두 실행해 확인). (b) PaddleOCR 윗첨자 표기 `$ ^{1} $`를 숫자로 바꿔야 한다. 바꾸지 않으면 "표(유통량 줄에서 Total Reserve 줄)를 찾지 못함"으로 실패한다(실행해 확인). Claude의 `¹`은 바꾸지 않아도 읽힌다. (c) Claude를 쓰려면 서명 위치용 좌표를 다른 곳(PaddleOCR 또는 Tesseract)에서 받아야 한다.

## 달마다 대조

금액은 원문 표기 그대로다. 정답 칸은 `flags.cents`, `report_dates`, `certifier`, `custodians`에서 가져왔다. 정답에는 앞 기준일 칸이 저장되지 않는다(파서가 월말 칸만 싣는다).

### 2024-10 (보고 날짜 2024-10-08, 2024-10-31)

| 줄 | 정답(Vision) 월말 | PaddleOCR (앞 / 월말) | Claude (앞 / 월말) | 일치 |
|---|---|---|---|---|
| GUSD issued and in circulation | 67,417,231.65 | 73,595,613.09 / 67,417,231.65 | 73,595,613.09 / 67,417,231.65 | 셋 다 같음 |
| Cash deposits held at U.S. regulated financial institutions | 68,629,770.82 | 74,679,214.36 / 68,629,770.82 | 74,679,214.36 / 68,629,770.82 | 셋 다 같음 |
| Money-market funds | 0 (대시) | - / - | - / - | 셋 다 같음 |
| Net cash receivable (payable) ... | (1,212,539.17) | (1,083,601.27) / (1,212,539.17) | (1,083,601.27) / (1,212,539.17) | 셋 다 같음 |
| Total Reserve | 67,417,231.65 | 73,595,613.09 / 67,417,231.65 | 73,595,613.09 / 67,417,231.65 | 셋 다 같음 |
| 서명 블록 | CEO/President | Marshall Beard, CEO/President, Gemini Trust Company, LLC, November 25, 2024 | 같음 | 셋 다 같음 |
| 각주 2 보관 기관 | State Street Bank and Trust Company; BNY Mellon N.A. | 같음 | 같음 | 셋 다 같음 |
| 각주 1 (Etherscan) | 못 찾음 | Per the Etherscan.io website located at: https://etherscan.io. | 같음 | 두 독자 같음, 정답만 다름 |

참고로 2024-10 Money-market funds 줄의 대시를 Vision은 못 읽었다(파서에 따로 처리하는 코드가 있다). 두 독자는 모두 `-`, `-`로 읽었다.

### 2026-03 (보고 날짜 2026-03-23, 2026-03-31)

| 줄 | 정답(Vision) 월말 | PaddleOCR (앞 / 월말) | Claude (앞 / 월말) | 일치 |
|---|---|---|---|---|
| GUSD issued and in circulation | 42,948,973.97 | 43,345,685.08 / 42,948,973.97 | 43,345,685.08 / 42,948,973.97 | 셋 다 같음 |
| Cash deposits held at U.S. regulated financial institutions | 43,571,282.42 | 43,857,583.57 / 43,571,282.42 | 43,857,583.57 / 43,571,282.42 | 셋 다 같음 |
| Net cash receivable (payable) ... | (622,308.45) | (511,898.49) / (622,308.45) | (511,898.49) / (622,308.45) | 셋 다 같음 |
| Total Reserve | 42,948,973.97 | 43,345,685.08 / 42,948,973.97 | 43,345,685.08 / 42,948,973.97 | 셋 다 같음 |
| 서명 블록 | Interim Chief Financial Officer | Danijela Stojanovic, Interim Chief Financial Officer, Gemini Space Station, Inc., April 30, 2026 | 같음 | 셋 다 같음 |
| 각주 2 보관 기관 | State Street; Western Alliance Bank | 같음 | 같음 | 셋 다 같음 |
| 각주 1 (Etherscan) | 4쪽에서 찾음 | 같음 | 같음 | 셋 다 같음 |

### 파서가 쓰지 않는 줄까지 전체 줄 대조(PaddleOCR 21줄, Claude 20줄)

- 2024-10: 다른 곳 1군데. PaddleOCR가 서명 그림 속 이름("Marshall Beard")을 글줄로 한 번 더 냈다. Claude에게는 같은 내용을 `[signature image: ...]` 주석으로 따로 받게 했고, 대조할 때 그 줄을 뺐다. 그래서 실제로 어긋난 것은 아니다.
- 2026-03: 다른 곳 1군데. 서명 그림 이름 줄(위와 같은 이유)과 DocuSign 해시가 다르다. PaddleOCR는 `E5290B3E33E642E`, Claude는 `E5290B3E33F642E`로 11번째 글자가 E와 F로 갈린다. 1200dpi로 잘라 보면 서명 밑줄이 해시 글자의 아래 획을 모두 가려서, E 네 개가 모두 F 모양으로 보인다(`hash_2026-03_crop2.png`). 그림으로는 가를 수 없다. 파서가 쓰지 않는 줄이라 보고서 값에는 영향이 없다.

## 서명 위치 찾기(215행 근처) 대체

`sig_check.py`: 이름(성)이 든 마지막 글상자의 위쪽 y를 구하고, `ri.signature_ink`로 잉크 수를 센다.

| 달 | PaddleOCR 블록 y → 잉크 | Tesseract 낱말 y → 잉크 | 좌표 없음(Claude 단독) | 정답 잉크 |
|---|---|---|---|---|
| 2024-10 | 449.6pt → 917 | 452.5pt → 917 | 잉크 0 → "서명 이미지 못 확인" 실패 | 917 |
| 2026-03 | 457.9pt → 876 | 459.7pt → 876 | 잉크 0 → 실패 | 876 |

- PaddleOCR는 줄이 아니라 블록 좌표를 준다. 두 달 모두 인쇄된 이름이 서명 블록(이름, 직함, 회사, 날짜 4줄)의 첫 줄이라서, 블록 위쪽 y가 곧 이름 줄 위쪽 y다. 이름이 든 블록은 둘이다(서명 그림 + 인쇄된 이름). y가 큰 쪽(아래)이 인쇄된 이름이고, 파서의 `bx[-1]`가 이것을 고른다. 이번 실행에서는 블록을 y 순으로 정렬해 넘겼다.
- Tesseract(`ocr_util._tesseract`)도 같은 잉크 수를 냈다. 이 Mac에는 `/opt/homebrew/bin/tesseract`가 있다. 다만 `OCR_ENGINE`과 `_tesseract`는 레포 작업 트리의 미커밋 변경(`scripts/ocr_util.py`, 10-08 15:06 수정, `git status`에 M)에만 있고 커밋본에는 없다.

## 걸린 시간과 비용

| 작업 | 2024-10 | 2026-03 | 비고 |
|---|---|---|---|
| PaddleOCR-VL 마크다운 | 201초 | 179초 | 모델 불러오기 제외, `caffeinate -i nice -n 15`, 메모리 안전장치가 멈춘 일 없음 |
| PaddleOCR-VL JSON 다시 읽기 | 495초 | 266초 | 마크다운에 각주와 좌표가 없어 다시 돌림. Claude와 동시에 돌았음 |
| Claude Opus 5.5 effort max | 492초, $0.57 | 1307초, $1.03 | 두 달을 차례로 실행 |

## 문제점

1. PaddleOCR `save_to_markdown`은 각주(`footnote` 블록)를 빼고 좌표가 없다. 처음부터 `save_to_json`을 같이 저장해야 한다. 이번에는 마크다운만 저장했다가 한 번 더 돌렸다.
2. 독자를 바꾸면 `data/reports_gemini.json`의 인용 줄 번호가 바뀐다(값은 같음). 2024-10은 각주 1 인용이 새로 생긴다(정답의 Vision 누락이 메워짐).
3. 글 모양 맞추기를 이 실행 안에서 했다. 윗첨자를 숫자 한 글자로 바꾸고, 표 칸을 공백 3칸으로 잇고, Claude 주석 줄을 뺐다. 숫자는 손대지 않았다. Vision 전용 쉼표/소수점 교정 정규식은 쓰지 않았다(두 독자 모두 필요 없었다).
4. Claude는 시간 편차가 크다(같은 질문, 같은 크기 그림에 492초와 1307초).
5. 처음 띄울 때 `run_safe.sh`에 실행 권한이 없었고 Claude 서브셸이 같이 죽어서, 몇 분 늦게 다시 띄웠다(결과에는 영향 없음).
6. 레포는 읽기만 했다(파일 수정, 커밋, pytest, `main()` 실행 없음). 다만 `parse_gemini`를 import할 때 파이썬이 추적 안 되는 캐시 `scripts/__pycache__/parse_gemini.cpython-314.pyc`를 다시 썼다(17:15). 다음에는 `PYTHONDONTWRITEBYTECODE=1`로 막을 수 있다.

## 파일

- `gemini_<달>_p4.png`: 4쪽 그림
- `paddle/<달>.md`, `paddle/<달>.json`: PaddleOCR-VL 결과 / `paddle_text_<달>.txt`: 파서에 넣은 글
- `claude_opus_<달>.json`: Claude 결과(봉투 그대로) / `claude_text_<달>.txt`: 파서에 넣은 글 / `prompt_gemini_page_v1.md`: 질문
- `compare_gemini.py` → `compare.txt`: 두 독자 줄 대조, 정답 필드 대조
- `sig_check.py`: 서명 위치 대체 시험
- `paddle_gemini.py`, `paddle_gemini_json.py`, `run_safe.sh`, `run_safe_json.sh`, `run_claude.sh`: 실행 스크립트, `times.txt`, `claude_times.txt`: 시간
- `paxos/`: 5번 조사(아래)

## Paxos 옛 형식 조사 (5번)

### 어디에 Vision OCR을 쓰나 (`data/reports_paxos.json` 103건 기준)

- 작업지시의 전제와 다른 점이 있다. 회계법인 서명이 그림인 옛 형식(PYUSD 16건, USDP 24건, 합 40건, 2023-08~2024-12)은 Vision OCR을 쓰지 않는다. 글자 층이 있고 회계법인 이름만 로고와 손글씨 서명에 있다. 그래서 `attestation.firm=null`, `flags.firm_signature_image=true`로 둔다(`parse_paxos.py` 300행 주석: 눈으로는 WithumSmith+Brown, PC).
- Vision OCR(`ocr_pages`)을 쓰는 Paxos 보고서는 USDG 17건이다.
  - 옛 형식, Enrome LLP 12건: 2024-10, 2024-12, 2025-01, 2025-02, 2025-03, 2025-04, 2025-06, 2025-07, 2025-08, 2025-09, 2025-10, 2025-12
  - 새 형식, KPMG LLP 5건: 2026-01, 2026-02, 2026-05, 2026-07, 2026-08
- OCR 쪽에서 나오는 값(`sources` 맨 위 항목 중 쪽이 `ocr_pages`에 든 것, holdings 등 안쪽 인용은 세지 않음): circulation, fair_value(13건), attestation.signed, circulation_note, reserve_currency(일부 달). 2025-03, 2026-05, 2026-07, 2026-08은 OCR 쪽에서 나오는 `sources` 값이 없다.
- 회계법인 이름이 OCR로만 나오는 건: 7건(2024-12, 2025-01, 2025-02, 2025-04, 2025-06, 2025-07, 2025-08). 모든 쪽이 그림이라 글자 층에 "Enrome LLP"가 없다(pdftotext로 확인). 이 7건은 서명 날짜("Singapore, D Month YYYY")도 OCR로 나온다. 나머지 10건은 글자 층에 회계법인 이름이 있다.

### 그림 2장 시험

| 그림 | 정답(reports_paxos.json) | PaddleOCR-VL | Claude Opus 5.5 |
|---|---|---|---|
| PYUSD 2023-08 4쪽 (`paxos/pyusd_2023-08_p4.png`, 글자 층 있음) | firm=null, firm_signature_image=true, signed=2023-09-21 | 로고 "withum"(doc_title 블록), 손글씨 "Wi then Smith + Brown, PC"(Withum을 틀리게 읽음), 날짜 "September 21, 2023" / 307초 | 로고 "withum", 손글씨 "WithumSmith+Brown, PC"(코드 주석의 눈 판독값과 글자까지 같음), 날짜 "September 21, 2023" / 765초, $0.46 |
| USDG 2025-01 4쪽 (`paxos/usdg_2025-01_p4.png`, 모든 쪽 그림) | firm=Enrome LLP, signed=2025-02-28(원문 "28 February 2025") | "ENROME LLP", "Public Accountants and Chartered Accountants", "Singapore, 28 February 2025", 바닥글 "Enrome LLP". 로고와 손글씨는 글 없는 그림 블록 / 125초 | "ENROME LLP", "Public Accountants and", "Chartered Accountants", "Singapore, 28 February 2025", 바닥글 "Enrome LLP", 로고 "ENROME", 손글씨 "Enrome LLP" / 182초, $0.45 |

`parse_paxos.py`의 서명 날짜 정규식(290~291행)과 회계법인 정규식(301행)을 두 독자 글에 그대로 대 본 결과:

| 그림 | PaddleOCR | Claude | 정답 |
|---|---|---|---|
| USDG 2025-01 4쪽 | signed "28 February 2025", firm "Enrome LLP" | 같음 | 2025-02-28, Enrome LLP |
| PYUSD 2023-08 4쪽 | signed 못 찾음, firm 못 찾음 | signed "September 21, 2023", firm 못 찾음 | 2023-09-21(글자 층), null |

- PYUSD에서 PaddleOCR가 서명 날짜를 못 찾는 이유: 손글씨 블록("Wi then Smith + Brown, PC")이 "in all material respects." 줄과 날짜 줄 사이에 끼어서, 날짜가 바로 다음 줄이어야 하는 정규식에 걸리지 않는다. PYUSD는 글자 층이 있어 실제로는 OCR을 쓰지 않으므로 지금 파이프라인에는 영향이 없다. Claude는 손글씨를 따로 받게 해서 걸리지 않았다.
- 회계법인 정규식은 `KPMG LLP|Enrome LLP|ENROME LLP`만 찾으므로, 손글씨나 로고에서 "WithumSmith+Brown, PC", "withum"을 읽어도 지금 코드로는 firm이 채워지지 않는다. 채우려면 파서에 손글씨/로고 판독을 받는 길과 이름 목록이 새로 있어야 한다(조사만, 고치지 않음).

### Paxos 정리

- 그림만 있는 USDG 7건의 회계법인 이름과 서명 날짜: 시험한 1장(2025-01 4쪽)에서는 PaddleOCR, Claude 모두 Vision 정답과 같은 값을 냈다. 나머지 6건과 USDG의 표 쪽(금액)은 시험하지 않았다.
- PYUSD, USDP 40건의 firm=null: Vision OCR 대체 문제가 아니라 손글씨, 로고 판독 문제다. Claude는 손글씨를 "WithumSmith+Brown, PC"로 정확히 읽었고, PaddleOCR는 "Wi then Smith + Brown, PC"로 틀렸다(로고 "withum"은 둘 다 맞음). 시험은 1장뿐이다.
