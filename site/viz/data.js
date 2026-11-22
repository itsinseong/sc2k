// 새 차트(viz/*.js)가 같이 쓰는 데이터. prototype/chart-lab/dump.mjs와 같은 모양을 브라우저에서 만든다.
// buildData(reports, jurisdictions, krCandidates) -> { jurisdictions, ruleNames, thresholds, krCandidates, krBills, reports }
import { RULE_IDS, evaluateReport, calendarDaysBetween, resolveRuleDef } from '../engine.js';

export const ORDER = ['kr-v1', 'us', 'eu-emt', 'eu-emt-significant', 'hk', 'sg', 'jp'];
export const SHORT = { 'kr-v1': '한국', us: '미국', 'eu-emt': 'EU 일반', 'eu-emt-significant': 'EU 중요', hk: '홍콩', sg: '싱가포르', jp: '일본' };
export const FLAG = { 'kr-v1': 'kr', us: 'us', 'eu-emt': 'eu', 'eu-emt-significant': 'eu', hk: 'hk', sg: 'sg', jp: 'jp' };
// 국기 그림(사이트 flags/). x, y는 왼쪽 위, h는 높이(가로는 4:3), 흰 국기도 보이게 옅은 테두리
export const flagImg = (id, x, y, h) => FLAG[id] ? `<image href="flags/${FLAG[id]}.svg" x="${Math.round(x * 10) / 10}" y="${Math.round(y * 10) / 10}" width="${Math.round(h * 4 / 3 * 10) / 10}" height="${h}" preserveAspectRatio="xMidYMid slice"/><rect x="${Math.round(x * 10) / 10}" y="${Math.round(y * 10) / 10}" width="${Math.round(h * 4 / 3 * 10) / 10}" height="${h}" fill="none" stroke="var(--line)"/>` : '';
export const COL = { ink: 'var(--ink)', fill: 'var(--ink-fill)', muted: 'var(--muted)', line: 'var(--line)', surface: 'var(--surface)', ok: 'var(--ok)', warn: 'var(--warn)', bad: 'var(--bad)', stone: 'var(--stone)', pale: 'var(--pale)' };
const STAT = { '충족': 'met', '미충족': 'unmet', '주의': 'caution' };

let cache = null, cacheKey = '';
export function buildData(reports, J, krCandidates = {}) {
  const key = reports.length + '|' + JSON.stringify(krCandidates);
  if (cache && cacheKey === key) return cache;
  const rows = reports.map((r) => {
    const c = r.components || {}, t = r.fair_value;
    const bank = !t ? null : c.cash != null ? c.cash / t : (c.other != null && r.flags?.cash_is_bank_deposit !== false ? c.other / t : null);
    const mix = t ? { bank: (c.cash ?? 0) / t, repo: (c.repo ?? 0) / t, fund: (c.government_mmf ?? c.circle_reserve_fund ?? 0) / t, treasury: (c.treasury ?? 0) / t, other: (c.other ?? 0) / t } : null;
    const verdicts = Object.fromEntries(ORDER.map((id) => {
      const ev = evaluateReport(r, J[id], id === 'kr-v1' ? krCandidates : {});
      return [id, Object.fromEntries(RULE_IDS.map((rid, i) => [rid, STAT[ev[i]?.status] || 'none']))];
    }));
    return { coin: `${r.issuer_short} ${r.token}`, month: r.month, as_of: r.as_of, bank, mix,
      coverage: r.coverage ?? (r.circulation && t ? t / r.circulation : null), circulation: r.circulation, fair_value: t,
      sign_days: calendarDaysBetween(r.as_of, r.attestation?.signed), verdicts };
  });
  const ruleNames = Object.fromEntries(RULE_IDS.map((rid) => [rid, J['kr-v1'].rules[rid]?.requirement]));
  const thresholds = Object.fromEntries(['R03', 'R05', 'R10', 'R13', 'R07', 'R02'].map((rid) => [rid, Object.fromEntries(ORDER.map((id) => {
    const d = resolveRuleDef(J[id], rid, id === 'kr-v1' ? krCandidates[rid] : undefined) || {};
    return [id, { status: d.legal_status ?? d.status ?? null, comparison: d.comparison ?? null, threshold: d.threshold ?? d.deadline_days ?? d.max_days ?? d.days ?? d.value ?? null, unit: d.unit ?? null, label: d.label ?? d.requirement ?? null }];
  }))]));
  const kc = Object.fromEntries(Object.entries(J['kr-v1'].rules).map(([rid, e]) => [rid, (e.candidates || []).map((c) => ({ id: c.id, label: c.label, threshold: c.threshold ?? null, comparison: c.comparison ?? null }))]));
  const kb = Object.fromEntries(Object.entries(J['kr-v1'].rules).map(([rid, e]) => [rid, (e.bills || []).map((b) => ({ bill: b.bill, value: b.value ?? null }))]));
  cache = { jurisdictions: ORDER.map((id) => ({ id, name: J[id].name })), ruleNames, thresholds, krCandidates: kc, krBills: kb, reports: rows };
  cacheKey = key;
  return cache;
}
