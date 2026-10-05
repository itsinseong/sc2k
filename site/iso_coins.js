// 준비금 그림: 동전 기둥 네 개를 가까이 모아 세운다. iso.js drawObj와 같은 정등각 투영을 쓴다.
// 사용(drawObj 안, 준비금 상자 자리):  else if (kind === 'coins') { const c = coinStacks(cx, cy, { symbol }); el.push(c.svg); ps.push(...c.poly); }
//   (cx, cy)는 바닥 가운데. 크기는 옛 준비금 상자(바닥 64.7 x 64.7, 높이 22)와 비슷하다: 가장 높은 기둥이 22, 가로 약 103(상자 112)
//   symbol은 나라 통화 기호('$', '€', 'HK$', 'S$', '¥', '₩'). 주면 기둥마다 맨 위 동전 윗면에 쓰고, 안 주면 기호 없이 그린다.
// 동전 하나는 짧은 원기둥이다. 바닥 반지름 r인 원은 화면에서 가로 반지름 r*sqrt(2)*C30, 세로 반지름 r*sqrt(2)/2인 타원이다.
// 모양: 맨 위 동전은 흰 윗면에 안쪽 고리 하나와 통화 기호, 옆면은 밝은 쪽 --pale과 오른쪽 어두운 쪽 --stone(상자의 두 옆면과 같은 빛), 동전 사이마다 가는 호, 바깥 윤곽은 --ink-2.
// 바깥 윤곽만 <polygon class="iso-face">이라 겹침 검사와 이름표 자리 잡기가 다른 블록처럼 읽는다. 블록 묶음(<g>) 안에 들어가므로 <g>는 쓰지 않는다(기호도 <text> 하나).
// 기호는 윗면 바닥 평면에 눕혀 쓴다. 글줄이 화면 가로로 읽히게 놓아, 바닥 길이 1이 화면에서 가로 sqrt(2)*C30, 세로 sqrt(2)/2가 된다(윗면 타원과 같은 비율).
//   국기처럼 칸 방향(x축)으로 글줄을 맞추면 기호가 비스듬히 누워 $와 ₩가 알아보기 어렵다.
//
// 붙여 넣을 CSS(styles.css의 .iso-r 규칙 아래). 채움은 기존 iso-t(흰색), iso-l(--pale), iso-r(--stone), iso-fl과 가는 선 iso-d를 그대로 쓴다.
// iso-coin이라는 이름은 쓰지 않는다: iso.js가 코인 이름표 묶음(iso-lab iso-coin)에 이미 붙여 두었고, 이 이름에 선을 주면 이름표 글자까지 번진다.
// 기호 글꼴은 .iso-svg text 규칙(var(--sans))을 따르고, 크기와 자리는 이 모듈이 정한다.
/*
.iso-face.iso-coin-edge{fill:none;stroke:var(--ink-2);stroke-opacity:1}
.iso-d.iso-coin-fine{stroke-width:.6}
.iso-ghost .iso-face.iso-coin-edge{fill:rgba(255,255,255,.4);stroke:var(--muted);stroke-opacity:.8}
.iso-coin-sym{fill:var(--ink-2);font-weight:800}
.iso-ghost .iso-coin-sym{fill:var(--muted);opacity:.45}
*/
const C30 = Math.sqrt(3) / 2;
const R = 17, T = 3.7, RING = .78, SHADE = .35, N = 36;   // 동전 바닥 반지름, 동전 한 개 두께, 윗면 고리와 윗면의 반지름 비, 어두운 옆면이 시작하는 자리(가운데에서 오른쪽으로 반지름의 몇 배), 타원 하나를 나누는 점 수
const G = 17.8;                                          // 기둥 가운데가 바닥 가운데에서 x, y로 떨어진 거리. 이웃한 기둥 사이가 2G - 2R = 1.6
// [바닥 x, y, 동전 개수]. 2 x 2로 서고, 뒤(x+y가 작은 쪽)가 높고 앞이 낮다
const STACKS = [[-G, -G, 6], [-G, G, 4], [G, -G, 5], [G, G, 3]];
// 기호 크기: 글자 상자(폭, 높이, 단위 em)를 감싸는 원의 지름이 안쪽 고리 지름의 FIT배가 되게 한다. 한 글자 기호는 모두 가장 넓은 ₩에 맞춘 같은 크기고, HK$나 S$는 그만큼 작다.
// 글자 폭은 Pretendard Variable 굵기 800 실측(em)이고 표에 없는 글자는 .66. 상자 폭은 폭의 합에서 양옆 여백 .06을 뺀 값, 높이는 $가 위아래로 삐져나와 .885, 나머지는 대문자 높이 .72
const ADV = { $: .64, '€': .67, '¥': .56, '₩': .92, H: .72, K: .68, S: .64 };
const FIT = .88, BASE = .354;                            // BASE: 글자 상자 가운데에서 글줄 바닥선까지(em). 여섯 기호가 같다
const fit = (t) => FIT * 2 * R * RING / Math.hypot([...t].reduce((n, c) => n + (ADV[c] ?? .66), 0) - .06, t.includes('$') ? .885 : .72);
const ONE = fit('₩');
const f = (n) => Math.round(n * 100) / 100;
const g4 = (n) => Math.round(n * 1e4) / 1e4;
const p = (x, y) => `${f(x)} ${f(y)}`;
const esc = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
// iso.js의 hull과 같다(모듈 하나로 쓰려고 옮김)
const hull = (a) => {
  const q = [...a].sort((m, n) => m[0] - n[0] || m[1] - n[1]), cr = (o, m, n) => (m[0] - o[0]) * (n[1] - o[1]) - (m[1] - o[1]) * (n[0] - o[0]);
  const half = (s) => { const r = []; for (const t of s) { while (r.length > 1 && cr(r[r.length - 2], r[r.length - 1], t) <= 0) r.pop(); r.push(t); } r.pop(); return r; };
  return [...half(q), ...half([...q].reverse())];
};

// opt.k: 크기 배율(기본 1). opt.symbol: 통화 기호(기본 없음). 되돌림: svg는 문자열, poly는 전체를 감싸는 볼록 윤곽 [[x, y], ...]
export function coinStacks(cx, cy, opt = {}) {
  const { k = 1 } = opt, sym = String(opt.symbol ?? '').trim(), fs = sym && Math.min(ONE, fit(sym));
  const rx = R * k * Math.SQRT2 * C30, ry = R * k * Math.SQRT1_2, t = T * k, dx = SHADE * rx, dy = ry * Math.sqrt(1 - SHADE * SHADE);   // dx, dy: 옆면 어두운 쪽이 시작하는 세로선의 가운데에서 거리와, 그 선이 타원 앞쪽과 만나는 높이
  const el = [], all = [];
  // ponytail: 그리는 차례는 깊이 x+y만 본다. 같은 크기의 기둥이 서로 겹쳐 서지 않을 때만 맞다
  for (const [gx, gy, n] of [...STACKS].sort((a, b) => a[0] + a[1] - b[0] - b[1] || a[0] - b[0])) {
    const x = cx + (gx - gy) * k * C30, yb = cy + (gx + gy) * k / 2, yt = yb - n * t;   // 바닥 타원과 맨 위 윗면 타원의 가운데
    const arc = (s, X, Y) => `A${p(rx, ry)} 0 0 ${s} ${p(X, Y)}`;                       // 사분호: s 0은 시계 반대, 1은 시계 방향
    const front = (y, ltr) => ltr ? arc(0, x, y + ry) + arc(0, x + rx, y) : arc(1, x, y + ry) + arc(1, x - rx, y);   // 타원 앞쪽 반
    const ring = (y, r) => `<ellipse class="iso-d iso-dn iso-coin-fine" cx="${f(x)}" cy="${f(y)}" rx="${f(rx * r)}" ry="${f(ry * r)}"/>`;
    // 기호: 글자 좌표(글줄 바닥선 y = BASE*fs, 가운데 x = 0)를 윗면 가운데에 놓고 가로 rx/R, 세로 ry/R로 보낸다
    const mark = sym && `<text class="iso-coin-sym" transform="matrix(${g4(rx / R)} 0 0 ${g4(ry / R)} ${f(x)} ${f(yt)})" y="${f(BASE * fs)}" font-size="${f(fs)}" text-anchor="middle">${esc(sym)}</text>`;
    // 윤곽: 위 타원의 뒤쪽 반(왼쪽 끝, 위, 오른쪽 끝)에 아래 타원의 앞쪽 반(오른쪽 끝, 앞, 왼쪽 끝)을 이어 붙인다
    const half = (y, u0) => Array.from({ length: N / 2 + 1 }, (_, i) => { const u = u0 + 2 * Math.PI * i / N; return [x + rx * Math.cos(u), y + ry * Math.sin(u)]; });
    const edge = [...half(yt, Math.PI), ...half(yb, 0)];
    all.push(...edge);
    let seam = '';
    for (let j = 1; j <= n; j++) seam += `M${p(x - rx, yb - j * t)}${front(yb - j * t, 1)}`;   // 동전 사이마다 앞쪽 호. 맨 위 호는 윗면의 앞 가장자리
    el.push(
      `<path class="iso-fl iso-l" d="M${p(x - rx, yt)}V${f(yb)}${front(yb, 1)}V${f(yt)}${front(yt, 0)}z"/>`,                                  // 옆면 전체(밝은 쪽)
      `<path class="iso-fl iso-r" d="M${p(x + dx, yt + dy)}V${f(yb + dy)}${arc(0, x + rx, yb)}V${f(yt)}${arc(1, x + dx, yt + dy)}z"/>`,   // 오른쪽 어두운 쪽
      `<ellipse class="iso-fl iso-t" cx="${f(x)}" cy="${f(yt)}" rx="${f(rx)}" ry="${f(ry)}"/>`,                                            // 윗면
      ring(yt, RING),
      mark,
      `<path class="iso-d iso-dn iso-coin-fine" d="${seam}"/>`,
      `<polygon class="iso-face iso-coin-edge" points="${edge.map(([X, Y]) => `${f(X)},${f(Y)}`).join(' ')}"/>`,               // 바깥 윤곽
    );
  }
  return { svg: el.join(''), poly: hull(all) };
}
