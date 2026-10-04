# 2차 Reference 조사 검증 html 생성기. ledger.json(검증대장)과 아래 CONTENT(본문)를 합친다.
# 실행: python3 build.py  → ~/HTML/미디어프로젝트_StableWatch/조사/ 에 html을 쓴다.
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.expanduser("~/HTML/미디어프로젝트_StableWatch/조사/StableWatch_2차덱_조사검증_2026-10-04.html")
CSS_BASE = open(os.path.expanduser("~/.claude/skills/doc-html/두리번.css"), encoding="utf-8").read()

CSS_WIDE = """
.wrap{max-width:1480px;padding:0 56px 88px}
.hero h1{font-size:clamp(32px,4vw,48px)}
.hero p{max-width:80ch}
.hd .a{font-size:17px;line-height:1.6;margin:0 0 24px;color:#222}
.cp{font-family:inherit;font-size:12px;color:#111;background:#fff;border:1px solid #bbb;border-radius:4px;padding:3px 10px;cursor:pointer;white-space:nowrap}
.cp:hover{border-color:#111}
.hero .tools{margin-top:20px;display:flex;gap:6px}
body.editing .hero,body.editing .page,body.editing footer{outline:1px dashed #999;outline-offset:10px}
body.editing #editToggle{background:#111;color:#fff;border-color:#111}
@media print{.tools{display:none}}
@media (min-width:1200px){
  .page{display:grid;grid-template-columns:320px minmax(0,1fr);column-gap:64px;align-items:start}
  .page > .hd{position:sticky;top:64px}
  .page .hd h2{font-size:28px}
  .page > .bd{min-width:0}
}
@media (max-width:1199px){.wrap{padding:0 24px 88px}}
@media (max-width:700px){.wrap{padding:0 16px 64px}}
/* 판정 표시: 파랑 = 원문과 맞음, 검정 = 원문과 다름, 테두리 = 원문으로 못 정함 */
.v{display:inline-block;font-size:12px;font-weight:700;border-radius:4px;padding:1px 7px;white-space:nowrap}
.v.ok{background:var(--accent);color:#fff}
.v.part{background:var(--tint);color:var(--ink)}
.v.bad{background:#111;color:#fff}
.v.na{border:1px solid #bbb;color:var(--ink-2)}
td.q{font-size:12.5px;color:#333}
td.q i{font-style:normal;color:var(--ink-3)}
td.nw,th.nw{white-space:nowrap}
tr.gh td{background:var(--soft);font-weight:700;font-size:12.5px;color:var(--ink-2)}
details{border-top:1px solid var(--line);padding:10px 0}
details > summary{cursor:pointer;font-weight:700;font-size:15px}
details[open] > summary{margin-bottom:10px}
.mono{font-family:ui-monospace,Menlo,monospace;font-size:12px}
.nw{white-space:nowrap}
table.mx td:first-child{white-space:nowrap}
table.dt td:first-child{min-width:132px;overflow-wrap:normal}
table.pv td:first-child{min-width:118px;overflow-wrap:normal}
table.fr td:nth-child(5),table.fr td:nth-child(6),table.fr td:nth-child(7){white-space:nowrap}
.tline{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));margin:10px 0 8px;position:relative}
.tline:before{content:"";position:absolute;left:0;right:0;top:33px;border-top:2px solid var(--line)}
.tline div{position:relative;padding:0 14px 0 0;font-size:12.5px;line-height:1.5;color:var(--ink-2)}
.tline b{display:block;font-size:13px;color:var(--ink);margin-bottom:8px;white-space:nowrap}
.tline i{display:block;width:12px;height:12px;border-radius:50%;background:#bdbdb8;margin:0 0 10px;position:relative;z-index:1}
.tline .on i{background:var(--accent)}.tline .on b{color:var(--accent)}
@media (max-width:900px){.tline{grid-template-columns:1fr 1fr}.tline:before{display:none}}
"""

SCRIPT = """
function flash(b,t){const o=b.textContent;b.textContent=t;setTimeout(()=>{b.textContent=o},1400)}
const regions=document.querySelectorAll('.hero,section,footer'),editBtn=document.getElementById('editToggle');
let dirty=false;
editBtn.addEventListener('click',()=>{
  const on=!document.body.classList.contains('editing');
  document.body.classList.toggle('editing',on);
  regions.forEach(r=>{r.contentEditable=on;r.querySelectorAll('button').forEach(b=>b.contentEditable=false)});
  editBtn.textContent=on?'수정 끝내기':'수정';
});
regions.forEach(r=>r.addEventListener('input',()=>{dirty=true}));
regions.forEach(r=>r.addEventListener('paste',e=>{e.preventDefault();document.execCommand('insertText',false,e.clipboardData.getData('text/plain'))}));
addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue=''}});
document.getElementById('saveFile').addEventListener('click',async e=>{
  const btn=e.currentTarget,c=document.documentElement.cloneNode(true);
  c.querySelectorAll('[contenteditable]').forEach(n=>n.removeAttribute('contenteditable'));
  c.querySelector('body').removeAttribute('class');
  c.querySelector('#editToggle').textContent='수정';
  c.querySelector('#saveFile').textContent='저장';
  const html='<!doctype html>\\n'+c.outerHTML+'\\n';
  const name=decodeURIComponent(location.pathname.split('/').pop())||'StableWatch_2차덱_조사검증.html';
  try{
    const h=await showSaveFilePicker({suggestedName:name,types:[{description:'HTML',accept:{'text/html':['.html']}}]});
    const w=await h.createWritable();await w.write(html);await w.close();dirty=false;flash(btn,'저장됨');
  }catch(err){
    if(err.name==='AbortError')return;
    const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([html],{type:'text/html'}));a.download=name;a.click();dirty=false;flash(btn,'내려받음');
  }
});
"""

e = html.escape

VCLASS = {"일치": "ok", "반박 통과": "ok", "부분 일치": "part", "불일치": "bad",
          "원문 없음": "na", "확인 불가": "na", "2차 출처만": "na", "판정 갈림": "na", "미판정": "na"}


def badge(v):
    return f'<span class="v {VCLASS.get(v, "na")}">{e(v)}</span>'


def link(url, text=None):
    if not url or not url.startswith("http"):
        return e(url or "")
    short = text or re.sub(r"^https?://(www\.)?", "", url)
    short = short if len(short) <= 60 else short[:57] + "..."
    return f'<a href="{e(url)}">{e(short)}</a>'


def page(pid, n, title, conclusion, body):
    return (f'<section class="page" id="{pid}">\n  <div class="hd">\n    <p class="n">{n}</p>\n'
            f'    <h2>{title}</h2>\n    <p class="a">{conclusion}</p>\n  </div>\n  <div class="bd">\n{body}\n  </div>\n</section>\n')


def final(c):
    """반박과 재판정을 반영한 최종 판정 하나."""
    if c.get("tiebreak"):
        return c["tiebreak"]["verdict"], c["tiebreak"]
    v = c.get("verdict") or {}
    ch = c.get("challenge")
    if not v:
        return "미판정", {}
    if ch and ch.get("agree") is False:
        return "판정 갈림", v
    return v.get("verdict", "미판정"), v


def ledger_table(claims):
    rows = ['<div class="tw"><table>',
            '<tr><th class="nw">번호</th><th>주장</th><th class="nw">덱 칸</th><th class="nw">판정</th><th>원문</th></tr>']
    for c in claims:
        fv, src = final(c)
        quote = src.get("primary_quote", "")
        corr = src.get("corrected", "")
        cell = (link(src.get("primary_url", "")) + (f"<br><i>{e(quote)}</i>" if quote else "")
                + (f"<br>원문 값: {e(corr)}" if corr else ""))
        ch = c.get("challenge")
        mark = " (반박 검증 통과)" if ch and ch.get("agree") and fv in ("일치", "불일치", "부분 일치") else ""
        rows.append(f'<tr><td class="nw mono">{e(c["id"])}</td><td>{e(c["claim"])}'
                    + (f'<br><small>값: {e(c.get("value",""))}</small>' if c.get("value") else "")
                    + f'</td><td class="nw">{e(c.get("deck_slot",""))}</td><td class="nw">{badge(fv)}<small>{e(mark)}</small></td>'
                    + f'<td class="q">{cell}</td></tr>')
    rows.append("</table></div>")
    return "\n".join(rows)


def build(content, ledger):
    pages = "".join(page(*p) for p in content["pages"])
    order = ["일치", "부분 일치", "불일치", "원문 없음", "2차 출처만", "확인 불가", "판정 갈림", "미판정"]
    groups = ledger["topics"] + [{"key": "M", "name": "누락 점검", "claims": ledger["recheck"]}]
    counts = [(t, [sum(1 for c in t["claims"] if final(c)[0] == o) for o in order]) for t in groups]
    used = [i for i, o in enumerate(order) if any(cs[i] for _, cs in counts)]
    summary = ('<div class="tw"><table><tr><th>주제</th><th class="c">주장</th>' + "".join(f'<th class="c">{order[i]}</th>' for i in used) + "</tr>"
               + "".join(f'<tr><td>{e(t["key"])} {e(t["name"])}</td><td class="c">{len(t["claims"])}</td>' + "".join(f'<td class="c">{cs[i] or ""}</td>' for i in used) + "</tr>" for t, cs in counts)
               + f'<tr class="me"><td>합계</td><td class="c">{sum(len(t["claims"]) for t in groups)}</td>' + "".join(f'<td class="c">{sum(cs[i] for _, cs in counts)}</td>' for i in used) + "</tr></table></div>"
               + '<p class="cav">판정은 반박 검증과 재판정을 반영한 최종 값이다. 부분 일치와 불일치 칸의 원문 값은 아래 주제별 표에 있다.</p>')
    appendix_body = summary + "".join(
        f'<details><summary>{e(t["key"])} {e(t["name"])} ({len(t["claims"])}건)</summary>{ledger_table(t["claims"])}</details>'
        for t in ledger["topics"])
    if ledger.get("recheck"):
        appendix_body += f'<details><summary>누락 점검에서 추가로 대조한 것 ({len(ledger["recheck"])}건)</summary>{ledger_table(ledger["recheck"])}</details>'
    pages += page("ledger", content["ledger_n"], "검증대장", content["ledger_a"], appendix_body)
    toc = "".join(f'<a href="#{p[0]}">{p[1]} {re.sub("<[^>]+>", "", p[2])}</a>' for p in content["pages"])
    toc += f'<a href="#ledger">{content["ledger_n"]} 검증대장</a>'
    doc = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(content["title"])}</title>
<style>
{CSS_BASE}
{CSS_WIDE}
</style>
</head>
<body>
<div class="wrap">

<header class="hero">
  <p class="eyebrow">{content["eyebrow"]}</p>
  <h1>{content["title"]}</h1>
  <p>{content["lede"]}</p>
  <div class="tools"><button class="cp" id="editToggle">수정</button><button class="cp" id="saveFile">저장</button></div>
</header>

<nav class="toc">{toc}</nav>

{pages}
<footer>{content["footer"]}</footer>
</div>
<script>{SCRIPT}</script>
</body>
</html>
"""
    doc = re.sub(r"\s*\u00b7\s*", ", ", doc)  # 가운뎃점은 쓰지 않는다(원문 인용 포함)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(doc)
    print("wrote", OUT, len(doc))


def load_ledger():
    r = json.load(open(os.path.join(HERE, "workflow_result.json"), encoding="utf-8"))
    topics = []
    for t in r["topics"]:
        vs = {x["id"]: x for x in t["verdicts"]}
        ch = {x["id"]: x for x in t["challenge"]}
        tb = {x["id"]: x for x in t["tiebreak"]}
        topics.append({"key": t["topic"], "name": t["name"],
                       "claims": [dict(c, verdict=vs.get(c["id"]), challenge=ch.get(c["id"]), tiebreak=tb.get(c["id"])) for c in t["claims"]]})
    rc = {x["id"]: x for x in r["recheck"]}
    recheck = [{"id": m["id"], "claim": m["claim"], "deck_slot": m["deck_slot"], "verdict": rc.get(m["id"])} for m in r["critic"]]
    c3p = os.path.join(HERE, "c3_result.json")
    if os.path.exists(c3p):
        c3 = json.load(open(c3p, encoding="utf-8"))
        vs = {x["id"]: x for x in c3["verdicts"]}
        ch = {x["id"]: x for x in c3.get("challenge", [])}
        tb = {x["id"]: x for x in c3.get("tiebreak", [])}
        topics.append({"key": "T6", "name": "Liner Scholar 보고서 '원화 기반 스테이블코인 규제 현황과 준비금 공시 의무'",
                       "claims": [dict(id=c["id"], claim=c["claim"], deck_slot="덱 관련" if c.get("deck") else "배경",
                                       verdict=vs.get(c["id"]), challenge=ch.get(c["id"]), tiebreak=tb.get(c["id"])) for c in c3["claims"]]})
    return {"topics": topics, "recheck": recheck}


def write_md(ledger):
    lines = ["# 2차 Reference 덱 검증대장 (2026-10-04)", "",
             "- 대상: NotebookLM 노트북 6개(NotebookLM_1차/), Liner 검색(라이너_1차/), Liner Scholar(라이너스콜라_2차/)",
             "- 판정: 1차 원문 대조, 덱 관련 판정은 반박 검증, 갈리면 재판정", ""]
    for t in ledger["topics"] + [{"key": "M", "name": "누락 점검", "claims": ledger["recheck"]}]:
        lines += [f"## {t['key']} {t['name']}", ""]
        for c in t["claims"]:
            fv, src = final(c)
            src = src or {}
            lines.append(f"- **{c['id']}** [{c.get('deck_slot','')}] {fv}: {c['claim']}")
            if src.get("corrected"):
                lines.append(f"  - 원문 값: {src['corrected']}")
            if src.get("primary_url"):
                lines.append(f"  - 원문: {src['primary_url']}")
            if src.get("primary_quote"):
                lines.append(f"  - 인용: {src['primary_quote']}")
        lines.append("")
    open(os.path.join(HERE, "검증대장_2026-10-04.md"), "w", encoding="utf-8").write("\n".join(lines))


if __name__ == "__main__":
    ledger = load_ledger()
    from content import CONTENT
    build(CONTENT, ledger)
    write_md(ledger)
