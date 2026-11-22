// 구역 9. 두 나라 비교: 15 표와 막대 셀, 02 차이만 강조한 행렬
import { COL, SHORT, flagImg } from './data.js';

const RN = { R01: '커버리지 100% 이상', R02: '허용 자산 종류', R03: '국채 만기 상한', R04: '레포 만기', R05: '은행 예금 최저 비율', R06: '준비금 통화 일치', R07: '공개 주기', R08: '검증 수준', R09: '검증 기준시각', R10: '공개 기한', R11: '발행잔액 계산식 공개', R12: '보관 기관 공개', R13: '돌려주는 조건', R14: '이자 지급 금지', R15: '경영진 서명' };
const SC = { met: COL.ok, caution: COL.warn, unmet: COL.bad, none: COL.stone };
const SN = { met: '충족', caution: '주의', unmet: '미충족', none: '판정 안 됨' };
const ORD = ['met', 'caution', 'unmet', 'none'];
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const f = (n) => +Number(n).toFixed(1);
const tw = (s, size) => [...String(s)].reduce((a, ch) => a + (ch.charCodeAt(0) > 255 ? size : /[A-Z]/.test(ch) ? size * .66 : /[a-z0-9]/.test(ch) ? size * .58 : ch === ' ' ? size * .3 : size * .45), 0);
const T = (x, y, s, o = {}) => `<text x="${f(x)}" y="${f(y)}" font-size="${o.s || 12}" fill="${o.c || COL.ink}"${o.w ? ` font-weight="${o.w}"` : ''}${o.a ? ` text-anchor="${o.a}"` : ''}${o.at || ''}>${esc(s)}</text>`;
const Rc = (x, y, w, h, fill, o = {}) => `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" fill="${fill}"${o.op != null ? ` fill-opacity="${o.op}"` : ''}${o.rx ? ` rx="${o.rx}"` : ''}/>`;
const Ln = (x1, y1, x2, y2) => `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke="${COL.line}" stroke-width="1"/>`;
const ym = (m) => `${m.slice(0, 4)}년 ${Number(m.slice(5))}월`;
const svg = (W, H, label, body) => `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" style="display:block;max-width:none" font-family="inherit" role="img" aria-label="${esc(label)}">${body}</svg>`;

function legend(x0, y, items, W) {
  let x = x0, o = '', n = 0;
  for (const [c, t, op] of items) {
    const w = 17 + tw(t, 11);
    if (x > x0 && x + w > W) { x = x0; n++; }
    o += Rc(x, y - 10 + n * 18, 12, 12, c, { op }) + T(x + 17, y + n * 18, t, { s: 11, c: COL.muted });
    x += w + 20;
  }
  return [o, n * 18];
}

export function views({ data, ri, cmp, focus, width }) {
  const wid = Number(width) > 0 ? Math.max(360, Number(width)) : 0;
  const R = data.reports, N = R.length, rp = R[ri] || R[0];
  const rids = Object.keys(rp.verdicts[focus]);
  const cn = SHORT[cmp] || cmp, fn = SHORT[focus] || focus;
  const K = rp.verdicts[focus], U = rp.verdicts[cmp];
  // 갈림 = 두 나라 모두 판정이 났는데 결과가 다름. 한쪽만 판정 안 됨(위임, 정함 없음 등)이면 갈림으로 세지 않고 '한쪽만 판정'으로 따로 보임
  const split = (a, b) => a !== b && a !== 'none' && b !== 'none';
  const diff = rids.filter((k) => split(K[k], U[k])), oneSide = rids.filter((k) => K[k] !== U[k] && !split(K[k], U[k]));
  const cnt = Object.fromEntries(rids.map((k) => [k, R.filter((r) => split(r.verdicts[focus][k], r.verdicts[cmp][k])).length]));
  const rpt = `${rp.coin} ${ym(rp.month)}`;
  const ctry = (x, y, id, nm, a, fh = 13.5) => `<g data-country="${id}" style="cursor:pointer">${flagImg(id, x - fh * 2 / 3, y - 16.5 - fh, fh)}${T(x, y, nm, { s: 12, w: 700, a })}</g>`;
  const note = T(0, 14, `선택 보고서 ${rpt}`, { s: 11, c: COL.muted });
  const aria = `규칙 15개 판정, ${fn}과 ${cn} 비교. ${rpt}에서 판정이 갈린 규칙 ${diff.length}개`;

  // 15 표와 막대 셀 (폭 640 미만이면 이름 아래 줄에 칸과 막대)
  const t15 = (() => {
    const W = wid || 800, c = W < 640, rh = c ? 44 : 26, y0 = c ? 62 : 72, hy = y0 - 8, fh = c ? 13.5 : 36, cw = c ? 92 : W >= 900 ? 100 : 84;
    const cx1 = c ? 0 : 270, cx2 = cx1 + cw + 8, bx = c ? cx2 + cw + 12 : cx2 + cw + 40, bw = Math.max(60, Math.min(W - bx - 40, 520));
    let b = note + (c ? '' : T(0, hy, '규칙', { s: 11, c: COL.muted })) + ctry(cx1 + cw / 2 + (c ? 9 : 0), hy, focus, fn, 'middle', fh) + ctry(cx2 + cw / 2 + (c ? 9 : 0), hy, cmp, cn, 'middle', fh) + T(bx, hy, `판정이 갈린 보고서(두 나라 모두 판정, ${N}건 중)`, { s: 11, c: COL.muted }) + Ln(0, y0 - 2, W, y0 - 2);
    const dy = c ? 22 : 0;
    rids.forEach((k, i) => {
      const y = y0 + i * rh, d = diff.includes(k), n = cnt[k];
      b += Ln(0, y + rh, W, y + rh);
      b += T(0, y + 17, `${k}  ${RN[k] || ''}`, { s: 12.5, w: d ? 700 : 400, c: d ? COL.ink : COL.muted });
      for (const [x, v] of [[cx1, K[k]], [cx2, U[k]]]) b += Rc(x, y + 4 + dy, cw, 18, SC[v], { rx: 2 }) + T(x + cw / 2, y + 17 + dy, SN[v], { s: 11, a: 'middle', c: v === 'none' ? COL.ink : '#fff' });
      if (n) b += Rc(bx, y + 7 + dy, Math.max(2, n / N * bw), 12, COL.fill, { rx: 1 });
      b += T(bx + (n ? Math.max(2, n / N * bw) + 6 : 0), y + 17 + dy, n, { s: 12, c: n ? COL.ink : COL.muted });
    });
    const [lg, lh] = legend(0, y0 + 15 * rh + 30, ORD.map((s) => [SC[s], SN[s]]), W);
    return svg(W, y0 + 15 * rh + 52 + lh, aria, b + lg);
  })();

  // 02 차이만 강조한 행렬
  const t02 = (() => {
    const W = wid || 760, c = W < 640, rh = c ? 44 : 26, y0 = c ? 62 : 72, hy = y0 - 8, fh = c ? 13.5 : 36, cw = c ? 92 : W >= 900 ? 120 : 100;
    const cx1 = c ? 0 : 270, cx2 = cx1 + cw + (c ? 8 : 6), dy = c ? 22 : 0;
    let b = note + ctry(cx1 + cw / 2 + (c ? 9 : 0), hy, focus, fn, 'middle', fh) + ctry(cx2 + cw / 2 + (c ? 9 : 0), hy, cmp, cn, 'middle', fh);
    rids.forEach((k, i) => {
      const y = y0 + i * rh, d = diff.includes(k);
      b += T(0, y + 17, `${k}  ${RN[k] || ''}`, { s: 12.5, w: d ? 700 : 400, c: d ? COL.ink : COL.muted });
      const shown = d || oneSide.includes(k);
      for (const [x, v] of [[cx1, K[k]], [cx2, U[k]]]) {
        b += Rc(x, y + 3 + dy, cw, 20, SC[v], { op: shown ? 1 : 0.28, rx: 2 });
        if (shown) b += T(x + cw / 2, y + 17 + dy, SN[v], { s: 11, a: 'middle', c: v === 'none' ? COL.ink : '#fff' });
      }
      if (d) b += T(cx2 + cw + 16, y + 17 + dy, '갈림', { s: 12, w: 700 });
      else if (oneSide.includes(k)) b += T(cx2 + cw + 16, y + 17 + dy, '한쪽만 판정', { s: 11, c: COL.muted });
      if (c) b += Ln(0, y + rh, W, y + rh);
    });
    const [lg, lh] = legend(0, y0 + 15 * rh + 30, [...ORD.map((s) => [SC[s], SN[s]]), [COL.muted, '옅은 칸: 두 나라 판정이 같음', 0.28]], W);
    return svg(W, y0 + 15 * rh + 52 + lh, aria, b + lg);
  })();

  return [{ key: '15', label: '표와 막대 셀', html: t15 }, { key: '02', label: '차이만 강조', html: t02 }];
}
