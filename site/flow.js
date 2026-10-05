// 판정 흐름: 나라 / 판정 결과 / 규칙 세 축을 잇는 평행 집합(parallel sets) 그래프.
// 판정 하나가 선 한 줄이고, 선은 가운데 축을 지나 같은 색으로 이어진다.
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const STATUS_ORDER = ['met', 'caution', 'unmet', 'none'];
const STATUS_NAME = { met: '충족', caution: '주의', unmet: '미충족', none: '판정 안 됨' };
// 나라 축 이름표: 국기(투명도 .5)와 이름. 국기 SVG는 flag-icons(MIT), site/flags/
const FLAG = { 'kr-v1': 'kr', us: 'us', 'eu-emt': 'eu', 'eu-emt-significant': 'eu', hk: 'hk', sg: 'sg', jp: 'jp' };
const U = 6, BAR = 8, TOP = 36, TAG_H = 17;
// 글자 폭 어림: 한글 1em, 숫자와 영문 .6em
const tw = (s, fs) => [...String(s)].reduce((n, c) => n + (c > 'ÿ' ? fs : fs * 0.6), 0);
const uniq = (list) => [...new Set(list)];
const sum = (rows, key) => rows.reduce((o, r) => (o[r[key]] = (o[r[key]] || 0) + 1, o), {});
const statusText = (n) => STATUS_ORDER.map((s) => `${STATUS_NAME[s]} ${n[s] || 0}`).join(', ');

// rows: [{country, countryName, rule, ruleName, status}] status는 met, caution, unmet, none
// 나라와 규칙의 축 순서는 rows에 처음 나온 순서
export function flowSvg(rows, { focus, width = 1100 } = {}) {
  const countries = uniq(rows.map((r) => r.country)), rules = uniq(rows.map((r) => r.rule));
  const nameOf = Object.fromEntries(rows.map((r) => [r.country, r.countryName]));
  // 왼쪽은 나라 이름과 국기 자리. 국기는 그 나라 막대와 같은 높이, 너비는 4:3
  const perC = sum(rows, 'country'), FW = Math.max(...countries.map((c) => perC[c])) * U * 4 / 3;
  const L = Math.ceil(Math.max(...countries.map((c) => tw(nameOf[c], 13))) + FW + 18);
  // 가로 폭은 칸 폭에 맞춤(오른쪽 규칙 이름 270 자리를 빼고 세 축을 벌림)
  const W = Math.max(900, Math.round(width)), R = W - 270, M = Math.round((L + R) / 2);
  const statuses = STATUS_ORDER.filter((s) => rows.some((r) => r.status === s));
  const ci = (r) => countries.indexOf(r.country), ri = (r) => rules.indexOf(r.rule), si = (r) => STATUS_ORDER.indexOf(r.status);
  const units = rows.map((r, i) => ({ ...r, i }));
  const ruleNameOf = Object.fromEntries(rows.map((r) => [r.rule, r.ruleName]));
  const H = rows.length * U + (rules.length - 1) * 8; // 규칙 축 높이(판정 수 × 줄 높이 + 규칙 사이 8px)가 기준. 나머지 축은 이 높이에 맞춰 간격을 벌림

  // 축마다 노드 위치를 잡고, 노드 안에서 판정을 줄 세운다
  const place = (keys, keyOf, sortFn, labelOf) => {
    const total = units.length * U, gap = keys.length > 1 ? (H - total) / (keys.length - 1) : 0;
    let y = TOP; const nodes = {};
    keys.forEach((k) => {
      const mine = units.filter((u) => keyOf(u) === k).sort(sortFn);
      nodes[k] = { key: k, y, h: mine.length * U, n: mine.length, label: labelOf(k) };
      mine.forEach((u, j) => { u[`y${keyOf.axis}`] = y + j * U; });
      y += mine.length * U + gap;
    });
    return nodes;
  };
  const kc = Object.assign((u) => u.country, { axis: 'L' }), ks = Object.assign((u) => u.status, { axis: 'M' }), kr = Object.assign((u) => u.rule, { axis: 'R' });
  const left = place(countries, kc, (a, b) => si(a) - si(b) || ri(a) - ri(b), (k) => nameOf[k]);
  const mid = place(statuses, ks, (a, b) => ci(a) - ci(b) || ri(a) - ri(b), (k) => STATUS_NAME[k]);
  // 규칙 축은 노드 높이가 모두 같으므로 간격 8px로 직접 배치
  const rightNodes = {}; let ry = TOP;
  rules.forEach((k) => {
    const mine = units.filter((u) => u.rule === k).sort((a, b) => si(a) - si(b) || ci(a) - ci(b));
    rightNodes[k] = { key: k, y: ry, h: mine.length * U, n: mine.length };
    mine.forEach((u, j) => { u.yR = ry + j * U; });
    ry += mine.length * U + 8;
  });

  const f = (x) => Math.round(x * 10) / 10;
  const band = (x1, y1, x2, y2) => { // 아래쪽을 .12px 겹쳐 인접한 줄 사이 틈이 안 보이게 함
    const h = U + 0.12, xm = (x1 + x2) / 2;
    return `M${f(x1)} ${f(y1)}C${f(xm)} ${f(y1)} ${f(xm)} ${f(y2)} ${f(x2)} ${f(y2)}V${f(y2 + h)}C${f(xm)} ${f(y2 + h)} ${f(xm)} ${f(y1 + h)} ${f(x1)} ${f(y1 + h)}Z`;
  };
  const label = (u) => `${u.countryName}, ${u.ruleName}: ${STATUS_NAME[u.status]}`;
  // 한국을 맨 위에 그림
  const drawn = [...units].sort((a, b) => (a.country === focus) - (b.country === focus));
  const ribbons = drawn.map((u) => `<g class="flow-u s-${u.status}${u.country === focus ? ' kr' : ''}" data-i="${u.i}" data-c="${esc(u.country)}" data-s="${u.status}" data-r="${esc(u.rule)}"><title>${esc(label(u))}</title><path d="${band(L + BAR, u.yL, M, u.yM)}"/><path d="${band(M + BAR, u.yM, R, u.yR)}"/></g>`).join('');

  const bar = (x, n, cls) => `<rect class="flow-bar ${cls}" x="${x}" y="${f(n.y)}" width="${BAR}" height="${n.h}"/>`;
  const tag = ({ k, v, x, anchor, n, cls = '', text, code, aria, big }) => {
    const fs = big ? 12 : 11, h = big ? TAG_H + 3 : TAG_H, y = n.y + n.h / 2;
    const w = Math.ceil(tw(`${code ? `${code}  ` : ''}${text}`, fs) + 12);
    const x0 = anchor === 'end' ? x - w : anchor === 'middle' ? x - w / 2 : x;
    return `<g class="flow-tag${big ? ' big' : ''} ${cls}" tabindex="0" role="button" data-k="${k}" data-v="${esc(v)}" aria-label="${esc(aria)}"><rect x="${f(x0)}" y="${f(y - h / 2)}" width="${w}" height="${h}" rx="2"/><text x="${f(x0 + 6)}" y="${f(y + fs * 0.36)}" font-size="${fs}">${code ? `<tspan class="flow-code" font-size="10">${esc(code)}</tspan><tspan dx="6">` : '<tspan>'}${esc(text)}</tspan></text></g>`;
  };
  // 국기는 막대 바로 왼쪽에 붙이고, 이름은 국기들 왼쪽에 오른쪽 맞춤
  const ctag = ({ v, n, text, aria, big }) => {
    const fs = big ? 13 : 12, fw = n.h * 4 / 3, fx = L - 4 - fw, tx = L - 12 - FW, x0 = tx - tw(text, fs) - 6;
    const flag = FLAG[v] ? `<image href="flags/${FLAG[v]}.svg" x="${f(fx)}" y="${f(n.y)}" width="${f(fw)}" height="${n.h}" opacity=".5"/><rect class="flow-flag" x="${f(fx)}" y="${f(n.y)}" width="${f(fw)}" height="${n.h}"/>` : '';
    return `<g class="flow-tag flow-ctag${big ? ' big' : ''}" tabindex="0" role="button" data-k="c" data-v="${esc(v)}" aria-label="${esc(aria)}"><rect x="${f(x0)}" y="${f(n.y - 3)}" width="${f(L - 2 - x0)}" height="${n.h + 6}" rx="3"/>${flag}<text x="${f(tx)}" y="${f(n.y + n.h / 2 + fs * 0.36)}" font-size="${fs}" text-anchor="end">${esc(text)}</text></g>`;
  };
  const byC = rows.reduce((o, r) => ((o[r.country] ||= {})[r.status] = (o[r.country][r.status] || 0) + 1, o), {});
  const tags = [
    ...countries.map((c) => ctag({ v: c, n: left[c], text: nameOf[c], big: c === focus, aria: `${nameOf[c]}: ${statusText(byC[c])}` })),
    ...statuses.map((s) => tag({ k: 's', v: s, x: M + BAR / 2, anchor: 'middle', n: mid[s], text: `${STATUS_NAME[s]} ${mid[s].n}`, aria: `${STATUS_NAME[s]} ${mid[s].n}개` })),
    ...rules.map((r) => tag({ k: 'r', v: r, x: R + BAR + 6, anchor: 'start', n: rightNodes[r], code: r, text: ruleNameOf[r], aria: `${r} ${ruleNameOf[r]}: ${statusText(sum(rows.filter((x) => x.rule === r), 'status'))}` })),
  ].join('');
  const bars = countries.map((c) => bar(L, left[c], 'c')).join('') + statuses.map((s) => bar(M, mid[s], `s-${s}`)).join('') + rules.map((r) => bar(R, rightNodes[r], 'r')).join('');
  const head = (x, anchor, t) => `<text class="flow-axis" x="${x}" y="16" text-anchor="${anchor}" font-size="12">${t}</text>`;
  const total = sum(rows, 'status'), Ht = TOP + H + 8;
  const aria = `판정 흐름: 판정 ${rows.length}건. ${focus && byC[focus] ? `${nameOf[focus]} ${statusText(byC[focus])}. ` : ''}전체 ${statusText(total)}`;
  return `<svg class="flow-svg" viewBox="0 0 ${W} ${Ht}" width="${W}" height="${Ht}" style="width:100%;max-width:${W}px" role="group" aria-label="${esc(aria)}">${head(L, 'end', `나라 ${countries.length}곳`)}${head(M + BAR / 2, 'middle', '판정 결과')}${head(R, 'start', `규칙 ${rules.length}개`)}<g class="flow-ribbons">${ribbons}</g>${bars}${tags}</svg>`;
}

// 그래프 아래 합계 줄: 한국, 전체, 가장 많이 미충족인 규칙
export function flowTotals(rows, { focus } = {}) {
  const total = sum(rows, 'status'), mine = rows.filter((r) => r.country === focus);
  const unmetBy = {}; rows.filter((r) => r.status === 'unmet').forEach((r) => { unmetBy[r.rule] = (unmetBy[r.rule] || 0) + 1; });
  const top = Object.entries(unmetBy).sort((a, b) => b[1] - a[1])[0];
  const name = rows.find((r) => r.rule === top?.[0])?.ruleName;
  const col = (k, v) => `<p><span>${k}</span><b class="num">${v}</b></p>`;
  return `<div class="flow-totals">${mine.length ? col(`${esc(mine[0].countryName)} ${mine.length}건`, esc(statusText(sum(mine, 'status')))) : ''}${col(`전체 ${rows.length}건`, esc(statusText(total)))}${col('미충족이 가장 많은 규칙', top ? `${esc(top[0])} ${esc(name)}, ${top[1]}곳` : '없음')}</div>`;
}

// 나라, 판정 결과, 규칙 이름이나 선에 올리면 그 판정만 진하게 보임. 구역 하나에 이벤트를 한 번만 걸면 다시 그려도 유지됨
export function bindFlow(root) {
  const set = (svg, el) => {
    if (!svg) return;
    const k = el?.dataset.k || (el ? 'i' : null), v = el?.dataset.v ?? el?.dataset.i;
    svg.classList.toggle('is-hl', Boolean(el));
    svg.querySelectorAll('.flow-u').forEach((u) => u.classList.toggle('hit', Boolean(el) && u.dataset[k === 'i' ? 'i' : k] === v));
    svg.querySelectorAll('.flow-tag').forEach((t) => t.classList.toggle('on', t === el));
  };
  const target = (e) => { const t = e.target.closest?.('.flow-tag, .flow-u'); return t ? { svg: t.closest('.flow-svg'), el: t } : { svg: e.target.closest?.('.flow-svg'), el: null }; };
  const on = (e) => { const { svg, el } = target(e); if (el) set(svg, el); };
  const off = (e) => set(e.target.closest?.('.flow-svg'), null);
  root.addEventListener('mouseover', on); root.addEventListener('focusin', on);
  root.addEventListener('mouseout', off); root.addEventListener('focusout', off);
}
