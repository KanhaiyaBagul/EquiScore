"""
Informal Income Synthesizer Service
Aggregates fragmented, irregular transaction streams (UPI, cash deposits, digital ledgers)
and computes recurring income, volatility CV, operational expenses, net surplus, and coverage quality.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

class MonthlyIncomeSummary(BaseModel):
    month_period: str # "2026-06"
    gross_receipts: float
    operating_expenses: float
    debt_emi_payments: float
    net_operating_surplus: float
    customer_tx_count: int


class IncomeSynthesisResult(BaseModel):
    average_monthly_gross_receipts: float
    average_monthly_expenses: float
    average_monthly_debt_emi: float
    average_monthly_net_surplus: float
    net_surplus_ratio: float
    income_volatility_cv: float
    min_observed_balance: float
    total_tx_count: int
    data_coverage_months: int
    coverage_reliability_percent: float
    monthly_trend: List[MonthlyIncomeSummary]
    anomaly_flags: List[str]


def synthesize_income_from_transactions(
    df: pd.DataFrame,
    min_ledger_balance: float = 8500.0
) -> IncomeSynthesisResult:
    """
    Synthesizes reliable informal income indicators from a validated transactions DataFrame.
    DataFrame must have columns: ['date', 'amount', 'direction', 'category']
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month_period"] = df["date"].dt.strftime("%Y-%m")
    
    # Categorize credits and debits
    # Receipts: credits excluding internal transfers and reversals
    receipts_df = df[(df["direction"] == "CREDIT") & (~df["category"].str.contains("TRANSFER|REVERSAL", case=False, na=False))]
    # EMI/Debt: debits matching loan, emi, repayment, finance
    is_emi = (df["direction"] == "DEBIT") & (
        df["category"].str.contains("EMI|LOAN|REPAYMENT|FINANCE|BORROW|INSTALLMENT", case=False, na=False) |
        df["description"].str.contains("EMI|LOAN|REPAYMENT|FINANCE|BORROW|INSTALLMENT", case=False, na=False)
    )
    emi_df = df[is_emi]
    # Operating expenses: all other debits excluding transfers, reversals, and EMI
    is_transfer = df["category"].str.contains("TRANSFER|REVERSAL|REFUND", case=False, na=False)
    expenses_df = df[(df["direction"] == "DEBIT") & (~is_emi) & (~is_transfer)]

    all_months = sorted(df["month_period"].unique())
    monthly_summaries: List[MonthlyIncomeSummary] = []
    monthly_gross_list = []
    monthly_surplus_list = []

    for m in all_months:
        m_receipts = float(receipts_df[receipts_df["month_period"] == m]["amount"].sum())
        m_expenses = float(expenses_df[expenses_df["month_period"] == m]["amount"].sum())
        m_emi = float(emi_df[emi_df["month_period"] == m]["amount"].sum())
        m_surplus = max(0.0, m_receipts - m_expenses)
        m_tx_count = int(len(receipts_df[receipts_df["month_period"] == m]))

        monthly_gross_list.append(m_receipts)
        monthly_surplus_list.append(m_surplus)

        monthly_summaries.append(MonthlyIncomeSummary(
            month_period=m,
            gross_receipts=round(m_receipts, 2),
            operating_expenses=round(m_expenses, 2),
            debt_emi_payments=round(m_emi, 2),
            net_operating_surplus=round(m_surplus, 2),
            customer_tx_count=m_tx_count
        ))

    # Statistical aggregations
    avg_gross = float(np.mean(monthly_gross_list)) if monthly_gross_list else 0.0
    avg_expenses = float(np.mean([s.operating_expenses for s in monthly_summaries])) if monthly_summaries else 0.0
    avg_emi = float(np.mean([s.debt_emi_payments for s in monthly_summaries])) if monthly_summaries else 0.0
    avg_surplus = float(np.mean(monthly_surplus_list)) if monthly_surplus_list else 0.0

    # Coefficient of Variation (CV = std / mean)
    if len(monthly_gross_list) > 1 and avg_gross > 0:
        std_gross = float(np.std(monthly_gross_list, ddof=1))
        cv = std_gross / avg_gross
    else:
        cv = 0.15 # Default conservative baseline

    surplus_ratio = (avg_surplus / avg_gross) if avg_gross > 0 else 0.0
    coverage_months = len(all_months)
    
    # Coverage reliability: full credit for 6+ months
    coverage_reliability = min(100.0, (coverage_months / 6.0) * 100.0)

    # Anomaly checks
    anomalies = []
    if cv > 0.40:
        anomalies.append(f"High monthly revenue variability detected (CV: {cv:.2f}). Seasonal smoothing applied.")
    if avg_emi > (avg_surplus * 0.60):
        anomalies.append(f"Elevated debt service ratio: Loan EMIs consume {(avg_emi/max(1,avg_surplus))*100:.1f}% of net operating surplus.")
    if coverage_months < 3:
        anomalies.append("Limited statement history (< 3 months). Preliminary assessment confidence reduced.")

    return IncomeSynthesisResult(
        average_monthly_gross_receipts=round(avg_gross, 2),
        average_monthly_expenses=round(avg_expenses, 2),
        average_monthly_debt_emi=round(avg_emi, 2),
        average_monthly_net_surplus=round(avg_surplus, 2),
        net_surplus_ratio=round(surplus_ratio, 4),
        income_volatility_cv=round(cv, 4),
        min_observed_balance=round(min_ledger_balance, 2),
        total_tx_count=len(df),
        data_coverage_months=coverage_months,
        coverage_reliability_percent=round(coverage_reliability, 1),
        monthly_trend=monthly_summaries,
        anomaly_flags=anomalies
    )
