// EU 일반(eu-emt) 감독 블록: 홈 회원국 감독기관(NCA) 가운데 승인된 EMT 발행사가 가장 많은 다섯 곳의 본부 건물을 한 바닥판 위에 모아 그린다.
// ESMA 임시 MiCA 등록부 EMT 발행사 파일(2026-09-30 갱신, 2026-10-05 읽음) 기준으로 프랑스 ACPR(6곳), 룩셈부르크 CSSF(3), 네덜란드 DNB(3), 리투아니아 Bank of Lithuania(2), 몰타 MFSA(2)다.
// 건물마다 사진에서 잰 덩어리, 비율, 창과 기둥의 짜임을 베끼고, 사진으로 자리를 정할 수 없는 부분(안뜰, 옥상 설비)은 그리지 않는다. 지붕은 모두 평평한 면이고 그 위에 EU 국기(flags/eu.svg)를 지붕 면 크기에 맞춰 꽉 채워 눕혀 붙인다(4:3이 아닌 지붕은 늘어난다). 회원국 국기는 쓰지 않는다.
// iso_buildings.js 건물과 같은 약속으로 그린다: (cx, cy, opt) -> { el, ps, poly }.
//   el: SVG 조각 문자열 목록(<g>는 쓰지 않는다), ps: 바깥 윤곽(iso-face) 꼭짓점 목록, poly: ps를 감싸는 볼록 윤곽(이름표 자리 잡기와 겹침 검사에 쓴다)
//   (cx, cy)는 바닥판 가운데가 화면에서 놓일 자리. opt.k는 크기 배율(기본 1). 건물 쪽 약속의 세 번째 인자(국기 파일 이름)가 오면 무시한다.
//   시험용: opt.only('acpr', 'dnb', 'cssf', 'bol', 'mfsa')면 바닥판 없이 그 건물만 바닥 가운데에 그린다.
// 입체 좌표 (x, y, z)는 iso.js와 같다: x는 오른쪽 아래, y는 왼쪽 아래로 가는 바닥 길이, z는 위로 가는 높이. 건물 안 좌표는 미터이고, 건물마다 1m가 화면의 s px가 되게 따로 줄여 그린다(실제 크기 차이가 커서 한 배율로는 작은 건물의 창이 안 보인다).
// 쓰는 CSS 클래스는 iso_buildings.js와 같다(iso-face, iso-l, iso-r, iso-t, iso-w, iso-fl, iso-dk, iso-df, iso-d). 기와, 화강암, 짙은 석재처럼 한 단계 더 어두운 면은 클래스 대신 style로 --muted와 --ink를 채운다(다른 클래스의 색이 바뀌어도 영향이 없게).
const C30 = Math.sqrt(3) / 2;
const f = (n) => Math.round(n * 20) / 20;
const g5 = (n) => Math.round(n * 1e5) / 1e5;
const pts = (a) => a.map(([x, y]) => `${f(x)},${f(y)}`).join(' ');
// iso.js의 hull과 같다(모듈 하나로 쓰려고 옮김)
const hull = (a) => {
  const q = [...a].sort((m, n) => m[0] - n[0] || m[1] - n[1]), cr = (o, m, n) => (m[0] - o[0]) * (n[1] - o[1]) - (m[1] - o[1]) * (n[0] - o[0]);
  const half = (s) => { const r = []; for (const t of s) { while (r.length > 1 && cr(r[r.length - 2], r[r.length - 1], t) <= 0) r.pop(); r.push(t); } r.pop(); return r; };
  return [...half(q), ...half([...q].reverse())];
};

const MUT = 'fill:var(--muted)', INK = 'fill:var(--ink)', INK2 = 'fill:var(--ink-2)', STONE = 'fill:var(--stone)';
const PLATE = 3;                               // 바닥판 두께(px)
const PW = 112, PD = 110;                      // 바닥판 가로(x), 세로(y)(px). 보통 블록 한 변(64.7)의 약 1.6배
// 건물마다 [바닥 가운데 x, y(바닥판 가운데 기준 px), 배율 s(1m가 몇 px)]. 그리는 차례는 뒤(x + y가 작은 쪽)에서 앞이다. 키가 가장 큰 DNB가 맨 뒤다
const LAYOUT = { dnb: [-26.4, -26.6, .33], acpr: [25.5, -36.1, .46], bol: [12, 40, .56], cssf: [33, 6, .55], mfsa: [-36, 29, .8] };

export function euNcaGroup(cx, cy, opt) {
  const k = +opt?.k || 1, only = opt?.only;
  const P = (x, y, z) => [cx + (x - y) * C30 * k, cy + ((x + y) * .5 - z) * k];
  const el = [], ps = [];
  const sty = (st) => st ? ` style="${st}"` : '';
  const face = (c, a, st) => { ps.push(...a); el.push(`<polygon class="iso-face ${c}"${sty(st)} points="${pts(a)}"/>`); };
  const fl = (c, a, st) => el.push(`<polygon class="iso-fl ${c}"${sty(st)} points="${pts(a)}"/>`);
  const ln = (a, c = '') => el.push(`<polyline class="iso-d iso-dn ${c}" points="${pts(a)}"/>`);
  // 같은 색의 네모 여럿(창 줄)을 경로 하나로. 꼭짓점은 첫 점에서 상대 좌표로 적는다
  const quads = (c, list, st) => el.push(`<path class="iso-fl ${c}"${sty(st)} d="${list.map((a) => `M${f(a[0][0])} ${f(a[0][1])}${a.slice(1).map((q, i) => `l${f(q[0] - a[i][0])} ${f(q[1] - a[i][1])}`).join('')}z`).join('')}"/>`);

  // 건물 하나를 그리는 연장 묶음. (ox, oy)는 건물 바닥 가운데가 바닥판 위에 놓일 자리(px), s는 1m가 몇 px인지
  const kit = ([ox, oy, s]) => {
    const Q = (x, y, z) => P(ox + x * s, oy + y * s, PLATE + z * s);
    // 가로 x0~x1, 세로 y0~y1, 높이 z0~z1 상자. 왼쪽 면은 y1, 오른쪽 면은 x1, 윗면은 z1
    const box = (x0, x1, y0, y1, z0, z1, c = {}) => {
      face(c.l ?? 'iso-l', [Q(x0, y1, z1), Q(x1, y1, z1), Q(x1, y1, z0), Q(x0, y1, z0)], c.ls);
      face(c.r ?? 'iso-r', [Q(x1, y1, z1), Q(x1, y0, z1), Q(x1, y0, z0), Q(x1, y1, z0)], c.rs);
      if (c.t !== 0) face(c.t ?? 'iso-t', [Q(x0, y0, z1), Q(x1, y0, z1), Q(x1, y1, z1), Q(x0, y1, z1)]);
    };
    const qL = (y, x0, x1, z0, z1) => [Q(x0, y, z1), Q(x1, y, z1), Q(x1, y, z0), Q(x0, y, z0)];   // 왼쪽 면 위의 네모
    const qR = (x, y0, y1, z0, z1) => [Q(x, y1, z1), Q(x, y0, z1), Q(x, y0, z0), Q(x, y1, z0)];   // 오른쪽 면 위의 네모
    // 윗면 EU 국기: 가로 fw(m), 세로 fh(기본 .75 fw, 지붕 모양에 맞춰 늘린다). 가로가 x 방향이고 위쪽이 오른쪽 위를 향한다
    const flag = (xc, yc, z, fw, fh = fw * .75) => {
      const O = Q(xc - fw / 2, yc - fh / 2, z), U = Q(xc + fw / 2, yc - fh / 2, z), V = Q(xc - fw / 2, yc + fh / 2, z);
      const m = [(U[0] - O[0]) / 640, (U[1] - O[1]) / 640, (V[0] - O[0]) / 480, (V[1] - O[1]) / 480];
      el.push(`<image class="iso-flag" href="flags/eu.svg" x="0" y="0" width="640" height="480" preserveAspectRatio="none" transform="matrix(${m.map(g5)},${f(O[0])},${f(O[1])})"/>`);
      ln([Q(xc - fw / 2, yc - fh / 2, z), Q(xc + fw / 2, yc - fh / 2, z), Q(xc + fw / 2, yc + fh / 2, z), Q(xc - fw / 2, yc + fh / 2, z), Q(xc - fw / 2, yc - fh / 2, z)]);
    };
    // 다각형 기둥의 벽: 앞(+x, +y)을 보는 벽만 뒤에서 앞으로 그린다. deco(e)는 벽마다 창과 띠를 얹는 함수
    const walls = (poly, z0, z1, deco) => {
      const sg = poly.reduce((a, p, i) => { const q = poly[(i + 1) % poly.length]; return a + p[0] * q[1] - q[0] * p[1]; }, 0) > 0 ? 1 : -1;
      poly.map((p, i) => { const q = poly[(i + 1) % poly.length], dx = q[0] - p[0], dy = q[1] - p[1], n = Math.hypot(dx, dy); return { p, q, nx: sg * dy / n, ny: -sg * dx / n, d: p[0] + q[0] + p[1] + q[1] }; })
        .filter((e) => e.nx + e.ny > 1e-6).sort((a, b) => a.d - b.d)
        .forEach((e) => { face(e.nx > e.ny ? 'iso-r' : 'iso-l', [Q(e.p[0], e.p[1], z1), Q(e.q[0], e.q[1], z1), Q(e.q[0], e.q[1], z0), Q(e.p[0], e.p[1], z0)]); deco?.(e); });
    };
    const band = (e, za, zb, c, st) => fl(c, [Q(e.p[0], e.p[1], zb), Q(e.q[0], e.q[1], zb), Q(e.q[0], e.q[1], za), Q(e.p[0], e.p[1], za)], st);   // 벽 하나를 따라가는 가로 띠
    return { Q, box, qL, qR, flag, walls, band };
  };

  // 바닥판
  const X0 = -PW / 2, X1 = PW / 2, Y0 = -PD / 2, Y1 = PD / 2;
  if (!only) {
    face('iso-l', [P(X0, Y1, PLATE), P(X1, Y1, PLATE), P(X1, Y1, 0), P(X0, Y1, 0)]);
    face('iso-r', [P(X1, Y1, PLATE), P(X1, Y0, PLATE), P(X1, Y0, 0), P(X1, Y1, 0)]);
    face('iso-t', [P(X0, Y0, PLATE), P(X1, Y0, PLATE), P(X1, Y1, PLATE), P(X0, Y1, PLATE)]);
  }

  const B = {
    // DNB(암스테르담 Frederiksplein 61): 1968년 Duintjer 설계, 2025년 개수. 3층 받침(바닥층 기둥, 기와 띠, 덧창 두 층, 흰 띠)과 그 위 15층 기와 탑
    // 평면은 OpenStreetMap(BAG) 윤곽 110 x 123m, 탑 45 x 18.5m와 높이 71.8m(건물 부분 height)는 OSM에서 쟀고, 받침 높이 17m는 3층에서 어림했다. 탑은 받침 위로 창 줄 12층이 보이고, 긴 면은 작은 창, 짧은 면은 이어진 유리 띠
    dnb(K) {
      const { box, qL, qR, flag } = K, ZP = 17, ZT = 71.8, rows = 12, rp = (ZT - ZP) / rows, TY0 = -26.2, TY1 = -7.7, TX0 = -12, TX1 = 33;
      // 바닥층은 4m 물러선 어두운 유리벽과 기둥이고(사진: 위층이 내밀어 그늘이 진다), 그 위 위층 받침이 사방으로 4m 내민다
      box(-51, 51, -57.3, 57.4, 0, 5, { l: 'iso-dk', r: 'iso-dk', t: 0 });
      for (let i = 0; i < 7; i++) fl('iso-df', qL(57.4, -51 + i * 17 - .6, -51 + i * 17 + .6, 0, 5));
      for (let i = 0; i < 8; i++) fl('iso-df', qR(51, -57.3 + i * 16.4 - .6, -57.3 + i * 16.4 + .6, 0, 5));
      box(-55, 55, -61.3, 61.4, 5, ZP);
      // 위층 받침 두 면의 가로 띠: 기와 띠(muted), 덧창, 흰 띠, 덧창, 지붕 가장자리 기와 띠
      for (const q of [(a, b) => qL(61.4, -55, 55, a, b), (a, b) => qR(55, -61.3, 61.4, a, b)]) {
        fl('', q(5, 7.5), MUT); fl('iso-dk', q(7.7, 10.5)); fl('iso-dk', q(13, 16)); fl('', q(16, ZP), MUT);
      }
      flag(0, 27, ZP, 106, 66);   // 탑 앞쪽 지붕(y -6 ~ 60)을 꽉 채운다
      // 탑: 겉은 기와색(사진의 붉은 갈색을 muted와 ink-2로 옮겼다)이고 층마다 옅은 창 줄이 선다. 긴 면(왼쪽)은 작은 창 줄, 짧은 면(오른쪽)은 이어진 유리 띠
      box(TX0, TX1, TY0, TY1, ZP, ZT, { ls: MUT, rs: INK2 });
      for (let i = 0; i < rows; i++) {
        const z = ZP + i * rp;
        fl('', qL(TY1, TX0 + .6, TX1 - .6, z + rp * .1, z + rp * .45), STONE);
        fl('', qR(TX1, TY0 + .6, TY1 - .6, z + rp * .1, z + rp * .55), STONE);
      }
      // 지붕 판(처마가 사방으로 2m 나온다)과 옥상 기계실 둘
      box(TX0 - 2, TX1 + 2, TY0 - 2, TY1 + 2, ZT, ZT + 1.6, { l: 'iso-w', r: 'iso-w' });
      box(-6, 2, -24, -16, ZT + 1.6, ZT + 4);
      box(24, 28, -14, -10, ZT + 1.6, ZT + 3.6);
    },
    // ACPR(파리 4 place de Budapest, Intown 건물, 2017년 개수 설계 Béchu와 Leclercq): 6층. 바닥층은 높은 유리, 위 네 층은 유리 난간 띠, 맨 위 층은 3.5m 물러선다
    // 평면 93 x 54m와 끝의 둥근 모서리는 OpenStreetMap 윤곽에서 쟀고(긴 면이 x 방향이 되게 돌렸다), 층 높이 3.5m와 맨 위 층이 물러선 3.5m는 사진에서 어림했다
    acpr(K) {
      const { Q, walls, band, flag } = K, o = [4.1, 0];
      const A = [[-42.5, 26.8], [40.3, 26.9], [44, 26.3], [46.5, 24.4], [49.6, 20.6], [50.7, 17.5], [47.4, 9.8], [39.9, -2.4], [30.4, -23.1], [25.7, -26.9], [-40.6, -26.9], [-41.7, 13.5]].map(([x, y]) => [x - o[0], y - o[1]]);
      const Z1 = 19.4, Z2 = 22.9, up = [5.4, 8.9, 12.4, 15.9], inset = (p) => [p[0] * (86.2 / 93.2), p[1] * (46.8 / 53.8)];
      walls(A, 0, Z1, (e) => {
        band(e, .4, 5, 'iso-dk');
        for (const z of up) band(e, z + .8, z + 2.9, '', MUT);
      });
      face('iso-t', A.map((p) => Q(p[0], p[1], Z1)));
      const S = A.map(inset);
      walls(S, Z1, Z2, (e) => band(e, Z1 + .7, Z2 - .5, '', MUT));
      face('iso-t', S.map((p) => Q(p[0], p[1], Z2)));
      flag(-6, 0, Z2, 76, 46);
    },
    // CSSF(룩셈부르크 283 route d'Arlon, 2015년 JSWD 설계): 하얀 3층 몸통이 유리 현관층 위로 4m쯤 내밀어 서 있다. 몸통 겉은 가는 창 둘레마다 깊은 흰 석재 살이 서는 세로 짜임(창 간격 1.35m)이고, 현관층은 뒤로 물러선 유리벽과 흰 원기둥이다
    // 평면 72 x 44m는 OpenStreetMap 윤곽(양끝이 15도쯤 꺾인 육각형)을 직사각형으로 줄여 쟀고, 높이는 JSWD 사진의 층 줄 비율로 쟀고 층 하나 4m는 어림했다: 현관층 4.1m, 사무층 셋이 4m씩, 맨 위 띠 2.8m. 안뜰과 옥상 위 작은 층은 사진으로 자리를 정할 수 없어 그리지 않는다
    cssf(K) {
      const { box, qL, qR, flag } = K, ZF = 4.1, Z1 = ZF + 14.5, bay = 1.8;
      box(-33, 33, -19, 19, 0, ZF, { l: 'iso-dk', r: 'iso-dk', t: 0 });
      for (let i = 0; i < 7; i++) fl('iso-df', qL(22, -30 + i * 10 - .5, -30 + i * 10 + .5, 0, ZF));
      for (let i = 0; i < 5; i++) fl('iso-df', qR(36, -16 + i * 8 - .5, -16 + i * 8 + .5, 0, ZF));
      box(-36, 36, -22, 22, ZF, Z1, { l: 'iso-w', r: 'iso-w' });
      const left = [], right = [];
      for (let r = 0; r < 3; r++) {
        const za = ZF + 1.2 + r * 4, zb = za + 2.5;
        for (let x = -35.2; x < 35.4; x += bay) left.push(qL(22, x, x + .7, za, zb));
        for (let y = -21.2; y < 21.4; y += bay) right.push(qR(36, y, y + .7, za, zb));
      }
      quads('', left, MUT); quads('', right, MUT);
      flag(0, 0, Z1, 69, 42);
    },
    // Bank of Lithuania(빌뉴스 Gedimino pr. 6): 1889~1891년 Górski 설계 3층 석조. 분홍 화강암 밑단, 바닥층, 띠, 아치 창 윗층, 처마와 난간
    // 큰길 쪽 몸통 73 x 18m, 왼쪽 끝에서 뒤로 꺾인 날개 폭 24.5m(큰길에서 모두 56.5m 깊이)는 OpenStreetMap 윤곽에서 쟀고, 가운데 현관 칸은 사진에서 쟀고 높이 19.8m는 어림했다. 지붕은 구리 지붕이지만 국기를 놓으려고 난간 안쪽을 평평하게 그린다
    bol(K) {
      const { box, qL, qR, flag, Q } = K, dk = [], H = 19.8, n = 15, W0 = -36.5, W1 = 36.5, D = 18, pw = 73 / n, E0 = 2.1, E1 = 11.1;
      box(W0, -12, -38.5, 0, 0, H, { t: 0 });
      const wing = [];
      for (let i = 0; i < 7; i++) { const y = -38.5 + i * 5.5 + 1.8; wing.push(qR(-12, y, y + 1.6, 3.8, 8), [Q(-12, y + 1.6, 16.5), Q(-12, y + .8, 17.4), Q(-12, y, 16.5), Q(-12, y, 11.6), Q(-12, y + 1.6, 11.6)]); }
      quads('iso-dk', wing);                                                           // 날개의 창은 큰길 쪽 몸통보다 먼저 그려야 몸통 지붕에 가려진다
      box(W0, W1, 0, D, 0, H, { t: 0 });
      box(E0, E1, D, D + 1.2, 0, H, { t: 0 });                                         // 가운데 현관 칸이 1.2m 앞으로 나온다
      const yf = (x) => x >= E0 && x <= E1 ? D + 1.2 : D;
      // 윗층 창은 둥근 머리(사진의 아치 창): 어깨 .9m 아래에서 시작해 꼭대기가 .9m 솟는 세 점 머리
      const archL = (y, x, z0, z1) => [Q(x, y, z1 - .9), Q(x + .8, y, z1), Q(x + 1.6, y, z1 - .9), Q(x + 1.6, y, z0), Q(x, y, z0)];
      const archR = (xx, y, z0, z1) => [Q(xx, y + 1.6, z1 - .9), Q(xx, y + .8, z1), Q(xx, y, z1 - .9), Q(xx, y, z0), Q(xx, y + 1.6, z0)];
      fl('', qL(D, W0, E0, 0, 2.4), MUT); fl('', qL(D, E1, W1, 0, 2.4), MUT); fl('', qL(D + 1.2, E0, E1, 0, 2.4), MUT);
      fl('iso-df', qL(D, W0, E0, 18, H)); fl('iso-df', qL(D, E1, W1, 18, H)); fl('iso-df', qL(D + 1.2, E0, E1, 18, H));
      for (let i = 0; i < n; i++) {
        const xc = W0 + (i + .5) * pw, y = yf(xc), x = xc - .8, door = Math.abs(xc - (E0 + E1) / 2) < pw / 2;
        if (!door) dk.push(qL(y, x, x + 1.6, 3.8, 8));
        dk.push(archL(y, x, 11.6, 17.4));
      }
      dk.push(qL(D + 1.2, (E0 + E1) / 2 - 1.2, (E0 + E1) / 2 + 1.2, 2.4, 6.8)); fl('iso-df', qL(D + 1.9, (E0 + E1) / 2 - 3.4, (E0 + E1) / 2 + 3.4, 9.2, 10.2));   // 문과 발코니
      fl('', qR(W1, 0, D, 0, 2.4), MUT); fl('iso-df', qR(W1, 0, D, 18, H));
      for (let i = 0; i < 4; i++) { const y = 1.5 + i * 4.2; dk.push(qR(W1, y, y + 1.6, 3.8, 8), archR(W1, y, 11.6, 17.4)); }
      quads('iso-dk', dk);
      face('iso-t', [Q(W0, -38.5, H), Q(-12, -38.5, H), Q(-12, 0, H), Q(W1, 0, H), Q(W1, D, H), Q(E1, D, H), Q(E1, D + 1.2, H), Q(E0, D + 1.2, H), Q(E0, D, H), Q(W0, D, H)]);
      flag(0, 9, H, 70, 16);                                                           // 큰길 쪽 몸통 지붕
      flag(-24.25, -19.25, H, 22, 36);                                                 // 뒤 날개 지붕
    },
    // MFSA(몰타 Birkirkara Triq l-Imdina): V자로 좁아지는 석회암 기둥 위에 유리 한 층, 그 위에 어두운 석재로 두른 두꺼운 지붕 판이 사방으로 나온다
    // 평면 36 x 46m는 OpenStreetMap 윤곽에서 쟀고 층 높이(바닥층 5m, 첫 층 4.6m, 지붕 판 3.6m)는 사진 한 장에서 어림했다
    mfsa(K) {
      const { box, qL, qR, flag, Q } = K, vL = [-18, -6, 6, 18], vR = [-23, -11.5, 0, 11.5, 23], Z0 = 5, Z1 = 9.6, Z2 = 13.2;
      box(-18, 18, -23, 23, 0, Z1, { l: 'iso-dk', r: 'iso-dk', t: 0 });                // 바닥층 유리(기둥 뒤)
      // 첫 층: 어두운 허리 판 아래위로 유리. 기둥 칸마다 유리 한 칸
      for (let i = 0; i < 3; i++) { const a = vL[i] + 2.1, b = vL[i + 1] - 2.1; fl('iso-r', qL(23, a, b, 0, Z0)); fl('iso-dk', qL(23, a, b, Z0, Z0 + 1.5)); fl('', qL(23, a, b, Z0 + 1.5, Z1 - .4), MUT); }
      for (let i = 0; i < 4; i++) { const a = vR[i] + 2.1, b = vR[i + 1] - 2.1; fl('iso-r', qR(18, a, b, 0, Z0)); fl('iso-dk', qR(18, a, b, Z0, Z0 + 1.5)); fl('', qR(18, a, b, Z0 + 1.5, Z1 - .4), MUT); }
      // 기둥: 첫 층 기둥에서 이어져 바닥에서 뾰족하게 좁아지는 V자(석회암). 모서리 기둥은 건물 안쪽으로만 폭을 둔다
      const col = (c, lo, hi, qq) => { const a = Math.max(c - 2.1, lo), b = Math.min(c + 2.1, hi), m = (a + b) / 2, v = [qq(a, Z1), qq(b, Z1), qq(b, Z0), qq(m + .5, 0), qq(m - .5, 0), qq(a, Z0)]; fl('iso-df', v); ln([...v, v[0]]); };
      for (const x of vL) col(x, -18, 18, (u, z) => Q(u, 23.2, z));
      for (const y of vR) col(y, -23, 23, (u, z) => Q(18.2, u, z));
      box(-19.2, 19.2, -24.2, 24.2, Z1, Z2, { l: 'iso-dk', r: 'iso-dk', rs: INK });          // 어두운 석재 지붕 판이 사방으로 1.2m 나온다
      flag(0, 0, Z2, 35, 45);
    },
  };

  // 뒤(x + y가 작은 쪽)에서 앞으로
  for (const name of Object.keys(LAYOUT).sort((a, b) => LAYOUT[a][0] + LAYOUT[a][1] - LAYOUT[b][0] - LAYOUT[b][1])) if (!only || only === name) B[name](kit(only ? [0, 0, LAYOUT[name][2]] : LAYOUT[name]));
  return { el, ps, poly: hull(ps) };
}
