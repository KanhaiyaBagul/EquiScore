"""
Financial Health Score (FHS) Engine
Deterministic 5-pillar composite scoring algorithm (0 - 100 scale).

Pillars:
1. Cash Flow Surplus (30%): Ratio of net monthly surplus to gross receipts.
2. Income Consistency (25%): 1 - Coefficient of Variation (CV) of monthly receipts.
3. Debt Burden Index (20%): Capacity of monthly surplus to cover existing EMI debt.
4. Liquidity Reserve Buffer (15%): Days of expense runway supported by minimum balance.
5. Documentation Coverage (10%): Multi-month duration and completeness reliability index.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class FHSInputFeatures(BaseModel):
    monthly_gross_receipts: float = Field(..., ge=0, description="Average monthly receipts/turnover in INR")
    monthly_operating_expenses: float = Field(..., ge=0, description="Average monthly business and living expenses in INR")
    monthly_debt_emi: float = Field(default=0.0, ge=0, description="Existing monthly loan/EMI obligations in INR")
    income_volatility_cv: float = Field(..., ge=0, description="Coefficient of variation of monthly receipts (std/mean)")
    min_ledger_balance: float = Field(default=0.0, ge=0, description="Lowest observed ledger balance in assessment period")
    data_coverage_months: int = Field(default=4, ge=1, le=120, description="Number of observed months of financial data")
    missing_period_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="Fraction of missing days/periods in range")


class FHSPillarBreakdown(BaseModel):
    pillar_name: str
    weight: float
    raw_metric: float
    raw_metric_formatted: str
    normalized_score: float # 0 to 100
    weighted_score: float # normalized_score * weight
    status_label: str # "EXCELLENT", "GOOD", "MODERATE", "NEEDS_IMPROVEMENT"
    explanatory_note: str


class FHSAssessmentResult(BaseModel):
    overall_score: int # 0 to 100
    health_band: str # "PRIME_STABLE", "RESILIENT", "MODERATE", "VULNERABLE"
    pillars: Dict[str, FHSPillarBreakdown]
    summary_narrative: str
    strengths: list[str]
    vulnerabilities: list[str]


def calculate_financial_health_score(inputs: FHSInputFeatures) -> FHSAssessmentResult:
    """
    Computes a deterministic, reproducible Financial Health Score (0 - 100).
    Pure mathematical formula; zero black-box hallucination.
    """
    gross = max(0.01, inputs.monthly_gross_receipts)
    expenses = inputs.monthly_operating_expenses
    surplus = max(0.0, gross - expenses)
    emi = inputs.monthly_debt_emi
    cv = inputs.income_volatility_cv
    buffer_balance = inputs.min_ledger_balance
    months = inputs.data_coverage_months
    missing_ratio = inputs.missing_period_ratio

    # -------------------------------------------------------------
    # 1. CASH FLOW SURPLUS PILLAR (30% weight)
    # Target surplus ratio is 35% or higher for full 100 score
    # -------------------------------------------------------------
    surplus_ratio = surplus / gross
    p1_normalized = min(100.0, max(0.0, (surplus_ratio / 0.35) * 100.0))
    p1_status = "EXCELLENT" if p1_normalized >= 80 else ("GOOD" if p1_normalized >= 60 else ("MODERATE" if p1_normalized >= 40 else "NEEDS_IMPROVEMENT"))
    p1_note = f"Net monthly surplus is ₹{surplus:,.0f} ({surplus_ratio*100:.1f}% of gross receipts)."
    
    p1 = FHSPillarBreakdown(
        pillar_name="Cash Flow Surplus",
        weight=0.30,
        raw_metric=round(surplus_ratio, 4),
        raw_metric_formatted=f"{surplus_ratio*100:.1f}% margin",
        normalized_score=round(p1_normalized, 1),
        weighted_score=round(p1_normalized * 0.30, 2),
        status_label=p1_status,
        explanatory_note=p1_note
    )

    # -------------------------------------------------------------
    # 2. INCOME CONSISTENCY PILLAR (25% weight)
    # Lower CV implies higher consistency. CV <= 0.10 is excellent, CV >= 0.50 is volatile.
    # -------------------------------------------------------------
    consistency_score = max(0.0, 1.0 - (cv / 0.50)) * 100.0
    p2_normalized = min(100.0, max(0.0, consistency_score))
    p2_status = "EXCELLENT" if p2_normalized >= 80 else ("GOOD" if p2_normalized >= 60 else ("MODERATE" if p2_normalized >= 40 else "NEEDS_IMPROVEMENT"))
    p2_note = f"Receipt variability index is {cv:.2f} (Month-to-month stability: {p2_normalized:.0f}%)."
    
    p2 = FHSPillarBreakdown(
        pillar_name="Income Consistency",
        weight=0.25,
        raw_metric=round(cv, 4),
        raw_metric_formatted=f"{cv:.2f} CV",
        normalized_score=round(p2_normalized, 1),
        weighted_score=round(p2_normalized * 0.25, 2),
        status_label=p2_status,
        explanatory_note=p2_note
    )

    # -------------------------------------------------------------
    # 3. DEBT BURDEN INDEX (20% weight)
    # Ratio of EMI commitments to net monthly surplus.
    # EMI <= 20% of surplus -> 100 score. EMI >= 80% of surplus -> 0 score.
    # -------------------------------------------------------------
    if surplus > 0:
        debt_ratio = emi / surplus
    else:
        debt_ratio = 1.0 if emi > 0 else 0.0

    if debt_ratio <= 0.05:
        p3_normalized = 100.0
    elif debt_ratio >= 0.80:
        p3_normalized = 0.0
    else:
        p3_normalized = max(0.0, 100.0 - ((debt_ratio - 0.05) / 0.75) * 100.0)

    p3_status = "EXCELLENT" if p3_normalized >= 80 else ("GOOD" if p3_normalized >= 60 else ("MODERATE" if p3_normalized >= 40 else "NEEDS_IMPROVEMENT"))
    p3_note = f"Monthly loan EMIs take {debt_ratio*100:.1f}% of net operating surplus (₹{emi:,.0f}/mo)."
    
    p3 = FHSPillarBreakdown(
        pillar_name="Debt Burden Index",
        weight=0.20,
        raw_metric=round(debt_ratio, 4),
        raw_metric_formatted=f"{debt_ratio*100:.1f}% of surplus",
        normalized_score=round(p3_normalized, 1),
        weighted_score=round(p3_normalized * 0.20, 2),
        status_label=p3_status,
        explanatory_note=p3_note
    )

    # -------------------------------------------------------------
    # 4. LIQUIDITY RESERVE BUFFER (15% weight)
    # Days of runway supported by lowest daily balance against average daily expense.
    # 25+ days is 100 score; <3 days is low.
    # -------------------------------------------------------------
    daily_burn = max(100.0, expenses / 30.0)
    buffer_days = buffer_balance / daily_burn
    p4_normalized = min(100.0, max(0.0, (buffer_days / 25.0) * 100.0))
    p4_status = "EXCELLENT" if p4_normalized >= 80 else ("GOOD" if p4_normalized >= 60 else ("MODERATE" if p4_normalized >= 40 else "NEEDS_IMPROVEMENT"))
    p4_note = f"Minimum observed balance covers approximately {buffer_days:.1f} days of operational expenses."
    
    p4 = FHSPillarBreakdown(
        pillar_name="Reserve Buffer",
        weight=0.15,
        raw_metric=round(buffer_days, 1),
        raw_metric_formatted=f"{buffer_days:.1f} days runway",
        normalized_score=round(p4_normalized, 1),
        weighted_score=round(p4_normalized * 0.15, 2),
        status_label=p4_status,
        explanatory_note=p4_note
    )

    # -------------------------------------------------------------
    # 5. DATA DOCUMENTATION COVERAGE (10% weight)
    # Based on duration (6+ months ideal) and absence of data gaps.
    # -------------------------------------------------------------
    duration_factor = min(1.0, months / 6.0)
    completeness_factor = 1.0 - missing_ratio
    p5_normalized = min(100.0, max(0.0, duration_factor * completeness_factor * 100.0))
    p5_status = "EXCELLENT" if p5_normalized >= 80 else ("GOOD" if p5_normalized >= 60 else ("MODERATE" if p5_normalized >= 40 else "NEEDS_IMPROVEMENT"))
    p5_note = f"{months} months of continuous statement records analyzed ({p5_normalized:.0f}% coverage fidelity)."
    
    p5 = FHSPillarBreakdown(
        pillar_name="Data Completeness",
        weight=0.10,
        raw_metric=round(duration_factor * completeness_factor, 4),
        raw_metric_formatted=f"{months} mos ({completeness_factor*100:.0f}% clean)",
        normalized_score=round(p5_normalized, 1),
        weighted_score=round(p5_normalized * 0.10, 2),
        status_label=p5_status,
        explanatory_note=p5_note
    )

    # Total Composite Score (0 - 100)
    total_score = p1.weighted_score + p2.weighted_score + p3.weighted_score + p4.weighted_score + p5.weighted_score
    overall_int = int(round(min(100.0, max(0.0, total_score))))

    if overall_int >= 80:
        band = "PRIME_STABLE"
    elif overall_int >= 65:
        band = "RESILIENT"
    elif overall_int >= 50:
        band = "MODERATE"
    else:
        band = "VULNERABLE"

    # Compile Strengths & Vulnerabilities
    strengths = []
    vulnerabilities = []
    pillars_dict = {
        "cash_flow_surplus": p1,
        "income_consistency": p2,
        "debt_burden": p3,
        "reserve_buffer": p4,
        "data_completeness": p5
    }

    for key, p in pillars_dict.items():
        if p.normalized_score >= 70:
            strengths.append(f"{p.pillar_name}: {p.explanatory_note}")
        elif p.normalized_score < 45:
            vulnerabilities.append(f"{p.pillar_name}: {p.explanatory_note}")

    if not strengths:
        strengths.append("Foundational daily transaction presence established.")
    if not vulnerabilities:
        vulnerabilities.append("No critical liquidity or debt burden bottlenecks detected.")

    narrative = (
        f"The applicant exhibits an overall Financial Health Score of {overall_int}/100 ({band.replace('_', ' ')}). "
        f"Primary strength lies in {p1.pillar_name.lower()} with a normalized score of {p1.normalized_score:.0f}/100. "
        f"Primary risk mitigation area is {p3.pillar_name.lower()} where debt obligations represent {debt_ratio*100:.1f}% of net surplus."
    )

    return FHSAssessmentResult(
        overall_score=overall_int,
        health_band=band,
        pillars=pillars_dict,
        summary_narrative=narrative,
        strengths=strengths,
        vulnerabilities=vulnerabilities
    )
