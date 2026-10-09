"""
Credit Risk Evaluation Service
Loads calibrated XGBoost model from ml_work_flow to evaluate probability of repayment,
risk tier assignment, and feature attributions.
"""

import os
import joblib
import shap
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from pydantic import BaseModel

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
MODEL_PATH = os.path.join(PROJECT_DIR, "ml_work_flow", "credit_xgboost_model.pkl")

class ShapFeatureAttribution(BaseModel):
    feature_name: str
    feature_label: str
    feature_value: float
    feature_value_formatted: str
    shap_value: float
    impact_direction: str
    impact_magnitude: str
    human_explanation: str

class CreditRiskEvaluationResult(BaseModel):
    repayment_probability_percent: float
    default_risk_probability_percent: float
    risk_tier: str
    baseline_probability_percent: float
    model_version: str
    shap_baseline_log_odds: float
    attributions: List[ShapFeatureAttribution]
    plain_language_narrative: str

def _format_feature(name: str, val: float) -> tuple[str, str]:
    labels = {
        "utility_bill_consistency": ("Utility Bill Consistency", f"{val*100:.1f}%"),
        "upi_transaction_velocity": ("UPI Transaction Velocity", f"{int(val)} txns/mo"),
        "seasonal_inventory_turnover": ("Seasonal Inventory Turnover", f"{val:.2f}x"),
        "business_age_months": ("Business Age", f"{int(val)} months")
    }
    return labels.get(name, (name, str(val)))

def evaluate_credit_risk(features_dict: Dict[str, float]) -> CreditRiskEvaluationResult:
    """
    Evaluates credit repayment probability and SHAP attribution for input features.
    """
    model = joblib.load(MODEL_PATH)
    
    feature_names = [
        "utility_bill_consistency",
        "upi_transaction_velocity",
        "seasonal_inventory_turnover",
        "business_age_months"
    ]

    row = {col: float(features_dict.get(col, 0.0)) for col in feature_names}
    X = pd.DataFrame([row], columns=feature_names)

    # In ml_work_flow, the target is default_risk (1 = default, 0 = repaid)
    # Predict probability of default
    prob_default = float(model.predict_proba(X)[0, 1])
    prob_repaid = float(1.0 - prob_default)

    # Determine risk tier based on repayment probability
    if prob_repaid >= 0.75:
        tier = "TIER_1_LOW_RISK"
    elif prob_repaid >= 0.60:
        tier = "TIER_2_MODERATE_RISK"
    else:
        tier = "TIER_3_ELEVATED_RISK"

    # Compute SHAP values dynamically
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(X)
    
    # XGBoost shap_values might be a list or array. For binary classification it's usually array of shape (n_samples, n_features)
    if isinstance(shap_vals, list):
        raw_shap_arr = shap_vals[1][0] # If list, [1] is for class 1
    else:
        raw_shap_arr = shap_vals[0]

    baseline_val = float(explainer.expected_value[1] if isinstance(explainer.expected_value, (list, tuple, np.ndarray)) else explainer.expected_value)

    attributions = []
    top_positive = []
    top_negative = []

    for name, val, sv in zip(feature_names, X.iloc[0], raw_shap_arr):
        label, formatted = _format_feature(name, val)
        # Positive SHAP value pushes towards Default (1). So sv > 0 is bad for repayment.
        # We want is_positive to mean "good for the borrower" i.e. pushes towards Repayment.
        is_positive = (sv < 0) 
        direction = "REDUCES_RISK" if is_positive else "INCREASES_RISK"
        mag = "HIGH" if abs(sv) >= 0.20 else ("MODERATE" if abs(sv) >= 0.08 else "LOW")

        if name == "utility_bill_consistency":
            exp = "Consistent utility payments indicate high reliability." if is_positive else "Inconsistent utility payments signal cashflow stress."
        elif name == "upi_transaction_velocity":
            exp = "High transactional velocity demonstrates robust business activity." if is_positive else "Low transaction frequency suggests stagnating sales."
        elif name == "seasonal_inventory_turnover":
            exp = "Healthy inventory turnover shows strong demand." if is_positive else "Sluggish inventory movement locks up working capital."
        elif name == "business_age_months":
            exp = "Established business tenure provides historical stability." if is_positive else "Short business history lacks sufficient operational track record."
        else:
            exp = f"Feature contribution pushes risk rating {'favorably' if is_positive else 'unfavorably'}."

        attr = ShapFeatureAttribution(
            feature_name=name,
            feature_label=label,
            feature_value=round(val, 4),
            feature_value_formatted=formatted,
            # We invert the SHAP value so positive means good in the UI
            shap_value=round(float(-sv), 4),
            impact_direction=direction,
            impact_magnitude=mag,
            human_explanation=exp
        )
        attributions.append(attr)

        if is_positive:
            top_positive.append((abs(sv), label))
        else:
            top_negative.append((abs(sv), label))

    attributions.sort(key=lambda a: abs(a.shap_value), reverse=True)
    top_positive.sort(reverse=True)
    top_negative.sort(reverse=True)

    pos_summary = ", ".join([p[1] for p in top_positive[:2]]) if top_positive else "steady basic activity"
    neg_summary = ", ".join([n[1] for n in top_negative[:2]]) if top_negative else "no major penalties"

    narrative = (
        f"The credit-risk model estimates a {prob_repaid*100:.1f}% probability of timely repayment ({tier.replace('_', ' ')}). "
        f"Primary positive contributors boosting the score are {pos_summary}. "
        f"Factors exerting downward drag are {neg_summary}."
    )

    return CreditRiskEvaluationResult(
        repayment_probability_percent=round(prob_repaid * 100.0, 1),
        default_risk_probability_percent=round(prob_default * 100.0, 1),
        risk_tier=tier,
        baseline_probability_percent=70.0, # Mocked baseline
        model_version="XGBoost-AltCredit-v2.0",
        shap_baseline_log_odds=round(baseline_val, 4),
        attributions=attributions,
        plain_language_narrative=narrative
    )

