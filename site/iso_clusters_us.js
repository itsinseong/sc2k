// 미국 감독 블록: GENIUS Act 규정을 맡은 연방 기관 넷의 본부 건물을 공동 바닥판 하나 위에 모아 그린다.
//   OCC(통화감독청) Constitution Center, 400 7th St SW, Washington DC 20219        (occ.gov/about/who-we-are/locations)
//   FDIC(연방예금보험공사) 본부, 550 17th Street NW, Washington DC 20429             (fdic.gov/about/topics-or-interests)
//   연준 이사회 Marriner S. Eccles Building, 20th Street and Constitution Avenue NW, Washington DC 20551 (federalreserve.gov/faqs/building-project-faqs.htm)
//   NCUA(신용협동조합청) 본부, 1775 Duke Street, Alexandria VA 22314               (ncua.gov/contact-us)
// 주 감독기관은 수가 많아 그리지 않는다. 건물 셋(OCC, FDIC, 연준)은 Wikimedia Commons 사진에서 베꼈고, NCUA는 Commons에 건물 사진이 없어 네모 상자로 둔다.
// iso_buildings.js 건물과 같은 약속으로 그린다: (cx, cy, opt) -> { el, ps, poly }.
//   el: SVG 조각 문자열 목록, ps: 바깥 윤곽(iso-face) 꼭짓점 목록, poly: 그룹 전체를 감싸는 볼록 윤곽(이름표 자리 잡기와 겹침 검사에 쓴다)
//   (cx, cy)는 공동 바닥판 가운데가 화면에서 놓일 자리. opt는 국기 파일 이름(문자열, 건물 쪽 약속의 세 번째 인자)이거나 { k, flag }.
//   opt.k는 크기 배율(기본 1). opt.flag는 국기 파일 이름(기본 'us', null이면 국기 없음).
//   k = 1일 때 바닥판은 가로 115 x 세로 100px(보통 블록 윗면 65px의 1.6~1.8배), 윤곽 poly는 (cx, cy)에서 왼쪽 88, 오른쪽 95, 위 72(OCC 지붕 모서리 탑), 아래 55px이다.
// 입체 좌표 (x, y, z)는 iso.js와 같다: x는 오른쪽 아래, y는 왼쪽 아래로 가는 바닥 길이, z는 위로 가는 높이. 왼쪽 면은 y가 큰 쪽, 오른쪽 면은 x가 큰 쪽이다.
// 건물마다 치수는 미터로 적고 건물마다 배율 m(px/m)을 곱한다. 한 배율로 그리면 FDIC와 NCUA가 너무 작아 창이 안 보이므로, 큰 건물은 작게 작은 건물은 크게 잡았다.
//   건물 하나의 가로 : 세로 : 높이는 실측 그대로다. 크기 차례(OCC > 연준 > FDIC, NCUA)와 높이 차례(OCC가 가장 높다)는 실제와 같다.
// 쓰는 CSS 클래스는 iso_buildings.js와 같다(iso-face, iso-l, iso-r, iso-t, iso-w, iso-fl, iso-df, iso-dk, iso-d, iso-lv, iso-fline, iso-flag). 국기는 flags/us.svg.
// 연결(iso.js drawObj 안): else if (kind === 'us4') { const c = usRegulators(cx, cy, flagFile); el.push(...c.el); ps.push(...c.poly); }
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
// [lo, hi]를 n칸으로 나눠 칸마다 가운데에 폭 w(칸 폭의 비율)짜리 구간을 돌려준다
const cells = (lo, hi, n, w) => Array.from({ length: n }, (_, i) => { const p = (hi - lo) / n, c = lo + (i + .5) * p; return [c - p * w / 2, c + p * w / 2]; });

// 바닥판과 건물 배치(그룹 바닥 좌표 px, 배율 1). m: 건물 배율(px/m), x y: 건물 바닥 가운데, hx hy: 바닥 반폭(m)
// 뒤쪽(x + y가 작은 쪽)에서 앞쪽으로 그린다. 가장 높은 OCC가 뒤, 가장 낮은 연준이 앞이고, FDIC와 NCUA는 양옆이라 서로 가리지 않는다
const PLATE = 3, RIM = 3;
const BLD = {
  occ: { m: .37, x: -29, y: -23, hx: 73, hy: 73 },
  ncua: { m: .44, x: 41.4, y: -32.2, hx: 27, hy: 40.5 },
  fdic: { m: .48, x: -39.5, y: 31, hx: 34.5, hy: 28.75 },
  eccles: { m: .58, x: 31, y: 29, hx: 52.5, hy: 37.4 },
};

// 건물 하나를 그리는 연장 묶음. 길이는 미터이고, 배율 m과 놓을 자리(ox, oy)를 곱해 화면 좌표로 바꾼다. zb는 건물이 선 높이(바닥판 윗면, px)
function kit(g, m, ox, oy, zb) {
  const { cx, cy, k, el, ps } = g;
  const P = (x, y, z) => { const X = ox + x * m, Y = oy + y * m; return [cx + (X - Y) * C30 * k, cy + ((X + Y) * .5 - zb - z * m) * k]; };
  const face = (c, a) => { ps.push(...a); el.push(`<polygon class="iso-face ${c}" points="${pts(a)}"/>`); };
  const fls = (c, qs) => { if (qs.length) el.push(`<path class="iso-fl ${c}" d="${qs.map((q) => `M${q.map(([x, y]) => `${f(x)} ${f(y)}`).join('L')}Z`).join('')}"/>`); };
  const path = (c, segs) => { if (segs.length) el.push(`<path class="${c}" d="${segs.map((s) => `M${s.map(([x, y]) => `${f(x)} ${f(y)}`).join('L')}`).join('')}"/>`); };
  const ln = (a) => el.push(`<polyline class="iso-d iso-dn" points="${pts(a)}"/>`);
  // 가로 x0~x1, 세로 y0~y1, 높이 z0~z1 상자. 왼쪽 면은 y1, 오른쪽 면은 x1, 윗면은 z1
  const box = (x0, x1, y0, y1, z0, z1, c = {}) => {
    face(c.l ?? 'iso-l', [P(x0, y1, z1), P(x1, y1, z1), P(x1, y1, z0), P(x0, y1, z0)]);
    face(c.r ?? 'iso-r', [P(x1, y1, z1), P(x1, y0, z1), P(x1, y0, z0), P(x1, y1, z0)]);
    face(c.t ?? 'iso-t', [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]);
  };
  // 면 위에 그리는 연장: 왼쪽 면(y 고정)과 오른쪽 면(x 고정). q(u0, u1, z0, z1)는 면 위의 네모, p(u, z)는 면 위의 점
  const sideL = (y) => ({ q: (u0, u1, z0, z1) => [P(u0, y, z1), P(u1, y, z1), P(u1, y, z0), P(u0, y, z0)], p: (u, z) => P(u, y, z) });
  const sideR = (x) => ({ q: (u0, u1, z0, z1) => [P(x, u1, z1), P(x, u0, z1), P(x, u0, z0), P(x, u1, z0)], p: (u, z) => P(x, u, z) });
  // 윗면에 국기를 눕혀 붙인다(세로 fh를 안 주면 4:3). 국기 가로는 x 방향, 위쪽이 오른쪽 위를 향한다
  const flag = (file, xc, yc, z, fw, fh = fw * .75) => {
    if (!file) return;
    const o = P(xc - fw / 2, yc - fh / 2, z), u = [P(xc + fw / 2, yc - fh / 2, z), P(xc - fw / 2, yc + fh / 2, z)];
    const m3 = [(u[0][0] - o[0]) / 640, (u[0][1] - o[1]) / 640, (u[1][0] - o[0]) / 480, (u[1][1] - o[1]) / 480];
    el.push(`<image class="iso-flag" href="flags/${file}.svg" x="0" y="0" width="640" height="480" preserveAspectRatio="none" transform="matrix(${m3.map(g5)},${f(o[0])},${f(o[1])})"/>`);
    ln([o, u[0], P(xc + fw / 2, yc + fh / 2, z), u[1], o]);
  };
  return { P, face, fls, path, box, sideL, sideR, flag };
}

// OCC Constitution Center(Edward Durell Stone 1969, 2009년 유리 외벽으로 고침. 한 블록 146 x 146m, 10층 42.7m). 사진: Tim1965 2011, Flickr 2024
// 둘레는 세로 살이 촘촘한 유리 벽이고, 밑에 회색 띠(2층), 위 두 층은 안으로 물러난 짙은 유리, 맨 위에 두꺼운 흰 지붕판이 얹힌다.
// 네 모서리에 흰 돌 기둥(탑)이 지붕판 위로 솟고, 앞 모서리는 두 기둥 사이가 ㄱ자로 파여 있다(사진 정면의 V 홈).
// 기둥 폭 22m(양쪽 벽 끝 기둥 한 면은 14m), 홈 8m, 지붕판 위로 솟은 높이 5.7m는 사진에서 쟀다. 안뜰은 밖에서 안 보여 그리지 않는다
function occ(t, flag) {
  const { P, face, fls, path, box, sideL, sideR, flag: put } = t;
  const A = 73, c = 22, s = 8, e = A - s, Hb = 37, Hc = 42.7, zb = 8.5, zr = 31, zp = 35.5, W = { l: 'iso-st-l', r: 'iso-st-r' }, L = sideL(A), R = sideR(A);
  face('iso-w', L.q(-A, e, 0, Hb));
  face('iso-l', R.q(-A, e, 0, Hb));
  face('iso-t', [P(-A, -A, Hb), P(A, -A, Hb), P(A, e, Hb), P(e, e, Hb), P(e, A, Hb), P(-A, A, Hb)]);
  // 두 면 같은 구성: 밑 띠(돌 회색), 유리(왼쪽 면은 흰색, 오른쪽 면은 연한 회색)와 세로 살, 물러난 짙은 띠, 지붕판 옆(흰)
  const fins = Array.from({ length: 24 }, (_, i) => -A + (i + 1) * (A + e) / 25);
  for (const S of [L, R]) {
    fls('iso-r', [S.q(-A, e, 0, zb)]);
    fls('iso-dk', cells(-A + c, e, 7, .62).map(([u0, u1]) => S.q(u0, u1, .6, zb - 1.2)));   // 바닥층 어두운 유리 칸(사이는 흰 돌 기둥)
    fls('iso-df', [S.q(-A, e, zp, Hb)]);
    fls('iso-dk', [S.q(-A, e, zr, zp)]);
    path('iso-lv', [...fins.map((u) => [S.p(u, zb), S.p(u, zr)]), [S.p(-A, zr), S.p(e, zr)]]);
    path('iso-fline', fins.map((u) => [S.p(u, zr), S.p(u, zp)]));
  }
  // 지붕판 처마: 유리 벽 밖으로 o만큼 나온다(기둥 사이 구간만). 앞 두 면은 옆면까지, 뒤 두 면은 윗면만 보인다
  const o = 8, K = { l: 'iso-dk', r: 'iso-dk', t: 'iso-r' };   // 얇고 짙은 회색 판이 깊게 나온다
  box(-A + c, A - c, A, A + o, zp, Hb, K);
  box(A, A + o, -A + c, A - c, zp, Hb, K);
  face('iso-r', [P(-A + c, -A - o, Hb), P(A - c, -A - o, Hb), P(A - c, -A, Hb), P(-A + c, -A, Hb)]);
  face('iso-r', [P(-A - o, -A + c, Hb), P(-A, -A + c, Hb), P(-A, A - c, Hb), P(-A - o, A - c, Hb)]);
  put(flag, 0, 0, Hb, 2 * (A - c), 2 * (A - c));   // 두 탑 사이 지붕 판 정사각형을 꽉 채운다
  // 뒤, 왼쪽, 오른쪽 모서리: 지붕판 위로 솟는 탑. 벽 쪽은 흰 기둥 띠
  box(-A, -A + c, -A, -A + c, Hb, Hc, W);
  box(-A, -A + c, A - c, A, Hb, Hc, W);
  fls('iso-st-l', [L.q(-A, -A + c, 0, Hb)]);
  box(A - c, A, -A, -A + c, Hb, Hc, W);
  fls('iso-st-r', [R.q(-A, -A + c, 0, Hb)]);
  // 앞 모서리: ㄱ자 기둥(뿌리부터 꼭대기까지). 두 기둥 사이 s x s가 홈이고 안쪽 두 벽이 보인다
  box(A - c, e, A - c, A, 0, Hc, W);
  box(e, A, A - c, e, 0, Hc, W);
  // 탑 패널 이음선: 3.5m마다 가로선(사진에서 보이는 패널 줄눈)
  const joints = (S, u0, u1) => path('iso-fline iso-fline-d', Array.from({ length: 12 }, (_, i) => [S.p(u0, 3.5 * (i + 1)), S.p(u1, 3.5 * (i + 1))]));
  joints(L, -A, -A + c); joints(R, -A, -A + c); joints(L, A - c, e); joints(R, A - c, e);
}

// FDIC 본부 550 17th St NW(윤곽 69 x 57.5m, 7층 27.4m). 사진: Commons Federal Deposit Insurance Corporation Headquarters (53844538271), FDIC Headquarters(PD)
// 연회색 석재 벽에 좁은 세로 창이 층마다 줄지어 서고(긴 면 42칸, 짧은 면 35칸), 창 3개가 한 묶음(칸 14개)이다. 밑은 기둥만 선 열린 1층(밑이 어둡다),
// 맨 위는 안으로 들어간 어두운 상자 칸 14개(긴 면)와 이어진 어두운 띠(짧은 면). 창 3개 묶음을 한 칸 창으로 줄여 그렸다
function fdic(t) {
  const { fls, path, box, sideL, sideR } = t;
  const a = 34.5, b = 28.75, H = 27.4, zg = 5.2, zt = 23.2, fl = 3.6;
  box(-a, a, -b, b, 0, H);
  const L = sideL(b), R = sideR(a);
  const rows = (S, lo, hi, n) => {
    const w = [];
    for (let j = 0; j < 5; j++) for (const [u0, u1] of cells(lo, hi, n, .44)) w.push(S.q(u0, u1, zg + j * fl + .7, zg + j * fl + 3.3));
    fls('iso-dk', w);
  };
  rows(L, -a, a, 14);
  rows(R, -b, b, 12);
  // 윗부분: 어두운 띠 + 밝은 칸막이
  const top = (S, lo, hi, n) => {
    fls('iso-dk', [S.q(lo + 1, hi - 1, zt + .5, H - .5)]);
    fls('iso-df', Array.from({ length: n + 1 }, (_, i) => { const u = lo + 1 + i * (hi - lo - 2) / n; return S.q(u - .7, u + .7, zt + .5, H - .5); }));
  };
  top(L, -a, a, 14);
  top(R, -b, b, 12);
  // 열린 1층(긴 면): 어두운 안쪽에 기둥
  fls('iso-dk', [L.q(-a + 1, a - 6, .3, zg - .3)]);
  fls('iso-df', Array.from({ length: 11 }, (_, i) => { const u = -a + 1 + i * (a - 6 + a - 1) / 10; return L.q(u - 1.2, u + 1.2, 0, zg); }));
}

// 연준 이사회 Marriner S. Eccles Building(Paul Cret 1937, 흰 대리석, 윤곽 105 x 74.7m). 사진: Commons 정면 사진 여럿(Flickr 2011, 2008, HDR 2012), 1937년 항공 사진
// 평면은 남북 두 동을 가운데 몸통이 잇는 공(工)자(DC GIS 건물 윤곽)이고 동서에 안뜰이 열려 있다. 남쪽 정면: 가운데 현관(네모 기둥 넷, 사이에 키 큰 어두운 창 셋)과 그 뒤로 솟은 위층,
// 양옆 날개에 키 큰 어두운 창 9개씩과 그 위 작은 창 한 줄. 높이는 가운데 몸통 25.9m(OSM 높이 25.908m)이고 날개 17.9m, 북쪽 동 21m는 사진의 창 간격(3.9m)에서 쟀다
function eccles(t) {
  const { fls, path, box, sideL, sideR } = t;
  const a = 52.5, yb = -37.4, yn = -14.7, yw = 7.3, yf = 30, yp = 37.4, sp = 15.2, po = 11.7, Hn = 21, Hw = 17.9, Hs = 25.9, Hp = 20.7, C = { l: 'iso-w', r: 'iso-l' };
  const F = sideL(yf), E = sideR(a), G = sideL(yp);
  const tall = (S, lo, hi, n) => fls('iso-dk', cells(lo, hi, n, .5).map(([u0, u1]) => S.q(u0, u1, 2.7, 10.8)));
  const small = (S, lo, hi, n) => fls('iso-dk', cells(lo, hi, n, .36).map(([u0, u1]) => S.q(u0, u1, 13.8, 15.8)));
  // 뒤에서 앞으로 그리고, 창은 그 건물을 그린 바로 뒤에 그린다(앞 건물이 뒤 건물의 창을 덮어야 한다)
  box(-a, a, yb, yn, 0, Hn, C);       // 북쪽 동. 동쪽 끝 면의 창
  tall(E, yb, yn, 5); small(E, yb, yn, 5);
  box(-a, -sp, yw, yf, 0, Hw, C);     // 남쪽 서쪽 날개
  tall(F, -a, -sp, 9); small(F, -a, -sp, 9);
  box(-sp, sp, -20, yf, 0, Hs, C);    // 가운데 몸통
  box(sp, a, yw, yf, 0, Hw, C);       // 남쪽 동쪽 날개. 앞면과 동쪽 끝 면의 창
  tall(F, sp, a, 9); small(F, sp, a, 9);
  tall(E, yw, yf, 5); small(E, yw, yf, 5);
  box(-sp + 1.5, sp - 1.5, -20 + 1.5, yf - 1.5, Hs, Hs + 2, C);   // 가운데 몸통 맨 위의 한 단 들어간 처마 단(평평한 윗면)
  box(-po, po, yf, yp, 0, Hp, C);     // 현관: 네모 기둥 넷 사이의 키 큰 창 셋, 위에 처마 띠
  fls('iso-dk', [[-6.85, -3.75], [-1.55, 1.55], [3.75, 6.85]].map(([u0, u1]) => G.q(u0, u1, 2.7, 15.5)));
  path('iso-lv', [[G.p(-po, 17), G.p(po, 17)]]);
}

// NCUA 본부 1775 Duke St, Alexandria(지상 7층 28m, 윤곽 약 54 x 81m). 사진: Bing 이미지 검색의 NCUA 본부 외관 사진 여러 장, Google 지도 위성 사진(참고만, 사이트에 넣지 않음)
// 베이지색 석재 벽에 네모 창이 층마다 촘촘히 줄지은 7층 건물이다. 1층은 석재 띠(창 없음), 맨 위층 위에 처마 띠, 지붕 가운데에 낮은 기계실이 앉는다.
// 평면은 긴 몸통 하나에 짧은 날개가 ㄱ자로 붙고, 날개 끝 모서리는 둥글게 돌아간다(사진의 원통 모서리). 둥근 모서리는 면 셋으로 근사했다
function ncua(t) {
  const { P, face, fls, path, box } = t, H = 28, fl = 4, C = { l: 'iso-w', r: 'iso-l' };
  box(-27, 0, -40.5, 40.5, 0, H, C);                                  // 긴 몸통
  const xa = 27, ya = 14, yb = 40.5, rc = 12;                          // 날개: x 0~27, y 14~40.5, 앞 모서리를 rc만큼 깎는다
  const poly = [[0, yb], [xa - rc, yb], [xa - rc * .3, yb - rc * .3], [xa, yb - rc], [xa, ya], [0, ya]];
  const top = poly.map(([x, y]) => P(x, y, H));
  for (let i = 0; i < 3; i++) { const [p, q] = [poly[i], poly[i + 1]]; face(i == 2 ? 'iso-l' : 'iso-w', [P(p[0], p[1], H), P(q[0], q[1], H), P(q[0], q[1], 0), P(p[0], p[1], 0)]); }
  face('iso-l', [P(xa, poly[3][1], H), P(xa, ya, H), P(xa, ya, 0), P(xa, poly[3][1], 0)]);
  face('iso-t', top);
  // 창: 면 위 두 점 사이를 n칸으로 나눠 층마다 네모 창
  const win = (a, b, n) => {
    const w = [];
    for (let j = 1; j < 7; j++) for (let i = 0; i < n; i++) {
      const u0 = (i + .22) / n, u1 = (i + .78) / n, z0 = j * fl + .8, z1 = j * fl + 3.1, X = (u) => a[0] + (b[0] - a[0]) * u, Y = (u) => a[1] + (b[1] - a[1]) * u;
      w.push([P(X(u0), Y(u0), z1), P(X(u1), Y(u1), z1), P(X(u1), Y(u1), z0), P(X(u0), Y(u0), z0)]);
    }
    fls('iso-dk', w);
    path('iso-fline iso-fline-d', [[P(a[0], a[1], fl), P(b[0], b[1], fl)], [P(a[0], a[1], H - .6), P(b[0], b[1], H - .6)]]);
  };
  win([-27, yb], [0, yb], 9);               // 몸통 앞(왼쪽) 면
  win([0, -40.5], [0, ya], 18);             // 몸통 긴 면(오른쪽)
  win(poly[0], poly[1], 5); win(poly[1], poly[2], 2); win(poly[2], poly[3], 2); win(poly[3], poly[4], 4);  // 날개 앞면, 둥근 모서리, 끝 면
  box(-21, -6, -24, 8, H, H + 4, C);        // 지붕 기계실
}

export function usRegulators(cx, cy, opt) {
  const k = +opt?.k || 1, flag = typeof opt === 'string' ? opt : opt?.flag === undefined ? 'us' : opt.flag;
  const el = [], ps = [], g = { cx, cy, k, el, ps }, draw = { occ, ncua, fdic, eccles };
  // 바닥판: 건물 바닥 전부를 RIM만큼 두르는 네모. 바닥판 안 건물은 PLATE 높이에서 선다
  const xs = Object.values(BLD).flatMap((b) => [b.x - b.hx * b.m, b.x + b.hx * b.m]), ys = Object.values(BLD).flatMap((b) => [b.y - b.hy * b.m, b.y + b.hy * b.m]);
  const x0 = Math.min(...xs) - RIM, x1 = Math.max(...xs) + RIM, y0 = Math.min(...ys) - RIM, y1 = Math.max(...ys) + RIM, p = kit(g, 1, 0, 0, 0);
  p.face('iso-l', p.sideL(y1).q(x0, x1, 0, PLATE));
  p.face('iso-r', p.sideR(x1).q(y0, y1, 0, PLATE));
  p.face('iso-t', [p.P(x0, y0, PLATE), p.P(x1, y0, PLATE), p.P(x1, y1, PLATE), p.P(x0, y1, PLATE)]);
  for (const [id, b] of Object.entries(BLD)) draw[id](kit(g, b.m, b.x, b.y, PLATE), flag);
  return { el, ps, poly: hull(ps) };
}
