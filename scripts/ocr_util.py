"""PDF 한 쪽을 macOS Vision(scripts/ocr_vision.swift)으로 읽는다. parse_ripple.py, parse_gemini.py가 쓴다.
parse_paxos.py의 ocr_pages와 달리 글상자의 x 위치를 남겨, 금액 칸(왼쪽 날짜 열/오른쪽 날짜 열)을 x로 가른다."""
import pathlib, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent


def ocr_boxes(pdf, page, dpi=200):
    """쪽 하나를 읽어 [(위쪽y, 왼쪽x, 글)] 목록으로 낸다(y 0=맨 위, 1=맨 아래)."""
    with tempfile.TemporaryDirectory() as tmp:
        prefix = pathlib.Path(tmp) / 'p'
        subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-f', str(page), '-l', str(page), '-singlefile',
                        str(pdf), str(prefix)], check=True)
        out = subprocess.run(['swift', str(ROOT / 'scripts' / 'ocr_vision.swift'), str(prefix) + '.png'],
                             capture_output=True, text=True, check=True).stdout
    boxes = []
    for ln in out.splitlines():
        f = ln.split('\t', 2)
        if len(f) == 3 and f[0] != '#': boxes.append((float(f[0]), float(f[1]), f[2]))
    return boxes


def box_lines(boxes):
    """위쪽 y가 0.005 안으로 붙은 글상자를 한 줄로 묶는다. 줄 하나 = [(x, 글)] 를 x순으로."""
    lines, y0 = [], None
    for y, x, t in sorted(boxes):
        if y0 is None or y - y0 > 0.005:
            lines.append([]); y0 = y
        lines[-1].append((x, t))
    return [sorted(ln) for ln in lines]
