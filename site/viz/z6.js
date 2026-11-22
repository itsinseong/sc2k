// 구역 6 규칙별 기준값 비교: 19 롤리팝(은행 예금 비율), 02 값 표(숫자 규칙 6개)
// 칸 값은 prototype/chart-lab/cells6.mjs와 같은 방식으로 jurisdictions/*.json에서 읽는다(data.thresholds에는 일수 필드와 R01, R04가 없음).
import { COL, SHORT } from './data.js';

const FOREIGN = ['us', 'eu-emt', 'eu-emt-significant', 'hk', 'sg', 'jp'];
let J = null; // 기준값 원본(jurisdictions/*.json). 사이트가 불러 둔 것을 ctx.J로 받는다

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const f = (n) => Math.round(n * 10) / 10;
const pn = (v) => Math.round(v * 1000) / 10;
const tx = (x, y, s, o = {}) => `<text x="${f(x)}" y="${f(y)}" font-size="${o.size || 11}" fill="${o.fill || COL.ink}"${o.anchor ? ` text-anchor="${o.anchor}"` : ''}${o.weight ? ` font-weight="${o.weight}"` : ''}${o.attr ? ' ' + o.attr : ''}>${esc(s)}</text>`;
const ln = (x1, y1, x2, y2, stroke, w = 1, extra = '') => `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke="${stroke}" stroke-width="${w}"${extra ? ' ' + extra : ''}/>`;
const svg = (W, H, label, body) => `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" style="display:block;max-width:none" font-family="inherit" role="img" aria-label="${esc(label)}">${body}</svg>`;
// 칸 폭(ctx.width)에 1:1로 그린다. 없으면 예전 기본 폭(좁은 판 520, 넓은 판 dw), 360 미만은 360
const widthOf = (ctx, dw) => (ctx.width ? Math.max(360, Math.round(ctx.width)) : ctx.compact ? 520 : dw);
const isNarrow = (ctx, W) => (ctx.width ? W < 640 : !!ctx.compact);

const COLS = ['의원안', '미국', 'EU 일반', 'EU 중요', '홍콩', '싱가포르', '일본'];
const CIDS = ['kr-v1', ...FOREIGN]; // 칸 열의 나라 id
const RN = { R01: '커버리지', R03: '국채 만기 상한', R04: '레포 만기', R05: '은행 예금 비율', R10: '공개 기한', R13: '돌려주는 조건' };
const DIR = { R01: '이상', R03: '이하', R04: '이하', R05: '이상', R10: '안', R13: '안' };
const NUMR = ['R01', 'R03', 'R04', 'R05', 'R10', 'R13'];

// ---- 칸 값 추출(cells6.mjs 이식) ----
const flat = (rule, id) => { if (!rule) return null; if (!rule.candidates) return rule; const c = rule.candidates.find((x) => x.id === id); return c ? { ...rule, ...c } : null; };
const numeric = (d) => typeof d.threshold === 'number' ? { k: 'gte', v: d.threshold } : typeof d.threshold_days === 'number' ? { k: 'td', v: d.threshold_days } : typeof d.deadline_days === 'number' ? { k: 'dl', v: d.deadline_days, unit: d.unit } : typeof d.max_days === 'number' ? { k: 'md', v: d.max_days, unit: d.unit } : null;
const strict = (n) => (n.k === 'gte' ? n.v : -n.v);
const fmtNum = (n, unit = n.unit) => (n.k === 'gte' ? `${pn(n.v)}%` : `${n.v}${n.k === 'td' ? '일' : unit === 'business_days' ? '영업일' : '일'}`);
function describe(d) {
  if (d.not_regulated) return { t: '미규정', st: 'none' };
  if (d.unresearched) return { t: '값 없음', st: 'unknown' };
  if (d.delegated) return { t: '위임', st: 'deleg' };
  if (d.partial) return { t: '일부 규정', st: 'partial' };
  const n = numeric(d);
  return n ? { t: fmtNum(n), n, st: 'num' } : { t: '값 없음', st: 'unknown' };
}
function billCell(rule) { // 의원안 칸: 법안 10건 중 숫자를 정한 법안의 최소~최대, cnt는 [숫자를 정한 법안 수, 전체 법안 수]
  const d = flat(rule, 'bill');
  if (!d) return { t: '값 없음', st: 'unknown' };
  const x = describe(d), n = x.n;
  let lo = null, hi = null, mixed = false, cnt = null;
  if (n && rule.bills) {
    const nums = rule.bills.filter((b) => typeof b.value === 'number');
    if (nums.length) {
      cnt = [nums.length, rule.bills.length];
      const vs = nums.map((b) => b.value); lo = Math.min(...vs); hi = Math.max(...vs);
      const bd = nums.map((b) => b.unit === 'business_days');
      mixed = bd.some(Boolean) && !bd.every(Boolean);
      const u = bd.every(Boolean) ? '영업일' : '일';
      x.t = n.k === 'gte' ? (lo === hi ? `${pn(lo)}%` : `${pn(lo)}~${pn(hi)}%`) : (lo === hi ? `${lo}${u}` : `${lo}~${hi}${u}`);
    }
  }
  return { ...x, lo, hi, mixed, cnt };
}
function build() {
  const kr = J['kr-v1'].rules;
  return NUMR.map((rid) => {
    const cells = [billCell(kr[rid]), ...FOREIGN.map((id) => { const d = flat(J[id]?.rules?.[rid]); return d ? describe(d) : { t: '자료 없음', st: 'unknown' }; })];
    cells.forEach((c) => { c.rep = c.n ? strict(c.n) : null; });
    const vals = [...new Set(cells.map((c) => c.rep).filter((v) => v != null))].sort((a, b) => b - a);
    cells.forEach((c) => { if (c.rep != null && vals.length > 1) c.shade = Math.round(vals.indexOf(c.rep) * 2 / (vals.length - 1)); });
    return { rid, cells };
  });
}
const num = (c) => (c.st === 'num' ? (c.n.k === 'gte' ? pn(c.n.v) : c.n.v) : null);

// ---- 19 롤리팝 ----
function lolli(ctx, rows) {
  const r = ctx.data.reports[ctx.ri], bank = r?.bank != null ? r.bank * 100 : null;
  const cells = rows.find((x) => x.rid === 'R05').cells;
  const vs = cells.map(num).filter((v) => v != null), fvs = cells.slice(1).map(num).filter((v) => v != null); // 해외 값만 모아 범위 설명에 쓴다
  const maxv = Math.max(60, Math.ceil(Math.max(...vs, bank ?? 0) / 20) * 20);
  const W = widthOf(ctx, 860), cp = isNarrow(ctx, W), gap = cp ? 6 : 8;
  const base = 300, top = 56, h = (base - top) / maxv, x0 = cp ? 36 : 60, m = cp ? 8 : 20;
  // 넓은 판은 오른쪽에 '이 보고서' 이름표 자리(약 90px)를 남기고, 칸 하나는 최대 110px
  const p = Math.min(110, cp ? (W - x0 - 14 - gap) / 7 : (W - x0 - 14 - gap - 96) / 7), cx = (j) => x0 + p / 2 + j * p + (j >= 1 ? gap : 0);
  const two = p < 50; // 아주 좁으면 이름을 두 줄로
  let b = '';
  for (let t = 0; t <= maxv; t += 20) b += ln(x0 - 8, base - t * h, x0 + 7 * p + 8, base - t * h, t ? COL.line : COL.muted) + tx(x0 - 14, base - t * h + 4, t, { fill: COL.muted, anchor: 'end' });
  b += tx(cp ? 8 : 20, 40, '%', { fill: COL.muted });
  cells.forEach((c, j) => {
    const x = cx(j), v = num(c), kr = j < 1, col = kr ? COL.fill : COL.ok;
    if (v != null) b += ln(x, base, x, base - v * h, col, 2) + `<circle cx="${f(x)}" cy="${f(base - v * h)}" r="7" fill="${col}"/>` + tx(x, base - v * h - 13, `${v}%`, { weight: 700, anchor: 'middle' });
    else { const by = bank != null && Math.abs(base - bank * h - (base - 10)) < 16 ? base - bank * h - 8 : base - 10; b += tx(x, by, c.t, { fill: COL.muted, anchor: 'middle' }); }
    (two ? COLS[j].split(' ') : [COLS[j]]).forEach((s, i) => { b += tx(x, base + 22 + i * 13, s, { anchor: 'middle', attr: `data-country="${CIDS[j]}" style="cursor:pointer"` }); });
  });
  if (bank != null) {
    const y = base - bank * h, xe = x0 + 7 * p + gap + 8;
    b += ln(x0 - 8, y, xe, y, COL.ink, 1.5, 'stroke-dasharray="5 4"');
    if (!cp) b += tx(xe + 6, y - 2, '이 보고서', { weight: 700 }) + tx(xe + 6, y + 13, `은행 예금 ${f(bank)}%`);
  }
  const lg = base + (two ? 66 : 52), note = bank != null ? [`점선은 선택한 보고서(${r.coin} ${r.month})의`, `은행 예금 비율 ${f(bank)}%. 값이 없는 곳은 위임 또는 미규정`] : ['값이 없는 곳은 위임 또는 미규정', '선택한 보고서는 은행 예금 비율을 알 수 없음'];
  b += `<rect x="${m}" y="${lg - 9}" width="10" height="10" fill="${COL.fill}"/>` + tx(m + 15, lg, '한국', { fill: COL.muted }) + `<rect x="${m + 60}" y="${lg - 9}" width="10" height="10" fill="${COL.ok}"/>` + tx(m + 75, lg, '해외', { fill: COL.muted });
  b += tx(m, lg + 20, note[0], { fill: COL.muted }) + tx(m, lg + 36, note[1], { fill: COL.muted });
  return svg(W, lg + 48, `은행 예금 최저 비율, 해외 ${fvs.length}곳 중 ${Math.min(...fvs)}에서 ${Math.max(...fvs)}% 범위, 한국 의원안은 ${cells[0].t}`, b);
}

// ---- 02 값 표 ----
const HD = { R01: [['커버리지', '이상'], ['커버리지', '이상']], R03: [['국채 만기', '상한 이하'], ['국채', '만기', '이하']], R04: [['레포 만기', '이하'], ['레포', '만기', '이하']], R05: [['은행 예금', '비율 이상'], ['은행', '예금', '이상']], R10: [['공개 기한', '안'], ['공개', '기한', '안']], R13: [['돌려주는', '조건 안'], ['돌려주는', '조건', '안']] };
const repVals = (r) => ({ R01: r.coverage != null ? `${f(r.coverage * 100)}%` : null, R05: r.bank != null ? `${f(r.bank * 100)}%` : null, R10: r.sign_days != null ? `${r.sign_days}일` : null });
const cellFill = (c) => { const isn = c.st === 'num', s = c.shade; return { isn, fill: !isn ? 'none' : s == null ? COL.pale : COL.ok, op: s === 1 ? ' fill-opacity=".55"' : s === 2 ? ' fill-opacity=".25"' : '', tf: isn && s === 0 ? '#fff' : isn ? COL.ink : COL.muted }; };
function tableCompact(ctx, rows, W) { // 행과 열을 돌린다: 나라가 행, 규칙이 열
  const r = ctx.data.reports[ctx.ri];
  const x0 = 58, p = Math.min(80, (W - x0 - 4) / 6), cw = p - 3, y0 = 76, rp = 36, ch = 32, three = p < 60;
  const rep = repVals(r);
  let b = '', mixed = null;
  rows.forEach(({ rid }, k) => { const x = x0 + k * p + cw / 2, hd = HD[rid][three ? 1 : 0]; hd.forEach((s, i) => { b += tx(x, 24 + i * 14, s, { weight: i === 0 ? 700 : 400, fill: i === 0 ? COL.ink : COL.muted, anchor: 'middle' }); }); b += ln(x0 + k * p, 24 + (three ? 28 : 14) + 8, x0 + k * p + cw, 24 + (three ? 28 : 14) + 8, COL.ink); });
  const yy = three ? 76 : 60;
  const ry = (j) => yy + j * rp + (j >= 1 ? 6 : 0);
  COLS.forEach((n, j) => {
    const y = ry(j);
    b += tx(8, y + 18, n, { attr: `data-country="${CIDS[j]}" style="cursor:pointer"` });
    rows.forEach(({ rid, cells }, k) => {
      const c = cells[j], x = x0 + k * p, z = cellFill(c), n2 = c.cnt;
      b += `<rect x="${f(x)}" y="${f(y)}" width="${f(cw)}" height="${ch}" fill="${z.fill}"${z.op}${z.isn ? '' : ` stroke="${COL.line}"`}/>` + tx(x + cw / 2, y + (n2 ? 14 : 20), c.t, { anchor: 'middle', weight: z.isn ? 500 : 400, fill: z.tf }) + (n2 ? tx(x + cw / 2, y + 27, `${n2[0]}/${n2[1]}건`, { size: 10, anchor: 'middle', fill: z.tf }) : '');
      if (c.mixed) mixed = rid;
    });
  });
  const y = ry(6) + rp + 8;
  b += tx(8, y + 12, '이 보고서', { weight: 700 }) + tx(8, y + 25, r.coin.split(' ').pop(), { fill: COL.muted });
  rows.forEach(({ rid }, k) => { const v = rep[rid], x = x0 + k * p; b += `<rect x="${f(x)}" y="${f(y)}" width="${f(cw)}" height="${ch + 4}" fill="none" stroke="${COL.fill}"/>` + tx(x + cw / 2, y + 20, v ?? '—', { anchor: 'middle', weight: v ? 700 : 400, fill: v ? COL.ink : COL.muted }); });
  const [lb, H] = legend(b, y + ch + 4 + 24, 8, mixed, r);
  return svg(W, H, `숫자 규칙 ${rows.length}개의 기준값 표, 선택 보고서 ${r.coin} ${r.month}의 값 포함`, lb);
}
// 범례와 설명 줄을 b에 붙여 [본문, 전체 높이]로 돌려준다
function legend(b, lg, m, mixed, r) {
  const sw = (x, fill, op, stroke, s) => `<rect x="${x}" y="${lg - 9}" width="10" height="10" fill="${fill}"${op ? ` fill-opacity="${op}"` : ''}${stroke ? ` stroke="${stroke}" stroke-width=".5"` : ''}/>` + tx(x + 15, lg, s, { fill: COL.muted });
  b += sw(m, COL.ok, 0, '', '가장 엄격') + sw(m + 85, COL.ok, '.55', '', '중간') + sw(m + 145, COL.ok, '.25', '', '느슨') + sw(m + 205, COL.pale, 0, COL.stone, '비교 값이 하나뿐');
  const notes = ['이상은 큰 값, 이하와 안은 작은 값이 엄격', '의원안은 숫자를 정한 법안의 최소~최대, 작은 글은 법안 수', ...(mixed ? [`의원안 ${RN[mixed]}은 일과 영업일이 섞인 범위`] : []), `이 보고서 칸은 ${r.coin} ${r.month}의 실제 값`, '(커버리지, 은행 예금 비율, 서명까지 걸린 일수)'];
  notes.forEach((s, i) => { b += tx(m, lg + 20 + i * 16, s, { fill: COL.muted }); });
  return [b, lg + 20 + (notes.length - 1) * 16 + 12];
}
function table(ctx, rows) {
  const W = widthOf(ctx, 760), r = ctx.data.reports[ctx.ri];
  if (isNarrow(ctx, W)) return tableCompact(ctx, rows, W);
  const x0 = W < 760 ? 112 : 150, p = Math.min(90, (W - x0 - 12 - 72 - 12 - 4) / 7), cw = p - 3, gx = (j) => x0 + j * p + (j >= 1 ? 4 : 0), rx = gx(6) + p + 12, rw = Math.min(W - 12 - rx, 130), y0 = 80, rp = 44, m = 12;
  const grp = (a, z, s) => tx((a + z) / 2, 44, s, { weight: 700, anchor: 'middle' }) + ln(a, 50, z, 50, COL.ink);
  let b = grp(gx(0), gx(0) + cw, '한국') + grp(gx(1), gx(6) + cw, '해외') + grp(rx, rx + rw, '이 보고서');
  COLS.forEach((n, j) => { b += tx(gx(j) + cw / 2, 68, n, { fill: COL.muted, anchor: 'middle', attr: `data-country="${CIDS[j]}" style="cursor:pointer"` }); });
  b += tx(rx + rw / 2, 68, r.coin.split(' ').pop(), { fill: COL.muted, anchor: 'middle' });
  const rep = repVals(r);
  let mixed = null;
  rows.forEach(({ rid, cells }, i) => {
    const y = y0 + i * rp;
    b += tx(m, y + 16, RN[rid]) + tx(m, y + 31, `${DIR[rid]} 기준`, { fill: COL.muted });
    cells.forEach((c, j) => {
      const x = gx(j), z = cellFill(c), n2 = c.cnt;
      b += `<rect x="${f(x)}" y="${y}" width="${f(cw)}" height="38" fill="${z.fill}"${z.op}${z.isn ? '' : ` stroke="${COL.line}"`}/>` + tx(x + cw / 2, y + (n2 ? 17 : 24), c.t, { anchor: 'middle', weight: z.isn ? 500 : 400, fill: z.tf }) + (n2 ? tx(x + cw / 2, y + 31, `${n2[1]}건 중 ${n2[0]}건`, { size: 10, anchor: 'middle', fill: z.tf }) : '');
      if (c.mixed) mixed = rid;
    });
    const v = rep[rid];
    b += `<rect x="${f(rx)}" y="${y}" width="${f(rw)}" height="38" fill="none" stroke="${COL.fill}"/>` + tx(rx + rw / 2, y + 24, v ?? '—', { anchor: 'middle', weight: v ? 700 : 400, fill: v ? COL.ink : COL.muted });
  });
  const [lb, H] = legend(b, y0 + rows.length * rp + 18, m, mixed, r);
  return svg(W, H, `숫자 규칙 ${rows.length}개의 기준값 표, 선택 보고서 ${r.coin} ${r.month}의 값 포함`, lb);
}

export function views(ctx) {
  if (ctx.J) J = ctx.J;
  if (!J) return [{ key: '19', label: '롤리팝', html: svg(widthOf(ctx, 480), 40, '기준값 파일을 불러오지 못함', tx(10, 24, '기준값 파일을 불러오지 못했습니다', { fill: COL.muted })) }];
  const rows = build();
  return [{ key: '19', label: '롤리팝', html: lolli(ctx, rows) }, { key: '02', label: '값 표', html: table(ctx, rows) }];
}
