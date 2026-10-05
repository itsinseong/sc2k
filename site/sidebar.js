
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

let ctx = null, el = null;
const open = { country: true, report: true, rules: false }; // 접기 상태. 다시 그려도 유지
let onRules = false;

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

function link(href, name, active, note = '') {
  return `<a class="side-link ${active ? 'active' : ''}" href="${href}"${active ? ' aria-current="page"' : ''}><span class="side-name">${esc(name)}</span>${note ? `<span class="side-date">${esc(note)}</span>` : ''}</a>`;
}

function draw() {
  const { order, names, subs = {}, jurisdiction, reports, index, groups } = ctx;
  const cur = reports[index].token;
  const { ruleGroups, ruleNames = {}, ruleActive = null } = ctx;
  if (ruleActive != null && !onRules) open.rules = true; // 규칙 설명 페이지로 들어오는 순간 한 번 펼침
  onRules = ruleActive != null;
  // 보고서는 코인마다 한 줄(이름, 개수, 검증 한 줄 설명). 누르면 사이드바 오른쪽에 그 코인을 강조한 보고서 달력이 뜸
  const tok = ([name, idx]) => `<button type="button" class="side-tok ${name === cur ? 'active' : ''}" data-tok="${esc(name)}" aria-haspopup="dialog"><span class="side-name">${esc(ctx.coin(reports[idx[0]]))}</span><small class="num">${idx.length}건</small><span class="side-sub">${esc(about(idx.map((i) => reports[i])))}</span></button>`;
  const note = '<p class="side-note">발행사가 회계법인 검증을 받아 매달 또는 분기마다 공개한 준비금 보고서입니다. 코인을 누르면 달력이 열리고, 달을 고르면 그 보고서로 판정합니다.</p>';
  const kr = 'kr-v1', countries = order.filter((id) => id !== kr);
  const row = (id) => link(`#${id}`, names[id], jurisdiction === id, subs[id]);
  // 한국은 이 사이트의 기준이라 나라 목록 맨 위에 따로 둠
  const krRow = `<a class="side-link side-kr ${jurisdiction === kr ? 'active' : ''}" href="#${kr}"${jurisdiction === kr ? ' aria-current="page"' : ''}><span class="side-name">${esc(names[kr])}</span><span class="side-sub">후보값으로 판정, 확정 전</span></a><p class="side-group">해외 규칙</p>`;
  const sec = (key, title, n, body) => `<details class="side-sec" data-sec="${key}"${open[key] ? ' open' : ''}><summary><h2>${title}<small class="num">${n}</small></h2></summary>${body}</details>`;
  // 규칙 칸은 app.js가 ruleGroups를 넘길 때만 그림. 맨 위는 전체 설명, 아래는 묶음별 규칙 링크
  const ruleSec = ruleGroups ? sec('rules', '규칙', ruleGroups.reduce((n, [, ids]) => n + ids.length, 0),
    link('#rules', '규칙 설명 전체', ruleActive === 'all') +
    ruleGroups.map(([g, ids]) => `<p class="side-group">${esc(g)}</p>${ids.map((rid) => link(`#rules/${rid}`, `${rid} ${ruleNames[rid] ?? ''}`, ruleActive === rid)).join('')}`).join('')) : '';
  el.innerHTML = `<div class="side-sec side-top">${link('#', '개요', !jurisdiction && ruleActive == null)}</div>
    ${sec('country', '나라', countries.length + 1, krRow + countries.map(row).join(''))}
    ${ruleSec}
    ${sec('report', '준비금 보고서', reports.length, note + groups.map(tok).join(''))}`;
}

export function bindSidebar(target) {
  target.addEventListener('toggle', (e) => {
    if (e.target.dataset?.sec) open[e.target.dataset.sec] = e.target.open;
  }, true);
  target.addEventListener('click', (e) => {
    const t = e.target.closest('[data-tok]');
    if (t) ctx.openReports(t.dataset.tok, t);
  });
}
