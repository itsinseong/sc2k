#!/usr/bin/env python3
"""data/reports*.json 을 전부 읽어 site/data/reports.json 으로 합친다.

지금은 data/reports.json(Circle) 하나뿐이지만, 같은 스키마의
data/reports_paxos.json 등이 늘어나도 파일명만 늘리면 된다.
표준 라이브러리만 쓴다.

사용: python3 scripts/build_site.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
OUT = ROOT / 'site' / 'data' / 'reports.json'


def load_reports(path):
    doc = json.loads(path.read_text(encoding='utf-8'))
    # data/reports.json 형식: {"reports": [...]}. 만약을 위해 그냥 리스트인 파일도 받는다.
    return doc['reports'] if isinstance(doc, dict) else doc


def main():
    files = sorted(DATA.glob('reports*.json'))
    if not files:
        print('data/reports*.json 을 찾지 못했다', file=sys.stderr)
        return 1

    reports = []
    sources = []
    for f in files:
        batch = load_reports(f)
        reports.extend(batch)
        sources.append(f.relative_to(ROOT).as_posix())
        print(f'{f.relative_to(ROOT)}: 보고서 {len(batch)}개')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({'source_files': sources, 'reports': reports}, ensure_ascii=False, indent=1) + '\n',
        encoding='utf-8',
    )
    print(f'{OUT.relative_to(ROOT)}: 총 {len(reports)}개 보고서')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
