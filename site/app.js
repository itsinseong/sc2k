import { RULE_IDS, STATUS, evaluateReport, resolveRuleDef, calendarDaysBetween } from './engine.js';
import { krSummary, ruleTable, ruleDots, ruleDotsPlots } from './charts.js';
import { mountGlobe, mountHeroGlobe } from './globe.js';

const ORDER = ['us', 'eu-emt', 'eu-emt-significant', 'hk', 'sg', 'kr-v1'];
const CROSS_BORDER = new Set(['hk', 'eu-emt', 'eu-emt-significant', 'kr-v1']);
const FOREIGN_NOTICE = '이 나라 발행사 보고서가 없어서 해외 보고서를 이 나라 규칙에 맞춰 본 결과이며, 이 나라 회사의 실제 공시가 아닙니다';
const KR_NOTICE = '한국 열은 제안값이며 확정된 규정이 아닙니다';
const CATEGORIES = [
  ['bank', '은행 예금'], ['repo', '하루짜리 담보 대출(레포)'],
  ['fund', '국채 펀드'], ['treasury', '국채'], ['other', '기타'],
];
const TYPE_NAMES = {cash:'현금',bank_deposit:'은행 예금',treasury_bill_93d:'93일 이하 국채',overnight_repo:'하루짜리 레포',government_mmf:'국채 펀드',overnight_reverse_repo:'하루짜리 역레포',approved_federal_asset:'감독기관 승인 연방정부 자산',tokenized_reserve:'토큰 형태 준비자산',cash_equivalent:'현금성 자산',government_bond_3m:'3개월 이하 국채',hqla:'고유동성 우량자산',bank_deposit_3m:'3개월 이내 은행 예금',low_risk_liquid_asset:'저위험 고유동성 자산',government_bond:'국채',other_designated:'그 밖의 지정 자산',examination:'검증 보고서',attestation:'확인 보고서',audit:'감사',quarterly_review:'분기 검토', 'reasonable assurance':'합리적 확신'};
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
function statusClass(status) { return status === STATUS.MET ? 'met' : status === STATUS.UNMET ? 'unmet' : status === STATUS.CAUTION ? 'caution' : 'none'; }
// 판정은 정사각형 색 칸으로만 보인다. 말은 옆에 보이거나 .sr에 있다
const sw = (cls) => `<i class="sw ${cls}" aria-hidden="true"></i>`;
function statusLegend(counts) {
  const items = [['met','충족'], ['caution','주의'], ['unmet','미충족'], ['none','판정 안 됨']];
  return `<span class="legend">${items.map(([cls,name]) => `<span>${sw(cls)}${name}${counts ? ` <b class="num">${counts[cls]}</b>` : ''}</span>`).join('')}</span>`;
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
  const limitTick = limit != null ? `<span class="tick limit num" style="bottom:${limit*100}%">${pct(limit,0)}</span><div class="reference-line" style="bottom:${limit*100}%"></div>` : '';
  const limitKey = limit != null ? `<span><i class="dash"></i>공시안 제안 은행 예금 ${pct(limit,0)}</span>` : '';
  return `<section class="chart-card panel" aria-labelledby="composition-title"><div class="panel-heading"><div><h2 id="composition-title">준비금 구성 비교</h2><p>발행사 보고서 ${reports.length}건의 준비금 구성입니다. 막대 맨 아래 칸이 은행 예금이고, 점선은 한국 제안 ${limit != null ? pct(limit,0) : ''}입니다.</p></div><span class="panel-index">막대 위 숫자는 은행 예금 비중</span></div><div class="plot-wrap"><div class="plot"><span class="tick num" style="bottom:100%">100%</span><span class="tick num" style="bottom:50%">50%</span><span class="tick num" style="bottom:0">0%</span><div class="bars">${bar}</div>${limitTick}</div>${axisLabels()}</div><div class="chart-foot"><span class="legend">${CATEGORIES.map(([key,name]) => `<span><i class="seg ${key}"></i>${name}</span>`).join('')}${limitKey}</span>${reports.some((x) => bankInfo(x).approx) ? '<p class="chart-note">* Circle은 은행 예금을 따로 적지 않아 기타 준비자산 비중으로 대신 계산했습니다. 국채가 섞인 달이 있습니다.</p>' : ''}</div></section>`;
}
function axisLabels() { return `<div class="axis-labels">${reports.map((r,i) => `<span class="${state.reportIndex === i ? 'chosen' : ''}">${esc(r.token)}<br>${Number(r.month.slice(5))}월</span>`).join('')}</div>`; }
const krProposal = (rid) => jurisdictions['kr-v1'].rules[rid].candidates.find((c) => c.id === 'proposal');
function daysRange() {
  const v = reports.map(days).filter((x) => x != null);
  return `보고서 ${v.length}건 모두 ${Math.min(...v)}~${Math.max(...v)}일`;
}
const GROUPS = [
  ['준비금 규모와 구성', ['R01','R05','R02','R03','R04','R06']],
  ['공개 방식', ['R07','R10','R11','R12']],
  ['검증과 서명', ['R08','R09','R15']],
  ['상환과 이자', ['R13','R14']],
];
const FOREIGN_IDS = ORDER.filter((id) => id !== 'kr-v1');
const SHORT = { us:'미국', 'eu-emt':'EU 일반', 'eu-emt-significant':'EU 중요', hk:'홍콩', sg:'싱가포르' };
const SUFFIX = { R01:'이상', R05:'이상', R03:'이하', R04:'이하', R07:'안', R10:'안', R13:'안' };
const ruleName = (rid) => esc(copy.규칙15개[rid]);
function criterion(v) { return `${fmt(v.rule, v.threshold)}${SUFFIX[v.rule] ? ` ${SUFFIX[v.rule]}` : ''}`; }
const noParen = (t) => String(t).replace(/\s*\(([^()]*)\)/g, ', $1');
function valueText(v) { return noParen(`이 보고서 ${fmt(v.rule, v.value)}${v.approx ? ' (근사)' : ''}${v.threshold != null ? `, 기준 ${criterion(v)}` : ''}`); }
const SHORT_NO = { [STATUS.NO_DATA]:'보고서에 값 없음', [STATUS.PENDING]:'기준 위임, 아직 미정', [STATUS.UNRESEARCHED]:'근거 조사 중', [STATUS.NOT_REGULATED]:'규정 없음' };
function krReason(v) {
  if (v.value != null) return valueText(v);
  if (SHORT_NO[v.status]) {
    const limit = v.rule === 'R05' && v.status === STATUS.PENDING ? krProposal('R05')?.threshold : null;
    return limit != null ? `${SHORT_NO[v.status]}. ${pct(limit,0)} 안은 후보값 바꾸기에서 선택` : SHORT_NO[v.status];
  }
  const def = resolveRuleDef(jurisdictions['kr-v1'], v.rule, state.candidates[v.rule]) || {};
  return def.label ? noParen(`기준 ${def.label}`) : '';
}
function krFindings(kr) {
  const line = (cls, name, list) => list.length ? `<p class="kr-find"><span class="kr-find-key ${cls}">${sw(cls)}${name}</span>${list.map((v) => `${ruleName(v.rule)}${v.value != null ? `: ${esc(valueText(v))}` : ''}`).join(' / ')}</p>` : '';
  return line('unmet', '미충족', kr.filter((v) => v.status === STATUS.UNMET)) + line('caution', '주의', kr.filter((v) => v.status === STATUS.CAUTION));
}
const COL_LABEL = { 'eu-emt':'EU<br>일반', 'eu-emt-significant':'EU<br>중요' };
function ruleList(kr, foreign) {
  const cell = (cls, who, rid, status) => { const t = `${who}, ${copy.규칙15개[rid]}: ${status}`; return `<i class="hm-c ${cls}" title="${esc(t)}"><span class="sr">${esc(t)}</span></i>`; };
  const row = (rid) => {
    const k = kr.find((x) => x.rule === rid), cls = statusClass(k.status), why = esc(krReason(k));
    const cells = cell(cls, '한국', rid, k.status) + FOREIGN_IDS.map((id) => { const x = foreign[id].find((v) => v.rule === rid); return cell(statusClass(x.status), SHORT[id], rid, x.status); }).join('');
    return `<div class="hm-row"><span class="hm-name">${ruleName(rid)} <small>${rid}</small></span><span class="hm-cells">${cells}</span><span class="hm-why">${cls === 'none' ? `<span class="hm-none">${why}</span>` : `<b class="hm-st ${cls}">${esc(k.status)}</b> ${why}`}</span></div>`;
  };
  const link = (id, text) => `<a href="#${id}" data-country="${id}">${text}</a>`;
  const head = (name) => `<div class="hm-row hm-head"><h3 class="hm-title">${name}</h3><span class="hm-cells">${link('kr-v1', '한국')}${FOREIGN_IDS.map((id) => link(id, COL_LABEL[id] || SHORT[id])).join('')}</span><span class="hm-why">한국 후보값 판정</span></div>`;
  // 한 줄 배치(좁은 화면)는 준비금, 공개, 검증, 상환 순. 넓은 화면은 왼쪽 열 0, 3번째 블록, 오른쪽 열 1, 2번째 블록
  const block = ([name, ids], i) => `<div class="hm-block" style="--o:${i}">${head(name)}${ids.map(row).join('')}</div>`;
  const col = (idx) => `<div class="hm-col">${idx.map((i) => block(GROUPS[i], i)).join('')}</div>`;
  return `<section class="rl-section panel" aria-labelledby="rl-title"><div class="section-head"><div><h2 id="rl-title">규칙별 판정</h2><p>한국 후보값으로 먼저 판정하고, 같은 보고서를 해외 5곳의 규칙에도 맞춰 봅니다. 나라 이름을 누르면 상세 화면으로 갑니다.</p></div>${statusLegend()}</div><div class="hm">${col([0, 3])}${col([1, 2])}</div></section>`;
}
function home() {
  const r = reports[state.reportIndex], cash = bankInfo(r), own = r.attestation?.firm || '이미지 서명, 이름 확인 필요';
  const kr = judged('kr-v1'), foreign = Object.fromEntries(FOREIGN_IDS.map((id) => [id, judged(id)]));
  const bankLim = krProposal('R05')?.threshold, dayLim = krProposal('R10')?.deadline_days;
  const stat = (name, valueHtml, note, cls = '') => `<div class="stat ${cls}"><span class="stat-label">${name}</span><strong class="stat-value num">${valueHtml}</strong><span class="stat-note">${note}</span></div>`;
  return `<div class="home"><div class="hero"><div class="home-head"><div><h1>원화 스테이블코인 준비금 공시 판정</h1><p class="lead">발행사가 공개한 준비금 검증 보고서 한 건을 한국 후보 기준 ${RULE_IDS.length}개로 점검하고, 같은 보고서를 해외 기준에도 맞춰 봅니다.</p><ol class="steps"><li><b class="num">1</b>위에서 판정할 보고서 고르기</li><li><b class="num">2</b>한국 기준 ${RULE_IDS.length}개 결과 보기</li><li><b class="num">3</b>해외 기준과 비교</li></ol><p class="report-line">판정 보고서 ${esc(label(r))} / 기준일 ${esc(r.as_of)} / 검증인 ${esc(own)}</p></div><span class="head-index">보고서 ${state.reportIndex+1} / ${reports.length}</span></div>
    <div class="hero-globe"></div><div class="hero-main">
      <section class="stats panel" aria-label="선택 보고서의 주요 수치">${stat(`은행 예금 비중${cash.approx ? ' (대신 계산)' : ''}`, metricPct(cash.ratio), `한국 규칙 ${ruleName('R05')}, 제안 ${bankLim != null ? pct(bankLim,0) : '자료 없음'} 이상${cash.approx ? '<br>기타 준비자산으로 대신 계산, 국채가 섞인 달이 있음' : ''}`, 'stat-main')}${stat('서명까지 걸린 날', days(r) == null ? '자료 없음' : `${days(r)}<small>일</small>`, `한국 규칙 ${ruleName('R10')}, 제안 ${dayLim ?? '자료 없음'}일 안<br>${daysRange()}`)}${stat('커버리지', metricPct(r.coverage ?? (r.fair_value && r.circulation ? r.fair_value/r.circulation : null)), `한국 규칙 ${ruleName('R01')}<br>준비금 공정가치 / 발행잔액`)}</section>
      <section class="result panel" aria-labelledby="result-title"><div class="section-head"><div><h2 id="result-title">한국 기준 판정 결과</h2><p>한국 후보값은 확정된 규정이 아닙니다</p></div><a class="link-more" href="#kr-v1" data-country="kr-v1">후보값 바꾸기 →</a></div><div class="result-body">${krSummary(kr)}<div class="kr-finds">${krFindings(kr)}</div></div></section>
    </div></div>
    ${ruleList(kr, foreign)}
    <div class="home-sec"><h2>한국 기준값과 해외 기준값</h2><p>한국 제안값은 해외 규칙과 국회 법안을 살펴 정했습니다. 표는 규칙마다 한국과 해외의 값을 나란히 보여 주고, 아래 그래프는 숫자 규칙 4개에서 한국 제안값이 어디에 놓이는지 보여 줍니다.</p></div>${ruleTable(jurisdictions, copy)}${ruleDots(jurisdictions, copy)}${chartComposition()}<div class="disclosure"><strong>${KR_NOTICE}</strong><br>홍콩, EU 일반, EU 중요, 한국 판정: ${FOREIGN_NOTICE}</div></div>`;
}
function rulesPane(id) {
  const values = judged(id), active = values.filter((v) => [STATUS.MET,STATUS.UNMET,STATUS.CAUTION].includes(v.status));
  const inactive = values.filter((v) => ![STATUS.MET,STATUS.UNMET,STATUS.CAUTION].includes(v.status));
  const shown = [...active,...(state.showAll ? inactive : [])];
  const kr = id === 'kr-v1' ? candidatePanel() : '';
  return kr + `<div class="pane-intro"><strong>판정 보고서: ${esc(label(reports[state.reportIndex]))}</strong> / 충족 ${active.filter((v) => v.status === STATUS.MET).length} / 미충족 ${active.filter((v) => v.status === STATUS.UNMET).length}<br>판정이 나온 규칙을 먼저 표시합니다. ${esc(id === 'kr-v1' ? KR_NOTICE : '')}</div>${shown.map((v) => ruleItem(id,v)).join('')}${inactive.length ? `<button class="fold-button" data-action="toggle-rules" type="button">${state.showAll ? `나머지 ${inactive.length}개 접기 ↑` : `판정이 나오지 않은 ${inactive.length}개 보기 ↓`}</button>` : ''}`;
}
function candOpts(rid, name) {
  const e = jurisdictions['kr-v1'].rules[rid], cur = state.candidates[rid] || e.default_candidate || e.candidates[0].id;
  return `<span class="cand-opts">${e.candidates.map((c) => `<label class="${c.id === cur ? 'on' : ''}"><input type="radio" name="${name}-${rid}" data-candidate="${rid}" value="${esc(c.id)}" ${c.id === cur ? 'checked' : ''}>${esc(c.label)}</label>`).join('')}</span>`;
}
function candidatePanel() {
  const rules = jurisdictions['kr-v1'].rules;
  const rows = RULE_IDS.filter((rid) => (rules[rid]?.candidates || []).length > 1).map((rid) => `<div class="cand-row"><span class="cand-rule"><b>${rid}</b>${esc(copy.규칙15개[rid])}</span>${candOpts(rid,'kc')}</div>`).join('');
  return `<section class="cand-panel"><div class="cand-head"><strong>한국 후보값</strong><span>후보를 바꾸면 아래 판정이 바로 바뀝니다. ${KR_NOTICE}</span></div>${rows}</section>`;
}
function ruleItem(id,v) {
  const open = state.openRule === v.rule;
  return `<article class="rule-item ${open ? 'open' : ''}"><button type="button" data-rule="${v.rule}" class="rule-heading" aria-expanded="${open}" aria-controls="body-${v.rule}"><span class="rule-code">${v.rule}</span><span class="rule-title">${esc(copy.규칙15개[v.rule])}</span><span class="rule-vals num">${v.value != null ? `${esc(fmt(v.rule,v.value))}${v.approx ? '*' : ''}` : ''}${v.threshold != null ? `<small>기준 ${esc(fmt(v.rule,v.threshold))}</small>` : ''}</span><span class="status ${statusClass(v.status)}">${sw(statusClass(v.status))}${esc(v.status)}</span><span class="chevron" aria-hidden="true"></span></button>${open ? `<div class="rule-body" id="body-${v.rule}">${ruleBody(id,v)}</div>` : ''}</article>`;
}
const NO_VALUE = { [STATUS.NO_DATA]:'보고서에 비교할 값이 없습니다.', [STATUS.NOT_REGULATED]:'이 항목에는 규정이 없습니다.', [STATUS.PENDING]:'세부 기준이 위임되어 아직 정해지지 않았습니다.', [STATUS.UNRESEARCHED]:'근거 조사가 끝나지 않았습니다.' };
function ruleBody(id,v) {
  const entry = jurisdictions[id].rules[v.rule] || {}, def = resolveRuleDef(jurisdictions[id],v.rule,id === 'kr-v1' ? state.candidates[v.rule] : undefined) || {};
  const link = safeLink(v.url);
  const explanation = NO_VALUE[v.status] || '';
  const radio = id === 'kr-v1' && entry.candidates?.length ? `<div class="body-cand"><span class="key">한국 후보값</span>${candOpts(v.rule,'candidate')}</div>` : '';
  return `<dl class="value-pair"><div><dt>보고서 값</dt><dd class="num">${esc(fmt(v.rule,v.value))}${v.approx ? ' (근사)' : ''}</dd></div><div><dt>기준</dt><dd class="num">${esc(fmt(v.rule,v.threshold,'기준 없음'))}</dd></div></dl>${explanation ? `<p>${esc(explanation)}</p>` : ''}<p><span class="key">요건</span>${esc(def.requirement || '자료 없음')}</p><p><span class="key">근거 조문</span>${esc(v.article || '기재 없음')}</p>${v.approx ? '<p>기타 준비자산으로 대신 계산, 국채가 섞인 달이 있음</p>' : ''}${link ? `<p><a href="${esc(link)}" target="_blank" rel="noopener noreferrer">원문 링크 열기 ↗</a></p>` : '<p><span class="key">원문 링크</span>자료 없음</p>'}${radio}`;
}
function reportItem(i) {
  const r = reports[i], b = bankInfo(r), current = i === state.reportIndex;
  return `<button type="button" class="report-item ${current ? 'current' : ''}" data-report="${i}" aria-pressed="${current}"><span class="report-item-top"><strong>${esc(label(r))}</strong>${current ? '<em>판정에 사용 중</em>' : '<em>이 보고서로 판정 →</em>'}</span><p class="issuer">${esc(r.issuer)}</p><dl class="report-fields"><div><dt>기준일</dt><dd class="num">${esc(date(r.as_of))}</dd></div><div><dt>커버리지</dt><dd class="num">${pct(r.coverage ?? (r.fair_value/r.circulation))}</dd></div><div><dt>서명일</dt><dd class="num">${esc(date(r.attestation?.signed))}</dd></div><div><dt>검증인</dt><dd>${esc(r.attestation?.firm || '이미지 서명, 이름 확인 필요')}</dd></div><div><dt>서명까지 걸린 날</dt><dd class="num">${days(r) == null ? '자료 없음' : `${days(r)}일`}</dd></div><div><dt>은행 예금 비중</dt><dd class="num">${pct(b.ratio)}${b.approx ? ' (기타 대신 계산)' : ''}</dd></div></dl>${b.approx ? '<p class="report-note">기타 준비자산으로 대신 계산, 국채가 섞인 달이 있음</p>' : ''}</button>`;
}
function weeklyPane() {
  const max = Math.max(...weekly.주간.map((row) => row.준비금));
  return `<div class="weekly"><p class="weekly-warning">회계법인 확인이 없는 회사 자체 공시</p><p>${esc(weekly.발행사)}의 ${esc(weekly.코인)} 주간 명세 ${weekly.주간.length}주치. ${esc(weekly.기준)}. 단위: ${esc(weekly.단위)}. ${esc(weekly.준비금구성)}.</p><table><thead><tr><th scope="col">기준일</th><th scope="col">유통량</th><th scope="col">준비금</th><th scope="col">규모 비교</th></tr></thead><tbody>${weekly.주간.map((row) => `<tr><td>${esc(row.기준일)}</td><td>${count(row.유통량)}</td><td>${count(row.준비금)}</td><td><div class="weekly-bars" role="img" aria-label="${esc(row.기준일)} 준비금 ${row.준비금}, 유통량 ${row.유통량} ${esc(weekly.단위)}"><i style="width:${row.준비금/max*100}%"></i><b style="width:${row.유통량/max*100}%"></b></div></td></tr>`).join('')}</tbody></table><div class="legend"><span><i class="bar"></i>준비금</span><span><i class="bar ink"></i>유통량</span></div><p>${esc(weekly.주석)}. 이 값은 판정 엔진에 넣지 않습니다.</p></div>`;
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
  const links = [...new Map(Object.values(jur.rules).filter((d) => safeLink(d.url)).map((d) => [safeLink(d.url), d.article || d.requirement])).entries()].slice(0,5);
  const reportCount = ownIndices(id).length;
  const notes = [
    CROSS_BORDER.has(id) ? FOREIGN_NOTICE : !ownIndices(id).includes(state.reportIndex) ? '선택한 보고서는 이 나라 발행사의 보고서가 아닙니다.' : '',
    id === 'kr-v1' ? KR_NOTICE : '',
  ].filter(Boolean);
  return `<div class="detail"><div class="detail-head"><a href="#" class="back-link">← 개요로 돌아가기</a><span class="context">선택 보고서 ${esc(label(r))} / 기준일 ${esc(r.as_of)}</span></div><div class="detail-layout"><section class="identity-card panel" aria-label="${esc(info.이름)} 개요"><div class="globe"></div><div class="identity-top"><div class="identity-name"><h1>${esc(info.이름)}</h1><div class="legal">법적 상태<strong>${esc(jur.legal_status)}</strong></div></div></div><div><div class="score"><strong class="num">${met}<small>/ ${done}</small></strong><span>판정된 규칙 ${done}개 중 충족</span></div><div class="rule-grid" role="img" aria-label="규칙 ${RULE_IDS.length}개 판정: 충족 ${met}, 주의 ${caution}, 미충족 ${unmet}, 판정 안 됨 ${none}">${results.map((v) => `<span class="rg ${statusClass(v.status)}" title="${v.rule} ${esc(copy.규칙15개[v.rule])}: ${esc(v.status)}"><b>${v.rule}</b></span>`).join('')}</div>${statusLegend({met,caution,unmet,none})}</div><div><div class="small-head">규정 설명</div><p>${esc(info.설명)}</p></div>${notes.length ? `<div class="notes">${notes.map((n) => `<div class="comparison-note">${n}</div>`).join('')}</div>` : ''}${links.length ? `<div><div class="small-head">규제 원문</div><ul class="source-links">${links.map(([u,t]) => `<li><a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(t)}</a></li>`).join('')}</ul></div>` : ''}<div class="source-date">규칙 자료 기준일 ${esc(jur.as_of)} / 판정 보고서 기준일 ${esc(r.as_of)}</div></section><section class="detail-right panel" aria-label="${esc(info.이름)} 판정과 보고서"><div class="detail-tabs" role="tablist" aria-label="상세 내용"><button type="button" role="tab" data-tab="rules" aria-selected="${state.tab === 'rules'}" tabindex="0">규칙 ${RULE_IDS.length}개</button><button type="button" role="tab" data-tab="reports" aria-selected="${state.tab === 'reports'}" tabindex="0">이 나라 보고서${id === 'hk' ? ` / 주간 명세 ${weekly.주간.length}주` : ` ${reportCount}건`}</button></div><div role="tabpanel">${state.tab === 'rules' ? rulesPane(id) : reportsPane(id)}</div></section></div><nav class="country-nav" aria-label="나라 이동"><a href="#" >전체 개요</a>${ORDER.map((key) => `<a href="#${key}" class="${id === key ? 'active' : ''}" ${id === key ? 'aria-current="page"' : ''}>${esc(copy.나라[key].이름)}</a>`).join('')}</nav></div>`;
}
// 점 그래프는 칸 폭에 1:1로 맞춘다. 그린 뒤 칸 폭을 재서 폭이 다르면 그 폭으로 다시 그린다
function fitDots() {
  const box = $('#app .rv-dots'), fig = box?.firstElementChild;
  if (!fig) return;
  const w = Math.max(280, Math.floor(fig.clientWidth));
  if (w !== Number(box.dataset.w)) { box.dataset.w = w; box.innerHTML = ruleDotsPlots(jurisdictions, copy, w); }
}
function render() {
  if (!reports) return;
  $('#app').innerHTML = state.jurisdiction ? detail() : home();
  fitDots();
  const g = $('#app .globe'); if (g && state.jurisdiction) mountGlobe(g, state.jurisdiction);
  const hg = $('#app .hero-globe'); if (hg && !state.jurisdiction) mountHeroGlobe(hg);
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
window.addEventListener('resize',fitDots);
init();
