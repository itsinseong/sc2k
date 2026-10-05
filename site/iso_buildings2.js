// 감독 블록으로 쓰는 실제 건물 둘을 더한 모듈: 일본 금융청이 든 중앙합동청사 제7호관 서관(霞が関コモンゲート西館), EBA가 든 파리 라데팡스의 Tour Europlaza.
// iso_buildings.js와 같은 약속으로 그린다: (cx, cy, flagFile) -> { el, ps }.
//   el: SVG 조각 문자열 목록, ps: 바깥 윤곽(iso-face) 꼭짓점 목록(이름표 자리 잡기와 겹침 검사에 쓴다).
// 입체 좌표 (x, y, z): x는 오른쪽 아래, y는 왼쪽 아래로 가는 바닥 길이, z는 위로 가는 높이. 한 단위가 실제 1m이고 화면에서 1px이다.
// 왼쪽 면은 y가 큰 쪽(y1), 오른쪽 면은 x가 큰 쪽(x1)이다. 쓰는 CSS 클래스는 iso_buildings.js와 같다(iso-face, iso-l, iso-r, iso-t, iso-w, iso-fl, iso-dk, iso-dp, iso-d, iso-fline, iso-flag).
const C30 = Math.sqrt(3) / 2;
const f = (n) => Math.round(n * 10) / 10;
const g5 = (n) => Math.round(n * 1e5) / 1e5;
const pts = (a) => a.map(([x, y]) => `${f(x)},${f(y)}`).join(' ');

// 건물 하나를 그리는 연장 묶음. (cx, cy)는 바닥 가운데가 화면에서 놓일 자리. iso_buildings.js의 kit과 같고,
// 같은 칠을 한 번에 하는 fls(네모 여럿을 path 하나로)와 기울어진 면에 국기를 붙이는 flagOn을 더했다
function kit(cx, cy, flagFile) {
  const P = (x, y, z) => [cx + (x - y) * C30, cy + (x + y) * .5 - z];
  const el = [], ps = [];
  const face = (c, a, st) => { ps.push(...a); el.push(`<polygon class="iso-face ${c}"${st ? ` style="${st}"` : ''} points="${pts(a)}"/>`); };
  const fls = (c, qs) => { if (qs.length) el.push(`<path class="iso-fl ${c}" d="${qs.map((q) => `M${q.map(([x, y]) => `${f(x)} ${f(y)}`).join('L')}Z`).join('')}"/>`); };
  const ln = (a, c = '') => el.push(`<polyline class="iso-d iso-dn ${c}" points="${pts(a)}"/>`);
  const path = (c, segs) => { if (segs.length) el.push(`<path class="${c}" d="${segs.map((s) => `M${s.map(([x, y]) => `${f(x)} ${f(y)}`).join('L')}`).join('')}"/>`); };
  const qL = (y, x0, x1, z0, z1) => [P(x0, y, z1), P(x1, y, z1), P(x1, y, z0), P(x0, y, z0)];   // 왼쪽 면 위의 네모
  const qR = (x, y0, y1, z0, z1) => [P(x, y1, z1), P(x, y0, z1), P(x, y0, z0), P(x, y1, z0)];   // 오른쪽 면 위의 네모
  // 윗면 국기: iso_buildings.js의 flag와 같고, 세로 fh를 주면 지붕 모양에 맞춰 늘린다. along 'x'는 가로가 x 방향, along 'y'는 가로가 y 방향
  const flag = (xc, yc, z, fw, along = 'x', fh = fw * .75) => {
    if (!flagFile) return;
    const sx = along === 'y' ? fh : fw, sy = along === 'y' ? fw : fh;
    const o = along === 'y' ? P(xc - fh / 2, yc + fw / 2, z) : P(xc - fw / 2, yc - fh / 2, z);
    const m = along === 'y' ? [fw * C30 / 640, -fw * .5 / 640, fh * C30 / 480, fh * .5 / 480] : [fw * C30 / 640, fw * .5 / 640, -fh * C30 / 480, fh * .5 / 480];
    el.push(`<image class="iso-flag" href="flags/${flagFile}.svg" x="0" y="0" width="640" height="480" preserveAspectRatio="none" transform="matrix(${m.map(g5)},${f(o[0])},${f(o[1])})"/>`);
    const a = xc - sx / 2, b = yc - sy / 2;
    ln([P(a, b, z), P(a + sx, b, z), P(a + sx, b + sy, z), P(a, b + sy, z), P(a, b, z)]);
  };
  // 기울어진 면 위의 국기: o는 국기 왼쪽 위 모서리, w는 가로 방향, h는 아래 방향(입체 좌표 벡터, 길이가 국기의 가로와 세로)
  const flagOn = (o, w, h) => {
    if (!flagFile) return;
    const at = (a, b = [0, 0, 0], c = [0, 0, 0]) => P(a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]);
    const O = at(o), U = at(o, w), V = at(o, h), W = at(o, w, h);
    const m = [(U[0] - O[0]) / 640, (U[1] - O[1]) / 640, (V[0] - O[0]) / 480, (V[1] - O[1]) / 480];
    el.push(`<image class="iso-flag" href="flags/${flagFile}.svg" x="0" y="0" width="640" height="480" preserveAspectRatio="none" transform="matrix(${m.map(g5)},${f(O[0])},${f(O[1])})"/>`);
    ln([O, U, W, V, O]);
  };
  return { P, el, ps, face, fls, ln, path, qL, qR, flag, flagOn };
}

// 금융청이 든 중앙합동청사 제7호관 서관(지상 38층, 높이 175.78m, 평면 약 55.9m x 50.1m). 사진에서 보이는 두 면: 남남서면(왼쪽, 긴 면)과 동남동면(오른쪽)
// 남남서면: 연한 세로 기둥과 짙은 창 줄이 반반씩 번갈아 서고(칸 폭 3.4m), 가운데에 층마다 가로 띠가 있는 유리 띠(폭 11m)가 선다. 왼쪽 24m는 5m 물러나고 두 층 낮은 동이다.
//   맨 위 1.6층은 기둥 사이가 루버, 유리 띠는 맨 위까지 유리다
// 동남동면: 창 없는 연한 벽에 가는 세로 홈 다섯 줄 두 묶음이 지붕 아래 두 층에서 바닥까지 간다
// 서관 평면은 OpenStreetMap(국토지리원 지도)의 윤곽선에서 쟀고, 칸 수와 두 층 낮은 정도는 Commons 사진(Soramimi 2015, Rs1421 2012)에서 쟀다
export function fsaTower(cx, cy, flagFile) {
  const { P, el, ps, face, fls, path, qL, qR, flag } = kit(cx, cy, flagFile);
  const Wd = 55.9, Dd = 50.1, Hh = 175.78, fp = Hh / 38, ZL = 1.6 * fp;
  const x0 = -Wd / 2, x1 = Wd / 2, y0 = -Dd / 2, y1 = Dd / 2;
  const xm = x0 + 24.2, yr = y1 - 5, Hl = Hh - 2 * fp;           // 낮은 동은 x0에서 xm까지, 앞면이 yr로 물러나 있고 높이는 Hl
  const bay = 3.43, ww = 1.9, off = (bay - ww) / 2;                // 칸 폭, 창 폭(사진에서 창 줄과 기둥이 거의 반반), 칸 안에서 창 줄이 놓이는 자리
  // 창 줄들: 바닥에서 루버 아래까지 짙은 창, 그 위는 루버. 층선은 층마다 줄 묶음 전체에 한 줄(흰 기둥 위에서는 흰 선이 안 보인다). a는 창 줄 왼쪽 x 목록
  const columns = (y, a, top) => {
    const lines = [];
    for (let z = fp; z < top - ZL - 1; z += fp) lines.push([P(a[0], y, z), P(a[a.length - 1] + ww, y, z)]);
    fls('iso-dk', a.map((x) => qL(y, x, x + ww, 0, top - ZL)));
    fls('iso-dp', a.map((x) => qL(y, x, x + ww, top - ZL, top - 1.2)));
    path('iso-fline', lines);
  };
  // 낮은 동: 앞면(물러난 벽)과 윗면
  face('iso-w', [P(x0, yr, Hl), P(xm, yr, Hl), P(xm, yr, 0), P(x0, yr, 0)]);
  face('iso-t', [P(x0, y0, Hl), P(xm, y0, Hl), P(xm, yr, Hl), P(x0, yr, Hl)]);
  columns(yr, Array.from({ length: 7 }, (_, i) => x0 + (3.457 - ww) / 2 + i * 3.457), Hl);
  // 높은 동: 왼쪽 면, 오른쪽 면, 윗면
  face('iso-w', [P(xm, y1, Hh), P(x1, y1, Hh), P(x1, y1, 0), P(xm, y1, 0)]);
  face('iso-l', [P(x1, y1, Hh), P(x1, y0, Hh), P(x1, y0, 0), P(x1, y1, 0)]);
  face('iso-t', [P(xm, y0, Hh), P(x1, y0, Hh), P(x1, y1, Hh), P(xm, y1, Hh)]);
  // 왼쪽 면 가로 구성: 창 세 줄, 유리 띠, 창 세 줄
  const sa = xm + 3 * bay, sb = sa + 11.1;
  for (const x of [xm, sb]) columns(y1, [0, 1, 2].map((j) => x + off + j * bay), Hh);
  // 유리 띠: 연한 유리에 층마다 짙은 가로 띠(맨 위 루버 높이는 띠 없이 유리만)
  fls('iso-dp', [qL(y1, sa, sb, 0, Hh)]);
  fls('iso-dk', Array.from({ length: 36 }, (_, k) => qL(y1, sa, sb, k * fp, k * fp + .45 * fp)));
  // 오른쪽 면: 홈 다섯 줄 두 묶음(남남서 모서리에서 4.5m, 7.9m, ... 와 32m, 35.4m, ...)
  fls('iso-dk', [4.5, 32].flatMap((u0) => Array.from({ length: 5 }, (_, k) => { const yc = y1 - u0 - k * 3.4; return qR(x1, yc - .55, yc + .55, 0, Hh - 2.2 * fp); })));
  // 윗면 국기: 높은 동 지붕(31.7m x 50.1m)에 4:3으로, 가로가 y 방향
  flag((xm + x1) / 2, 0, Hh, Dd, 'y', x1 - xm);   // 지붕 31.7m x 50.1m를 꽉 채운다(국기 2:3에 가깝다)
  return { el, ps };
}

// EBA가 든 Tour Europlaza(31층, 몸통 높이 약 110m, 경사 지붕 꼭대기 122.66m, 마스트 끝 135.5m, 평면 약 29.2m x 32.5m). 사진에서 보이는 두 면: 왼쪽 줄무늬 면과 오른쪽 전면 유리 면
// 왼쪽 면: 양쪽 화강암 기둥 사이에 창 줄(층마다 짙은 창 띠와 화강암 띠), 가운데 넓은 화강암 기둥 둘 사이에 유리 띠(폭 10.7m). 오른쪽 면: 가는 틀의 전면 유리에 층마다 어두운 가로 띠, 양 끝에 화강암 기둥
// 지붕: 몸통 위에 한 층 높이 기계실, 그 위에 맞배지붕. 용마루에 폭 4m 틈이 길게 나 있고 틈 안에 마스트가 선다. 긴 비탈면이 오른쪽 면 위로 내려오며 국기는 이 비탈면에 붙인다
// 평면과 높이는 OpenStreetMap 지적도 윤곽과 PSS-archi 수치, 칸 수는 Commons와 위키백과 사진에서 쟀다
export function ebaTower(cx, cy, flagFile) {
  const { P, el, ps, face, fls, ln, path, qL, qR, flagOn } = kit(cx, cy, flagFile);
  const Wd = 29.2, Dd = 32.5, Hh = 110, fp = Hh / 31;
  const x0 = -Wd / 2, x1 = Wd / 2, y0 = -Dd / 2, y1 = Dd / 2;
  const GR = 'fill:var(--muted)', GL = 'fill:var(--ink-2)';   // 사진: 짙은 회색 화강암 띠와 어두운 반사 유리
  face('', [P(x0, y1, Hh), P(x1, y1, Hh), P(x1, y1, 0), P(x0, y1, 0)], GR);
  face('', [P(x1, y1, Hh), P(x1, y0, Hh), P(x1, y0, 0), P(x1, y1, 0)], GL);
  face('iso-t', [P(x0, y0, Hh), P(x1, y0, Hh), P(x1, y1, Hh), P(x0, y1, Hh)]);
  // 층마다 맨 위 .4층은 화강암 띠, 그 아래 .6층은 유리 띠(맨 위 층부터 30층)
  const zt = (k) => Hh - (k + .4) * fp, floors = Array.from({ length: 30 }, (_, k) => k);
  // 왼쪽 면: 양 끝 화강암 기둥 사이에 창 줄 칸(층마다 창 띠와 화강암 띠), 가운데 넓은 이어진 유리 칸
  fls('iso-dp', floors.flatMap((k) => [qL(y1, x0 + 1.3, x0 + 7.4, zt(k) - .6 * fp, zt(k)), qL(y1, x0 + 21.4, x1, zt(k) - .6 * fp, zt(k))]));
  fls('iso-dk', [qL(y1, x0 + 9, x0 + 19.7, fp, zt(0))]);
  path('iso-fline', floors.map((k) => [P(x0 + 9, y1, zt(k)), P(x0 + 19.7, y1, zt(k))]));
  // 오른쪽 면: 가는 틀의 전면 유리(가로 띠 없음), 양 끝 화강암 기둥
  path('iso-fline', Array.from({ length: 19 }, (_, i) => [P(x1, y0 + 1 + i * (Dd - 2) / 19, 0), P(x1, y0 + 1 + i * (Dd - 2) / 19, Hh)]));
  fls('', [qR(x1, y1 - 1, y1, 0, Hh), qR(x1, y0, y0 + 1, 0, Hh)]);
  el[el.length - 1] = el[el.length - 1].replace('class="iso-fl "', 'class="iso-fl" style="fill:var(--muted)"');
  // 지붕: 기계실(한 층), 맞배지붕
  const zp = Hh + 3, zr = 126, ya = y1 - 2, yb = y0 + 2, xa = x0 + .25 * Wd, xb = x1 - 1, xr = (xa + xb) / 2, gap = 3;
  const zs = zp + (zr - zp) * (1 - gap / (xb - xr));              // 틈 가장자리의 높이
  face('', [P(x0 + 2, ya, zp), P(xb, ya, zp), P(xb, ya, Hh), P(x0 + 2, ya, Hh)], GR);
  face('', [P(xb, ya, zp), P(xb, yb, zp), P(xb, yb, Hh), P(xb, ya, Hh)], GL);
  face('iso-t', [P(x0 + 2, yb, zp), P(xb, yb, zp), P(xb, ya, zp), P(x0 + 2, ya, zp)]);
  fls('iso-dk', [qR(xr - gap, yb, ya, zp, zs)]);                   // 틈 안쪽 벽
  face('', [P(xb, ya, zp), P(xb, yb, zp), P(xr + gap, yb, zs), P(xr + gap, ya, zs)], GL);   // 보이는 비탈면
  // 비탈면 국기: 비탈면 전체(길이 x 깊이)를 꽉 채운다
  const ls = Math.hypot(xb - xr - gap, zs - zp), fh = ls, fw = ya - yb, d = [(xb - xr - gap) / ls, 0, -(zs - zp) / ls];
  flagOn([xr + gap, (ya + yb) / 2 + fw / 2, zs], [0, -fw, 0], [d[0] * fh, 0, d[2] * fh]);
  // 앞 박공(틈 양옆 두 쪽)과 틈
  face('', [P(xa, ya, zp), P(xr - gap, ya, zp), P(xr - gap, ya, zs)], GR);
  face('', [P(xr + gap, ya, zp), P(xb, ya, zp), P(xr + gap, ya, zs)], GR);
  fls('iso-dk', [qL(ya, xr - gap, xr + gap, zp, zs)]);
  // 마스트
  const tip = P(xr, (ya + yb) / 2, 135.5);
  ln([P(xr, (ya + yb) / 2, zs), tip]);
  ps.push(tip);
  return { el, ps };
}

// kind 이름으로 찾아 쓰는 표(iso.js의 BUILDING 값)
export const BUILDINGS2 = { fsa: fsaTower, eba: ebaTower };
