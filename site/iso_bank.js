// 보관 블록 그림: 은행 건물. 고전 신전 꼴(계단 위 앞줄 기둥, BANK를 새긴 엔타블러처, 통화 기호를 넣은 삼각 지붕 머리, 낮은 맞배지붕)이라
// 상자에 작은 그림을 얹은 것보다 한눈에 은행으로 읽힌다. iso.js drawObj와 같은 정등각 투영과 같은 약속을 쓴다.
//   bankBuilding(cx, cy, opt) -> { el, ps, poly }
//   (cx, cy)는 계단까지 합친 바닥판 가운데(drawObj가 보관 자리로 주는 값). 바닥판 가로 72 x 깊이 48, 화면 윤곽은 폭 약 104 x 높이 약 106
//   (옛 보관 상자는 64.7 x 64.7 x 22, 윤곽 112 x 87). 폭은 같은 자리를 쓰고 높이만 더 높다.
//   el: SVG 조각 문자열 목록(opt.ghost면 한 조각), ps: 바깥 윤곽(iso-face) 꼭짓점 목록(drawObj가 hull(ps)로 윤곽을 만든다), poly: ps의 볼록 윤곽(coinStacks, personFigure처럼 바로 쓸 때)
//   opt.symbol: 나라 통화 기호('$', '€', 'HK$', 'S$', '¥', '₩'). 삼각 지붕 머리 안에 쓴다. 없으면 비운다
//   opt.ghost: 참이면 el 전체를 <g class="iso-ghost">로 감싼다(보관 없음). iso.js는 블록 묶음에 iso-ghost를 이미 붙이므로 그 경우엔 안 줘도 같다
//   opt.cols: 앞줄 기둥 수 4~6(기본 4. 5부터는 기둥 사이가 좁아져 1배에서 빽빽하다)
// 사용(iso.js drawObj 안, 보관 상자 자리):  else if (kind === 'bank') { const c = bankBuilding(cx, cy, { symbol: cur }); el.push(...c.el); ps.push(...c.poly); }
//   cube(64.7, 22, 'bank')와 PIC.bank는 쓸 곳이 없어진다.
// 입체 좌표 (x, y, z): x는 오른쪽 아래, y는 왼쪽 아래로 가는 바닥 길이(px), z는 위로 가는 높이(px). 앞줄 기둥이 서는 정면이 왼쪽 면(y가 큰 쪽), 옆면이 오른쪽 면(x가 큰 쪽)이다.
// 칠은 흰색(iso-t, iso-w), --pale(iso-l), --stone(iso-r)뿐이고 선은 --ink-2다. 그라데이션과 로고는 없다.
// 면은 가려지는 부분을 뺀 보이는 모양만 그린다. 보관 없음처럼 면이 투명해도 가려진 선이 비쳐 보이지 않는다.
//   ponytail: 가림은 치수 관계로 미리 풀었다(포치 벽 오각형, 몸체 옆면의 ㄱ자, 처마돌림에 가려지는 OV, 바닥판 ㄱ자). 포치 깊이(YE - YW)가 기둥 높이보다 깊어지거나 기둥이 몸체 폭 밖으로 나가면 다시 풀어야 한다.
// 새 CSS는 없다: 쓰는 클래스는 모두 styles.css에 이미 있고(iso-face, iso-l, iso-r, iso-t, iso-w, iso-fl, iso-d, iso-dn, iso-df, iso-fline, iso-fline-d, iso-coin-sym), 보관 없음은 iso-ghost 규칙이 그대로 받는다.
//   BANK 글자와 통화 기호는 코인 기호와 같은 칠이라 iso-coin-sym을 쓴다(먹색 --ink-2, 굵기 800, 보관 없음에서는 --muted 흐리게). 코인 기호 칠을 바꾸면 이 글자도 같이 바뀐다.
const C30 = Math.sqrt(3) / 2, RX = Math.SQRT2 * C30, RY = Math.SQRT1_2;   // 바닥 원 반지름 r은 화면에서 가로 r*RX, 세로 r*RY인 타원
const f = (n) => Math.round(n * 10) / 10;
const g4 = (n) => Math.round(n * 1e4) / 1e4;
const pts = (a) => a.map(([x, y]) => `${f(x)},${f(y)}`).join(' ');
const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
// iso.js의 hull과 같다(모듈 하나로 쓰려고 옮김)
const hull = (a) => {
  const q = [...a].sort((m, n) => m[0] - n[0] || m[1] - n[1]), cr = (o, m, n) => (m[0] - o[0]) * (n[1] - o[1]) - (m[1] - o[1]) * (n[0] - o[0]);
  const half = (s) => { const r = []; for (const t of s) { while (r.length > 1 && cr(r[r.length - 2], r[r.length - 1], t) <= 0) r.pop(); r.push(t); } r.pop(); return r; };
  return [...half(q), ...half([...q].reverse())];
};
// 통화 기호의 잉크 상자 [폭, 높이](글자 크기 1일 때, Pretendard 800 실측). iso.js의 INK와 같다. 없는 기호는 그리지 않는다
const INK = { $: [.573, .885], '€': [.592, .727], '¥': [.535, .707], '₩': [.881, .707], 'HK$': [1.944, .885], 'S$': [1.211, .885] };
const CAP = .707, BASE = .354;   // 대문자 높이, 잉크 가운데에서 글줄 바닥선까지(em). Pretendard 800 실측

// ---- 치수(입체 길이, px). 바꿀 때는 여기만 ----
const HX = 36, YF = 24, YB = -24;                    // 바닥판 반폭, 맨 아래 단 앞(y), 바닥판 뒤(y). 앞뒤 깊이 48이 (0, 0)을 가운데로 선다
const RISE = 2.6, ZS = 3 * RISE, YT = 15.6;          // 계단 한 단 높이, 계단 전체 높이(기둥이 서는 바닥), 맨 위 단 앞 가장자리 y. 계단은 세 단
const HB = 34, YW = 2, YK = -22;                     // 몸체와 엔타블러처 반폭, 포치 안쪽 벽 y, 몸체 뒷면 y
const AB = 3.4, YE = 12.6;                           // 기둥머리 네모판 반폭, 엔타블러처 앞면 y(네모판 앞면과 한 면)
const COL = { rb: 3.3, hb: 1.3, r0: 2.7, r1: 2.3, hs: 21.4, rc: 3, hc: 1.2, ha: 1.6 };   // 기둥: 받침 원판 반지름과 높이, 몸 아래와 위 반지름과 높이, 기둥머리 원판 반지름과 높이, 네모판 높이
const ARCH = 2.4, FR = 10, CORN = 2.4, OV = 1;       // 엔타블러처 아래 띠, BANK를 새기는 띠, 처마돌림 높이, 처마돌림이 내미는 길이
const PITCH = 25;                                    // 지붕 기울기(도). 낮은 맞배지붕
const SHADE = .35;                                   // 기둥 어두운 쪽이 시작하는 자리(반지름의 몇 배, 가운데에서 오른쪽으로)

export function bankBuilding(cx, cy, opt = {}) {
  const cols = Math.min(6, Math.max(4, Math.round(opt.cols ?? 4))), sym = String(opt.symbol ?? '').trim();
  const P = (x, y, z) => [cx + (x - y) * C30, cy + (x + y) * .5 - z];
  const el = [], ps = [];
  const face = (c, a) => { ps.push(...a); el.push(`<polygon class="iso-face ${c}" points="${pts(a)}"/>`); };
  const fl = (c, a) => el.push(`<polygon class="iso-fl ${c}" points="${pts(a)}"/>`);
  const ln = (a, c = '') => el.push(`<polyline class="iso-d iso-dn ${c}" points="${pts(a)}"/>`);
  const win = (a) => el.push(`<polygon class="iso-d iso-df" points="${pts(a)}"/>`);                 // 흰 칸에 선(문, 창)
  const qL = (y, x0, x1, z0, z1) => [P(x0, y, z1), P(x1, y, z1), P(x1, y, z0), P(x0, y, z0)];   // 정면(왼쪽 면) 위의 네모
  const qR = (x, y0, y1, z0, z1) => [P(x, y1, z1), P(x, y0, z1), P(x, y0, z0), P(x, y1, z0)];   // 옆면(오른쪽 면) 위의 네모
  // 정면에 눕힌 글: 글줄이 x 방향으로 가고 글자 위가 z 방향이다. (x, y, z)는 글줄 가운데 바닥선. 글자 사이를 벌리면 끝 글자 뒤 빈칸만큼 가운데가 밀리므로 ls/2로 되돌린다
  const text = (x, y, z, s, str, ls = 0) => { const [X, Y] = P(x, y, z); return `<text class="iso-coin-sym" transform="matrix(${g4(C30)} .5 0 1 ${f(X)} ${f(Y)})" x="${ls / 2}" font-size="${f(s)}" text-anchor="middle"${ls ? ` letter-spacing="${ls}"` : ''}>${esc(str)}</text>`; };

  // ---- 높이 ----
  const zC = ZS + COL.hb + COL.hs + COL.hc + COL.ha, zA = zC + ARCH, zF = zA + FR, zE = zF + CORN;   // 기둥 맨 위(엔타블러처 아래), 띠 둘의 경계, 처마돌림 아래, 처마돌림 위(지붕 시작)
  const zv = zF - OV;                                                                               // 처마돌림에 윗부분이 가려진 엔타블러처 면의 보이는 맨 위
  const HW = HB + OV, hp = HW * Math.tan(PITCH * Math.PI / 180), YP = YE + OV, YR = YK - OV;       // 삼각 머리 반폭과 높이, 처마돌림 앞면 y, 지붕 뒤 끝 y

  // ---- 바닥판과 계단: 오른쪽 옆은 계단 단면 하나, 앞은 단마다 세로면(riser)과 윗면(tread). 윗 바닥은 몸체에 가려지지 않은 앞 포치 바닥과 오른쪽 가장자리만 ----
  const ys = [YF, (YF + YT) / 2, YT];
  face('iso-r', [P(HX, YB, 0), ...ys.flatMap((y, i) => [P(HX, y, i * RISE), P(HX, y, (i + 1) * RISE)]), P(HX, YB, ZS)]);
  ys.forEach((y, i) => face('iso-l', qL(y, -HX, HX, i * RISE, (i + 1) * RISE)));
  for (const [i, z] of [[0, RISE], [1, 2 * RISE]]) face('iso-t', [P(-HX, ys[i + 1], z), P(HX, ys[i + 1], z), P(HX, ys[i], z), P(-HX, ys[i], z)]);
  face('iso-t', [P(-HX, YT, ZS), P(HX, YT, ZS), P(HX, YB, ZS), P(HB, YB, ZS), P(HB, YW, ZS), P(-HX, YW, ZS)]);

  // ---- 포치 안쪽 벽과 문: 그늘이라 어두운 톤. 벽 윗부분은 엔타블러처 아래선에 가려져 보이는 모양이 오각형이다(왼쪽 위 꼭짓점은 벽 왼쪽 끝이 엔타블러처 아래선과 만나는 곳, 오른쪽 위 둘은 엔타블러처 오른쪽 아래 모서리와 벽 오른쪽 위 모서리) ----
  // 기둥 줄 뒤에 있어 화면에서는 오른쪽으로 밀려 보이므로 문은 기둥 사이 가운데에서 포치 깊이(YC - YW)만큼 왼쪽에 둔다
  const YC = YE - AB, xs = Array.from({ length: cols }, (_, i) => -(HB - AB) + i * 2 * (HB - AB) / (cols - 1)), g = Math.floor((cols - 1) / 2), xd = (xs[g] + xs[g + 1]) / 2 - (YC - YW);
  face('iso-r', [P(-HB, YW, ZS), P(HB, YW, ZS), P(HB, YW, zC), P(HB, YE, zC), P(-HB, YW, zC - (YE - YW))]);
  win(qL(YW, xd - 3.2, xd + 3.2, ZS, ZS + 14)); ln([P(xd, YW, ZS), P(xd, YW, ZS + 14)]);

  // ---- 기둥: 받침 원판, 위로 가늘어지는 기둥 몸, 기둥머리 원판, 네모판 ----
  // 원기둥(위 반지름 r1, 아래 반지름 r0): 옆면 전체(밝은 쪽), 오른쪽 어두운 쪽, 가장자리 선, 필요하면 윗면
  const cyl = (x, y, r0, r1, z0, z1, top) => {
    const [X, Yb] = P(x, y, z0), Yt = P(x, y, z1)[1], a0 = r0 * RX, b0 = r0 * RY, a1 = r1 * RX, b1 = r1 * RY;
    const d0 = SHADE * a0, e0 = b0 * Math.sqrt(1 - SHADE * SHADE), d1 = SHADE * a1, e1 = b1 * Math.sqrt(1 - SHADE * SHADE);
    const arc = (a, b, s, ex, ey) => `A${f(a)} ${f(b)} 0 0 ${s} ${f(ex)} ${f(ey)}`;
    el.push(`<path class="iso-fl iso-l" d="M${f(X - a1)} ${f(Yt)}L${f(X - a0)} ${f(Yb)}${arc(a0, b0, 0, X + a0, Yb)}L${f(X + a1)} ${f(Yt)}${arc(a1, b1, 1, X - a1, Yt)}z"/>`);
    el.push(`<path class="iso-fl iso-r" d="M${f(X + d1)} ${f(Yt + e1)}L${f(X + d0)} ${f(Yb + e0)}${arc(a0, b0, 0, X + a0, Yb)}L${f(X + a1)} ${f(Yt)}${arc(a1, b1, 1, X + d1, Yt + e1)}z"/>`);
    el.push(`<path class="iso-d iso-dn" d="M${f(X - a1)} ${f(Yt)}L${f(X - a0)} ${f(Yb)}${arc(a0, b0, 0, X + a0, Yb)}L${f(X + a1)} ${f(Yt)}"/>`);
    if (top) el.push(`<ellipse class="iso-d iso-df" cx="${f(X)}" cy="${f(Yt)}" rx="${f(a1)}" ry="${f(b1)}"/>`);
  };
  for (const x of xs) {
    const z1 = ZS + COL.hb, z2 = z1 + COL.hs, z3 = z2 + COL.hc;
    cyl(x, YC, COL.rb, COL.rb, ZS, z1, true);
    cyl(x, YC, COL.r0, COL.r1, z1, z2, false);
    cyl(x, YC, COL.rc, COL.rc, z2, z3, false);
    // 기둥머리 네모판: 앞면은 엔타블러처 앞면과 한 면, 윗면은 엔타블러처가 덮는다
    const qa = qL(YC + AB, x - AB, x + AB, z3, zC), qb = qR(x + AB, YC - AB, YC + AB, z3, zC);
    fl('iso-l', qa); fl('iso-r', qb); ln([...qa, qa[0]]); ln([...qb, qb[0]]);
  }

  // ---- 몸체 오른쪽 옆: 한 면으로 이어지는 벽과 엔타블러처 옆면(포치 쪽은 열려 있어 기둥 높이까지 비어 있다). 창은 세로로 긴 칸 셋 ----
  face('iso-r', [P(HB, YK, ZS), P(HB, YW, ZS), P(HB, YW, zC), P(HB, YE, zC), P(HB, YE, zv), P(HB, YK, zv)]);
  for (const y of [-17.6, -10, -2.4]) win(qR(HB, y - 2, y + 2, ZS + 6.5, zC - 2));
  ln([P(HB, YE, zA), P(HB, YK, zA)]); ln([P(HB, YW, zC), P(HB, YK, zC)]);

  // ---- 엔타블러처 앞면: 아래 띠(architrave)와 BANK를 새긴 띠(frieze). 띠 윗부분 OV는 처마돌림에 가려진다 ----
  face('iso-l', qL(YE, -HB, HB, zC, zv));
  ln([P(-HB, YE, zA), P(HB, YE, zA)]);
  const fs = 9;
  el.push(text(0, YE, zA + (FR - OV - CAP * fs) / 2, fs, 'BANK', 1.2));
  // 처마돌림: 엔타블러처 위에 조금 내민 띠
  face('iso-l', qL(YP, -HW, HW, zF, zE));
  face('iso-r', qR(HW, YR, YP, zF, zE));

  // ---- 삼각 지붕 머리: 흰 바탕에 안쪽 테두리 선 하나와 통화 기호 ----
  face('iso-w', [P(-HW, YP, zE), P(HW, YP, zE), P(0, YP, zE + hp)]);
  const L = Math.hypot(HW, hp), dIn = 1.6, zb = 1, st = hp / HW, za = hp - dIn * L / HW, xb = HW - (zb * HW + dIn * L) / hp;   // 안쪽 삼각형: 바닥 zb, 꼭대기 za, 밑 반폭 xb. 변이 바깥 변과 dIn 떨어져 나란하다
  ln([P(-xb, YP, zE + zb), P(0, YP, zE + za), P(xb, YP, zE + zb), P(-xb, YP, zE + zb)]);
  if (INK[sym]) {
    const [w, h] = INK[sym], zs = 3.2, s = Math.min(9, (za - 2.6 - zs) / (h + w * st / 2));   // 기호 글자 크기: 안쪽 삼각형 두 윗모서리와 1.1 이상 떨어지게. 한 글자는 모두 10
    el.push(text(0, YP, zE + zs + h * s / 2 - BASE * s, s, sym));   // 잉크 상자 바닥이 zs, 잉크 가운데가 글줄 바닥선에서 BASE*s 위(iso.js symText와 같은 기준)
  }

  // ---- 낮은 맞배지붕: 용마루가 앞뒤로 가고 오른쪽 비탈만 보인다. 용마루와 나란한 가는 선 둘 ----
  face('iso-l', [P(HW, YP, zE), P(HW, YR, zE), P(0, YR, zE + hp), P(0, YP, zE + hp)]);
  el.push(`<path class="iso-fline iso-fline-d" d="${[1 / 3, 2 / 3].map((t) => `M${P(HW * (1 - t), YP, zE + hp * t).map(f).join(' ')}L${P(HW * (1 - t), YR, zE + hp * t).map(f).join(' ')}`).join('')}"/>`);

  const out = opt.ghost ? [`<g class="iso-ghost">${el.join('')}</g>`] : el;
  return { el: out, ps, poly: hull(ps) };
}
