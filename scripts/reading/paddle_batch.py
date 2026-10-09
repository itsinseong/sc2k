"""Ripple 21건 표 쪽을 PaddleOCR-VL로 읽고, 한 건 끝날 때마다 Vision 기준값과 대조해 results.txt에 적는다. 이미 읽은 달은 건너뛴다."""
import json, pathlib, subprocess, sys, time, io, contextlib
W = pathlib.Path(__file__).resolve().parent
REPO = W.parents[1]; D = REPO / 'docs/research/읽기엔진시험_2026-10-09'
P = D / 'paddle'; P.mkdir(exist_ok=True)
PNG = D / 'png/paddle'; PNG.mkdir(parents=True, exist_ok=True)  # 그림과 PaddleOCR 작업 폴더(커밋 안 함)
RES = D / 'results.txt'
sys.path.insert(0, str(W))
from paddle_rows import rows_of
from claude_read import compare, base
from paddleocr import PaddleOCRVL
# 그림은 모델을 불러오기 전에 미리 만든다(모델이 메모리를 잡은 뒤엔 pdftoppm이 실패한 적 있음, 10/09)
for month in sorted(base):
    png = PNG / f'ripple_{month}.png'
    if not (P / f'ripple_{month}.md').exists() and not png.exists():
        page = base[month]['flags']['ocr_pages'][0]
        subprocess.run(['pdftoppm', '-r', '200', '-png', '-f', str(page), '-l', str(page), '-singlefile',
                        str(REPO / f'data/samples/Ripple_RLUSD_Examination_{month}.pdf'), str(png.with_suffix(''))], check=True)
pipe = PaddleOCRVL()
ONLY = sys.argv[1:]  # 달을 주면 그 달만
for month in [m for m in sorted(base) if not ONLY or m in ONLY]:
    page = base[month]['flags']['ocr_pages'][0]
    png = PNG / f'ripple_{month}.png'; md = P / f'ripple_{month}.md'
    if not md.exists():
        t = time.time()
        for r in pipe.predict(str(png)): r.save_to_markdown(save_path=str(PNG / f'_{month}'))
        next((PNG / f'_{month}').glob('*.md')).rename(md)
        secs = round(time.time() - t)
    else: secs = 0
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf): ok = compare(month, rows_of(md.read_text()))
        line = buf.getvalue().strip()
    except Exception as e: line = f'{month} ERROR {e!r}'
    with open(RES, 'a') as f: f.write(f'{line} | {secs}s\n')
with open(RES, 'a') as f: f.write('ALL DONE\n')
