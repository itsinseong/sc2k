// EU 일반(eu-emt) 감독 블록: 회원국 27곳의 국가 감독기관을 한 덩어리로 보여 준다.
// 한 건물로 특정할 수 없으므로 건물 모양은 베끼지 않는다. 같은 네모 상자 27개를 바닥판 하나(공동 바닥) 위에 격자로 세우고,
// 상자마다 지붕에 그 나라 국기를 4:3 그대로 눕혀 붙인다. 지붕이 4:3이라 국기가 가장자리까지 꼭 맞는다.
// iso_buildings.js 건물과 같은 약속으로 그린다: (cx, cy, opt) -> { el, ps, poly }.
//   el: SVG 조각 문자열 목록, ps: 바깥 윤곽(iso-face) 꼭짓점 목록, poly: 그 전체를 감싸는 볼록 윤곽(이름표 자리 잡기와 겹침 검사에 쓴다)
//   (cx, cy)는 바닥판 가운데가 화면에서 놓일 자리. opt.k는 크기 배율(기본 1). 건물 쪽 약속의 세 번째 인자(국기 파일 이름)가 오면 무시한다.
// 입체 좌표 (x, y, z)는 iso.js와 같다: x는 오른쪽 아래, y는 왼쪽 아래로 가는 바닥 길이(px), z는 위로 가는 높이(px).
// 국기는 flag-icons 7.5.0(MIT)의 4x3 SVG를 flags/<코드>.svg로 쓴다. 코드와 놓는 차례는 EU_CODES(영어 이름 가나다순 27개).
// iso.js 연결(drawObj 안): else if (kind === 'eu27') { const c = euAuthorities(cx, cy, { k }); el.push(...c.el); ps.push(...c.poly); }
const C30 = Math.sqrt(3) / 2;
const f = (n) => Math.round(n * 10) / 10;
const g5 = (n) => Math.round(n * 1e5) / 1e5;
const pts = (a) => a.map(([x, y]) => `${f(x)},${f(y)}`).join(' ');
// iso.js의 hull과 같다(모듈 하나로 쓰려고 옮김)
const hull = (a) => {
  const q = [...a].sort((m, n) => m[0] - n[0] || m[1] - n[1]), cr = (o, m, n) => (m[0] - o[0]) * (n[1] - o[1]) - (m[1] - o[1]) * (n[0] - o[0]);
  const half = (s) => { const r = []; for (const t of s) { while (r.length > 1 && cr(r[r.length - 2], r[r.length - 1], t) <= 0) r.pop(); r.push(t); } r.pop(); return r; };
  return [...half(q), ...half([...q].reverse())];
};

export const EU_CODES = 'at be bg hr cy cz dk ee fi fr de gr hu ie it lv lt lu mt nl pl pt ro sk si es se'.split(' ');

// 길이는 px(배율 1). 6행(y) 격자에 27곳을 열 순서(뒤에서 앞으로)로 채운다: 열 4개는 6곳씩, 마지막 열(오른쪽 앞 변)은 3곳이라 앞쪽 3칸이 빈다.
// 바닥판은 상자를 둘레 RIM만큼 덮는 ㄴ자 모양이라 빈 칸에 맨바닥이 드러나지 않는다. 상자 지붕은 BW x BD = 4:3
const ROWS = 6, BD = 14, BW = BD * 4 / 3, GAP = 2, RIM = 3, PLATE = 5, H = 9;

export function euAuthorities(cx, cy, opt) {
  const k = +opt?.k || 1, COLS = Math.ceil(EU_CODES.length / ROWS), last = EU_CODES.length - (COLS - 1) * ROWS, PX = BW + GAP, PY = BD + GAP;
  const P = (x, y, z) => [cx + (x - y) * C30 * k, cy + ((x + y) * .5 - z) * k];
  const el = [], ps = [];
  const face = (c, a) => { ps.push(...a); el.push(`<polygon class="iso-face ${c}" points="${pts(a)}"/>`); };
  const X0 = -(COLS * BW + (COLS - 1) * GAP) / 2, Y0 = -(ROWS * BD + (ROWS - 1) * GAP) / 2;   // 격자의 뒤쪽 모서리(x, y가 가장 작은 곳)
  // 바닥판: 점 여섯 개를 시계 방향(y가 아래로 가는 평면)으로 돈다. x가 줄어드는 변은 바깥이 +y라 왼쪽 면, y가 늘어나는 변은 바깥이 +x라 오른쪽 면이 보인다
  const xl = X0 - RIM, xr = -X0 + RIM, yt = Y0 - RIM, yb = -Y0 + RIM, xc = X0 + (COLS - 1) * PX - GAP + RIM, yc = Y0 + last * PY - GAP + RIM;
  const A = [[xl, yt], [xr, yt], [xr, yc], [xc, yc], [xc, yb], [xl, yb]];
  A.forEach(([x, y], i) => {
    const [x1, y1] = A[(i + 1) % A.length], wall = [P(x, y, PLATE), P(x1, y1, PLATE), P(x1, y1, 0), P(x, y, 0)];
    if (x1 < x) face('iso-l', wall); else if (y1 > y) face('iso-r', wall);
  });
  face('iso-t', A.map(([x, y]) => P(x, y, PLATE)));
  // 상자는 뒤에서 앞으로(x + y가 작은 쪽부터) 그린다. 지붕 높이가 모두 같고 서로 떨어져 있어 앞 상자가 뒤 상자의 지붕을 가리지 않는다
  const cells = EU_CODES.map((code, n) => ({ code, x: X0 + Math.floor(n / ROWS) * PX, y: Y0 + (n % ROWS) * PY }));
  for (const { code, x, y } of cells.sort((a, b) => a.x + a.y - b.x - b.y)) {
    const z = PLATE + H, o = P(x, y, z);
    face('iso-l', [P(x, y + BD, z), P(x + BW, y + BD, z), P(x + BW, y + BD, PLATE), P(x, y + BD, PLATE)]);
    face('iso-r', [P(x + BW, y + BD, z), P(x + BW, y, z), P(x + BW, y, PLATE), P(x + BW, y + BD, PLATE)]);
    face('iso-t', [o, P(x + BW, y, z), P(x + BW, y + BD, z), P(x, y + BD, z)]);
    // 국기는 640 x 480 그대로 두고 지붕 평행사변형에 맞춰 눕힌다(Chrome은 SVG 그림을 자기 4:3 비율로 그린다). 국기 위쪽은 오른쪽 위를 향한다
    el.push(`<image class="iso-flag" href="flags/${code}.svg" x="0" y="0" width="640" height="480" preserveAspectRatio="none" transform="matrix(${[BW * C30 * k / 640, BW * .5 * k / 640, -BD * C30 * k / 480, BD * .5 * k / 480].map(g5)},${f(o[0])},${f(o[1])})"/>`);
    el.push(`<polyline class="iso-d iso-dn" points="${pts([o, P(x + BW, y, z), P(x + BW, y + BD, z), P(x, y + BD, z), o])}"/>`);
  }
  return { el, ps, poly: hull(ps) };
}
