// node --test tests/engine.test.mjs 로 돈다. 프레임워크 없이 node:test만 쓴다.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { evaluateRule, evaluateReport, STATUS } from '../site/engine.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

function readJurisdiction(id) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, 'site/jurisdictions', `${id}.json`), 'utf8'));
}

function jur(ruleId, ruleDef) {
  return { rules: { [ruleId]: ruleDef } };
}

// ---- 규칙 15개: 충족, 미충족, 데이터 없음 각각 한 케이스 ----
// 어느 규칙도 구조상 미충족이 불가능하지 않아 전부 세 상태를 낸다.

test('R01 커버리지: 충족/미충족/데이터없음', () => {
  const rd = { comparison: 'gte', threshold: 1.0 };
  assert.equal(evaluateRule('R01', { fair_value: 105, circulation: 100 }, jur('R01', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R01', { fair_value: 95, circulation: 100 }, jur('R01', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R01', {}, jur('R01', rd)).status, STATUS.NO_DATA);
});

test('R02 허용 자산 종류: 충족/미충족/데이터없음', () => {
  const rd = { allowed: ['cash', 'treasury'] };
  assert.equal(evaluateRule('R02', { asset_types: ['cash', 'treasury'] }, jur('R02', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R02', { asset_types: ['cash', 'crypto'] }, jur('R02', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R02', {}, jur('R02', rd)).status, STATUS.NO_DATA);
});

test('R03 국채 잔존만기 상한: 충족/미충족/데이터없음', () => {
  const rd = { threshold_days: 93 };
  assert.equal(evaluateRule('R03', { treasury_max_maturity_days: 60 }, jur('R03', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R03', { treasury_max_maturity_days: 120 }, jur('R03', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R03', {}, jur('R03', rd)).status, STATUS.NO_DATA);
});

test('R04 레포 만기: 충족/미충족/데이터없음', () => {
  const rd = { threshold_days: 1 };
  assert.equal(evaluateRule('R04', { repo_max_maturity_days: 1 }, jur('R04', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R04', { repo_max_maturity_days: 7 }, jur('R04', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R04', {}, jur('R04', rd)).status, STATUS.NO_DATA);
});

test('R05 현금성 최저 비율: 충족/미충족/데이터없음', () => {
  const rd = { comparison: 'gte', threshold: 0.3 };
  assert.equal(evaluateRule('R05', { cash_ratio: 0.35 }, jur('R05', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R05', { cash_ratio: 0.1 }, jur('R05', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R05', {}, jur('R05', rd)).status, STATUS.NO_DATA);
});

test('R05는 fair_value/components.other로 현금성 비율을 근사한다', () => {
  const rd = { comparison: 'gte', threshold: 0.1 };
  const r = evaluateRule('R05', { fair_value: 100, components: { other: 15 } }, jur('R05', rd));
  assert.equal(r.status, STATUS.MET);
  assert.ok(Math.abs(r.value - 0.15) < 1e-9);
});

test('R06 준비자산 통화 일치: 충족/미충족/데이터없음', () => {
  const rd = { required_currency: 'same_as_peg' };
  assert.equal(evaluateRule('R06', { token: 'USDX', reserve_currency: 'USD' }, jur('R06', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R06', { token: 'USDX', reserve_currency: 'EUR' }, jur('R06', rd)).status, STATUS.UNMET);
  // 원문에서 표시 통화를 못 읽었으면 페그 통화로 채우지 않는다
  assert.equal(evaluateRule('R06', { token: 'USDX' }, jur('R06', rd)).status, STATUS.NO_DATA);
});

test('R07 공개 주기: 충족/미충족/데이터없음', () => {
  const rd = { cadence_days: 31 };
  assert.equal(evaluateRule('R07', { disclosure_cadence_days: 30 }, jur('R07', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R07', { disclosure_cadence_days: 90 }, jur('R07', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R07', {}, jur('R07', rd)).status, STATUS.NO_DATA);
});

test('R08 검증 수준: 충족/미충족/데이터없음', () => {
  const ex = { attestation: { type: 'examination' } };
  assert.equal(evaluateRule('R08', ex, jur('R08', { verification_types: ['examination'] })).status, STATUS.MET);
  // examination(합리적 확신)은 분기 검토(제한적 보증)보다 높아 충족
  assert.equal(evaluateRule('R08', ex, jur('R08', { verification_types: ['quarterly_review'] })).status, STATUS.MET);
  // 같은 수준이지만 대상이 다른 감사 요구에는 주의
  assert.equal(evaluateRule('R08', ex, jur('R08', { verification_types: ['audit'] })).status, STATUS.CAUTION);
  assert.equal(evaluateRule('R08', { attestation: { type: 'review' } }, jur('R08', { verification_types: ['examination'] })).status, STATUS.UNMET);
  assert.equal(evaluateRule('R08', {}, jur('R08', { verification_types: ['examination'] })).status, STATUS.NO_DATA);
});

test('R09 검증 기준시각: 충족/미충족/데이터없음', () => {
  const rd = { time_bucket: 'noon', time_label: '정오' };
  assert.equal(evaluateRule('R09', { as_of_time: '12:00 ET' }, jur('R09', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R09', { as_of_time: '23:59 UTC' }, jur('R09', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R09', {}, jur('R09', rd)).status, STATUS.NO_DATA);
});

test('R09 영업일 지정형(HK류)은 데이터가 있어도 주의로 낸다', () => {
  const rd = { time_bucket: 'unspecified_business_day', time_label: '기간 말 영업일' };
  assert.equal(evaluateRule('R09', { as_of_time: '17:00 HKT' }, jur('R09', rd)).status, STATUS.CAUTION);
});

test('R10 공개 기한: 충족/미충족/데이터없음', () => {
  const rd = { deadline_days: 30, unit: 'calendar_days' };
  assert.equal(
    evaluateRule('R10', { as_of: '2026-01-01', attestation: { signed: '2026-01-20' } }, jur('R10', rd)).status,
    STATUS.MET,
  );
  assert.equal(
    evaluateRule('R10', { as_of: '2026-01-01', attestation: { signed: '2026-03-01' } }, jur('R10', rd)).status,
    STATUS.UNMET,
  );
  assert.equal(evaluateRule('R10', {}, jur('R10', rd)).status, STATUS.NO_DATA);
});

test('R11 발행잔액 산식 공개: 충족/미충족/데이터없음', () => {
  const rd = { expected: true };
  assert.equal(evaluateRule('R11', { circulation_formula_disclosed: true }, jur('R11', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R11', { circulation_formula_disclosed: false }, jur('R11', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R11', {}, jur('R11', rd)).status, STATUS.NO_DATA);
});

test('R12 수탁기관과 위치 공개: 충족/미충족/데이터없음', () => {
  const rd = { expected: true };
  assert.equal(evaluateRule('R12', { custodian_disclosure: true }, jur('R12', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R12', { custodian_disclosure: false }, jur('R12', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R12', {}, jur('R12', rd)).status, STATUS.NO_DATA);
});

test('R13 환매 기한: 충족/미충족/데이터없음', () => {
  const rd = { max_days: 3, unit: 'business_days' };
  assert.equal(evaluateRule('R13', { redemption_days: 2 }, jur('R13', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R13', { redemption_days: 10 }, jur('R13', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R13', {}, jur('R13', rd)).status, STATUS.NO_DATA);
});

test('R14 이자 지급 금지: 충족/미충족/데이터없음', () => {
  const rd = { expected: false };
  assert.equal(evaluateRule('R14', { interest_paid: false }, jur('R14', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R14', { interest_paid: true }, jur('R14', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R14', {}, jur('R14', rd)).status, STATUS.NO_DATA);
});

test('R15 경영진 인증: 충족/미충족/데이터없음', () => {
  const rd = { expected: true };
  assert.equal(evaluateRule('R15', { management_certification: true }, jur('R15', rd)).status, STATUS.MET);
  assert.equal(evaluateRule('R15', { management_certification: false }, jur('R15', rd)).status, STATUS.UNMET);
  assert.equal(evaluateRule('R15', {}, jur('R15', rd)).status, STATUS.NO_DATA);
});

// ---- 공통 상태 처리(규정 없음, 위임 예정, 주의, 조사 미완료) ----

test('규칙 항목이 아예 없으면 규정 없음', () => {
  assert.equal(evaluateRule('R01', { fair_value: 100, circulation: 100 }, jur('R99', {})).status, STATUS.NOT_REGULATED);
});

test('not_regulated 플래그는 데이터가 있어도 규정 없음으로 낸다', () => {
  const rd = { comparison: 'gte', threshold: 1.0, not_regulated: true };
  assert.equal(evaluateRule('R01', { fair_value: 100, circulation: 100 }, jur('R01', rd)).status, STATUS.NOT_REGULATED);
});

test('delegated 플래그는 위임 예정을 낸다(관할권 무관)', () => {
  const rd = { comparison: 'gte', threshold: 0.3, delegated: true };
  assert.equal(evaluateRule('R05', { cash_ratio: 0.5 }, jur('R05', rd)).status, STATUS.PENDING);
});

test('partial 플래그는 주의를 낸다', () => {
  const rd = { expected: true, partial: true };
  assert.equal(evaluateRule('R11', { circulation_formula_disclosed: true }, jur('R11', rd)).status, STATUS.CAUTION);
});

test('candidates가 빈 배열이면 조사 미완료(R04 공백 후보 패턴)', () => {
  const rd = { candidates: [] };
  assert.equal(evaluateRule('R04', { repo_max_maturity_days: 1 }, jur('R04', rd)).status, STATUS.UNRESEARCHED);
});

test('mandatory:false는 안전항이라 미충족 대신 주의를 낸다', () => {
  const rd = { comparison: 'gte', threshold: 0.3, mandatory: false };
  assert.equal(evaluateRule('R05', { cash_ratio: 0.1 }, jur('R05', rd)).status, STATUS.CAUTION);
  assert.equal(evaluateRule('R05', { cash_ratio: 0.5 }, jur('R05', rd)).status, STATUS.MET);
});

// ---- 같은 보고서가 관할권에 따라 다른 판정을 받는다 ----

test('KR-v1 R06: 법안(연동 통화와 동일)은 충족, 원화 전제 공시안은 미충족', () => {
  const report = { token: 'USDC', reserve_currency: 'USD' };
  const kr = readJurisdiction('kr-v1');
  assert.equal(evaluateRule('R06', report, readJurisdiction('us')).status, STATUS.MET);
  assert.equal(evaluateRule('R06', report, kr, 'bill').status, STATUS.MET);
  assert.equal(evaluateRule('R06', report, kr, 'proposal').status, STATUS.UNMET);
});

test('같은 보고서, 관할권 두 곳에서 R10 판정이 갈린다(미국 충족, 한국 법안 미충족)', () => {
  const report = { as_of: '2026-07-31', attestation: { signed: '2026-08-27' } };
  const kr = readJurisdiction('kr-v1');
  assert.equal(evaluateRule('R10', report, readJurisdiction('us')).status, STATUS.MET);
  assert.equal(evaluateRule('R10', report, readJurisdiction('hk')).status, STATUS.MET);
  assert.equal(evaluateRule('R10', report, kr, 'bill').status, STATUS.UNMET);
  assert.equal(evaluateRule('R10', report, kr, 'proposal').status, STATUS.MET);
});

// ---- 한국 후보값을 바꾸면 판정이 바뀐다 ----

test('KR-v1 R05 후보값을 바꾸면 위임 예정 -> 미충족 -> 충족으로 바뀐다', () => {
  const report = { fair_value: 100, components: { other: 15 } }; // 근사 현금성 비율 15%
  const kr = readJurisdiction('kr-v1');
  assert.equal(evaluateRule('R05', report, kr, 'bill').status, STATUS.PENDING);
  assert.equal(evaluateRule('R05', report, kr, 'foreign_ref').status, STATUS.UNMET); // 30% 요구, 15% 실측
  assert.equal(evaluateRule('R05', report, kr, 'proposal').status, STATUS.MET); // 15% 요구, 15% 실측
});

test('KR-v1 R09 후보값을 바꾸면 주의 -> 충족으로 바뀐다', () => {
  const report = { as_of_time: '23:59 UTC' };
  const kr = readJurisdiction('kr-v1');
  assert.equal(evaluateRule('R09', report, kr, 'bill').status, STATUS.CAUTION);
  assert.equal(evaluateRule('R09', report, kr, 'proposal').status, STATUS.MET);
});

// ---- evaluateReport는 규칙 15개를 전부 낸다 ----

test('evaluateReport는 RULE_IDS 순서대로 15개를 낸다', () => {
  const us = readJurisdiction('us');
  const report = { fair_value: 100, circulation: 100 };
  const verdicts = evaluateReport(report, us);
  assert.equal(verdicts.length, 15);
  assert.deepEqual(verdicts.map((v) => v.rule), [
    'R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08',
    'R09', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15',
  ]);
});
