// 나라별 구조 흐름도: 가로로 낮은 입체(아이소메트릭) 블록 도식.
// 블록과 선의 자리는 모든 나라가 같고, 이름표와 선 이름표의 문구와 자리만 나라마다 바뀝니다.
// 감독 블록은 실제 건물 사진을 보고 그대로 옮긴 모양(서울 정부서울청사 본관, 홍콩 Two IFC, 싱가포르 MAS 빌딩, 도쿄 중앙합동청사 제7호관 서관, 파리 Tour Europlaza)이거나, 감독기관이 여럿인 미국(연방 기관 넷)과 EU 일반(회원국 감독기관 다섯)은 그 기관들의 본부 건물을 한 바닥판에 모은 묶음이고, 사진으로 한 건물을 특정할 수 없으면 네모 상자입니다.
// 칸 좌표 (a, b): 가로로 a칸, 세로로 b칸. a와 b의 홀짝이 같은 점이 격자 교점입니다.
// isoFlowSvg(spec, { name, id }): 오른쪽 열 그림과 크게 보기 대화 상자가 같은 전체판(블록 이름표 줄과 선 이름표를 모두 쓴 판)을 씁니다.
// 이름표, 선 이름표, 꼬리표는 뒤에 번진 흰 테두리(iso-halo)와 글자 둘레 흰 선(styles.css)으로 젖빛 유리처럼 보이게 해 격자와 선이 글자를 가로지르지 않습니다.
import { BUILDINGS } from './iso_buildings.js';
import { BUILDINGS2 } from './iso_buildings2.js';
import { usRegulators } from './iso_clusters_us.js';
import { euNcaGroup } from './iso_eu_authorities.js';
import { coinStacks } from './iso_coins.js';
import { bankBuilding } from './iso_bank.js';
import { vaultBuilding } from './iso_vault.js';
// 보관: 규칙에 은행 예치가 적힌 곳(EU 일반, EU 중요, 한국)은 은행 건물, 은행으로 정하지 않은 곳은 금고(미국, 홍콩은 보관 기관, 싱가포르, 일본은 신탁)
const VAULT = { us: 'CUSTODY', hk: 'CUSTODY', sg: 'TRUST', jp: 'TRUST' };
// 검증 블록 윗면 글자: 법이 요구하는 검증 종류(어느 회계법인인지는 발행사가 고르므로 법인은 그리지 않는다). 없는 나라는 체크 그림
const VERIFY = { us: 'ATTEST', hk: 'ATTEST', sg: 'ATTEST', 'eu-emt-significant': 'AUDIT', 'kr-v1': 'REVIEW', jp: 'CERT' };
import { personFigure } from './iso_person.js';
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const HW0 = 40, SP = 1.2;                // 칸 한 개의 윗면 반폭(px)과 칸 간격 배율. 물체 크기는 그대로 두고 칸 간격만 넓힌다
const HW = HW0 * SP, HH = HW * 15 / 26;  // 한 칸 반폭, 반높이(px)
const C30 = Math.sqrt(3) / 2;            // 입체 좌표에서 길이 1이 화면 가로로 가는 몫(세로는 1/2)
const F1 = 13, F2 = 12;                  // 이름표 이름, 이름표 줄과 선 이름표 글자 크기
const FROST = 4, BLUR = 3;               // 이름표 뒤 흰 번짐: 이름표보다 사방으로 더 나오는 거리(px)와 흐림 정도(가우시안 표준편차)
const f = (n) => Math.round(n * 10) / 10;
const g5 = (n) => Math.round(n * 1e5) / 1e5;
const pts = (a) => a.map(([x, y]) => `${f(x)},${f(y)}`).join(' ');
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

// 글자 폭 어림(em). Pretendard 실측: 한글은 굵기와 상관없이 .864, 나머지는 굵으면 조금 더 넓다. 3% 여유
const REG = { han: .864, digit: .583, up: .641, low: .505, sp: .251, pct: .862, comma: .258, paren: .341, other: .6, misc: .4 };
const BLD = { han: .864, digit: .61, up: .665, low: .535, sp: .235, pct: .94, comma: .28, paren: .385, other: .6, misc: .42 };
const cw = (K, c) => c > '⹿' ? K.han : c > '\u007f' ? K.other : /\d/.test(c) ? K.digit : /[A-Z]/.test(c) ? K.up : /[a-z]/.test(c) ? K.low : c === ' ' ? K.sp : c === '%' ? K.pct : /[,.:;]/.test(c) ? K.comma : /[()[\]]/.test(c) ? K.paren : K.misc;
const tw = (s, fs, bold) => [...String(s)].reduce((n, c) => n + cw(bold ? BLD : REG, c), 0) * fs * 1.03;
// 공백에서 줄을 바꾸고, 한 단어가 폭보다 길면 글자 단위로 자른다
function fill(text, fs, max, bold) {
  const rows = []; let cur = '';
  for (const word of String(text ?? '').split(/\s+/).filter(Boolean)) {
    const t = cur ? `${cur} ${word}` : word;
    if (!cur || tw(t, fs, bold) <= max) { cur = t; continue; }
    rows.push(cur); cur = word;
  }
  if (cur) rows.push(cur);
  return rows.flatMap((row) => {
    if (tw(row, fs, bold) <= max) return [row];
    const cut = []; let s = '';
    for (const c of row) { if (s && tw(s + c, fs, bold) > max) { cut.push(s); s = ''; } s += c; }
    return s ? [...cut, s] : cut;
  });
}
// 줄 수는 그대로 두고 폭을 줄여, 마지막 줄에 한두 글자만 남지 않게 줄 길이를 고른다
function wrap(text, fs, max, bold) {
  const rows = fill(text, fs, max, bold);
  if (rows.length < 2) return rows;
  let lo = 0, hi = max;
  for (let i = 0; i < 8; i++) { const mid = (lo + hi) / 2; if (fill(text, fs, mid, bold).length <= rows.length) hi = mid; else lo = mid; }
  return fill(text, fs, hi, bold);
}

// ---- 장면: 가운데 줄에 이용자, 발행사, 준비금, 보관이 왼쪽에서 오른쪽으로 서고, 뒷줄(위)에 감독과 검증, 앞줄(아래)에 공개가 선다 ----
// 블록은 모두 격자 교점에 서고, 가운데 줄 밖의 블록은 가운데 줄 블록에서 ±30도 선(칸 방향) 위로 3칸, 4칸 떨어진다
const X0 = 80;
// 장판: 판정 항목 4묶음(app.js GROUPS)마다 그 규칙을 보는 블록 밑에 까는 옅은 판. 바닥에 묶음 이름과 규칙 번호를 눕혀 쓴다
// 발행사는 모든 규칙의 대상이라, 감독은 규칙을 정하는 쪽이라 장판 밖에 둔다
// u=(a+b)/2는 오른쪽 아래, v=(a-b)/2는 오른쪽 위 방향 칸 좌표. 블록 바닥 윤곽에서 0.1~0.2칸 더 나가고, 오른쪽 아래 가장자리(u 끝) 0.6칸은 글자 자리다
const ZONES = [
  { name: '상환과 이자', rules: 'R13, R14', u: [-.55, 1.15], v: [-.65, .75] },
  { name: '공개 방식', rules: 'R07, R10~R12', u: [3.5, 5.15], v: [-.72, .72] },
  { name: '준비금 규모와 구성', rules: 'R01~R06', u: [6.1, 11.3], v: [6.1, 10.6] },
  { name: '검증과 서명', rules: 'R08, R09, R15', u: [6, 8.6], v: [11.35, 12.75] },
];
const ZU = HW0 * SP / C30;               // 칸 한 개의 바닥 길이(입체 좌표 px)
// 흐름별 2묶음(보는 사람이 고를 때): 앞은 이용자와 발행사 사이에 코인이 오가는 쪽, 뒤는 받은 돈이 준비금으로 쌓이는 쪽. 규칙 번호는 4묶음을 합친 것
const ZONES_FLOW = [
  { name: '발행과 상환', rules: 'R07, R10~R14', u: [-.6, 5], v: [-.6, 5] },
  { name: '준비금 관리', rules: 'R01~R06, R08, R09, R15', u: [6, 10.75], v: [6.05, 11.5] },
];
const CELL = { 이용자: [0, 0], 공개: [4, 4], 발행사: [8, 0], 감독: [12, -4], 준비금: [14, 0], 검증: [19, -5], 보관: [20, 0] };
const MODES = { group: { zones: ZONES, cell: CELL }, flow: { zones: ZONES_FLOW, cell: { ...CELL, 검증: [18, -4] } } };   // 4묶음은 검증이 준비금 장판과 떨어지게 한 칸 오른쪽 위
// sides: 이름표를 놓아 볼 방향 순서(t 위, b 아래, l 왼쪽, r 오른쪽)
const SIDES = { 이용자: 'tbl', 공개: 'lrbt', 발행사: 'blr', 감독: 'tlrb', 준비금: 'btrl', 검증: 'tlrb', 보관: 'btrl', 코인: 'trl' };
const ORDER = ['감독', '검증', '이용자', '공개', '발행사', '준비금', '보관'];  // 블록 이름표 항목 순서
const W = Math.ceil(X0 + 20 * HW + 56 + 70);
const FLAG = { us: 'us', 'eu-emt': 'eu', 'eu-emt-significant': 'eu', hk: 'hk', sg: 'sg', jp: 'jp', 'kr-v1': 'kr' };
// 코인 표면(발행사 윗면과 준비금 동전 윗면)에 새기는 나라 통화 기호. 없는 나라는 고리만 그린다.
// 나라 기준이라, 이름표의 코인이 다른 통화(미국의 EURC, 싱가포르의 Paxos USDG는 달러 코인)여도 나라 통화로 쓴다. 싱가포르를 달러로 보이게 하려면 'S$'를 '$'로 바꾼다
const CUR = { us: '$', 'eu-emt': '€', 'eu-emt-significant': '€', hk: 'HK$', sg: 'S$', jp: '¥', 'kr-v1': '₩' };
// 감독 블록이 베끼는 실제 건물(미국과 EU 일반은 감독기관 여럿의 본부 건물을 한 바닥판에 모은 묶음). 없으면 네모 상자
const BUILDING = { 'kr-v1': 'seoul', hk: 'ifc', sg: 'mas', jp: 'fsa', 'eu-emt-significant': 'eba', us: 'us4', 'eu-emt': 'eu5' };
const TITLE_COIN = 'SC2K 자료의 코인';
const DRAW = { ...BUILDINGS, ...BUILDINGS2, us4: usRegulators, eu5: euNcaGroup };   // BUILDING의 값으로 찾는 그리기 함수: (cx, cy, 국기 파일) -> { el, ps }

// ---- 물체 그리기 ----
// 입체 좌표 (x, y, z): x는 오른쪽 아래, y는 왼쪽 아래로 가는 바닥 길이(px), z는 위로 가는 높이(px). 세 길이가 화면에서 같은 크기로 보이는 정등각이다.
// 바깥 윤곽(iso-face)은 겹침 검사와 이름표 자리 잡기에 쓰인다. 창, 기둥, 국기, 그림 같은 세부(iso-d, iso-fl, iso-flag, iso-mark)는 윤곽 안에만 그린다.
const hull = (a) => {
  const p = [...a].sort((m, n) => m[0] - n[0] || m[1] - n[1]), cr = (o, m, n) => (m[0] - o[0]) * (n[1] - o[1]) - (m[1] - o[1]) * (n[0] - o[0]);
  const half = (q) => { const r = []; for (const t of q) { while (r.length > 1 && cr(r[r.length - 2], r[r.length - 1], t) <= 0) r.pop(); r.push(t); } r.pop(); return r; };
  return [...half(p), ...half([...p].reverse())];
};
// 코인 윗면: 고리 하나와 나라 통화 기호 하나. 고리 반지름은 그림 좌표다
const COIN_R = 16.5;
// 통화 기호의 잉크 상자 [폭, 높이](글자 크기 1일 때, Pretendard 800 실측). 기호를 고리 안에 꼭 맞추는 데 쓴다
const INK = { $: [.573, .885], '€': [.592, .727], '¥': [.535, .707], '₩': [.881, .707], 'HK$': [1.944, .885], 'S$': [1.211, .885] };
const symText = (sym) => {
  if (!INK[sym]) return '';
  const [w, h] = INK[sym], s = Math.min(1.78, 1.76 / Math.hypot(w, h)) * COIN_R;   // 잉크 상자의 대각선이 고리 지름의 88%를 넘지 않게, 한 글자는 높이도 제한
  return `<text class="iso-coin-sym" y="${f(.354 * s)}" font-size="${f(s)}" text-anchor="middle">${esc(sym)}</text>`;   // .354 s: 기호 잉크 가운데를 고리 가운데에 맞추는 기준선 내림
};
// 윗면에 눕혀 그리는 그림: 그림 좌표 ±13을 화면 가로는 그대로, 세로는 .577로 눌러 바닥에 누운 모양으로 만든다
const PIC = {
  coin: `<circle r="${COIN_R}"/>`,
  check: '<circle cx="-4" cy="-1.5" r="9.8"/><path d="M5.8 -1.5H14.5M-8.8 -1.5L-5 2.2L1 -5.6"/>',
};
// 감독 건물의 치수와 그리는 법은 iso_buildings.js(서울, 홍콩, 싱가포르)와 iso_buildings2.js(도쿄, 파리), 건물 묶음은 iso_clusters_us.js(미국)와 iso_eu_authorities.js(EU 일반), 준비금 동전 기둥은 iso_coins.js, 보관 은행 건물은 iso_bank.js, 이용자 그림은 iso_person.js에 있다.
function drawObj(k, cx, cy, kind, flagFile, cur) {
  const bld = DRAW[kind];
  if (bld) return bld(cx, cy, flagFile);
  const P = (x, y, z) => [cx + (x - y) * C30, cy + (x + y) * .5 - z];
  const el = [], ps = [];
  const face = (c, a) => { ps.push(...a); el.push(`<polygon class="iso-face ${c}" points="${pts(a)}"/>`); };
  const ln = (a, c = '') => el.push(`<polyline class="iso-d iso-dn ${c}" points="${pts(a)}"/>`);
  const path = (c, segs) => el.push(`<path class="${c}" d="${segs.map((s) => `M${s.map(([x, y]) => `${f(x)} ${f(y)}`).join('L')}`).join('')}"/>`);
  // 가로 x0~x1, 세로 y0~y1, 높이 z0~z1 상자. 왼쪽 면은 y1, 오른쪽 면은 x1, 윗면은 z1
  const box = (x0, x1, y0, y1, z0, z1, c = {}) => {
    face(c.l ?? 'iso-l', [P(x0, y1, z1), P(x1, y1, z1), P(x1, y1, z0), P(x0, y1, z0)]);
    face(c.r ?? 'iso-r', [P(x1, y1, z1), P(x1, y0, z1), P(x1, y0, z0), P(x1, y1, z0)]);
    if (c.t !== 0) face(c.t ?? 'iso-t', [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]);
  };
  // 윗면에 국기를 4:3 그대로 눕혀 붙인다. 국기 가로는 x 방향, 세로는 y 방향이고 국기 위쪽이 오른쪽 위를 향한다
  const flag = (xc, yc, z, fw) => {
    if (!flagFile) return;
    const fh = fw * .75, x0 = xc - fw / 2, y0 = yc - fh / 2, o = P(x0, y0, z);
    el.push(`<image class="iso-flag" href="flags/${flagFile}.svg" x="0" y="0" width="640" height="480" preserveAspectRatio="none" transform="matrix(${g5(fw * C30 / 640)},${g5(fw * .5 / 640)},${g5(-fh * C30 / 480)},${g5(fh * .5 / 480)},${f(o[0])},${f(o[1])})"/>`);
    ln([P(x0, y0, z), P(x0 + fw, y0, z), P(x0 + fw, y0 + fh, z), P(x0, y0 + fh, z), P(x0, y0, z)]);
  };
  const mark = (pic, z, a, sym) => { const [x, y] = P(0, 0, z); el.push(`<g class="iso-mark" transform="translate(${f(x)},${f(y)}) scale(${g5(a / 36)},${g5(a / 36 * .5774)})">${PIC[pic]}${sym ? symText(sym) : ''}</g>`); };
  const cube = (a, h, pic, sym) => { box(-a / 2, a / 2, -a / 2, a / 2, 0, h); mark(pic, h, a, sym); };

  // 네모 상자: 감독이 사진으로 한 건물을 특정할 수 없을 때. 윗면이 4:3이라 국기가 그대로 들어맞는다
  const slab = () => { const d = 52, w = d * 4 / 3, h = 30; box(-w / 2, w / 2, -d / 2, d / 2, 0, h, { l: 'iso-w', r: 'iso-w' }); flag(0, 0, h, w); };
  // 공개: 종이 묶음. 종이 8장을 약간씩 어긋나게 쌓고 맨 위 장에 글줄
  const papers = () => {
    const sw = 38, sd = 52, t = 2.4, off = [[0, 0], [1.4, -1], [-1.2, 1.2], [1, .6], [-1.5, -.8], [.8, 1.3], [-.6, -1.2], [0, 0]];
    off.forEach(([du, dv], i) => box(-sw / 2 + du, sw / 2 + du, -sd / 2 + dv, sd / 2 + dv, i * t, (i + 1) * t));
    const z = off.length * t;
    path('iso-d iso-dn', [-14, -6, 2, 10, 18].map((y) => [P(-sw / 2 + 6, y, z), P(sw / 2 - 6, y, z)]));
  };

  if (kind === 'slab') slab();
  else if (kind === 'papers') papers();
  else if (kind === 'person') { const c = personFigure(cx, cy); el.push(c.svg); ps.push(...c.poly); }
  else if (kind === 'coin') cube(80, 28, 'coin', cur);
  else if (kind === 'coins') { const c = coinStacks(cx, cy, { symbol: cur }); el.push(c.svg); ps.push(...c.poly); }
  else if (kind === 'check') cube(64.7, 22, 'check');
  else if (kind.startsWith('check:')) { const ax = 92, ay = 46, h = 24, w = kind.slice(6), fs = Math.min(15, (ax - 16) / (w.length * .72)), [x, y] = P(0, 0, h); box(-ax / 2, ax / 2, -ay / 2, ay / 2, 0, h); el.push(`<text class="iso-coin-sym" transform="matrix(${g5(C30)} .5 ${g5(-C30)} .5 ${f(x)} ${f(y)})" x=".3" y="${f(.36 * fs)}" font-size="${f(fs)}" text-anchor="middle" letter-spacing=".6">${esc(w)}</text>`); }
  else if (kind === 'bank') { const c = bankBuilding(cx, cy, { symbol: cur }); el.push(...c.el); ps.push(...c.poly); }
  else if (kind.startsWith('vault:')) { const c = vaultBuilding(cx, cy, { word: kind.slice(6) }); el.push(...c.el); ps.push(...c.poly); }
  return { el, ps };
}

// 장면 만들기: 블록마다 물체를 그리고, 바깥 윤곽(볼록 다각형), 이름표를 붙일 점(윤곽 위)을 구한다.
// 윤곽은 물체 전체(지붕, 국기, 종이 묶음, 사람 머리까지)를 감싼다. padTop은 가장 높은 물체 위쪽 여백, padBot은 가장 낮은 물체 아래쪽 여백(이름표 자리)
function makeScene(id, padTop, padBot, mode) {
  const { zones: ZS, cell } = MODES[mode] ?? MODES.group;
  const KINDS = { 이용자: 'person', 공개: 'papers', 발행사: 'coin', 감독: BUILDING[id] ?? 'slab', 준비금: 'coins', 검증: VERIFY[id] ? `check:${VERIFY[id]}` : 'check', 보관: VAULT[id] ? `vault:${VAULT[id]}` : 'bank' };
  const make = (Y0) => {
    const B = {};
    for (const [k, [a, b]] of Object.entries(cell)) {
      const x = X0 + a * HW, y = Y0 + b * HH, o = drawObj(k, x, y, KINDS[k], k === '감독' ? FLAG[id] : null, CUR[id]), ppl = k === '이용자';
      const poly = hull(o.ps), xs = poly.map((p) => p[0]), ys = poly.map((p) => p[1]), x0 = Math.min(...xs), y0 = Math.min(...ys);
      const my = y - 16;
      B[k] = { k, x, y, el: o.el, poly, ppl, bb: { x: x0, y: y0, w: Math.max(...xs) - x0, h: Math.max(...ys) - y0 }, sides: SIDES[k],
        port: { l: [x - exitT(poly, [x, my], [-1, 0]), my], r: [x + exitT(poly, [x, my], [1, 0]), my], t: [x, my - exitT(poly, [x, my], [0, -1])], b: [x, my + exitT(poly, [x, my], [0, 1])] } };
    }
    return B;
  };
  const zones = (Y0) => ZS.map((z) => {
    const { u: [u0, u1], v: [v0, v1] } = z, S = (u, v) => [X0 + (u + v) * HW, Y0 + (u - v) * HH], q = (a, b) => [S(a, v0), S(b, v0), S(b, v1), S(a, v1)];
    return { ...z, poly: q(u0, u1) };
  });
  const ys = (B, Z) => [...Object.values(B).flatMap((b) => [b.bb.y, b.bb.y + b.bb.h]), ...Z.flatMap((z) => z.poly.map((p) => p[1]))];
  const top = Math.min(...ys(make(0), zones(0))), Y0 = Math.ceil(padTop - top), B = make(Y0), Z = zones(Y0);
  return { B, Z, Y0, H: Math.ceil(Math.max(...ys(B, Z)) + padBot) };
}

// ---- 기하 도우미 ----
const hitR = (a, b, m = 0) => a.x < b.x + b.w + m && b.x < a.x + a.w + m && a.y < b.y + b.h + m && b.y < a.y + a.h + m;
// 볼록 다각형과 네모(m만큼 부풀림)가 겹치는지(분리축 검사)
function polyHit(poly, r, m = 0) {
  const x0 = r.x - m, y0 = r.y - m, x1 = r.x + r.w + m, y1 = r.y + r.h + m, rp = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
  const axes = [[1, 0], [0, 1]];
  for (let i = 0; i < poly.length; i++) { const a = poly[i], b = poly[(i + 1) % poly.length]; axes.push([-(b[1] - a[1]), b[0] - a[0]]); }
  for (const [ax, ay] of axes) {
    let a0 = 1e9, a1 = -1e9, b0 = 1e9, b1 = -1e9;
    for (const p of poly) { const v = p[0] * ax + p[1] * ay; a0 = Math.min(a0, v); a1 = Math.max(a1, v); }
    for (const p of rp) { const v = p[0] * ax + p[1] * ay; b0 = Math.min(b0, v); b1 = Math.max(b1, v); }
    if (a1 <= b0 || b1 <= a0) return false;
  }
  return true;
}
// 선분이 네모를 지나는지: 3px 간격으로 찍어 본다
function segHit(r, p, q, m = 0) {
  const n = Math.max(1, Math.ceil(Math.hypot(q[0] - p[0], q[1] - p[1]) / 3));
  for (let i = 0; i <= n; i++) {
    const x = p[0] + (q[0] - p[0]) * i / n, y = p[1] + (q[1] - p[1]) * i / n;
    if (x > r.x - m && x < r.x + r.w + m && y > r.y - m && y < r.y + r.h + m) return true;
  }
  return false;
}
const cross2 = (p, q, r) => (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]);
const segX = (a, b, c, d) => cross2(a, b, c) * cross2(a, b, d) < 0 && cross2(c, d, a) * cross2(c, d, b) < 0;
// 네모와 선분 사이 거리(겹치면 0). 선분을 듬성듬성 찍어 재면 비스듬한 선이 모서리에 바짝 붙어도 4px 넘게 나오므로 정확히 잰다
const ptSeg = (x, y, p, q) => { const vx = q[0] - p[0], vy = q[1] - p[1], t = clamp(((x - p[0]) * vx + (y - p[1]) * vy) / (vx * vx + vy * vy), 0, 1); return Math.hypot(p[0] + vx * t - x, p[1] + vy * t - y); };
function rgap(r, p, q) {
  const c = [[r.x, r.y], [r.x + r.w, r.y], [r.x + r.w, r.y + r.h], [r.x, r.y + r.h]], at = (a) => a[0] >= r.x && a[0] <= r.x + r.w && a[1] >= r.y && a[1] <= r.y + r.h;
  if (at(p) || at(q)) return 0;
  let g = Infinity;
  for (let i = 0; i < 4; i++) { const a = c[i], b = c[(i + 1) % 4]; if (segX(p, q, a, b)) return 0; g = Math.min(g, ptSeg(a[0], a[1], p, q), ptSeg(p[0], p[1], a, b), ptSeg(q[0], q[1], a, b)); }
  return g;
}
const inPoly = (poly, x, y) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const [xi, yi] = poly[i], [xj, yj] = poly[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
const bbox = (a, b) => ({ x: Math.min(a[0], b[0]), y: Math.min(a[1], b[1]), w: Math.abs(a[0] - b[0]), h: Math.abs(a[1] - b[1]) });
// 볼록 다각형 안의 점 p에서 단위 방향 d로 나갈 때 윤곽까지 거리
function exitT(poly, p, d) {
  let best = Infinity;
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length], ex = b[0] - a[0], ey = b[1] - a[1], den = d[0] * ey - d[1] * ex;
    if (Math.abs(den) < 1e-9) continue;
    const t = ((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den, u = ((a[0] - p[0]) * d[1] - (a[1] - p[1]) * d[0]) / den;
    if (t > 0 && u >= 0 && u <= 1) best = Math.min(best, t);
  }
  return best;
}
// 세로선 x(가로선 y)가 윤곽과 만나는 y(x)의 [최소, 최대]
function chord(poly, axis, v) {
  let lo = 1e9, hi = -1e9;
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length], p = axis, q = 1 - axis;
    if ((a[p] - v) * (b[p] - v) > 0) continue;
    const t = a[p] === b[p] ? 0 : (v - a[p]) / (b[p] - a[p]);
    for (const u of a[p] === b[p] ? [a[q], b[q]] : [a[q] + (b[q] - a[q]) * t]) { lo = Math.min(lo, u); hi = Math.max(hi, u); }
  }
  return [lo, hi];
}

// 선: 바닥 가운데끼리 이은 직선을 블록 윤곽 밖에서 시작하고 끝낸다. money는 돈과 코인이 오가는 선(진한 점선), 나머지는 확인과 공개(옅은 점선)
// off는 직선에서 옆으로 벌리는 거리(px). 이용자와 발행사 사이 두 줄은 시작과 끝을 같은 자리에 맞춘다
// 두 줄 사이(OFF의 두 배)가 좁으면 한 줄의 화살표 머리가 다른 줄의 점과 선에 바짝 붙는다. OFF 6이면 6.4px, 8이면 10px 넘게 떨어진다
const OFF = 8;
const LINKS = [
  { id: '발행', from: '이용자', to: '발행사', money: 1, off: OFF },
  { id: '상환', from: '발행사', to: '이용자', money: 1, off: OFF },
  { id: '예치', from: '발행사', to: '준비금', money: 1 },
  { id: '보관', from: '준비금', to: '보관', money: 1 },
  { id: '검증', from: '검증', to: '준비금' },
  { id: '공개', from: '발행사', to: '공개' },
  { id: '열람', from: '공개', to: '이용자' },
  { id: '감독', from: '감독', to: '발행사' },
];
const GAP = 9;                          // 선 끝(시작 점, 화살표 머리)과 블록 윤곽 사이 거리(px). 비스듬한 선은 면에 비스듬히 닿아 실제 간격이 이만큼 안 나오므로 넉넉히 둔다
const PAIR = {
  a: (A, d) => Math.max(exitT(A.poly, [A.x, A.y - OFF], d), exitT(A.poly, [A.x, A.y + OFF], d)) + GAP,
  b: (T, d) => Math.max(exitT(T.poly, [T.x, T.y - OFF], [-d[0], -d[1]]), exitT(T.poly, [T.x, T.y + OFF], [-d[0], -d[1]])) + GAP,
};
function route(B, l) {
  const A = B[l.from], T = B[l.to];
  let dx = T.x - A.x, dy = T.y - A.y; const len = Math.hypot(dx, dy); dx /= len; dy /= len;
  const nx = -dy * (l.off || 0), ny = dx * (l.off || 0), p0 = [A.x + nx, A.y + ny], p1 = [T.x + nx, T.y + ny];
  const a = l.off ? PAIR.a(A, [dx, dy]) : exitT(A.poly, p0, [dx, dy]) + GAP, b = l.off ? PAIR.b(T, [dx, dy]) : exitT(T.poly, p1, [-dx, -dy]) + GAP;
  let s = [p0[0] + dx * a, p0[1] + dy * a], e = [p1[0] - dx * b, p1[1] - dy * b];
  // 비스듬히 닿는 선은 윤곽까지 실제 거리가 GAP보다 짧을 수 있으므로, 시작 점은 GAP, 화살표 끝은 머리 길이만큼 더 떨어질 때까지 물린다(두 줄 쌍은 위에서 맞췄으므로 건드리지 않는다)
  if (!l.off) {
    for (let i = 0; i < 80 && polyDist(A.poly, s) < GAP; i++) { s = [s[0] + dx, s[1] + dy]; }
    for (let i = 0; i < 80 && polyDist(T.poly, e) < GAP + 5; i++) { e = [e[0] - dx, e[1] - dy]; }
  }
  return [s, e];
}
// 점에서 볼록 윤곽까지 거리(안이면 0)
const polyDist = (poly, p) => inPoly(poly, p[0], p[1]) ? 0 : Math.min(...poly.map((a, i) => ptSeg(p[0], p[1], a, poly[(i + 1) % poly.length])));

// ---- 자리 잡기: 이름표, 선 이름표, 꼬리표를 서로와 블록, 선에 겹치지 않게 놓는다 ----
// 항목마다 후보 자리를 만들고(블록과 선을 피하는 자리만), 후보끼리 겹치지 않는 조합 가운데 값이 가장 싼 것을 되돌아가며 찾는다.
// 값은 지시선과 선 이름표가 짧을수록, 이름표가 블록 가까이 있을수록 싸다. 시간이 아닌 탐색 횟수로 끊어서 기기와 상관없이 같은 그림이 나온다.
const MG = 8;                            // 이름표, 선 이름표가 물체, 선, 다른 이름표와 떨어져야 하는 거리(px)
const EDGE = 12;                         // 이름표가 그림판 가장자리에서 떨어져야 하는 거리(px)
// 이름표 가장자리에서 블록 윤곽까지 지시선. 붙이는 점은 이름표 쪽으로 가장 가까운 윤곽 위(윗면 포함)
const lead = (B, k, s, r) => {
  const { bb, poly } = B[k];
  if (s === 'l' || s === 'r') {
    const y = clamp(r.y + r.h / 2, bb.y + 6, bb.y + bb.h - 6), [x0, x1] = chord(poly, 1, y);
    return [[s === 'r' ? r.x : r.x + r.w, clamp(y, r.y + 9, r.y + r.h - 9)], [s === 'r' ? x1 : x0, y]];
  }
  const hx = B[k].ppl ? [B[k].x - 3, B[k].x + 3] : [bb.x + 6, bb.x + bb.w - 6];   // 사람은 머리 폭 안에서만 붙인다
  const x = clamp(r.x + r.w / 2, hx[0], hx[1]), [y0, y1] = chord(poly, 0, x);
  return [[clamp(x, r.x + 10, r.x + r.w - 10), s === 't' ? r.y + r.h : r.y], [x, s === 't' ? y0 : y1]];
};
// 선 이름표 지시선: 이름표 네 변 가운데 중 선에 가장 가까운 점에서 그 선 위 가장 가까운 점까지(시작 동그라미 10px, 화살표 머리 16px는 피한다)
const pillLead = (r, p, q) => {
  const vx = q[0] - p[0], vy = q[1] - p[1], vv = vx * vx + vy * vy, len = Math.sqrt(vv);
  let best = null;
  for (const [x, y] of [[r.x + r.w / 2, r.y], [r.x + r.w / 2, r.y + r.h], [r.x, r.y + r.h / 2], [r.x + r.w, r.y + r.h / 2]]) {
    const t = clamp(((x - p[0]) * vx + (y - p[1]) * vy) / vv, 10 / len, 1 - 16 / len), s = [p[0] + vx * t, p[1] + vy * t], d = Math.hypot(s[0] - x, s[1] - y);
    if (!best || d < best[0]) best = [d, [[x, y], s]];
  }
  return best[1];
};
function compat(a, b) {
  if (hitR(a.r, b.r, MG)) return false;
  if (a.ld && hitR(a.lb, b.r, MG) && segHit(b.r, a.ld[0], a.ld[1], MG)) return false;
  if (b.ld && hitR(b.lb, a.r, MG) && segHit(a.r, b.ld[0], b.ld[1], MG)) return false;
  if (a.ld && b.ld && segX(a.ld[0], a.ld[1], b.ld[0], b.ld[1])) return false;
  return true;
}
// 되돌아가기 탐색: 남은 후보가 가장 적은 항목부터, 값이 싼 후보부터. 남은 항목의 가장 싼 값을 더한 하한으로 가지를 친다.
// 첫 조합을 first번 안에 못 찾으면 그만두고, 찾으면 more번(전체 cap번까지) 더 본다
function solve(items, more, cap, first) {
  const n = items.length;
  let best = null, nodes = 0, stop = first, total = 0;
  for (const it of items) for (const c of it.cands) c.i = total++;
  const memo = new Uint8Array(total * total);          // 후보 쌍 검사 결과 기억: 1 맞음, 2 겹침
  const ok = (a, b) => { const k = a.i * total + b.i, v = memo[k]; if (v) return v === 1; const r = compat(a, b); memo[k] = memo[b.i * total + a.i] = r ? 1 : 2; return r; };
  const done = Array(n).fill(false), chosen = Array(n).fill(null);
  const rec = (doms, cost) => {
    if (++nodes > stop) return;
    let bi = -1, bs = 1e9;
    for (let i = 0; i < n; i++) if (!done[i] && doms[i].length < bs) { bs = doms[i].length; bi = i; }
    if (bi < 0) { if (!best || cost < best.cost) { if (!best) stop = Math.min(cap, nodes + more); best = { cost, chosen: chosen.slice() }; } return; }
    for (const c of doms[bi]) {
      if (best && cost + c.cost >= best.cost) break;
      const nd = doms.map((d, j) => done[j] || j === bi ? d : d.filter((x) => ok(c, x)));
      let lb = 0, dead = false;
      for (let j = 0; j < n; j++) if (!done[j] && j !== bi) { if (!nd[j].length) { dead = true; break; } lb += nd[j][0].cost; }
      if (dead || (best && cost + c.cost + lb >= best.cost)) continue;
      done[bi] = true; chosen[bi] = c;
      rec(nd, cost + c.cost);
      done[bi] = false; chosen[bi] = null;
      if (nodes > stop) return;
    }
  };
  rec(items.map((it) => it.cands), 0);
  return best;
}

// 풀이 조건: 간격(m)이 넉넉하고 지시선(capL)과 선 이름표 거리(capP)가 짧은 조건부터 하나씩 푼다. cap은 탐색 횟수 한도, first는 첫 풀이를 찾는 데 쓰는 한도
// 간격은 어느 조건에서도 8px 아래로 내리지 않는다. 안 풀리면 간격 대신 그림판을 키워 다시 푼다(CANVAS)
const LEVELS = [{ m: 10, capL: 90, capP: 33, cap: 250, first: 60 }, { m: 9, capL: 125, capP: 40, cap: 250, first: 60 }, { m: 8, capL: 175, capP: 46, cap: 500, first: 120 }, { m: 8, capL: 999, capP: 54, cap: 900, first: 900 }];
const CANVAS = [{ pt: 56, pb: 84 }, { pt: 96, pb: 110 }, { pt: 140, pb: 140 }, { pt: 190, pb: 180 }];
const cache = new Map();
export function isoFlowSvg(spec, opt = {}) {
  if (!spec?.노드) return '';
  const key = `${opt.id}|${opt.name}|${opt.zones}|${JSON.stringify(spec)}`;
  if (!cache.has(key)) cache.set(key, build(spec, opt));
  return cache.get(key);
}

function build(spec, { name = '', id = '', zones = 'group' } = {}) {
  const N = spec.노드, C = spec.연결 || {}, coins = Array.isArray(spec.코인) ? spec.코인.filter(Boolean) : [];
  const nd = (k) => N[k] || {}, rows = (k) => nd(k).줄 || [], title = (k) => String(nd(k).이름 ?? '').trim() || k, gone = (k) => Boolean(nd(k).없음);
  let res = null;
  for (const cv of CANVAS) { res = attempt(cv); if (res.ok) break; }
  const { sol, items, B, Z, H, links, note } = res;

  function attempt(cv) {
    const { B, Z, H } = makeScene(id, cv.pt, cv.pb, zones);
    // 이름표는 장판 테두리에 걸치지 않는다(장판 안이나 밖에 통째로 놓인다). 장판 이름은 제 장판 테두리에만 걸칠 수 있다
    const zEdges = Z.flatMap(({ poly: z }, zi) => z.map((p, i) => [p, z[(i + 1) % 4], zi])), onZone = (r, own = -1) => zEdges.some(([p, q, zi]) => zi !== own && segHit(r, p, q, 3));
    const bodies = Object.values(B).map((b) => ({ poly: b.poly, bb: b.bb }));
    const inside = (r) => r.x >= EDGE && r.y >= EDGE && r.x + r.w <= W - EDGE && r.y + r.h <= H - EDGE;
    const offBlocks = (r, m) => !bodies.some((b) => hitR(r, b.bb, m) && polyHit(b.poly, r, m));
    const links = LINKS.map((l) => ({ ...l, path: route(B, l), ghost: gone(l.from) || gone(l.to) }));
    // 화살표 머리(길이 9.6, 폭 9.6, 선 끝보다 1.9 앞으로 나감)가 차지하는 네모. 선만 보고 띄우면 머리 옆으로 3px밖에 안 떨어진다
    const head = (p, q) => {
      const L = Math.hypot(q[0] - p[0], q[1] - p[1]), ux = (q[0] - p[0]) / L, uy = (q[1] - p[1]) / L, nx = -uy * 4.8, ny = ux * 4.8;
      const xs = [q[0] + ux * 1.9, q[0] - ux * 7.7 + nx, q[0] - ux * 7.7 - nx], ys = [q[1] + uy * 1.9, q[1] - uy * 7.7 + ny, q[1] - uy * 7.7 - ny];
      return { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) };
    };
    const segs = links.map((l) => ({ id: l.id, p: l.path[0], q: l.path[1], bb: bbox(l.path[0], l.path[1]), ah: head(l.path[0], l.path[1]) }));
    const onLine = (r, own, m) => segs.some((s) => s.id !== own && ((hitR(r, s.bb, m) && segHit(r, s.p, s.q, m)) || hitR(r, s.ah, m)));
    const linkCross = (a, b) => segs.filter((s) => segX(a, b, s.p, s.q)).length;
    // 선분 a-b가 블록 안(또는 m px 안쪽)을 지나는지: steps등분해 앞의 last+1개 점을 본다. 윤곽 네모 밖의 점은 건너뛴다
    const blockHit = (a, b, last, steps, m = 0) => {
      for (let i = 0; i <= last; i++) {
        const x = a[0] + (b[0] - a[0]) * i / steps, y = a[1] + (b[1] - a[1]) * i / steps;
        if (bodies.some((k) => x > k.bb.x - m && x < k.bb.x + k.bb.w + m && y > k.bb.y - m && y < k.bb.y + k.bb.h + m && [[0, 0], [m, 0], [-m, 0], [0, m], [0, -m]].some(([ox, oy]) => inPoly(k.poly, x + ox, y + oy)))) return true;
      }
      return false;
    };
    const items = [];

    // 선 이름표: 선 위(가운데 줄 선)나 선 옆에 놓는다. 선 가운데 둘레를 6px 간격으로 훑어, 블록과 다른 선을 피하는 자리만 후보로 삼는다
    for (const l of links) {
      const text = String(C[l.id] ?? '').trim();
      if (!text) continue;
      const variants = [wrap(text, F2, 94, 1)];
      if (tw(text, F2, 1) <= 176) variants.unshift([text]);
      const [p, q] = l.path, dx = q[0] - p[0], dy = q[1] - p[1], len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len, mx = (p[0] + q[0]) / 2, my = (p[1] + q[1]) / 2;
      const mk = (lv) => {
        const cands = [];
        variants.forEach((lines, vi) => {
          if (vi && lines.length === variants[0].length && lines.every((t, i) => t === variants[0][i])) return;
          const w = Math.ceil(Math.max(...lines.map((t) => tw(t, F2, 1)))) + 20, h = 7 + lines.length * 14.5 + (lines.length > 1 ? 1 : 0);
          for (let oy = -70; oy <= 70; oy += 6) for (let ox = -90; ox <= 90; ox += 6) {
            const cx = mx + ox, cy = my + oy, r = { x: cx - w / 2, y: cy - h / 2, w, h };
            if (!inside(r) || !offBlocks(r, lv.m) || onLine(r, l.id, MG) || onZone(r)) continue;
            const on = segHit(r, p, q, 0);
            // 선 위에 놓을 때는 화살표 끝과 시작점이 가려지지 않아야 하고, 선이 이름표 가운데 가까이를 지나야 한다(테두리나 모서리만 스치는 자리는 뺀다)
            if (on && (segHit(r, p, [p[0] + ux * 14, p[1] + uy * 14], 2) || segHit(r, q, [q[0] - ux * 18, q[1] - uy * 18], 2))) continue;
            const perp = Math.abs((cx - p[0]) * uy - (cy - p[1]) * ux);
            if (on && perp > h * .25) continue;
            // 선과의 거리(겹치면 0). 다른 선이 자기 선만큼 가까우면 어느 선의 이름표인지 헷갈리므로 뺀다
            let gap = 0;
            if (!on) { gap = rgap(r, p, q); if (gap < 4 || gap > lv.capP) continue; }
            if (links.some((o) => o !== l && rgap(r, o.path[0], o.path[1]) <= gap + (Boolean(o.money) !== Boolean(l.money) ? 16 : 3))) continue;   // 종류(돈, 확인)가 다른 선이 더 가까이 있으면 그 선의 이름표로 읽히므로 더 멀리 둔다
            let ld = null; // 선에서 8px 넘게 떨어지면 지시선으로 잇는다. 지시선이 블록이나 다른 선을 지나는 자리는 뺀다
            if (gap > 8) { ld = pillLead(r, p, q); const n = Math.ceil(Math.hypot(ld[1][0] - ld[0][0], ld[1][1] - ld[0][1]) / 2); if (blockHit(ld[0], ld[1], n, n, 2) || segs.some((s) => s.id !== l.id && segX(ld[0], ld[1], s.p, s.q))) continue; }
            cands.push({ r, lines, link: l, ld, lb: ld && bbox(ld[0], ld[1]), cost: gap * 2 + gap * gap / 40 + (on ? perp * .5 : 10) + (ld ? 4 : 0) + Math.abs((cx - mx) * ux + (cy - my) * uy) * .35 + (lines.length > 1 ? 3 : 0) });
          }
        });
        return cands.sort((a, b) => a.cost - b.cost).slice(0, 70);
      };
      items.push({ kind: 'pill', id: l.id, mk });
    }

    // 블록 이름표: 이름은 13px 굵게, 줄은 12px. 한 항목은 두 줄까지만 나눈다. 코인 이름표는 발행사에 붙는다
    // keep: 줄을 나누지 않는 이름표(코인 이름은 'Circle USDC, EURC'가 한 줄이어야 읽힘)
    const layout = (hd, bd, mw, keep) => {
      const head = wrap(hd, F1, mw - 20, 1), body = bd.map((t) => wrap(t, F2, mw - 20));
      if (head.length > 2 || body.some((r) => r.length > (keep ? 1 : 2))) return null;
      const flat = body.flat(), w = Math.max(64, Math.ceil(Math.max(...head.map((t) => tw(t, F1, 1)), ...flat.map((t) => tw(t, F2)))) + 20);
      return { head, body: flat, w, h: Math.ceil(17 + (head.length - 1) * 15.5 + (flat.length ? 15.5 + (flat.length - 1) * 14.5 : 0) + 7) };
    };
    const tall = Math.max(...Object.values(B).map((b) => b.bb.h)), SH = [0, -11, 11, -24, 24, -42, 42, -64, 64, -88, 88, ...(tall > 150 ? [-115, 115, -145, 145] : [])];
    const labItems = [...ORDER.map((k) => ({ id: k, obj: k, hd: title(k), bd: rows(k) })), ...(coins.length ? [{ id: '코인', obj: '발행사', hd: TITLE_COIN, bd: coins }] : [])];
    for (const li of labItems) {
      const k = li.obj, sides = SIDES[li.id];
      const mk = (lv) => {
        const cands = [], seen = new Set();
        [196, 174, 154, 136, 120].forEach((mw, wr) => {
          const L = layout(li.hd, li.bd, mw, li.id === '코인'); if (!L) return;
          const sig = `${L.head}#${L.body}`; if (seen.has(sig)) return; seen.add(sig);
          [...sides].forEach((s, si) => {
            const [px, py] = B[k].port[s], { w, h } = L;
            for (const step of [0, 7, 15, 28, 46, 68]) for (const sh of SH) {
              const r = s === 'r' ? { x: px + 13 + step, y: py - h / 2 + sh, w, h } : s === 'l' ? { x: px - 13 - step - w, y: py - h / 2 + sh, w, h } : s === 't' ? { x: px - w / 2 + sh, y: py - 13 - step - h, w, h } : { x: px - w / 2 + sh, y: py + 13 + step, w, h };
              if (!inside(r) || !offBlocks(r, lv.m + 6) || onLine(r, null, MG) || onZone(r)) continue;   // 이름표는 블록 윤곽에서 선 이름표보다 6px 더 떨어진다
              const ld = lead(B, k, s, r), ll = Math.hypot(ld[1][0] - ld[0][0], ld[1][1] - ld[0][1]);
              if (ll > lv.capL) continue;
              if (blockHit(ld[0], ld[1], 14, 16)) continue; // 지시선이 블록을 지나면 안 된다
              if (linkCross(ld[0], ld[1])) continue;       // 지시선이 선을 가로지르면 안 된다
              cands.push({ r, L, s, ld, lb: bbox(ld[0], ld[1]), cost: ll + ll * ll / 70 + si * 16 + wr * 10 + Math.abs(sh) * .3 });
            }
          });
        });
        return cands.sort((a, b) => a.cost - b.cost).slice(0, 110);
      };
      items.push({ kind: 'lab', id: li.id, mk });
    }

    // 장판 이름: 묶음 이름(굵게)과 규칙 번호. 한 줄이나 두 줄로, 제 장판에 걸치게 놓는다(블록 하나뿐인 장판은 빈 데가 적어 밖으로 반쯤 나갈 수 있다). 장판 안쪽, 앞쪽(아래) 모서리에 가까울수록 싸다
    Z.forEach((z, zi) => {
      const w1 = Math.ceil(tw(z.name, F2, 1) + 6 + tw(z.rules, 11)) + 8, w2 = Math.ceil(Math.max(tw(z.name, F2, 1), tw(z.rules, 11))) + 8;
      const ys = z.poly.map((p) => p[1]), xs = z.poly.map((p) => p[0]), front = z.poly[ys.indexOf(Math.max(...ys))];
      z.L = [{ two: false, w: w1, h: 20 }, { two: true, w: w2, h: 34 }];
      const mk = (lv) => {
        const cands = [];
        for (const L of z.L) for (let cy = Math.min(...ys) - L.h / 2; cy <= Math.max(...ys) + L.h / 2; cy += 4) for (let cx = Math.min(...xs) - L.w / 2; cx <= Math.max(...xs) + L.w / 2; cx += 4) {
          const r = { x: cx - L.w / 2, y: cy - L.h / 2, w: L.w, h: L.h }, pin = [[r.x, r.y], [r.x + r.w, r.y], [r.x, r.y + r.h], [r.x + r.w, r.y + r.h], [cx, cy]].map(([x, y]) => inPoly(z.poly, x, y));
          if (!pin.some(Boolean) || !inside(r) || !offBlocks(r, lv.m) || onLine(r, null, MG) || onZone(r, zi)) continue;
          cands.push({ r, L, cost: Math.hypot(cx - front[0], cy - front[1]) * .4 + pin.slice(0, 4).filter((v) => !v).length * 12 + (pin[4] ? 0 : 30) + (L.two ? 6 : 0) });
        }
        return cands.sort((a, b) => a.cost - b.cost).slice(0, 60);
      };
      items.push({ kind: 'zone', id: z.name, mk });
    });

    // 꼬리표(검토 중인 값 표시)
    const note = spec.꼬리표 ? { text: String(spec.꼬리표), w: Math.ceil(tw(spec.꼬리표, F2, 1)) + 22, h: 24 } : null;
    if (note) items.push({ kind: 'note', id: 'note', mk: (lv) => [[EDGE, EDGE], [EDGE, H - note.h - EDGE], [W / 2 - note.w / 2, EDGE], [W - note.w - EDGE, EDGE], [W - note.w - EDGE, H - note.h - EDGE]].map(([x, y], i) => ({ r: { x, y, w: note.w, h: note.h }, cost: i * 10 })).filter((c) => offBlocks(c.r, lv.m) && !onLine(c.r, null, MG) && !onZone(c.r)) });

    // 풀기: 조건을 하나씩 풀어 가며 시험한다. 끝내 안 풀리면 ok를 거짓으로 돌려 더 큰 그림판으로 다시 푼다
    let sol = null;
    for (const lv of LEVELS) {
      for (const it of items) it.cands = it.mk(lv);
      if (items.some((it) => !it.cands.length)) continue;
      sol = solve(items, 140, lv.cap, lv.first);
      if (sol) break;
    }
    if (!sol && cv !== CANVAS[CANVAS.length - 1]) return { ok: false };
    if (!sol) { // 마지막 그림판에서도 안 풀리면 후보가 적은 항목부터 앞서 놓은 것과 가장 덜 겹치는 싼 후보를 고른다(후보가 없으면 왼쪽 위 구석)
      for (const it of items) if (!it.cands.length) it.cands = [{ r: { x: 5, y: 5, w: 90, h: 36 }, cost: 0, L: layout(title(it.id), rows(it.id), 176) || { head: [it.id], body: [], w: 90, h: 36 }, s: 't', lines: [it.id], link: links[0] }];
      const chosen = [], placed = [];
      for (const i of items.map((_, j) => j).sort((a, b) => items[a].cands.length - items[b].cands.length)) {
        const hits = (c) => placed.filter((q) => !compat(c, q)).length;
        chosen[i] = items[i].cands.reduce((a, c) => hits(c) < hits(a) ? c : a, items[i].cands[0]);
        placed.push(chosen[i]);
      }
      sol = { chosen };
    }
    return { ok: true, sol, items, B, Z, H, links, note };
  }

  const out = [];
  const pick = (kind, key) => sol.chosen[items.findIndex((it) => it.kind === kind && it.id === key)];
  const labIds = [...ORDER, ...(coins.length ? ['코인'] : [])];
  const labels = Object.fromEntries(labIds.map((k) => [k, pick('lab', k)]));
  const pills = links.filter((l) => items.some((it) => it.kind === 'pill' && it.id === l.id)).map((l) => { const c = pick('pill', l.id); return { ...c, ...c.r }; });
  if (note) Object.assign(note, pick('note', 'note').r);

  // ---- 그리기: 격자, 선, 블록(뒤에서 앞으로), 이름표 ----
  const m = HH / HW, grid = [], Y0 = res.B.이용자.y;
  for (let k = -16; k <= 24; k++) { // 오른쪽 아래로 가는 선(c1)과 오른쪽 위로 가는 선(c2). 블록이 서는 교점을 지나게 맞추고 화면 안쪽만 그린다
    const c1 = Y0 - m * X0 + 2 * HH * k, c2 = Y0 + m * X0 + 2 * HH * k;
    const a1 = Math.max(0, -c1 / m), b1 = Math.min(W, (H - c1) / m), a2 = Math.max(0, (c2 - H) / m), b2 = Math.min(W, c2 / m);
    if (b1 > a1) grid.push(`M${f(a1)} ${f(c1 + m * a1)}L${f(b1)} ${f(c1 + m * b1)}`);
    if (b2 > a2) grid.push(`M${f(a2)} ${f(c2 - m * a2)}L${f(b2)} ${f(c2 - m * b2)}`);
  }
  const mk = (i) => `<marker id="iso-ar-${i}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path class="iso-mk iso-mk-${i}" d="M0 0L10 5L0 10z"/></marker>`;
  const aria = `${name} 흐름도. 이용자와 발행사 사이에 코인 발행과 상환이 오가고, 발행사는 준비금을 ${gone('보관') ? '' : `${title('보관')}에 `}예치하고 공개합니다. 감독은 ${title('감독')}입니다.${gone('검증') ? '' : ` 검증은 ${title('검증')}입니다.`}`;
  // 보조기기용 설명: 블록 이름표와 선 이름표의 글. 줄이 쉼표로 끝나면 다음 줄을 같은 문장으로 잇는다
  const sentence = (a) => a.reduce((s, t) => s ? `${s}${s.endsWith(',') ? ' ' : ', '}${t}` : t, '');
  const desc = [...ORDER.map((k) => `${k === title(k) ? k : `${k}(${title(k)})`}: ${sentence(rows(k))}`), ...(coins.length ? [`${TITLE_COIN}: ${coins.join(', ')}`] : []), ...Object.entries(C).filter(([, t]) => String(t ?? '').trim()).map(([k, t]) => `연결 ${k}: ${t}`)].join('. ');
  // 가로는 칸 폭을 따르되 W*.75(12px 글자가 9px 밑으로 가지 않는 폭)보다 줄지 않고, W*1.077(13px 글자가 본문 14px를 넘지 않는 폭)보다 늘지 않는다
  const frostDef = `<filter id="iso-frost" filterUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}"><feGaussianBlur stdDeviation="${BLUR}"/></filter>`;
  out.push(`<svg class="iso-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(aria)}" aria-describedby="iso-desc" style="width:100%;max-width:${Math.round(W * 1.077)}px;min-width:${Math.round(W * .75)}px"><desc id="iso-desc">${esc(desc)}</desc><defs>${mk('ink')}${mk('mut')}${mk('off')}${frostDef}</defs><path class="iso-grid" d="${grid.join('')}"/>${Z.map((z) => `<polygon class="iso-zone" points="${pts(z.poly)}"/>`).join('')}`);
  const leadAt = out.length;
  for (const l of links) {
    const kind = l.ghost ? 'off' : l.money ? 'ink' : 'mut', [sx, sy] = l.path[0];
    out.push(`<polyline class="iso-ln iso-ln-${kind}" data-id="${l.id}" points="${pts(l.path)}" marker-end="url(#iso-ar-${kind})"/><circle class="iso-dot iso-dot-${kind}" cx="${f(sx)}" cy="${f(sy)}" r="2.6"/>`);
  }
  for (const k of Object.keys(B).sort((a, b) => B[a].y - B[b].y || B[a].x - B[b].x)) {
    const cls = `${k === '발행사' ? 'iso-main' : ''} ${gone(k) ? 'iso-ghost' : ''}`;
    out.push(`<g class="iso-blk ${cls}" data-k="${k}">${B[k].el.join('')}</g>`);
  }
  const leads = [], leadTag = ([a, b]) => `<line class="iso-lead" x1="${f(a[0])}" y1="${f(a[1])}" x2="${f(b[0])}" y2="${f(b[1])}"/>`;
  const frost = [], frostAt = out.length;   // 이름표 뒤 흰 번짐 자리: 블록 위, 이름표 아래
  for (const p of pills) if (p.ld) leads.push(leadTag(p.ld));
  for (const k of labIds) {
    const c = labels[k], { L } = c, { x, y, w, h } = c.r;
    const txt = [...L.head.map((t, i) => `<text class="iso-t1" x="10" y="${17 + i * 15.5}" font-size="${F1}">${esc(t)}</text>`), ...L.body.map((t, i) => `<text class="iso-t2" x="10" y="${17 + (L.head.length - 1) * 15.5 + 15.5 + i * 14.5}" font-size="${F2}">${esc(t)}</text>`)];
    leads.push(leadTag(c.ld));
    frost.push([x, y, w, h, 5]);
    out.push(`<g class="iso-lab ${k === '코인' ? 'iso-coin' : ''} ${gone(k) ? 'iso-ghost' : ''}" transform="translate(${f(x)},${f(y)})" data-k="lab-${k}"><rect width="${w}" height="${h}" rx="5"/>${txt.join('')}</g>`);
  }
  for (const p of pills) {
    const kind = p.link.ghost ? 'off' : p.link.money ? 'ink' : 'mut';
    frost.push([p.x, p.y, p.w, p.h, 10]);
    out.push(`<g class="iso-pill iso-pill-${kind}" data-id="${p.link.id}" transform="translate(${f(p.x)},${f(p.y)})" data-k="pill-${p.link.id}"><rect width="${p.w}" height="${p.h}" rx="10"/>${p.lines.map((t, i) => `<text x="${p.w / 2}" y="${15 + i * 14.5}" text-anchor="middle" font-size="${F2}">${esc(t)}</text>`).join('')}</g>`);
  }
  for (const z of Z) {
    const c = pick('zone', z.name), { x, y } = c.r, two = c.L?.two;
    frost.push([x, y, c.r.w, c.r.h, 6]);
    out.push(`<g class="iso-ztag" transform="translate(${f(x)},${f(y)})" data-k="zone-${esc(z.name)}"><rect width="${c.r.w}" height="${c.r.h}"/><text class="iso-zone-t" x="4" y="14.5" font-size="${F2}">${esc(z.name)}</text><text class="iso-zone-r" x="${two ? 4 : f(4 + tw(z.name, F2, 1) + 6)}" y="${two ? 29 : 14.5}" font-size="11">${esc(z.rules)}</text></g>`);
  }
  if (note) {
    frost.push([note.x, note.y, note.w, note.h, 12]);
    out.push(`<g class="iso-note" transform="translate(${note.x},${note.y})" data-k="note"><rect width="${note.w}" height="${note.h}" rx="12"/><text x="${note.w / 2}" y="16.5" text-anchor="middle" font-size="${F2}">${esc(note.text)}</text></g>`);
  }
  // 흰 번짐: 이름표마다 사방으로 FROST px 큰 흰 네모를 한 묶음으로 모아 한 번만 흐린다
  out.splice(frostAt, 0, `<g class="iso-halo" filter="url(#iso-frost)">${frost.map(([x, y, w, h, r]) => `<rect x="${f(x - FROST)}" y="${f(y - FROST)}" width="${f(w + 2 * FROST)}" height="${f(h + 2 * FROST)}" rx="${r + FROST}"/>`).join('')}</g>`);
  out.splice(leadAt, 0, ...leads);
  out.push('</svg>');
  return out.join('');
}
