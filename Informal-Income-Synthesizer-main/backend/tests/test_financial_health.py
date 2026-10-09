"""
Unit Tests for Financial Health Score (FHS) Service
Validates mathematical boundary invariants (0 <= score <= 100) and edge cases.
"""

import pytest
from backend.app.services.financial_health_service import (
    calculate_financial_health_score,
    FHSInputFeatures
)

def test_fhs_healthy_vendor():
    # Ramesh scenario: ₹41,500 gross, ₹19,200 expenses, ₹3,200 EMI, CV 0.12, 18 days buffer
    inputs = FHSInputFeatures(
        monthly_gross_receipts=41500.0,
        monthly_operating_expenses=19200.0,
        monthly_debt_emi=3200.0,
        income_volatility_cv=0.12,
        min_ledger_balance=11500.0,
        data_coverage_months=4,
        missing_period_ratio=0.0
    )
    result = calculate_financial_health_score(inputs)
    assert 0 <= result.overall_score <= 100
    assert result.overall_score >= 70, f"Expected resilient score, got {result.overall_score}"
    assert result.health_band in ["PRIME_STABLE", "RESILIENT"]
    assert len(result.strengths) >= 1

def test_fhs_stressed_borrower():
    # High debt, volatile, zero buffer
    inputs = FHSInputFeatures(
        monthly_gross_receipts=25000.0,
        monthly_operating_expenses=21000.0,
        monthly_debt_emi=3800.0, # High debt against small surplus of 4k
        income_volatility_cv=0.48, # High volatility
        min_ledger_balance=500.0,
        data_coverage_months=2,
        missing_period_ratio=0.25
    )
    result = calculate_financial_health_score(inputs)
    assert 0 <= result.overall_score <= 100
    assert result.overall_score < 55, f"Expected vulnerable score, got {result.overall_score}"
    assert len(result.vulnerabilities) >= 1

def test_fhs_zero_income_edge_case():
    # Extreme edge case: Zero receipts
    inputs = FHSInputFeatures(
        monthly_gross_receipts=0.0,
        monthly_operating_expenses=5000.0,
        monthly_debt_emi=1000.0,
        income_volatility_cv=0.8,
        min_ledger_balance=0.0,
        data_coverage_months=1,
        missing_period_ratio=0.5
    )
    result = calculate_financial_health_score(inputs)
    assert 0 <= result.overall_score <= 100
    assert result.overall_score <= 30
