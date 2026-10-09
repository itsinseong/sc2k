"""paddle_gemini.py와 같은 그림을 다시 읽어 JSON(블록 좌표, 각주 포함)을 paddle/<달>.json으로 남긴다. 마크다운은 각주를 빼고 좌표가 없어서."""
import pathlib, time
from paddleocr import PaddleOCRVL
W = pathlib.Path(__file__).resolve().parents[3] / 'docs/research/읽기엔진시험_2026-10-09/gemini'; P = W / 'paddle'; P.mkdir(exist_ok=True)
PNG = W.parent / 'png/gemini'  # 그림과 PaddleOCR 작업 폴더(커밋 안 함)
pipe = PaddleOCRVL()
for month in ['2024-10', '2026-03']:
    js = P / f'{month}.json'
    if js.exists(): continue
    t = time.time()
    for r in pipe.predict(str(PNG / f'gemini_{month}_p4.png')):
        r.save_to_json(save_path=str(PNG / 'paddle' / f'_{month}_json')); r.save_to_markdown(save_path=str(PNG / 'paddle' / f'_{month}_md2'))
    next((PNG / 'paddle' / f'_{month}_json').glob('*.json')).rename(js)
    with open(W / 'times.txt', 'a') as f: f.write(f'{month} json {round(time.time() - t)}s\n')
with open(W / 'times.txt', 'a') as f: f.write('JSON DONE\n')
