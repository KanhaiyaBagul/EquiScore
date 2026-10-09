"""
What-If Financial Scenario Simulation Service
Evaluates hypothetical financial changes (reduced expenses, boosted revenue, debt payoff)
against the deterministic FHS scoring engine and calibrated ML credit risk pipeline.
CRITICAL INVARIANT: Never mutates baseline database records. All simulations run in isolated memory.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

from backend.app.services.financial_health_service import (
    calculate_financial_health_score,
    FHSInputFeatures,
    FHSAssessmentResult
)
from backend.app.services.credit_risk_service import (
    evaluate_credit_risk,
    CreditRiskEvaluationResult
)

class ScenarioInputDelta(BaseModel):
    baseline_gross: float = Field(..., ge=0)
    baseline_expenses: float = Field(..., ge=0)
    baseline_emi: float = Field(default=0.0, ge=0)
    baseline_cv: float = Field(default=0.15, ge=0)
    baseline_min_balance: float = Field(default=8000.0, ge=0)
    baseline_coverage_months: int = Field(default=4, ge=1)
    
    # Delta adjustments from user sliders
    delta_expenses: float = Field(default=0.0, description="Monthly expense reduction/increase in INR (e.g. -4000)")
    delta_gross: float = Field(default=0.0, description="Monthly receipts boost/reduction in INR (e.g. +5000)")
    delta_emi: float = Field(default=0.0, description="Monthly debt reduction in INR (e.g. -2000)")
    delta_reserve_balance: float = Field(default=0.0, description="Emergency reserve addition in INR (e.g. +10000)")


class ScenarioSimulationResult(BaseModel):
    baseline_fhs_score: int
    simulated_fhs_score: int
    fhs_score_delta: int # e.g. +7
    
    baseline_repayment_prob: float
    simulated_repayment_prob: float
    repayment_prob_delta: float # e.g. +4.2%
    
    baseline_risk_tier: str
    simulated_risk_tier: str
    
    new_monthly_surplus: float
    surplus_delta: float
    
    impact_factors: List[str]
    advice_note: str


def simulate_what_if_scenario(delta_inputs: ScenarioInputDelta) -> ScenarioSimulationResult:
    """
    Computes side-by-side comparison between baseline and simulated hypothetical parameters.
    """
    # 1. Evaluate Baseline
    base_inp = FHSInputFeatures(
        monthly_gross_receipts=delta_inputs.baseline_gross,
        monthly_operating_expenses=delta_inputs.baseline_expenses,
        monthly_debt_emi=delta_inputs.baseline_emi,
        income_volatility_cv=delta_inputs.baseline_cv,
        min_ledger_balance=delta_inputs.baseline_min_balance,
        data_coverage_months=delta_inputs.baseline_coverage_months
    )
    base_fhs = calculate_financial_health_score(base_inp)

    base_surplus = max(0.0, delta_inputs.baseline_gross - delta_inputs.baseline_expenses)
    base_features = {
        "monthly_gross_receipts": delta_inputs.baseline_gross,
        "monthly_operating_expenses": delta_inputs.baseline_expenses,
        "net_surplus_ratio": (base_surplus / max(1.0, delta_inputs.baseline_gross)),
        "income_volatility_cv": delta_inputs.baseline_cv,
        "debt_to_surplus_ratio": (delta_inputs.baseline_emi / max(1.0, base_surplus)),
        "reserve_buffer_days": (delta_inputs.baseline_min_balance / max(100.0, delta_inputs.baseline_expenses / 30.0)),
        "tx_frequency_monthly": 200,
        "data_coverage_months": delta_inputs.baseline_coverage_months
    }
    base_risk = evaluate_credit_risk(base_features)

    # 2. Evaluate Simulated Hypothetical State
    sim_gross = max(0.0, delta_inputs.baseline_gross + delta_inputs.delta_gross)
    sim_expenses = max(0.0, delta_inputs.baseline_expenses + delta_inputs.delta_expenses)
    sim_emi = max(0.0, delta_inputs.baseline_emi + delta_inputs.delta_emi)
    sim_balance = max(0.0, delta_inputs.baseline_min_balance + delta_inputs.delta_reserve_balance)
    sim_surplus = max(0.0, sim_gross - sim_expenses)

    sim_inp = FHSInputFeatures(
        monthly_gross_receipts=sim_gross,
        monthly_operating_expenses=sim_expenses,
        monthly_debt_emi=sim_emi,
        income_volatility_cv=delta_inputs.baseline_cv,
        min_ledger_balance=sim_balance,
        data_coverage_months=delta_inputs.baseline_coverage_months
    )
    sim_fhs = calculate_financial_health_score(sim_inp)

    sim_features = {
        "monthly_gross_receipts": sim_gross,
        "monthly_operating_expenses": sim_expenses,
        "net_surplus_ratio": (sim_surplus / max(1.0, sim_gross)),
        "income_volatility_cv": delta_inputs.baseline_cv,
        "debt_to_surplus_ratio": (sim_emi / max(1.0, sim_surplus)),
        "reserve_buffer_days": (sim_balance / max(100.0, sim_expenses / 30.0)),
        "tx_frequency_monthly": 200,
        "data_coverage_months": delta_inputs.baseline_coverage_months
    }
    sim_risk = evaluate_credit_risk(sim_features)

    # Deltas
    fhs_diff = sim_fhs.overall_score - base_fhs.overall_score
    prob_diff = round(sim_risk.repayment_probability_percent - base_risk.repayment_probability_percent, 1)
    surplus_diff = round(sim_surplus - base_surplus, 2)

    # Key factors driving the delta
    impacts = []
    if delta_inputs.delta_expenses < 0:
        impacts.append(f"Reducing expenses by INR {abs(delta_inputs.delta_expenses):,.0f} expands net monthly surplus to INR {sim_surplus:,.0f}.")
    if delta_inputs.delta_gross > 0:
        impacts.append(f"Boosting monthly turnover by INR {delta_inputs.delta_gross:,.0f} lifts cashflow capacity.")
    if delta_inputs.delta_emi < 0:
        impacts.append(f"Paying down monthly debt by INR {abs(delta_inputs.delta_emi):,.0f} reduces debt service burden to {(sim_emi/max(1,sim_surplus))*100:.1f}%.")
    if delta_inputs.delta_reserve_balance > 0:
        impacts.append(f"Adding INR {delta_inputs.delta_reserve_balance:,.0f} to reserves extends liquidity runway to {(sim_balance/max(100, sim_expenses/30.0)):.1f} days.")

    if not impacts:
        impacts.append("No changes applied from baseline.")

    advice = (
        f"Hypothetical changes yield a {abs(fhs_diff)} point {'gain' if fhs_diff >= 0 else 'drop'} in Financial Health Score "
        f"(from {base_fhs.overall_score} to {sim_fhs.overall_score}/100) and adjust repayment probability by "
        f"{'+' if prob_diff >= 0 else ''}{prob_diff}%."
    )

    return ScenarioSimulationResult(
        baseline_fhs_score=base_fhs.overall_score,
        simulated_fhs_score=sim_fhs.overall_score,
        fhs_score_delta=fhs_diff,
        baseline_repayment_prob=base_risk.repayment_probability_percent,
        simulated_repayment_prob=sim_risk.repayment_probability_percent,
        repayment_prob_delta=prob_diff,
        baseline_risk_tier=base_risk.risk_tier,
        simulated_risk_tier=sim_risk.risk_tier,
        new_monthly_surplus=round(sim_surplus, 2),
        surplus_delta=surplus_diff,
        impact_factors=impacts,
        advice_note=advice
    )
