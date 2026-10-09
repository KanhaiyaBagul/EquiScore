"""
Underwriting Decision & Policy Rules Service
Evaluates transparent eligibility rules against verified financial features and outputs
unambiguous reason codes, checklist statuses, and actionable next steps.
Separates normative credit policies from model predictions.
"""

from typing import List, Dict, Any
from pydantic import BaseModel

class PolicyCriterionResult(BaseModel):
    rule_id: str
    rule_name: str
    target_threshold: str
    actual_value_formatted: str
    is_passed: bool
    status_tag: str # "PASSED", "WARNING", "FAILED"
    reason_code: str
    remediation_advice: str


class UnderwritingDecisionResult(BaseModel):
    decision_status: str # "ELIGIBLE", "CONDITIONAL_APPROVAL", "NOT_ELIGIBLE"
    status_label: str
    status_badge_color: str # "LIME", "AMBER", "RED"
    policy_version: str
    criteria_evaluated: List[PolicyCriterionResult]
    passed_count: int
    total_rules_count: int
    primary_reason_codes: List[str]
    actionable_next_steps: List[str]


def evaluate_underwriting_policy(
    monthly_gross: float,
    monthly_surplus: float,
    fhs_score: int,
    repayment_prob: float,
    debt_to_surplus_ratio: float,
    coverage_months: int,
    volatility_cv: float
) -> UnderwritingDecisionResult:
    """
    Evaluates 5 explicit lending policy criteria and returns auditable reason codes.
    """
    criteria = []

    # Rule 1: Minimum Monthly Surplus >= INR 6,000
    r1_pass = monthly_surplus >= 6000.0
    criteria.append(PolicyCriterionResult(
        rule_id="RULE_01_SURPLUS",
        rule_name="Minimum Net Monthly Surplus",
        target_threshold=">= INR 6,000/mo",
        actual_value_formatted=f"INR {monthly_surplus:,.0f}/mo",
        is_passed=r1_pass,
        status_tag="PASSED" if r1_pass else "FAILED",
        reason_code="SURPLUS_SUFFICIENT" if r1_pass else "INSUFFICIENT_NET_CASHFLOW",
        remediation_advice="Increase daily sales or lower recurring operational costs to widen operating surplus."
    ))

    # Rule 2: Financial Health Score >= 65
    r2_pass = fhs_score >= 65
    criteria.append(PolicyCriterionResult(
        rule_id="RULE_02_FHS_THRESHOLD",
        rule_name="Composite Financial Health Score",
        target_threshold=">= 65 / 100",
        actual_value_formatted=f"{fhs_score} / 100",
        is_passed=r2_pass,
        status_tag="PASSED" if r2_pass else "FAILED",
        reason_code="FHS_THRESHOLD_MET" if r2_pass else "BELOW_FHS_BENCHMARK",
        remediation_advice="Maintain consistent weekly UPI transaction frequency and build liquid reserves."
    ))

    # Rule 3: Debt Burden <= 50% of Surplus
    r3_pass = debt_to_surplus_ratio <= 0.50
    criteria.append(PolicyCriterionResult(
        rule_id="RULE_03_DEBT_RATIO",
        rule_name="Debt Service-to-Surplus Ratio",
        target_threshold="<= 50% of surplus",
        actual_value_formatted=f"{debt_to_surplus_ratio*100:.1f}%",
        is_passed=r3_pass,
        status_tag="PASSED" if r3_pass else "FAILED",
        reason_code="DEBT_BURDEN_HEALTHY" if r3_pass else "EXCESSIVE_LEVERAGE",
        remediation_advice="Pay down existing micro-loans to release monthly debt servicing obligations."
    ))

    # Rule 4: Data Coverage >= 3 Months
    r4_pass = coverage_months >= 3
    criteria.append(PolicyCriterionResult(
        rule_id="RULE_04_COVERAGE",
        rule_name="Minimum Transaction Duration",
        target_threshold=">= 3 months continuous records",
        actual_value_formatted=f"{coverage_months} months observed",
        is_passed=r4_pass,
        status_tag="PASSED" if r4_pass else "WARNING",
        reason_code="STATEMENT_DURATION_ADEQUATE" if r4_pass else "INSUFFICIENT_HISTORY_WINDOW",
        remediation_advice="Provide at least 3 to 6 months of continuous digital transaction records."
    ))

    # Rule 5: Repayment Probability >= 60%
    r5_pass = repayment_prob >= 60.0
    criteria.append(PolicyCriterionResult(
        rule_id="RULE_05_ML_RISK",
        rule_name="Alternative Credit Model Confidence",
        target_threshold=">= 60.0% probability",
        actual_value_formatted=f"{repayment_prob:.1f}% probability",
        is_passed=r5_pass,
        status_tag="PASSED" if r5_pass else "FAILED",
        reason_code="ML_CREDIT_CONFIDENCE_MET" if r5_pass else "MODEL_HIGH_RISK_FLAG",
        remediation_advice="Stabilize day-to-day sales consistency to reduce model cashflow volatility penalties."
    ))

    passed_count = sum(1 for c in criteria if c.is_passed)
    total_count = len(criteria)

    # Determine overall status
    if passed_count == total_count:
        status = "ELIGIBLE"
        label = "Eligible for Micro-Credit Facility"
        color = "LIME"
    elif passed_count >= 3 and r1_pass:
        status = "CONDITIONAL_APPROVAL"
        label = "Conditional Approval / Manual Review"
        color = "AMBER"
    else:
        status = "NOT_ELIGIBLE"
        label = "Eligibility Thresholds Not Met"
        color = "RED"

    # Assemble reasons and next steps
    reasons = [c.reason_code for c in criteria if not c.is_passed]
    if not reasons:
        reasons = ["ALL_POLICY_PREREQUISITES_SATISFIED"]

    next_steps = [c.remediation_advice for c in criteria if not c.is_passed]
    if not next_steps:
        next_steps = ["Proceed to download Digital Financial Passport and present to authorized partner lenders."]

    return UnderwritingDecisionResult(
        decision_status=status,
        status_label=label,
        status_badge_color=color,
        policy_version="MFI-Standard-Micro-Policy-2026.1",
        criteria_evaluated=criteria,
        passed_count=passed_count,
        total_rules_count=total_count,
        primary_reason_codes=reasons,
        actionable_next_steps=next_steps
    )
