// 구역 3 준비금 보고서 273건: 20 묶음 막대(기준별 미달 건수)
import { COL } from './data.js';

const LIMS = [0.3, 0.5, 0.6]; // 해외 기준값(EU 일반과 미국 OCC 안, 일본, EU 중요). 한국 의원안은 숫자가 없음
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const pct = (v) => `${Math.round(v * 100)}%`;
const T = (x, y, s, o = {}) => `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" font-size="${o.size ?? 11}" fill="${o.fill ?? COL.ink}"${o.anchor ? ` text-anchor="${o.anchor}"` : ''}${o.weight ? ` font-weight="${o.weight}"` : ''}>${esc(s)}</text>`;

export function views({ data, ri, lim, compact, width, side: sideMode = 'table' }) {
  const narrow = width ? width < 640 : compact;
  const WW = Math.max(360, width ?? (compact ? 520 : 900));
  const R = data.reports;
  const coins = [...new Set(R.map((r) => r.coin))];
  const lims = [...new Set([...LIMS, lim])].sort((a, b) => a - b);
  const sh = (c) => c.split(' ').pop();
  const fail = (c, l) => R.filter((r) => r.coin === c && r.bank != null && r.bank < l).length;
  const vals = coins.map((c) => lims.map((l) => fail(c, l)));
  const step = 10, mx = Math.max(step, Math.ceil(Math.max(...vals.flat()) / step) * step);
  const sel = R[ri]?.coin;
  const latest = (c) => R.reduce((a, r, i) => (r.coin === c && (a < 0 || r.month >= R[a].month) ? i : a), -1);
  const opac = (j) => (0.3 + 0.7 * (lims.length === 1 ? 1 : j / (lims.length - 1))).toFixed(2);

  if (narrow) {
    // 반쪽 칸: 가로 묶음 막대, 이름은 왼쪽, 값은 막대 끝, 범례는 2열
    const W = WW, x0 = 56, xe = W - 26, y0 = 36, bh = 12, gp = bh * lims.length + 14, y1 = y0 + gp * coins.length;
    const xv = (v) => x0 + (v / mx) * (xe - x0);
    let c = '';
    const cols2 = W >= 460, lc = cols2 ? 2 : 1;
    for (let v = 0; v <= mx; v += step) c += `<line x1="${xv(v)}" y1="${y0 - 4}" x2="${xv(v)}" y2="${y1}" stroke="${COL.line}"/>` + T(xv(v), y0 - 8, v, { anchor: 'middle', fill: COL.muted });
    coins.forEach((cn, k) => {
      const gy = y0 + k * gp, top = gy + 7, on = cn === sel;
      if (on) c += `<rect x="2" y="${gy}" width="${W - 4}" height="${gp}" rx="4" fill="${COL.pale}"/>`;
      lims.forEach((lm, j) => {
        const v = vals[k][j], y = top + j * bh, hit = lm === lim;
        if (v) c += `<rect x="${x0}" y="${(y + 1).toFixed(1)}" width="${(xv(v) - x0).toFixed(1)}" height="${bh - 2}" fill="${COL.bad}" fill-opacity="${opac(j)}"/>`;
        c += T(xv(v) + 4, y + bh - 2, v, { fill: hit ? COL.bad : COL.muted, weight: hit ? 700 : 400 });
      });
      c += `<g data-report="${latest(cn)}" style="cursor:pointer"><rect x="2" y="${gy}" width="${x0 - 2}" height="${gp}" fill="transparent"/>${T(x0 - 8, gy + gp / 2 + 4, sh(cn), { anchor: 'end', size: 12, weight: on ? 700 : 400 })}</g>`;
    });
    c += `<line x1="${x0}" y1="${y0 - 4}" x2="${x0}" y2="${y1}" stroke="${COL.muted}"/>` + T(2, 11, '미달 보고서 건수', { fill: COL.muted });
    lims.forEach((l, j) => {
      const lx = x0 + (cols2 ? (j % 2) * Math.min(220, (W - x0 - 10) / 2) : 0), ly = y1 + 26 + Math.floor(j / lc) * 20;
      c += `<rect x="${lx}" y="${ly - 9}" width="11" height="11" fill="${COL.bad}" fill-opacity="${opac(j)}"/>` + T(lx + 16, ly, `${pct(l)} 미만${l === lim ? ' (현재 기준)' : ''}`, { fill: COL.muted });
    });
    const H = y1 + 26 + Math.ceil(lims.length / lc) * 20 - 6;
    const total = vals.reduce((n, v) => n + v[lims.indexOf(lim)], 0);
    return [{ key: '20', label: '묶음 막대', html: `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" style="display:block;max-width:none" font-family="inherit" role="img" aria-label="코인 ${coins.length}종의 은행 예금 기준별 미달 보고서 건수. 기준 ${pct(lim)} 미만은 모두 ${total}건">${c}</svg>` }];
  }

  // 넓은 칸(1000 이상)은 오른쪽에 미달 비율 표를 붙인다: 코인마다 보고서 수와 기준별 미달 비율(건수는 코인마다 보고서 수가 달라 비율로 다시 봄)
  const CWD = 52, side = WW >= 1000 && sideMode !== 'none', BWD = 200, DWD = 220;
  const SIDE = !side ? 0 : sideMode === 'bars' ? 28 + 56 + BWD + 44 : sideMode === 'dots' ? 28 + 56 + DWD + 84 : 28 + 56 + 44 + lims.length * CWD;
  const W = WW, x0 = 48, x1 = W - 16 - SIDE, y0 = 24, y1 = 250, gp = (x1 - x0) / coins.length; // 칸 폭을 다 씀(막대 굵기는 22 상한)
  const bw = Math.min(22, (gp - 14) / lims.length), yv = (v) => y1 - (v / mx) * (y1 - y0);
  let b = '';
  for (let v = 0; v <= mx; v += step) b += `<line x1="${x0}" y1="${yv(v)}" x2="${x0 + gp * coins.length}" y2="${yv(v)}" stroke="${COL.line}"/>` + T(x0 - 8, yv(v) + 4, v, { anchor: 'end', fill: COL.muted });
  coins.forEach((c, k) => {
    const gw = bw * lims.length, gx = x0 + k * gp + (gp - gw) / 2, cx = gx + gw / 2, l = latest(c);
    const on = c === sel;
    if (on) b += `<rect x="${(x0 + k * gp + 2).toFixed(1)}" y="${y0 - 2}" width="${(gp - 4).toFixed(1)}" height="${y1 - y0 + 32}" rx="4" fill="${COL.pale}"/>`;
    lims.forEach((lm, j) => {
      const v = vals[k][j], x = gx + j * bw, hit = lm === lim;
      if (v) b += `<rect x="${(x + 1).toFixed(1)}" y="${yv(v).toFixed(1)}" width="${(bw - 2).toFixed(1)}" height="${(y1 - yv(v)).toFixed(1)}" fill="${COL.bad}" fill-opacity="${opac(j)}"/>`;
      b += T(x + bw / 2, yv(v) - 4, v, { anchor: 'middle', size: 11, fill: hit ? COL.bad : COL.muted, weight: hit ? 700 : 400 });
    });
    b += `<g data-report="${l}" style="cursor:pointer"><rect x="${(x0 + k * gp).toFixed(1)}" y="${y1 + 4}" width="${gp.toFixed(1)}" height="22" fill="transparent"/>${T(cx, y1 + 20, sh(c), { anchor: 'middle', size: 12, weight: on ? 700 : 400 })}</g>`;
  });
  b += `<line x1="${x0}" y1="${y1}" x2="${x0 + gp * coins.length}" y2="${y1}" stroke="${COL.muted}"/>` + T(x0, y0 - 10, '미달 보고서 건수', { fill: COL.muted });
  if (side && sideMode === 'table') {
    const sx = W - SIDE + 28, nx = sx + 56 + 44, rh = 26, ty0 = y0 + 22;
    const known = (c) => R.filter((r) => r.coin === c && r.bank != null).length;
    b += T(sx, y0 - 10, '미달 비율 (은행 예금을 알 수 있는 보고서 중)', { fill: COL.muted }) + T(sx, y0 + 12, '코인', { fill: COL.muted }) + T(nx - 10, y0 + 12, '보고서', { fill: COL.muted, anchor: 'end' });
    lims.forEach((l, j) => { b += T(nx + j * CWD + CWD / 2, y0 + 12, pct(l), { anchor: 'middle', size: 12, weight: l === lim ? 700 : 400, fill: l === lim ? COL.bad : COL.ink }); });
    coins.forEach((c, k) => {
      const y = ty0 + k * rh, n = known(c), on = c === sel;
      if (on) b += `<rect x="${sx - 6}" y="${y}" width="${SIDE - 28 + 6}" height="${rh}" rx="4" fill="${COL.pale}"/>`;
      b += `<g data-report="${latest(c)}" style="cursor:pointer">${T(sx, y + 17, sh(c), { size: 12, weight: on ? 700 : 400 })}</g>` + T(nx - 10, y + 17, n, { size: 12, anchor: 'end', fill: COL.muted });
      lims.forEach((l, j) => {
        const r = n ? vals[k][j] / n : 0, x = nx + j * CWD;
        b += `<rect x="${x + 2}" y="${y + 3}" width="${CWD - 4}" height="${rh - 6}" fill="${r ? COL.bad : COL.pale}"${r ? ` fill-opacity="${(0.12 + 0.78 * r).toFixed(2)}"` : ''}/>` + T(x + CWD / 2, y + 17, n ? pct(r) : '-', { anchor: 'middle', size: 12, weight: l === lim ? 700 : 400, fill: r >= 0.55 ? '#fff' : r ? COL.ink : COL.muted });
      });
    });
  }  if (side && sideMode !== 'table') {
    const sx = W - SIDE + 28, rh = 26, ty0 = y0 + 22, known = (c) => R.filter((r) => r.coin === c && r.bank != null).length, li = lims.indexOf(lim), gx = sx + 56;
    b += T(sx, y0 - 10, sideMode === 'bars' ? `미달 비율, 기준 ${pct(lim)} (은행 예금을 알 수 있는 보고서 중)` : '기준별 미달 비율 (은행 예금을 알 수 있는 보고서 중)', { fill: COL.muted });
    if (sideMode === 'dots') [0, 0.5, 1].forEach((t) => { b += `<line x1="${gx + t * DWD}" y1="${ty0 - 2}" x2="${gx + t * DWD}" y2="${ty0 + coins.length * rh}" stroke="${COL.line}"/>` + T(gx + t * DWD, y0 + 12, pct(t), { anchor: 'middle', fill: COL.muted }); });
    coins.forEach((c, k) => {
      const y = ty0 + k * rh, n = known(c), on = c === sel, rs = lims.map((l, j) => (n ? vals[k][j] / n : 0));
      if (on) b += `<rect x="${sx - 6}" y="${y}" width="${SIDE - 28 + 6}" height="${rh}" rx="4" fill="${COL.pale}"/>`;
      b += `<g data-report="${latest(c)}" style="cursor:pointer">${T(sx, y + 17, sh(c), { size: 12, weight: on ? 700 : 400 })}</g>`;
      if (sideMode === 'bars') {
        const r = rs[li];
        b += `<rect x="${gx}" y="${y + 6}" width="${BWD}" height="${rh - 12}" fill="${COL.pale}"/>` + (r ? `<rect x="${gx}" y="${y + 6}" width="${(r * BWD).toFixed(1)}" height="${rh - 12}" fill="${COL.bad}"/>` : '') + T(gx + BWD + 8, y + 17, n ? pct(r) : '-', { size: 12, weight: 700, fill: r ? COL.ink : COL.muted });
      } else {
        const lo = Math.min(...rs), hi = Math.max(...rs), cy = y + rh / 2;
        b += `<line x1="${(gx + lo * DWD).toFixed(1)}" y1="${cy}" x2="${(gx + hi * DWD).toFixed(1)}" y2="${cy}" stroke="${COL.bad}" stroke-opacity=".35" stroke-width="3"/>`;
        rs.forEach((r, j) => { b += `<circle cx="${(gx + r * DWD).toFixed(1)}" cy="${cy}" r="${j === li ? 6 : 4.5}" fill="${COL.bad}" fill-opacity="${opac(j)}"${j === li ? ` stroke="${COL.ink}" stroke-width="1.5"` : ''}/>`; });
        b += T(gx + DWD + 12, y + 17, n ? `${pct(rs[0])}→${pct(rs[rs.length - 1])}` : '-', { size: 11, fill: COL.muted });
      }
    });
  }

  let lx = x0; const ly = y1 + 52;
  lims.forEach((l, j) => {
    const label = `${pct(l)} 미만${l === lim ? ' (현재 기준)' : ''}`;
    b += `<rect x="${lx}" y="${ly - 9}" width="11" height="11" fill="${COL.bad}" fill-opacity="${opac(j)}"/>` + T(lx + 16, ly, label, { fill: COL.muted });
    lx += 16 + [...label].reduce((w, ch) => w + (ch.charCodeAt(0) > 0x2e80 ? 11 : 6.5), 0) + 22;
  });
  const H = ly + 12;
  const total = vals.reduce((n, v) => n + v[lims.indexOf(lim)], 0);
  const html = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" style="display:block;max-width:none" font-family="inherit" role="img" aria-label="코인 ${coins.length}종의 은행 예금 기준별 미달 보고서 건수. 기준 ${pct(lim)} 미만은 모두 ${total}건">${b}</svg>`;
  return [{ key: '20', label: '묶음 막대', html }];
}
