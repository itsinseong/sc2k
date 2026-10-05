// 보관 블록 그림: 금고. 은행이 아닌 보관(미국 수탁기관, 홍콩 수탁자, 싱가포르와 일본 신탁계좌)에 쓴다.
//   vaultBuilding(cx, cy, opt) -> { el, ps, poly }   (iso_bank.js bankBuilding과 같은 약속: (cx, cy)=바닥판 가운데, el=SVG 조각 목록, ps=바깥 윤곽 꼭짓점, poly=볼록 윤곽)
//   opt.word: 윗면 글자 'CUSTODY'(기본) 또는 'TRUST'.  opt.ghost: 참이면 el 전체를 <g class="iso-ghost">로 감쌈
//   바닥판 가로 68 x 깊이 44, 화면 윤곽은 폭 약 98 x 높이 약 78. 새 CSS 없음(iso-face, iso-l/r/t, iso-d, iso-df, iso-dk, iso-fl, iso-coin-sym만 씀)
// 입체 좌표는 iso_bank.js와 같다: x 오른쪽 아래, y 왼쪽 아래(앞면이 y가 큰 쪽=왼쪽 면), z 위.
const C30 = Math.sqrt(3) / 2;
const f = (n) => Math.round(n * 10) / 10;
const g4 = (n) => Math.round(n * 1e4) / 1e4;
const pts = (a) => a.map(([x, y]) => `${f(x)},${f(y)}`).join(' ');
const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const hull = (a) => {
  const q = [...a].sort((m, n) => m[0] - n[0] || m[1] - n[1]), cr = (o, m, n) => (m[0] - o[0]) * (n[1] - o[1]) - (m[1] - o[1]) * (n[0] - o[0]);
  const half = (s) => { const r = []; for (const t of s) { while (r.length > 1 && cr(r[r.length - 2], r[r.length - 1], t) <= 0) r.pop(); r.push(t); } r.pop(); return r; };
  return [...half(q), ...half([...q].reverse())];
};

// ---- 치수(px) ----
const PX = 34, PY = 22, PZ = 4;          // 낮은 받침 반폭, 반깊이, 높이
const BX = 28, BY = 17, BZ = 58;         // 금고 몸체 반폭, 반깊이, 맨 위 높이
const DZ = 28, DR = 19;                  // 문 중심 높이, 바깥 반지름

export function vaultBuilding(cx, cy, opt = {}) {
  const word = String(opt.word ?? 'CUSTODY');
  const P = (x, y, z) => [cx + (x - y) * C30, cy + (x + y) * .5 - z];
  const el = [], ps = [];
  const face = (c, a) => { ps.push(...a); el.push(`<polygon class="iso-face ${c}" points="${pts(a)}"/>`); };
  const ln = (a) => el.push(`<polyline class="iso-d iso-dn" points="${pts(a)}"/>`);
  const qL = (y, x0, x1, z0, z1) => [P(x0, y, z1), P(x1, y, z1), P(x1, y, z0), P(x0, y, z0)];
  const qR = (x, y0, y1, z0, z1) => [P(x, y1, z1), P(x, y0, z1), P(x, y0, z0), P(x, y1, z0)];
  // 정면(y=BY) 위의 원: 중심 (x, z), 반지름 r. 화면에서는 타원이라 꼭짓점 40개 다각형으로 그린다
  const disc = (x, z, r, cls) => el.push(`<polygon class="iso-d ${cls}" points="${pts(Array.from({ length: 40 }, (_, i) => P(x + r * Math.cos(i * Math.PI / 20), BY, z + r * Math.sin(i * Math.PI / 20))))}"/>`);

  // 받침: 몸체에 가려지지 않는 앞과 오른쪽 가장자리 ㄱ자 윗면 + 두 옆면
  face('iso-r', qR(PX, -PY, PY, 0, PZ));
  face('iso-l', qL(PY, -PX, PX, 0, PZ));
  face('iso-t', [P(-PX, PY, PZ), P(PX, PY, PZ), P(PX, -PY, PZ), P(BX, -PY, PZ), P(BX, BY, PZ), P(-PX, BY, PZ)]);
  // 몸체
  face('iso-r', qR(BX, -BY, BY, PZ, BZ));
  face('iso-l', qL(BY, -BX, BX, PZ, BZ));
  face('iso-t', [P(-BX, BY, BZ), P(BX, BY, BZ), P(BX, -BY, BZ), P(-BX, -BY, BZ)]);
  // 옆면: 보강 줄 둘, 앞면: 위아래 가는 줄
  for (const z of [PZ + 8, BZ - 8]) ln([P(BX, BY, z), P(BX, -BY, z)]);
  // 문: 흰 바깥 고리(볼트) > 석색 안쪽 판 > 흰 허브
  disc(0, DZ, DR, 'iso-df');
  for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 + Math.PI / 8; disc((DR - 2.6) * Math.cos(a), DZ + (DR - 2.6) * Math.sin(a), .9, 'iso-dk'); }
  disc(0, DZ, DR - 5.2, 'iso-dp');
  // 경첩: 문 왼쪽 가장자리 위아래
  for (const dz of [-10, 10]) { el.push(`<polygon class="iso-d iso-df" points="${pts(qL(BY, -DR - 2.5, -DR + 3, DZ + dz - 2.6, DZ + dz + 2.6))}"/>`); }
  // 손잡이: 허브에서 세 갈래 살(위, 왼아래, 오른아래)과 끝 손잡이
  const sp = [90, 210, 330].map((d) => d * Math.PI / 180);
  for (const a of sp) ln([P(0, BY, DZ), P(10.5 * Math.cos(a), BY, DZ + 10.5 * Math.sin(a))]);
  for (const a of sp) disc(10.5 * Math.cos(a), DZ + 10.5 * Math.sin(a), 2, 'iso-df');
  disc(0, DZ, 4.2, 'iso-df'); disc(0, DZ, 1.3, 'iso-dk');
  // 글자: 윗면 가운데, x축(오른쪽 아래) 방향으로 눕혀 씀. 윗면 폭 56 안에 들어가게 글자 수로 크기를 정함
  const fs = Math.min(12, 46 / (word.length * .72)), ls = .6, [X, Y] = P(0, 0, BZ);
  el.push(`<text class="iso-coin-sym" transform="matrix(${g4(C30)} .5 ${g4(-C30)} .5 ${f(X)} ${f(Y)})" x="${ls / 2}" y="${f(.36 * fs)}" font-size="${f(fs)}" text-anchor="middle" letter-spacing="${ls}">${esc(word)}</text>`);

  const out = opt.ghost ? [`<g class="iso-ghost">${el.join('')}</g>`] : el;
  return { el: out, ps, poly: hull(ps) };
}
