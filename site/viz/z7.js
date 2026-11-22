// 구역 7 숫자 규칙 분포: 09 누적 분포(ECDF), 26 100% 누적 막대
import { COL, SHORT } from './data.js';

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const f1 = (v) => Math.round(v * 10) / 10;
const pct = (a, b) => (b ? Math.round((a / b) * 1000) / 10 : 0);
const tx = (x, y, s, o = {}) => `<text x="${f1(x)}" y="${f1(y)}" font-size="${o.size || 12}" fill="${o.fill || COL.muted}" text-anchor="${o.anchor || 'start'}"${o.weight ? ` font-weight="${o.weight}"` : ''}>${esc(s)}</text>`;
const ln = (x1, y1, x2, y2, c = COL.line, w = 1, dash) => `<line x1="${f1(x1)}" y1="${f1(y1)}" x2="${f1(x2)}" y2="${f1(y2)}" stroke="${c}" stroke-width="${w}"${dash ? ` stroke-dasharray="${dash}"` : ''}/>`;
const rc = (x, y, w, h, fill) => `<rect x="${f1(x)}" y="${f1(y)}" width="${f1(Math.max(w, 0))}" height="${f1(h)}" fill="${fill}"/>`;
const tw = (s, size = 12) => [...String(s)].reduce((a, ch) => a + (/[ㄱ-힣]/.test(ch) ? size : ch === ' ' ? size * 0.3 : size * 0.6), 0);
const svg = (W, H, label, body) => `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" style="display:block;max-width:none" font-family="inherit" role="img" aria-label="${esc(label)}">${body}</svg>`;
// 범례: 한 줄에 못 들어가면 줄바꿈. 반환 { html, h }
function legend(items, W, y0) {
  let x = 0, y = 0; const out = [];
  items.forEach((it) => {
    const w = 18 + tw(it.label) + 18;
    if (x + w > W - 40 && x > 0) { x = 0; y += 18; }
    const X = 20 + x, Y = y0 + y;
    out.push(it.k === 'sq' ? rc(X, Y - 9, 10, 10, it.c) : it.k === 'dot' ? `<circle cx="${X + 5}" cy="${Y - 4}" r="4" fill="${it.c}"/>` : ln(X, Y - 4, X + 12, Y - 4, it.c, it.k === 'line' ? 2 : 1.5, it.k === 'dash' ? '3 2' : undefined));
    out.push(tx(X + 17, Y, it.label));
    x += w;
  });
  return { html: out.join(''), h: y + 18 };
}

// 칸 안쪽 폭(없으면 compact 520 / 기본 760), 최소 360. 640 미만이면 좁은 배치
const wid = (ctx) => Math.max(360, Math.round(ctx.width || (ctx.compact ? 520 : 760)));

// 한국 의원안 값(법안별 숫자 중 최소, 최대). 법안마다 같은 값이면 한 점. fmt는 값 표기, k는 단위 배율. 숫자가 없으면 []
const krPts = (data, rid, fmt, k = 1) => {
  const bills = data.krBills[rid] || [], vs = bills.map((b) => b.value).filter((v) => typeof v === 'number').map((v) => v * k);
  if (!vs.length) return [];
  const lo = Math.min(...vs), hi = Math.max(...vs), cnt = `${bills.length}건 중 ${vs.length}건`;
  return lo === hi ? [{ label: `의원안 ${fmt(lo)}`, v: lo, cnt }] : [{ label: `의원안 최소 ${fmt(lo)}`, v: lo, cnt }, { label: `의원안 최대 ${fmt(hi)}`, v: hi, cnt }];
};
// 규칙별 기준값을 data에서 뽑는다(없으면 빈 값). 사용자가 고른 기준(ctx.dayLim, ctx.lim)은 한국 값이 아니므로 쓰지 않는다
function refs(data) {
  const fDays = ['us', 'hk', 'sg'].map((id) => data.thresholds.R10?.[id]?.threshold).filter((v) => typeof v === 'number');
  // ponytail: data.js가 deadline_days를 아직 안 읽어 R10 해외 값이 비면 31일(미국, 홍콩, 싱가포르 공통)로 대신한다
  const foreignDay = fDays.length ? Math.min(...fDays) : 31;
  const bank = Object.entries(data.thresholds.R05 || {}).filter(([id, d]) => id !== 'kr-v1' && typeof d.threshold === 'number')
    .map(([id, d]) => ({ v: d.threshold * 100, label: `${SHORT[id]} ${f1(d.threshold * 100)}%`, id }));
  return { billDays: krPts(data, 'R10', (v) => `${v}일`), billBank: krPts(data, 'R05', (v) => `${f1(v)}%`, 100), foreignDay, bank };
}

// ===== 09 누적 분포 =====
function ecdf(ctx) {
  const { data, ri } = ctx, R = refs(data);
  const days = data.reports.map((r) => r.sign_days).filter((d) => d != null).sort((a, b) => a - b), n = days.length;
  const W = wid(ctx), C = W < 640, X0 = C ? 44 : 56, X1 = W - (C ? 34 : 32), Y1 = 44, Y0 = C ? 260 : 290, max = Math.ceil((Math.max(...days, R.foreignDay, ...R.billDays.map((p) => p.v)) + 1) / 5) * 5;
  const X = (v) => X0 + (v / max) * (X1 - X0), Y = (p) => Y0 - p * (Y0 - Y1);
  const F = (v) => days.filter((x) => x <= v).length / n, P = (v) => pct(days.filter((x) => x <= v).length, n);
  const out = [];
  [0, 0.25, 0.5, 0.75, 1].forEach((p) => out.push(ln(X0, Y(p), X1, Y(p)), tx(X0 - 8, Y(p) + 4, `${p * 100}%`, { anchor: 'end' })));
  for (let tk = 0; tk <= max; tk += C ? 15 : 10) out.push(tx(X(tk), Y0 + 18, tk, { anchor: 'middle' }));
  out.push(tx(X1 + 8, Y0 + 18, '일'), tx(C ? 4 : X0 - 40, Y1 - 14, '누적 비율(서명까지 걸린 날수 이하)'));
  // 기준선(같은 날수는 한 점으로 합친다)
  const marks = new Map();
  [...R.billDays.map((p) => [p.v, COL.ok, p.label]), [R.foreignDay, COL.muted, `해외 ${R.foreignDay}일`]]
    .forEach(([v, c, l]) => { const e = marks.get(v) || { v, c, ls: [] }; e.ls.push(l); marks.set(v, e); });
  const ms = [...marks.values()].sort((a, b) => a.v - b.v);
  ms.forEach((m) => out.push(ln(X(m.v), Y1 - 4, X(m.v), Y0, m.c, 1.2, '3 2')));
  let d = `M${f1(X(0))} ${f1(Y(0))}`, cum = 0;
  [...new Set(days)].forEach((v) => { d += ` L${f1(X(v))} ${f1(Y(cum / n))}`; cum = days.filter((x) => x <= v).length; d += ` L${f1(X(v))} ${f1(Y(cum / n))}`; });
  out.push(`<path d="${d} L${f1(X(max))} ${f1(Y(1))}" fill="none" stroke="${COL.fill}" stroke-width="2"/>`);
  ms.forEach((m, i) => {
    const y = Y(F(m.v)), name = m.ls.join(', '), t = `${name} ${P(m.v)}%`;
    out.push(`<circle cx="${f1(X(m.v))}" cy="${f1(y)}" r="4.5" fill="${m.c}"/>`);
    if (F(m.v) < 0.1) out.push(tx(X(m.v) + 9, y - 24, name, { fill: m.c, weight: 600 }), tx(X(m.v) + 9, y - 10, `${P(m.v)}%`, { fill: m.c, weight: 600 }));
    else if (i === ms.length - 1) out.push(tx(X(m.v) + 10, y + 16, t, { fill: m.c, weight: 600 }));
    else out.push(tx(X(m.v) - 10, y - 8, t, { fill: m.c, weight: 600, anchor: 'end' }));
  });
  // 선택 보고서
  const r = data.reports[ri], sd = r?.sign_days;
  if (sd != null) {
    const x = X(sd), y = Y(F(sd));
    out.push(`<g data-report="${ri}" style="cursor:pointer"><path d="M${f1(x)} ${Y0 + 2} l-5 8 h10 z" fill="${COL.ink}"/><circle cx="${f1(x)}" cy="${f1(y)}" r="7" fill="none" stroke="${COL.ink}" stroke-width="2"/>`
      + tx(Math.min(Math.max(x, X0 + 80), X1 - 80), Y0 + 38, `선택 보고서 ${sd}일, ${P(sd)}%`, { fill: COL.ink, anchor: 'middle', weight: 600 }) + '</g>');
  }
  const leg = legend([{ k: 'line', c: COL.fill, label: '누적 비율' }, ...R.billDays.map((p) => ({ k: 'dash', c: COL.ok, label: `${p.label}(${p.cnt})` })), { k: 'dash', c: COL.muted, label: `해외 ${R.foreignDay}일` }, ...(sd != null ? [{ k: 'dot', c: COL.ink, label: '선택 보고서' }] : [])], W, Y0 + 66);
  const H = Y0 + 66 + leg.h;
  return svg(W, H, `기준일수별 통과 비율. ${n}건 중 ${R.billDays.map((p) => `${p.label} 이내 ${P(p.v)}%, `).join('')}해외 ${R.foreignDay}일 이내 ${P(R.foreignDay)}%`, out.join('') + leg.html);
}

// ===== 26 100% 누적 막대 =====
function stacked(ctx) {
  const { data, ri } = ctx, R = refs(data), reps = data.reports, N = reps.length, W = wid(ctx), C = W < 640, X0 = C ? 124 : 170, X1 = C ? W - 40 : Math.min(W - 100, X0 + 700), BW = X1 - X0, RH = 28;
  const sel = reps[ri], out = []; let y = 8;
  const seg = (x, w, c, lab) => { out.push(rc(x, y, w, 20, c)); if (lab && w > 40) out.push(tx(x + w / 2, y + 14.5, lab, { fill: '#fff', anchor: 'middle', weight: 500 })); };
  const hdr = (s, s2) => { out.push(tx(C ? 10 : 20, y + 12, s, { fill: COL.ink, weight: 700 })); y += 22; if (s2) { out.push(tx(C ? 10 : 20, y + 8, s2)); y += 20; } };
  // 한 줄: ok(m) / bad / stone(값 없음), 선택 보고서 점은 오른쪽 끝
  const row = (label, m, valid, selState) => {
    out.push(tx(C ? 10 : 28, y + 14.5, label, { fill: COL.ink }));
    let x = X0; const w = (k) => (k / N) * BW;
    if (m) { seg(x, w(m), COL.ok, `${pct(m, N)}%`); x += w(m); }
    if (valid - m) { seg(x, w(valid - m), COL.bad, `${pct(valid - m, N)}%`); x += w(valid - m); }
    if (N - valid) seg(x, w(N - valid), COL.stone);
    if (selState) out.push(`<circle cx="${X1 + 22}" cy="${y + 10}" r="5.5" fill="${selState === 'ok' ? COL.ok : selState === 'bad' ? COL.bad : COL.stone}" data-report="${ri}" style="cursor:pointer"/>`);
    y += RH;
  };
  const dayVals = reps.map((r) => r.sign_days), dn = dayVals.filter((d) => d != null).length;
  C ? hdr(`R10 ${data.ruleNames.R10 || '공개 기한'}`, '서명까지 걸린 날이 기준 이하면 충족') : hdr(`R10 ${data.ruleNames.R10 || '공개 기한'}: 서명까지 걸린 날이 기준 이하면 충족`);
  [...R.billDays.map((p) => [p.label, p.v]), [`해외 ${R.foreignDay}일`, R.foreignDay]].sort((a, b) => a[1] - b[1])
    .forEach(([l, th]) => row(l, dayVals.filter((d) => d != null && d <= th).length, dn, sel.sign_days == null ? 'none' : sel.sign_days <= th ? 'ok' : 'bad'));
  y += 8;
  const banks = reps.map((r) => r.bank), bn = banks.filter((b) => b != null).length, eps = 1e-9;
  C ? hdr(`R05 ${data.ruleNames.R05 || '은행 예금 비율'}`, '비중이 기준 이상이면 충족') : hdr(`R05 ${data.ruleNames.R05 || '은행 예금 비율'}: 비중이 기준 이상이면 충족`);
  [...R.billBank.map((p) => [p.label, p.v]), ...R.bank.map((b) => [b.label, b.v])].sort((a, b) => a[1] - b[1])
    .forEach(([l, th]) => row(l, banks.filter((b) => b != null && b * 100 >= th - eps).length, bn, sel.bank == null ? 'none' : sel.bank * 100 >= th - eps ? 'ok' : 'bad'));
  out.push(tx(X1 + 22, C ? 20 : 20, '선택', { anchor: 'middle', fill: COL.muted, size: 11 }));
  const noB = N - bn, noD = N - dn;
  const leg = legend([{ k: 'sq', c: COL.ok, label: '충족' }, { k: 'sq', c: COL.bad, label: '미충족' }, ...(noB || noD ? [{ k: 'sq', c: COL.stone, label: `값 없음(${noB ? `은행 예금 ${noB}건` : ''}${noB && noD ? ', ' : ''}${noD ? `서명 날수 ${noD}건` : ''})` }] : []), { k: 'dot', c: COL.ink, label: '오른쪽 점은 선택 보고서' }], W, y + 14);
  const H = y + 14 + leg.h;
  return svg(W, H, `기준값별 충족 비율, 보고서 ${N}건. 서명 날수 해외 ${R.foreignDay}일 이내 ${pct(dayVals.filter((d) => d != null && d <= R.foreignDay).length, N)}%, 은행 예금 해외 ${R.bank.length}곳 기준 이상 ${R.bank.map((b) => `${b.label} ${pct(banks.filter((x) => x != null && x * 100 >= b.v - eps).length, N)}%`).join(', ')}`, out.join('') + leg.html);
}

export function views(ctx) {
  return [{ key: '09', label: '누적 분포', html: ecdf(ctx) }, { key: '26', label: '100% 누적 막대', html: stacked(ctx) }];
}
