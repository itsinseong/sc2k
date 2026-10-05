// 감독 블록으로 쓰는 실제 건물 셋: 서울 정부서울청사 본관(kr-v1), 홍콩 Two IFC(hk), 싱가포르 MAS 빌딩(sg).
// iso.js의 drawObj가 부르는 것과 같은 약속으로 그린다: (cx, cy, flagFile) -> { el, ps }.
//   el: SVG 조각 문자열 목록, ps: 바깥 윤곽(iso-face) 꼭짓점 목록(이름표 자리 잡기와 겹침 검사에 쓴다).
// 입체 좌표 (x, y, z): x는 오른쪽 아래, y는 왼쪽 아래로 가는 바닥 길이(px), z는 위로 가는 높이(px). 세 길이가 화면에서 같은 크기로 보이는 정등각이다.
// 치수는 참고 사진에서 잰 비율이다. 사진에 없는 선이나 장식은 넣지 않는다.
const C30 = Math.sqrt(3) / 2;
const f = (n) => Math.round(n * 10) / 10;
const g5 = (n) => Math.round(n * 1e5) / 1e5;
const pts = (a) => a.map(([x, y]) => `${f(x)},${f(y)}`).join(' ');

// 건물 하나를 그리는 연장 묶음. (cx, cy)는 바닥 가운데가 화면에서 놓일 자리
function kit(cx, cy, flagFile) {
  const P = (x, y, z) => [cx + (x - y) * C30, cy + (x + y) * .5 - z];
  const el = [], ps = [];
  const face = (c, a) => { ps.push(...a); el.push(`<polygon class="iso-face ${c}" points="${pts(a)}"/>`); };
  const fl = (c, a) => el.push(`<polygon class="iso-fl ${c}" points="${pts(a)}"/>`);
  const ln = (a, c = '') => el.push(`<polyline class="iso-d iso-dn ${c}" points="${pts(a)}"/>`);
  const path = (c, segs) => el.push(`<path class="${c}" d="${segs.map((s) => `M${s.map(([x, y]) => `${f(x)} ${f(y)}`).join('L')}`).join('')}"/>`);
  // 가로 x0~x1, 세로 y0~y1, 높이 z0~z1 상자. 왼쪽 면은 y1, 오른쪽 면은 x1, 윗면은 z1
  const box = (x0, x1, y0, y1, z0, z1, c = {}) => {
    face(c.l ?? 'iso-l', [P(x0, y1, z1), P(x1, y1, z1), P(x1, y1, z0), P(x0, y1, z0)]);
    face(c.r ?? 'iso-r', [P(x1, y1, z1), P(x1, y0, z1), P(x1, y0, z0), P(x1, y1, z0)]);
    if (c.t !== 0) face(c.t ?? 'iso-t', [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]);
  };
  const qL = (y, x0, x1, z0, z1) => [P(x0, y, z1), P(x1, y, z1), P(x1, y, z0), P(x0, y, z0)];   // 왼쪽 면 위의 네모
  const qR = (x, y0, y1, z0, z1) => [P(x, y1, z1), P(x, y0, z1), P(x, y0, z0), P(x, y1, z0)];   // 오른쪽 면 위의 네모
  // 윗면에 국기를 4:3 그대로 눕혀 붙인다. 가로세로 비율은 어느 쪽으로 눕혀도 4:3이다.
  //   along 'x'(기본): 국기 가로가 x 방향, 위쪽이 오른쪽 위를 향한다. along 'y': 국기 가로가 y 방향, 위쪽이 왼쪽 위를 향한다.
  const flag = (xc, yc, z, fw, along = 'x') => {
    if (!flagFile) return;
    const fh = fw * .75, sx = along === 'y' ? fh : fw, sy = along === 'y' ? fw : fh;
    const o = along === 'y' ? P(xc - fh / 2, yc + fw / 2, z) : P(xc - fw / 2, yc - fh / 2, z);
    const m = along === 'y' ? [fw * C30 / 640, -fw * .5 / 640, fh * C30 / 480, fh * .5 / 480] : [fw * C30 / 640, fw * .5 / 640, -fh * C30 / 480, fh * .5 / 480];
    el.push(`<image class="iso-flag" href="flags/${flagFile}.svg" x="0" y="0" width="640" height="480" preserveAspectRatio="none" transform="matrix(${m.map(g5)},${f(o[0])},${f(o[1])})"/>`);
    const a = xc - sx / 2, b = yc - sy / 2;
    ln([P(a, b, z), P(a + sx, b, z), P(a + sx, b + sy, z), P(a, b + sy, z), P(a, b, z)]);
  };
  return { P, el, ps, face, fl, ln, path, box, qL, qR, flag };
}

// 서울 정부서울청사 본관(사진: 앞면 12칸, 옆면 4칸). 가늘고 흰 세로 기둥이 층 전체를 덮고, 기둥 사이에 짙은 창 줄이 선다. 맨 위는 창 없는 띠
// 사진 실측: 한 칸 p, 창 .58p, 기둥 .42p(양끝 기둥도 같다), 앞면 12.42p, 옆면 4.42p, 높이 10.2p, 맨 위 띠 .87p, 창 줄 21층
export function seoul(cx, cy, flagFile) {
  const { P, el, ps, fl, path, box, qL, qR, flag } = kit(cx, cy, flagFile);
  const p = 6.4, Wd = 12.42 * p, Dd = 4.42 * p, Hh = 10.2 * p, x0 = -Wd / 2, x1 = Wd / 2, y0 = -Dd / 2, y1 = Dd / 2, band = .87 * p, zt = Hh - band;
  box(x0, x1, y0, y1, 0, Hh, { l: 'iso-w', r: 'iso-w' });
  // 창 줄 칸: 기둥 .42p, 창 .58p가 되풀이된다. 길이 len에 창 n개가 든다
  const bays = (len, n) => Array.from({ length: n }, (_, i) => { const a = -len / 2 + .42 * p + i * p; return [a, a + .58 * p]; });
  const long = bays(Wd, 12), short = bays(Dd, 4), floors = 21;
  for (const [a, b] of long) { fl('iso-dk', qL(y1, a, b, 0, zt)); fl('iso-dk', qL(y1, a, b, Hh - .77 * p, Hh - .6 * p)); }
  for (const [a, b] of short) { fl('iso-dk', qR(x1, a, b, 0, zt)); fl('iso-dk', qR(x1, a, b, Hh - .77 * p, Hh - .6 * p)); }
  const fls = (bs, q) => { const s = []; for (const [a, b] of bs) for (let i = 1; i < floors; i++) { const z = zt * i / floors; s.push([q(a, z), q(b, z)]); } return s; };
  path('iso-fline', [...fls(long, (u, z) => P(u, y1, z)), ...fls(short, (u, z) => P(x1, u, z))]);
  // 기둥 가운데 홈: 사진의 기둥은 리브 둘 사이에 홈이 있다
  const gv = [];
  for (let k = 0; k <= 12; k++) gv.push([P(x0 + (k + .21) * p, y1, 0), P(x0 + (k + .21) * p, y1, Hh)]);
  for (let k = 0; k <= 4; k++) gv.push([P(x1, y0 + (k + .21) * p, 0), P(x1, y0 + (k + .21) * p, Hh)]);
  path('iso-lv', gv);
  // 지붕은 깊이를 꽉 채우는 4:3 국기 하나(지붕이 4:3이 아니라 가로로 남는 자리는 비워 둔다)
  flag(0, 0, Hh, Dd * 4 / 3);
  return { el, ps };
}

// 홍콩 Two IFC: 네 모서리를 모두 깎은 팔각 단면(깎은 길이는 한 변의 .22)이 거의 곧게 서다가 위쪽에서 둥글게 좁아진다.
// 큰 면 두 개에만 기계층 어두운 띠가 서고, 앞 깎은 면 양옆에 세로 홈이 선다
// 사진 실측: 높이 : 한 변 약 7.2, 단면 곡선은 사진 윤곽과 4% 안에서 맞다, 어두운 띠 높이 .34 .58 .74
export function ifc(cx, cy, flagFile) {
  const { P, el, ps, face, fl, ln, path, qL, qR, flag } = kit(cx, cy, flagFile);
  const s0 = 28, Hh = 186, ch = .22;
  const prof = [[0, 1], [.3, 1], [.6, 1], [.62, .97], [.74, .97], [.76, .93], [.86, .93], [.88, .88], [1, .78]].map(([fz, r]) => [fz * Hh, r * s0]);
  // 팔각 단면의 네 꼭짓점 줄: 왼쪽 큰 면 A-B, 앞 깎은 면 B-C, 오른쪽 큰 면 C-D(화면에서 보이는 세 면)
  const A = prof.map(([z, s]) => P(-s / 2 + ch * s, s / 2, z)), B = prof.map(([z, s]) => P(s / 2 - ch * s, s / 2, z));
  const C = prof.map(([z, s]) => P(s / 2, s / 2 - ch * s, z)), D = prof.map(([z, s]) => P(s / 2, -s / 2 + ch * s, z));
  face('iso-w', [...A, ...[...B].reverse()]);
  face('iso-l', [...B, ...[...C].reverse()]);
  face('iso-l', [...C, ...[...D].reverse()]);
  const sAt = (z) => { let i = 1; while (i < prof.length - 1 && prof[i][0] < z) i++; const [z0, s0_] = prof[i - 1], [z1, s1] = prof[i]; return s0_ + (s1 - s0_) * (z - z0) / (z1 - z0); };
  // 층 가로선: 세 면을 끊김 없이 잇는다. 4층마다
  const lines = [];
  for (let z = Hh / 22; z < Hh * .9; z += Hh / 40) { const s = sAt(z), e = ch * s; lines.push([P(-s / 2 + e, s / 2, z), P(s / 2 - e, s / 2, z), P(s / 2, s / 2 - e, z), P(s / 2, -s / 2 + e, z)]); }
  path('iso-fline iso-fline-d', lines);
  // 세로 홈: 앞 깎은 면 양옆
  ln(prof.map(([z, s]) => P(s / 2 - ch * s, s / 2, z)));
  ln(prof.map(([z, s]) => P(s / 2, s / 2 - ch * s, z)));
  // 기계층 어두운 띠: 큰 면 두 개에만, 깎은 면 쪽에 붙여 큰 면 길이의 76%
  for (const fz of [.34, .79]) {
    const z = fz * Hh, s = sAt(z), e = ch * s, L = s - 2 * e, k = .76 * L;
    fl('iso-dk', qL(s / 2, s / 2 - e - k, s / 2 - e, z, z + 4));
    fl('iso-dk', qR(s / 2, s / 2 - e - k, s / 2 - e, z, z + 4));
  }
  const st = prof[prof.length - 1][1], e = ch * st;
  face('iso-t', [P(-st / 2 + e, -st / 2, Hh), P(st / 2 - e, -st / 2, Hh), P(st / 2, -st / 2 + e, Hh), P(st / 2, st / 2 - e, Hh), P(st / 2 - e, st / 2, Hh), P(-st / 2 + e, st / 2, Hh), P(-st / 2, st / 2 - e, Hh), P(-st / 2, -st / 2 + e, Hh)]);
  flag(0, 0, Hh, st * .85);
  return { el, ps };
}

// 싱가포르 MAS 빌딩: 정면에 굵은 기둥, 양끝에 가는 살창, 맨 위에 창 없는 띠와 가로 틈 두 줄. 옆면은 민벽과 살창
// 사진 실측: 정면 : 옆면 : 높이 = 48 : 36 : 100(지붕이 4:3. 사진에서 띠 있는 정면이 옆면보다 넓다), 정면 가로 구성은 폭의 %
export function mas(cx, cy, flagFile) {
  const { el, ps, fl, box, qL, qR, flag } = kit(cx, cy, flagFile);
  const Wd = 48, Dd = 36, Hh = 100, x0 = -Wd / 2, x1 = Wd / 2, y0 = -Dd / 2, y1 = Dd / 2, zt = Hh * .842;
  box(x0, x1, y0, y1, 0, Hh, { l: 'iso-w', r: 'iso-w' });
  // 정면(왼쪽 면) 가로 구성, 폭의 %: e 모서리 기둥, b 갈색 띠, v 살창, p 밝은 기둥, g 어두운 틈, n 민 패널
  const seg = [['e', 4.4], ['b', 6.7], ['v', 16.9], ['p', 8], ['g', 2.8], ['p', 8], ['g', 3.5], ['n', 10], ['p', 8], ['g', 2.9], ['p', 7.5], ['g', 2.9], ['v', 14.8], ['e', 3.6]];
  let a = x0; const spans = seg.map(([t, w]) => { const r = [t, a, a + w / 100 * Wd]; a = r[2]; return r; });
  // 맨 위: 창 없는 띠 7.5%, 어두운 틈 2.6%, 보 1.9%, 어두운 틈 1.9%, 보 1.9%, 그 아래부터 기둥과 살창
  const ex0 = spans[0][2], ex1 = spans[spans.length - 1][1];
  for (const z of [.84, .875, .91]) fl('iso-dk', qL(y1, ex0, ex1, Hh * z, Hh * z + 2.6));   // 사진: 깊게 들어간 어두운 띠 셋과 그 사이 넓은 흰 보
  // 살창 칸: 어두운 바탕에 밝은 날
  const slats = (q, s0, s1, z1, n) => { const pw = (s1 - s0) / n; for (let i = 0; i < n; i++) fl('iso-dp', q(s0 + i * pw + pw * .5, s0 + i * pw + pw * .85, 0, z1)); };
  for (const [t, s0, s1] of spans) {
    if (t === 'b' || t === 'g') fl('iso-dk', qL(y1, s0, s1, 0, zt));
    if (t === 'v') { fl('iso-dk', qL(y1, s0, s1, 0, zt)); slats((u0, u1, z0, z1) => qL(y1, u0, u1, z0, z1), s0, s1, zt, 6); }
  }
  // 옆면(오른쪽 면): 앞 모서리에서 민벽 30%, 살창 65%, 끝 5%. 살창 위 22%는 왕관이고, 아래에서 위로 선반과 유리 띠, 열린 철골, 정면과 같은 높이의 창 없는 띠(7.5%)다
  const ra = y1 - .3 * Dd, rb = y1 - .95 * Dd, zl = Hh * .775;
  fl('iso-dk', qR(x1, rb, ra, 0, zl));
  slats((u0, u1, z0, z1) => qR(x1, u0, u1, z0, z1), rb, ra, zl, 14);
  fl('iso-dp', qR(x1, rb, ra, zl, Hh * .865));
  fl('iso-dk', qR(x1, rb, ra, Hh * .865, Hh * .925));
  // 지붕이 4:3이라 국기가 가장자리까지 꼭 맞는다
  flag(0, 0, Hh, Wd);
  return { el, ps };
}

// kind 이름으로 찾아 쓰는 표: iso.js의 BUILDING 값('seoul', 'ifc', 'mas')이 그대로 열쇠다
export const BUILDINGS = { seoul, ifc, mas };
