import { evaluateReport, STATUS, calendarDaysBetween } from './engine.js';

const JURISDICTIONS = [
  { id: 'us', label: 'US' },
  { id: 'eu-emt', label: 'EU 일반 EMT' },
  { id: 'eu-emt-significant', label: 'EU 중요 EMT' },
  { id: 'hk', label: 'HK' },
  { id: 'sg', label: 'SG' },
  { id: 'kr-v1', label: 'KR-v1' },
];

// PRD 7절 판정 규칙 표의 규칙명. 관할권/후보값별 세부 요건 문구는 각 ruleDef.requirement에 있다.
const RULE_TITLES = {
  R01: '커버리지 = 준비자산 공정가치 / 발행잔액 ≥ 100%',
  R02: '허용 자산 종류',
  R03: '국채 잔존만기 상한',
  R04: '레포 만기',
  R05: '현금성(은행 예치) 최저 비율',
  R06: '준비자산 통화 일치',
  R07: '공개 주기',
  R08: '검증 수준(examination, attestation, audit 구분)',
  R09: '검증 기준시각',
  R10: '공개 기한',
  R11: '발행잔액 산식 공개',
  R12: '수탁기관과 위치 공개',
  R13: '환매 조건(액면, 기한, 수수료)',
  R14: '이자 지급 금지',
  R15: '경영진 인증',
};

const STATUS_CLASS = {
  [STATUS.MET]: 'st-met',
  [STATUS.UNMET]: 'st-unmet',
  [STATUS.CAUTION]: 'st-caution',
  [STATUS.NO_DATA]: 'st-nodata',
  [STATUS.PENDING]: 'st-pending',
  [STATUS.NOT_REGULATED]: 'st-notreg',
  [STATUS.UNRESEARCHED]: 'st-unresearched',
};

const STATUS_COLOR_VAR = {
  [STATUS.MET]: '--good',
  [STATUS.UNMET]: '--critical',
  [STATUS.CAUTION]: '--warning',
  [STATUS.NO_DATA]: '--ink-3',
  [STATUS.PENDING]: '--pending',
  [STATUS.NOT_REGULATED]: '--ink-3',
  [STATUS.UNRESEARCHED]: '--ink-3',
};

const state = {
  reports: [],
  jurisdictions: {},
  reportIdx: 0,
  jurId: 'us',
  // KR-v1 전용: { R05: 'proposal', ... }. 안 고르면 관할권 설정의 default_candidate.
  candidates: {},
  expanded: new Set(),
};

async function loadAll() {
  const reportsRes = await fetch('data/reports.json');
  const reportsDoc = await reportsRes.json();
  state.reports = reportsDoc.reports;

  const entries = await Promise.all(
    JURISDICTIONS.map(async (j) => [j.id, await (await fetch(`jurisdictions/${j.id}.json`)).json()]),
  );
  state.jurisdictions = Object.fromEntries(entries);
}

function currentReport() {
  return state.reports[state.reportIdx];
}

function fmtPct(x, digits = 4) {
  if (x == null || Number.isNaN(x)) return '—';
  return `${(x * 100).toFixed(digits)}%`;
}

function reportLabel(r) {
  return `${r.issuer || r.token} ${r.token}, ${r.month}`;
}

function renderReportSelect() {
  const sel = document.getElementById('reportSelect');
  sel.innerHTML = state.reports
    .map((r, i) => `<option value="${i}" ${i === state.reportIdx ? 'selected' : ''}>${reportLabel(r)}</option>`)
    .join('');
  sel.onchange = () => {
    state.reportIdx = Number(sel.value);
    renderAll();
  };
}

function renderJurToggle() {
  const box = document.getElementById('jurToggle');
  box.innerHTML = JURISDICTIONS.map(
    (j) => `<button type="button" data-jur="${j.id}" aria-pressed="${j.id === state.jurId}">${j.label}</button>`,
  ).join('');
  box.querySelectorAll('button').forEach((btn) => {
    btn.onclick = () => {
      state.jurId = btn.dataset.jur;
      renderAll();
    };
  });
}

function renderStats(verdicts) {
  const report = currentReport();
  const jur = state.jurisdictions[state.jurId];
  const r01 = verdicts.find((v) => v.rule === 'R01');
  const coverage = r01 && typeof r01.value === 'number' ? r01.value : null;
  const freshDays = calendarDaysBetween(report.as_of, new Date().toISOString().slice(0, 10));
  const stale = freshDays != null && freshDays > 45;

  const covPct = coverage == null ? null : Math.max(0, Math.min(1, (coverage - 0.99) / 0.02)) * 100;

  document.getElementById('statsRow').innerHTML = `
    <div class="stat"><dt>발행사</dt><dd>${report.issuer || '—'}</dd></div>
    <div class="stat"><dt>기준일</dt><dd class="mono">${report.as_of || '—'}</dd></div>
    <div class="stat"><dt>기준일로부터 오늘까지</dt><dd class="mono ${stale ? 'warn' : ''}">${freshDays == null ? '—' : `${freshDays}일`}</dd></div>
    <div class="stat"><dt>검증기관</dt><dd>${(report.attestation && report.attestation.firm) || '미확인'}</dd></div>
    <div class="stat"><dt>검증 서명일</dt><dd class="mono">${(report.attestation && report.attestation.signed) || '—'}</dd></div>
    <div class="stat">
      <dt>커버리지(R01, ${jur.name})</dt>
      <dd class="mono">${coverage == null ? '데이터 없음' : fmtPct(coverage)}</dd>
      ${coverage == null ? '' : `<div class="cov-bar"><div class="fill" style="width:${covPct}%"></div><div class="mark"></div></div>`}
    </div>
  `;
}

function renderComposition(verdicts) {
  const counts = {};
  for (const v of verdicts) counts[v.status] = (counts[v.status] || 0) + 1;
  const order = [STATUS.MET, STATUS.UNMET, STATUS.CAUTION, STATUS.PENDING, STATUS.NO_DATA, STATUS.NOT_REGULATED, STATUS.UNRESEARCHED];
  const total = verdicts.length;
  const bar = order
    .filter((s) => counts[s])
    .map((s) => `<span style="width:${(counts[s] / total) * 100}%;background:var(${STATUS_COLOR_VAR[s]})" title="${s} ${counts[s]}"></span>`)
    .join('');
  const legend = order
    .filter((s) => counts[s])
    .map((s) => `<span class="lg"><span class="sw" style="background:var(${STATUS_COLOR_VAR[s]})"></span>${s} ${counts[s]}</span>`)
    .join('');
  document.getElementById('compositionRow').innerHTML = `
    <h2>규칙 15개 판정 구성(${state.jurisdictions[state.jurId].name})</h2>
    <div class="comp-bar">${bar}</div>
    <div class="comp-legend">${legend}</div>
  `;
}

function candidateOptionsHtml(ruleId, entry, chosenId) {
  if (!Array.isArray(entry.candidates) || entry.candidates.length < 2) return '';
  const options = entry.candidates
    .map((c) => `<option value="${c.id}" ${c.id === chosenId ? 'selected' : ''}>${c.label}</option>`)
    .join('');
  return `
    <div class="candidate-picker">
      <label for="cand-${ruleId}">후보값</label>
      <select id="cand-${ruleId}" data-rule="${ruleId}">${options}</select>
    </div>
  `;
}

function renderRuleList(verdicts) {
  const jur = state.jurisdictions[state.jurId];
  const html = verdicts
    .map((v) => {
      const entry = jur.rules[v.rule];
      const isOpen = state.expanded.has(v.rule);
      const chosenId =
        state.candidates[v.rule] ||
        (entry && Array.isArray(entry.candidates) ? entry.default_candidate || (entry.candidates[0] && entry.candidates[0].id) : null);
      const isRatio = v.rule === 'R01' || v.rule === 'R05';
      const show = (x) => (Array.isArray(x) ? x.join(', ') : isRatio && typeof x === 'number' ? fmtPct(x, 2) : x);
      const valueLine =
        v.value != null
          ? `<span>관측값 <b>${show(v.value)}</b>${v.approx ? ' (근사: 기타 준비자산 비중, 현금과 국채가 섞일 수 있음)' : ''}</span>`
          : '';
      const thresholdLine =
        v.threshold != null
          ? `<span>기준 <b>${show(v.threshold)}</b></span>`
          : '';
      const chosenCandidate =
        entry && Array.isArray(entry.candidates) ? entry.candidates.find((c) => c.id === chosenId) : null;
      const subText = chosenCandidate ? `${entry.requirement}, ${chosenCandidate.label}` : entry && entry.requirement;
      return `
        <article class="rule-card ${STATUS_CLASS[v.status] || ''}" data-rule="${v.rule}">
          <div class="rule-top" data-toggle="${v.rule}">
            <span class="rule-id">${v.rule}</span>
            <span class="rule-name">${RULE_TITLES[v.rule]}</span>
            <span class="badge">${v.status}</span>
          </div>
          ${subText ? `<p class="rule-sub">${subText}</p>` : ''}
          ${
            isOpen
              ? `<div class="rule-detail">
                  <div class="kv">${valueLine} ${thresholdLine}</div>
                  <div class="kv"><span>근거 <b>${v.article || '미기재'}</b></span></div>
                  <div class="kv"><span>기준시각(보고서) <b class="mono">${v.as_of || '—'}</b></span></div>
                  ${v.url ? `<div class="kv"><a href="${v.url}" target="_blank" rel="noopener">원문 열기 ↗</a></div>` : ''}
                  ${candidateOptionsHtml(v.rule, entry || {}, chosenId)}
                </div>`
              : ''
          }
        </article>
      `;
    })
    .join('');
  const list = document.getElementById('ruleList');
  list.innerHTML = html;

  list.querySelectorAll('[data-toggle]').forEach((el) => {
    el.onclick = () => {
      const id = el.dataset.toggle;
      if (state.expanded.has(id)) state.expanded.delete(id);
      else state.expanded.add(id);
      renderAll();
    };
  });
  list.querySelectorAll('select[data-rule]').forEach((sel) => {
    sel.onclick = (e) => e.stopPropagation();
    sel.onchange = (e) => {
      state.candidates[sel.dataset.rule] = sel.value;
      renderAll();
    };
  });
}

function renderAll() {
  const report = currentReport();
  const jur = state.jurisdictions[state.jurId];
  const verdicts = evaluateReport(report, jur, state.jurId === 'kr-v1' ? state.candidates : {});
  renderReportSelect();
  renderJurToggle();
  renderStats(verdicts);
  renderComposition(verdicts);
  renderRuleList(verdicts);
}

loadAll().then(renderAll).catch((err) => {
  document.getElementById('ruleList').innerHTML = `<p style="color:var(--critical)">데이터를 불러오지 못했다: ${err.message}</p>`;
  console.error(err);
});
