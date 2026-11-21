// 판정기 사이트(site/)의 아이소 그림 모듈로 Brand Board 포스터용 장면 SVG를 만든다. build_hub.py가 실행해 stdout을 받는다.
const S = new URL('../../site/', import.meta.url).href;
const { seoul } = await import(S + 'iso_buildings.js');
const { bankBuilding } = await import(S + 'iso_bank.js');
const { vaultBuilding } = await import(S + 'iso_vault.js');
const { coinStacks } = await import(S + 'iso_coins.js');
const { personFigure } = await import(S + 'iso_person.js');

const items = [
  seoul(80, 150, null),
  bankBuilding(215, 150, { symbol: '₩' }),
  vaultBuilding(350, 150),
  coinStacks(470, 150, { symbol: '₩' }),
  personFigure(585, 150),
];
const body = items.map((o) => o.svg ?? o.el.join('')).join('');
const xs = [], ys = [];
for (const o of items) for (const [x, y] of (o.ps ?? o.poly)) { xs.push(x); ys.push(y); }
const pad = 8, x0 = Math.min(...xs) - pad, y0 = Math.min(...ys) - pad;
const w = Math.max(...xs) + pad - x0, h = Math.max(...ys) + pad - y0;
const css = `.iso-face{stroke:#736D68;stroke-opacity:.5;stroke-width:.8;stroke-linejoin:round}.iso-t,.iso-w{fill:#fff}.iso-l{fill:#ECE9E6}.iso-r{fill:#D9D5D1}.iso-st-l{fill:#dccfb4}.iso-st-r{fill:#c9b995}.iso-face.iso-coin-edge{fill:none;stroke:#4A4541;stroke-opacity:1}.iso-d.iso-coin-fine{stroke-width:.6}.iso-pf-l{fill:#4A4541}.iso-pf-d{fill:#141210}.iso-pf-s1{fill:#ECE9E6}.iso-pf-s2{fill:#D9D5D1}.iso-mark{fill:none;stroke:#4A4541;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}.iso-coin-sym{fill:#4A4541;stroke:none;font-weight:800}.iso-d{fill:none;stroke:#4A4541;stroke-width:.9;stroke-linejoin:round;stroke-linecap:round}.iso-df{fill:#fff}.iso-dp{fill:#ECE9E6}.iso-dk{fill:#4A4541}.iso-fl{stroke:none}.iso-fline{fill:none;stroke:#fff;stroke-opacity:.4;stroke-width:.5}text{font-family:-apple-system,"Apple SD Gothic Neo",sans-serif}`;
process.stdout.write(`<svg class="bb-iso" viewBox="${x0.toFixed(1)} ${y0.toFixed(1)} ${w.toFixed(1)} ${h.toFixed(1)}" role="img" aria-label="규제기관, 은행, 금고, 원화 코인, 이용자"><style>${css}</style>${body}</svg>`);
