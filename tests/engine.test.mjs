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

// ---- R02 kinds 대응표 ----
const KINDS = {
  bank_deposit: { verdict: 'allowed', code: 'bank_deposit', same_currency: true },
  treasury_bill: { verdict: 'allowed', code: 'tb', max_days: 93, same_currency: true },
  bitcoin: { verdict: 'not_allowed', code: null },
  term_deposit: { verdict: 'unclear', code: null },
};
const kindsRd = { allowed: ['bank_deposit', 'tb'], kinds: KINDS };
const h = (kind, extra = {}) => ({ kind, amount: 100, currency: 'USD', maturity_max_days: null, ...extra });
const r02 = (holdings, token = 'USDX') => evaluateRule('R02', { token, holdings }, jur('R02', kindsRd));

test('R02 대응표: 허용만 있으면 충족, settlement와 0 이하 줄은 건너뛴다', () => {
  const r = r02([h('bank_deposit'), h('settlement', { amount: -5 }), h('bitcoin', { amount: 0 })]);
  assert.equal(r.status, STATUS.MET);
  assert.deepEqual(r.value.map((v) => [v.kind, v.verdict]), [['bank_deposit', 'allowed']]);
});

test('R02 대응표: 허용 밖이 하나라도 있으면 미충족', () => {
  const r = r02([h('bank_deposit'), h('bitcoin'), h('term_deposit')]);
  assert.equal(r.status, STATUS.UNMET);
  assert.equal(r.value.length, 3);
});

test('R02 대응표: 해석 필요(unclear)와 표에 없는 kind는 주의', () => {
  assert.equal(r02([h('bank_deposit'), h('term_deposit')]).status, STATUS.CAUTION);
  assert.equal(r02([h('bank_deposit'), h('mystery_asset')]).status, STATUS.CAUTION);
});

test('R02 대응표: 만기 조건(초과는 미충족, 만기 없음은 주의)', () => {
  assert.equal(r02([h('treasury_bill', { maturity_max_days: 90 })]).status, STATUS.MET);
  assert.equal(r02([h('treasury_bill', { maturity_max_days: 120 })]).status, STATUS.UNMET);
  assert.equal(r02([h('treasury_bill', { maturity_max_days: null })]).status, STATUS.CAUTION);
});

test('R02 대응표: 통화 조건(페그와 다르면 미충족, 페그를 모르면 주의)', () => {
  assert.equal(r02([h('bank_deposit', { currency: 'EUR' })]).status, STATUS.UNMET);
  assert.equal(r02([h('bank_deposit', { currency: 'USD' })], 'FOO').status, STATUS.CAUTION);
});

test('R02 대응표: 같은 kind 여러 줄은 합치고 가장 나쁜 판정을 쓴다', () => {
  const r = r02([h('treasury_bill', { maturity_max_days: 10 }), h('treasury_bill', { maturity_max_days: 200 })]);
  assert.equal(r.status, STATUS.UNMET);
  assert.equal(r.value.length, 1);
  assert.equal(r.value[0].amount, 200);
});

test('R02 대응표가 있고 holdings가 없으면 보고서에 없음', () => {
  assert.equal(evaluateRule('R02', { asset_types: ['cash'] }, jur('R02', kindsRd)).status, STATUS.NO_DATA);
});

test('R03, R04: field_notes가 not_applicable이면 해당 없음, 값이 null이면 보고서에 없음', () => {
  const na = (f) => ({ field_notes: { [f]: { state: 'not_applicable' } } });
  assert.equal(STATUS.NOT_APPLICABLE, '해당 없음');
  assert.equal(STATUS.NO_DATA, '보고서에 없음');
  assert.equal(evaluateRule('R03', na('treasury_max_maturity_days'), jur('R03', { threshold_days: 93 })).status, STATUS.NOT_APPLICABLE);
  assert.equal(evaluateRule('R04', na('repo_max_maturity_days'), jur('R04', { threshold_days: 1 })).status, STATUS.NOT_APPLICABLE);
  const nf = { field_notes: { treasury_max_maturity_days: { state: 'not_in_report' } }, treasury_max_maturity_days: null };
  assert.equal(evaluateRule('R03', nf, jur('R03', { threshold_days: 93 })).status, STATUS.NO_DATA);
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

test('KR-v1 R06: 법안(연동 통화와 동일)은 충족', () => {
  const report = { token: 'USDC', reserve_currency: 'USD' };
  const kr = readJurisdiction('kr-v1');
  assert.equal(evaluateRule('R06', report, readJurisdiction('us')).status, STATUS.MET);
  assert.equal(evaluateRule('R06', report, kr, 'bill').status, STATUS.MET);
});

test('같은 보고서, 관할권 두 곳에서 R10 판정이 갈린다(미국 충족, 한국 법안 미충족)', () => {
  const report = { as_of: '2026-07-31', attestation: { signed: '2026-08-27' } };
  const kr = readJurisdiction('kr-v1');
  assert.equal(evaluateRule('R10', report, readJurisdiction('us')).status, STATUS.MET);
  assert.equal(evaluateRule('R10', report, readJurisdiction('hk')).status, STATUS.MET);
  assert.equal(evaluateRule('R10', report, kr, 'bill').status, STATUS.UNMET);
});

// ---- 한국 후보값을 바꾸면 판정이 바뀐다 ----

test('KR-v1 R05 후보값을 바꾸면 위임 예정 -> 미충족 -> 충족으로 바뀐다', () => {
  const report = { fair_value: 100, components: { other: 15 } }; // 근사 현금성 비율 15%
  const kr = readJurisdiction('kr-v1');
  assert.equal(evaluateRule('R05', report, kr, 'bill').status, STATUS.PENDING);
  assert.equal(evaluateRule('R05', report, kr, 'foreign_ref').status, STATUS.UNMET); // 30% 요구, 15% 실측
  assert.equal(evaluateRule('R05', { fair_value: 100, components: { other: 30 } }, kr, 'foreign_ref').status, STATUS.MET); // 30% 요구, 30% 실측
});

test('은행 예금을 나누지 않은 보고서는 R05를 근사하지 않고 데이터 없음', () => {
  const report = { fair_value: 100, components: { cash: null, other: 90, treasury: 10 }, flags: { cash_is_bank_deposit: false } };
  assert.equal(evaluateRule('R05', report, readJurisdiction('kr-v1'), 'foreign_ref').status, STATUS.NO_DATA);
});

test('KR-v1 R13 법안 값마다(3일, 5일, 10일) 후보를 바꾸면 미충족 -> 충족으로 바뀐다', () => {
  const report = { redemption_days: 5 };
  const kr = readJurisdiction('kr-v1');
  assert.equal(evaluateRule('R13', report, kr, 'bill').status, STATUS.UNMET);
  assert.equal(evaluateRule('R13', report, kr, 'bill_5').status, STATUS.MET);
  assert.equal(evaluateRule('R13', report, kr, 'bill_10').status, STATUS.MET);
});

test('KR-v1 R08 법안 검토 3건과 감사 6건 후보로 판정이 갈린다', () => {
  const report = { attestation: { type: 'examination' } };
  const kr = readJurisdiction('kr-v1');
  assert.equal(evaluateRule('R08', report, kr, 'bill').status, STATUS.MET);
  assert.equal(evaluateRule('R08', report, kr, 'bill_audit').status, STATUS.CAUTION);
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

test('일본(jp.json)은 보고서 전부 규칙 15개를 판정한다', () => {
  const jp = readJurisdiction('jp');
  assert.equal(jp.id, 'jp');
  const { reports } = JSON.parse(fs.readFileSync(path.join(ROOT, 'site/data/reports.json'), 'utf8'));
  assert.equal(reports.length, 273); // site/data/reports.json 실제 수
  reports.forEach((r) => assert.equal(evaluateReport(r, jp).length, 15));
  const by = Object.fromEntries(evaluateReport(reports[0], jp).map((v) => [v.rule, v.status]));
  assert.equal(by.R04, STATUS.NOT_REGULATED); // 못 찾은 규칙은 값을 만들지 않고 규정 없음
  assert.equal(by.R03, STATUS.PENDING); // 원문 단위가 월이라 일수로 바꾸지 않음
  assert.equal(by.R07, STATUS.CAUTION); // 조건부 공표는 주의
});
