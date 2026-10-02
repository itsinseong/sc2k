import { RULE_IDS, STATUS, evaluateReport, resolveRuleDef, calendarDaysBetween } from './engine.js';

const ORDER = ['us', 'eu-emt', 'eu-emt-significant', 'hk', 'sg', 'kr-v1'];
const CROSS_BORDER = new Set(['hk', 'eu-emt', 'eu-emt-significant', 'kr-v1']);
const FOREIGN_NOTICE = '이 나라 발행사 보고서가 없어서 해외 보고서를 이 나라 규칙에 맞춰 본 결과이며, 이 나라 회사의 실제 공시가 아닙니다';
const KR_NOTICE = '한국 열은 제안값이며 확정된 규정이 아닙니다';
const CATEGORIES = [
  ['bank', '은행 예금'], ['repo', '하루짜리 담보 대출(레포)'],
  ['fund', '국채 펀드'], ['treasury', '국채'], ['other', '기타'],
];
const TYPE_NAMES = {cash:'현금',bank_deposit:'은행 예금',treasury_bill_93d:'93일 이하 국채',overnight_repo:'하루짜리 레포',government_mmf:'국채 펀드',cash_equivalent:'현금성 자산',government_bond_3m:'3개월 이하 국채',hqla:'고유동성 우량자산',bank_deposit_3m:'3개월 이내 은행 예금',low_risk_liquid_asset:'저위험 고유동성 자산',government_bond:'국채',other_designated:'그 밖의 지정 자산',examination:'검증 보고서',attestation:'확인 보고서',audit:'감사',quarterly_review:'분기 검토', 'reasonable assurance':'합리적 확신'};
const $ = (sel) => document.querySelector(sel);
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pct = (ratio, digits=2) => ratio == null ? '자료 없음' : `${(ratio * 100).toFixed(digits)}%`;
const metricPct = (ratio, digits=2) => ratio == null ? '자료 없음' : `${pct(ratio, digits).slice(0,-1)}<small class="unit">%</small>`;
const count = (x) => x == null ? '자료 없음' : Number(x).toLocaleString('ko-KR');
const date = (x) => x || '자료 없음';
const file = (path) => fetch(path).then((response) => {
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return response.json();
});
const state = { reportIndex: 0, jurisdiction: null, tab: 'rules', openRule: null, showAll: false, candidates: {} };
let reports, jurisdictions, copy, weekly;

function label(report) {
  const issuer = report.token === 'USDC' ? 'Circle' : 'Paxos';
  return `${issuer} ${report.token} ${Number(report.month.slice(5))}월`;
}
function ownIndices(jurisdiction) {
  if (jurisdiction === 'us') return reports.map((r,i) => ['USDC','PYUSD','USDP'].includes(r.token) ? i : -1).filter((i) => i >= 0);
  if (jurisdiction === 'sg') return reports.map((r,i) => r.token === 'USDG' ? i : -1).filter((i) => i >= 0);
  return [];
}
function judged(jurisdiction) {
  return evaluateReport(reports[state.reportIndex], jurisdictions[jurisdiction], jurisdiction === 'kr-v1' ? state.candidates : {});
}
function days(report) { return calendarDaysBetween(report.as_of, report.attestation?.signed); }
function bankInfo(report) {
  const c = report.components || {};
  if (!report.fair_value) return { ratio:null, approx:false };
  if (c.cash != null) return { ratio:c.cash / report.fair_value, approx:false };
  if (c.other != null) return { ratio:c.other / report.fair_value, approx:true };
  return { ratio:null, approx:false };
}
function mix(report) {
  const c = report.components || {}, total = report.fair_value;
  if (!total) return CATEGORIES.map(([type]) => ({ type, ratio:0 }));
  return [
    {type:'bank',ratio:(c.cash ?? 0)/total},
    {type:'repo',ratio:(c.repo ?? 0)/total},
    {type:'fund',ratio:(c.government_mmf ?? c.circle_reserve_fund ?? 0)/total},
    {type:'treasury',ratio:(c.treasury ?? 0)/total},
    {type:'other',ratio:(c.other ?? 0)/total},
  ];
}
function fmt(rule, value, empty='자료 없음') {
  if (value == null) return empty;
  if (Array.isArray(value)) return value.length ? value.map((v) => TYPE_NAMES[v] || v).join(', ') : '해당 없음';
  if (typeof value === 'boolean') return value ? '예' : '아니오';
  if (typeof value === 'number') {
    if (rule === 'R01' || rule === 'R05') return pct(value);
    if (['R03','R04','R07','R10','R13'].includes(rule)) return `${count(value)}일`;
    return count(value);
  }
  return TYPE_NAMES[value] || String(value);
}
function safeLink(url) { try { const parsed = new URL(url); return ['http:','https:'].includes(parsed.protocol) ? parsed.href : ''; } catch { return ''; } }
function route() {
  const [raw, tab] = window.location.hash.slice(1).split('/');
  const jurisdiction = raw === 'kr' ? 'kr-v1' : raw;
  if (ORDER.includes(jurisdiction)) {
    state.jurisdiction = jurisdiction;
    state.tab = tab === 'reports' ? 'reports' : 'rules';
  } else { state.jurisdiction = null; state.tab = 'rules'; }
  state.openRule = null;
  state.showAll = false;
  render();
}
function selectReport(index) {
  if (!Number.isInteger(index) || index < 0 || index >= reports.length) return;
  state.reportIndex = index;
  state.openRule = null;
  render();
}
function selectJurisdiction(id) {
  if (!ORDER.includes(id)) return;
  window.location.hash = `#${id}`;
  if (state.jurisdiction === id && state.tab === 'rules') route();
  window.scrollTo({top:0,behavior:'instant'});
}
function ruleStrip(results) {
  return `<span class="rule-strip" aria-hidden="true">${results.map((v) => `<i class="${v.status === STATUS.MET ? 'met' : v.status === STATUS.UNMET ? 'unmet' : v.status === STATUS.CAUTION ? 'caution' : ''}"></i>`).join('')}</span>`;
}
function chartComposition() {
  const proposal = jurisdictions['kr-v1'].rules.R05.candidates.find((c) => c.id === 'proposal');
  const limit = proposal?.threshold;
  const bar = reports.map((r,i) => {
    const slices = mix(r).filter((x) => x.ratio > 0);
    const title = `${label(r)}: ${slices.map((x) => `${CATEGORIES.find(([k]) => k === x.type)[1]} ${pct(x.ratio)}`).join(', ')}`;
    const b = bankInfo(r);
    return `<button type="button" class="bar-button ${state.reportIndex === i ? 'selected' : ''}" data-report="${i}" aria-label="${esc(title)}" title="${esc(title)}"><span class="bank-value num ${b.ratio != null && limit != null && b.ratio < limit ? 'below' : ''}">${b.ratio == null ? '' : pct(b.ratio,1)}${b.approx ? '<sup>*</sup>' : ''}</span><span class="stack">${slices.map((x) => `<span class="seg ${x.type}" style="height:${x.ratio*100}%"></span>`).join('')}</span></button>`;
  }).join('');
  return `<section class="chart-card glass" aria-labelledby="composition-title"><div class="panel-heading"><div><h2 id="composition-title">준비금 구성 비교</h2><p>보고서 ${reports.length}건, 각 보고서 준비금 공정가치 기준</p></div><span class="panel-index">위 숫자는 은행 예금 비중</span></div><div class="plot-wrap"><div class="plot"><span class="tick num" style="bottom:100%">100%</span><span class="tick num" style="bottom:50%">50%</span><span class="tick num" style="bottom:0">0%</span><div class="bars">${bar}</div>${limit != null ? `<div class="reference-line" style="bottom:${limit*100}%"><span>공시안 제안 은행 예금 ${pct(limit,0)}</span></div>` : ''}</div>${axisLabels()}</div><div class="legend">${CATEGORIES.map(([key,name]) => `<span><i class="seg ${key}"></i>${name}</span>`).join('')}</div>${reports.some((x) => bankInfo(x).approx) ? '<p class="chart-note">* Circle은 은행 예금을 따로 적지 않아 기타 준비자산 비중으로 대신 계산했습니다. 국채가 섞인 달이 있습니다.</p>' : ''}</section>`;
}
function axisLabels() { return `<div class="axis-labels">${reports.map((r,i) => `<span class="${state.reportIndex === i ? 'chosen' : ''}">${esc(r.token)}<br>${Number(r.month.slice(5))}월</span>`).join('')}</div>`; }
function daysRange() {
  const v = reports.map(days).filter((x) => x != null), lim = jurisdictions['kr-v1'].rules.R10.candidates.find((c) => c.id === 'proposal')?.deadline_days;
  const lo = Math.min(...v), hi = Math.max(...v);
  return `보고서 ${v.length}건 모두 ${lo}~${hi}일${lim != null && hi <= lim ? `, 공시안 제안 ${lim}일 안` : ''}`;
}
function chartDays() {
  const proposal = jurisdictions['kr-v1'].rules.R10.candidates.find((c) => c.id === 'proposal');
  const limit = proposal?.deadline_days;
  const vals = reports.map(days), max = Math.max(limit || 0,...vals.filter((v) => v != null));
  const scale = Math.ceil((max + 5) / 10) * 10;
  return `<section class="chart-card glass" aria-labelledby="days-title"><div class="panel-heading"><div><h2 id="days-title">서명까지 걸린 날</h2><p>보고서 기준일부터 검증 서명일까지의 달력 기준 일수</p></div><span class="panel-index">02 / 02</span></div><div class="plot-wrap"><div class="plot"><span class="tick num" style="bottom:100%">${scale}</span><span class="tick num" style="bottom:50%">${scale/2}</span><span class="tick num" style="bottom:0">0</span><div class="bars">${reports.map((r,i) => {const h = vals[i] == null ? 0 : vals[i]/scale*100;return `<button type="button" data-report="${i}" class="bar-button ${state.reportIndex === i ? 'selected' : ''}" aria-label="${esc(label(r))}, ${vals[i] == null ? '자료 없음' : `${vals[i]}일`}"><span class="day-bar" style="height:${h}%"></span><span class="day-value num" style="--height:${h}%">${vals[i] ?? '—'}</span></button>`;}).join('')}</div>${limit != null ? `<div class="reference-line" style="bottom:${limit/scale*100}%"><span>공시안 제안 ${count(limit)}일</span></div>` : ''}</div>${axisLabels()}</div></section>`;
}
function home() {
  const r = reports[state.reportIndex], cash = bankInfo(r), own = r.attestation?.firm || '이미지 서명, 이름 확인 필요';
  return `<div class="home"><div class="home-head"><div><h1>여섯 나라 준비금 공시 판정</h1><p>${esc(label(r))} 보고서 / 기준일 ${esc(r.as_of)} / 검증인 ${esc(own)}</p></div><span class="head-index">보고서 ${state.reportIndex+1} / ${reports.length}</span></div>
    <section class="stats glass" aria-label="선택 보고서의 주요 수치"><div class="stat stat-main"><span class="stat-label">은행 예금 비중${cash.approx ? ' (대신 계산)' : ''}</span><strong class="stat-value num">${metricPct(cash.ratio)}</strong><span class="stat-note">${cash.approx ? '기타 준비자산으로 대신 계산, 국채가 섞인 달이 있음' : '은행 예금 / 준비금 공정가치, 공시안 제안 15%'}</span></div><div class="stat"><span class="stat-label">서명까지 걸린 날</span><strong class="stat-value num">${days(r) == null ? '자료 없음' : `${days(r)}<small>일</small>`}</strong><span class="stat-note">${daysRange()}</span></div><div class="stat"><span class="stat-label">커버리지</span><strong class="stat-value num">${metricPct(r.coverage ?? (r.fair_value && r.circulation ? r.fair_value/r.circulation : null))}</strong><span class="stat-note">준비금 공정가치 / 발행잔액, 100% 이상이 기준</span></div></section>
    <div class="charts">${chartComposition()}</div>
    <section class="country-section glass" aria-labelledby="country-title"><div class="section-head"><div><h2 id="country-title">나라별 판정</h2><p>선택한 보고서를 각 나라의 규칙 15개에 대조한 결과</p></div><span class="strip-legend"><span><i class="met"></i>충족</span><span><i class="caution"></i>주의</span><span><i class="unmet"></i>미충족</span><span><i></i>판정 안 됨</span></span></div><div class="country-grid">${ORDER.map((id) => {
      const v = judged(id), met = v.filter((x) => x.status === STATUS.MET).length, unmet = v.filter((x) => x.status === STATUS.UNMET).length;
      const ownCount = ownIndices(id).length;
      return `<button type="button" class="country-card" data-country="${id}" aria-label="${esc(copy.나라[id].이름)} 상세, 충족 ${met}, 미충족 ${unmet}, 이 나라 보고서 ${ownCount}건"><span class="country-top"><strong>${esc(copy.나라[id].이름)}</strong><small>${esc(jurisdictions[id].legal_status)}</small></span>${ruleStrip(v)}<span class="country-meta"><span><b>충족 ${met}</b> / 미충족 ${unmet} / 전체 ${RULE_IDS.length}</span><em>보고서 ${ownCount}건${id === 'hk' ? `, 주간 명세 ${weekly.주간.length}주` : ''}</em></span></button>`;
    }).join('')}</div></section><div class="disclosure"><strong>${KR_NOTICE}</strong><br>홍콩, EU 일반, EU 중요, 한국 판정: ${FOREIGN_NOTICE}</div></div>`;
}
function statusClass(status) { return status === STATUS.MET ? 'met' : status === STATUS.UNMET ? 'unmet' : status === STATUS.CAUTION ? 'caution' : ''; }
function rulesPane(id) {
  const values = judged(id), active = values.filter((v) => [STATUS.MET,STATUS.UNMET,STATUS.CAUTION].includes(v.status));
  const inactive = values.filter((v) => ![STATUS.MET,STATUS.UNMET,STATUS.CAUTION].includes(v.status));
  const shown = [...active,...(state.showAll ? inactive : [])];
  const kr = id === 'kr-v1' ? candidatePanel() : '';
  return kr + `<div class="pane-intro"><strong>판정 보고서: ${esc(label(reports[state.reportIndex]))}</strong> / 충족 ${active.filter((v) => v.status === STATUS.MET).length} / 미충족 ${active.filter((v) => v.status === STATUS.UNMET).length}<br>판정이 나온 규칙을 먼저 표시합니다. ${esc(id === 'kr-v1' ? KR_NOTICE : '')}</div>${shown.map((v) => ruleItem(id,v)).join('')}${inactive.length ? `<button class="fold-button" data-action="toggle-rules" type="button">${state.showAll ? `나머지 ${inactive.length}개 접기 ↑` : `판정이 나오지 않은 ${inactive.length}개 보기 ↓`}</button>` : ''}`;
}
function candidatePanel() {
  const rules = jurisdictions['kr-v1'].rules;
  const rows = RULE_IDS.filter((rid) => (rules[rid]?.candidates || []).length > 1).map((rid) => {
    const e = rules[rid], cur = state.candidates[rid] || e.default_candidate || e.candidates[0].id;
    return `<div class="cand-row"><span class="cand-rule"><b>${rid}</b>${esc(copy.규칙15개[rid])}</span><span class="cand-opts">${e.candidates.map((c) => `<label class="${c.id === cur ? 'on' : ''}"><input type="radio" name="kc-${rid}" data-candidate="${rid}" value="${esc(c.id)}" ${c.id === cur ? 'checked' : ''}>${esc(c.label)}</label>`).join('')}</span></div>`;
  }).join('');
  return `<section class="cand-panel"><div class="cand-head"><strong>한국 후보값</strong><span>후보를 바꾸면 아래 판정이 바로 바뀝니다. ${KR_NOTICE}</span></div>${rows}</section>`;
}
function ruleItem(id,v) {
  const open = state.openRule === v.rule;
  return `<article class="rule-item ${open ? 'open' : ''}"><button type="button" data-rule="${v.rule}" class="rule-heading" aria-expanded="${open}" aria-controls="body-${v.rule}"><span class="rule-code">${v.rule}</span><span class="rule-title">${esc(copy.규칙15개[v.rule])}</span><span class="rule-vals num">${v.value != null ? `${esc(fmt(v.rule,v.value))}${v.approx ? '*' : ''}` : ''}${v.threshold != null ? `<small>기준 ${esc(fmt(v.rule,v.threshold))}</small>` : ''}</span><span class="status ${statusClass(v.status)}">${esc(v.status)}</span><span class="chevron" aria-hidden="true">${open ? '⌃' : '⌄'}</span></button>${open ? `<div class="rule-body" id="body-${v.rule}">${ruleBody(id,v)}</div>` : ''}</article>`;
}
function ruleBody(id,v) {
  const entry = jurisdictions[id].rules[v.rule] || {}, def = resolveRuleDef(jurisdictions[id],v.rule,id === 'kr-v1' ? state.candidates[v.rule] : undefined) || {};
  const link = safeLink(v.url);
  const explanation = v.status === STATUS.NO_DATA ? '보고서에 비교할 값이 없습니다.' : v.status === STATUS.NOT_REGULATED ? '이 항목에는 규정이 없습니다.' : v.status === STATUS.PENDING ? '세부 기준이 위임되어 아직 정해지지 않았습니다.' : v.status === STATUS.UNRESEARCHED ? '근거 조사가 끝나지 않았습니다.' : '';
  const radio = id === 'kr-v1' && entry.candidates?.length ? `<fieldset class="candidate-field"><legend>한국 후보값 선택</legend>${entry.candidates.map((c) => `<label><input type="radio" name="candidate-${v.rule}" data-candidate="${v.rule}" value="${esc(c.id)}" ${c.id === (state.candidates[v.rule] || entry.default_candidate || entry.candidates[0].id) ? 'checked' : ''}><span>${esc(c.label)}</span></label>`).join('')}</fieldset>` : '';
  return `<dl class="value-pair"><div><dt>보고서 값</dt><dd class="num">${esc(fmt(v.rule,v.value))}${v.approx ? ' (근사)' : ''}</dd></div><div><dt>기준</dt><dd class="num">${esc(fmt(v.rule,v.threshold,'기준 없음'))}</dd></div></dl>${explanation ? `<p>${esc(explanation)}</p>` : ''}<p><span class="key">요건</span>${esc(def.requirement || '자료 없음')}</p><p><span class="key">근거 조문</span>${esc(v.article || '기재 없음')}</p>${v.approx ? '<p>기타 준비자산으로 대신 계산, 국채가 섞인 달이 있음</p>' : ''}${link ? `<p><a href="${esc(link)}" target="_blank" rel="noopener noreferrer">원문 링크 열기 ↗</a></p>` : '<p><span class="key">원문 링크</span>자료 없음</p>'}${radio}`;
}
function reportItem(i) {
  const r = reports[i], b = bankInfo(r), current = i === state.reportIndex;
  return `<button type="button" class="report-item ${current ? 'current' : ''}" data-report="${i}" aria-pressed="${current}"><span class="report-item-top"><strong>${esc(label(r))}</strong>${current ? '<em>판정에 사용 중</em>' : '<em>이 보고서로 판정 →</em>'}</span><p class="issuer">${esc(r.issuer)}</p><dl class="report-fields"><div><dt>기준일</dt><dd class="num">${esc(date(r.as_of))}</dd></div><div><dt>커버리지</dt><dd class="num">${pct(r.coverage ?? (r.fair_value/r.circulation))}</dd></div><div><dt>서명일</dt><dd class="num">${esc(date(r.attestation?.signed))}</dd></div><div><dt>검증인</dt><dd>${esc(r.attestation?.firm || '이미지 서명, 이름 확인 필요')}</dd></div><div><dt>서명까지 걸린 날</dt><dd class="num">${days(r) == null ? '자료 없음' : `${days(r)}일`}</dd></div><div><dt>은행 예금 비중</dt><dd class="num">${pct(b.ratio)}${b.approx ? ' (기타 대신 계산)' : ''}</dd></div></dl>${b.approx ? '<p class="report-note">기타 준비자산으로 대신 계산, 국채가 섞인 달이 있음</p>' : ''}</button>`;
}
function weeklyPane() {
  const max = Math.max(...weekly.주간.map((row) => row.준비금));
  return `<div class="weekly"><span class="weekly-warning">회계법인 확인이 없는 회사 자체 공시</span><p>${esc(weekly.발행사)}의 ${esc(weekly.코인)} 주간 명세 ${weekly.주간.length}주치. ${esc(weekly.기준)}. 단위: ${esc(weekly.단위)}. ${esc(weekly.준비금구성)}.</p><table><thead><tr><th scope="col">기준일</th><th scope="col">유통량</th><th scope="col">준비금</th><th scope="col">규모 비교</th></tr></thead><tbody>${weekly.주간.map((row) => `<tr><td>${esc(row.기준일)}</td><td>${count(row.유통량)}</td><td>${count(row.준비금)}</td><td><div class="weekly-bars" role="img" aria-label="${esc(row.기준일)} 준비금 ${row.준비금}, 유통량 ${row.유통량} ${esc(weekly.단위)}"><i style="width:${row.준비금/max*100}%"></i><b style="width:${row.유통량/max*100}%"></b></div></td></tr>`).join('')}</tbody></table><div class="weekly-legend"><span><i style="background:#D9D5D1"></i>준비금</span><span><i style="background:var(--accent)"></i>유통량</span></div><p>${esc(weekly.주석)}. 이 값은 판정 엔진에 넣지 않습니다.</p></div>`;
}
function reportsPane(id) {
  if (id === 'hk') return weeklyPane();
  const indices = ownIndices(id);
  if (!indices.length) {
    const text = id === 'kr-v1' ? '한국에는 발행 전이라 보고서가 없습니다. 해외 보고서를 한국 후보값에 넣어 판정합니다.' : '확보한 발행사 보고서가 없습니다';
    return `<div class="empty-report">${esc(text)}${id === 'kr-v1' ? `<small>${KR_NOTICE}</small>` : ''}</div>`;
  }
  return `<div class="pane-intro">${esc(copy.나라[id].이름)} 발행사 검증 보고서 ${indices.length}건. 보고서를 누르면 그 보고서로 판정이 바뀝니다.</div>${indices.map(reportItem).join('')}`;
}
function detail() {
  const id = state.jurisdiction, jur = jurisdictions[id], info = copy.나라[id], r = reports[state.reportIndex];
  const results = judged(id), met = results.filter((v) => v.status === STATUS.MET).length, unmet = results.filter((v) => v.status === STATUS.UNMET).length;
  const caution = results.filter((v) => v.status === STATUS.CAUTION).length, done = met + unmet + caution, none = RULE_IDS.length - done;
  const T = RULE_IDS.length, a1 = met/T*100, a2 = (met+caution)/T*100, a3 = done/T*100;
  const links = [...new Map(Object.values(jur.rules).filter((d) => safeLink(d.url)).map((d) => [safeLink(d.url), d.article || d.requirement])).entries()].slice(0,5);
  const reportCount = ownIndices(id).length;
  return `<div class="detail"><div class="detail-head"><a href="#" class="back-link">← 개요로 돌아가기</a><span class="context">선택 보고서 ${esc(label(r))} / 기준일 ${esc(r.as_of)}</span></div><div class="detail-layout"><section class="identity-card glass" aria-label="${esc(info.이름)} 개요"><span class="watermark" aria-hidden="true">${esc(info.워터마크)}</span><div class="identity-top"><div><h1>${esc(info.이름)}</h1></div><div class="legal">법적 상태<strong>${esc(jur.legal_status)}</strong></div></div><div class="score-area"><div class="score-ring" style="background:conic-gradient(var(--accent) 0 ${a1}%, #8FB0C8 ${a1}% ${a2}%, var(--red) ${a2}% ${a3}%, #E5E2DF ${a3}% 100%)" role="img" aria-label="판정 ${done}개 중 충족 ${met}, 주의 ${caution}, 미충족 ${unmet}, 판정 안 됨 ${none}"><span class="score-center"><small>판정된 규칙 ${done}개 중 충족</small><strong class="num">${met}<small class="unit">개</small></strong><em>판정 안 됨 ${none}개는 보고서에 값이 없음</em></span></div><div class="score-caption"><span><i class="dot met"></i>충족 ${met}</span><span><i class="dot caution"></i>주의 ${caution}</span><span><i class="dot unmet"></i>미충족 ${unmet}</span><span><i class="dot"></i>판정 안 됨 ${none}</span></div></div><div class="identity-bottom"><div class="small-head">규정 설명</div><p>${esc(info.설명)}</p>${CROSS_BORDER.has(id) ? `<div class="comparison-note">${FOREIGN_NOTICE}</div>` : !ownIndices(id).includes(state.reportIndex) ? '<div class="comparison-note">선택한 보고서는 이 나라 발행사의 보고서가 아닙니다.</div>' : ''}${id === 'kr-v1' ? `<div class="comparison-note">${KR_NOTICE}</div>` : ''}${links.length ? `<div class="small-head">규제 원문</div><ul class="source-links">${links.map(([u,t]) => `<li><a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(t)}</a></li>`).join('')}</ul>` : ''}<div class="source-date">규칙 자료 기준일 ${esc(jur.as_of)} / 판정 보고서 기준일 ${esc(r.as_of)}</div></div></section><section class="detail-right glass" aria-label="${esc(info.이름)} 판정과 보고서"><div class="detail-tabs" role="tablist" aria-label="상세 내용"><button type="button" role="tab" data-tab="rules" aria-selected="${state.tab === 'rules'}" tabindex="0">규칙 ${RULE_IDS.length}개</button><button type="button" role="tab" data-tab="reports" aria-selected="${state.tab === 'reports'}" tabindex="0">이 나라 보고서${id === 'hk' ? ` / 주간 명세 ${weekly.주간.length}주` : ` ${reportCount}건`}</button></div><div class="pane" role="tabpanel">${state.tab === 'rules' ? rulesPane(id) : reportsPane(id)}</div></section></div><nav class="country-nav" aria-label="나라 이동"><a href="#" >전체 개요</a>${ORDER.map((key) => `<a href="#${key}" class="${id === key ? 'active' : ''}" ${id === key ? 'aria-current="page"' : ''}>${esc(copy.나라[key].이름)}</a>`).join('')}</nav></div>`;
}
function render() {
  if (!reports) return;
  $('#app').innerHTML = state.jurisdiction ? detail() : home();
  $('#report-select').value = String(state.reportIndex);
  $('#rail-home').classList.toggle('active',!state.jurisdiction);
  $('#rail-country').classList.toggle('active',Boolean(state.jurisdiction && state.jurisdiction !== 'kr-v1'));
  $('#rail-kr').classList.toggle('active',state.jurisdiction === 'kr-v1');
  $('#rail-country').href = state.jurisdiction && state.jurisdiction !== 'kr-v1' ? `#${state.jurisdiction}` : '#us';
}
async function init() {
  try {
    const files = await Promise.all([
      file('./data/reports.json'), file('./화면문구.json'), file('./data/홍콩_주간명세.json'),
      ...ORDER.map((id) => file(`./jurisdictions/${id}.json`)),
    ]);
    reports = files[0].reports; copy = files[1]; weekly = files[2];
    jurisdictions = Object.fromEntries(ORDER.map((id,i) => [id, files[i+3]]));
    state.reportIndex = Math.max(0,reports.findIndex((r) => r.token === 'PYUSD'));
    $('#report-select').innerHTML = reports.map((r,i) => `<option value="${i}">${esc(label(r))}</option>`).join('');
    route();
  } catch (error) {
    console.error('자료 불러오기 실패',error);
    $('#app').innerHTML = '<div class="empty-report">자료를 불러오지 못했습니다. 정적 웹 서버에서 다시 열어 주세요.</div>';
  }
}
$('#report-select').addEventListener('change',(e) => selectReport(Number(e.target.value)));
$('#app').addEventListener('click',(e) => {
  const report = e.target.closest('[data-report]'); if (report) return selectReport(Number(report.dataset.report));
  const country = e.target.closest('[data-country]'); if (country) return selectJurisdiction(country.dataset.country);
  const tab = e.target.closest('[data-tab]'); if (tab) {const next = tab.dataset.tab; if (next !== state.tab) window.location.hash = `#${state.jurisdiction}${next === 'reports' ? '/reports' : ''}`;return;}
  const fold = e.target.closest('[data-action="toggle-rules"]'); if (fold) { state.showAll = !state.showAll; if (!state.showAll && ![STATUS.MET,STATUS.UNMET,STATUS.CAUTION].includes(judged(state.jurisdiction).find((v) => v.rule === state.openRule)?.status)) state.openRule = null; render(); return; }
  const rule = e.target.closest('[data-rule]'); if (rule) {state.openRule = state.openRule === rule.dataset.rule ? null : rule.dataset.rule; render(); return;}
});
$('#app').addEventListener('change',(e) => {
  if (e.target.matches('[data-candidate]')) {
    state.candidates[e.target.dataset.candidate] = e.target.value;
    render();
  }
});
window.addEventListener('hashchange',route);
init();
