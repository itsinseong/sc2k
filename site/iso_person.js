// 이용자 그림(시험판): 얇은 발판 위에 선 사람. 머리는 구, 몸통은 둥근 어깨(타원체 윗반쪽)다. 흰 테두리는 어디에도 없다.
// iso.js drawObj와 같은 정등각 투영을 쓴다: 입체 좌표 (x, y, z)는 화면 (cx + (x - y) * C30, cy + (x + y) / 2 - z).
//   (cx, cy)는 발판 바닥 가운데(drawObj가 이용자 자리로 주는 값)이고 발판은 iso.js plate()와 같다(46.2 x 46.2, 높이 6).
//   사용(drawObj 안, 이용자 자리):  const c = personFigure(cx, cy); el.push(c.svg); ps.push(...c.poly);
//   되돌림: svg는 문자열(발판, 그림자, 몸통, 머리 차례, <g> 없음), poly는 전체를 감싸는 볼록 윤곽 [[x, y], ...]
//   opt.k: 그림 크기 배율(기본 1은 iso.js PS 1.2일 때의 크기). 발판 크기는 그대로다.
//   붙일 때: drawObj의 이용자 자리(plate())에서 personFigure를 부르고, makeScene의 ppl 윤곽 점 여섯 개와 person()은 없앤다(poly가 그림까지 감싸고, 발판과 그림이 한 묶음 <g class="iso-blk">으로 그려진다).
// 모양: 빛이 왼쪽 위 앞에서 온다(상자의 왼쪽 면이 밝고 오른쪽 면이 어두운 것과 같은 쪽). 밝은 쪽과 그늘진 쪽 두 톤만 쓰고 번짐(그라데이션)은 없다.
//   겉모양(윤곽)은 타원 호로 그리고, 그늘진 쪽만 면을 점으로 훑어 구한다(darkSide). 머리와 몸통이 같은 빛을 쓰므로 그늘이 같은 쪽에 진다.
//   크기: 어깨 너비와 머리 지름은 옛 person()과 같고(26.9, 17.5), 어깨 높이 대 반너비 비율도 같다(1.4). 옛 그림은 발판 가운데 위에 떠 있었고 이 그림은 발판 가운데에 선다.
//
// 붙여 넣을 CSS(styles.css의 .iso-fig 규칙을 이것으로 바꾼다. .iso-ppl .iso-t의 어두운 윗면 규칙도 지운다: 발판 윗면은 다른 블록처럼 흰색이다).
/*
.iso-pf-l{fill:var(--ink-2)}
.iso-pf-d{fill:var(--ink)}
.iso-pf-s1{fill:var(--pale)}
.iso-pf-s2{fill:var(--stone)}
.iso-ghost .iso-pf-l,.iso-ghost .iso-pf-d{fill:var(--stone)}
.iso-ghost .iso-pf-s1,.iso-ghost .iso-pf-s2{display:none}
*/
const C30 = Math.sqrt(3) / 2, S = Math.sqrt(1.5);          // S: 입체 길이 1이 화면에서 구의 반지름으로 보이는 몫(= 바닥 원의 가로 반지름 몫, sqrt2 * C30)
const f = (n) => Math.round(n * 100) / 100;
// iso.js의 hull과 같다(모듈 하나로 쓰려고 옮김)
const hull = (a) => {
  const q = [...a].sort((m, n) => m[0] - n[0] || m[1] - n[1]), cr = (o, m, n) => (m[0] - o[0]) * (n[1] - o[1]) - (m[1] - o[1]) * (n[0] - o[0]);
  const half = (s) => { const r = []; for (const t of s) { while (r.length > 1 && cr(r[r.length - 2], r[r.length - 1], t) <= 0) r.pop(); r.push(t); } r.pop(); return r; };
  return [...half(q), ...half([...q].reverse())];
};

// 빛: 수평 방향 LA(x축에서 잰 각), 높이각 LE. 135도면 상자 왼쪽 면은 밝고 오른쪽 면은 어두워 가운데에서 반반으로 갈린다. 127도는 그늘 경계가 어깨 둘레에서 가운데보다 오른쪽 1.4할 자리에 선다
const LA = 127 * Math.PI / 180, LE = 45 * Math.PI / 180, LH = Math.cos(LE), LZ = Math.sin(LE);
const TV = Math.PI / 4;                                      // 보는 쪽 수평 방향(1, 1, 1)의 각
const DL = Math.atan2(Math.sin(LA + Math.PI - TV), Math.cos(LA + Math.PI - TV));   // 그늘진 쪽 가운데가 보는 쪽에서 얼마나 돌아 있는가
const arcOf = (c) => c >= 1 ? -1 : c <= -1 ? Math.PI : Math.acos(c);               // cos(t) >= c 인 t의 반폭. 하나도 없으면 -1, 전부면 PI

// 회전체의 그늘진 쪽: prof는 아래에서 위로 [높이, 반지름] 목록(세로축은 x = y = 0). 화면에 보이는 면 가운데 빛을 등진 쪽을 다각형 점 목록으로 되돌린다.
// 겹(높이 하나의 원)마다 보이는 호와 그늘진 호의 겹침 [a, b]를 구하고, 한쪽 끝 점들을 위로, 다른 쪽 끝 점들을 아래로 이으면 경계가 된다.
// ponytail: 그늘진 곳이 위아래로 이어진 한 덩어리라고 가정한다. 여러 덩어리로 갈라지는 모양이면 이 다각형은 틀린다
function darkSide(prof, Q) {
  const rs = [];
  prof.forEach(([z, r], j) => {
    const [z0, r0] = prof[Math.max(0, j - 1)], [z1, r1] = prof[Math.min(prof.length - 1, j + 1)], l = Math.hypot(z1 - z0, r1 - r0);
    const nr = (z1 - z0) / l, nz = -(r1 - r0) / l;           // 겉면 바깥쪽 법선(반지름 방향 몫, 위쪽 몫)
    const seen = arcOf(-nz / (Math.SQRT2 * nr)), dark = arcOf(nz * LZ / (nr * LH));
    if (seen < 0 || dark < 0) return;
    let v = null;
    for (const s of [-2 * Math.PI, 0, 2 * Math.PI]) {         // 보이는 호 [-seen, seen]과 그늘진 호의 겹침
      const a = Math.max(-seen, DL + s - dark), b = Math.min(seen, DL + s + dark);
      if (b > a && (!v || b - a > v[1] - v[0])) v = [a, b];
    }
    if (v) rs.push({ z, r, v });
  });
  if (!rs.length) return [];
  const at = (q, t) => { const u = TV + t; return Q(q.r * Math.cos(u), q.r * Math.sin(u), q.z); };
  const arc = (q, p, s) => { const n = q.r < 1e-6 ? 1 : Math.max(1, Math.ceil(Math.abs(s - p) / .06)); return Array.from({ length: n - 1 }, (_, i) => at(q, p + (s - p) * (i + 1) / n)); };
  const lo = rs[0], hi = rs[rs.length - 1];
  return [...rs.map((q) => at(q, q.v[0])), ...arc(hi, hi.v[0], hi.v[1]), ...rs.map((q) => at(q, q.v[1])).reverse(), ...arc(lo, lo.v[1], lo.v[0])];
}

// 위로 가면서 반지름이 줄어드는 타원체 윗반쪽의 [높이, 반지름] 목록: 높이 zc + hz sin(a), 반지름 r cos(a). a는 a0에서 90도까지 deg도씩
const ellip = (zc, hz, r, a0, deg) => { const o = []; for (let a = a0; a <= 90; a += deg) o.push([zc + hz * Math.sin(a * Math.PI / 180), r * Math.cos(a * Math.PI / 180)]); return o; };

export function personFigure(cx, cy, opt = {}) {
  const { k = 1 } = opt;
  const P = (x, y, z) => [cx + (x - y) * C30, cy + (x + y) * .5 - z];
  const Q = (x, y, z) => P(x, y, z + 6);                     // 발판 윗면(높이 6)에서 잰 좌표
  const el = [], ps = [];
  const pts = (a) => `points="${a.map(([x, y]) => `${f(x)},${f(y)}`).join(' ')}"`;
  const face = (c, a) => { ps.push(...a); el.push(`<polygon class="iso-face ${c}" ${pts(a)}/>`); };
  // 발판: iso.js plate()와 같다. 윗면은 흰색이라 흰 테두리가 없다
  const d = 23.1;
  face('iso-l', [P(-d, d, 6), P(d, d, 6), P(d, d, 0), P(-d, d, 0)]);
  face('iso-r', [P(d, d, 6), P(d, -d, 6), P(d, -d, 0), P(d, d, 0)]);
  face('iso-t', [P(-d, -d, 6), P(d, -d, 6), P(d, d, 6), P(-d, d, 6)]);

  const R = 11 * k, HD = 17 * k, RH = 8.76 / S * k, GAP = 1.8 * k;   // 어깨 반지름과 높이(입체 길이), 머리 반지름, 어깨와 머리 사이 틈(화면 길이)
  // 그림자: 발판 윗면에 눕힌 타원 둘(바깥이 옅고 안쪽이 진하다). 반지름 rr, 빛 반대쪽으로 dd만큼 밀린다
  const sh = (rr, dd, c) => { const [x, y] = Q(-dd * k * Math.cos(LA), -dd * k * Math.sin(LA), 0); el.push(`<ellipse class="${c}" cx="${f(x)}" cy="${f(y)}" rx="${f(rr * S)}" ry="${f(rr * S / Math.sqrt(3))}"/>`); };
  sh(R + 3.8 * k, 5.5, 'iso-pf-s1');
  sh(R + 1.6 * k, 4.1, 'iso-pf-s2');

  // 몸통: 바닥 원 앞쪽 반타원과 윗부분 반타원이 가로 지름 하나를 나눈다. 윗부분 윤곽의 세로 반지름은 타원체(R, R, HD)를 정등각으로 본 값 S * sqrt((R^2 + 2 HD^2) / 3)
  const [bx, by] = Q(0, 0, 0), rx = R * S, ryb = rx / Math.sqrt(3), ryd = S * Math.sqrt((R * R + 2 * HD * HD) / 3);
  el.push(`<path class="iso-pf-l" d="M${f(bx - rx)} ${f(by)}A${f(rx)} ${f(ryb)} 0 0 0 ${f(bx + rx)} ${f(by)}A${f(rx)} ${f(ryd)} 0 0 0 ${f(bx - rx)} ${f(by)}z"/>`);
  el.push(`<polygon class="iso-pf-d" ${pts(darkSide(ellip(0, HD, R, 0, 2), Q))}/>`);
  // 머리: 반지름 RH 구. 화면에서는 지름이 같은 원이다. 가운데 높이 = 어깨 맨 위 + 틈 + 머리 반지름
  const zh = ryd + GAP + RH * S, [hx, hy] = Q(0, 0, zh), hr = RH * S;
  el.push(`<circle class="iso-pf-l" cx="${f(hx)}" cy="${f(hy)}" r="${f(hr)}"/>`);
  el.push(`<polygon class="iso-pf-d" ${pts(darkSide(ellip(zh, RH, RH, -90, 3), Q))}/>`);

  // 바깥 윤곽: 발판 모서리, 몸통(밑 앞쪽 반타원, 윗부분 반타원), 머리 원 위의 점
  const on = (x, y, a, b, u0, u1) => Array.from({ length: 13 }, (_, i) => { const u = u0 + (u1 - u0) * i / 12; return [x + a * Math.cos(u), y + b * Math.sin(u)]; });
  ps.push(...on(bx, by, rx, ryb, 0, Math.PI), ...on(bx, by, rx, ryd, Math.PI, 2 * Math.PI), ...on(hx, hy, hr, hr, 0, 2 * Math.PI));
  return { svg: el.join(''), poly: hull(ps) };
}
