// 구역 4 규칙별 판정: 02 히트맵 행렬(문자 병기), 20 표와 막대 셀. 판정은 ctx.data.reports[ri].verdicts 에서 계산.
import { COL, SHORT, ORDER, flagImg } from './data.js';

// 사이트 화면문구.json 규칙15개와 같은 짧은 이름(칸 폭 때문에 긴 요구 문장 대신 사용)
const RN = { R01: '커버리지 100% 이상', R02: '허용 자산 종류', R03: '국채 만기 상한', R04: '레포 만기', R05: '은행 예금 최저 비율', R06: '준비금 통화 일치', R07: '공개 주기', R08: '검증 수준', R09: '검증 기준시각', R10: '공개 기한', R11: '발행잔액 계산식 공개', R12: '보관 기관 공개', R13: '돌려주는 조건', R14: '이자 지급 금지', R15: '경영진 서명' };
const ST = [['met', '충족', COL.ok], ['caution', '주의', COL.warn], ['unmet', '미충족', COL.bad], ['none', '판정 안 됨', COL.stone]];
const LAB = Object.fromEntries(ST.map(([k, l]) => [k, l]));
const FILL = Object.fromEntries(ST.map(([k, , c]) => [k, c]));
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const tx = (x, y, s, o = {}) => `<text x="${x}" y="${y}" font-size="${o.size || 12}" font-weight="${o.w || 400}" fill="${o.fill || COL.ink}" text-anchor="${o.anchor || 'start'}"${o.extra || ''}>${esc(s)}</text>`;
const rc = (x, y, w, h, fill, extra = '') => `<rect x="${x}" y="${y}" width="${Math.max(w, 0)}" height="${h}" fill="${fill}"${extra}/>`;
const svg = (W, H, label, body) => `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" style="display:block;max-width:none" font-family="inherit" role="img" aria-label="${esc(label)}">${body}</svg>`;
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
// 좁은 판용: 공백 기준으로 최대 m자씩 두 줄까지 나눔
const wrap = (s, m = 9) => { if (s.length <= m) return [s]; const w = s.split(' '); let a = ''; while (w.length && (a + ' ' + w[0]).trim().length <= m) a = (a + ' ' + w.shift()).trim(); return a ? [a, w.join(' ')].filter(Boolean) : [s.slice(0, m), s.slice(m)]; };
const nameCell = (r, y, rh, x, narrow) => {
  if (!narrow) return tx(x, y + 14, RN[r], { size: 12 });
  const L = wrap(RN[r]), top = y + (rh - 4) / 2 - (L.length - 1) * 6.5 + 4;
  return L.map((l, i) => tx(x, top + i * 13, l, { size: 11 })).join('');
};
// 범례: 판정 4종을 한 줄로, 설명은 넓으면 같은 줄 뒤에 좁으면 아랫줄에. 높이 반환
const legend = (y, note, narrow) => {
  let x = 0, b = '';
  for (const [, l, c] of ST) { b += rc(x, y - 10, 11, 11, c) + tx(x + 16, y, l, { size: 11, fill: COL.muted }); x += 16 + l.length * 11 + 14; }
  if (!note) return { b, h: 0 };
  return narrow ? { b: b + tx(0, y + 18, note, { size: 11, fill: COL.muted }), h: 18 } : { b: b + tx(x + 6, y, note, { size: 11, fill: COL.muted }), h: 0 };
};

export function views({ data, ri, width, compact , side: sideMode = 'nums', krSplit = {} }) {
  const rep = data.reports[ri] || data.reports[0];
  const V = rep.verdicts, RS = Object.keys(V[ORDER[0]]), n = ORDER.length;
  const TR = Object.fromEntries(RS.map((r) => [r, Object.fromEntries(ST.map(([k]) => [k, ORDER.filter((c) => V[c][r] === k).length]))]));
  const total = n * RS.length, judged = ORDER.flatMap((c) => RS.map((r) => V[c][r])).filter((s) => s !== 'none').length;
  const who = `${rep.coin} ${rep.month}`;
  // 칸 폭 1:1. width 없으면 compact는 520, 아니면 기본 766. 360 아래는 360으로 그림
  const W = Math.round(Math.max(360, width || (compact ? 520 : 766))), narrow = W < 680;

  // 02 히트맵 행렬(문자 병기): 규칙 x 나라, 칸 안에 판정 글자
  const heat = (() => {
    // 넓은 칸(1000 이상)은 오른쪽에 규칙별 판정 수 표를 같은 줄에 붙인다: 구성 막대(나라 1곳 = 1칸) + 판정 4종 숫자(열마다 오른쪽 맞춤)
    const showBar = sideMode !== 'nums', showNum = sideMode !== 'bars', BU = sideMode === 'bars' ? 24 : 16, BW = showBar ? n * BU : 0, NC = showNum ? [44, 44, 52, 66] : [];
    const side = !narrow && W >= 1000 && sideMode !== 'none', SIDE = side ? 28 + BW + (showBar && showNum ? 12 : 0) + NC.reduce((a, b) => a + b, 0) : 0;
    const x0 = narrow ? 100 : 214, p = narrow ? (W - x0 - 4) / n : clamp((W - x0 - 6 - SIDE) / n, 66, 170);
    const sx = x0 + n * p + 28, nx = NC.map((w, j) => sx + BW + (showBar ? 12 : 0) + NC.slice(0, j + 1).reduce((a, b) => a + b, 0)); // nx = 숫자 열의 오른쪽 끝
    const FH = narrow ? 13.5 : Math.min(54, Math.round((p - 24) * 0.75)); // 넓은 칸은 국기를 생키처럼 크게
    const nameY = narrow ? 38 : 6 + FH + 22, y0 = narrow ? 76 : nameY + 14, rh = narrow ? 30 : 26, short = p < 50;
    let b = ORDER.map((c, j) => {
      const cx = x0 + j * p + p / 2, hd = ` data-country="${c}" style="cursor:pointer"`, w = c === 'kr-v1' ? 700 : 500;
      return flagImg(c, cx - FH * 2 / 3, 6, FH) + (narrow ? `<text transform="translate(${cx + 4},${y0 - 6}) rotate(-90)" font-size="12" font-weight="${w}" fill="${COL.ink}"${hd}>${esc(SHORT[c])}</text>` : tx(cx, nameY, SHORT[c], { size: 12, w, anchor: 'middle', extra: hd }));
    }).join('');
    if (side) b += (showBar ? tx(sx, nameY, `판정 구성 (${n}곳)`, { size: 12, fill: COL.muted }) : '') + (showNum ? ST.map(([k, l, c], j) => tx(nx[j], nameY, l, { size: 12, w: 700, anchor: 'end', fill: k === 'none' ? COL.muted : c })).join('') : '');
    let splitN = 0;
    RS.forEach((r, i) => {
      const y = y0 + i * rh, ty = y + (rh - 4) / 2 + 4;
      b += nameCell(r, y, rh, 0, narrow) + (narrow ? '' : tx(x0 - 8, ty, r, { size: 11, fill: COL.muted, anchor: 'end' }));
      if (side) { let bx = sx; ST.forEach(([k, , c], j) => { const v = TR[r][k]; if (v && showBar) { b += rc(bx, y, v * BU - 1, rh - 4, c) + (showNum ? '' : tx(bx + v * BU / 2, ty, v, { size: 12, anchor: 'middle', w: 700, fill: k === 'none' ? COL.muted : '#fff' })); bx += v * BU; } if (showNum) b += tx(nx[j], ty, v, { size: 12, anchor: 'end', w: v ? 600 : 400, fill: v ? COL.ink : COL.stone }); }); }
      ORDER.forEach((c, j) => {
        const s = V[c][r], t = s === 'none' ? '-' : short ? LAB[s][0] : LAB[s];
        // 한국 칸: 후보(의원안 값마다, 해외 참조 등)에 따라 판정이 갈리면 칸 아래에 후보 수만큼 나눈 띠를 각 후보 판정 색으로. 글자는 띠 위로 올림
        const ks = c === 'kr-v1' ? krSplit[r] : null, split = !!ks && new Set(ks.map((k) => k.s).filter((x) => x !== 'none')).size > 1;
        b += rc((x0 + j * p + 1).toFixed(1), y, (p - 2).toFixed(1), rh - 4, FILL[s]) + tx((x0 + j * p + p / 2).toFixed(1), split ? ty - 3 : ty, t, { size: split ? 11 : 12, anchor: 'middle', fill: s === 'none' ? COL.muted : '#fff' });
        if (split) {
          const sw = (p - 2) / ks.length, sy = y + rh - 4 - 4;
          b += `<g><title>${esc(`한국 ${r} 후보별 판정: ${ks.map((k) => `${k.n} ${LAB[k.s] || '판정 안 됨'}`).join(', ')}`)}</title>` + rc((x0 + j * p + 1).toFixed(1), sy - 1, (p - 2).toFixed(1), 5, '#fff') + ks.map((k, q) => rc((x0 + j * p + 1 + q * sw + (q ? 1 : 0)).toFixed(1), sy, (sw - (q ? 1 : 0)).toFixed(1), 4, FILL[k.s])).join('') + '</g>';
          splitN++;
        }
      });
    });
    const ly = y0 + RS.length * rh + 22, lg = legend(ly, '', narrow);
    const sn = splitN ? tx(x0, ly + 22, `한국 칸 아래 여러 색 띠: 후보값(의원안 값마다, 해외 참조)에 따라 판정이 갈리는 규칙 ${splitN}개. 칸 색은 지금 고른 후보의 판정`, { size: 11, fill: COL.muted }) : '';
    return svg(W, ly + (splitN ? 34 : 12), `${who} 규칙 ${RS.length}개 x 나라 ${n}곳 판정 행렬. ${total}칸 중 ${judged}칸에서 판정이 나옴`, b + lg.b + sn);
  })();

  // 20 표와 막대 셀: 규칙마다 판정별 나라 수
  const tab = (() => {
    const x0 = narrow ? 100 : 214, cw = narrow ? (W - x0 - 4) / ST.length : clamp((W - x0) / ST.length, 110, 180);
    const bu = narrow ? (cw - 22) / n : clamp((cw - 36) / n, 12, 18), y0 = narrow ? 44 : 52, rh = narrow ? 30 : 26;
    let b = ST.map(([k, l, c], j) => tx(x0 + j * cw, y0 - 18, l, { size: narrow ? 11 : 12, w: 700, fill: k === 'none' ? COL.muted : c })).join('');
    RS.forEach((r, i) => {
      const y = y0 + i * rh, ty = y + (rh - 4) / 2 + 4;
      if (i % 2 === 0) b += rc(0, y - 4, W, rh, COL.surface);
      b += nameCell(r, y, rh, 4, narrow) + (narrow ? '' : tx(x0 - 8, ty, r, { size: 11, fill: COL.muted, anchor: 'end' }));
      ST.forEach(([k, , c], j) => {
        const v = TR[r][k], x = x0 + j * cw;
        b += (v ? rc(x.toFixed(1), y, (v * bu).toFixed(1), rh - 8, c) : '') + tx((x + v * bu + 5).toFixed(1), ty, v, { size: 12, fill: v ? COL.ink : COL.muted });
      });
    });
    const ly = y0 + RS.length * rh + 22, lg = legend(ly, `막대 길이와 숫자: 해당 판정을 받은 나라 수(${n}곳 중)`, narrow);
    return svg(W, ly + lg.h + 12, `${who} 규칙별로 판정마다 나라 몇 곳인지(${n}곳 중)`, b + lg.b);
  })();

  return [{ key: '02', label: '히트맵 행렬', html: heat }, { key: '20', label: '표와 막대 셀', html: tab }];
}
