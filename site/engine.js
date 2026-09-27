// StableWatch 규칙 엔진. 순수 함수만 둔다.
//
// 규칙 코드는 관할권을 모른다. 임계치, 주기, 기한, 법적 상태는 전부
// jurisdictions/*.json에서 온다. 한국(KR-v1)은 규칙마다 후보값 배열을 두고,
// 화면이 고른 candidateId로 그중 하나를 골라 넣는다.
//
// 입력 필드가 report에 없으면 값을 채우지 않고 "데이터 없음"을 낸다.
// (PRD 10절 운영 원칙, graph/schema.md 상태 체계)

export const RULE_IDS = [
  'R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08',
  'R09', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15',
];

export const STATUS = {
  MET: '충족',
  UNMET: '미충족',
  CAUTION: '주의',
  NO_DATA: '데이터 없음',
  PENDING: '위임 예정',
  NOT_REGULATED: '규정 없음',
  UNRESEARCHED: '조사 미완료',
};

// ---- 날짜 유틸 ----
// ponytail: 월~금만 세는 단순 카운터. 한국 공휴일 캘린더는 반영하지 않는다.
// 공휴일 정밀도가 필요해지면 관공서공휴일규정 날짜 테이블을 추가한다.

function toUTCDate(s) {
  if (!s) return null;
  const d = new Date(s + 'T00:00:00Z');
  return Number.isNaN(d.getTime()) ? null : d;
}

export function calendarDaysBetween(fromStr, toStr) {
  const a = toUTCDate(fromStr);
  const b = toUTCDate(toStr);
  if (!a || !b) return null;
  return Math.round((b - a) / 86400000);
}

export function businessDaysBetween(fromStr, toStr) {
  const a = toUTCDate(fromStr);
  const b = toUTCDate(toStr);
  if (!a || !b) return null;
  let count = 0;
  const cur = new Date(a);
  cur.setUTCDate(cur.getUTCDate() + 1);
  while (cur <= b) {
    const day = cur.getUTCDay();
    if (day !== 0 && day !== 6) count++;
    cur.setUTCDate(cur.getUTCDate() + 1);
  }
  return count;
}

// ---- 통화 유틸 ----
// 토큰 이름에 든 통화 코드로 페그 통화를 추정한다(USDC, PYUSD→USD 등). 일반 지식이며
// 보고서별 실측 필드가 아니다. 알 수 없는 토큰은 null(데이터 없음으로 이어짐).

const PEG_PREFIXES = ['USD', 'EUR', 'HKD', 'SGD', 'KRW', 'GBP', 'JPY'];

export function inferPegCurrency(report) {
  if (report.peg_currency) return report.peg_currency;
  const token = String(report.token || '').toUpperCase();
  const hit = PEG_PREFIXES.find((p) => token.includes(p));
  return hit || null;
}

// ---- 관할권 설정에서 규칙 하나를 고른다 ----
// KR-v1처럼 candidates 배열이 있으면 candidateId로 고르고, 없으면 골라진 후보를
// entry 위에 얹는다. 없으면(고정값 관할권) entry를 그대로 쓴다.

export function resolveRuleDef(jurisdiction, ruleId, candidateId) {
  const entry = jurisdiction && jurisdiction.rules && jurisdiction.rules[ruleId];
  if (!entry) return null;
  if (!Array.isArray(entry.candidates)) return entry;
  if (entry.candidates.length === 0) return { ...entry };
  const chosen =
    entry.candidates.find((c) => c.id === candidateId) ||
    entry.candidates.find((c) => c.id === entry.default_candidate) ||
    entry.candidates[0];
  return { ...entry, ...chosen, candidates: entry.candidates, id: undefined };
}

// 규칙 코드가 공통으로 처리하는 상태: 규정 없음, 조사 미완료, 위임 예정, 부분 공백(주의).
// 이 넷은 report 값을 보지 않고도 정해진다. 나머지만 규칙별 비교로 넘어간다.
function shortCircuit(ruleDef) {
  if (!ruleDef) return STATUS.NOT_REGULATED;
  if (ruleDef.not_regulated === true) return STATUS.NOT_REGULATED;
  if (ruleDef.unresearched === true || (Array.isArray(ruleDef.candidates) && ruleDef.candidates.length === 0)) {
    return STATUS.UNRESEARCHED;
  }
  if (ruleDef.delegated === true) return STATUS.PENDING;
  if (ruleDef.partial === true) return STATUS.CAUTION;
  return null;
}

function numericVerdict(observed, threshold, comparison, mandatory) {
  const ok = comparison === 'lte' ? observed <= threshold : observed >= threshold;
  if (ok) return STATUS.MET;
  return mandatory === false ? STATUS.CAUTION : STATUS.UNMET;
}

// ---- 규칙 15개 ----
// 각 함수는 (report, ruleDef) -> {status, value, threshold} 를 낸다.
// rule과 article, url, as_of는 evaluateRule에서 공통으로 붙인다.

function ruleCoverage(report, rd) {
  // R01 커버리지 = 준비자산 공정가치 / 발행잔액 ≥ 임계치
  const observed =
    report.coverage_ratio ?? report.coverage ??
    (report.fair_value != null && report.circulation ? report.fair_value / report.circulation : null);
  if (observed == null) return { status: STATUS.NO_DATA };
  if (rd.threshold == null) return { status: STATUS.NOT_REGULATED };
  return {
    status: numericVerdict(observed, rd.threshold, rd.comparison || 'gte', rd.mandatory),
    value: observed,
    threshold: rd.threshold,
  };
}

function ruleAssetTypes(report, rd) {
  // R02 허용 자산 종류: report.asset_types가 rd.allowed의 부분집합인지
  if (!Array.isArray(report.asset_types) || report.asset_types.length === 0) return { status: STATUS.NO_DATA };
  if (!Array.isArray(rd.allowed)) return { status: STATUS.NOT_REGULATED };
  const disallowed = report.asset_types.filter((t) => !rd.allowed.includes(t));
  return {
    status: disallowed.length === 0 ? STATUS.MET : STATUS.UNMET,
    value: report.asset_types,
    threshold: rd.allowed,
  };
}

function ruleTreasuryMaturity(report, rd) {
  // R03 국채 잔존만기 상한(일)
  const observed = report.treasury_max_maturity_days;
  if (observed == null) return { status: STATUS.NO_DATA };
  if (rd.threshold_days == null) return { status: STATUS.NOT_REGULATED };
  return {
    status: numericVerdict(observed, rd.threshold_days, 'lte', rd.mandatory),
    value: observed,
    threshold: rd.threshold_days,
  };
}

function ruleRepoMaturity(report, rd) {
  // R04 레포 만기(일). overnight은 1일로 취급
  const observed = report.repo_max_maturity_days;
  if (observed == null) return { status: STATUS.NO_DATA };
  if (rd.threshold_days == null) return { status: STATUS.NOT_REGULATED };
  return {
    status: numericVerdict(observed, rd.threshold_days, 'lte', rd.mandatory),
    value: observed,
    threshold: rd.threshold_days,
  };
}

function ruleCashRatio(report, rd) {
  // R05 현금성(은행 예치) 최저 비율.
  // 파서마다 현금 항목 이름이 다르다. components.cash(Paxos류, 현금만 명시)가 있으면
  // 그걸 쓰고, 없으면 components.other/fair_value(Circle류, 현금+국채가 섞인 근사치)를
  // 쓴다. 한국공시안_v1 D-05가 같은 방식으로 M4를 측정했다(파서가 현금만 분리하면
  // 이 근사는 폐기한다).
  let observed = report.cash_ratio;
  let approx = false;
  if (observed == null && report.components && report.fair_value) {
    if (report.components.cash != null) {
      observed = report.components.cash / report.fair_value;
    } else if (report.components.other != null) {
      observed = report.components.other / report.fair_value;
      approx = true;
    }
  }
  if (observed == null) return { status: STATUS.NO_DATA };
  if (rd.threshold == null) return { status: STATUS.NOT_REGULATED };
  return {
    status: numericVerdict(observed, rd.threshold, 'gte', rd.mandatory),
    value: observed,
    threshold: rd.threshold,
    approx,
  };
}

function ruleCurrencyMatch(report, rd) {
  // R06 준비자산 통화 일치. reserve_currency는 파서가 원문에서 읽은 표시 통화다.
  // 없으면 채우지 않고 데이터 없음(페그 통화와 같다고 가정하면 비교가 아니라 저장값 반환이 된다).
  const peg = inferPegCurrency(report);
  const reserve = report.reserve_currency;
  if (!peg || !reserve) return { status: STATUS.NO_DATA };
  if (!rd.required_currency) return { status: STATUS.NOT_REGULATED };
  const required = rd.required_currency === 'same_as_peg' ? peg : rd.required_currency;
  return {
    status: reserve === required ? STATUS.MET : STATUS.UNMET,
    value: reserve,
    threshold: required,
  };
}

function ruleDisclosureCadence(report, rd) {
  // R07 공개 주기(일 단위로 환산). 보고서 자신이 밝힌 공개 주기가 있어야 비교한다.
  const observed = report.disclosure_cadence_days;
  if (observed == null) return { status: STATUS.NO_DATA };
  if (rd.cadence_days == null) return { status: STATUS.NOT_REGULATED };
  return {
    status: numericVerdict(observed, rd.cadence_days, 'lte', rd.mandatory),
    value: observed,
    threshold: rd.cadence_days,
  };
}

// 보증 수준. 합의된 절차(보증 없음) < 검토(제한적 보증) < examination, 합리적 확신, 감사.
// attestation은 HKMA와 MAS가 쓰는 상위어라 제한적 보증 이상이면 된다고 본다.
// 수준이 같아도 종류가 다르면(examination과 audit) 대상 문서가 달라 주의로 낸다.
const ASSURANCE_LEVEL = {
  agreed_upon_procedures: 0,
  review: 1, quarterly_review: 1, 'limited assurance': 1, attestation: 1,
  examination: 2, 'reasonable assurance': 2, audit: 2,
};

function ruleVerificationLevel(report, rd) {
  // R08 검증 수준. 요구 목록 중 하나라도 같은 종류이거나 더 높은 수준이면 충족.
  const observed = report.attestation && report.attestation.type;
  if (!observed) return { status: STATUS.NO_DATA };
  if (!Array.isArray(rd.verification_types)) return { status: STATUS.NOT_REGULATED };
  const lv = ASSURANCE_LEVEL[observed];
  const verdicts = rd.verification_types.map((req) => {
    const rl = ASSURANCE_LEVEL[req];
    if (req === observed || (lv != null && rl != null && lv > rl)) return STATUS.MET;
    if (lv != null && rl != null && lv === rl) return STATUS.CAUTION;
    return STATUS.UNMET;
  });
  const status = verdicts.includes(STATUS.MET) ? STATUS.MET
    : verdicts.includes(STATUS.CAUTION) ? STATUS.CAUTION : STATUS.UNMET;
  return { status, value: observed, threshold: rd.verification_types };
}

function timeBucket(timeStr) {
  const s = String(timeStr || '').toLowerCase();
  if (s.includes('23:59') || s.includes('24:00') || s.includes('자정')) return 'midnight';
  if (s.includes('12:00') || s.includes('정오')) return 'noon';
  return null;
}

function ruleAsOfTime(report, rd) {
  // R09 검증 기준시각. 시각을 자정/정오/그 외로 단순화해서 비교한다.
  // 관할권 값이 "기간 말 영업일" 같은 영업일 지정형이면 시각 비교가 원천적으로
  // 애매하므로 데이터가 있어도 "주의"로 낸다.
  const observedRaw = report.as_of_time;
  if (!observedRaw) return { status: STATUS.NO_DATA };
  if (!rd.time_bucket) return { status: STATUS.NOT_REGULATED };
  if (rd.time_bucket === 'unspecified_business_day') {
    return { status: STATUS.CAUTION, value: observedRaw, threshold: rd.time_label || rd.time_bucket };
  }
  const observed = timeBucket(observedRaw);
  return {
    status: observed === rd.time_bucket ? STATUS.MET : STATUS.UNMET,
    value: observedRaw,
    threshold: rd.time_label || rd.time_bucket,
  };
}

function ruleDisclosureDeadline(report, rd) {
  // R10 공개 기한: 기준일(as_of)에서 검증 서명일까지 걸린 날을 관할권 기한과 비교한다.
  if (!report.as_of || !(report.attestation && report.attestation.signed)) return { status: STATUS.NO_DATA };
  if (rd.deadline_days == null) return { status: STATUS.NOT_REGULATED };
  const elapsed =
    rd.unit === 'business_days'
      ? businessDaysBetween(report.as_of, report.attestation.signed)
      : calendarDaysBetween(report.as_of, report.attestation.signed);
  if (elapsed == null) return { status: STATUS.NO_DATA };
  return {
    status: numericVerdict(elapsed, rd.deadline_days, 'lte', rd.mandatory),
    value: elapsed,
    threshold: rd.deadline_days,
  };
}

function ruleBooleanRequirement(field) {
  // rd.expected는 그 필드가 규정을 지키려면 가져야 할 값이다.
  // R11, R12, R15는 "공개했는가"라 expected:true. R14는 "이자를 지급했는가"라
  // 금지를 지키려면 expected:false여야 한다(공개 요구가 아니라 금지 규정).
  return (report, rd) => {
    const observed = report[field];
    if (observed == null) return { status: STATUS.NO_DATA };
    if (rd.expected == null) return { status: STATUS.NOT_REGULATED };
    return {
      status: observed === rd.expected ? STATUS.MET : STATUS.UNMET,
      value: observed,
      threshold: rd.expected,
    };
  };
}

function ruleRedemptionDays(report, rd) {
  // R13 환매 조건(기한). 액면과 수수료 조건은 article 텍스트로만 다루고, 숫자 비교는 기한만 한다.
  const observed = report.redemption_days;
  if (observed == null) return { status: STATUS.NO_DATA };
  if (rd.max_days == null) return { status: STATUS.NOT_REGULATED };
  return {
    status: numericVerdict(observed, rd.max_days, 'lte', rd.mandatory),
    value: observed,
    threshold: rd.max_days,
  };
}

const RULE_FUNCS = {
  R01: ruleCoverage,
  R02: ruleAssetTypes,
  R03: ruleTreasuryMaturity,
  R04: ruleRepoMaturity,
  R05: ruleCashRatio,
  R06: ruleCurrencyMatch,
  R07: ruleDisclosureCadence,
  R08: ruleVerificationLevel,
  R09: ruleAsOfTime,
  R10: ruleDisclosureDeadline,
  R11: ruleBooleanRequirement('circulation_formula_disclosed'),
  R12: ruleBooleanRequirement('custodian_disclosure'),
  R13: ruleRedemptionDays,
  R14: ruleBooleanRequirement('interest_paid'),
  R15: ruleBooleanRequirement('management_certification'),
};

/**
 * 규칙 하나를 판정한다.
 * @param {string} ruleId R01~R15
 * @param {object} report 파싱된 보고서 객체(data/reports.json의 원소)
 * @param {object} jurisdiction 관할권 설정(jurisdictions/*.json)
 * @param {string} [candidateId] KR-v1처럼 후보값 배열이 있을 때 고를 후보 id
 * @returns {{rule:string, status:string, value:*, threshold:*, article:?string, url:?string, as_of:?string}}
 */
export function evaluateRule(ruleId, report, jurisdiction, candidateId) {
  const ruleDef = resolveRuleDef(jurisdiction, ruleId, candidateId);
  const forced = shortCircuit(ruleDef);
  const fn = RULE_FUNCS[ruleId];
  const result = forced ? { status: forced } : fn(report, ruleDef || {});
  return {
    rule: ruleId,
    status: result.status,
    value: result.value ?? null,
    threshold: result.threshold ?? null,
    approx: result.approx === true,
    article: (ruleDef && ruleDef.article) || null,
    url: (ruleDef && ruleDef.url) || null,
    as_of: report.as_of || null,
  };
}

/**
 * 보고서 하나를 관할권 설정으로 규칙 15개 전부 판정한다.
 * @param {object} report
 * @param {object} jurisdiction
 * @param {Object<string,string>} [candidateSelections] 규칙ID -> 후보 id (KR-v1)
 */
export function evaluateReport(report, jurisdiction, candidateSelections = {}) {
  return RULE_IDS.map((id) => evaluateRule(id, report, jurisdiction, candidateSelections[id]));
}
