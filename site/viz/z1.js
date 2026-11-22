// 구역 1 지표 카드: 06 진행 막대, 04 원형 게이지, 03 불릿. 숫자는 전부 ctx(선택 보고서 ri, 기준 lim/dayLim)에서 계산한다.
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const f1 = (v) => Math.round(v * 10) / 10;
const f2 = (v) => Math.round(v * 100) / 100;
const T = (x, y, s, o = {}) => `<text x="${f1(x)}" y="${f1(y)}" font-size="${o.size || 11}" fill="${o.fill || 'var(--ink)'}" font-weight="${o.w || 400}" text-anchor="${o.a || 'start'}">${esc(s)}</text>`;
const Ln = (x1, y1, x2, y2, o = {}) => `<line x1="${f1(x1)}" y1="${f1(y1)}" x2="${f1(x2)}" y2="${f1(y2)}" stroke="${o.stroke || 'var(--ink)'}" stroke-width="${o.w || 2}"/>`;
const Rc = (x, y, w, h, fill, rx = 0) => `<rect x="${f1(x)}" y="${f1(y)}" width="${f1(Math.max(w, 0))}" height="${f1(Math.max(h, 0))}" fill="${fill}"${rx ? ` rx="${rx}"` : ''}/>`;
const arc = (cx, cy, r, a0, a1, stroke, w) => {
  const p = (a) => [cx + r * Math.cos((a * Math.PI) / 180), cy + r * Math.sin((a * Math.PI) / 180)];
  const [x0, y0] = p(a0), [x1, y1] = p(a1);
  return `<path d="M${f1(x0)},${f1(y0)} A${r},${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${f1(x1)},${f1(y1)}" fill="none" stroke="${stroke}" stroke-width="${w}" stroke-linecap="round"/>`;
};
// 늘이지 않는 크기(1:1). W는 칸 안쪽 폭(최소 360), 글자는 항상 실제 크기.
const svg = (W, H, body, label, title) => `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" style="display:block;max-width:none" font-family="inherit" role="img" aria-label="${esc(label)}">${title ? `<title>${esc(title)}</title>` : ''}${body}</svg>`;
const widthOf = (ctx) => Math.max(360, Math.round(ctx.width || 500));

// 세 지표: 은행 예금 비중, 서명까지 걸린 날, 커버리지
export function metrics({ data, ri, lim, dayLim }) {
  const r = data.reports[ri];
  const pct = Math.round(lim * 10000) / 100;
  const mk = (key, name, v, d, unit, ref, up, refTxt, gap) => ({ key, name, v, disp: v == null ? '자료 없음' : v.toFixed(d), unit, ref, up, refTxt,
    ok: v == null ? null : up ? v >= ref : v <= ref, gap: v == null ? '' : gap(v) });
  return [
    mk('bank', '은행 예금 비중', r.bank == null ? null : f2(r.bank * 100), 2, '%', pct, true, `기준 ${pct}% 이상`, (v) => `기준보다 ${Math.abs(f2(pct - v)).toFixed(2)}%p ${v >= pct ? '높음' : '낮음'}`),
    mk('days', '기준일부터 서명까지', r.sign_days, 0, '일', dayLim, false, `기준 ${dayLim}일 이내`, (v) => (v <= dayLim ? `기준까지 ${dayLim - v}일 남음` : `기준보다 ${v - dayLim}일 넘음`)),
    mk('cov', '커버리지', r.coverage == null ? null : f2(r.coverage * 100), 2, '%', 100, true, '기준 100% 이상', (v) => `기준보다 ${Math.abs(f2(v - 100)).toFixed(2)}%p ${v >= 100 ? '높음' : '낮음'}`),
  ];
}
const col = (m) => (m.ok == null ? 'var(--stone)' : m.ok ? 'var(--ok)' : 'var(--bad)');
const tcol = (m) => (m.ok == null ? 'var(--muted)' : col(m));
const unitTxt = (m) => (m.v == null ? '' : m.unit);

function progress(ms, W, dense) {
  const R = Math.min(W - 24, 640), w = R - 24 - 46;
  let s = '';
  ms.forEach((m, i) => {
    const y = dense ? 18 + i * 58 : 24 + i * 82, ratio = m.v == null ? 0 : m.v / m.ref;
    const share = m.v == null ? '자료 없음' : `${m.key === 'days' ? '기한' : '기준'}의 ${(ratio * 100).toFixed(m.key === 'cov' ? 2 : 0)}%`;
    s += T(24, y, m.name, { size: 13, w: 700 }) + T(R, y, share, { size: 13, w: 700, a: 'end', fill: tcol(m) });
    const by = dense ? y + 8 : y + 12;
    s += Rc(24, by, w, 14, 'var(--pale)', 7) + (m.v == null ? '' : Rc(24, by, Math.max(Math.min(ratio, 1) * w, 3), 14, col(m), Math.min(7, Math.max(Math.min(ratio, 1) * w, 3) / 2)));
    s += Ln(24 + w, by - 6, 24 + w, by + 20) + T(24 + w + 10, by + 12, '기준', { size: 11, fill: 'var(--muted)' });
    s += T(24, y + (dense ? 38 : 46), m.v == null ? '값을 계산할 수 없음' : `${m.disp}${m.unit} / ${m.refTxt}`, { size: 12, fill: 'var(--muted)' });
  });
  const lab = '지표 세 개가 기준값을 얼마나 채웠는지 보여 주는 진행 막대';
  if (dense) return svg(W, 182, s, lab, `${lab}. 막대 끝의 검은 선이 기준값(100%). 서명까지 걸린 날은 한도 대비 사용분.`);
  s += T(24, 276, '막대 끝의 검은 선이 기준값(100%).', { size: 11, fill: 'var(--muted)' });
  s += T(24, 292, '서명까지 걸린 날은 한도 대비 사용분.', { size: 11, fill: 'var(--muted)' });
  return svg(W, 304, s, lab);
}

function ring(ms, W, dense) {
  let s = '', H;
  const note = '눈금 끝은 기준값의 2배, 위쪽 검은 눈금이 기준값. 파랑은 충족, 빨강은 미달.';
  const fill = (m) => (m.v == null ? 0 : Math.min(m.v / (m.ref * 2), 1));
  if ((W - 48) / 3 >= 150) { // 가로 세 칸
    const cell = Math.min((W - 48) / 3, 200);
    ms.forEach((m, i) => {
      const cx = 24 + cell / 2 + i * cell, cy = dense ? 84 : 98, r = dense ? 48 : 50, f = fill(m);
      s += T(cx, 14, m.name, { size: 13, w: 700, a: 'middle' });
      s += arc(cx, cy, r, 135, 405, 'var(--pale)', 12) + (f > 0.004 ? arc(cx, cy, r, 135, 135 + 270 * f, col(m), 12) : '');
      s += Ln(cx, cy - r - 10, cx, cy - r + 10);
      s += `<text x="${f1(cx)}" y="${cy + 6}" text-anchor="middle" font-weight="700" fill="${m.v == null ? 'var(--muted)' : 'var(--ink)'}" font-size="${m.disp.length > 5 ? 17 : 21}">${esc(m.disp)}<tspan font-size="12" font-weight="400" fill="var(--muted)">${esc(unitTxt(m))}</tspan></text>`;
      s += T(cx, cy + 26, m.refTxt, { size: 11, fill: 'var(--muted)', a: 'middle' });
      s += T(cx, dense ? 150 : 186, m.gap, { size: 12, w: 700, fill: tcol(m), a: 'middle' });
    });
    if (!dense) {
      s += T(24, 224, '눈금 끝은 기준값의 2배, 위쪽 검은 눈금이 기준값.', { size: 11, fill: 'var(--muted)' });
      s += T(24, 240, '파랑은 충족, 빨강은 미달.', { size: 11, fill: 'var(--muted)' });
    }
    H = dense ? 162 : 252;
  } else { // 좁은 칸: 한 줄에 게이지 하나, 글은 오른쪽
    ms.forEach((m, i) => {
      const rr = dense ? 26 : 38, cx = 24 + 44, cy = dense ? 34 + i * 60 : 52 + i * 100, r = rr, f = fill(m), sw = dense ? 9 : 12;
      s += arc(cx, cy, r, 135, 405, 'var(--pale)', sw) + (f > 0.004 ? arc(cx, cy, r, 135, 135 + 270 * f, col(m), sw) : '');
      s += Ln(cx, cy - r - (dense ? 7 : 10), cx, cy - r + (dense ? 7 : 10));
      s += `<text x="${cx}" y="${cy + 5}" text-anchor="middle" font-weight="700" fill="${m.v == null ? 'var(--muted)' : 'var(--ink)'}" font-size="${dense ? (m.disp.length > 5 ? 11 : 12) : m.disp.length > 5 ? 13 : 15}">${esc(m.disp)}<tspan font-size="11" font-weight="400" fill="var(--muted)">${esc(unitTxt(m))}</tspan></text>`;
      s += T(128, cy - (dense ? 12 : 16), m.name, { size: 13, w: 700 }) + T(128, cy + (dense ? 4 : 4), m.refTxt, { size: 11, fill: 'var(--muted)' }) + T(128, cy + (dense ? 20 : 24), m.gap, { size: 12, w: 700, fill: tcol(m) });
    });
    if (!dense) {
      s += T(24, 316, '눈금 끝은 기준값의 2배, 위쪽 검은 눈금이 기준값.', { size: 11, fill: 'var(--muted)' });
      s += T(24, 332, '파랑은 충족, 빨강은 미달.', { size: 11, fill: 'var(--muted)' });
    }
    H = dense ? 184 : 344;
  }
  return svg(W, H, s, '지표 세 개의 원형 게이지', dense ? `지표 세 개의 원형 게이지. ${note}` : '');
}

function bullet(ms, W, dense) {
  const nice = (x, step) => Math.ceil(x / step) * step;
  const R = Math.min(W - 24, 640), len = R - 24;
  let s = '';
  ms.forEach((m, i) => {
    const y = 14 + i * (dense ? 58 : 90), ref = m.ref, bt = dense ? 12 : 14, bh = dense ? 16 : 22;
    const max = nice(Math.max(ref * (m.key === 'days' ? 1.5 : m.key === 'cov' ? 1.2 : 2), (m.v ?? 0) * 1.05), m.key === 'days' ? 5 : m.key === 'cov' ? 10 : 5);
    const X = (v) => 24 + (v / max) * len, xr = X(ref);
    s += T(24, y + 4, m.name, { size: 13, w: 700 }) + T(R, y + 4, m.v == null ? '자료 없음' : m.disp + m.unit, { size: 13, w: 700, a: 'end' });
    const badZ = m.up ? [24, xr] : [xr, R], goodZ = m.up ? [xr, R] : [24, xr];
    s += Rc(badZ[0], y + bt, badZ[1] - badZ[0], bh, 'var(--stone)') + Rc(goodZ[0], y + bt, goodZ[1] - goodZ[0], bh, 'var(--pale)');
    if (m.v != null) s += Rc(24, y + bt + (bh - 8) / 2, X(Math.min(m.v, max)) - 24, 8, 'var(--ink-fill)');
    s += Ln(xr, y + bt - 4, xr, y + bt + bh + 4, { w: 2.5 });
    const ticks = [...new Set([0, ref / 2, ref, max].map((t) => f2(t)))].sort((a, b) => a - b);
    ticks.forEach((t, k) => {
      const lab = `${t}${m.unit}`, near = t !== ref && Math.abs(X(t) - xr) < 34;
      if (near) return;
      s += T(X(t), y + bt + bh + (dense ? 16 : 18), lab, { size: 11, fill: t === ref ? 'var(--ink)' : 'var(--muted)', a: k === 0 ? 'start' : k === ticks.length - 1 ? 'end' : 'middle', w: t === ref ? 700 : 400 });
    });
  });
  const lab = '지표 세 개를 기준 구간 위에 얹은 불릿 그래프';
  if (dense) return svg(W, 180, s, lab, `${lab}. 검은 막대는 현재 값, 검은 선은 기준값. 진한 회색은 미달, 옅은 회색은 충족 구간.`);
  s += T(24, 284, '검은 막대는 현재 값, 검은 선은 기준값.', { size: 11, fill: 'var(--muted)' });
  s += T(24, 300, '진한 회색은 미달, 옅은 회색은 충족 구간.', { size: 11, fill: 'var(--muted)' });
  return svg(W, 312, s, lab);
}

export function views(ctx) {
  const ms = metrics(ctx), W = widthOf(ctx);
  return [
    { key: '06', label: '진행 막대', html: progress(ms, W, ctx.dense) },
    { key: '04', label: '원형 게이지', html: ring(ms, W, ctx.dense) },
    { key: '03', label: '불릿', html: bullet(ms, W, ctx.dense) },
  ];
}
