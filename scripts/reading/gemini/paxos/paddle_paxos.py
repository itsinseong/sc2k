"""Paxos 시험 그림 2장(PYUSD 2023-08 4쪽, USDG 2025-01 4쪽)을 PaddleOCR-VL로 읽어 <이름>.md, <이름>.json으로 남긴다."""
import pathlib, time
from paddleocr import PaddleOCRVL
W = pathlib.Path(__file__).resolve().parents[4] / 'docs/research/읽기엔진시험_2026-10-09/gemini/paxos'
PNG = W.parents[1] / 'png/gemini/paxos'  # 그림과 PaddleOCR 작업 폴더(커밋 안 함)
pipe = PaddleOCRVL()
for name in ['pyusd_2023-08_p4', 'usdg_2025-01_p4']:
    if (W / f'{name}.json').exists(): continue
    t = time.time()
    for r in pipe.predict(str(PNG / f'{name}.png')):
        r.save_to_json(save_path=str(PNG / f'_{name}')); r.save_to_markdown(save_path=str(PNG / f'_{name}'))
    next((PNG / f'_{name}').glob('*.md')).rename(W / f'{name}.md')
    next((PNG / f'_{name}').glob('*.json')).rename(W / f'{name}.json')
    with open(W / 'times.txt', 'a') as f: f.write(f'{name} {round(time.time() - t)}s\n')
with open(W / 'times.txt', 'a') as f: f.write('ALL DONE\n')
