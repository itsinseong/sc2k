import { RULE_IDS, STATUS, evaluateReport, evaluateRule, resolveRuleDef, calendarDaysBetween } from './engine.js';
import { ruleDots, ruleDotsPlots } from './charts.js';
import { mountGlobe, mountHeroGlobe } from './globe.js';
import { renderSidebar, bindSidebar } from './sidebar.js';
import { flowSvg, flowTotals, bindFlow } from './flow.js';
import { isoFlowSvg } from './iso.js';
import { buildData } from './viz/data.js';
import * as Z1 from './viz/z1.js';
import * as Z2 from './viz/z2.js';
import * as Z3 from './viz/z3.js';
import * as Z4 from './viz/z4.js';
import * as Z6 from './viz/z6.js';
import * as Z7 from './viz/z7.js';
import * as Z9 from './viz/z9.js';
const wa = (s) => { const c = s.charCodeAt(s.length - 1); return s + (c >= 0xAC00 && c <= 0xD7A3 && (c - 0xAC00) % 28 ? '과' : '와'); };  // 받침 있으면 과(한국과), 없으면 와(싱가포르와)


const ORDER = ['us', 'eu-emt', 'eu-emt-significant', 'hk', 'sg', 'jp', 'kr-v1'];
const FOREIGN_NOTICE = '이 나라 발행사의 보고서는 아직 자료에 없어서, 다른 나라 발행사의 보고서를 이 나라 규칙에 대 본 결과입니다. 이 나라 회사의 실제 공시가 아닙니다';
const KR_NOTICE = '한국 열은 국회 의원안 값이며 확정된 규정이 아닙니다';
const JP_NOTICE = '일본 열은 신탁형(특정신탁수익권) 규칙입니다. 자금이동업자형은 규칙을 눌렀을 때 보조로 보입니다. 규정 없음은 읽은 원문 범위에서 찾지 못했다는 뜻입니다';
const CATEGORIES = [
  ['bank', '은행 예금'], ['repo', '하루짜리 담보 대출(레포)'],
  ['fund', '국채 펀드'], ['treasury', '국채'], ['other', '기타'],
];
const TYPE_NAMES = {cash:'현금',bank_deposit:'은행 예금',treasury_bill_93d:'93일 이하 국채',overnight_repo:'하루짜리 레포',government_mmf:'국채 펀드',overnight_reverse_repo:'하루짜리 역레포',approved_federal_asset:'감독기관 승인 연방정부 자산',tokenized_reserve:'토큰 형태 준비자산',cash_equivalent:'현금성 자산',government_bond_3m:'3개월 이하 국채',hqla:'고유동성 우량자산',bank_deposit_3m:'3개월 이내 은행 예금',low_risk_liquid_asset:'저위험 고유동성 자산',government_bond:'국채',other_designated:'그 밖의 지정 자산',examination:'검증 보고서',attestation:'확인 보고서',audit:'감사',quarterly_review:'분기 검토', 'reasonable assurance':'합리적 확신',demand_deposit_same_currency:'같은 통화 요구불 예금',term_deposit_principal_protected_cancellable_anytime:'원금 보전, 수시 해약 정기예금',jgb_remaining_le_3m_jpy_only:'3개월 이내 엔화 국채',foreign_bond_remaining_le_3m_same_currency:'3개월 이내 같은 통화 외국 채권'};
const $ = (sel) => document.querySelector(sel);
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pct = (ratio, digits=2) => ratio == null ? '자료 없음' : `${(ratio * 100).toFixed(digits)}%`;
const count = (x) => x == null ? '자료 없음' : Number(x).toLocaleString('ko-KR');
const date = (x) => x || '자료 없음';
const file = (path) => fetch(path).then((response) => {
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return response.json();
});
const state = { reportIndex: 0, jurisdiction: null, rules: null, tab: 'rules', openRule: null, showAll: false, candidates: {}, cmp: null }; // cmp: 나라 화면에서 비교할 나라
let reports, jurisdictions, copy, weekly, excluded = [], series = {};
// ---- 새 차트(viz/z*.js): 구역마다 보기 2~3개, 첫 보기가 기본. 보기 단추는 state.viz[구역]에 기억 ----
const VZ = { 1: Z1, 2: Z2, 3: Z3, 4: Z4, 6: Z6, 7: Z7, 9: Z9 };
state.viz = {};
const vzW = {}; // 구역별 실제 칸 폭(px). 그린 뒤 fitViz가 재서 다르면 다시 그린다
function vizViews(n, extra = {}) {
  try { return VZ[n].views({ data: buildData(reports, jurisdictions, state.candidates), ri: state.reportIndex, cmp: 'us', lim: krLim(), dayLim: krDayLim() ?? 30, focus: 'kr-v1', J: jurisdictions, width: vzW[n], krSplit: krSplitMap(), ...extra }) || []; }
  catch (e) { console.error('viz', n, e); return []; }
}
const vzTabs = (n, items, curKey) => items.length > 1 ? `<div class="rt-pills vz-tabs" role="group" aria-label="보기">${items.map(([k, label]) => `<button type="button" class="rt-pill" data-vzview="${n}:${k}" aria-pressed="${k === curKey}">${esc(label)}</button>`).join('')}</div>` : '';
function vizBlock(n, extra = {}) {
  const vs = vizViews(n, extra);
  if (!vs.length) return '';
  const cur = vs.find((v) => v.key === state.viz[n]) || vs[0];
  return `<div class="vz" data-vz="${n}">${vzTabs(n, vs.map((v) => [v.key, v.label]), cur.key)}<div class="vz-body">${cur.html}</div></div>`;
}
// 그린 뒤 칸 폭을 재서, 차트가 그 폭으로 그려지지 않았으면 그 폭으로 다시 그린다(글자 크기를 어디서나 같게)
let vzFitting = false;
function fitViz() {
  if (vzFitting) return;
  let changed = false;
  document.querySelectorAll('#app [data-vz]').forEach((el) => {
    const n = el.dataset.vz, body = el.querySelector('.vz-body');
    if (!body) return;
    const w = Math.floor(body.clientWidth) - 2; // 칸 폭과 똑같이 그리면 화면 확대율(zoom .9)의 소수점 오차로 넘쳐 가로 스크롤바가 생김
    if (w > 0 && Math.abs(w - (vzW[n] || 0)) > 2) { vzW[n] = w; changed = true; }
  });
  if (changed) { vzFitting = true; const y = window.scrollY; render(); window.scrollTo({ top: y, behavior: 'instant' }); vzFitting = false; }
}
const vzPanel = (n, title, desc, extra) => `<section class="rl-section panel vz-section"><div class="section-head"><div><h2>${title}</h2><p>${desc}</p></div></div>${vizBlock(n, extra)}</section>`;

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
    state.tab = ['reports', 'compare'].includes(tab) ? 'compare' : 'rules'; // 옛 주소 #us/reports는 비교 탭으로
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
  state.reportIndex = index;
  state.openRule = null;
  render();
  document.querySelectorAll('#app .report-line, #app .detail-head .context, #report-btn').forEach((el) => { el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash'); }); // 판정이 다른 보고서로 바뀌었음을 보임
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
const candOf = (id, rid) => id === 'kr-v1' ? state.candidates[rid] : undefined;
// 차트가 쓰는 한국 기준: 고른 후보값(의원안 값, 해외 참조). 은행 예금은 3단계 단추(state.mxLim)가 먼저, 고른 후보가 위임이면 해외 값 중 가장 낮은 30%
const krPick = (rid) => resolveRuleDef(jurisdictions['kr-v1'], rid, state.candidates[rid]) || {};
const krLim = () => state.mxLim ?? krPick('R05').threshold ?? MX_LIMS[0][0];
const krDayLim = () => krPick('R10').deadline_days;
// 종합 화면 3번 표: 줄은 코인, 가로는 달. 칸에 숫자를 쓰지 않고, 고른 은행 예금 기준에 못 미친 보고서를 굵은 띠로 잇는다.
// 한국 의원안은 은행 예금 비율을 위임하거나 정하지 않아서, 해외 기준값 중에서 단추로 고르게 한다
const MX_LIMS = [[0.3, 'EU 일반, 미국 OCC 안'], [0.5, '일본'], [0.6, 'EU 중요']];
const MX_SHORT = { bank:'예금', repo:'레포', fund:'펀드', treasury:'국채', other:'기타' };
function chartReports() {
  const lim = krLim(), dayLim = krDayLim() ?? 30;
  const months = [...new Set(reports.map((r) => r.month))].sort(), n = months.length, last = months[n - 1];
  const P = (v) => `${(v * 100).toFixed(4).replace(/\.?0+$/, '')}%`, at = (i, w = 1) => `left:${P(i / n)};width:${P(w / n)}`;
  const limTxt = pct(lim, 0), quarterly = new Set(reports.filter((x) => x.disclosure_cadence === 'quarterly').map((x) => x.token));
  let fails = 0, lates = 0;
  const rows = [...new Set(reports.map((r) => r.token))].map((tok) => {
    const se = series[tok], mine = reports.flatMap((x, i) => x.token === tok ? [i] : []), latest = reports[mine.at(-1)];
    // 달마다 상태: pre(출시 전, 그리지 않음), pass, fail, gap(보고서 없음 또는 은행 예금을 알 수 없음)
    const cells = months.map((m) => {
      const i = mine.find((k) => reports[k].month === m);
      if (i == null) {
        const ex = excluded.find((e) => e.token === tok && e.month === m);
        if (se && m < se.first_month) return { k:'pre' };
        return { k:'gap', why: ex ? `원문 합계 오류로 뺌. ${ex.reason}` : se?.not_yet_published?.includes(m) ? '아직 게시 전' : quarterly.has(tok) ? '분기 공시라 보고서 없는 달' : '보고서 없음' };
      }
      const r = reports[i], b = bankInfo(r), d = days(r);
      if (d != null && d > dayLim) lates++;
      if (b.ratio == null) return { k:'gap', i, d, why:'원문이 은행 예금을 따로 적지 않아 구분 안 됨' };
      const fail = b.ratio < lim; if (fail) fails++;
      return { k: fail ? 'fail' : 'pass', i, d, b };
    });
    // 미달 묶음: 미달 보고서 사이에 보고서 없는 달만 끼면 한 묶음으로 센다(분기 공시). 통과나 구분 안 됨이 끼면 끊는다
    const runs = []; let cur = null;
    cells.forEach((c, j) => {
      if (c.k === 'fail') { if (cur) { cur.end = j; cur.count++; } else cur = { start:j, end:j, count:1 }; }
      else if (!(c.k === 'gap' && c.i == null && cur)) { if (cur) runs.push(cur); cur = null; }
    });
    if (cur) runs.push(cur);
    const inRun = (j) => runs.some((r) => j > r.start && j < r.end);
    let track = '';
    cells.forEach((c, j) => {
      if (c.k === 'pass') track += `<i class="rt-line" style="${at(j)}"></i>`;
      else if (c.k === 'gap') track += `<i class="rt-gap${inRun(j) ? ' in' : ''}" style="${at(j)}"></i>`;
    });
    // 띠: 붙어 있는 미달 달을 한 조각으로
    cells.forEach((c, j) => { if (c.k === 'fail' && cells[j - 1]?.k !== 'fail') { let e = j; while (cells[e + 1]?.k === 'fail') e++; track += `<i class="rt-band" style="${at(j, e - j + 1)}"></i>`; } });
    runs.filter((r) => r.count >= 3).forEach((r) => { track += `<span class="rt-run" style="left:${P(r.start / n)}">${quarterly.has(tok) ? '분기 보고서 ' : ''}${r.count}건 연속 미달</span>`; });
    cells.forEach((c, j) => {
      if (c.i == null && c.k !== 'gap') return;
      const when = `${coin(latest)} ${months[j].slice(0,4)}년 ${Number(months[j].slice(5))}월`;
      if (c.i == null) { track += `<span class="rt-c empty" style="${at(j)}" title="${esc(`${when}: ${c.why}`)}"></span>`; return; }
      const r = reports[c.i], sel = state.reportIndex === c.i, late = c.d != null && c.d > dayLim;
      const t = `${label(r)}: ${c.b ? `은행 예금 ${pct(c.b.ratio,1)}${c.b.approx ? ' (대신 계산)' : ''}, 기준 ${limTxt} ${c.k === 'fail' ? '미만' : '이상'}` : c.why}, 서명까지 ${c.d ?? '자료 없음'}일${late ? `, ${dayLim}일 초과` : ''}`;
      if (late) track += `<i class="rt-late" style="left:${P((j + 0.5) / n)}"></i>`;
      track += `<button type="button" class="rt-c${sel ? ' selected' : ''}" style="${at(j)}" data-report="${c.i}" aria-pressed="${sel}" aria-label="${esc(t)}" title="${esc(t)}"></button>`;
    });
    const judgedN = cells.filter((c) => c.k === 'pass' || c.k === 'fail').length, failN = cells.filter((c) => c.k === 'fail').length, lb = bankInfo(latest);
    const comp = mix(latest).filter((x) => x.ratio >= 0.005).map((x) => `${MX_SHORT[x.type]} ${Math.round(x.ratio * 100)}%`).join(', ');
    return `<div class="rt-head"><strong>${esc(coin(latest))}</strong><small>${latest.month === last ? '' : `${esc(ym(latest))} 기준 `}${esc(comp)}</small></div><div class="rt-track">${track}</div><div class="rt-n num"><b>${failN}</b>/${judgedN}</div><div class="rt-n num${lb.ratio != null && lb.ratio < lim ? ' low' : ''}"><b>${lb.ratio == null ? '–' : lb.ratio >= 0.9995 ? `${Math.round(lb.ratio * 100)}%` : pct(lb.ratio, 1)}</b></div>`;
  }).join('');
  const axis = months.map((m) => `<span${m === last ? ' class="last"' : ''}>${m.endsWith('-01') || m === months[0] ? `<em>${m.slice(0,4)}</em>` : ''}${Number(m.slice(5))}${m === last ? '월' : ''}</span>`).join('');
  const pills = MX_LIMS.map(([v, t]) => `<button type="button" class="rt-pill" data-mxlim="${v}" aria-pressed="${v === lim}">${pct(v,0)} ${t}</button>`).join('');
  return `<section class="chart-card panel rt-card" aria-labelledby="composition-title"><div class="panel-heading"><div><h2 id="composition-title"><b class="step-no num">3</b>준비금 보고서 ${reports.length}건 비교</h2><div class="rt-pills" role="group" aria-label="은행 예금 기준">${pills}</div><p>한국 의원안 10건 중 2건은 은행 예금 비율을 대통령령에 맡겼고, 1건(정태호 안)은 자산별 구성비율을 금융위원회 고시에 맡겼고, 7건은 정하지 않아, 법에 정해진 숫자는 없습니다. 위 단추로 기준을 고르면 그 기준에 못 미친 보고서가 굵은 띠로 바뀝니다. 칸을 누르면 그 보고서로 판정합니다.</p><p class="rt-sum">전체 ${reports.length}건 중 은행 예금이 ${limTxt} 미만인 보고서 <b class="num">${fails}건</b>, 서명까지 ${dayLim}일을 넘긴 보고서 <b class="num">${lates}건</b></p></div></div><div class="mx-wrap"><div class="rt-grid"><span class="rt-cap">준비금 구성(최근 달)</span><div class="rt-axis">${axis}</div><span class="rt-cap r">미달 / 판정</span><span class="rt-cap r">최근 은행 예금</span>${rows}</div></div><div class="chart-foot"><span class="legend rt-legend"><span><i class="rt-k line"></i>은행 예금 ${limTxt} 이상</span><span><i class="rt-k band"></i>${limTxt} 미만</span><span><i class="rt-k gap"></i>보고서가 없거나 은행 예금을 알 수 없는 달</span><span><i class="rt-k late"></i>서명 ${dayLim}일 초과</span></span></div></section>`;
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
// 한국 규칙은 후보값(의원안 값마다, 해외 참조, 보도)이 범위라서, 한 보고서를 후보마다 판정해 같이 보인다
// tone: 판정이 난 후보가 모두 같으면 그 판정, 갈리면 split. 숫자 없는 후보(위임 등)는 none
const candFmt = (rid, x) => (rid === 'R01' || rid === 'R05') ? pct(x, Number.isInteger(Math.round(x * 10000) / 100) ? 0 : 1) : fmt(rid, x); // 후보값은 15%, 100%처럼 짧게
const CAND_SHORT = { bill: '법안', foreign_ref: '해외 참조', press: '보도' };
// 후보 짧은 이름: 법안 후보는 이름의 '법안 10건 중 N건'에서 건수를 따고, 숫자 기준이 없으면 괄호 첫 낱말(검토, 감사)을 붙임
const candShort = (c) => {
  if (!c.id.startsWith('bill')) return CAND_SHORT[c.id] || c.id;
  const n = c.label?.match(/법안 10건 중 (\d+)건/)?.[1], kind = c.label?.match(/\((검토|감사)[:)]/)?.[1];
  return `법안${n ? ` ${n}건` : ''}${kind ? `(${kind})` : ''}`;
};
const TONE_COL = { met: 'var(--ok)', unmet: 'var(--bad)', caution: 'var(--warn)', split: 'var(--warn)', none: 'var(--muted)' };
const TONE_TXT = { met: 'var(--ok-text)', unmet: 'var(--bad-text)', caution: 'var(--warn-text)', split: 'var(--warn-text)', none: 'var(--ink)' };
const TONE_NOTE = { met: '후보 모두 충족', unmet: '후보 모두 미충족', caution: '후보 모두 주의', split: '후보에 따라 갈림', none: '판정할 후보 없음' };
function krCands(rid, r = reports[state.reportIndex]) {
  const e = jurisdictions['kr-v1'].rules[rid];
  if (!e?.candidates?.length) return null;
  const cur = state.candidates[rid] || e.default_candidate || e.candidates[0].id;
  const list = e.candidates.map((c) => { const v = evaluateRule(rid, r, jurisdictions['kr-v1'], c.id); return { id: c.id, short: candShort(c), status: statusClass(v.status), threshold: typeof v.threshold === 'number' ? v.threshold : null, value: v.value, cur: c.id === cur }; });
  const set = new Set(list.map((c) => c.status).filter((s) => s !== 'none'));
  return { rid, list, tone: !set.size ? 'none' : set.size === 1 ? [...set][0] : 'split', value: list.find((c) => typeof c.value === 'number')?.value ?? null };
}
// 숫자 규칙의 범위 그림: 후보 최소~최대 띠, 후보 눈금과 이름, 보고서 값 점. 숫자 후보가 없으면 빈 글
function candStrip(k) {
  const nums = k?.list.filter((c) => c.threshold != null);
  if (!nums?.length || typeof k.value !== 'number') return '';
  const vals = [...new Set(nums.map((c) => c.threshold))].sort((a, b) => a - b), lo0 = vals[0], hi0 = vals.at(-1), v = k.value, cov = k.rid === 'R01';
  const lo = cov ? Math.min(v, lo0) - hi0 * 0.04 : 0, hi = Math.max(v, hi0) * (cov ? 1.03 : 1.15), X = (x) => Math.max(0, Math.min(100, ((x - lo) / (hi - lo)) * 100));
  const anchor = (x) => x > 72 ? 'transform:translateX(-100%)' : x < 20 ? '' : 'transform:translateX(-50%)';
  const ticks = vals.map((x) => { const ids = nums.filter((c) => c.threshold === x), txt = `${ids.length > 2 ? `후보 ${ids.length}건` : ids.map((c) => c.short).join(', ')} ${candFmt(k.rid, x)}`; const pick = ids.find((c) => c.cur) || ids[0]; return `<i class="r-tick" style="left:${X(x).toFixed(1)}%"></i><button type="button" class="r-lab${pick.cur ? ' cur' : ''}" data-kcand="${k.rid}:${pick.id}" aria-pressed="${pick.cur}" title="이 후보값으로 판정" style="left:${X(x).toFixed(1)}%;${anchor(X(x))}">${esc(txt)}</button>`; }).join('');
  return `<span class="kk-rng"><i class="r-track"></i>${hi0 > lo0 ? `<i class="r-band" style="left:${X(lo0).toFixed(1)}%;width:${(X(hi0) - X(lo0)).toFixed(1)}%"></i>` : ''}${ticks}<i class="r-dot" style="left:${X(v).toFixed(1)}%;background:${TONE_COL[k.tone]}"></i></span>`;
}
const candNote = (k) => { const none = k.list.filter((c) => c.status === 'none').map((c) => c.short); return `${TONE_NOTE[k.tone]}${none.length && none.length < k.list.length ? `, ${none.join(', ')}은 판정 안 됨` : ''}`; };
// 4단계 히트맵 한국 칸: 규칙마다 후보별 판정 [{ n: 이름, s: 판정 }]
const krSplitMap = () => Object.fromEntries(RULE_IDS.map((rid) => { const k = krCands(rid); return [rid, k?.list.length > 1 ? k.list.map((c) => ({ n: `${c.short}${c.threshold != null ? ` ${candFmt(rid, c.threshold)}` : ''}`, s: c.status })) : null]; }));
// 2단계 칸 위 숫자 셋
function krKpi() {
  const ms = Z1.metrics({ data: buildData(reports, jurisdictions, state.candidates), ri: state.reportIndex, lim: krLim(), dayLim: krDayLim() ?? 30 });
  const RID = { bank: 'R05', days: 'R10', cov: 'R01' }, name = { bank: '은행 예금', days: '기준일부터 서명까지', cov: '커버리지' };
  return `<div class="kr-kpi" role="list">${ms.map((m) => {
    const k = krCands(RID[m.key]);
    return `<div class="kk" role="listitem"><div class="kk-a"><span class="kk-l">${name[m.key]}</span><b class="kk-v num" style="color:${TONE_TXT[k.tone]}">${esc(m.disp)}<small>${m.v == null ? '' : m.unit}</small></b></div><div class="kk-b">${candStrip(k)}<span class="kk-n">${candNote(k)}</span></div></div>`;
  }).join('')}</div>`;
}
function krFindings(kr) {
  const line = (cls, name, list) => list.length ? `<p class="kr-find"><span class="kr-find-key ${cls}">${sw(cls)}${name}</span>${list.map((v) => `${ruleName(v.rule)}${v.value != null ? `: ${esc(valueText(v))}` : ''}`).join(' / ')}</p>` : '';
  return line('unmet', '미충족', kr.filter((v) => v.status === STATUS.UNMET)) + line('caution', '주의', kr.filter((v) => v.status === STATUS.CAUTION));
}
const COL_LABEL = { 'eu-emt':'EU<br>일반', 'eu-emt-significant':'EU<br>중요' };
// ---- 판정 흐름: 7개 나라 x 규칙 15개 = 판정 105건을 나라, 판정 결과, 규칙 세 축으로 이음 ----
const FLOW_RULES = GROUPS.flatMap(([, ids]) => ids);
// 4단계 나라별 판정: 같은 판정 105건을 히트맵과 판정 수 표(기본), 흐름(생키) 두 가지로 본다. 범례는 그림마다 붙는다
function verdictSection() {
  const rows = ['kr-v1', ...FOREIGN_IDS].flatMap((id) => {
    const by = Object.fromEntries(judged(id).map((v) => [v.rule, v]));
    return FLOW_RULES.map((rule) => ({ country: id, countryName: id === 'kr-v1' ? '한국' : SHORT[id], rule, ruleName: copy.규칙15개[rule], status: statusClass(by[rule].status) }));
  });
  const opt = { focus: 'kr-v1' };
  lastFlow = { rows, opt };
  const k = state.viz[4] === 'flow' ? 'flow' : '02';
  const body = k === 'flow' ? `<div class="flow-scroll">${flowSvg(rows, { ...opt, width: flowW })}</div><div class="chart-foot">${statusLegend()}</div>` : `<div class="vz-body">${vizViews(4).find((v) => v.key === k)?.html || ''}</div>`;
  return `<section class="rl-section panel hm-sec flow-section" aria-labelledby="rl-title"><div class="section-head"><div><h2 id="rl-title"><b class="step-no num">4</b>나라별 판정</h2><p>한국 후보값으로 먼저 판정하고, 같은 보고서를 해외 ${FOREIGN_IDS.length}곳의 규칙에도 맞춰 봅니다. 나라 7곳의 규칙 ${RULE_IDS.length}개 판정 ${rows.length}건이고, 나라 이름을 누르면 상세 화면으로 갑니다.</p><p class="rl-note">EU 일반과 EU 중요는 나라가 아니라 EU 규칙(MiCA)의 토큰 단계입니다. EU 중요는 유럽은행감독청이 이용자와 발행 규모가 커서 대형으로 지정한 토큰이고, 은행 예금 60% 이상, 6개월마다 감사처럼 규칙이 더 셉니다. 판정 안 됨은 보고서에 없음, 해당 없음, 규정 없음, 위임 예정, 조사 미완료를 묶은 것입니다.</p></div></div><div class="vz" data-vz="4">${vzTabs(4, [['02', '히트맵과 표'], ['flow', '흐름']], k)}${body}</div>${flowTotals(rows, opt)}</section>`;
}
// ---- 개요 지구본 위 유리 카드: 선택 보고서의 판정 수를 나라 옆에 보여 줌 ----
const tally = (id) => { const n = { met:0, caution:0, unmet:0, none:0 }; judged(id).forEach((v) => n[statusClass(v.status)]++); return n; };
const CARD_NAMES = { met:'충족', caution:'주의', unmet:'미충족', none:'판정 안 됨' };
const miniCounts = (n) => ['met','caution','unmet'].map((k) => `<span class="gc-n">${sw(k)}<b class="num">${n[k]}</b><span class="sr">${CARD_NAMES[k]}</span></span>`).join('');
function heroCards() {
  const one = (gid, id, name) => `<a class="gc" data-gc="${gid}" href="#${id}" data-country="${id}"><span class="gc-name">${name}</span><span class="gc-row">${miniCounts(tally(id))}</span></a>`;
  const eu = (id, name) => `<a class="gc-line" href="#${id}" data-country="${id}"><span class="gc-sub">${name}</span><span class="gc-row">${miniCounts(tally(id))}</span></a>`;
  return one('us', 'us', '미국') + one('hk', 'hk', '홍콩') + one('sg', 'sg', '싱가포르') + one('jp', 'jp', '일본')
    + `<div class="gc" data-gc="eu"><span class="gc-name">EU</span>${eu('eu-emt', '일반')}${eu('eu-emt-significant', '중요')}</div>`;
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
  return `<div class="home"><div class="hero"><div class="home-head"><div><h1>원화 스테이블코인 준비금 공시 검증 시스템</h1><p class="lead">발행사가 공개한 준비금 검증 보고서 한 건을 한국 후보 기준 ${RULE_IDS.length}개로 점검하고, 같은 보고서를 해외 기준에도 맞춰 봅니다.</p><ol class="steps">${[['report', '보고서'], ['kr', '한국 기준'], ['compare', `${reports.length}건 비교`], ['flow', '해외 기준'], ['rules', '기준값']].map(([k, t], i) => `<li><button type="button" class="step-btn" data-jump="${k}"><b class="num">${i + 1}</b>${t}</button></li>`).join('')}</ol><p class="report-line"><b class="step-no num">1</b>판정 보고서 ${esc(label(r))} / 기준일 ${esc(r.as_of)} / 검증인 ${esc(own)} / 보고서 ${state.reportIndex+1} / ${reports.length}</p></div></div>
    <div class="hero-globe"></div><div class="hero-main">
      <section class="result panel" aria-labelledby="result-title"><div class="section-head"><div><h2 id="result-title"><b class="step-no num">2</b>한국 기준 판정 결과</h2><p>한국 후보값은 확정된 규정이 아닙니다</p></div><a class="link-more" href="#kr-v1" data-country="kr-v1">후보값 바꾸기 →</a></div>${krKpi()}<div class="result-body">${vizBlock(2, { dense: true })}<div class="kr-finds">${krFindings(kr)}</div></div></section>
    </div></div>
    ${chartReports()}
    ${vzPanel(3, '<b class="step-no num">3</b>기준별 미달 보고서 수', '은행 예금 기준을 해외 값인 30%, 50%, 60%로 둘 때 코인마다 기준에 못 미친 보고서 수입니다. 한국 의원안 10건에는 이 비율 숫자가 없습니다. 기준을 올리면 어느 코인이 새로 떨어지는지 봅니다.')}
    ${verdictSection()}
    <div class="vz-pair vz-32">${vzPanel(6, '<b class="step-no num">5</b>규칙별 기준값 비교', '한국 의원안 10건과 해외 6곳의 기준값입니다. 숫자가 없는 칸은 위임이나 미규정입니다.')}${vzPanel(7, '<b class="step-no num">5</b>숫자 규칙 분포', '기준값을 어디에 두느냐에 따라 보고서 273건 중 몇 건이 통과하는지 봅니다.')}</div>
    <div class="disclosure"><strong>${KR_NOTICE}</strong><br>${foreignNames()} 판정: ${FOREIGN_NOTICE}</div>${rulesDock()}</div>`;
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
  // 규칙 15개 모두: 후보가 둘 이상이면 고르는 단추, 하나면 고정 표시, 없으면 법안 10건에 정함이 없다고 적음
  const rows = RULE_IDS.map((rid) => {
    const cs = rules[rid]?.candidates || [];
    const opts = cs.length > 1 ? candOpts(rid, 'kc') : cs.length ? `<span class="cand-opts"><span class="cand-fixed">${esc(cs[0].label)}</span></span>` : `<span class="cand-opts"><span class="cand-fixed none">법안 ${(rules[rid]?.bills || []).length || 10}건 모두 정함 없음</span></span>`;
    return `<div class="cand-row"><span class="cand-rule"><b>${rid}</b>${esc(copy.규칙15개[rid])}</span>${opts}</div>`;
  }).join('');
  return `<section class="cand-panel"><div class="cand-head"><strong>한국 후보값</strong><span>규칙 ${RULE_IDS.length}개에 대한 국회 의원안 10건의 값입니다. 법안마다 값이 다른 규칙은 눌러서 바꾸면 아래 판정이 바로 바뀝니다. ${KR_NOTICE}</span></div>${rows}</section>`;
}
// 한국 페이지 규칙 줄 아래: 후보가 둘 이상이면 후보마다 판정. 숫자 규칙은 범위 그림도
function krCandLine(rid) {
  const k = krCands(rid);
  if (!k || k.list.length < 2) return '';
  const chips = k.list.map((c) => `<button type="button" class="kc${c.cur ? ' cur' : ''}" data-kcand="${rid}:${c.id}" aria-pressed="${c.cur}" title="${esc(c.cur ? '지금 판정에 쓰는 후보' : '이 후보값으로 판정')}">${sw(c.status)}${esc(c.short)}${c.threshold != null ? ` ${esc(candFmt(rid, c.threshold))}` : ''}</button>`).join('');
  return `<div class="kr-cand-line"><span class="kc-note" style="color:${TONE_TXT[k.tone]}">${TONE_NOTE[k.tone]}</span>${chips}${candStrip(k)}</div>`;
}
function ruleItem(id,v) {
  const open = state.openRule === v.rule;
  return `<article class="rule-item ${open ? 'open' : ''}"><button type="button" data-rule="${v.rule}" class="rule-heading" aria-expanded="${open}" aria-controls="body-${v.rule}"><span class="rule-code">${v.rule}</span><span class="rule-title">${esc(copy.규칙15개[v.rule])}</span><span class="rule-vals num">${v.value != null && typeof v.value !== 'boolean' ? `${esc(fmt(v.rule,v.value))}${v.approx ? '*' : ''}` : ''}${v.threshold != null && typeof v.threshold !== 'boolean' && v.rule !== 'R02' ? `<small>기준 ${esc(fmt(v.rule,v.threshold))}</small>` : ''}</span><span class="status ${statusClass(v.status)}" title="${esc(statusTitle(v))}">${sw(statusClass(v.status))}${esc(statusLabel(v))}</span><span class="chevron" aria-hidden="true"></span></button>${id === 'kr-v1' ? krCandLine(v.rule) : ''}${open ? `<div class="rule-body" id="body-${v.rule}">${ruleBody(id,v)}</div>` : ''}</article>`;
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
function weeklyPane() {
  const max = Math.max(...weekly.주간.map((row) => row.준비금));
  return `<div class="weekly"><p class="weekly-warning">회계법인 확인이 없는 회사 자체 공시</p><p>${esc(weekly.발행사)}의 ${esc(weekly.코인)} 주간 명세 ${weekly.주간.length}주치. ${esc(weekly.기준)}. 단위: ${esc(weekly.단위)}. ${esc(weekly.준비금구성)}.</p><table><thead><tr><th scope="col">기준일</th><th scope="col">유통량</th><th scope="col">준비금</th><th scope="col">규모 비교</th></tr></thead><tbody>${weekly.주간.map((row) => `<tr><td>${esc(row.기준일)}</td><td>${count(row.유통량)}</td><td>${count(row.준비금)}</td><td><div class="weekly-bars" role="img" aria-label="${esc(row.기준일)} 준비금 ${row.준비금}, 유통량 ${row.유통량} ${esc(weekly.단위)}"><i style="width:${row.준비금/max*100}%"></i><b style="width:${row.유통량/max*100}%"></b></div></td></tr>`).join('')}</tbody></table><div class="legend"><span><i class="bar"></i>준비금</span><span><i class="bar ink"></i>유통량</span></div><p>${esc(weekly.주석)}. 이 값은 판정 엔진에 넣지 않습니다.</p></div>`;
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
    let v = tileValue(rid, d), tag = d.mandatory === false || d.legal_status === '협의 중' ? '협의 중' : '', note = '';
    // 한국은 의원안 후보(법안 값마다)만으로 최소~최대를 보이고 몇 건인지 적음. 해외 참조, 보도는 한국 값이 아니라서 넣지 않음
    const bills = id === 'kr-v1' ? (jur.rules[rid]?.candidates || []).filter((c) => c.id.startsWith('bill')) : [];
    if (bills.length) {
      const vs = bills.map((c) => ({ c, v: tileValue(rid, resolveRuleDef(jur, rid, c.id) || {}) })), nums = vs.filter((x) => x.v && typeof x.v[0] === 'number');
      const cnt = bills.reduce((n, c) => n + Number(c.label?.match(/법안 10건 중 (\d+)건/)?.[1] || 0), 0);
      tag = '의원안';
      if (nums.length) {
        const ns = [...new Set(nums.map((x) => x.v[0]))].sort((x, y) => x - y), sfx = new Set(nums.map((x) => x.v[1]));
        v = [ns.length > 1 ? `${ns[0]}~${ns.at(-1)}` : ns[0], sfx.size === 1 ? nums[0].v[1] : nums[0].v[1].replace('영업일', '일')];
        note = cnt ? `10건 중 ${cnt}건${ns.length > 1 ? `, 법안마다 다름` : ''}` : '';
      } else if (typeof v?.[0] !== 'string') { v = null; note = ''; } else note = cnt ? `10건 중 ${cnt}건` : '';
    }
    const val = v ? `<strong${/^[\d.~]+$/.test(String(v[0])) ? ' class="num"' : ''}>${esc(v[0])}</strong>${v[1] ? `<small>${esc(v[1])}</small>` : ''}${note ? `<em class="kt-n">${esc(note)}</em>` : ''}` : `<em>${d.delegated ? '아직 안 정함' : '정함 없음'}</em>`;
    return `<div class="kpi-t" title="${esc([d.requirement, d.label].filter(Boolean).join(' / '))}"><span>${name}${tag ? `<i>${tag}</i>` : ''}</span><p>${val}</p></div>`;
  }).join('')}</div>`;
}
function glance(info, id) {
  const law = (info.핵심 || []).find((x) => x.항목 === '법');
  return `${law ? `<div class="gl-law"><div class="gl-val"><strong>${esc(law.값)}</strong>${law.설명 ? `<span>${esc(law.설명)}</span>` : ''}</div>${stageSteps(id)}</div>` : ''}${tiles(id)}<p class="eli-line">${esc(info.한줄 || info.설명)}</p>`;
}
// ---- 나라 화면 아래 '다른 나라와 비교': 같은 보고서를 이 나라와 고른 나라 기준으로 나란히 ----
// 나라 화면 비교 탭의 보고서 273건: 첫 화면 3번과 같은 띠 그림. 코인마다 두 줄(위 기준 나라, 아래 비교 나라)
// 띠는 '은행 예금 최저 비율' 미충족(옅은 띠는 주의), 선은 충족, 점선은 판정 안 됨이나 보고서 없는 달, ▼는 기준 나라 '공개 기한' 초과
function chartVerdictBands(own, cmp) {
  const nm = (k) => copy.나라[k].이름, months = [...new Set(reports.map((r) => r.month))].sort(), n = months.length, last = months[n - 1];
  const P = (v) => `${(v * 100).toFixed(4).replace(/\.?0+$/, '')}%`, at = (i, w = 1) => `left:${P(i / n)};width:${P(w / n)}`;
  const st = (id, rid, r) => statusClass(evaluateRule(rid, r, jurisdictions[id], candOf(id, rid)).status);
  let nDiff = 0, nBoth = 0;
  const rows = [...new Set(reports.map((r) => r.token))].map((tok) => {
    const se = series[tok], mine = reports.flatMap((x, i) => x.token === tok ? [i] : []), latest = reports[mine.at(-1)];
    const cells = months.map((m) => {
      const i = mine.find((k) => reports[k].month === m);
      if (i == null) return se && m < se.first_month ? null : { i: null };
      const r = reports[i], a = st(own, 'R05', r), b = st(cmp, 'R05', r);
      if (a !== 'none' && b !== 'none') { nBoth++; if (a !== b) nDiff++; } // 갈림은 두 나라 모두 판정이 났을 때만
      return { i, a, b, late: st(own, 'R10', r) === 'unmet' };
    });
    let track = '';
    const line = (key, cls) => cells.forEach((c, j) => {
      if (!c) return;
      const s = c.i == null ? 'none' : c[key];
      if (s === 'met') track += `<i class="rt-line ${cls}" style="${at(j)}"></i>`;
      else if (s === 'none') track += `<i class="rt-gap ${cls}" style="${at(j)}"></i>`;
      else if (cells[j - 1]?.[key] !== s || cells[j - 1]?.i == null) { let e = j; while (cells[e + 1] && cells[e + 1].i != null && cells[e + 1][key] === s) e++; track += `<i class="rt-band ${cls}${s === 'caution' ? ' ca' : ''}" style="${at(j, e - j + 1)}"></i>`; }
    });
    line('a', 'up'); line('b', 'dn');
    cells.forEach((c, j) => {
      if (!c || c.i == null) return;
      const r = reports[c.i], sel = state.reportIndex === c.i, L = { met: '충족', caution: '주의', unmet: '미충족', none: '판정 안 됨' };
      const t = `${label(r)}: 은행 예금 ${bankInfo(r).ratio == null ? '구분 안 됨' : pct(bankInfo(r).ratio, 1)}, ${nm(own)} ${L[c.a]}, ${nm(cmp)} ${L[c.b]}, 서명까지 ${days(r) ?? '자료 없음'}일${c.late ? `, ${nm(own)} 공개 기한 넘김` : ''}`;
      if (c.late) track += `<i class="rt-late up" style="left:${P((j + 0.5) / n)}"></i>`;
      track += `<button type="button" class="rt-c${sel ? ' selected' : ''}" style="${at(j)}" data-report="${c.i}" aria-pressed="${sel}" aria-label="${esc(t)}" title="${esc(t)}"></button>`;
    });
    const cnt = (key) => cells.filter((c) => c?.[key] === 'unmet').length, judgedN = cells.filter((c) => c?.i != null).length;
    const mineTag = latest.home?.includes(own) ? '<small>이 나라 발행사</small>' : '';
    return `<div class="rt-head"><strong>${esc(coin(latest))}</strong>${mineTag}</div><div class="rt-track two">${track}</div><div class="rt-n num"><b>${cnt('a')}</b>/${judgedN}</div><div class="rt-n num"><b>${cnt('b')}</b>/${judgedN}</div>`;
  }).join('');
  const axis = months.map((m) => `<span${m === last ? ' class="last"' : ''}>${m.endsWith('-01') || m === months[0] ? `<em>${m.slice(0,4)}</em>` : ''}${Number(m.slice(5))}${m === last ? '월' : ''}</span>`).join('');
  return `<div class="cp-block rt-card"><h3>준비금 보고서 ${reports.length}건을 ${esc(wa(nm(own)))} ${esc(nm(cmp))} 기준으로</h3><p>'${ruleName('R05')}' 판정입니다. 코인마다 위 줄이 ${esc(nm(own))}, 아래 줄이 ${esc(nm(cmp))}입니다. ${nBoth ? `두 나라 모두 판정이 난 보고서 ${nBoth}건 중 ${nDiff}건에서 판정이 갈립니다.` : '두 나라 중 한쪽은 이 규칙의 판정이 나오지 않아(위임, 정함 없음 등) 판정을 견줄 수 없습니다.'} 칸을 누르면 그 보고서로 판정합니다.</p><div class="mx-wrap"><div class="rt-grid"><span class="rt-cap">코인</span><div class="rt-axis">${axis}</div><span class="rt-cap r">${esc(nm(own))} 미충족</span><span class="rt-cap r">${esc(nm(cmp))} 미충족</span>${rows}</div></div><div class="chart-foot"><span class="legend rt-legend"><span><i class="rt-k line"></i>충족</span><span><i class="rt-k band"></i>미충족</span><span><i class="rt-k band ca"></i>주의</span><span><i class="rt-k gap"></i>판정 안 됨이나 보고서 없는 달</span><span><i class="rt-k late"></i>${esc(nm(own))} 공개 기한 넘김</span></span></div></div>`;
}
function compareSection(id) {
  const others = ORDER.filter((k) => k !== id), nm = (k) => copy.나라[k].이름;
  const cmp = others.includes(state.cmp) ? state.cmp : id === 'kr-v1' ? 'us' : 'kr-v1';
  const a = Object.fromEntries(judged(id).map((v) => [v.rule, v])), b = Object.fromEntries(judged(cmp).map((v) => [v.rule, v]));
  const differs = (rid) => statusClass(a[rid].status) !== statusClass(b[rid].status), nDiff = FLOW_RULES.filter(differs).length;
  const cell = (k, v) => { const t = `${nm(k)}, ${v.rule} ${copy.규칙15개[v.rule]}: ${statusLabel(v)}`; return `<i class="hm-c ${statusClass(v.status)}" title="${esc(t)}"><span class="sr">${esc(t)}</span></i>`; };
  const row = (k, by) => `<span class="cp-name">${esc(nm(k))}</span>${FLOW_RULES.map((rid) => cell(k, by[rid])).join('')}`;
  const grid = `<div class="cp-grid"><span></span>${FLOW_RULES.map((rid) => `<span class="cp-rid${differs(rid) ? ' df' : ''}" title="${esc(copy.규칙15개[rid])}">${rid}</span>`).join('')}${row(id, a)}${row(cmp, b)}</div>`;
  const FL = { 'kr-v1': 'kr', us: 'us', 'eu-emt': 'eu', 'eu-emt-significant': 'eu', hk: 'hk', sg: 'sg', jp: 'jp' };
  const pick = `<div class="cp-pick"><span class="cp-base">기준 <b><img src="flags/${FL[id]}.svg" alt="">${esc(nm(id))}</b></span><span class="cp-vs">비교</span><span class="cp-btns" role="radiogroup" aria-label="비교할 나라">${others.map((k) => `<button type="button" role="radio" data-cmp="${k}" aria-checked="${k === cmp}"><img src="flags/${FL[k]}.svg" alt="">${esc(nm(k))}</button>`).join('')}</span></div>`;
  return `<section class="rl-section panel cp-section" aria-labelledby="cp-title"><div class="section-head"><div><h2 id="cp-title">다른 나라와 비교</h2><p>같은 보고서를 ${esc(nm(id))} 기준과 ${esc(nm(cmp))} 기준으로 나란히 봅니다.</p></div>${pick}</div>
    <div class="cp-block"><h3>두 나라 판정 비교</h3><p>선택 보고서 ${esc(label(reports[state.reportIndex]))}. 규칙마다 두 나라 판정과, 보고서 ${reports.length}건 중 판정이 갈린 수입니다.</p>${vizBlock(9, { cmp, focus: id })}</div>
    ${chartVerdictBands(id, cmp)}
    <div class="cp-block"><h3>숫자 규칙 분포</h3><p>${esc(wa(nm(id)))} ${esc(nm(cmp))}의 기준값만 진하게 보입니다.</p>${ruleDots(jurisdictions, copy, 600, [id, cmp], true)}</div>${id === 'hk' ? `<div class="cp-block"><h3>주간 준비금 명세 ${weekly.주간.length}주</h3>${weeklyPane()}</div>` : ''}</section>`;
}
function detail() {
  const id = state.jurisdiction, jur = jurisdictions[id], info = copy.나라[id], r = reports[state.reportIndex];
  const results = judged(id), met = results.filter((v) => v.status === STATUS.MET).length, unmet = results.filter((v) => v.status === STATUS.UNMET).length;
  const caution = results.filter((v) => v.status === STATUS.CAUTION).length, done = met + unmet + caution, none = RULE_IDS.length - done;
  const links = [...new Map(Object.values(jur.rules).filter((d) => safeLink(d.url)).map((d) => [safeLink(d.url), d.article || d.requirement])).entries()].slice(0,5);
  const own = ownIndices(id);
  const notes = [
    !own.length ? FOREIGN_NOTICE : !own.includes(state.reportIndex) ? '선택한 보고서는 이 나라 발행사의 보고서가 아닙니다.' : '',
    id === 'kr-v1' ? KR_NOTICE : '',
    id === 'jp' ? JP_NOTICE : '',
  ].filter(Boolean);
  const tabs = `<div class="detail-tabs top" role="tablist" aria-label="상세 내용">${[['rules', `규칙 ${RULE_IDS.length}개`], ['compare', '다른 나라와 비교']].map(([k, t]) => `<button type="button" role="tab" data-tab="${k}" aria-selected="${state.tab === k}" tabindex="0">${t}</button>`).join('')}</div>`;
  const body = state.tab === 'compare' ? compareSection(id) : `<div class="detail-layout"><section class="identity-card panel" aria-label="${esc(info.이름)} 개요"><div class="globe"></div><div class="identity-top"><div class="identity-name"><h1>${esc(info.이름)}</h1><div class="legal">법적 상태<strong>${esc(jur.legal_status)}</strong></div></div></div><div><div class="score"><strong class="num">${met}<small>/ ${done}</small></strong><span>판정된 규칙 ${done}개 중 충족</span></div><div class="rule-grid" role="img" aria-label="규칙 ${RULE_IDS.length}개 판정: 충족 ${met}, 주의 ${caution}, 미충족 ${unmet}, 판정 안 됨 ${none}">${results.map((v) => `<span class="rg ${statusClass(v.status)}" title="${v.rule} ${esc(copy.규칙15개[v.rule])}: ${esc(statusLabel(v))}${notDisclosed(v) ? `, 판정 ${esc(v.status)}` : ''}. ${esc(ruleHelp(v.rule))}"><b>${v.rule}</b></span>`).join('')}</div>${statusLegend({met,caution,unmet,none})}</div><div class="eli"><div class="small-head">${esc(info.이름)} 한눈에</div>${glance(info, id)}</div>${notes.length ? `<div class="notes">${notes.map((n) => `<div class="comparison-note">${n}</div>`).join('')}</div>` : ''}${links.length ? `<div><div class="small-head">규제 원문</div><ul class="source-links">${links.map(([u,t]) => `<li><a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(t)}</a></li>`).join('')}</ul></div>` : ''}<div class="source-date">규칙 자료 기준일 ${esc(jur.as_of)} / 판정 보고서 기준일 ${esc(r.as_of)}</div></section><div class="detail-side">${isoSection(info, id)}<section class="detail-right panel" aria-label="${esc(info.이름)} 판정과 보고서"><div role="tabpanel">${rulesPane(id)}</div></section></div></div>`;
  return `<div class="detail"><div class="detail-head"><a href="#" class="back-link">← 종합 판정으로 돌아가기</a><span class="context">선택 보고서 ${esc(label(r))} / 기준일 ${esc(r.as_of)}</span></div>${tabs}${body}</div>`;
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
  if (w !== Number(box.dataset.w)) { box.dataset.w = w; box.innerHTML = ruleDotsPlots(jurisdictions, copy, w, box.dataset.focus ? box.dataset.focus.split(',') : null); }
}
function render() {
  if (!reports) return;
  const kept = $('#app .mx-wrap')?.scrollLeft; // 비교 격자를 옆으로 밀어 둔 자리는 다시 그려도 유지
  $('#app').innerHTML = state.jurisdiction ? detail() : state.rules ? rulesPage() : home();
  const mxw = $('#app .mx-wrap'); if (mxw) mxw.scrollLeft = kept ?? mxw.scrollWidth; // 좁은 화면에서 처음엔 최근 달이 보이게 오른쪽 끝에서 시작
  fitDots(); fitFlow(); fitViz();
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
    state.viz[4] = '02'; render(); // 규칙별 줄이 있는 히트맵 보기로
    document.querySelector('#app .hm-sec')?.scrollIntoView({ block: 'start' });
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
  const jump = e.target.closest('[data-jump]'); if (jump) {
    const k = jump.dataset.jump;
    if (k === 'report') { window.scrollTo({ top: 0, behavior: 'smooth' }); toggleReportPop(true); return; }
    document.querySelector({ kr: '#app .result', compare: '#app .chart-card', flow: '#app .rl-section.hm-sec', rules: '#app .vz-pair.vz-32' }[k])?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    return;
  }
  const kcd = e.target.closest('[data-kcand]'); if (kcd) { const [rid, cid] = kcd.dataset.kcand.split(':'); state.candidates[rid] = cid; if (rid === 'R05') state.mxLim = undefined; const y = window.scrollY; render(); window.scrollTo({ top: y, behavior: 'instant' }); return; }
  const vzv = e.target.closest('[data-vzview]'); if (vzv) { const [n, k] = vzv.dataset.vzview.split(':'); state.viz[n] = k; const y = window.scrollY; render(); window.scrollTo({ top: y, behavior: 'instant' }); return; }
  const cmpBtn = e.target.closest('[data-cmp]'); if (cmpBtn) { state.cmp = cmpBtn.dataset.cmp; const y = window.scrollY; render(); window.scrollTo({ top: y, behavior: 'instant' }); return; }
  const mxLim = e.target.closest('[data-mxlim]'); if (mxLim) { state.mxLim = Number(mxLim.dataset.mxlim); const y = window.scrollY; render(); window.scrollTo({ top: y, behavior: 'instant' }); return; }
  const report = e.target.closest('[data-report]'); if (report) return selectReport(Number(report.dataset.report));
  const country = e.target.closest('[data-country]'); if (country) return selectJurisdiction(country.dataset.country);
  const tab = e.target.closest('[data-tab]'); if (tab) {const next = tab.dataset.tab; if (next !== state.tab) window.location.hash = `#${state.jurisdiction}${next === 'rules' ? '' : `/${next}`}`;return;}
  const fold = e.target.closest('[data-action="toggle-rules"]'); if (fold) { state.showAll = !state.showAll; if (!state.showAll && ![STATUS.MET,STATUS.UNMET,STATUS.CAUTION].includes(judged(state.jurisdiction).find((v) => v.rule === state.openRule)?.status)) state.openRule = null; render(); return; }
  const rule = e.target.closest('[data-rule]'); if (rule) {state.openRule = state.openRule === rule.dataset.rule ? null : rule.dataset.rule; render(); return;}
});
$('#app').addEventListener('change',(e) => {
  if (e.target.matches('[data-candidate]')) {
    state.candidates[e.target.dataset.candidate] = e.target.value;
    if (e.target.dataset.candidate === 'R05') state.mxLim = undefined;
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
bindSidebar($('#side'));
bindFlow($('#app'));
window.addEventListener('hashchange',route);
window.addEventListener('resize',() => { fitDots(); fitFlow(); fitViz(); });
init();
