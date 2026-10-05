import { RULE_IDS, STATUS, evaluateReport, resolveRuleDef, calendarDaysBetween } from './engine.js';
import { krSummary, ruleTable, ruleDots, ruleDotsPlots } from './charts.js';
import { mountGlobe, mountHeroGlobe } from './globe.js';
import { renderSidebar, bindSidebar } from './sidebar.js';
import { flowSvg, flowTotals, bindFlow } from './flow.js';
import { isoFlowSvg } from './iso.js';

const ORDER = ['us', 'eu-emt', 'eu-emt-significant', 'hk', 'sg', 'jp', 'kr-v1'];
const FOREIGN_NOTICE = '이 나라 발행사의 보고서는 아직 자료에 없어서, 다른 나라 발행사의 보고서를 이 나라 규칙에 대 본 결과입니다. 이 나라 회사의 실제 공시가 아닙니다';
const KR_NOTICE = '한국 열은 제안값이며 확정된 규정이 아닙니다';
const JP_NOTICE = '일본 열은 신탁형(특정신탁수익권) 규칙입니다. 자금이동업자형은 규칙을 눌렀을 때 보조로 보입니다. 규정 없음은 읽은 원문 범위에서 찾지 못했다는 뜻입니다';
const CATEGORIES = [
  ['bank', '은행 예금'], ['repo', '하루짜리 담보 대출(레포)'],
  ['fund', '국채 펀드'], ['treasury', '국채'], ['other', '기타'],
];
const TYPE_NAMES = {cash:'현금',bank_deposit:'은행 예금',treasury_bill_93d:'93일 이하 국채',overnight_repo:'하루짜리 레포',government_mmf:'국채 펀드',overnight_reverse_repo:'하루짜리 역레포',approved_federal_asset:'감독기관 승인 연방정부 자산',tokenized_reserve:'토큰 형태 준비자산',cash_equivalent:'현금성 자산',government_bond_3m:'3개월 이하 국채',hqla:'고유동성 우량자산',bank_deposit_3m:'3개월 이내 은행 예금',low_risk_liquid_asset:'저위험 고유동성 자산',government_bond:'국채',other_designated:'그 밖의 지정 자산',examination:'검증 보고서',attestation:'확인 보고서',audit:'감사',quarterly_review:'분기 검토', 'reasonable assurance':'합리적 확신',demand_deposit_same_currency:'같은 통화 요구불 예금',term_deposit_principal_protected_cancellable_anytime:'원금 보전, 수시 해약 정기예금',jgb_remaining_le_3m_jpy_only:'3개월 이내 엔화 국채',foreign_bond_remaining_le_3m_same_currency:'3개월 이내 같은 통화 외국 채권'};
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
const state = { reportIndex: 0, jurisdiction: null, rules: null, tab: 'rules', openRule: null, showAll: false, candidates: {} };
const grpOpen = {}; // 토큰 묶음(details)을 사용자가 펼치고 접은 상태. 다시 그려도 유지
let reports, jurisdictions, copy, weekly, excluded = [], series = {};

// 보고서 이름은 '{발행사} {토큰} {YYYY}년 {M}월'. 토큰이 이미 보이는 묶음 안에서는 ym만 쓴다
function coin(report) { return `${report.issuer_short} ${report.token}`; }
function ym(report) { return `${report.month.slice(0,4)}년 ${Number(report.month.slice(5))}월`; }
function label(report) { return `${coin(report)} ${ym(report)}`; }
// 이 나라 발행사의 보고서 번호들(보고서의 home에 나라가 있는 것). 비면 다른 나라 보고서를 대 본 화면이다
function ownIndices(jurisdiction) { return reports.flatMap((r, i) => r.home?.includes(jurisdiction) ? [i] : []); }
// 토큰별 묶음 [[토큰, [보고서 번호...]], ...]. 토큰은 자료에 나온 차례
function byToken(indices) {
  const groups = new Map();
  indices.forEach((i) => groups.set(reports[i].token, [...(groups.get(reports[i].token) || []), i]));
  return [...groups];
}
// 이 나라 발행사의 보고서가 없는 나라 이름들(개요 맨 아래 안내)
function foreignNames() { return ORDER.filter((id) => !ownIndices(id).length).map((id) => SHORT[id] || '한국').join(', '); }
function judged(jurisdiction) {
  return evaluateReport(reports[state.reportIndex], jurisdictions[jurisdiction], jurisdiction === 'kr-v1' ? state.candidates : {});
}
function days(report) { return calendarDaysBetween(report.as_of, report.attestation?.signed); }
function bankInfo(report) {
  const c = report.components || {};
  if (!report.fair_value) return { ratio:null, approx:false };
  if (c.cash != null) return { ratio:c.cash / report.fair_value, approx:false };
  // 원문이 은행 예금을 나누지 않은 보고서(USDG 옛 형식)는 기타로 근사하지 않고 자료 없음. engine.js와 같은 규칙
  if (c.other != null && report.flags?.cash_is_bank_deposit !== false) return { ratio:c.other / report.fair_value, approx:true };
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
// R11, R12, R15는 '공개했는가'를 묻는 규칙이라 false는 '공개 안 함'(판정은 미충족). 값이 없는 '보고서에 없음'과 다르다
const DISCLOSE = ['R11','R12','R15'];
const KIND_NAMES = { cash:'현금', bank_deposit:'은행 예금', term_deposit:'정기예금', treasury_bill:'단기 국채', treasury_note:'중기 국채', non_us_government_bill:'외국 정부 단기채', government_mmf:'정부 MMF', reverse_repo_overnight:'하루짜리 역레포', reverse_repo_term:'기간물 역레포', cash_equivalents_unsplit:'현금과 현금성 자산 묶음', corporate_bond:'회사채', precious_metal:'귀금속', bitcoin:'비트코인', other_investment:'기타 투자', secured_loan:'담보 대출', public_equity:'상장 주식' };
const VERDICT_TEXT = { allowed:['met','허용'], not_allowed:['unmet','허용 밖'], unclear:['caution','해석 필요'] };
function kindSummary(list) {
  return ['allowed','unclear','not_allowed'].flatMap((k) => { const n = list.filter((x) => x.verdict === k).length; return n ? [`${VERDICT_TEXT[k][1]} ${n}종`] : []; }).join(', ');
}
function fmt(rule, value, empty='자료 없음') {
  if (value == null) return empty;
  if (Array.isArray(value)) return !value.length ? '해당 없음' : typeof value[0] === 'object' ? kindSummary(value) : value.map((v) => TYPE_NAMES[v] || v).join(', ');
  if (typeof value === 'boolean') return DISCLOSE.includes(rule) ? (value ? '공개함' : '공개 안 함') : value ? '예' : '아니오';
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
  state.rules = raw === 'rules' ? (RULE_IDS.includes(tab) ? tab : 'all') : null; // #rules, #rules/R03: 규칙 설명 페이지
  state.openRule = null;
  state.showAll = false;
  render();
  if (state.rules) {
    const at = state.rules !== 'all' && document.getElementById(`rule-${state.rules}`);
    const top = at?.previousElementSibling?.matches('.rs-gh') ? at.parentElement : at; // 묶음 첫 항목이면 묶음 제목부터 보이게
    if (top) top.scrollIntoView({ block: 'start', behavior: 'instant' }); else window.scrollTo({ top: 0, behavior: 'instant' });
  }
}
function selectReport(index) {
  if (!Number.isInteger(index) || index < 0 || index >= reports.length) return;
  if (reports[index].token !== reports[state.reportIndex].token) grpOpen[`r:${reports[index].token}`] = true; // 다른 토큰 것을 고르면 그 묶음을 펼침. 나머지는 사용자가 둔 대로
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
// 보고서에 없음, 해당 없음, 규정 없음, 위임 예정, 조사 미완료는 모두 none(회색)
function statusClass(status) { return status === STATUS.MET ? 'met' : status === STATUS.UNMET ? 'unmet' : status === STATUS.CAUTION ? 'caution' : 'none'; }
// 판정은 정사각형 색 칸으로만 보인다. 말은 옆에 보이거나 .sr에 있다
const sw = (cls) => `<i class="sw ${cls}" aria-hidden="true"></i>`;
// 공개 여부 규칙이 false이면 '공개 안 함'. 판정은 미충족이다
const notDisclosed = (v) => DISCLOSE.includes(v.rule) && v.value === false;
const statusLabel = (v) => notDisclosed(v) ? '공개 안 함' : v.status;
const statusTitle = (v) => notDisclosed(v) ? `${v.status}, 보고서가 공개하지 않음` : v.status;
function statusLegend(counts) {
  const items = [['met','충족'], ['caution','주의'], ['unmet','미충족'], ['none', counts ? '판정 안 됨' : '판정 안 됨(보고서에 없음, 해당 없음, 규정 없음, 위임 예정, 조사 미완료)']];
  return `<span class="legend">${items.map(([cls,name]) => `<span>${sw(cls)}${name}${counts ? ` <b class="num">${counts[cls]}</b>` : ''}</span>`).join('')}</span>`;
}
// 준비금 보고서 비교: 줄은 코인, 칸은 달. 칸에 은행 예금 비중과 서명까지 걸린 날, 줄 머리에 고른 달의 준비금 구성
function chartComposition() {
  const limit = krProposal('R05')?.threshold, dayLim = krProposal('R10')?.deadline_days;
  const billDays = jurisdictions['kr-v1'].rules.R10.candidates.find((c) => c.id === 'bill')?.deadline_days;
  const inBill = reports.filter((r) => days(r) != null && billDays != null && days(r) <= billDays).length;
  const months = [...new Set(reports.map((r) => r.month))].sort(), pick = reports[state.reportIndex].month;
  const at = (tok, m) => reports.findIndex((r) => r.token === tok && r.month === m);
  const short = (ratio) => { const v = ratio * 100; return v >= 99.95 ? String(Math.round(v)) : v.toFixed(1); }; // 44칸이 한 줄에 들어가도록 100% 이상은 정수로
  // 보고서가 없는 칸은 이유를 구별한다: 출시 전, 원문 합계 오류로 뺌, 아직 게시 전, 분기 공시라 없는 달
  const quarterly = new Set(reports.filter((x) => x.disclosure_cadence === 'quarterly').map((x) => x.token));
  const emptyCell = (tok, m) => {
    const se = series[tok], ex = excluded.find((e) => e.token === tok && e.month === m), name = coin(reports.find((x) => x.token === tok)), when = `${m.slice(0,4)}년 ${Number(m.slice(5))}월`;
    const [kind, mark, why] = se && m < se.first_month ? ['pre', '', '출시 전']
      : ex ? ['excl', '×', `원문 합계 오류로 뺌. ${ex.reason}`]
      : se?.not_yet_published?.includes(m) ? ['wait', '…', '아직 게시 전']
      : ['qtr', '–', quarterly.has(tok) ? '분기마다 공시해서 이 달은 보고서 없음' : '이 달 보고서 없음'];
    const t = `${name} ${when}: ${why}`;
    return `<span class="mx-c empty ${kind}" role="img" aria-label="${esc(t)}" title="${esc(t)}">${mark}</span>`;
  };
  const cell = (i, tok, m) => {
    if (i < 0) return emptyCell(tok, m);
    const r = reports[i], b = bankInfo(r), d = days(r), sel = state.reportIndex === i, nb = r.flags?.cash_is_bank_deposit === false;
    const tone = b.ratio == null || limit == null ? '' : b.ratio >= limit ? ' hi' : ' lo';
    const t = `${label(r)}: ${nb ? '원문이 은행 예금을 따로 적지 않아 구분 안 됨' : `은행 예금 ${pct(b.ratio,1)}${b.approx ? ' (대신 계산)' : ''}`}, 서명까지 ${d ?? '자료 없음'}일`;
    return `<button type="button" class="mx-c${tone}${nb ? ' nb' : ''}${sel ? ' selected' : ''}" data-report="${i}" aria-pressed="${sel}" aria-label="${esc(t)}" title="${esc(t)}"><b class="num">${b.ratio == null ? '–' : short(b.ratio)}${b.approx ? '<sup>*</sup>' : ''}</b><small class="num${d != null && dayLim != null && d > dayLim ? ' over' : ''}">${d ?? '–'}일</small></button>`;
  };
  const rows = [...new Set(reports.map((r) => r.token))].map((tok) => {
    // 줄 머리 막대는 고른 달의 구성. 그 달 보고서가 없는 코인(분기 보고서 등)은 앞의 가장 가까운 달 것을 쓰고 달을 적는다
    const mine = reports.flatMap((x, i) => x.token === tok ? [i] : []), r = reports[mine.findLast((i) => reports[i].month <= pick) ?? mine[0]];
    const slices = mix(r).filter((x) => x.ratio > 0);
    const desc = `${ym(r)} 준비금 구성: ${slices.map((x) => `${CATEGORIES.find(([k]) => k === x.type)[1]} ${pct(x.ratio,1)}`).join(', ')}`;
    return `<div class="mx-head"><strong>${esc(coin(r))}</strong><span class="mx-bar" role="img" aria-label="${esc(desc)}" title="${esc(desc)}">${slices.map((x) => `<i class="seg ${x.type}" style="width:${(x.ratio*100).toFixed(2)}%"></i>`).join('')}</span>${r.month === pick ? '' : `<small>${esc(ym(r))} 기준</small>`}</div>${months.map((m) => cell(at(tok, m), tok, m)).join('')}`;
  }).join('');
  // 달 축: 44개월을 다 쓰면 겹치므로 1월 칸에 연도만 쓰고, 고른 달만 'N월'로 표시. 나머지 칸은 비움
  const axis = (m) => m.endsWith('-01') ? `<span class="mx-m yr${m === pick ? ' chosen' : ''}">${m.slice(0,4)}</span>` : `<span class="mx-m${m === pick ? ' chosen' : ''}">${m === pick ? `${Number(m.slice(5))}월` : ''}</span>`;
  const head = `<span class="mx-m mx-corner">준비금 구성(${ym(reports[state.reportIndex])})</span>${months.map(axis).join('')}`;
  const lim = limit != null ? pct(limit,0) : '자료 없음';
  return `<section class="chart-card panel" aria-labelledby="composition-title"><div class="panel-heading"><div><h2 id="composition-title">준비금 보고서 ${reports.length}건 비교</h2><p>줄은 코인, 칸은 달입니다. 칸의 큰 숫자는 은행 예금 비중(%)이고, 한국 제안 ${lim} 이상이면 파랑, 미만이면 빨강입니다. 작은 숫자는 기준일부터 검증인 서명까지 걸린 날이고, 제안 ${dayLim ?? '자료 없음'}일을 넘으면 빨강입니다. 의원안 ${billDays ?? '자료 없음'}일 안에 서명한 보고서는 ${inBill ? `${inBill}건입니다` : '없습니다'}. 칸을 누르면 그 보고서로 판정합니다.</p></div></div><div class="mx-wrap"><div class="mx" style="--n:${months.length}">${head}${rows}</div></div><div class="chart-foot"><span class="legend"><span><i class="tint hi"></i>은행 예금 ${lim} 이상</span><span><i class="tint lo"></i>${lim} 미만</span><span><i class="tint nb"></i>은행 예금 구분 안 됨</span>${CATEGORIES.map(([key,name]) => `<span><i class="seg ${key}"></i>${name}</span>`).join('')}</span><span class="legend mx-key"><span><i class="mk pre"></i>출시 전</span><span><i class="mk excl">×</i>원문 합계 오류로 뺌</span><span><i class="mk wait">…</i>아직 게시 전</span><span><i class="mk qtr">–</i>분기 공시라 없는 달</span></span>${reports.some((x) => bankInfo(x).approx) ? '<p class="chart-note">* Circle은 은행 예금을 따로 적지 않아 기타 준비자산 비중으로 대신 계산했습니다. 국채가 섞인 달이 있습니다.</p>' : ''}</div></section>`;
}
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
const ruleHelp = (rid) => copy.규칙설명?.[rid] || '';
const SHORT = { us:'미국', 'eu-emt':'EU 일반', 'eu-emt-significant':'EU 중요', hk:'홍콩', sg:'싱가포르', jp:'일본' };
const SUFFIX = { R01:'이상', R05:'이상', R03:'이하', R04:'이하', R07:'안', R10:'안', R13:'안' };
const ruleName = (rid) => esc(copy.규칙15개[rid]);
function criterion(v) { return `${fmt(v.rule, v.threshold)}${SUFFIX[v.rule] ? ` ${SUFFIX[v.rule]}` : ''}`; }
const noParen = (t) => String(t).replace(/\s*\(([^()]*)\)/g, ', $1');
function valueText(v) {
  if (typeof v.value === 'boolean' && DISCLOSE.includes(v.rule)) return `이 보고서는 ${v.value ? '공개함' : '공개하지 않음'}`;
  return noParen(`이 보고서 ${fmt(v.rule, v.value)}${v.approx ? ' (근사)' : ''}${v.threshold != null ? `, 기준 ${criterion(v)}` : ''}`);
}
const SHORT_NO = { [STATUS.NO_DATA]:'보고서에 이 항목 없음', [STATUS.NOT_APPLICABLE]:'해당 자산을 들고 있지 않아 해당 없음', [STATUS.PENDING]:'기준 위임, 아직 미정', [STATUS.UNRESEARCHED]:'근거 조사 중', [STATUS.NOT_REGULATED]:'규정 없음' };
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
  const cell = (cls, who, rid, v) => { const t = `${who}, ${copy.규칙15개[rid]}: ${statusLabel(v)}${statusLabel(v) !== v.status ? `, 판정 ${v.status}` : ''}`; return `<i class="hm-c ${cls}" title="${esc(t)}"><span class="sr">${esc(t)}</span></i>`; };
  const row = (rid) => {
    const k = kr.find((x) => x.rule === rid), cls = statusClass(k.status), why = esc(krReason(k));
    const cells = cell(cls, '한국', rid, k) + FOREIGN_IDS.map((id) => { const x = foreign[id].find((v) => v.rule === rid); return cell(statusClass(x.status), SHORT[id], rid, x); }).join('');
    return `<div class="hm-rule" data-hm="${rid}"><div class="hm-row"><span class="hm-name" title="${esc(ruleHelp(rid))}">${ruleName(rid)} <small>${rid}</small></span><span class="hm-cells">${cells}</span><span class="hm-why">${cls === 'none' ? `<span class="hm-none">${why}</span>` : `<b class="hm-st ${cls}">${esc(k.status)}</b> ${why}`}</span></div></div>`;
  };
  const link = (id, text) => `<a href="#${id}" data-country="${id}">${text}</a>`;
  const head = (name) => `<div class="hm-row hm-head"><h3 class="hm-title">${name}</h3><span class="hm-cells">${link('kr-v1', '한국')}${FOREIGN_IDS.map((id) => link(id, COL_LABEL[id] || SHORT[id])).join('')}</span><span class="hm-why">한국 후보값 판정</span></div>`;
  // 한 줄 배치(좁은 화면)는 준비금, 공개, 검증, 상환 순. 넓은 화면은 왼쪽 열 0, 3번째 블록, 오른쪽 열 1, 2번째 블록
  const block = ([name, ids], i) => `<div class="hm-block" style="--o:${i}">${head(name)}${ids.map(row).join('')}</div>`;
  const col = (idx) => `<div class="hm-col">${idx.map((i) => block(GROUPS[i], i)).join('')}</div>`;
  return `<section class="rl-section panel" aria-labelledby="rl-title"><div class="section-head"><div><h2 id="rl-title">규칙별 판정</h2><p>한국 후보값으로 먼저 판정하고, 같은 보고서를 해외 ${FOREIGN_IDS.length}곳의 규칙에도 맞춰 봅니다. 나라 이름을 누르면 상세 화면으로 갑니다.</p><p class="rl-note">EU 일반과 EU 중요는 나라가 아니라 EU 규칙(MiCA)의 토큰 단계입니다. EU 중요는 유럽은행감독청이 이용자와 발행 규모가 커서 대형으로 지정한 토큰이고, 은행 예금 60% 이상, 6개월마다 감사처럼 규칙이 더 셉니다.</p></div>${statusLegend()}</div><div class="hm">${col([0, 3])}${col([1, 2])}</div></section>`;
}
// ---- 판정 흐름: 7개 나라 x 규칙 15개 = 판정 105건을 나라, 판정 결과, 규칙 세 축으로 이음 ----
const FLOW_RULES = GROUPS.flatMap(([, ids]) => ids);
function flowSection() {
  const rows = ['kr-v1', ...FOREIGN_IDS].flatMap((id) => {
    const by = Object.fromEntries(judged(id).map((v) => [v.rule, v]));
    return FLOW_RULES.map((rule) => ({ country: id, countryName: id === 'kr-v1' ? '한국' : SHORT[id], rule, ruleName: copy.규칙15개[rule], status: statusClass(by[rule].status) }));
  });
  const opt = { focus: 'kr-v1' };
  lastFlow = { rows, opt };
  return `<section class="rl-section panel flow-section" aria-labelledby="flow-title"><div class="section-head"><div><h2 id="flow-title">판정 흐름</h2><p>선 한 줄이 판정 하나입니다. 나라에서 판정 결과를 거쳐 규칙으로 이어집니다. 나라, 판정 결과, 규칙 이름에 올리면 그 판정만 진하게 보입니다.</p></div>${statusLegend()}</div><div class="flow-scroll">${flowSvg(rows, { ...opt, width: flowW })}</div>${flowTotals(rows, opt)}</section>`;
}
// ---- 개요 지구본 위 유리 카드: 선택 보고서의 판정 수를 나라 옆에 보여 줌 ----
const tally = (id) => { const n = { met:0, caution:0, unmet:0, none:0 }; judged(id).forEach((v) => n[statusClass(v.status)]++); return n; };
const CARD_NAMES = { met:'충족', caution:'주의', unmet:'미충족', none:'판정 안 됨' };
const miniCounts = (n) => ['met','caution','unmet'].map((k) => `<span class="gc-n">${sw(k)}<b class="num">${n[k]}</b><span class="sr">${CARD_NAMES[k]}</span></span>`).join('');
function heroCards() {
  const one = (gid, id, name) => `<a class="gc" data-gc="${gid}" href="#${id}" data-country="${id}"><span class="gc-name">${name}</span><span class="gc-row">${miniCounts(tally(id))}</span></a>`;
  const eu = (id, name) => `<a class="gc-line" href="#${id}" data-country="${id}"><span class="gc-sub">${name}</span><span class="gc-row">${miniCounts(tally(id))}</span></a>`;
  const k = tally('kr-v1');
  return one('us', 'us', '미국') + one('hk', 'hk', '홍콩') + one('sg', 'sg', '싱가포르') + one('jp', 'jp', '일본')
    + `<div class="gc" data-gc="eu"><span class="gc-name">EU</span>${eu('eu-emt', '일반')}${eu('eu-emt-significant', '중요')}</div>`
    + `<a class="gc gc-kr" data-gc="kr" href="#kr-v1" data-country="kr-v1"><span class="gc-name">한국</span><span class="gc-sub">후보값 기준</span><span class="gc-grid">${['met','caution','unmet','none'].map((c) => `<span class="gc-n">${sw(c)}${CARD_NAMES[c]} <b class="num">${k[c]}</b></span>`).join('')}</span></a>`;
}
// 카드를 출발점 둘레 여덟 방향 후보 중 가장 가까운 빈 자리에 놓음. 호, 서울, 다른 카드와 겹치거나 가장자리 흐린 구간으로 나가면 건너뜀. 자리가 없으면 숨김
function placeCards(el, L) {
  let box = el.querySelector('.gcards');
  if (!box) { box = document.createElement('div'); box.className = 'gcards'; box.innerHTML = heroCards(); el.append(box); }
  const wide = matchMedia('(min-width:1100px)').matches, M = 4, placed = [], done = [];
  const hit = (a, b) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
  const onArc = (r) => L.arcs.some((a) => { for (let i = 0; i < a.length; i += 2) if (a[i] > r.x - 5 && a[i] < r.x + r.w + 5 && a[i + 1] > r.y - 5 && a[i + 1] < r.y + r.h + 5) return true; return false; });
  const anchors = { kr: { x: L.seoul.x, y: L.seoul.y, gap: 26 }, ...Object.fromEntries(L.points.map((p) => [p.id, { x: p.x, y: p.y, gap: 10 }])) };
  const seoulBox = { x: L.seoul.x - 24, y: L.seoul.y - 24, w: 48, h: 48 };
  const onLand = (r) => (L.keep || []).some((p) => p.x > r.x - 4 && p.x < r.x + r.w + 4 && p.y > r.y - 4 && p.y < r.y + r.h + 4); // 한국, 일본 땅
  for (const gid of ['kr', 'us', 'eu', 'hk', 'sg', 'jp']) {
    const c = box.querySelector(`[data-gc="${gid}"]`), a = anchors[gid];
    if (!c) continue;
    if (!a || (!wide && gid !== 'kr')) { c.hidden = true; continue; }
    c.hidden = false;
    const w = c.offsetWidth, h = c.offsetHeight, g = a.gap;
    const fit = (f) => { const maxX = L.W * f, maxY = L.H * f; return [[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,1],[1,-1],[-1,-1]].flatMap(([sx, sy]) => [0, 14, 30, 50, 70].map((extra) => ({
      x: sx > 0 ? a.x + g + extra : sx < 0 ? a.x - g - w - extra : a.x - w / 2, y: sy > 0 ? a.y + g + extra : sy < 0 ? a.y - g - h - extra : a.y - h / 2, w, h,
    }))).filter((r) => r.x >= M && r.y >= M && r.x + r.w <= maxX && r.y + r.h <= maxY && !hit(r, seoulBox) && !onLand(r) && !placed.some((q) => hit(r, { x: q.x - 6, y: q.y - 6, w: q.w + 12, h: q.h + 12 })) && (gid === 'kr' || !onArc(r)))
      .sort((p, q) => Math.hypot(p.x + w / 2 - a.x, p.y + h / 2 - a.y) - Math.hypot(q.x + w / 2 - a.x, q.y + h / 2 - a.y)); };
    const all = fit(0.98), r = (gid === 'kr' && (all.find((q) => q.x + q.w <= a.x && q.y + q.h <= a.y) || all.find((q) => q.x + q.w <= a.x))) || all[0]; // 한국은 서울 왼쪽 위를 먼저(오른쪽은 일본 땅), 없으면 왼쪽. 카드는 흐림 밖이라 칸 끝(98%)까지 씀
    if (!r) { c.hidden = true; continue; }
    c.style.left = `${r.x}px`; c.style.top = `${r.y}px`; placed.push(r); done.push(gid);
  }
  return done;
}
function home() {
  const r = reports[state.reportIndex], cash = bankInfo(r), own = r.attestation?.firm || '이미지 서명, 이름 확인 필요';
  const kr = judged('kr-v1'), foreign = Object.fromEntries(FOREIGN_IDS.map((id) => [id, judged(id)]));
  const bankLim = krProposal('R05')?.threshold, dayLim = krProposal('R10')?.deadline_days;
  const stat = (name, valueHtml, note, cls = '') => `<div class="stat ${cls}"><span class="stat-label">${name}</span><strong class="stat-value num">${valueHtml}</strong><span class="stat-note">${note}</span></div>`;
  return `<div class="home"><div class="hero"><div class="home-head"><div><h1>원화 스테이블코인 준비금 공시 판정</h1><p class="lead">발행사가 공개한 준비금 검증 보고서 한 건을 한국 후보 기준 ${RULE_IDS.length}개로 점검하고, 같은 보고서를 해외 기준에도 맞춰 봅니다.</p><ol class="steps"><li><b class="num">1</b>위에서 판정할 보고서 고르기</li><li><b class="num">2</b>한국 기준 ${RULE_IDS.length}개 결과 보기</li><li><b class="num">3</b>해외 기준과 비교</li></ol><p class="report-line">판정 보고서 ${esc(label(r))} / 기준일 ${esc(r.as_of)} / 검증인 ${esc(own)} / 보고서 ${state.reportIndex+1} / ${reports.length}</p></div></div>
    <div class="hero-globe"></div><div class="hero-main">
      <section class="stats panel" aria-label="선택 보고서의 주요 수치">${stat(`은행 예금 비중${cash.approx ? ' (대신 계산)' : ''}`, metricPct(cash.ratio), `한국 규칙 ${ruleName('R05')}, 제안 ${bankLim != null ? pct(bankLim,0) : '자료 없음'} 이상${cash.approx ? '<br>기타 준비자산으로 대신 계산, 국채가 섞인 달이 있음' : ''}`, 'stat-main')}${stat('서명까지 걸린 날', days(r) == null ? '자료 없음' : `${days(r)}<small>일</small>`, `한국 규칙 ${ruleName('R10')}, 제안 ${dayLim ?? '자료 없음'}일 안<br>${daysRange()}`)}${stat('커버리지', metricPct(r.coverage ?? (r.fair_value && r.circulation ? r.fair_value/r.circulation : null)), `한국 규칙 ${ruleName('R01')}<br>준비금 공정가치 / 발행잔액`)}</section>
      <section class="result panel" aria-labelledby="result-title"><div class="section-head"><div><h2 id="result-title">한국 기준 판정 결과</h2><p>한국 후보값은 확정된 규정이 아닙니다</p></div><a class="link-more" href="#kr-v1" data-country="kr-v1">후보값 바꾸기 →</a></div><div class="result-body">${krSummary(kr)}<div class="kr-finds">${krFindings(kr)}</div></div></section>
    </div></div>
    ${chartComposition()}
    ${ruleList(kr, foreign)}
    ${flowSection()}
    <div class="home-sec"><h2>한국 기준값과 해외 기준값</h2><p>한국 제안값은 해외 기준과 국회 법안을 살펴 정했습니다. 표는 규칙마다 한국과 해외의 값을 나란히 보여 주고, 아래 그래프는 숫자 규칙 4개에서 한국 제안값이 어디에 놓이는지 보여 줍니다.</p></div>${ruleTable(jurisdictions, copy)}${ruleDots(jurisdictions, copy)}<div class="disclosure"><strong>${KR_NOTICE}</strong><br>${foreignNames()} 판정: ${FOREIGN_NOTICE}</div>${rulesDock()}</div>`;
}
// ---- 개요 오른쪽 끝에서 나오는 규칙 설명 패널. 열고 닫는 것은 CSS(:hover, :has(:focus-visible))가 하고, 터치는 단추가 .open을 켠다 ----
// 규칙 한 줄 그림: 지금 고른 보고서를 한국 후보값으로 판정한 결과(evaluateRule)를 작은 그림과 짧은 글로 보인다. 패널과 설명 페이지가 같이 쓴다
const GL_W = 124;
const LADDER = ['합의된 절차', '검토', '검증', '감사'];
const LEVEL = { agreed_upon_procedures:0, review:1, quarterly_review:1, 'limited assurance':1, attestation:1, examination:2, 'reasonable assurance':3, audit:3 };
// 한국 기준이 아직 없어(위임 예정, 조사 미완료, 주의) 판정 값이 비어도 보고서 자체 값은 그림으로 보인다
const RAW = { R01:(r) => r.coverage, R03:(r) => r.treasury_max_maturity_days, R04:(r) => r.repo_max_maturity_days, R05:(r) => bankInfo(r).ratio, R06:(r) => r.reserve_currency, R07:(r) => r.disclosure_cadence_days, R08:(r) => r.attestation?.type, R09:(r) => r.as_of_time, R10:(r) => days(r), R11:(r) => r.circulation_formula_disclosed, R12:(r) => r.custodian_disclosure, R13:(r) => r.redemption_days, R14:(r) => r.interest_paid, R15:(r) => r.management_certification };
const GL_MAX = { R01:1.2, R03:365, R04:30, R05:1, R07:92, R10:60, R13:10 }; // 기준이 없을 때 눈금 끝
function ruleGlance(v) {
  const rid = v.rule, cls = statusClass(v.status);
  let val = v.value, thr = v.threshold;
  const own = val == null; // 판정 값 대신 보고서 값을 씀(기준 없음)
  if (own) { val = RAW[rid]?.(reports[state.reportIndex]) ?? null; thr = null; }
  const txt = (t) => ({ fig: `<span class="gl-txt ${cls}">${esc(t)}</span>`, text: '' }); // 글 그림은 두 칸을 쓰므로 값 글을 따로 두지 않는다(상태는 색 칸)
  if (val == null) return { fig: `<span class="gl-no">${esc(v.status)}</span>`, text: '' };
  if (['R01','R03','R04','R05','R07','R10','R13'].includes(rid) && typeof val === 'number') {
    const hasThr = typeof thr === 'number', max = (hasThr ? Math.max(val, thr) * 1.2 : Math.max(val * 1.1, GL_MAX[rid])) || 1, x = (n) => (5 + (GL_W - 10) * n / max).toFixed(1);
    return { fig: `<svg class="gl" viewBox="0 0 ${GL_W} 14" width="${GL_W}" height="14" aria-hidden="true"><line class="gl-base" x1="0" x2="${GL_W}" y1="7" y2="7"/>${hasThr ? `<line class="gl-tick" x1="${x(thr)}" x2="${x(thr)}" y1="1" y2="13"/>` : ''}<circle class="gl-dot ${cls}" cx="${x(val)}" cy="7" r="4"/></svg>`, text: `${esc(fmt(rid, val))} / ${hasThr ? `기준 ${esc(rid === 'R01' || rid === 'R05' ? `${+(thr * 100).toFixed(2)}%` : fmt(rid, thr))}` : esc(v.status)}` };
  }
  if (rid === 'R02' && typeof val[0] === 'object') {
    const total = val.reduce((s, k) => s + k.amount, 0) || 1, n = (k) => val.filter((x) => x.verdict === k).length;
    const seg = ['allowed', 'unclear', 'not_allowed'].flatMap((k) => val.filter((x) => x.verdict === k).map((x) => `<i class="${VERDICT_TEXT[k][0]}" style="flex:${Math.max(x.amount, total * .02)} 1 0"></i>`)).join('');
    const word = cls === 'unmet' ? `허용 밖 ${n('not_allowed')}종` : cls === 'caution' ? `해석 필요 ${n('unclear')}종` : `허용 ${n('allowed')}종`;
    return { fig: `<span class="gl-bar" aria-hidden="true">${seg}</span>`, text: word };
  }
  if (rid === 'R08' && LEVEL[val] != null) {
    const need = (Array.isArray(thr) ? thr : []).map((t) => LEVEL[t]).filter((l) => l != null);
    const cells = LADDER.map((_, i) => `<i class="${i === LEVEL[val] ? cls : ''} ${need.includes(i) ? 'need' : ''}"></i>`).join('');
    return { fig: `<span class="gl-ladder" aria-hidden="true">${cells}</span>`, text: `${LADDER[LEVEL[val]]}${need.length ? ` / 기준 ${LADDER[Math.min(...need)]}` : ''}` };
  }
  if (rid === 'R06') return txt(thr == null ? String(val) : `${val} ${val === thr ? '=' : '≠'} ${thr}`);
  if (rid === 'R09') {
    const at = String(val).match(/^\d\d:\d\d/)?.[0] || (val === 'end of day' ? '일 마감' : val), label = String(thr ?? '');
    return txt(thr == null ? at : `${at} / 기준 ${label.match(/자정|정오/)?.[0] || label.replace(/\(.*?\)|\s*기준$/g, '').trim()}`);
  }
  if (typeof val === 'boolean') return txt(rid === 'R14' ? (val ? '이자 지급' : '이자 없음') : rid === 'R15' ? (val ? '서명함' : '서명 안 함') : fmt(rid, val));
  return txt(fmt(rid, val));
}
function glanceRow(rid) {
  const v = judged('kr-v1').find((x) => x.rule === rid), g = ruleGlance(v);
  return `${g.fig}${g.text ? `<span class="gl-t">${g.text}</span>` : ''}${sw(statusClass(v.status))}<span class="sr">${esc(statusLabel(v))}</span>`;
}
// 개요 오른쪽 숨김 패널: 규칙마다 이름과 무엇을 보는지 한 문장(규칙설명 첫 문장, 최대 2줄)
function rulesDock() {
  const item = (rid) => `<a class="rx-item" href="#rules/${rid}"><small>${rid}</small><b>${ruleName(rid)}</b><p>${esc(copy.규칙설명[rid].split(/(?<=다\.)\s/)[0])}</p></a>`;
  const group = ([name, ids]) => `<div class="rx-group"><h3>${esc(name)}</h3>${ids.map(item).join('')}</div>`;
  return `<aside class="rx-dock" aria-label="판정 항목 설명"><i class="rx-edge" aria-hidden="true"></i><button type="button" class="rx-tab" aria-controls="rx-panel" aria-expanded="false">판정 항목</button><div class="rx-panel" id="rx-panel"><div class="rx-head"><strong>판정 항목 ${RULE_IDS.length}개</strong><a href="#rules">설명 페이지</a></div>${GROUPS.map(group).join('')}</div></aside>`;
}
// ---- 규칙 설명 페이지(#rules, #rules/R03): 규칙마다 설명, 나라별 기준 표, 보고서 현황 ----
const RULE_FIELD = { R03: 'treasury_max_maturity_days', R04: 'repo_max_maturity_days', R11: 'circulation_formula_disclosed', R12: 'custodian_disclosure', R15: 'management_certification', R07: 'disclosure_cadence', R13: 'redemption_days', R14: 'interest_paid' }; // field_notes가 있는 규칙
const NOTE_COUNT_NAME = { found: '읽음', not_disclosed: '공개 안 함', not_in_report: '보고서에 없음', not_applicable: '해당 없음' };
const HAS_VALUE = { // field_notes가 없는 규칙은 엔진이 읽는 값이 있는 보고서 수
  R01: (r) => (r.coverage_ratio ?? r.coverage ?? (r.fair_value != null && r.circulation ? 1 : null)) != null,
  R02: (r) => (r.holdings || []).some((h) => h.kind !== 'settlement' && h.amount > 0),
  R05: (r) => bankInfo(r).ratio != null,
  R06: (r) => r.reserve_currency != null,
  R08: (r) => r.attestation?.type != null,
  R09: (r) => r.as_of_time != null,
  R10: (r) => r.as_of && r.attestation?.signed,
};
function reportStatus(rid) {
  const total = reports.length, field = RULE_FIELD[rid];
  if (field) {
    const n = {};
    reports.forEach((r) => { const s = r.field_notes?.[field]?.state; if (s) n[s] = (n[s] || 0) + 1; });
    const parts = Object.keys(NOTE_COUNT_NAME).filter((s) => n[s]).map((s) => `${NOTE_COUNT_NAME[s]} <b class="num">${n[s]}</b>건`);
    return `보고서 ${total}건 중 ${parts.join(', ') || '표시 없음'}`;
  }
  const has = reports.filter((r) => HAS_VALUE[rid]?.(r)).length;
  return `보고서 ${total}건 중 값이 있는 것 <b class="num">${has}</b>건`;
}
// 규칙 정의 하나를 표 한 줄 글로: 엔진 상태(규정 없음 등), 값, 요건
function ruleState(d) {
  if (d.not_regulated) return STATUS.NOT_REGULATED;
  if (d.unresearched || (Array.isArray(d.candidates) && !d.candidates.length)) return STATUS.UNRESEARCHED;
  if (d.delegated) return `${STATUS.PENDING}, 세부 기준 미정`;
  if (d.partial) return '일부만 규정';
  return '';
}
function ruleValue(rid, d) {
  const dayUnit = d.unit === 'business_days' ? '영업일' : '일';
  if (d.threshold != null && (rid === 'R01' || rid === 'R05')) return `${pct(d.threshold, 0)} ${d.comparison === 'lte' ? '이하' : '이상'}`;
  if (d.threshold_days != null) return `${count(d.threshold_days)}일 이하`;
  if (d.cadence_days != null) return `${count(d.cadence_days)}일 안`;
  if (d.deadline_days != null) return `${count(d.deadline_days)}${dayUnit} 안`;
  if (d.max_days != null) return `${count(d.max_days)}${dayUnit} 안`;
  if (d.time_label) return d.time_label;
  if (Array.isArray(d.verification_types)) return d.verification_types.map((t) => TYPE_NAMES[t] || t).join(', ');
  if (d.required_currency) return d.required_currency === 'same_as_peg' ? '발행 통화와 같은 통화' : d.required_currency;
  return '';
}
function countryRows(rid) {
  const rows = [];
  ['kr-v1', ...FOREIGN_IDS].forEach((id) => {
    const j = jurisdictions[id], entry = j.rules[rid] || {}, name = id === 'kr-v1' ? '한국' : SHORT[id];
    const cands = id === 'kr-v1' && entry.candidates?.length ? entry.candidates : [null];
    cands.forEach((c, i) => {
      const d = c ? resolveRuleDef(j, rid, c.id) : entry, st = ruleState(d), val = st === STATUS.NOT_REGULATED ? '' : ruleValue(rid, d), url = safeLink(d.url);
      const isDef = c && c.id === (entry.default_candidate || entry.candidates[0].id);
      const who = `${i ? '' : `<strong>${name}</strong>`}${c ? `<small>${esc(c.label)}${isDef ? ', 기본 후보' : ''}</small>` : ''}`;
      const body = `${st ? `<b class="rs-state">${esc(st)}</b>` : ''}${val ? `<b class="num">${esc(val)}</b>` : ''}<span>${esc(d.requirement || '')}</span>`;
      const art = d.article ? (url ? `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(d.article)} ↗</a>` : esc(d.article)) : '기재 없음';
      rows.push(`<tr${i ? ' class="more"' : ''}><th scope="row" class="rs-who">${who}</th><td class="rs-std">${body}</td><td>${art}</td><td>${esc(d.legal_status || j.legal_status || '자료 없음')}</td></tr>`);
    });
  });
  return `<div class="rs-tablewrap"><table class="rs-table"><thead><tr><th scope="col">나라</th><th scope="col">기준</th><th scope="col">근거 조문</th><th scope="col">법적 상태</th></tr></thead><tbody>${rows.join('')}</tbody></table></div>`;
}
// R02: 자산 종류 x 나라. 칸은 지금 판정과 같은 색 칸(허용 파랑, 허용 밖 빨강, 해석 필요 회색)
function kindMatrix() {
  const ids = ['kr-v1', ...FOREIGN_IDS];
  const defs = ids.map((id) => resolveRuleDef(jurisdictions[id], 'R02', id === 'kr-v1' ? state.candidates.R02 : undefined) || {});
  const have = new Set(defs.flatMap((d) => Object.keys(d.kinds || {})));
  const kinds = [...Object.keys(KIND_NAMES).filter((k) => have.has(k)), ...[...have].filter((k) => !KIND_NAMES[k])];
  const cell = (d, kind) => {
    const k = d.kinds?.[kind], v = k ? k.verdict : 'unclear';
    const cls = v === 'allowed' ? 'met' : v === 'not_allowed' ? 'unmet' : 'caution', word = v === 'allowed' ? '허용' : v === 'not_allowed' ? '허용 밖' : '해석 필요'; // 해석 필요는 판정에서 주의라 같은 색
    const cond = k ? [k.max_days != null ? `만기 ${k.max_days}일 이하` : '', k.same_currency ? '같은 통화' : ''].filter(Boolean).join(', ') : '';
    const why = k ? cleanBasis(k.basis) : '대응표에 없는 종류라 허용 여부를 정할 수 없습니다.';
    return `<td class="rs-v" title="${esc(why)}">${sw(cls)}<span>${word}</span>${cond ? `<small>${cond}</small>` : ''}</td>`;
  };
  const kr = jurisdictions['kr-v1'].rules.R02, cur = state.candidates.R02 || kr.default_candidate;
  const head = ids.map((id, i) => `<th scope="col">${id === 'kr-v1' ? '한국' : (COL_LABEL[id] || SHORT[id]).replace('<br>', ' ')}</th>`).join('');
  return `<div class="rs-sub"><h4>자산 종류와 나라별 허용 여부</h4><p>칸에 올리면 근거 문장이 보입니다. 한국 열은 후보 '${esc(kr.candidates.find((c) => c.id === cur)?.label || '')}' 기준이고, 나라 화면에서 후보를 바꾸면 따라 바뀝니다.</p></div><div class="rs-tablewrap"><table class="rs-table rs-mx"><thead><tr><th scope="col">자산 종류</th>${head}</tr></thead><tbody>${kinds.map((kind) => `<tr><th scope="row">${esc(KIND_NAMES[kind] || kind)}</th>${defs.map((d) => cell(d, kind)).join('')}</tr>`).join('')}</tbody></table></div>`;
}
function ruleDoc(rid) {
  const line = (k, t) => `<dt>${k}</dt><dd>${esc(t || '')}</dd>`;
  return `<article class="rs-rule panel" id="rule-${rid}" aria-labelledby="rt-${rid}"><h3 id="rt-${rid}"><a href="#rules/${rid}"><small class="num">${rid}</small> ${ruleName(rid)}</a></h3><p class="rs-now"><b>지금 고른 보고서로 보면</b>${glanceRow(rid)}</p><dl class="rs-dl">${line('무엇을 보나', copy.규칙설명?.[rid])}${line('보고서에서 읽는 곳', copy.규칙읽는곳?.[rid])}${line('값이 없을 때', copy.규칙없을때?.[rid])}</dl><div class="rs-sub"><h4>나라별 기준</h4></div>${countryRows(rid)}${rid === 'R02' ? kindMatrix() : ''}<p class="rs-status"><b>보고서 현황</b>${reportStatus(rid)}</p></article>`;
}
function rulesPage() {
  const index = GROUPS.map(([name, ids]) => `<div><h2>${esc(name)}</h2>${ids.map((rid) => `<a href="#rules/${rid}"><small class="num">${rid}</small> ${ruleName(rid)}</a>`).join('')}</div>`).join('');
  const group = ([name, ids]) => `<section class="rs-group" aria-label="${esc(name)}"><div class="rs-gh"><h2>${esc(name)}</h2><p>${esc(copy.묶음설명?.[name] || '')}</p></div>${ids.map(ruleDoc).join('')}</section>`;
  return `<div class="rs-page"><a href="#" class="back-link">← 종합 판정으로 돌아가기</a><section class="rs-top panel"><h1>판정 항목 ${RULE_IDS.length}개</h1><p>한국 후보 기준 ${RULE_IDS.length}개로 준비금 보고서 한 건을 점검하고, 같은 항목으로 해외 ${FOREIGN_IDS.length}곳(미국, EU 일반, EU 중요, 홍콩, 싱가포르, 일본)의 기준에도 맞춰 봅니다. 항목은 네 묶음으로 나뉩니다.</p><p>칸 색의 뜻은 아래 범례와 같습니다. ${KR_NOTICE}.</p>${statusLegend()}<nav class="rs-index" aria-label="판정 항목 목록">${index}</nav></section>${GROUPS.map(group).join('')}</div>`;
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
  return `<article class="rule-item ${open ? 'open' : ''}"><button type="button" data-rule="${v.rule}" class="rule-heading" aria-expanded="${open}" aria-controls="body-${v.rule}"><span class="rule-code">${v.rule}</span><span class="rule-title">${esc(copy.규칙15개[v.rule])}</span><span class="rule-vals num">${v.value != null && typeof v.value !== 'boolean' ? `${esc(fmt(v.rule,v.value))}${v.approx ? '*' : ''}` : ''}${v.threshold != null && typeof v.threshold !== 'boolean' && v.rule !== 'R02' ? `<small>기준 ${esc(fmt(v.rule,v.threshold))}</small>` : ''}</span><span class="status ${statusClass(v.status)}" title="${esc(statusTitle(v))}">${sw(statusClass(v.status))}${esc(statusLabel(v))}</span><span class="chevron" aria-hidden="true"></span></button>${open ? `<div class="rule-body" id="body-${v.rule}">${ruleBody(id,v)}</div>` : ''}</article>`;
}
const NO_VALUE = { [STATUS.NO_DATA]:'이 보고서에는 이 규칙을 따질 항목이 없습니다.', [STATUS.NOT_APPLICABLE]:'이 보고서는 이 규칙이 다루는 자산을 들고 있지 않아 따질 대상이 없습니다.', [STATUS.NOT_REGULATED]:'이 항목에는 규정이 없습니다.', [STATUS.PENDING]:'세부 기준이 위임되어 아직 정해지지 않았습니다.', [STATUS.UNRESEARCHED]:'근거 조사가 끝나지 않았습니다.' };
// 원문 위치, 근거, 수집값 같은 규칙별 상세. 보고서 한 건의 field_notes와 규칙 정의의 kinds에서 읽는다
const FIELD_OF = { R03:'treasury_max_maturity_days', R04:'repo_max_maturity_days', R11:'circulation_formula_disclosed', R12:'custodian_disclosure', R15:'management_certification' };
const NOTE_STATE = { found:'원문에서 찾음', not_disclosed:'원문에 적지 않음', not_in_report:'보고서에 없음', not_applicable:'해당 없음' };
const BASIS_NAME = { direct:'직접 보유한 국채', fund:'준비금 펀드 안 국채', both:'직접 보유와 펀드 안 국채 둘 다' };
// 근거 문장에서 저장소 자료 경로와 행 번호 같은 작업 표시는 뺀다
const cleanBasis = (b) => String(b || '').replace(/\s*(?:근거\s*)?docs\/\S+(?:\s+(?:M-\d+|[\d, ]+행|\d+번))?(?:\([^()]*\))?/g, '').replace(/,?\s*\d+~\d+행:?/g, '').replace(/\(\s*\)/g, '').replace(/\(\s+/g, '(').replace(/,?\s*B\d~B\d\([^)]*\),?\s*D-\d+\.?/g, '').replace(/\)\.:\s*/g, '). ').replace(/^[\s:.]+/, '').replace(/\.{2,}/g, '.').trim();
const money = (n, cur) => `<span title="${esc(count(n))} ${esc(cur || '')}">${esc(new Intl.NumberFormat('ko-KR', { notation:'compact', maximumFractionDigits:1 }).format(n))}${cur ? ` ${esc(cur)}` : ''}</span>`;
function kindList(v, def, r) {
  if (!Array.isArray(v.value) || !v.value.length || typeof v.value[0] !== 'object') return '';
  const items = v.value.map((x) => {
    const [cls, word] = VERDICT_TEXT[x.verdict], basis = def.kinds?.[x.kind]?.basis;
    return `<li><span class="kind-name">${esc(KIND_NAMES[x.kind] || x.kind)}</span><span class="kind-v ${cls}">${sw(cls)}${word}</span><span class="kind-amt num">${money(x.amount, r.reserve_currency)}</span><p class="kind-basis">${esc(cleanBasis(basis) || '대응표에 없는 종류라 허용 여부를 정할 수 없습니다.')}</p></li>`;
  }).join('');
  return `<div class="kind-box"><span class="key">자산 종류별 판정</span><ul class="kind-list">${items}</ul></div>`;
}
// field_notes.where는 글, {page, line, raw}, 그 목록, 없음 중 하나다
const clip = (t) => { t = String(t || ''); return t.length > 90 ? `${t.slice(0, 90)}...` : t; };
function whereText(w) {
  if (!w) return '';
  if (Array.isArray(w)) return `${w.slice(0, 2).map(whereText).join(' / ')}${w.length > 2 ? ` 외 ${w.length - 2}곳` : ''}`;
  if (typeof w === 'object') return `p.${w.page ?? '?'} ${w.line ?? '?'}번째 줄${w.raw ? `, '${clip(w.raw)}'` : ''}`;
  return String(w);
}
function ruleExtra(v, def, r) {
  const note = r.field_notes?.[FIELD_OF[v.rule]], line = (k, t) => t ? `<p><span class="key">${k}</span>${t}</p>` : '';
  const where = note ? line('원문 확인', `${NOTE_STATE[note.state] || '기재 없음'}${whereText(note.where) ? `, ${esc(whereText(note.where))}` : ''}`) : '';
  const memo = line('비고', note?.note ? esc(note.note) : '');
  if (v.rule === 'R02') return kindList(v, def, r);
  if (v.rule === 'R03') return line('최장 만기', r.treasury_max_maturity_days != null ? `${count(r.treasury_max_maturity_days)}일${r.treasury_maturity_basis ? `, 기준 ${BASIS_NAME[r.treasury_maturity_basis]}` : ''}` : '') + where + memo;
  if (v.rule === 'R04') return line('최장 만기', r.repo_max_maturity_days != null ? `${count(r.repo_max_maturity_days)}일` : '') + where + memo;
  if (v.rule === 'R11') return where + memo;
  if (v.rule === 'R12') return line('보관 기관', r.custodians?.length ? esc(r.custodians.join(', ')) : '이름을 적은 곳 없음') + where;
  if (v.rule === 'R15') return line('서명자', r.certifier ? esc(r.certifier) : '') + where + memo;
  return '';
}
function ruleBody(id,v) {
  const entry = jurisdictions[id].rules[v.rule] || {}, def = resolveRuleDef(jurisdictions[id],v.rule,id === 'kr-v1' ? state.candidates[v.rule] : undefined) || {};
  const link = safeLink(v.url);
  const explanation = NO_VALUE[v.status] || '';
  const radio = id === 'kr-v1' && entry.candidates?.length ? `<div class="body-cand"><span class="key">한국 후보값</span>${candOpts(v.rule,'candidate')}</div>` : '';
  return `<p class="rule-help">${esc(ruleHelp(v.rule))}</p><dl class="value-pair"><div><dt>보고서 값</dt><dd class="num">${esc(fmt(v.rule,v.value))}${v.approx ? ' (근사)' : ''}</dd></div><div><dt>기준</dt><dd class="num">${esc(fmt(v.rule,v.threshold,'기준 없음'))}</dd></div></dl>${explanation ? `<p>${esc(explanation)}</p>` : ''}${ruleExtra(v, def, reports[state.reportIndex])}<p><span class="key">요건</span>${esc(def.requirement || '자료 없음')}</p><p><span class="key">근거 조문</span>${esc(v.article || '기재 없음')}</p>${entry.alt ? `<p><span class="key">자금이동업자형</span>${esc(entry.alt.requirement)}${entry.alt.article ? `, ${esc(entry.alt.article)}` : ''}</p>` : ''}${v.approx ? '<p>기타 준비자산으로 대신 계산, 국채가 섞인 달이 있음</p>' : ''}${link ? `<p><a href="${esc(link)}" target="_blank" rel="noopener noreferrer">원문 링크 열기 ↗</a></p>` : '<p><span class="key">원문 링크</span>자료 없음</p>'}${radio}`;
}
function reportItem(i) {
  const r = reports[i], b = bankInfo(r), current = i === state.reportIndex;
  return `<button type="button" class="report-item ${current ? 'current' : ''}" data-report="${i}" aria-pressed="${current}"><span class="report-item-top"><strong>${esc(ym(r))}</strong>${current ? '<em>판정에 사용 중</em>' : '<em>이 보고서로 판정 →</em>'}</span><p class="issuer">${esc(r.issuer)}</p><dl class="report-fields"><div><dt>기준일</dt><dd class="num">${esc(date(r.as_of))}</dd></div><div><dt>커버리지</dt><dd class="num">${pct(r.coverage ?? (r.fair_value/r.circulation))}</dd></div><div><dt>서명일</dt><dd class="num">${esc(date(r.attestation?.signed))}</dd></div><div><dt>검증인</dt><dd>${esc(r.attestation?.firm || '이미지 서명, 이름 확인 필요')}</dd></div><div><dt>서명까지 걸린 날</dt><dd class="num">${days(r) == null ? '자료 없음' : `${days(r)}일`}</dd></div><div><dt>은행 예금 비중</dt><dd class="num">${pct(b.ratio)}${b.approx ? ' (기타 대신 계산)' : ''}</dd></div></dl>${b.approx ? '<p class="report-note">기타 준비자산으로 대신 계산, 국채가 섞인 달이 있음</p>' : ''}</button>`;
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
  // 토큰마다 접어 묶는다. 사용자가 펼치고 접은 것이 없으면 선택 보고서의 토큰(이 나라 것이면), 아니면 첫 토큰만 펼침
  const groups = byToken(indices), sel = reports[state.reportIndex].token, first = groups.some(([tok]) => tok === sel) ? sel : groups[0][0];
  const group = ([tok, idx]) => `<details class="rep-grp" data-grp="r:${esc(tok)}"${(grpOpen[`r:${tok}`] ?? tok === first) ? ' open' : ''}><summary><strong>${esc(coin(reports[idx[0]]))}</strong><small class="num">${idx.length}건</small></summary>${idx.map(reportItem).join('')}</details>`;
  return `<div class="pane-intro">${esc(copy.나라[id].이름)} 발행사 검증 보고서 ${indices.length}건. 보고서를 누르면 그 보고서로 판정이 바뀝니다.</div>${groups.map(group).join('')}`;
}
// ---- 나라 상세 오른쪽 열 맨 위 구조 흐름도: 화면문구.json 나라[id].흐름이 있을 때만 그린다 ----
// 장판 묶음: 'group' 판정 항목 4묶음(기본), 'flow' 흐름 2묶음. 나라를 옮겨도 고른 것을 유지한다
let isoMode = 'group';
const isoModeBtns = () => `<div class="iso-mode" role="group" aria-label="장판 묶음">${[['group', '판정 항목별'], ['flow', '흐름별']].map(([m, t]) => `<button type="button" data-iso-mode="${m}" aria-pressed="${isoMode === m}">${t}</button>`).join('')}</div>`;
// 장판 묶음을 바꿀 때 그림이 천천히 옮겨 가게: 바꾸기 전 블록, 이름표 자리를 재 두었다가 새 그림에서 그 자리부터 미끄러지게 한다. 선, 장판, 지시선은 조금 뒤에 떠오른다
const isoPos = (svg) => {
  const m = new Map(), c = svg.getBoundingClientRect(), s = svg.viewBox.baseVal.width / c.width;
  svg.querySelectorAll('[data-k]').forEach((el) => { const b = el.getBoundingClientRect(); m.set(el.dataset.k, [(b.left - c.left) * s, (b.top - c.top) * s]); });
  return m;
};
function isoGlide(svg, old) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const now = isoPos(svg), move = { duration: 700, easing: 'cubic-bezier(.4,0,.2,1)' }, fade = { duration: 450, delay: 350, easing: 'ease-out', fill: 'backwards' };
  svg.querySelectorAll('[data-k]').forEach((el) => {
    const p = old.get(el.dataset.k), q = now.get(el.dataset.k);
    if (!p) { el.animate([{ opacity: 0 }, { opacity: 1 }], fade); return; }
    const dx = p[0] - q[0], dy = p[1] - q[1], t = el.transform?.baseVal.consolidate()?.matrix, ax = t?.e ?? 0, ay = t?.f ?? 0;
    if (Math.abs(dx) + Math.abs(dy) > .5) el.animate([{ transform: `translate(${ax + dx}px,${ay + dy}px)` }, { transform: `translate(${ax}px,${ay}px)` }], move);
  });
  svg.querySelectorAll('.iso-zone, .iso-ln, .iso-dot, .iso-lead, .iso-halo').forEach((el) => el.animate([{ opacity: 0 }, { opacity: 1 }], fade));
}
function setIsoMode(m) {
  isoMode = m;
  document.querySelectorAll('.iso-section, .iso-dlg').forEach((root) => {
    const svg = root.querySelector('.iso-svg'), id = root.dataset.iso, info = copy.나라[id];
    root.querySelectorAll('[data-iso-mode]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.isoMode === m)));
    if (!svg || !info?.흐름) return;
    const old = isoPos(svg), box = document.createElement('div');
    box.innerHTML = isoFlowSvg(info.흐름, { name: info.이름, id, zones: m });
    svg.replaceWith(box.firstElementChild);
    isoGlide(root.querySelector('.iso-svg'), old);
  });
}
function isoSection(info, id) {
  const spec = info.흐름;
  if (!spec?.노드) return '';
  const ghost = Object.values(spec.노드).some((n) => n?.없음);
  const key = (cls, name) => `<span><i class="iso-key ${cls}" aria-hidden="true"></i>${name}</span>`; // 범례: 선 색과 같은 동그라미
  const legend = `<span class="legend iso-legend">${key('money', '돈과 코인')}${key('check', '확인과 공개')}${ghost ? key('ghost', '규칙에 없는 단계') : ''}</span>`;
  return `<section class="panel iso-section" data-iso="${esc(id)}" aria-labelledby="iso-title"><div class="iso-head"><h2 id="iso-title">${esc(info.이름)} 흐름</h2>${isoModeBtns()}<button type="button" class="iso-zoom" data-action="iso-zoom">크게 보기</button></div><p>발행, 준비금 보관, 검증, 공개가 누구 사이에서 일어나는지 보여 줍니다.</p>${legend}<div class="iso-scroll" data-action="iso-zoom" role="group" aria-labelledby="iso-title">${isoFlowSvg(spec, { name: info.이름, id, zones: isoMode })}</div></section>`;
}
// 흐름도 크게 보기: 열 안의 그림과 같은 전체판(블록 이름표 줄과 선 이름표 모두)을 대화 상자에 원래 크기로 그린다. Esc나 바깥을 누르면 닫힌다
function openIsoZoom(section) {
  let dlg = document.querySelector('.iso-dlg');
  if (!dlg) {
    dlg = document.createElement('dialog'); dlg.className = 'iso-dlg';
    dlg.addEventListener('click', (e) => {
      const m = e.target.closest('[data-iso-mode]'); if (m) { setIsoMode(m.dataset.isoMode); return; }
      if (e.target === dlg || e.target.closest('[data-action="iso-close"]')) dlg.close();
    });
    document.body.append(dlg);
  }
  const title = section.querySelector('h2')?.textContent || '흐름', id = section.dataset.iso, info = copy.나라[id];
  dlg.dataset.iso = id;
  dlg.innerHTML = `<div class="iso-head"><h2>${esc(title)}</h2>${isoModeBtns()}<button type="button" class="iso-zoom" data-action="iso-close">닫기</button></div>${info?.흐름 ? isoFlowSvg(info.흐름, { name: info.이름, id, zones: isoMode }) : ''}`;
  dlg.showModal();
}
// ---- 나라 한눈에: 법(논의, 제정, 시행 단계 점) + 숫자 카드 6개 + 한 줄 설명 ----
const STAGES = ['논의', '제정', '시행'];
const STAGE_OF = { '국회 심사 중': 0, '협의 중': 0, '제정 후 미발효': 1, '시행 중': 2 };
function stageSteps(id) {
  const s = STAGE_OF[jurisdictions[id].legal_status];
  return s === undefined ? '' : `<ol class="gl-steps">${STAGES.map((t, i) => `<li class="${i < s ? 'done' : i === s ? 'on' : ''}"${i === s ? ' aria-current="step"' : ''}>${t}</li>`).join('')}</ol>`;
}
// 숫자 카드 6개: 규칙 자료에서 바로 읽는다(한국은 고른 후보값). 숫자가 없으면 흐린 글
const TILES = [['R01', '준비금'], ['R05', '은행 예금'], ['R03', '국채 만기'], ['R07', '공개 주기'], ['R10', '공개 기한'], ['R13', '돌려받기 기한']];
function tileValue(rid, d) { // [큰 글, 작은 글] 또는 거짓
  const days = (n, unit, tail) => (n % 365 === 0 ? [n / 365, `년 ${tail}`] : [n, `${unit === 'business_days' ? '영업일' : '일'} ${tail}`]);
  if (rid === 'R01' || rid === 'R05') return d.threshold != null && [Math.round(d.threshold * 100), '% 이상'];
  if (rid === 'R03') return d.threshold_days ? days(d.threshold_days, 'days', '이하') : d.max_months && [d.max_months, '개월 이내'];
  if (rid === 'R07') return d.cadence_days ? (d.cadence_days === 7 ? ['매주', ''] : d.cadence_days >= 28 && d.cadence_days <= 31 ? ['매월', ''] : [d.cadence_days, '일마다']) : d.frequency === 'quarterly' && ['분기마다', ''];
  return d.deadline_days ? days(d.deadline_days, d.unit, '안') : d.max_days && days(d.max_days, d.unit, '안');
}
function tiles(id) {
  const jur = jurisdictions[id];
  return `<div class="kpi">${TILES.map(([rid, name]) => {
    const d = resolveRuleDef(jur, rid, id === 'kr-v1' ? state.candidates[rid] : undefined) || {};
    const v = tileValue(rid, d), tag = d.mandatory === false || d.legal_status === '협의 중' ? '제안' : '';
    const val = v ? `<strong${typeof v[0] === 'number' ? ' class="num"' : ''}>${esc(v[0])}</strong>${v[1] ? `<small>${esc(v[1])}</small>` : ''}` : `<em>${d.delegated ? '아직 안 정함' : '정함 없음'}</em>`;
    return `<div class="kpi-t" title="${esc([d.requirement, d.label].filter(Boolean).join(' / '))}"><span>${name}${tag ? `<i>${tag}</i>` : ''}</span><p>${val}</p></div>`;
  }).join('')}</div>`;
}
function glance(info, id) {
  const law = (info.핵심 || []).find((x) => x.항목 === '법');
  return `${law ? `<div class="gl-law"><div class="gl-val"><strong>${esc(law.값)}</strong>${law.설명 ? `<span>${esc(law.설명)}</span>` : ''}</div>${stageSteps(id)}</div>` : ''}${tiles(id)}<p class="eli-line">${esc(info.한줄 || info.설명)}</p>`;
}
function detail() {
  const id = state.jurisdiction, jur = jurisdictions[id], info = copy.나라[id], r = reports[state.reportIndex];
  const results = judged(id), met = results.filter((v) => v.status === STATUS.MET).length, unmet = results.filter((v) => v.status === STATUS.UNMET).length;
  const caution = results.filter((v) => v.status === STATUS.CAUTION).length, done = met + unmet + caution, none = RULE_IDS.length - done;
  const links = [...new Map(Object.values(jur.rules).filter((d) => safeLink(d.url)).map((d) => [safeLink(d.url), d.article || d.requirement])).entries()].slice(0,5);
  const own = ownIndices(id), reportCount = own.length;
  const notes = [
    !own.length ? FOREIGN_NOTICE : !own.includes(state.reportIndex) ? '선택한 보고서는 이 나라 발행사의 보고서가 아닙니다.' : '',
    id === 'kr-v1' ? KR_NOTICE : '',
    id === 'jp' ? JP_NOTICE : '',
  ].filter(Boolean);
  return `<div class="detail"><div class="detail-head"><a href="#" class="back-link">← 종합 판정으로 돌아가기</a><span class="context">선택 보고서 ${esc(label(r))} / 기준일 ${esc(r.as_of)}</span></div><div class="detail-layout"><section class="identity-card panel" aria-label="${esc(info.이름)} 개요"><div class="globe"></div><div class="identity-top"><div class="identity-name"><h1>${esc(info.이름)}</h1><div class="legal">법적 상태<strong>${esc(jur.legal_status)}</strong></div></div></div><div><div class="score"><strong class="num">${met}<small>/ ${done}</small></strong><span>판정된 규칙 ${done}개 중 충족</span></div><div class="rule-grid" role="img" aria-label="규칙 ${RULE_IDS.length}개 판정: 충족 ${met}, 주의 ${caution}, 미충족 ${unmet}, 판정 안 됨 ${none}">${results.map((v) => `<span class="rg ${statusClass(v.status)}" title="${v.rule} ${esc(copy.규칙15개[v.rule])}: ${esc(statusLabel(v))}${notDisclosed(v) ? `, 판정 ${esc(v.status)}` : ''}. ${esc(ruleHelp(v.rule))}"><b>${v.rule}</b></span>`).join('')}</div>${statusLegend({met,caution,unmet,none})}</div><div class="eli"><div class="small-head">${esc(info.이름)} 한눈에</div>${glance(info, id)}</div>${notes.length ? `<div class="notes">${notes.map((n) => `<div class="comparison-note">${n}</div>`).join('')}</div>` : ''}${links.length ? `<div><div class="small-head">규제 원문</div><ul class="source-links">${links.map(([u,t]) => `<li><a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(t)}</a></li>`).join('')}</ul></div>` : ''}<div class="source-date">규칙 자료 기준일 ${esc(jur.as_of)} / 판정 보고서 기준일 ${esc(r.as_of)}</div></section><div class="detail-side">${isoSection(info, id)}<section class="detail-right panel" aria-label="${esc(info.이름)} 판정과 보고서"><div class="detail-tabs" role="tablist" aria-label="상세 내용"><button type="button" role="tab" data-tab="rules" aria-selected="${state.tab === 'rules'}" tabindex="0">규칙 ${RULE_IDS.length}개</button><button type="button" role="tab" data-tab="reports" aria-selected="${state.tab === 'reports'}" tabindex="0">이 나라 보고서${id === 'hk' ? ` / 주간 명세 ${weekly.주간.length}주` : ` ${reportCount}건`}</button></div><div role="tabpanel">${state.tab === 'rules' ? rulesPane(id) : reportsPane(id)}</div></section></div></div><nav class="country-nav" aria-label="나라 이동"><a href="#" >종합 판정</a>${ORDER.map((key) => `<a href="#${key}" class="${id === key ? 'active' : ''}" ${id === key ? 'aria-current="page"' : ''}>${esc(copy.나라[key].이름)}</a>`).join('')}</nav></div>`;
}
// 점 그래프는 칸 폭에 1:1로 맞춘다. 그린 뒤 칸 폭을 재서 폭이 다르면 그 폭으로 다시 그린다
// 판정 흐름은 칸 폭에 맞춰 가로로 늘림. 그린 뒤 칸 폭을 재서 다르면 그 폭으로 다시 그림
let lastFlow = null, flowW = 1100;
function fitFlow() {
  const box = $('#app .flow-scroll');
  if (!box || !lastFlow) return;
  const w = Math.max(900, Math.floor(box.clientWidth));
  if (w !== flowW) { flowW = w; box.innerHTML = flowSvg(lastFlow.rows, { ...lastFlow.opt, width: w }); }
}
function fitDots() {
  const box = $('#app .rv-dots'), fig = box?.firstElementChild;
  if (!fig) return;
  const w = Math.max(280, Math.floor(fig.clientWidth));
  if (w !== Number(box.dataset.w)) { box.dataset.w = w; box.innerHTML = ruleDotsPlots(jurisdictions, copy, w); }
}
function render() {
  if (!reports) return;
  const kept = $('#app .mx-wrap')?.scrollLeft; // 비교 격자를 옆으로 밀어 둔 자리는 다시 그려도 유지
  $('#app').innerHTML = state.jurisdiction ? detail() : state.rules ? rulesPage() : home();
  const mxw = $('#app .mx-wrap'); if (mxw) mxw.scrollLeft = kept ?? mxw.scrollWidth; // 좁은 화면에서 처음엔 최근 달이 보이게 오른쪽 끝에서 시작
  fitDots(); fitFlow();
  const g = $('#app .globe'); if (g && state.jurisdiction) mountGlobe(g, state.jurisdiction);
  const hg = $('#app .hero-globe'); if (hg && !state.jurisdiction) mountHeroGlobe(hg, { onLayout: (L) => placeCards(hg, L) });
  $('#report-btn').innerHTML = `<span>${esc(coin(reports[state.reportIndex]))}</span>${esc(ym(reports[state.reportIndex]))}`; // 칸 안에 코인 이름(옅게)과 달
  $('#rail-home').classList.toggle('active',!state.jurisdiction && !state.rules);
  $('#rail-country').classList.toggle('active',Boolean(state.jurisdiction && state.jurisdiction !== 'kr-v1'));
  $('#rail-kr').classList.toggle('active',state.jurisdiction === 'kr-v1');
  $('#rail-country').href = state.jurisdiction && state.jurisdiction !== 'kr-v1' ? `#${state.jurisdiction}` : '#us';
  renderSidebar($('#side'), {
    ruleGroups: GROUPS, ruleActive: state.rules,
    reports, order: ORDER, jurisdiction: state.jurisdiction, index: state.reportIndex, ym, coin, groups: byToken([...reports.keys()]), openReports: (tok, el) => toggleReportPop(!(rpTok === tok && !reportPop.hidden), tok, el),
    names: Object.fromEntries(ORDER.map((id) => [id, copy.나라[id].이름])),
    subs: Object.fromEntries(ORDER.map((id) => [id, copy.나라[id].부제 || ''])),
  });
}
async function init() {
  try {
    const files = await Promise.all([
      file('./data/reports.json'), file('./화면문구.json'), file('./data/홍콩_주간명세.json'),
      ...ORDER.map((id) => file(`./jurisdictions/${id}.json`)),
    ]);
    reports = files[0].reports; excluded = files[0].excluded || []; series = files[0].series || {}; copy = files[1]; weekly = files[2];
    jurisdictions = Object.fromEntries(ORDER.map((id,i) => [id, files[i+3]]));
    state.reportIndex = Math.max(0,reports.findLastIndex((r) => r.token === 'PYUSD')); // 가장 최근 PYUSD 보고서
    route();
  } catch (error) {
    console.error('자료 불러오기 실패',error);
    $('#app').innerHTML = '<div class="empty-report">자료를 불러오지 못했습니다. 정적 웹 서버에서 다시 열어 주세요.</div>';
  }
}
// 보고서 고르는 창: 칸 아래 왼쪽으로 펼침. 위는 연도 탭, 아래는 그 해의 보고서 8줄 x 12달. 칸에는 달 숫자, 자료 없는 달은 점
const reportBtn = $('#report-btn'), reportPop = $('#report-pop');
let rpYear, rpLine = null, rpTok = null; // rpLine: 이름을 눌러 강조한 줄. rpTok: 사이드바에서 연 코인(있으면 사이드바 옆에 띄움)
function drawReportPop() {
  const lo = reports.reduce((a, r) => r.month < a ? r.month : a, '9'), hi = reports.reduce((a, r) => r.month > a ? r.month : a, '');
  const years = []; for (let y = Number(lo.slice(0,4)); y <= Number(hi.slice(0,4)); y++) years.push(y);
  const rows = byToken([...reports.keys()]).map(([t, idx]) => ({ t, name: coin(reports[idx[0]]), at: new Map(idx.map((i) => [reports[i].month, i])) }));
  const ks = Array.from({length:12}, (_, m) => `${rpYear}-${String(m+1).padStart(2,'0')}`);
  const cell = (row, ri, k) => {
    const m = Number(k.slice(5)), qe = [3,6,9].includes(m) ? ' qe' : ''; // qe: 분기 끝 달 뒤를 조금 띄움
    if (k < lo || k > hi) return `<i class="later${qe}"></i>`; // 자료 기간 밖(아직 안 온 달): 빈 상자
    const i = row.at.get(k), text = `${row.name} ${rpYear}년 ${m}월`;
    if (i == null) return `<i class="miss${qe}" data-row="${ri}" data-miss="${esc(text)}"></i>`;
    const on = i === state.reportIndex;
    return `<button type="button" data-ri="${i}" data-row="${ri}" data-col="${m}" class="${on ? 'on' : ''}${qe}" tabindex="${on ? 0 : -1}" aria-label="${esc(text)}">${m}</button>`;
  };
  reportPop.innerHTML = `<div class="rp-body"><span></span><div class="rp-years" role="tablist" aria-label="연도">${years.map((y) => `<button type="button" role="tab" data-year="${y}" aria-selected="${y === rpYear}">${y}</button>`).join('')}</div><span></span><span class="rp-row rp-qs" aria-hidden="true">${[1,2,3,4].map((q) => `<b class="${q < 4 ? 'qe' : ''}">${q}분기</b>`).join('')}</span>${rows.map((row, ri) => `<div class="rp-line${row.t === reports[state.reportIndex].token ? ' cur' : ''}${rpLine === ri ? ' pick' : ''}" data-line="${ri}"><button type="button" class="rp-name${row.t === reports[state.reportIndex].token ? ' on' : ''}" aria-pressed="${rpLine === ri}">${esc(row.name)}</button><span class="rp-row">${ks.map((k) => cell(row, ri, k)).join('')}</span></div>`).join('')}</div><div class="rp-cap"></div>`;
  reportPop.querySelector('.rp-body').classList.toggle('picking', rpLine != null);
  if (!reportPop.querySelector('[data-ri][tabindex="0"]')) reportPop.querySelector('[data-ri]')?.setAttribute('tabindex', '0'); // 고른 보고서가 다른 해면 첫 칸이 키보드 진입점
  rpCaption(null);
}
// 아래 한 줄: 가리킨 칸의 보고서(없으면 고른 보고서). 가리킨 줄의 이름도 진하게
function rpCaption(el) {
  const r = !el ? reports[state.reportIndex] : el.dataset.ri != null ? reports[Number(el.dataset.ri)] : null;
  reportPop.querySelector('.rp-cap').innerHTML = r ? `<strong>${esc(coin(r))}</strong> ${esc(ym(r))}<span>기준일 ${esc(r.as_of)}</span>` : `${esc(el.dataset.miss)}<span>자료 없음</span>`;
  reportPop.querySelectorAll('.rp-name.hi').forEach((x) => x.classList.remove('hi'));
  if (el) reportPop.querySelector(`[data-line="${el.dataset.row}"] .rp-name`)?.classList.add('hi');
}
// tok, anchor를 주면(사이드바 코인 줄) 그 코인 줄을 강조하고, 다른 코인이면 그 코인의 최근 보고서 해를 보여 줌
function toggleReportPop(open, tok = null, anchor = null) {
  rpTok = open ? tok : null;
  reportPop.classList.toggle('side', Boolean(rpTok));
  if (!rpTok) reportPop.style.cssText = '';
  if (open) {
    const rows = byToken([...reports.keys()]), line = rows.findIndex(([t]) => t === tok), cur = reports[state.reportIndex];
    const base = line < 0 || cur.token === tok ? cur : reports[rows[line][1].at(-1)];
    rpYear = Number(base.month.slice(0,4)); rpLine = line < 0 ? null : line; drawReportPop();
  }
  reportPop.hidden = !open;
  reportBtn.setAttribute('aria-expanded', String(open && !rpTok));
  if (open && anchor) placeBeside(anchor);
  const box = reportPop.querySelector('.rp-line.pick') || reportPop;
  if (open) (box.querySelector('[data-ri].on') || [...box.querySelectorAll('[data-ri]')].at(-1))?.focus({ preventScroll: true });
}
// 사이드바 오른쪽, 코인 줄 높이에 띄움(화면 밖으로 나가면 위로 올림). html zoom 때문에 화면 크기를 CSS 값으로 바꾸는 비율 k를 곱함
function placeBeside(anchor) {
  const a = anchor.getBoundingClientRect(), k = anchor.offsetWidth / a.width, h = reportPop.getBoundingClientRect().height;
  reportPop.style.left = `${(anchor.closest('.rail').getBoundingClientRect().right + 8) * k}px`;
  reportPop.style.top = `${Math.max(8, Math.min(a.top - 8, innerHeight - h - 8)) * k}px`;
}
const rpBack = (tok) => ((tok && $(`#side [data-tok="${tok}"]`)) || reportBtn).focus(); // 닫으면 연 자리로 초점을 돌림
reportBtn.addEventListener('click', () => toggleReportPop(reportPop.hidden));
reportPop.addEventListener('click', (e) => {
  const yb = e.target.closest('[data-year]'); if (yb) { rpYear = Number(yb.dataset.year); drawReportPop(); reportPop.querySelector(`[data-year="${rpYear}"]`).focus(); return; }
  const nm = e.target.closest('.rp-name'); if (nm) { // 이름: 그 줄만 띠로 강조하고 나머지는 흐리게. 다시 누르면 풀림
    const line = Number(nm.parentNode.dataset.line); rpLine = rpLine === line ? null : line;
    reportPop.querySelector('.rp-body').classList.toggle('picking', rpLine != null);
    reportPop.querySelectorAll('.rp-line').forEach((x) => { const on = Number(x.dataset.line) === rpLine; x.classList.toggle('pick', on); x.querySelector('.rp-name').setAttribute('aria-pressed', String(on)); });
    return;
  }
  const ri = e.target.closest('[data-ri]'); if (ri) { const tok = rpTok; toggleReportPop(false); selectReport(Number(ri.dataset.ri)); rpBack(tok); }
});
reportPop.addEventListener('mouseover', (e) => { const c = e.target.closest('[data-ri],[data-miss]'); if (c) rpCaption(c); });
reportPop.addEventListener('mouseleave', () => rpCaption(document.activeElement?.closest?.('#report-pop [data-ri]') || null));
reportPop.addEventListener('focusin', (e) => { if (e.target.dataset.ri) rpCaption(e.target); });
// 방향키: 좌우는 같은 줄의 이웃 보고서, 위아래는 옆 줄에서 가장 가까운 달
reportPop.addEventListener('keydown', (e) => {
  const b = e.target.closest('[data-ri]'), d = {ArrowLeft:[0,-1],ArrowRight:[0,1],ArrowUp:[-1,0],ArrowDown:[1,0]}[e.key];
  if (!b || !d) return;
  e.preventDefault();
  const row = Number(b.dataset.row) + d[0], col = Number(b.dataset.col);
  const next = [...reportPop.querySelectorAll(`button[data-row="${row}"]`)].filter((x) => !d[1] || Math.sign(x.dataset.col - col) === d[1]).sort((x, y) => Math.abs(x.dataset.col - col) - Math.abs(y.dataset.col - col))[0];
  if (next) { b.tabIndex = -1; next.tabIndex = 0; next.focus(); }
});
document.addEventListener('click', (e) => { if (!reportPop.hidden && !e.composedPath().includes(reportPop.parentNode) && !e.target.closest?.('#side [data-tok]')) toggleReportPop(false); }); // 토큰을 누르면 창을 다시 그려 눌린 단추가 떨어져 나가므로 composedPath로 판단
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !reportPop.hidden) { const tok = rpTok; toggleReportPop(false); rpBack(tok); } });
$('.rail').addEventListener('scroll', () => { if (rpTok) placeBeside($(`#side [data-tok="${rpTok}"]`)); }, { passive: true }); // 사이드바를 굴려도 코인 줄 옆에 붙어 있게
// 찾기: 나라, 규칙, 보고서. 고르면 그 나라 화면, 그 규칙, 그 보고서로 이동
const searchBox = $('#search'), searchList = $('#search-list');
let hits = [], cur = 0;
function findRule(rid) {
  if (state.rules) { window.location.hash = `#rules/${rid}`; return; } // 규칙 설명 페이지: 그 규칙으로
  if (!state.jurisdiction) { // 개요: 규칙별 판정의 그 줄로
    const row = document.querySelector(`[data-hm="${rid}"]`);
    if (row) { row.scrollIntoView({ block: 'center' }); row.classList.add('hit'); setTimeout(() => row.classList.remove('hit'), 1600); }
    return;
  }
  if (state.tab !== 'rules') history.replaceState(null, '', `#${state.jurisdiction}`); // 나라 화면: 규칙 탭에서 그 규칙을 펼침
  Object.assign(state, { tab: 'rules', openRule: rid, showAll: true });
  render();
  document.querySelector(`[data-rule="${rid}"]`)?.scrollIntoView({ block: 'center' });
}
function runSearch() {
  const q = searchBox.value.trim().toLowerCase();
  const items = !copy ? [] : [
    ...ORDER.map((id) => ({ kind: '나라', title: copy.나라[id].이름, sub: copy.나라[id].부제 || '', text: copy.나라[id].한줄 || '', go: () => selectJurisdiction(id) })),
    ...RULE_IDS.map((rid) => ({ kind: '규칙', title: `${rid} ${copy.규칙15개[rid]}`, sub: '', text: copy.규칙설명?.[rid] || '', go: () => findRule(rid) })),
    ...reports.map((r, i) => ({ kind: '보고서', title: label(r), sub: r.as_of, text: `${r.issuer} ${r.token}`, go: () => selectReport(i) })),
  ];
  // 이름이 검색어로 시작 > 이름에 들어 있음 > 설명에 들어 있음
  hits = q ? items.map((x) => { const t = x.title.toLowerCase(); return { ...x, s: t.startsWith(q) ? 0 : t.includes(q) ? 1 : `${x.sub} ${x.text}`.toLowerCase().includes(q) ? 2 : 9 }; }).filter((x) => x.s < 9).sort((a, b) => a.s - b.s).slice(0, 8) : [];
  cur = 0;
  searchList.innerHTML = hits.length ? hits.map((x, i) => `<li role="option" id="sr-${i}" data-i="${i}" aria-selected="${i === cur}"><span class="search-kind">${x.kind}</span><span class="search-title">${esc(x.title)}</span><span class="search-sub">${esc(x.sub)}</span></li>`).join('') : '<li class="search-empty">찾는 항목이 없습니다</li>';
  searchList.hidden = !q;
  searchBox.setAttribute('aria-expanded', String(Boolean(q)));
  searchBox.setAttribute('aria-activedescendant', hits.length ? 'sr-0' : '');
}
const closeSearch = () => { searchList.hidden = true; searchBox.setAttribute('aria-expanded', 'false'); };
function pickHit(i) { const h = hits[i]; if (!h) return; searchBox.value = ''; closeSearch(); searchBox.blur(); h.go(); }
searchBox.addEventListener('input', runSearch);
searchBox.addEventListener('focus', () => { if (searchBox.value.trim()) runSearch(); });
searchBox.addEventListener('blur', closeSearch);
searchBox.addEventListener('keydown', (e) => {
  if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && hits.length) {
    e.preventDefault(); cur = (cur + (e.key === 'ArrowDown' ? 1 : hits.length - 1)) % hits.length;
    searchList.querySelectorAll('[data-i]').forEach((li) => li.setAttribute('aria-selected', String(Number(li.dataset.i) === cur)));
    searchBox.setAttribute('aria-activedescendant', `sr-${cur}`);
  } else if (e.key === 'Enter' && hits.length) { e.preventDefault(); pickHit(cur); }
  else if (e.key === 'Escape') closeSearch();
});
searchList.addEventListener('mousedown', (e) => { const li = e.target.closest('[data-i]'); if (li) { e.preventDefault(); pickHit(Number(li.dataset.i)); } });
$('#app').addEventListener('click',(e) => {
  const isoM = e.target.closest('[data-iso-mode]'); if (isoM) { setIsoMode(isoM.dataset.isoMode); return; }
  const zoom = e.target.closest('[data-action="iso-zoom"]'); if (zoom) { openIsoZoom(zoom.closest('.iso-section')); return; }
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
// 규칙 설명 패널: 마우스는 CSS가 열고 닫는다. 손가락(터치, 펜)은 손잡이를 눌러 열고, 바깥을 누르거나 Esc로 닫는다
$('#app').addEventListener('mousedown', (e) => { if (e.target.closest('.rx-tab')) e.preventDefault(); });
// 판정 항목 패널: 탭이나 화면 오른쪽 끝 띠에 커서만 대도 열리고, 패널 밖으로 나가면 잠깐 뒤 닫힌다(밀려 나오는 동안 커서가 탭에서 벗어나도 닫히지 않게)
let rxTimer = 0;
const rxSet = (d, on) => { d.classList.toggle('open', on); d.querySelector('.rx-tab')?.setAttribute('aria-expanded', String(on)); };
$('#app').addEventListener('mouseover', (e) => { const d = e.target.closest?.('.rx-dock'); if (!d) return; clearTimeout(rxTimer); if (e.target.closest('.rx-tab, .rx-edge')) rxSet(d, true); });
$('#app').addEventListener('mouseout', (e) => { const d = e.target.closest?.('.rx-dock'); if (!d || d.contains(e.relatedTarget)) return; clearTimeout(rxTimer); rxTimer = setTimeout(() => rxSet(d, false), 300); }); // 마우스로 눌러도 포커스가 남아 패널이 안 닫히는 것을 막음
$('#app').addEventListener('click', (e) => { const t = e.target.closest('.rx-tab'); if (t && e.pointerType !== 'mouse') t.setAttribute('aria-expanded', String(t.closest('.rx-dock').classList.toggle('open'))); });
document.addEventListener('pointerdown', (e) => { const d = document.querySelector('.rx-dock.open'); if (d && !d.contains(e.target)) { d.classList.remove('open'); d.querySelector('.rx-tab').setAttribute('aria-expanded', 'false'); } });
document.addEventListener('keydown', (e) => { const d = e.key === 'Escape' && document.querySelector('.rx-dock'); if (d) { d.classList.remove('open'); d.querySelector('.rx-tab').setAttribute('aria-expanded', 'false'); if (d.contains(document.activeElement)) document.activeElement.blur(); } });
// details의 toggle은 위로 올라가지 않아 잡아서(capture) 받는다
$('#app').addEventListener('toggle',(e) => { if (e.target.dataset?.grp) grpOpen[e.target.dataset.grp] = e.target.open; }, true);
bindSidebar($('#side'));
bindFlow($('#app'));
window.addEventListener('hashchange',route);
window.addEventListener('resize',() => { fitDots(); fitFlow(); });
init();
