// 구역 2 한국 기준 판정 결과: 01 와플, 16 덤벨
import { COL } from './data.js';

const ST = ['met', 'caution', 'unmet', 'none'];
const LAB = { met: '충족', caution: '주의', unmet: '미충족', none: '판정 안 됨' };
const FILL = { met: COL.ok, caution: COL.warn, unmet: COL.bad, none: COL.stone };
const f1 = (x) => (Math.round(x * 10) / 10).toFixed(1);
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const T = (x, y, s, o = {}) => `<text x="${x}" y="${y}" font-size="${o.size || 12}" font-weight="${o.w || 400}" fill="${o.fill || COL.ink}"${o.anchor ? ` text-anchor="${o.anchor}"` : ''}>${esc(s)}</text>`;
const svg = (W, H, label, body) => `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" style="display:block;max-width:none" font-family="inherit" role="img" aria-label="${esc(label)}">${body}</svg>`;

export function views({ data, ri, focus, width, dense }) {
  const FW = Math.max(360, Math.round(width || 500));
  const ids = Object.keys(data.ruleNames), R = data.reports, N = R.length;
  const sel = R[ri] || R[0], sv = sel.verdicts[focus];
  const cnt = ids.reduce((c, id) => (c[sv[id]]++, c), { met: 0, caution: 0, unmet: 0, none: 0 });
  const avg = Object.fromEntries(ST.map((s) => [s, R.reduce((a, r) => a + ids.filter((id) => r.verdicts[focus][id] === s).length, 0) / N]));
  const aria = `${sel.coin} ${sel.month}, 규칙 ${ids.length}개 판정: ` + ST.map((s) => `${LAB[s]} ${cnt[s]}개`).join(', ');

  // 01 와플: 칸 1개 = 규칙 1개
  const cells = ST.flatMap((s) => ids.filter((id) => sv[id] === s).map(() => s));
  const p = dense ? 38 : Math.min(54, Math.floor((FW - 134) / 5)), cs = p - (dense ? 4 : 6), lx = 5 * p + (dense ? 14 : 20), lh = dense ? 30 : 58;
  let w = cells.map((s, i) => `<rect x="${(i % 5) * p}" y="${Math.floor(i / 5) * p}" width="${cs}" height="${cs}" rx="3" fill="${FILL[s]}"/>`).join('');
  w += ST.map((s, i) => `<rect x="${lx}" y="${i * lh + 2}" width="10" height="10" fill="${FILL[s]}"/>` + (dense ? T(lx + 18, i * lh + 12, LAB[s], { fill: COL.muted }) + T(lx + 86, i * lh + 13, `${cnt[s]}개`, { size: 15, w: 700, fill: s === 'none' ? COL.muted : FILL[s] }) : T(lx + 18, i * lh + 12, LAB[s], { fill: COL.muted }) + T(lx + 18, i * lh + 38, `${cnt[s]}개`, { size: 24, w: 700, fill: s === 'none' ? COL.muted : FILL[s] }))).join('');
  const rows = Math.ceil(cells.length / 5), wh = Math.max(rows * p, 4 * lh), note = `칸 1개 = 규칙 1개, ${sel.coin} ${sel.month}`;
  const waffle = dense ? svg(FW, wh + 12, aria, `<title>${esc(note)}</title><g transform="translate(0,6)">${w}</g>`)
    : svg(FW, wh + 52, aria, `<g transform="translate(0,6)">${w}</g>` + T(0, wh + 36, note, { size: 11, fill: COL.muted }));

  // 16 덤벨: 선택 보고서 대 전체 평균
  const mx = Math.max(6, Math.ceil(Math.max(...ST.map((s) => Math.max(cnt[s], avg[s]))))), step = Math.min(64, (FW - 200) / mx), X = (v) => 110 + v * step;
  const ticks = []; for (let v = 0; v <= mx; v += 2) ticks.push(v);
  const W = FW;
  const ys = dense ? 28 : 56, y0 = dense ? 14 : 40, ty = dense ? 128 : 248, ly = dense ? 146 : 284;
  let d = ticks.map((v) => `<line x1="${X(v)}" y1="${dense ? 2 : 10}" x2="${X(v)}" y2="${dense ? 114 : 230}" stroke="${COL.line}"/>` + T(X(v), ty, v, { size: 11, fill: COL.muted, anchor: 'middle' })).join('');
  ST.forEach((s, i) => {
    const y = y0 + i * ys;
    d += T(0, y + 4, LAB[s], { w: 500 }) + `<line x1="${X(cnt[s])}" y1="${y}" x2="${X(avg[s])}" y2="${y}" stroke="${COL.muted}" stroke-width="2"/>`
      + `<circle cx="${X(avg[s])}" cy="${y}" r="7" fill="var(--surface)" stroke="${COL.ink}" stroke-width="2"/><circle cx="${X(cnt[s])}" cy="${y}" r="8" fill="${FILL[s]}"/>`
      + T(X(Math.max(cnt[s], avg[s])) + 16, y + 4, `${cnt[s]} / ${f1(avg[s])}`, { size: 12, fill: COL.muted });
  });
  d += `<circle cx="5" cy="${ly - 4}" r="4.5" fill="${COL.ok}"/>` + T(16, ly, '선택 보고서', { size: 11, fill: COL.muted })
    + `<circle cx="116" cy="${ly - 4}" r="4" fill="var(--surface)" stroke="${COL.muted}" stroke-width="1.5"/>` + T(128, ly, `${N}건 평균`, { size: 11, fill: COL.muted })
    + T(W, ly, '단위: 규칙 수(개)', { size: 11, fill: COL.muted, anchor: 'end' });
  const dumb = svg(W, dense ? 150 : 296, aria + `, 전체 ${N}건 평균과 비교`, dense ? d : `<g transform="translate(0,4)">${d}</g>`);

  return [{ key: '01', label: '와플', html: waffle }, { key: '16', label: '덤벨', html: dumb }];
}
