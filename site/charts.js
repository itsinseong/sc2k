// 차트 3종: 한국 요약 띠, 규칙 값 표(히트맵), 규칙 점 그래프.
// 전부 HTML 문자열을 돌려주는 순수 함수다. 값은 넘겨받은 객체에서만 읽는다.
import { STATUS } from './engine.js';

const RULES = ['R01','R02','R03','R04','R05','R06','R07','R08','R09','R10','R11','R12','R13','R14','R15'];
const FOREIGN = ['us', 'eu-emt', 'eu-emt-significant', 'hk', 'sg', 'jp'];
const FALLBACK_NAME = { us: '미국', 'eu-emt': 'EU 일반', 'eu-emt-significant': 'EU 중요', hk: '홍콩', sg: '싱가포르', jp: '일본' };
// app.js의 TYPE_NAMES와 같은 표기
const TYPE_NAMES = {cash:'현금',bank_deposit:'은행 예금',treasury_bill_93d:'93일 이하 국채',overnight_repo:'하루짜리 레포',government_mmf:'국채 펀드',overnight_reverse_repo:'하루짜리 역레포',approved_federal_asset:'감독기관 승인 연방정부 자산',tokenized_reserve:'토큰 형태 준비자산',cash_equivalent:'현금성 자산',government_bond_3m:'3개월 이하 국채',hqla:'고유동성 우량자산',bank_deposit_3m:'3개월 이내 은행 예금',low_risk_liquid_asset:'저위험 고유동성 자산',government_bond:'국채',other_designated:'그 밖의 지정 자산',examination:'검증 보고서',attestation:'확인 보고서',audit:'감사',quarterly_review:'분기 검토', 'reasonable assurance':'합리적 확신',demand_deposit_same_currency:'같은 통화 요구불 예금',term_deposit_principal_protected_cancellable_anytime:'원금 보전, 수시 해약 정기예금',jgb_remaining_le_3m_jpy_only:'3개월 이내 엔화 국채',foreign_bond_remaining_le_3m_same_currency:'3개월 이내 같은 통화 외국 채권'};
const tn = (k) => TYPE_NAMES[k] || k;
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const withNum = (s) => esc(s).replace(/(\d[\d.,~]*)/g, '<span class="rv-n">$1</span>');

// ---- 값 읽기 ----
const flat = (rule, id) => {
  if (!rule) return null;
  if (!rule.candidates) return rule;
  const c = rule.candidates.find((x) => x.id === id);
  return c ? { ...rule, ...c } : null;
};
const numeric = (d) =>
  typeof d.threshold === 'number' ? { k: 'gte', v: d.threshold }
  : typeof d.threshold_days === 'number' ? { k: 'td', v: d.threshold_days }
  : typeof d.deadline_days === 'number' ? { k: 'dl', v: d.deadline_days, unit: d.unit }
  : typeof d.max_days === 'number' ? { k: 'md', v: d.max_days, unit: d.unit }
  : null;
const strict = (n) => (n.k === 'gte' ? n.v : -n.v); // 클수록 엄격
const pn = (v) => Math.round(v * 1000) / 10;
const unitName = (u) => (u === 'business_days' ? '영업일' : '일');
function fmtNum(n, suffix = true, unit = n.unit) {
  const u = unitName(unit);
  if (n.k === 'gte') return `${pn(n.v)}%${suffix ? ' 이상' : ''}`;
  if (n.k === 'td') return `${n.v}일${suffix ? ' 이하' : ''}`;
  return `${n.v}${u}${suffix ? ' 안' : ''}`;
}
const expectedText = (d) => (d.expected === true ? '요구' : d.expected === false ? '금지' : null);
const TEXT = {
  R02: (d) => d.allowed && { t: `${d.allowed.length}종`, tip: `허용: ${d.allowed.map(tn).join(', ')}` },
  R06: (d) => d.required_currency && { t: d.required_currency === 'KRW' ? '원화' : '페그 통화 일치' },
  R07: (d) => d.cadence_days != null && { t: (/월별|주간|매월/.exec(`${d.requirement} ${d.label || ''}`) || [`${d.cadence_days}일마다`])[0] },
  R08: (d) => d.verification_types && { t: d.verification_types.map(tn).join(', ') },
  R09: (d) => d.time_label && { t: d.time_label.replace(/\(.*?\)/g, '').trim() },
};
// 한 규칙 정의 하나를 칸 내용으로 바꾼다. 판정 순서는 engine.js의 shortCircuit과 같다.
function describe(rid, d) {
  if (d.not_regulated) return { t: '미규정', muted: true };
  if (d.unresearched) return { t: '—', muted: true };
  if (d.delegated) return { t: '위임', muted: true };
  if (d.partial) return { t: '일부 규정', muted: true };
  const n = numeric(d);
  if (n) return { t: fmtNum(n), n, opt: d.mandatory === false };
  const x = (TEXT[rid] && TEXT[rid](d)) || (expectedText(d) && { t: expectedText(d) });
  return x ? { ...x, opt: d.mandatory === false } : { t: '—', muted: true };
}
const tipOf = (d, extra) => [d.requirement || d.label, d.label && d.requirement ? d.label : null, d.article, d.mandatory === false ? '의무 아님' : null, extra].filter(Boolean).join('\n');
const billWho = (b) => b.bill;
const billCount = (b) => String(b.bill).split(',').length;

// ---- 1. 한국 요약 ----
export function krSummary(results) {
  const c = { met: 0, caution: 0, unmet: 0, none: 0 };
  results.forEach((r) => { c[r.status === STATUS.MET ? 'met' : r.status === STATUS.CAUTION ? 'caution' : r.status === STATUS.UNMET ? 'unmet' : 'none']++; });
  const items = [['met', '충족'], ['caution', '주의'], ['unmet', '미충족'], ['none', '판정 안 됨']];
  const label = `한국 후보값으로 본 규칙 ${results.length}개: ${items.map(([k, n]) => `${n} ${c[k]}`).join(', ')}`;
  const nums = items.map(([k, n]) => `<div class="rv-sum-item"><strong class="rv-sum-n">${c[k]}</strong><span class="rv-sum-name"><i class="sw ${k}"></i>${n}</span></div>`).join('');
  const units = items.flatMap(([k]) => Array.from({ length: c[k] }, () => `<i class="hm-c ${k}"></i>`)).join('');
  return `<div class="rv-sum" role="img" aria-label="${esc(label)}"><p class="rv-sum-label">한국 후보값으로 본 규칙 ${results.length}개</p><div class="rv-sum-nums">${nums}</div><div class="rv-sum-bar" style="--rv-count:${results.length}">${units}</div></div>`;
}

// ---- 2. 규칙 값 표 ----
function foreignCell(rid, d) {
  if (!d) return { t: '자료 없음', tip: '', muted: true };
  const x = describe(rid, d);
  return { ...x, tip: tipOf(d, x.tip), rep: x.n ? strict(x.n) : null };
}
function billCell(rid, rule) {
  const d = flat(rule, 'bill');
  if (!d) return { t: '—', muted: true, tip: [rule.requirement, rule.note].filter(Boolean).join('\n') };
  const x = describe(rid, d), n = x.n;
  const bills = rule.bills;
  let t = x.t, star = false;
  const lines = [d.label, d.article].filter(Boolean);
  if (bills) {
    const val = (b) => {
      if (typeof b.value === 'number' && n) return fmtNum({ ...n, v: b.value }, false, b.unit);
      if (b.value != null) return String(b.value);
      return '숫자 없음';
    };
    lines.push('', ...bills.map((b) => `${billWho(b)}: ${val(b)}${b.note ? ` (${b.note})` : ''}${b.article ? `, ${b.article}` : ''}`));
    const nums = bills.filter((b) => typeof b.value === 'number');
    if (n && nums.length) {
      lines.splice(lines.length - bills.length - 1, 0, `숫자를 정한 법안 ${bills.length}건 중 ${nums.length}건`);
      const vs = nums.map((b) => b.value), lo = Math.min(...vs), hi = Math.max(...vs);
      const bd = nums.every((b) => b.unit === 'business_days');
      star = nums.length < bills.length;
      t = lo === hi ? fmtNum({ ...n, v: lo }, true, bd ? 'business_days' : 'days')
        : n.k === 'gte' ? `${pn(lo)}~${pn(hi)}%` : `${lo}~${hi}${bd ? '영업일' : nums.some((b) => b.unit === 'business_days') ? '일, 영업일 포함' : '일'}`;
    }
  }
  return { t, muted: x.muted, star, tip: lines.join('\n'), rep: n ? strict(n) : null };
}
function shadeRow(cells) {
  const vals = [...new Set(cells.map((c) => c && c.rep).filter((v) => v != null))].sort((a, b) => b - a); // 엄격한 순
  if (vals.length < 2) return;
  cells.forEach((c) => { if (c && c.rep != null) c.shade = Math.round(vals.indexOf(c.rep) * 2 / (vals.length - 1)); });
}
export function ruleTable(jurisdictions, copy) {
  const names = (id) => copy?.나라?.[id]?.이름 || FALLBACK_NAME[id];
  const kr = jurisdictions['kr-v1'].rules;
  const rows = RULES.map((rid) => {
    const foreign = FOREIGN.map((id) => foreignCell(rid, flat(jurisdictions[id]?.rules?.[rid])));
    const cells = [...foreign, billCell(rid, kr[rid])];
    shadeRow(cells);
    return { rid, cells };
  });
  const td = (c) => `<td class="rv-cell${c.shade != null ? ` rv-s${c.shade}` : ''}${c.muted ? ' rv-muted' : ''}" title="${esc(c.tip)}">${c.opt ? '<i class="rv-opt" aria-hidden="true"></i>' : ''}${withNum(c.t)}${c.star ? '<span class="rv-star">*</span>' : ''}</td>`;
  const body = rows.map(({ rid, cells }) => `<tr><th scope="row" class="rv-rule">${esc(copy?.규칙15개?.[rid] || '')}<span class="rv-code">${rid}</span></th>${cells.slice(FOREIGN.length).map(td).join('')}<td class="rv-gap" aria-hidden="true"></td>${cells.slice(0, FOREIGN.length).map(td).join('')}</tr>`).join('');
  const head = `<thead><tr class="rv-group"><th></th><th>한국</th><th class="rv-gap" aria-hidden="true"></th><th colspan="${FOREIGN.length}">해외 기준</th></tr><tr class="rv-cols"><th scope="col" class="rv-rule">규칙</th><th scope="col">한국 의원안</th><th class="rv-gap" aria-hidden="true"></th>${FOREIGN.map((id) => `<th scope="col">${esc(names(id))}</th>`).join('')}</tr></thead>`;
  const cols = `<colgroup><col class="rv-col-rule">${'<col>'}<col class="rv-col-gap">${'<col>'.repeat(FOREIGN.length)}</colgroup>`;
  const legend = `<div class="rv-legend"><span class="rv-leg-steps" aria-hidden="true"><i class="rv-s0"></i><i class="rv-s1"></i><i class="rv-s2"></i></span><span>숫자 규칙만, 진할수록 엄격</span><span><i class="rv-opt" aria-hidden="true"></i>의무 아님</span><span><span class="rv-star">*</span>숫자 없는 법안 있음</span><span>의원안 범위는 판정에 쓰는 값으로 칠함</span><span class="rv-swipe">좌우로 밀어서 보기</span></div>`;
  return `<section class="rv-card panel" aria-labelledby="rv-table-title"><div class="panel-heading"><div><h2 id="rv-table-title">규칙별 기준값 비교</h2><p>한국 의원안 값(법안 10건의 최소~최대)과 해외 ${FOREIGN.length}곳의 규칙값을 나란히 놓았습니다.</p></div></div><div class="rv-scroll"><table class="rv-table">${cols}${head}<tbody>${body}</tbody></table></div>${legend}</section>`;
}

// ---- 3. 규칙 점 그래프 ----
const DOT_RULES = ['R03', 'R05', 'R10', 'R13'];
const L = 84, ROW = 26;
const NICE = [1, 2, 5, 10, 20, 25, 50, 100, 200, 500];
const plotVal = (n) => (n.k === 'gte' ? pn(n.v) : n.v);
function plot(rid, jurisdictions, copy, W, focus = null) {
  const R = W - 34;
  const names = (id) => copy?.나라?.[id]?.이름 || FALLBACK_NAME[id];
  const rule = jurisdictions['kr-v1'].rules[rid];
  const pct = rid === 'R05';
  const rows = FOREIGN.map((id) => {
    const d = flat(jurisdictions[id]?.rules?.[rid]);
    if (!d) return { id, label: names(id), text: '자료 없음' };
    const x = describe(rid, d);
    if (!x.n) return { id, label: names(id), text: x.t };
    const bd = x.n.unit === 'business_days';
    const why = x.opt ? '의무 아님' : bd ? '영업일' : '';
    return { id, label: names(id), dots: [{ v: plotVal(x.n), hollow: !!why, why, n: 1, tip: `${names(id)}: ${fmtNum(x.n, false)}${x.opt ? ', 의무 아님' : ''}\n${d.article || d.requirement}` }], note: x.opt ? '의무 아님' : '' };
  });
  // 한국 의원안 행
  const bd0 = flat(rule, 'bill'), bx = bd0 && describe(rid, bd0);
  const krRow = { id: 'kr-v1', label: '한국 의원안', bold: true };
  if (rule.bills && bx?.n) {
    const nums = rule.bills.filter((b) => typeof b.value === 'number');
    const noNum = rule.bills.filter((b) => typeof b.value !== 'number').reduce((s, b) => s + billCount(b), 0);
    const groups = new Map();
    nums.forEach((b) => {
      const hollow = b.unit === 'business_days', key = `${b.value}|${hollow}`;
      const g = groups.get(key) || { v: plotVal({ ...bx.n, v: b.value }), hollow, why: hollow ? '영업일' : '', n: 0, who: [] };
      g.n += billCount(b); g.who.push(`${b.bill}: ${fmtNum({ ...bx.n, v: b.value }, false, b.unit)}${b.article ? `, ${b.article}` : ''}`);
      groups.set(key, g);
    });
    krRow.dots = [...groups.values()].map((g) => ({ ...g, tip: `한국 의원안 ${g.n}건\n${g.who.join('\n')}` }));
    krRow.sub = noNum ? `숫자 없음 ${noNum}건` : '';
    if (rid === 'R13' && nums.length) krRow.band = [Math.min(...krRow.dots.map((g) => g.v)), Math.max(...krRow.dots.map((g) => g.v))];
  } else if (bx?.n) {
    krRow.dots = [{ v: plotVal(bx.n), hollow: false, n: 1, tip: `한국 의원안: ${fmtNum(bx.n, false)}\n${bd0.article || bd0.label}` }];
  } else krRow.text = bx ? bx.t : '—';
  rows.push(krRow);
  // 축
  const all = rows.flatMap((r) => (r.dots || []).map((d) => d.v));
  const max = Math.max(...all);
  const step = NICE.find((s) => Math.ceil(max / s) <= 4) || NICE[NICE.length - 1];
  const dom = step * Math.ceil(max / step);
  const ticks = Array.from({ length: dom / step + 1 }, (_, i) => i * step);
  const X = (v) => L + (v / dom) * (R - L);
  // 세로 배치
  const top = 24;
  let y = top;
  const geo = rows.map((r) => {
    const stacked = r.dots && r.dots.some((d) => d.hollow) && r.dots.some((d) => !d.hollow && r.dots.some((e) => e.v === d.v && e.hollow));
    const h = stacked ? 44 : r.sub ? 34 : ROW;
    const g = { r, cy: y + h / 2, h, stacked };
    y += h;
    return g;
  });
  const axisY = y + 4, H = axisY + 22;
  const out = [];
  ticks.forEach((t) => out.push(`<line x1="${X(t)}" y1="${top - 2}" x2="${X(t)}" y2="${axisY}" stroke="var(--line)" stroke-width="1"/><text x="${X(t)}" y="${axisY + 15}" text-anchor="middle" font-size="11" fill="var(--muted)" class="rv-svg-num">${t}</text>`));
  out.push(`<text x="0" y="${axisY + 15}" text-anchor="start" font-size="11" fill="var(--muted)">(${pct ? '%' : '일'})</text>`);
  out.push(`<line x1="${L}" y1="${axisY}" x2="${R}" y2="${axisY}" stroke="var(--stone)" stroke-width="1"/>`);
  let hasBd = false, hasOpt = false;
  geo.forEach(({ r, cy, stacked }) => {
    const on = focus ? focus.includes(r.id) : r.bold, dim = focus && !on;
    out.push(dim ? '<g opacity=".28">' : '<g>');
    out.push(`<text x="0" y="${cy - (r.sub ? 4 : 0)}" dominant-baseline="central" font-size="12" ${on ? 'font-weight="650" fill="var(--ink)"' : 'fill="var(--ink-2)"'}>${esc(r.label)}</text>`);
    if (r.sub) out.push(`<text x="0" y="${cy + 10}" dominant-baseline="central" font-size="11" fill="var(--muted)">${esc(r.sub)}</text>`);
    if (r.text) { out.push(`<text x="${L + 6}" y="${cy}" dominant-baseline="central" font-size="11" fill="var(--muted)">${esc(r.text)}</text>`, '</g>'); return; }
    out.push(`<line x1="${L}" y1="${cy}" x2="${R}" y2="${cy}" stroke="var(--line)" stroke-width="1"/>`);
    if (r.band) out.push(`<rect x="${X(r.band[0])}" y="${cy - (stacked ? 16 : 9)}" width="${Math.max(X(r.band[1]) - X(r.band[0]), 1)}" height="${stacked ? 32 : 18}" fill="var(--pale)"/>`);
    r.dots.forEach((d) => {
      const dy = stacked && r.dots.some((e) => e !== d && e.v === d.v) ? (d.hollow ? 6 : -6) : 0;
      if (d.hollow) { d.why === '영업일' ? (hasBd = true) : (hasOpt = true); }
      out.push(`<circle cx="${X(d.v)}" cy="${cy + dy}" r="4" fill="${d.hollow ? '#fff' : 'var(--ink-fill)'}" stroke="var(--ink-fill)" stroke-width="1.5"><title>${esc(d.tip)}</title></circle>`);
      if (d.n > 1) out.push(`<text x="${X(d.v) + 8}" y="${cy + dy}" dominant-baseline="central" font-size="11" fill="var(--muted)">${d.n}건</text>`);
      else if (r.note) out.push(`<text x="${X(d.v) + 8}" y="${cy + dy}" dominant-baseline="central" font-size="11" fill="var(--muted)">${esc(r.note)}</text>`);
    });
    out.push('</g>');
  });
  const key = [
    `<span><i class="rv-key-dot"></i>${rid === 'R05' ? '의무 규정' : '일'}</span>`,
    hasBd ? '<span><i class="rv-key-dot hollow"></i>영업일</span>' : '',
    hasOpt ? '<span><i class="rv-key-dot hollow"></i>의무 아님</span>' : '',
    rid === 'R13' ? '<span><i class="rv-key-band"></i>의원안 범위</span>' : '',
  ].join('');
  const title = copy?.규칙15개?.[rid] || rid;
  const aria = `${title} (${rid})`;
  return `<figure class="rv-plot"><h3>${esc(title)}<small class="rv-code2">${rid}</small></h3><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(aria)}" style="width:100%;max-width:${W}px;height:auto;display:block" font-family="var(--sans)">${out.join('')}</svg><figcaption class="rv-key">${key}</figcaption></figure>`;
}
export const ruleDotsPlots = (jurisdictions, copy, W = 600, focus = null) => DOT_RULES.map((rid) => plot(rid, jurisdictions, copy, W, focus)).join('');
export function ruleDots(jurisdictions, copy, W = 600, focus = null, bare = false) {
  const plots = `<div class="rv-dots" data-w="${W}"${focus ? ` data-focus="${focus.join(',')}"` : ''}>${ruleDotsPlots(jurisdictions, copy, W, focus)}</div>`;
  if (bare) return plots;
  return `<section class="rv-card panel" aria-labelledby="rv-dots-title"><div class="panel-heading"><div><h2 id="rv-dots-title">숫자 규칙 분포</h2><p>점은 나라 하나 또는 같은 값을 정한 법안, 점 옆 건수는 그 법안 수</p></div></div>${plots}</section>`;
}
