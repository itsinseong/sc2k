// 지구본: TopoJSON 직접 해석 + 정사영 투영 + 대원 호. 외부 라이브러리 없음.
const SEOUL = [126.98, 37.57];
const ANCHORS = { us: [-77.04, 38.91], eu: [4.35, 50.85], hk: [114.17, 22.32], sg: [103.82, 1.35], jp: [139.69, 35.69] };
const EU_IDS = '040 056 100 191 196 203 208 233 246 250 276 300 348 372 380 428 440 442 470 528 616 620 642 703 705 724 752'.split(' ');
const FY = 0.34; // 나라를 둘 높이 비율(위쪽). 아래 점수 글에 가리지 않게
const CFG = { // pin = 표시할 점, ids = 칠할 나라, view = 시점 중심, k = 구 반지름 / 상자 너비(클수록 확대), top = 있으면 구의 윗 테두리를 상자 안에 두고 나라를 상자 높이의 이 비율 자리에 둠
  us: { name: '미국', pin: ANCHORS.us, ids: ['840'], label: '미국', view: [-98, 40], k: 0.75, top: FY },
  'eu-emt': { name: 'EU', pin: ANCHORS.eu, ids: EU_IDS, label: 'EU', view: [11, 51], k: 1.0, top: FY },
  'eu-emt-significant': { name: 'EU', pin: ANCHORS.eu, ids: EU_IDS, label: 'EU', view: [11, 51], k: 1.0, top: FY },
  hk: { name: '홍콩', pin: ANCHORS.hk, ids: ['344'], dot: true, label: '홍콩', view: [114.1, 22.35], k: 18, det: 'hk' },
  sg: { name: '싱가포르', pin: ANCHORS.sg, ids: ['702'], dot: true, label: '싱가포르', view: [103.82, 1.35], k: 20, det: 'sg' },
  jp: { name: '일본', pin: ANCHORS.jp, ids: ['392'], label: '일본', view: [137.5, 37.5], k: 1.9, det: 'kr' },
  'kr-v1': { name: '한국', pin: SEOUL, ids: ['410'], label: '한국', view: [127.5, 36], k: 3.0, det: 'kr' },
};
const T_TWEEN = 1.1, T_PULSE = 2.4, TM = 6; // TM: 윗 테두리 여백
const RAD = Math.PI / 180;

const S = { world: null, loading: null, rot: null, id: null, detail: null, detailLoading: null }; // 모듈 상태: 해석된 지도, 마지막 회전, 마지막 id, 확대용 1:10m 지도(지역별)

// ---- TopoJSON 해석 ----
const vec = (lon, lat) => { const a = lon * RAD, b = lat * RAD, c = Math.cos(b); return [c * Math.cos(a), c * Math.sin(a), Math.sin(b)]; };
function densify(ring) { // 경도, 위도 고리를 약 2도 간격 3차원 점으로 쪼갬. seam=경계선이 아닌 자름선(180도, 남극)
  const xyz = [], seam = [];
  const v = ring.map(p => vec(p[0], p[1]));
  for (let i = 0; i < ring.length; i++) {
    const a = v[i], b = v[(i + 1) % ring.length], pa = ring[i], pb = ring[(i + 1) % ring.length];
    const cut = (Math.abs(pa[0]) > 179.9 && Math.abs(pb[0]) > 179.9) || (pa[1] < -89.9 && pb[1] < -89.9);
    const dot = Math.max(-1, Math.min(1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]));
    const ang = Math.acos(dot), n = Math.max(1, Math.ceil(ang / (2 * RAD)));
    for (let k = 0; k < n; k++) {
      const t = k / n, s = Math.sin(ang) || 1, w1 = Math.sin((1 - t) * ang) / s, w2 = Math.sin(t * ang) / s;
      if (ang < 1e-9) xyz.push(a[0], a[1], a[2]); else xyz.push(w1 * a[0] + w2 * b[0], w1 * a[1] + w2 * b[1], w1 * a[2] + w2 * b[2]);
      seam.push(cut ? 1 : 0); // 이 점으로 들어오는 변이 아니라 이 점에서 나가는 변 기준
    }
  }
  // 변 기준을 "들어오는 변"으로 맞춤: 한 칸 뒤로 회전
  seam.unshift(seam.pop());
  const n = seam.length; let cx = 0, cy = 0, cz = 0; // 고리를 감싸는 원(중심 벡터 c, 각반경 rad): 화면 밖 고리를 건너뛰는 데 씀
  for (let i = 0; i < n; i++) { cx += xyz[3 * i]; cy += xyz[3 * i + 1]; cz += xyz[3 * i + 2]; }
  const m = Math.hypot(cx, cy, cz); let c = [1, 0, 0], rad = Math.PI;
  if (m > 1e-3 * n) { c = [cx / m, cy / m, cz / m]; let mn = 1; for (let i = 0; i < n; i++) mn = Math.min(mn, c[0] * xyz[3 * i] + c[1] * xyz[3 * i + 1] + c[2] * xyz[3 * i + 2]); rad = Math.acos(Math.max(-1, mn)); }
  return { xyz: Float32Array.from(xyz), seam: Uint8Array.from(seam), n, c, rad };
}
function decode(topo) {
  const { scale, translate } = topo.transform;
  const arcs = topo.arcs.map(a => { let x = 0, y = 0; return a.map(([dx, dy]) => { x += dx; y += dy; return [x * scale[0] + translate[0], y * scale[1] + translate[1]]; }); });
  const arc = i => (i >= 0 ? arcs[i] : arcs[~i].slice().reverse());
  const ring = idxs => { const pts = []; idxs.forEach((i, k) => { const a = arc(i); pts.push(...(k ? a.slice(1) : a)); }); pts.pop(); return pts; }; // 마지막 점은 첫 점과 같음
  const out = new Map();
  for (const g of topo.objects.countries.geometries) {
    const polys = g.type === 'Polygon' ? [g.arcs] : g.type === 'MultiPolygon' ? g.arcs : [];
    out.set(String(g.id ?? g.properties.name).padStart(3, '0'), polys.flatMap(p => p.map(r => densify(ring(r)))));
  }
  return out;
}
function loadWorld() {
  S.loading ||= fetch(new URL('./data/world-50m.json', import.meta.url)).then(r => r.json()).then(t => (S.world = decode(t)));
  return S.loading;
}
// 홍콩, 싱가포르, 한국 확대용 1:10m 지도. 해당 나라 화면을 열 때만 받음. 고리는 닫는 점 없이 [경도, 위도] 목록
function loadDetail() {
  S.detailLoading ||= fetch(new URL('./data/world-detail.json', import.meta.url)).then(r => r.json()).then(d => {
    S.detail = {}; for (const [k, v] of Object.entries(d)) S.detail[k] = { bbox: v.bbox, world: new Map(Object.entries(v.countries).map(([id, rs]) => [id, rs.map(densify)])) };
  });
  return S.detailLoading;
}
// 화면 둘레(네 모서리와 변 가운데)가 모두 지역 상자 안이면 그 지역 지도를, 아니면 null(50m 사용). 한 프레임에 두 지도를 섞지 않음
function detailFor(reg, rot, R, cx, cy, W, H) {
  const D = S.detail?.[reg]; if (!D) return null;
  const [w, s, e, n] = D.bbox, lo = rot.lon * RAD, la = rot.lat * RAD, cl = Math.cos(lo), sl = Math.sin(lo), cp = Math.cos(la), sp = Math.sin(la);
  for (const [x, y] of [[0, 0], [W / 2, 0], [W, 0], [0, H / 2], [W, H / 2], [0, H], [W / 2, H], [W, H]]) {
    const sx = (x - cx) / R, sy = (cy - y) / R, d2 = 1 - sx * sx - sy * sy; if (d2 <= 0) return null; // 구 밖
    const d = Math.sqrt(d2), X = -sl * sx - sp * cl * sy + cp * cl * d, Y = cl * sx - sp * sl * sy + cp * sl * d, Z = cp * sy + sp * d;
    const gl = Math.atan2(Y, X) / RAD, gt = Math.asin(Math.max(-1, Math.min(1, Z))) / RAD;
    if (gl < w || gl > e || gt < s || gt > n) return null;
  }
  return D.world;
}

// ---- 투영 ----
function view(lon, lat, R, cx, cy, roll = 0) { // 점 (X,Y,Z) -> [px, py, 보임 여부]. roll = 화면 안에서 구를 반시계로 돌리는 각(도)
  const rc = Math.cos(roll * RAD), rs = Math.sin(roll * RAD), cl = Math.cos(lon * RAD), sl = Math.sin(lon * RAD), cp = Math.cos(lat * RAD), sp = Math.sin(lat * RAD);
  return (X, Y, Z, fold) => {
    const c = X * cl + Y * sl; let sx = Y * cl - X * sl, sy = cp * Z - sp * c; const d = sp * Z + cp * c;
    if (fold && d < 0) { const r = Math.hypot(sx, sy) || 1; sx /= r; sy /= r; } // 뒷면 점은 가장자리 위로
    if (roll) [sx, sy] = [sx * rc - sy * rs, sx * rs + sy * rc];
    return [cx + sx * R, cy - sy * R, d > 0];
  };
}
function slerp(a, b, t) {
  const dot = Math.max(-1, Math.min(1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2])), ang = Math.acos(dot), s = Math.sin(ang) || 1;
  const w1 = Math.sin((1 - t) * ang) / s, w2 = Math.sin(t * ang) / s;
  return [w1 * a[0] + w2 * b[0], w1 * a[1] + w2 * b[1], w1 * a[2] + w2 * b[2]];
}
const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const dlon = (a, b) => ((b - a + 540) % 360) - 180;

// ---- 그리기 공통 ----
function colors() {
  const cs = getComputedStyle(document.documentElement), g = n => cs.getPropertyValue(n).trim();
  return { ink: g('--ink'), ink2: g('--ink-2'), line: g('--line'), surface: g('--surface'), accent: g('--accent'), stone: g('--stone'), sans: g('--sans') };
}
// 투영 P에서 ids 나라의 채움(가장자리 접기)과 경계선(보이는 변만) 경로. g = { P, vc, cap }
function shapes(ids, g) {
  const fill = new Path2D(), edge = new Path2D(), { P, vc, cap, world = S.world } = g; // world: 쓸 지도(기본 50m)
  for (const id of ids) if (id !== '010') for (const r of world.get(id) || []) { // 남극은 접으면 원판 전체를 덮어 제외
    if (Math.acos(Math.max(-1, Math.min(1, vc[0] * r.c[0] + vc[1] * r.c[1] + vc[2] * r.c[2]))) > cap + r.rad + 0.02) continue; // 화면 밖
    let prev = null, down = false, any = false;
    for (let i = 0; i < r.n && !any; i++) any = P(r.xyz[3 * i], r.xyz[3 * i + 1], r.xyz[3 * i + 2], false)[2];
    if (!any) continue; // 뒷면에 통째로 있는 고리는 접으면 원판 전체를 덮을 수 있어 건너뜀
    for (let i = 0; i <= r.n; i++) {
      const j = i % r.n, X = r.xyz[3 * j], Y = r.xyz[3 * j + 1], Z = r.xyz[3 * j + 2];
      const [x, y] = P(X, Y, Z, true), vis = P(X, Y, Z, false)[2];
      i ? fill.lineTo(x, y) : fill.moveTo(x, y);
      if (i && vis && prev && !r.seam[j]) { if (!down) { edge.moveTo(prev[0], prev[1]); } edge.lineTo(x, y); down = true; } else down = false;
      prev = vis ? [x, y] : null;
    }
    fill.closePath();
  }
  return { fill, edge };
}
// 뒷면에만 있는 고리를 접지 않고 그대로 투영한 경로(유리처럼 비쳐 보이는 먼 쪽 땅)
function backShape(P) {
  const fill = new Path2D();
  for (const [id, rings] of S.world) if (id !== '010') for (const r of rings) {
    let any = false;
    for (let i = 0; i < r.n && !any; i++) any = P(r.xyz[3 * i], r.xyz[3 * i + 1], r.xyz[3 * i + 2], false)[2];
    if (any) continue;
    for (let i = 0; i < r.n; i++) { const [x, y] = P(r.xyz[3 * i], r.xyz[3 * i + 1], r.xyz[3 * i + 2], false); i ? fill.lineTo(x, y) : fill.moveTo(x, y); }
    fill.closePath();
  }
  return fill;
}
function graticule(ctx, P, step) {
  ctx.beginPath();
  const poly = f => { let down = false; for (let k = 0; k <= 120; k++) { const [x, y, z] = P(...f(k / 120), false); if (z) { down ? ctx.lineTo(x, y) : ctx.moveTo(x, y); down = true; } else down = false; } };
  for (let lo = -180; lo < 180; lo += step) poly(t => vec(lo, -90 + 180 * t));
  for (let la = -90 + step; la < 90; la += step) poly(t => vec(-180 + 360 * t, la));
  ctx.stroke();
}
function sizeCanvas(canvas) {
  const W = canvas.clientWidth || 440, H = canvas.clientHeight || 260, dpr = window.devicePixelRatio || 1;
  if (canvas.width !== Math.round(W * dpr) || canvas.height !== Math.round(H * dpr)) { canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr); }
  return { W, H, dpr };
}
// 가장자리 이름표: 흰 테두리를 두르고 상자 안으로 눌러 넣음
function tag(ctx, col, W, H, txt, x, y, align, color) {
  const m = ctx.measureText(txt).width;
  x = align === 'left' ? Math.min(x, W - 4 - m) : Math.max(x, 4 + m);
  if (y < 8 || y > H - 8) return;
  ctx.textAlign = align; ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.strokeText(txt, x, y); ctx.fillStyle = color || col.ink2; ctx.fillText(txt, x, y);
}

// ---- 나라 화면 지구본: 나라 하나를 크게, 끌어서 돌림. 한국으로 가는 선은 개요 화면에만 있음 ----
function draw(inst, rot, pulse) {
  const { canvas, cfg, col } = inst, ctx = canvas.getContext('2d'), { W, H, dpr } = sizeCanvas(canvas);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);
  // 나라를 상자 높이의 FY 자리(위쪽)에 둬서 아래 점수 글에 가리지 않게 함
  const R = rot.k * W, cx = W / 2, cy = cfg.top ? TM + R : FY * H;
  const lat = rot.lat, P = view(rot.lon, lat, R, cx, cy); // 윗 테두리를 보이는 구의 기울이기는 mountGlobe의 목표 시점(cfg.top)에서 한 번만 함
  const maxd = Math.max(Math.hypot(cx, cy), Math.hypot(W - cx, cy), Math.hypot(cx, H - cy), Math.hypot(W - cx, H - cy));
  const world = (cfg.det && detailFor(cfg.det, rot, R, cx, cy, W, H)) || S.world; // 화면이 확대용 지도 범위 안이면 1:10m, 아니면 50m
  const g = { P, vc: vec(rot.lon, lat), cap: maxd >= R ? Math.PI / 2 : Math.asin(maxd / R), world }; // cap: 화면이 덮는 각도, 이 밖의 고리는 건너뜀

  ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.globalAlpha = 0.3; ctx.fillStyle = col.surface; ctx.fill(); ctx.globalAlpha = 0.7;
  ctx.strokeStyle = col.line; ctx.lineWidth = 1;
  graticule(ctx, P, rot.k > 10 ? 2 : rot.k > 2.2 ? 10 : 30); ctx.globalAlpha = 1;
  const all = shapes(world.keys(), g);
  ctx.globalAlpha = 0.6; ctx.fillStyle = col.stone; ctx.fill(all.fill, 'nonzero'); ctx.globalAlpha = 1;
  ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 0.5; ctx.stroke(all.edge);
  const hl = shapes(cfg.ids, g);
  ctx.fillStyle = col.ink; ctx.fill(hl.fill, 'nonzero'); ctx.strokeStyle = '#fff'; ctx.stroke(hl.edge);
  ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.strokeStyle = col.line; ctx.lineWidth = 1; ctx.stroke();

  const [x, y, z] = P(...vec(...cfg.pin), false), onBox = z && x > -8 && x < W + 8 && y > -8 && y < H + 8;
  if (onBox) {
    ctx.beginPath(); ctx.arc(x, y, cfg.dot ? 3.5 : 2.5, 0, 7); ctx.fillStyle = cfg.dot || cfg.pin === SEOUL ? col.accent : col.ink; ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5; ctx.stroke();
    if (cfg.dot && pulse >= 0) { const f = (pulse % 0.8) / 0.8; ctx.globalAlpha = 0.55 * (1 - f); ctx.strokeStyle = col.ink; ctx.lineWidth = 1.25; ctx.beginPath(); ctx.arc(x, y, 4 + 12 * f, 0, 7); ctx.stroke(); ctx.globalAlpha = 1; }
    ctx.font = `500 11px ${col.sans}`; ctx.textBaseline = 'middle';
    // 홍콩, 싱가포르는 확대해서 칠한 땅이 점 옆으로 넓으니 이름표를 더 띄움
    const right = x < W * 0.6; const o = cfg.dot ? 30 : 7; tag(ctx, col, W, H, cfg.label, x + (right ? o : -o), y - (cfg.dot ? 0 : 8), right ? 'left' : 'right');
  }
}

const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

export function mountGlobe(el, id) {
  const cfg = CFG[id]; if (!cfg) return;
  el.textContent = '';
  const canvas = document.createElement('canvas');
  canvas.className = 'globe-canvas'; canvas.setAttribute('role', 'img');
  canvas.setAttribute('aria-label', `지구본: ${cfg.name} 위치`);
  el.append(canvas);
  const inst = { canvas, cfg, col: colors() }, to = { lon: cfg.view[0], lat: cfg.view[1], k: cfg.k };
  if (cfg.top) { // 구의 중심이 나라보다 아래에 오도록 시점을 남쪽으로 내림(중앙 자오선 위의 점은 sin(내린 각) 만큼 위로 보임)
    const W = el.clientWidth || 360, H = el.clientHeight || 330, R = cfg.k * W;
    to.lat -= Math.asin(Math.max(-1, Math.min(1, (TM + R - cfg.top * H) / R))) / RAD;
  }
  const replay = S.id !== id && !reduced();
  const from = S.rot ? { ...S.rot } : { lon: to.lon - 80, lat: 10, k: to.k * 0.6 };
  let rot = replay ? from : { ...(S.id === id && S.rot ? S.rot : to) };
  let tweening = replay, t = replay ? 0 : 99, running = false;
  S.id = id; S.rot = rot;
  const pulsing = !!cfg.dot && !reduced();

  const render = () => { const ta = t - T_TWEEN; draw(inst, rot, pulsing && ta > 0 && ta < T_PULSE ? ta : -1); };
  let prev = 0;
  const frame = (now) => {
    running = false;
    if (!el.isConnected) return;
    if (document.hidden) { document.addEventListener('visibilitychange', go, { once: true }); return; }
    t += Math.min((now - prev) / 1000, 0.05); prev = now;
    if (tweening) {
      if (t < T_TWEEN) { const e = ease(t / T_TWEEN); rot.lon = from.lon + dlon(from.lon, to.lon) * e; rot.lat = from.lat + (to.lat - from.lat) * e; rot.k = from.k * Math.pow(to.k / from.k, e); } // 확대는 로그 보간
      else { rot.lon = to.lon; rot.lat = to.lat; rot.k = to.k; tweening = false; }
    }
    render();
    if (t < T_TWEEN + (pulsing ? T_PULSE : 0)) go();
  };
  function go() { if (running) return; running = true; requestAnimationFrame(n => { prev = n; requestAnimationFrame(frame); }); }

  // 끌기로 회전
  let drag = null;
  canvas.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY }; tweening = false; canvas.setPointerCapture(e.pointerId); canvas.classList.add('globe-dragging'); });
  canvas.addEventListener('pointermove', e => {
    if (!drag) return;
    const q = 1 / (RAD * rot.k * canvas.clientWidth); // 확대와 무관하게 포인터를 따라 도는 각도(도/픽셀)
    rot.lon -= (e.clientX - drag.x) * q; rot.lat = Math.max(-60, Math.min(80, rot.lat + (e.clientY - drag.y) * q)); drag = { x: e.clientX, y: e.clientY };
    if (!running) render();
  });
  const end = () => { drag = null; canvas.classList.remove('globe-dragging'); };
  canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end);

  new ResizeObserver(() => { if (!running && S.world && el.isConnected) render(); }).observe(el);
  loadWorld().then(() => {
    if (!el.isConnected) return;
    if (replay) go(); else render();
  }).catch(() => { S.loading = null; }); // 지도 파일을 못 받으면 빈 원으로 남김
  if (cfg.det) loadDetail().then(() => { if (el.isConnected && S.world && !running) render(); }).catch(() => { S.detailLoading = null; }); // 못 받으면 50m로 남김
}

// ---- 개요 화면 지구본: 해외 다섯 곳에서 서울로 오는 흐름. 고정 시점 ----
const FLOWS = [['미국', [-115.87, 42.5], 'us'], // 미국 점: 워싱턴은 이 시점에서 뒷면이라 앞면 가장자리에 걸리는 아이다호 남부에 둠(직접 찍은 자리). 나라 화면 핀(ANCHORS.us)은 워싱턴 그대로
  ['EU', ANCHORS.eu, 'eu'], ['홍콩', ANCHORS.hk, 'hk'], ['싱가포르', ANCHORS.sg, 'sg'], ['일본', [132.46, 34.39], 'jp']]; // 일본 점: 개요에서는 히로시마. 나라 화면 핀(ANCHORS.jp)은 도쿄 그대로
const HERO_N = 90, TAIL = 9;
const T0 = performance.now();
let hero = null; // 지금 떠 있는 개요 지구본 하나. 다시 그려지면 이전 것을 멈춤

// 북쪽이 위. 윗 테두리는 보이고, 구가 칸보다 크면 오른쪽과 아래가 잘림. 시점은 유라시아 위(직접 돌려 맞춘 자리):
// EU, 홍콩, 싱가포르, 일본, 한국은 앞면
const HERO_VIEW = [119.31, 35.66], HERO_ROLL = 0, HERO_M = 22;
// 카드가 가리면 안 되는 땅: 한국과 일본 해안을 따라 찍은 점(경도, 위도)
const KEEP = [[126.5, 37.5], [127, 35], [129, 35.2], [129.4, 36], [128.6, 38.2], [126.5, 33.4], [126.4, 34.8], [129.9, 33.2], [130.5, 31.4], [131.6, 33.2], [132.6, 33.4], [134.6, 33.8], [131, 34.4], [132.5, 35.4], [134, 35.5], [135.5, 34.7], [136.9, 35.2], [136.6, 36.6], [137.5, 37.4], [138.2, 36.2], [139, 37.9], [139.7, 35.7], [140.9, 38.3], [140, 39.7], [141.4, 40.5], [140.7, 41], [140.3, 41.8], [141.4, 43.1], [142.4, 44.4], [141.7, 45.4], [143.2, 42.9], [144.4, 43], [145.3, 43.3], [144.3, 44]];
function heroGeo(W, H) {
  const R = Math.min((H - HERO_M - 26) / 1.69, W * 0.56); // 싱가포르(중심 아래 약 0.69R)와 이름표까지 보이게
  return { R, cx: Math.max(HERO_M + R, W * 0.45), cy: HERO_M + R, view: HERO_VIEW }; // 가운데보다 조금 왼쪽: 한국 오른쪽에 카드 자리
}

// 고정 시점이라 호의 화면 좌표는 크기가 바뀔 때만 계산하고, 매 프레임은 점과 번짐만 그림
function buildHero(inst) {
  const { canvas, col } = inst, { W, H, dpr } = sizeCanvas(canvas);
  const { R, cx, cy, view: V } = heroGeo(W, H), P = view(V[0], V[1], R, cx, cy, HERO_ROLL);
  const maxd = Math.max(Math.hypot(cx, cy), Math.hypot(W - cx, cy), Math.hypot(cx, H - cy), Math.hypot(W - cx, H - cy));
  const g = { P, vc: vec(...V), cap: maxd >= R ? Math.PI / 2 : Math.asin(maxd / R) };
  const sc = document.createElement('canvas'); sc.width = Math.round(W * dpr); sc.height = Math.round(H * dpr);
  const c = sc.getContext('2d'); c.setTransform(dpr, 0, 0, dpr, 0, 0);
  const sphere = () => { c.beginPath(); c.arc(cx, cy, R, 0, 7); };
  sphere(); c.globalAlpha = 0.2; c.fillStyle = col.surface; c.fill(); c.globalAlpha = 1; // 거의 비치는 구
  c.strokeStyle = col.line; c.lineWidth = 1; c.globalAlpha = 0.8; graticule(c, P, 30); c.globalAlpha = 1;
  c.globalAlpha = 0.1; c.fillStyle = col.stone; c.fill(backShape(P), 'nonzero'); c.globalAlpha = 1; // 먼 쪽 땅
  const all = shapes(S.world.keys(), g);
  c.globalAlpha = 0.55; c.fillStyle = col.stone; c.fill(all.fill, 'nonzero'); c.globalAlpha = 1;
  c.strokeStyle = 'rgba(255,255,255,.7)'; c.lineWidth = 0.5; c.stroke(all.edge);
  const peers = shapes([...EU_IDS, '840', '344', '702', '392'], g); c.globalAlpha = 0.3; c.fillStyle = col.accent; c.fill(peers.fill, 'nonzero'); c.globalAlpha = 1; // 비교하는 나라(미국, EU, 홍콩, 싱가포르, 일본)는 연하게
  const kr = shapes(['410'], g); c.fillStyle = col.accent; c.fill(kr.fill, 'nonzero');
  sphere(); c.strokeStyle = col.line; c.lineWidth = 1; c.stroke();

  // 호: 지표에서 떠올라 가는 대원. 가장자리 밖으로 나간 부분은 보임
  const seoul = vec(...SEOUL), seg = P(...seoul, false), flows = [];
  c.lineCap = 'round'; c.lineJoin = 'round';
  for (const [name, p, id] of FLOWS) {
    const a = vec(...p), ang = Math.acos(Math.max(-1, Math.min(1, a[0] * seoul[0] + a[1] * seoul[1] + a[2] * seoul[2])));
    const h = 0.05 + 0.2 * Math.min(1, ang / 1.8), xs = new Float32Array(HERO_N + 1), ys = new Float32Array(HERO_N + 1), vis = new Uint8Array(HERO_N + 1);
    c.beginPath(); let down = false, first = -1;
    for (let k = 0; k <= HERO_N; k++) {
      const u = k / HERO_N, v = slerp(a, seoul, u).map(q => q * (1 + h * Math.sin(Math.PI * u))), [x, y, z] = P(...v, false);
      xs[k] = x; ys[k] = y; vis[k] = z || Math.hypot(x - cx, y - cy) > R ? 1 : 0;
      if (vis[k]) { down ? c.lineTo(x, y) : c.moveTo(x, y); down = true; if (first < 0 && x > 14 && x < W * 0.9 && y > 16 && y < H * 0.9) first = k; } else down = false;
    }
    c.strokeStyle = col.ink; c.globalAlpha = 0.28; c.lineWidth = 1; c.stroke(); c.globalAlpha = 1;
    flows.push({ name, id, xs, ys, vis, first, period: 2.6 + 2 * ang });
  }
  // 카드 자리 넘기기: 각 호의 첫 보이는 점(출발점이 뒤에 있으면 호가 화면에 처음 들어오는 자리)과 서울, 호의 보이는 점들(카드가 호를 가리지 않게). 화면 좌표는 캔버스와 같은 CSS px.
  // onLayout이 카드를 놓은 id 목록을 돌려주면 그 곳의 캔버스 이름표는 그리지 않음
  const pts = flows.filter(f => f.first >= 0).map(f => ({ id: f.id, name: f.name, x: f.xs[f.first], y: f.ys[f.first], dx: f.xs[Math.min(f.first + 8, HERO_N)] - f.xs[f.first] }));
  const arcs = flows.map(f => { const o = []; for (let k = 0; k <= HERO_N; k++) if (f.vis[k]) o.push(f.xs[k], f.ys[k]); return o; });
  const keep = KEEP.map(([lo, la]) => P(...vec(lo, la), false)).filter((q) => q[2]).map(([x, y]) => ({ x, y }));
  const carded = new Set(inst.onLayout?.({ W, H, points: pts, seoul: { x: seg[0], y: seg[1] }, arcs, keep }) || []);
  // 이름표: 출발점이 보이면 그 자리, 뒤에 있으면 호가 화면에 처음 들어오는 자리
  c.font = `500 11px ${col.sans}`; c.textBaseline = 'middle';
  for (const f of flows) {
    if (f.first < 0) continue;
    const x = f.xs[f.first], y = f.ys[f.first], k2 = Math.min(f.first + 8, HERO_N), dx = f.xs[k2] - x, dy = f.ys[k2] - y; // 이름표는 호가 뻗는 쪽의 반대편
    c.beginPath(); c.arc(x, y, 2.5, 0, 7); c.fillStyle = col.ink; c.fill(); c.strokeStyle = '#fff'; c.lineWidth = 1.5; c.stroke();
    if (!carded.has(f.id)) tag(c, col, W, H, f.name, x + (dx > 0 ? -7 : 7), y + (dy > 0 ? -9 : 10), dx > 0 ? 'right' : 'left');
  }
  c.beginPath(); c.arc(seg[0], seg[1], 11, 0, 7); c.strokeStyle = col.accent; c.globalAlpha = 0.35; c.lineWidth = 1; c.stroke(); c.globalAlpha = 1; // 한국 둘레 고리
  c.beginPath(); c.arc(seg[0], seg[1], 3.5, 0, 7); c.fillStyle = col.accent; c.fill(); c.strokeStyle = '#fff'; c.lineWidth = 1.5; c.stroke();
  c.font = `600 12px ${col.sans}`; if (!carded.has('kr')) tag(c, col, W, H, '한국', seg[0] + 16, seg[1] - 4, 'left', col.accent);
  Object.assign(inst, { W, H, dpr, sc, flows, seoul: seg, ready: true });
}

function heroFrame(inst, sec) {
  const { canvas, col, W, H, dpr, sc, flows, seoul } = inst, ctx = canvas.getContext('2d');
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, canvas.width, canvas.height); ctx.drawImage(sc, 0, 0);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  if (inst.still) return;
  flows.forEach((f, i) => {
    for (let q = 0; q < 2; q++) {
      const ph = sec / f.period + q / 2 + i * 0.23, u = ph - Math.floor(ph), N = f.xs.length - 1;
      // 도착 직후 서울에서 번지는 고리
      const age = u * f.period;
      if (age < 1.5) { const m = age / 1.5; ctx.globalAlpha = 0.35 * (1 - m); ctx.strokeStyle = col.accent; ctx.lineWidth = 1.25; ctx.beginPath(); ctx.arc(seoul[0], seoul[1], 4 + 20 * m, 0, 7); ctx.stroke(); ctx.globalAlpha = 0.07 * (1 - m); ctx.fillStyle = col.accent; ctx.beginPath(); ctx.arc(seoul[0], seoul[1], 4 + 24 * m, 0, 7); ctx.fill(); }
      ctx.fillStyle = col.ink;
      for (let j = 0; j < TAIL; j++) { // 꼬리: 뒤로 갈수록 작고 옅게
        const pos = (u - j * 0.012) * N; if (pos < 0) break;
        const k = Math.min(N - 1, Math.floor(pos)), r = pos - k;
        if (!f.vis[k] || !f.vis[k + 1]) continue;
        ctx.globalAlpha = 0.8 * (1 - j / TAIL); ctx.beginPath(); ctx.arc(f.xs[k] + (f.xs[k + 1] - f.xs[k]) * r, f.ys[k] + (f.ys[k + 1] - f.ys[k]) * r, 2.1 * (1 - j / (TAIL + 2)), 0, 7); ctx.fill();
      }
    }
  });
  ctx.globalAlpha = 1;
}

export function mountHeroGlobe(el, { onLayout } = {}) { // onLayout({ W, H, points, seoul, arcs, keep }) => 카드를 놓은 id 목록, 크기가 바뀔 때마다 부름
  hero?.stop();
  const canvas = document.createElement('canvas');
  canvas.className = 'globe-canvas hero-canvas'; canvas.setAttribute('role', 'img');
  canvas.setAttribute('aria-label', '지구본: 미국, EU, 홍콩, 싱가포르, 일본에서 한국으로 이어지는 흐름');
  el.textContent = ''; el.append(canvas);
  const inst = { canvas, col: colors(), still: reduced(), ready: false, onLayout };
  let raf = 0, dead = false, onScreen = true;
  const stop = () => { dead = true; cancelAnimationFrame(raf); ro.disconnect(); io.disconnect(); document.removeEventListener('visibilitychange', kick); };
  const tick = now => {
    raf = 0;
    if (dead || !el.isConnected) { stop(); return; }
    if (!onScreen || document.hidden || !inst.ready) return; // 다시 보이면 kick이 이어 줌
    heroFrame(inst, (now - T0) / 1000);
    if (!inst.still) raf = requestAnimationFrame(tick);
  };
  function kick() { if (!raf && !dead) raf = requestAnimationFrame(tick); }
  const rebuild = () => { if (dead || !S.world || !el.isConnected) return; buildHero(inst); kick(); };
  let rq = 0; const ro = new ResizeObserver(() => { cancelAnimationFrame(rq); rq = requestAnimationFrame(rebuild); }); ro.observe(el);
  const io = new IntersectionObserver(es => { onScreen = es[es.length - 1].isIntersecting; if (onScreen) kick(); }); io.observe(el);
  document.addEventListener('visibilitychange', kick);
  hero = { stop };
  loadWorld().then(rebuild).catch(() => { S.loading = null; });
}
