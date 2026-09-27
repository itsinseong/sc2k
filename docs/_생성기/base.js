// Word 붙여넣기용 정리: 화면용 서식(회색 배경, 웹폰트)을 걷어내고 Word가 인식하는 인라인 서식만 남긴다
const WORD={
  h2:'font-size:14pt;font-weight:bold;margin:16pt 0 6pt',
  h3:'font-size:12pt;font-weight:bold;margin:12pt 0 4pt',
  h4:'font-size:11pt;font-weight:bold;margin:8pt 0 2pt',
  p:'margin:0 0 6pt',li:'margin:0 0 3pt',
  table:'border-collapse:collapse;width:100%',
  th:'border:1px solid #000;background:#E7E7E7;padding:3pt 5pt;font-size:9.5pt;font-weight:bold;text-align:left',
  td:'border:1px solid #000;padding:3pt 5pt;font-size:9.5pt;vertical-align:top'
};
function clean(node){
  const c=node.cloneNode(true);
  c.querySelectorAll('.nocopy,button').forEach(n=>n.remove());
  c.querySelectorAll('figure').forEach(f=>{const p=document.createElement('p');p.textContent='['+(f.querySelector('figcaption')?.textContent||'그림')+' 삽입]';f.replaceWith(p)});
  c.querySelectorAll('.stats b').forEach(b=>b.after(': '));
  c.querySelectorAll('.tbd').forEach(n=>{const b=document.createElement('b');b.textContent='['+n.textContent+']';n.replaceWith(b)});
  c.querySelectorAll('dl').forEach(dl=>{const box=document.createElement('div');dl.querySelectorAll('dt').forEach(dt=>{const p=document.createElement('p');p.innerHTML='<b>'+dt.textContent+':</b> '+dt.nextElementSibling.innerHTML;box.appendChild(p)});dl.replaceWith(box)});
  c.querySelectorAll('td br').forEach(n=>n.remove());
  c.querySelectorAll('small').forEach(n=>n.replaceWith(document.createTextNode(' ('+n.textContent+')')));
  c.querySelectorAll('a').forEach(a=>a.replaceWith(document.createTextNode(a.textContent)));
  c.querySelectorAll('*').forEach(n=>{n.removeAttribute('class');n.removeAttribute('style');n.removeAttribute('id')});
  c.querySelectorAll('table').forEach(t=>{t.setAttribute('border','1');t.setAttribute('cellspacing','0');t.setAttribute('cellpadding','5')});
  for(const [tag,css] of Object.entries(WORD))c.querySelectorAll(tag).forEach(n=>n.setAttribute('style',css));
  return c;
}
// 정리된 노드를 {html, text}로 만든다. innerText는 화면에 붙어 있어야 줄바꿈이 맞게 나온다
function payload(node){
  const c=clean(node),holder=document.createElement('div');
  holder.style.cssText='position:fixed;left:-9999px;top:0;width:800px';
  holder.appendChild(c);document.body.appendChild(holder);
  const out={html:'<div style="font-family:\'맑은 고딕\',\'Malgun Gothic\',\'Apple SD Gothic Neo\',sans-serif;font-size:10pt;color:#000">'+c.innerHTML+'</div>',text:c.innerText};
  holder.remove();return out;
}
let pending=null; // 버튼 복사가 execCommand 경로로 떨어질 때 copy 이벤트에 넘길 내용
async function copyNode(node,btn){
  const d=payload(node);let ok=false;
  try{
    await navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([d.html],{type:'text/html'}),'text/plain':new Blob([d.text],{type:'text/plain'})})]);ok=true;
  }catch(e){pending=d;ok=document.execCommand('copy');pending=null}
  flash(btn,ok?'복사됨':'복사 실패');
}
// 드래그 선택 후 Cmd+C, Ctrl+C도 같은 정리를 거친다
document.addEventListener('copy',e=>{
  if(document.body.classList.contains('editing')&&!pending)return; // 수정 중에는 브라우저 기본 복사
  let d=pending;
  if(!d){
    const sel=getSelection();if(sel.isCollapsed||!sel.rangeCount)return;
    const r=sel.getRangeAt(0);let anc=r.commonAncestorContainer;if(anc.nodeType!==1)anc=anc.parentElement;
    let box=document.createElement('div');box.appendChild(r.cloneContents());
    // 표 안에서만 선택하면 tr, td 조각만 복제되므로 표 구조를 다시 씌운다
    const wrap={TR:['table','tbody','tr'],TBODY:['table','tbody'],TABLE:['table']}[anc.tagName];
    if(wrap){const root=document.createElement('div');let cur=root;for(const t of wrap){const el=document.createElement(t);cur.appendChild(el);cur=el}cur.append(...box.childNodes);box=root}
    d=payload(box);
  }
  e.clipboardData.setData('text/html',d.html);e.clipboardData.setData('text/plain',d.text);e.preventDefault();
});
function flash(btn,msg){const t=btn.textContent;btn.textContent=msg;btn.classList.add('ok');setTimeout(()=>{btn.textContent=t;btn.classList.remove('ok')},1400)}
function copyPng(fig,btn){
  const svg=fig.querySelector('svg'),vb=svg.viewBox.baseVal,k=2,img=new Image();
  const url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'}));
  img.onload=()=>{
    const cv=document.createElement('canvas');cv.width=vb.width*k;cv.height=vb.height*k;
    cv.getContext('2d').drawImage(img,0,0,cv.width,cv.height);URL.revokeObjectURL(url);
    cv.toBlob(async b=>{
      try{await navigator.clipboard.write([new ClipboardItem({'image/png':b})]);flash(btn,'복사됨')}
      catch(e){const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=fig.dataset.name+'.png';a.click();flash(btn,'PNG 저장됨')}
    });
  };
  img.onerror=()=>flash(btn,'변환 실패');img.src=url;
}
