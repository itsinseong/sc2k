
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

let ctx = null, el = null;

// 토큰 묶음 한 줄 설명. 검증 주기(월간, 분기)와 회계법인 이름. 이름은 묶음의 모든 보고서에 있을 때만 쓴다
// ponytail: 평균 간격이 2개월을 넘으면 분기로 봄(반기나 연간 보고서가 생기면 구분을 늘릴 것)
const FIRM_END = / (LLP|S\.p\.A\.|S\.r\.l\.)$/;
const monthNo = (r) => Number(r.month.slice(0, 4)) * 12 + Number(r.month.slice(5));
function about(list) {
  const gap = list.length > 1 ? (monthNo(list.at(-1)) - monthNo(list[0])) / (list.length - 1) : 1;
  const firms = [...new Set(list.map((r) => r.attestation?.firm?.replace(FIRM_END, '')))];
  return `${gap > 2 ? '분기' : '월간'} 준비금 검증${firms.every(Boolean) ? `, ${firms.join(', ')}` : ''}`;
}

export function renderSidebar(target, next) {
  el = target; ctx = next;
  draw();
}

// 나라 칸 오른쪽에 깔리는 국기(은은하게, 왼쪽으로 갈수록 사라짐). 국기 파일은 flag-icons(MIT), site/flags/
const FLAG = { 'kr-v1': 'kr', us: 'us', 'eu-emt': 'eu', 'eu-emt-significant': 'eu', hk: 'hk', sg: 'sg', jp: 'jp' };
const flagBg = (id) => FLAG[id] ? ` side-flagbg" style="--flag:url(flags/${FLAG[id]}.svg)` : '';

// 나라 칸(flag 있음)은 이름 아래에 법 이름을 한 단계 작게 두고, 오른쪽은 국기 자리로 비운다
function link(href, name, active, note = '', flag = '') {
  const body = flag ? `<span class="side-nm"><span class="side-name">${esc(name)}</span>${note ? `<span class="side-law">${esc(note)}</span>` : ''}</span>` : `<span class="side-name">${esc(name)}</span>${note ? `<span class="side-date">${esc(note)}</span>` : ''}`;
  return `<a class="side-link ${active ? 'active' : ''}${flag}" href="${href}"${active ? ' aria-current="page"' : ''}>${body}</a>`;
}

function draw() {
  const { order, names, subs = {}, jurisdiction, reports, index, groups } = ctx;
  const cur = reports[index].token;
  const { ruleGroups, ruleActive = null } = ctx;
  // 보고서는 코인마다 한 줄(이름, 개수, 검증 한 줄 설명). 누르면 사이드바 오른쪽에 그 코인을 강조한 보고서 달력이 뜸
  const tok = ([name, idx]) => `<button type="button" class="side-tok ${name === cur ? 'active' : ''}" data-tok="${esc(name)}" aria-haspopup="dialog"><span class="side-name">${esc(ctx.coin(reports[idx[0]]))}</span><small class="num">${idx.length}건</small><span class="side-sub">${esc(about(idx.map((i) => reports[i])))}</span></button>`;
  const note = '<p class="side-note">발행사가 회계법인 검증을 받아 매달 또는 분기마다 공개한 준비금 보고서입니다.</p>';
  const kr = 'kr-v1', countries = order.filter((id) => id !== kr);
  const row = (id) => link(`#${id}`, names[id], jurisdiction === id, subs[id], flagBg(id));
  // 한국은 이 사이트의 기준이라 나라 목록 맨 위에 따로 둠
  const krRow = `<a class="side-link side-kr ${jurisdiction === kr ? 'active' : ''}${flagBg(kr)}" href="#${kr}"${jurisdiction === kr ? ' aria-current="page"' : ''}><span class="side-name">${esc(names[kr])}</span><span class="side-sub">후보값으로 판정, 확정 전</span></a><p class="side-group">해외 기준</p>`;
  const sec = (title, n, body, href) => `<section class="side-sec"><h2>${href ? `<a class="side-h" href="${href}">${title}</a>` : title}<small class="num">${n}</small></h2>${body}</section>`; // 칸은 접지 않고 늘 펼쳐 둠. href가 있으면 제목을 누를 수 있음
  // 판정 항목 칸은 app.js가 ruleGroups를 넘길 때만 그림. 제목은 설명 페이지 맨 위로, 묶음 이름은 그 묶음으로
  const ruleSec = ruleGroups ? sec('판정 항목', ruleGroups.reduce((n, [, ids]) => n + ids.length, 0),
    ruleGroups.map(([g, ids]) => link(`#rules/${ids[0]}`, g, ids.includes(ruleActive))).join(''), '#rules') : '';
  el.innerHTML = `<div class="side-sec side-top">${link('#', '종합 판정', !jurisdiction && ruleActive == null)}</div>
    ${sec('나라', countries.length + 1, krRow + countries.map(row).join(''))}
    ${ruleSec}
    ${sec('준비금 보고서', reports.length, note + groups.map(tok).join(''))}`;
}

export function bindSidebar(target) {
  target.addEventListener('click', (e) => {
    const t = e.target.closest('[data-tok]');
    if (t) ctx.openReports(t.dataset.tok, t);
    // 지금 주소와 같은 링크는 hashchange가 안 나서 스크롤이 그대로임. 직접 한 번 더 보내 그 자리로 다시 감
    const a = e.target.closest('a[href^="#"]');
    if (a && a.getAttribute('href') === (location.hash || '#')) window.dispatchEvent(new HashChangeEvent('hashchange'));
  });
}
