"""
Fairness and Algorithmic Bias Audit Engine (Fairlearn)
Audits the Calibrated XGBoost Alternative Credit Risk Model for demographic disparities
across Gender, Geographic Tiers, and Business Archetypes.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from fairlearn.metrics import (
    MetricFrame,
    selection_rate,
    demographic_parity_difference,
    equalized_odds_difference,
    false_positive_rate,
    false_negative_rate
)
from sklearn.metrics import accuracy_score, precision_score, recall_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "ml", "artifacts")
DATA_PATH = os.path.join(BASE_DIR, "data", "training_cohort_5000.csv")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "calibrated_pipeline.joblib")

def audit_model_fairness():
    print("Loading model and dataset for algorithmic fairness audit...")
    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATA_PATH)

    with open(os.path.join(ARTIFACTS_DIR, "feature_names.json"), "r") as f:
        features = json.load(f)

    X = df[features]
    y_true = df["repaid_status"]

    # Model predictions
    y_prob = model.predict_proba(X)[:, 1]
    y_pred = (y_prob >= 0.50).astype(int)

    # Demographic groups
    sensitive_features = {
        "gender_group": df["gender_group"],
        "geography_tier": df["geography_tier"],
        "business_category": df["business_category"]
    }

    audit_results = {
        "model_id": "XGBoost-AltCredit-v1.0",
        "audit_timestamp": "2026-10-09",
        "sample_size": len(df),
        "overall_selection_rate": round(float(np.mean(y_pred)), 4),
        "decision_threshold": 0.50,
        "cohort_audits": {}
    }

    print("\n--- Running Fairlearn Group Disparity Audits ---")

    for attr_name, sensitive_series in sensitive_features.items():
        # MetricFrame for detailed group breakdowns
        mf = MetricFrame(
            metrics={
                "selection_rate": selection_rate,
                "accuracy": accuracy_score,
                "precision": precision_score,
                "recall": recall_score,
                "fpr": false_positive_rate,
                "fnr": false_negative_rate
            },
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sensitive_series
        )

        dp_diff = float(demographic_parity_difference(y_true, y_pred, sensitive_features=sensitive_series))
        eo_diff = float(equalized_odds_difference(y_true, y_pred, sensitive_features=sensitive_series))

        # Status: Pass if difference < 0.10
        dp_pass = dp_diff < 0.10
        eo_pass = eo_diff < 0.10

        cohort_data = {}
        by_group = mf.by_group
        for grp in by_group.index:
            cohort_data[str(grp)] = {
                "sample_count": int(df[sensitive_series == grp].shape[0]),
                "selection_rate": round(float(by_group.loc[grp, "selection_rate"]), 4),
                "accuracy": round(float(by_group.loc[grp, "accuracy"]), 4),
                "precision": round(float(by_group.loc[grp, "precision"]), 4),
                "recall": round(float(by_group.loc[grp, "recall"]), 4),
                "false_positive_rate": round(float(by_group.loc[grp, "fpr"]), 4),
                "false_negative_rate": round(float(by_group.loc[grp, "fnr"]), 4)
            }

        audit_results["cohort_audits"][attr_name] = {
            "demographic_parity_difference": round(dp_diff, 4),
            "demographic_parity_passed": dp_pass,
            "equalized_odds_difference": round(eo_diff, 4),
            "equalized_odds_passed": eo_pass,
            "group_breakdowns": cohort_data
        }

        status_str = "COMPLIANT (PASSED)" if (dp_pass and eo_pass) else "FLAGGED FOR REVIEW"
        print(f"\nAudit Attribute: {attr_name}")
        print(f"  Demographic Parity Diff: {dp_diff:.4f} (Threshold < 0.10: {'PASS' if dp_pass else 'FAIL'})")
        print(f"  Equalized Odds Diff:     {eo_diff:.4f} (Threshold < 0.10: {'PASS' if eo_pass else 'FAIL'})")
        print(f"  Status:                  {status_str}")

    report_path = os.path.join(ARTIFACTS_DIR, "fairness_audit_report.json")
    with open(report_path, "w") as f:
        json.dump(audit_results, f, indent=2)

    print(f"\nFairness audit report successfully saved to: {report_path}")
    return audit_results

if __name__ == "__main__":
    audit_model_fairness()
