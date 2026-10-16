# coding=utf-8
# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FiNER-139: A Financial Numeric Entity Recognition dataset"""


import datasets
import json
import os

logger = datasets.logging.get_logger(__name__)

_CITATION = """@inproceedings{loukas-etal-2022-finer,
    title = "{FiNER: Financial Numeric Entity Recognition for XBRL Tagging}",
    author = "Loukas, Lefteris  and
      Fergadiotis, Manos  and
      Chalkidis, Ilias and
      Spyropoulou, Eirini and
      Malakasiotis, Prodromos  and
      Androutsopoulos, Ion and
      Paliouras George",
    booktitle = "Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics",
    month = "may",
    year = "2022",
    publisher = "Association for Computational Linguistics",
}"""

_DESCRIPTION = """
FiNER-139 is a named entity recognition dataset consisting of 10K annual 
and quarterly English reports (filings) of publicly traded companies 
downloaded from the U.S. Securities and Exchange Commission (SEC) 
annotated with 139 XBRL tags in the IOB2 format.
"""

_DATA_URL = "finer139.zip"

_HOMEPAGE = "http://nlp.cs.aueb.gr/"

_VERSION = "1.0.0"

_LABELS = [
    "O",
    "B-AccrualForEnvironmentalLossContingencies",
    "B-AcquiredFiniteLivedIntangibleAssetsWeightedAverageUsefulLife",
    "I-AcquiredFiniteLivedIntangibleAssetsWeightedAverageUsefulLife",
    "B-AllocatedShareBasedCompensationExpense",
    "B-AmortizationOfFinancingCosts",
    "B-AmortizationOfIntangibleAssets",
    "I-AmortizationOfIntangibleAssets",
    "B-AntidilutiveSecuritiesExcludedFromComputationOfEarningsPerShareAmount",
    "I-AntidilutiveSecuritiesExcludedFromComputationOfEarningsPerShareAmount",
    "B-AreaOfRealEstateProperty",
    "I-AreaOfRealEstateProperty",
    "B-AssetImpairmentCharges",
    "B-BusinessAcquisitionEquityInterestsIssuedOrIssuableNumberOfSharesIssued",
    "B-BusinessAcquisitionPercentageOfVotingInterestsAcquired",
    "I-BusinessAcquisitionPercentageOfVotingInterestsAcquired",
    "B-BusinessCombinationAcquisitionRelatedCosts",
    "B-BusinessCombinationConsiderationTransferred1",
    "B-BusinessCombinationContingentConsiderationLiability",
    "B-BusinessCombinationRecognizedIdentifiableAssetsAcquiredAndLiabilitiesAssumedIntangibleAssetsOtherThanGoodwill",
    "B-BusinessCombinationRecognizedIdentifiableAssetsAcquiredAndLiabilitiesAssumedIntangibles",
    "B-CapitalizedContractCostAmortization",
    "B-CashAndCashEquivalentsFairValueDisclosure",
    "B-ClassOfWarrantOrRightExercisePriceOfWarrantsOrRights1",
    "B-CommonStockCapitalSharesReservedForFutureIssuance",
    "B-CommonStockDividendsPerShareDeclared",
    "B-CommonStockParOrStatedValuePerShare",
    "B-CommonStockSharesAuthorized",
    "I-CommonStockSharesAuthorized",
    "B-CommonStockSharesOutstanding",
    "B-ConcentrationRiskPercentage1",
    "B-ContractWithCustomerLiability",
    "B-ContractWithCustomerLiabilityRevenueRecognized",
    "B-CumulativeEffectOfNewAccountingPrincipleInPeriodOfAdoption",
    "B-DebtInstrumentBasisSpreadOnVariableRate1",
    "B-DebtInstrumentCarryingAmount",
    "B-DebtInstrumentConvertibleConversionPrice1",
    "B-DebtInstrumentFaceAmount",
    "I-DebtInstrumentFaceAmount",
    "B-DebtInstrumentFairValue",
    "B-DebtInstrumentInterestRateEffectivePercentage",
    "B-DebtInstrumentInterestRateStatedPercentage",
    "B-DebtInstrumentMaturityDate",
    "I-DebtInstrumentMaturityDate",
    "B-DebtInstrumentRedemptionPricePercentage",
    "B-DebtInstrumentTerm",
    "I-DebtInstrumentTerm",
    "B-DebtInstrumentUnamortizedDiscount",
    "B-DebtWeightedAverageInterestRate",
    "B-DeferredFinanceCostsGross",
    "B-DeferredFinanceCostsNet",
    "B-DefinedBenefitPlanContributionsByEmployer",
    "B-DefinedContributionPlanCostRecognized",
    "B-Depreciation",
    "B-DerivativeFixedInterestRate",
    "B-DerivativeNotionalAmount",
    "B-DisposalGroupIncludingDiscontinuedOperationConsideration",
    "B-EffectiveIncomeTaxRateContinuingOperations",
    "B-EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate",
    "B-EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognized",
    "B-EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognizedPeriodForRecognition1",
    "I-EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognizedPeriodForRecognition1",
    "B-EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognizedShareBasedAwardsOtherThanOptions",
    "B-EmployeeServiceShareBasedCompensationTaxBenefitFromCompensationExpense",
    "B-EquityMethodInvestmentOwnershipPercentage",
    "I-EquityMethodInvestmentOwnershipPercentage",
    "B-EquityMethodInvestments",
    "B-FiniteLivedIntangibleAssetUsefulLife",
    "I-FiniteLivedIntangibleAssetUsefulLife",
    "B-GainsLossesOnExtinguishmentOfDebt",
    "B-Goodwill",
    "B-GoodwillImpairmentLoss",
    "B-GuaranteeObligationsMaximumExposure",
    "B-IncomeLossFromEquityMethodInvestments",
    "B-IncomeTaxExpenseBenefit",
    "B-InterestExpense",
    "B-InterestExpenseDebt",
    "B-LeaseAndRentalExpense",
    "B-LesseeOperatingLeaseRenewalTerm",
    "I-LesseeOperatingLeaseRenewalTerm",
    "B-LesseeOperatingLeaseTermOfContract",
    "I-LesseeOperatingLeaseTermOfContract",
    "B-LettersOfCreditOutstandingAmount",
    "B-LineOfCredit",
    "B-LineOfCreditFacilityCommitmentFeePercentage",
    "B-LineOfCreditFacilityCurrentBorrowingCapacity",
    "B-LineOfCreditFacilityInterestRateAtPeriodEnd",
    "B-LineOfCreditFacilityMaximumBorrowingCapacity",
    "B-LineOfCreditFacilityRemainingBorrowingCapacity",
    "B-LineOfCreditFacilityUnusedCapacityCommitmentFeePercentage",
    "B-LongTermDebt",
    "B-LongTermDebtFairValue",
    "B-LossContingencyAccrualAtCarryingValue",
    "B-LossContingencyDamagesSoughtValue",
    "B-LossContingencyEstimateOfPossibleLoss",
    "B-LossContingencyPendingClaimsNumber",
    "I-LossContingencyPendingClaimsNumber",
    "B-MinorityInterestOwnershipPercentageByNoncontrollingOwners",
    "B-MinorityInterestOwnershipPercentageByParent",
    "B-NumberOfOperatingSegments",
    "B-NumberOfRealEstateProperties",
    "I-NumberOfRealEstateProperties",
    "B-NumberOfReportableSegments",
    "B-OperatingLeaseCost",
    "B-OperatingLeaseExpense",
    "B-OperatingLeaseLiability",
    "B-OperatingLeasePayments",
    "B-OperatingLeaseRightOfUseAsset",
    "B-OperatingLeaseWeightedAverageDiscountRatePercent",
    "B-OperatingLeaseWeightedAverageRemainingLeaseTerm1",
    "I-OperatingLeaseWeightedAverageRemainingLeaseTerm1",
    "B-OperatingLeasesRentExpenseNet",
    "B-OperatingLossCarryforwards",
    "B-PaymentsToAcquireBusinessesGross",
    "B-PaymentsToAcquireBusinessesNetOfCashAcquired",
    "B-PreferredStockDividendRatePercentage",
    "B-PreferredStockSharesAuthorized",
    "I-PreferredStockSharesAuthorized",
    "B-ProceedsFromIssuanceOfCommonStock",
    "B-PropertyPlantAndEquipmentUsefulLife",
    "I-PropertyPlantAndEquipmentUsefulLife",
    "B-PublicUtilitiesRequestedRateIncreaseDecreaseAmount",
    "B-RelatedPartyTransactionAmountsOfTransaction",
    "I-RelatedPartyTransactionAmountsOfTransaction",
    "B-RelatedPartyTransactionExpensesFromTransactionsWithRelatedParty",
    "I-RelatedPartyTransactionExpensesFromTransactionsWithRelatedParty",
    "B-RepaymentsOfDebt",
    "B-RestructuringAndRelatedCostExpectedCost1",
    "B-RestructuringCharges",
    "B-RevenueFromContractWithCustomerExcludingAssessedTax",
    "B-RevenueFromContractWithCustomerIncludingAssessedTax",
    "B-RevenueFromRelatedParties",
    "B-RevenueRemainingPerformanceObligation",
    "B-Revenues",
    "B-SaleOfStockNumberOfSharesIssuedInTransaction",
    "I-SaleOfStockNumberOfSharesIssuedInTransaction",
    "B-SaleOfStockPricePerShare",
    "B-ShareBasedCompensation",
    "B-ShareBasedCompensationArrangementByShareBasedPaymentAwardAwardVestingPeriod1",
    "I-ShareBasedCompensationArrangementByShareBasedPaymentAwardAwardVestingPeriod1",
    "B-ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsGrantsInPeriod",
    "I-ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsGrantsInPeriod",
    "B-ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsGrantsInPeriodWeightedAverageGrantDateFairValue",
    "B-ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber",
    "B-ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsVestedInPeriodTotalFairValue",
    "B-ShareBasedCompensationArrangementByShareBasedPaymentAwardNumberOfSharesAuthorized",
    "I-ShareBasedCompensationArrangementByShareBasedPaymentAwardNumberOfSharesAuthorized",
    "B-ShareBasedCompensationArrangementByShareBasedPaymentAwardNumberOfSharesAvailableForGrant",
    "B-ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsExercisesInPeriodTotalIntrinsicValue",
    "B-ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsGrantsInPeriodGross",
    "B-ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsGrantsInPeriodWeightedAverageGrantDateFairValue",
    "B-SharePrice",
    "B-SharebasedCompensationArrangementBySharebasedPaymentAwardAwardVestingRightsPercentage",
    "I-SharebasedCompensationArrangementBySharebasedPaymentAwardAwardVestingRightsPercentage",
    "B-SharebasedCompensationArrangementBySharebasedPaymentAwardExpirationPeriod",
    "I-SharebasedCompensationArrangementBySharebasedPaymentAwardExpirationPeriod",
    "B-StockIssuedDuringPeriodSharesNewIssues",
    "I-StockIssuedDuringPeriodSharesNewIssues",
    "B-StockRepurchaseProgramAuthorizedAmount1",
    "B-StockRepurchaseProgramRemainingAuthorizedRepurchaseAmount1",
    "B-StockRepurchasedAndRetiredDuringPeriodShares",
    "B-StockRepurchasedDuringPeriodShares",
    "I-StockRepurchasedDuringPeriodShares",
    "B-SupplementalInformationForPropertyCasualtyInsuranceUnderwritersPriorYearClaimsAndClaimsAdjustmentExpense",
    "B-TreasuryStockAcquiredAverageCostPerShare",
    "B-TreasuryStockSharesAcquired",
    "I-TreasuryStockSharesAcquired",
    "B-TreasuryStockValueAcquiredCostMethod",
    "B-UnrecognizedTaxBenefits",
    "B-UnrecognizedTaxBenefitsThatWouldImpactEffectiveTaxRate",
    "I-DeferredFinanceCostsGross",
    "I-CommonStockParOrStatedValuePerShare",
    "I-LossContingencyEstimateOfPossibleLoss",
    "I-DefinedContributionPlanCostRecognized",
    "I-DebtInstrumentFairValue",
    "I-ContractWithCustomerLiabilityRevenueRecognized",
    "I-RevenueRemainingPerformanceObligation",
    "I-EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognized",
    "I-DebtInstrumentInterestRateStatedPercentage",
    "I-OperatingLossCarryforwards",
    "I-MinorityInterestOwnershipPercentageByNoncontrollingOwners",
    "I-InterestExpense",
    "I-LongTermDebt",
    "I-ShareBasedCompensation",
    "I-DebtWeightedAverageInterestRate",
    "I-DebtInstrumentCarryingAmount",
    "I-DebtInstrumentConvertibleConversionPrice1",
    "I-IncomeTaxExpenseBenefit",
    "I-ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsGrantsInPeriodWeightedAverageGrantDateFairValue",
    "I-EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognizedShareBasedAwardsOtherThanOptions",
    "I-EquityMethodInvestments",
    "I-DebtInstrumentUnamortizedDiscount",
    "I-GainsLossesOnExtinguishmentOfDebt",
    "I-ShareBasedCompensationArrangementByShareBasedPaymentAwardNumberOfSharesAvailableForGrant",
    "I-BusinessCombinationRecognizedIdentifiableAssetsAcquiredAndLiabilitiesAssumedIntangibleAssetsOtherThanGoodwill",
    "I-PreferredStockDividendRatePercentage",
    "I-RevenueFromContractWithCustomerIncludingAssessedTax",
    "I-OperatingLeaseWeightedAverageDiscountRatePercent",
    "I-LineOfCredit",
    "I-LineOfCreditFacilityMaximumBorrowingCapacity",
    "I-EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate",
    "I-LineOfCreditFacilityCommitmentFeePercentage",
    "I-BusinessCombinationConsiderationTransferred1",
    "I-CommonStockDividendsPerShareDeclared",
    "I-DebtInstrumentBasisSpreadOnVariableRate1",
    "I-DisposalGroupIncludingDiscontinuedOperationConsideration",
    "I-ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsGrantsInPeriodGross",
    "I-CommonStockSharesOutstanding",
    "I-AmortizationOfFinancingCosts",
    "I-LineOfCreditFacilityCurrentBorrowingCapacity",
    "I-TreasuryStockValueAcquiredCostMethod",
    "I-ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsNonvestedNumber",
    "I-DebtInstrumentInterestRateEffectivePercentage",
    "I-SaleOfStockPricePerShare",
    "I-CapitalizedContractCostAmortization",
    "I-RestructuringCharges",
    "I-ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsVestedInPeriodTotalFairValue",
    "I-AccrualForEnvironmentalLossContingencies",
    "I-CashAndCashEquivalentsFairValueDisclosure",
    "I-ProceedsFromIssuanceOfCommonStock",
    "I-Revenues",
    "I-BusinessCombinationRecognizedIdentifiableAssetsAcquiredAndLiabilitiesAssumedIntangibles",
    "I-LettersOfCreditOutstandingAmount",
    "I-ShareBasedCompensationArrangementByShareBasedPaymentAwardEquityInstrumentsOtherThanOptionsGrantsInPeriodWeightedAverageGrantDateFairValue",
    "I-OperatingLeasePayments",
    "I-LineOfCreditFacilityRemainingBorrowingCapacity",
    "I-PaymentsToAcquireBusinessesGross",
    "I-TreasuryStockAcquiredAverageCostPerShare",
    "I-DeferredFinanceCostsNet",
    "I-StockRepurchaseProgramAuthorizedAmount1",
    "I-InterestExpenseDebt",
    "I-ContractWithCustomerLiability",
    "I-OperatingLeaseExpense",
    "I-Depreciation",
    "I-AllocatedShareBasedCompensationExpense",
    "I-LossContingencyAccrualAtCarryingValue",
    "I-LineOfCreditFacilityUnusedCapacityCommitmentFeePercentage",
    "I-SupplementalInformationForPropertyCasualtyInsuranceUnderwritersPriorYearClaimsAndClaimsAdjustmentExpense",
    "I-OperatingLeaseLiability",
    "I-RevenueFromRelatedParties",
    "I-PaymentsToAcquireBusinessesNetOfCashAcquired",
    "I-BusinessCombinationContingentConsiderationLiability",
    "I-LossContingencyDamagesSoughtValue",
    "I-NumberOfOperatingSegments",
    "I-BusinessAcquisitionEquityInterestsIssuedOrIssuableNumberOfSharesIssued",
    "I-OperatingLeaseRightOfUseAsset",
    "I-BusinessCombinationAcquisitionRelatedCosts",
    "I-UnrecognizedTaxBenefits",
    "I-GuaranteeObligationsMaximumExposure",
    "I-RestructuringAndRelatedCostExpectedCost1",
    "I-DefinedBenefitPlanContributionsByEmployer",
    "I-OperatingLeaseCost",
    "I-DerivativeFixedInterestRate",
    "I-Goodwill",
    "I-GoodwillImpairmentLoss",
    "I-CommonStockCapitalSharesReservedForFutureIssuance",
    "I-StockRepurchasedAndRetiredDuringPeriodShares",
    "I-EmployeeServiceShareBasedCompensationTaxBenefitFromCompensationExpense",
    "I-IncomeLossFromEquityMethodInvestments",
    "I-NumberOfReportableSegments",
    "I-LongTermDebtFairValue",
    "I-RepaymentsOfDebt",
    "I-ConcentrationRiskPercentage1",
    "I-DebtInstrumentRedemptionPricePercentage",
    "I-CumulativeEffectOfNewAccountingPrincipleInPeriodOfAdoption",
    "I-SharePrice",
    "I-UnrecognizedTaxBenefitsThatWouldImpactEffectiveTaxRate",
    "I-ShareBasedCompensationArrangementByShareBasedPaymentAwardOptionsExercisesInPeriodTotalIntrinsicValue",
    "I-EffectiveIncomeTaxRateContinuingOperations",
    "I-RevenueFromContractWithCustomerExcludingAssessedTax",
    "I-StockRepurchaseProgramRemainingAuthorizedRepurchaseAmount1",
    "I-LineOfCreditFacilityInterestRateAtPeriodEnd",
    "I-ClassOfWarrantOrRightExercisePriceOfWarrantsOrRights1",
    "I-OperatingLeasesRentExpenseNet",
    "I-LeaseAndRentalExpense",
    "I-PublicUtilitiesRequestedRateIncreaseDecreaseAmount",
    "I-MinorityInterestOwnershipPercentageByParent",
    "I-AssetImpairmentCharges",
    "I-DerivativeNotionalAmount",
]


class Finer139Config(datasets.BuilderConfig):
    """BuilderConfig for FiNER-139"""
    def __init__(self, **kwargs):
        super(Finer139Config, self).__init__(version=datasets.Version(_VERSION, ""), **kwargs)


class Finer139(datasets.GeneratorBasedBuilder):
    """
    FiNER-139 is a named entity recognition dataset consisting of 10K annual
    and quarterly English reports (filings) of publicly traded companies
    downloaded from the U.S. Securities and Exchange Commission (SEC)
    annotated with 139 XBRL tags in the IOB2 format.
    """

    VERSION = datasets.Version(_VERSION)
    BUILDER_CONFIGS = [
        Finer139Config(name='finer-139', description="FiNER-139 dataset")
    ]

    def _info(self):
        features = datasets.Features(
            {
                "id": datasets.Value("int32"),
                "tokens": datasets.Sequence(datasets.Value("string")),
                "ner_tags": datasets.Sequence(datasets.features.ClassLabel(names=_LABELS))
            }
        )
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=features,
            supervised_keys=None,
            homepage=_HOMEPAGE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        data_dir = dl_manager.download_and_extract(_DATA_URL)

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"filepath": os.path.join(data_dir, "train.jsonl")},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={"filepath": os.path.join(data_dir, "validation.jsonl")},
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={"filepath": os.path.join(data_dir, "test.jsonl")},
            )
        ]

    def _generate_examples(self, filepath):
        """
        Reads line by line samples and generates examples.

        :param filepath: Path to jsonl file with line by line samples.
        """
        logger.info("⏳ Generating examples from = %s", filepath)
        with open(filepath, encoding="utf-8") as f:
            for row in f:
                data = json.loads(row)
                yield data["id"], {
                    "id": data["id"],
                    "tokens": data["tokens"],
                    "ner_tags": data["ner_tags"]
                }
