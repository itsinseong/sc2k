"""idea, prd, ref, final 본문 + base.css, base.js -> ../StableWatch_종합.html (탭 4개, 전체 검색, 다크 모드).
디자인과 스크립트는 실록_종합.html(AI융합캡스톤디자인2)과 같은 체계를 복사해 쓴다."""
import base64, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "StableWatch_종합.html")

def read(name):
    return open(os.path.join(HERE, name), encoding="utf-8").read()

TABS = [("idea", "아이디어 제안서"), ("prd", "PRD"), ("ref", "레퍼런스"), ("site", "판정 사이트"), ("mas", "MAS 자문"), ("final", "최종"), ("todo", "할 일"), ("brand", "Brand Board")]
bodies = {k: read(f"{k}.html") for k, _ in TABS}
shot = base64.b64encode(open(os.path.join(HERE, "dash.jpg"), "rb").read()).decode()
BRAND = os.path.join(os.path.dirname(os.path.dirname(HERE)), "brand")
def svg(name, cls, label):
    src = open(os.path.join(BRAND, name), encoding="utf-8").read()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    d = "".join(f'<path d="{x}"/>' for x in re.findall(r' d="([^"]+)"', src))
    return f'<svg class="{cls}" viewBox="{vb}" role="img" aria-label="{label}"><title>{label}</title>{d}</svg>', vb, d
LOGO, _, _ = svg("sc2k-wordmark.svg", "lg", "SC2K")
SYMBOL, SYM_VB, SYM_D = svg("sc2k-symbol.svg", "sym", "SC2K")
FAVICON = "data:image/svg+xml;base64," + base64.b64encode(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{SYM_VB}" fill="#141210">{SYM_D}</svg>'.encode()).decode()
import subprocess
ISO = subprocess.run(["node", os.path.join(HERE, "iso_scene.mjs")], capture_output=True, text=True, check=True).stdout
JOST = base64.b64encode(open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "site", "fonts", "JostVariable-Latin.woff2"), "rb").read()).decode()
bodies = {k: b.replace("{{ISO}}", ISO).replace("{{LOGO}}", LOGO).replace("{{SYMBOL}}", SYMBOL) for k, b in bodies.items()}
bodies["idea"] = bodies["idea"].replace('src="dash.jpg"', f'src="data:image/jpeg;base64,{shot}"')

HEAD_JS = """try{var t=localStorage.getItem('stablewatch-theme')}catch(e){}
document.documentElement.dataset.theme=t||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');"""

SVG_SEARCH = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
SVG_SUN = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
SVG_MOON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/></svg>'

HEADER = f"""<header class="hub-top">
  <div class="hub-bar">
    <a class="hub-brand" href="#idea">{LOGO}<small>미디어프로젝트 2026-2, 원화 스테이블코인 준비금 공시 판정 체계</small></a>
    <div class="hub-search">
      <label>{SVG_SEARCH}<input id="gq" type="search" placeholder="전체 문서 검색 (⌘K)" autocomplete="off" aria-label="전체 검색"></label>
      <div class="hub-res" id="gres" hidden></div>
    </div>
    <div class="theme" role="group" aria-label="화면 모드"><button data-t="light" title="라이트 모드" aria-label="라이트 모드">{SVG_SUN}</button><button data-t="dark" title="다크 모드" aria-label="다크 모드">{SVG_MOON}</button></div>
  </div>
  <nav class="hub-tabs">{"".join(f'<a href="#{k}" data-tab="{k}">{n}</a>' for k, n in TABS)}</nav>
</header>"""

HUB_CSS = """
:root{--bg:#fff;--line2:#cfcfca;--hover:#fafaf8}
:root[data-theme="dark"]{--ink:#ececea;--ink-2:#b9b9b4;--ink-3:#8d8d88;--line:#2d2d2b;--line2:#46463f;--soft:#202020;--accent:#4b91e3;--tint:#1d3453;--tint-2:#162338;--mute:#6f6f6b;--bg:#151515;--hover:#1c1c1c;color-scheme:dark}
body{background:var(--bg)}
.toc,.chip,.cp{background:var(--bg)}

.hub-top{position:sticky;top:0;z-index:30;background:var(--bg);border-bottom:1px solid var(--line)}
.hub-bar{height:64px;display:flex;align-items:center;gap:24px;padding:0 clamp(24px,4vw,72px)}
.hub-brand{display:flex;align-items:baseline;gap:12px;text-decoration:none;color:var(--ink);min-width:0}
.hub-brand{align-items:center}
.hub-brand .lg{height:20px;width:auto;flex:none;display:block}
.lg,.sym{fill:currentColor;display:inline-block;width:auto}
@font-face{font-family:"Jost";src:url(data:font/woff2;base64,{JOST}) format("woff2");font-weight:100 900}
.bb-wrap{padding-top:40px}
.poster{container-type:inline-size;max-width:980px;margin:0 auto;aspect-ratio:1/1.414;display:grid;grid-template-rows:34fr 27fr 48fr 18fr 7fr;background:#F6F5F4;color:#141210;border-radius:6px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.06),0 18px 50px rgba(0,0,0,.12)}
.poster p{margin:0}
.poster code{background:none;padding:0;color:inherit;font-family:"Jost",sans-serif;font-size:1.15cqw;opacity:.75}
.pl{font-family:"Jost",sans-serif;font-size:1.25cqw;font-weight:500;letter-spacing:.04em;color:#736D68}
.pt{background:#141210;color:#fff;padding:4.5cqw 5cqw 4cqw;display:flex;flex-direction:column;justify-content:space-between}
.pt-row{display:flex;justify-content:space-between;align-items:baseline;font-family:"Jost",sans-serif;font-size:1.3cqw;letter-spacing:.06em;color:#B9B4AF}
.pt-mark .lg{display:block;width:58%;height:auto;color:#fff}
.pt-sub b{font-family:inherit;font-size:2.3cqw;font-weight:650;letter-spacing:-.02em;color:#fff}
.pt-sub span{font-size:1.8cqw;font-weight:300;letter-spacing:.02em;color:#fff}
.pi{padding:3cqw 5cqw 2.4cqw;display:flex;flex-direction:column;border-bottom:2px dashed #D9D5D1}
.pi .bb-iso{flex:1;min-height:0;width:100%;margin:1cqw 0}
.pi-cap{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(5,1fr);text-align:center;font-size:1.3cqw;font-weight:600;color:#4A4541}
.pg{display:grid;grid-template-columns:1fr 1fr 1fr;border-bottom:2px dashed #D9D5D1}
.pc{position:relative;padding:3cqw 3.2cqw;display:flex;flex-direction:column;gap:1.6cqw}
.pc+.pc{border-left:2px dashed #D9D5D1}
.ps-big{flex:1;display:grid;place-items:center}
.ps-big .sym{width:16cqw;height:16cqw}
.ps-sz{display:flex;align-items:flex-end;gap:2.2cqw;font-family:"Jost",sans-serif;font-size:1cqw;color:#736D68}
.ps-sz span{display:flex;flex-direction:column;align-items:center;gap:.6cqw}
.ps-sz span:nth-child(1) .sym{width:64px;height:64px}.ps-sz span:nth-child(2) .sym{width:32px;height:32px}.ps-sz span:nth-child(3) .sym{width:16px;height:16px}
.pn{font-size:1.25cqw;color:#736D68}
.pty{line-height:.95}
.pty b,.pty i{display:block;font-size:8.2cqw;font-weight:700;font-style:normal;letter-spacing:-.04em}
.pty.jost i{font-family:"Jost",sans-serif;font-weight:300;letter-spacing:-.02em}
.pty p{margin-top:.8cqw!important;font-size:1.6cqw;font-weight:700}
.pty small{font-size:1.2cqw;color:#736D68}
.pscale{margin-top:auto!important;display:flex;align-items:baseline;gap:1.2cqw;border-top:1px solid #D9D5D1;padding-top:1cqw;font-weight:650;line-height:1}
.pcol{flex:1;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(3,1fr);gap:1cqw}
.pcol div{border-radius:1cqw;padding:1.3cqw 1.4cqw;display:flex;flex-direction:column;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)}
.pcol .tall{grid-row:span 3}
.pcol b{font-size:1.5cqw}.pcol small{font-size:1.1cqw;opacity:.65}
.pcol code{margin-top:auto}
.pj{padding:2.6cqw 5cqw;display:flex;flex-direction:column;gap:1.4cqw;border-bottom:2px dashed #D9D5D1}
.pj-cells{display:grid;grid-template-columns:repeat(15,1fr);gap:.5cqw}
.pj-cells i{aspect-ratio:1;border-radius:.6cqw}
.pj-key{display:flex;gap:3cqw;font-size:1.35cqw;font-weight:600}
.pj-key span{display:flex;align-items:center;gap:.7cqw}
.pj-key i{width:1.3cqw;height:1.3cqw;border-radius:.3cqw;box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)}
.pj-cells i{box-shadow:inset 0 0 0 1px rgba(0,0,0,.06)}
.pf{padding:0 5cqw;display:flex;justify-content:space-between;align-items:center;font-size:1.15cqw;color:#736D68}
.pf span:first-child,.pf span:last-child{font-family:"Jost",sans-serif;letter-spacing:.03em}
.bb-def{max-width:980px;margin:40px auto 0}
[data-theme="dark"] .poster{box-shadow:0 0 0 1px #333}

.lgh{display:flex;align-items:center;gap:.4em}
.lgh .lg{height:.82em}
.hub-brand small{font-size:12.5px;color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hub-search{margin-left:auto;position:relative}
.hub-search label{display:flex;align-items:center;gap:8px;border:1px solid var(--line2);border-radius:8px;padding:7px 12px;width:380px;background:var(--bg);color:var(--ink-3)}
.hub-search label:focus-within{border-color:var(--ink)}
.hub-search input{border:0;outline:0;background:transparent;color:var(--ink);font:inherit;font-size:14px;width:100%}
.hub-res{position:absolute;right:0;top:calc(100% + 6px);width:min(560px,90vw);max-height:62vh;overflow:auto;background:var(--bg);border:1px solid var(--line2);border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.12);padding:6px}
.hr-count{font-size:12px;color:var(--ink-3);padding:4px 10px 6px}
.hr-item{display:block;width:100%;text-align:left;border:0;background:transparent;padding:8px 10px;border-radius:7px;cursor:pointer;color:var(--ink);font:inherit}
.hr-item:hover,.hr-item.sel{background:var(--soft)}
.hr-t{display:block;font-size:12px;color:var(--ink-3);margin-bottom:2px}
.hr-s{display:block;font-size:13.5px;line-height:1.5}
.hr-s mark{background:var(--tint);color:inherit;border-radius:2px;padding:0 1px}
.theme{display:flex;border:1px solid var(--line2);border-radius:999px;padding:3px;flex:none}
.theme button{border:0;background:transparent;color:var(--ink-3);width:30px;height:28px;border-radius:999px;cursor:pointer;display:grid;place-items:center}
.theme button[aria-pressed="true"]{background:var(--soft);color:var(--ink)}
.hub-tabs{display:flex;gap:32px;padding:0 clamp(24px,4vw,72px);height:50px;align-items:stretch;overflow-x:auto}
.hub-tabs a{display:flex;align-items:center;text-decoration:none;font-size:14.5px;font-weight:600;color:var(--ink-3);border-bottom:2px solid transparent;white-space:nowrap}
.hub-tabs a:hover{color:var(--ink)}
.hub-tabs a.on{color:var(--ink);border-bottom-color:var(--accent)}

.toc{top:115px}
section,:target{scroll-margin-top:170px}
.panel[hidden]{display:none}
.cav a,footer a,td a{color:inherit}
@keyframes hit{0%{background:var(--tint)}100%{background:transparent}}
.hit,tr.hit>td{animation:hit 2.2s ease-out}

.shot{margin:18px 0 0}
.shot img{display:block;width:100%;max-width:1400px;height:auto;border:1px solid var(--line);border-radius:10px}
.do > p:not(.k){font-size:14px;color:var(--ink-2);margin:0 0 14px}

[data-theme="dark"] .tbd{background:rgba(238,161,44,.2);color:#ffc266;border-color:#b87412}
[data-theme="dark"] .toc a:hover{color:#fff}
[data-theme="dark"] .def dd{color:var(--ink)}
[data-theme="dark"] .warn,[data-theme="dark"] .src{color:var(--ink-2)}
[data-theme="dark"] [data-tip]:hover::after,[data-theme="dark"] [data-tip]:focus-visible::after{background:#eee;color:#111}
[data-theme="dark"] .stack .g{background:#3a3a37}
[data-theme="dark"] .m.x{color:#666}
[data-theme="dark"] .mock .row{border-color:var(--line)}
[data-theme="dark"] .cp{color:var(--ink);border-color:#555}
[data-theme="dark"] .cp:hover{border-color:var(--ink)}
[data-theme="dark"] figure svg{filter:invert(.9) hue-rotate(180deg)}
[data-theme="dark"] .hub-res{box-shadow:0 10px 30px rgba(0,0,0,.5)}

@media (max-width:900px){.hub-brand small{display:none}.hub-search label{width:min(300px,52vw)}.hub-tabs{gap:22px}}
"""

COPY_CLICK = """
document.addEventListener('click',e=>{
 const b=e.target.closest('button.cp');if(!b)return;
 if(b.dataset.act==='copyall')return copyNode(b.closest('.wrap').querySelector('main.doc'),b);
 if(b.classList.contains('png'))return copyPng(b.closest('figure'),b);
 const sec=b.closest('section');if(!sec||!sec.querySelector('.body'))return;
 const w=document.createElement('div');w.appendChild(sec.querySelector('h2').cloneNode(true));w.appendChild(sec.querySelector('.body').cloneNode(true));copyNode(w,b);
});
"""

ROUTER = """
(function(){
var panels=[].slice.call(document.querySelectorAll('.panel')),tabs=[].slice.call(document.querySelectorAll('.hub-tabs a[data-tab]'));
function activate(panel){panels.forEach(function(p){p.hidden=p!==panel});tabs.forEach(function(t){t.classList.toggle('on',t.dataset.tab===panel.id)})}
window.hubShow=function(id){activate(document.getElementById(id))};
function show(){
 var id=decodeURIComponent(location.hash.slice(1))||panels[0].id,el=document.getElementById(id);
 var panel=el?(el.classList.contains('panel')?el:el.closest('.panel')):null;
 if(!panel){panel=panels[0];el=null}
 activate(panel);
 if(el&&el!==panel){requestAnimationFrame(function(){el.scrollIntoView({block:el.tagName==='TR'?'center':'start'})})}else{scrollTo(0,0)}
}
addEventListener('hashchange',show);show();
})();
"""

THEME_JS = """
(function(){
var r=document.documentElement,bs=[].slice.call(document.querySelectorAll('.theme button'));
function sync(){bs.forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.t===r.dataset.theme))})}
bs.forEach(function(b){b.addEventListener('click',function(){r.dataset.theme=b.dataset.t;try{localStorage.setItem('stablewatch-theme',b.dataset.t)}catch(e){}sync()})});
sync();
})();
"""

SEARCH_JS = """
(function(){
var input=document.getElementById('gq'),box=document.getElementById('gres'),TAB=%s,list=[],sel=0;
function norm(t){return t.replace(/\\s+/g,' ').trim()}
function esc(s){return s.replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function index(){
 var out=[];
 document.querySelectorAll('.panel').forEach(function(p){
  p.querySelectorAll('h2,h3,p,li,dt,dd,tr,.tile,figcaption').forEach(function(el){
   if(el.closest('nav,button,.tools,.key'))return;
   if(el.tagName==='TR'){if(el.querySelector('th'))return}
   else if(el.closest('tr,.tile')&&!el.classList.contains('tile'))return;
   var t=norm(el.tagName==='TR'?[].map.call(el.cells,function(c){return c.textContent}).join(' '):el.textContent);if(!t)return;
   var sec=el.closest('section'),h=sec&&sec.querySelector('h2');
   out.push({el:el,p:p.id,t:t,title:TAB[p.id]+(h?' / '+norm(h.textContent):'')});
  });
 });
 return out;
}
function snip(t,k,n){var a=Math.max(0,k-40),b=Math.min(t.length,k+n+70);return(a?'… ':'')+esc(t.slice(a,k))+'<mark>'+esc(t.slice(k,k+n))+'</mark>'+esc(t.slice(k+n,b))+(b<t.length?' …':'')}
function run(){
 var q=norm(input.value).toLowerCase();
 if(!q){box.hidden=true;list=[];return}
 var idx=index(),hits=[],total=0;
 idx.forEach(function(it){var k=it.t.toLowerCase().indexOf(q);if(k>-1){total++;if(hits.length<60)hits.push([it,k])}});
 list=hits.map(function(h){return h[0]});sel=0;
 box.innerHTML='<div class="hr-count">'+(total?total+'건'+(total>hits.length?', 앞 '+hits.length+'건 표시':''):'결과 없음')+'</div>'+
  hits.map(function(h,i){return '<button class="hr-item'+(i?'':' sel')+'" data-i="'+i+'"><span class="hr-t">'+esc(h[0].title)+'</span><span class="hr-s">'+snip(h[0].t,h[1],q.length)+'</span></button>'}).join('');
 box.hidden=false;
}
function mark(){[].slice.call(box.querySelectorAll('.hr-item')).forEach(function(b,i){b.classList.toggle('sel',i===sel);if(i===sel)b.scrollIntoView({block:'nearest'})})}
function go(it){
 box.hidden=true;input.blur();
 window.hubShow(it.p);
 requestAnimationFrame(function(){
  it.el.scrollIntoView({block:'center'});
  it.el.classList.remove('hit');void it.el.offsetWidth;it.el.classList.add('hit');
  setTimeout(function(){it.el.classList.remove('hit')},2300);
 });
}
input.addEventListener('input',run);
input.addEventListener('focus',function(){if(input.value)run()});
input.addEventListener('keydown',function(e){
 if(e.key==='ArrowDown'&&list.length){e.preventDefault();sel=Math.min(sel+1,list.length-1);mark()}
 else if(e.key==='ArrowUp'&&list.length){e.preventDefault();sel=Math.max(sel-1,0);mark()}
 else if(e.key==='Enter'&&list.length){e.preventDefault();go(list[sel])}
 else if(e.key==='Escape'){box.hidden=true;input.blur()}
});
box.addEventListener('mousedown',function(e){var b=e.target.closest('.hr-item');if(b){e.preventDefault();go(list[+b.dataset.i])}});
document.addEventListener('mousedown',function(e){if(!e.target.closest('.hub-search'))box.hidden=true});
document.addEventListener('keydown',function(e){if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();input.focus();input.select()}});
})();
""" % ("{" + ",".join(f"{k}:'{n}'" for k, n in TABS) + "}")

# ONE=1: 동료평가용 한 페이지판(탭 없음, 할 일 탭 제외, 맨 위에 발표 덱) -> ~/HTML/미디어프로젝트_SC2K/동료평가/index.html
ONE = os.environ.get("ONE") == "1"
if ONE:
    import shutil
    OUT = os.path.expanduser("~/HTML/미디어프로젝트_SC2K/동료평가/index.html")
    DECK = os.path.expanduser("~/HTML/미디어프로젝트_SC2K/발표/최종")
    shutil.copytree(os.path.join(DECK, "img"), os.path.join(os.path.dirname(OUT), "deck", "img"), dirs_exist_ok=True)
    shutil.copy(os.path.join(DECK, "SC2K_최종_발표.html"), os.path.join(os.path.dirname(OUT), "deck", "index.html"))
    TABS = [t for t in TABS if t[0] != "todo"]
    HEADER = re.sub(r'<nav class="hub-tabs">.*?</nav>', "", HEADER, flags=re.S)
    ROUTER = "window.hubShow=function(){};"
    HUB_CSS += """
.one-top{max-width:1180px;margin:0 auto;padding:56px clamp(24px,4vw,72px) 24px}
.one-top h1{font-size:clamp(26px,3.4vw,40px);margin:0 0 10px}
.one-top p{color:var(--ink-2);margin:0 0 20px}
.one-links{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:28px}
.one-links a{border:1px solid var(--line2);border-radius:999px;padding:8px 16px;color:var(--ink);text-decoration:none;font-weight:600}
.one-links a:hover{border-color:var(--ink)}
.one-deck{width:100%;aspect-ratio:16/9;border:1px solid var(--line);border-radius:8px;background:#000}
.panel+.panel{border-top:1px solid var(--line);margin-top:48px}
"""
    TOP = """<section class="one-top" id="top">
  <h1>원화 스테이블코인 준비금 공시 검증 시스템</h1>
  <p>미디어프로젝트 2026-2 최종 제출. 발표 자료, 판정기, 소스코드, 기획 문서를 이 페이지 한 장에 모았습니다.</p>
  <div class="one-links"><a href="https://sc2k.kr">판정기 sc2k.kr</a><a href="deck/">발표 자료 전체 화면</a><a href="https://github.com/itsinseong/sc2k">소스코드 GitHub</a></div>
  <iframe class="one-deck" src="deck/" title="SC2K 최종 발표 자료" loading="lazy"></iframe>
</section>"""

panels = ("" if not ONE else TOP + "\n") + "\n".join(f'<div class="panel" id="{k}"{"" if i == 0 or ONE else " hidden"}>\n{bodies[k]}\n</div>' for i, (k, _) in enumerate(TABS))

page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SC2K 기획 문서</title>
<link rel="icon" href="{FAVICON}">
<script>{HEAD_JS}</script>
<style>
{read("base.css")}
{HUB_CSS.replace("{JOST}", JOST)}
</style>
</head>
<body>
{HEADER}
{panels}
<script>{read("base.js")}{COPY_CLICK}</script>
<script>{ROUTER}</script>
<script>{THEME_JS}</script>
<script>{SEARCH_JS}</script>
</body>
</html>
"""
if ONE: page = page.replace("판정 체계", "공시 검증 시스템").replace("<title>SC2K 기획 문서</title>", "<title>SC2K 동료평가</title>")
assert "·" not in page, "가운뎃점 금지"
open(OUT, "w", encoding="utf-8").write(page)
ids = re.findall(r'\bid="([^"]+)"', page)
dup = {i for i in ids if ids.count(i) > 1}
missing = sorted(h for h in set(re.findall(r'href="#([^"]+)"', page)) if h not in ids)
print("written", OUT, f"{len(page)//1024}KB", "dup ids:", dup or "none", "missing anchors:", missing or "none")
