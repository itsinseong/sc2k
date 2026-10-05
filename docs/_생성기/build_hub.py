"""idea, prd, ref, final 본문 + base.css, base.js -> ../StableWatch_종합.html (탭 4개, 전체 검색, 다크 모드).
디자인과 스크립트는 실록_종합.html(AI융합캡스톤디자인2)과 같은 체계를 복사해 쓴다."""
import base64, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "StableWatch_종합.html")

def read(name):
    return open(os.path.join(HERE, name), encoding="utf-8").read()

TABS = [("idea", "아이디어 제안서"), ("prd", "PRD"), ("ref", "레퍼런스"), ("site", "판정기"), ("mas", "MAS 자문"), ("final", "최종"), ("todo", "할 일")]
bodies = {k: read(f"{k}.html") for k, _ in TABS}
shot = base64.b64encode(open(os.path.join(HERE, "dash.jpg"), "rb").read()).decode()
bodies["idea"] = bodies["idea"].replace('src="dash.jpg"', f'src="data:image/jpeg;base64,{shot}"')

HEAD_JS = """try{var t=localStorage.getItem('stablewatch-theme')}catch(e){}
document.documentElement.dataset.theme=t||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');"""

SVG_SEARCH = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
SVG_SUN = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
SVG_MOON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/></svg>'

HEADER = f"""<header class="hub-top">
  <div class="hub-bar">
    <a class="hub-brand" href="#idea"><b>Stablecoin2Korea</b><small>미디어프로젝트 2026-2, 원화 스테이블코인 준비금 공시 판정기</small></a>
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
.hub-brand b{font-size:19px;font-weight:800;letter-spacing:-.01em}
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

panels = "\n".join(f'<div class="panel" id="{k}"{"" if i == 0 else " hidden"}>\n{bodies[k]}\n</div>' for i, (k, _) in enumerate(TABS))

page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stablecoin2Korea 기획 문서</title>
<script>{HEAD_JS}</script>
<style>
{read("base.css")}
{HUB_CSS}
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
assert "·" not in page, "가운뎃점 금지"
open(OUT, "w", encoding="utf-8").write(page)
ids = re.findall(r'\bid="([^"]+)"', page)
dup = {i for i in ids if ids.count(i) > 1}
missing = sorted(h for h in set(re.findall(r'href="#([^"]+)"', page)) if h not in ids)
print("written", OUT, f"{len(page)//1024}KB", "dup ids:", dup or "none", "missing anchors:", missing or "none")
