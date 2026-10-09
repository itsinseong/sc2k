"""Gemini OCR 쪽 2건(4쪽)을 PaddleOCR-VL로 읽어 paddle/<달>.md로 남긴다. 시간은 times.txt에 적는다."""
import pathlib, time
from paddleocr import PaddleOCRVL
W = pathlib.Path(__file__).resolve().parents[3] / 'docs/research/읽기엔진시험_2026-10-09/gemini'; P = W / 'paddle'; P.mkdir(exist_ok=True)
PNG = W.parent / 'png/gemini'  # 그림과 PaddleOCR 작업 폴더(커밋 안 함)
pipe = PaddleOCRVL()
for month in ['2024-10', '2026-03']:
    md = P / f'{month}.md'
    if md.exists(): continue
    t = time.time()
    for r in pipe.predict(str(PNG / f'gemini_{month}_p4.png')): r.save_to_markdown(save_path=str(PNG / 'paddle' / f'_{month}'))
    next((PNG / 'paddle' / f'_{month}').glob('*.md')).rename(md)
    with open(W / 'times.txt', 'a') as f: f.write(f'{month} {round(time.time() - t)}s\n')
with open(W / 'times.txt', 'a') as f: f.write('ALL DONE\n')
