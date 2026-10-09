"""
SHAP TreeExplainer Module
Initializes shap.TreeExplainer on the trained XGBoost model,
computes the baseline expectation phi_0, and exports the explainer artifact.
"""

import os
import json
import joblib
import shap
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "ml", "artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "risk_model_xgboost.joblib")
DATA_PATH = os.path.join(BASE_DIR, "data", "training_cohort_5000.csv")

def export_shap_explainer():
    print(f"Loading trained XGBoost model from {MODEL_PATH}...")
    model = joblib.load(MODEL_PATH)

    with open(os.path.join(ARTIFACTS_DIR, "feature_names.json"), "r") as f:
        feature_names = json.load(f)

    # Initialize TreeExplainer
    explainer = shap.TreeExplainer(model)

    # Expected value phi_0 in margin / log-odds space
    base_val = explainer.expected_value
    if isinstance(base_val, (list, np.ndarray)):
        base_val = float(base_val[0])
    else:
        base_val = float(base_val)

    # Convert margin base value to baseline probability via logistic sigmoid
    base_prob = 1.0 / (1.0 + np.exp(-base_val))

    print(f"SHAP TreeExplainer initialized successfully.")
    print(f"Baseline Expected Value (log-odds space): {base_val:.4f}")
    print(f"Baseline Expected Probability:           {base_prob*100:.1f}%")

    # Export explainer
    explainer_path = os.path.join(ARTIFACTS_DIR, "shap_explainer.joblib")
    joblib.dump(explainer, explainer_path)

    baseline_payload = {
        "expected_value_log_odds": round(base_val, 4),
        "expected_probability": round(base_prob, 4),
        "feature_count": len(feature_names),
        "explainer_type": "TreeExplainer"
    }

    baseline_path = os.path.join(ARTIFACTS_DIR, "baseline_value.json")
    with open(baseline_path, "w") as f:
        json.dump(baseline_payload, f, indent=2)

    print(f"Exported SHAP explainer to: {explainer_path}")
    print(f"Exported baseline info to:  {baseline_path}")

    # Validate with a test applicant (Ramesh features)
    ramesh_features = pd.DataFrame([{
        "monthly_gross_receipts": 41500.0,
        "monthly_operating_expenses": 19200.0,
        "net_surplus_ratio": 0.537,
        "income_volatility_cv": 0.12,
        "debt_to_surplus_ratio": 0.143,
        "reserve_buffer_days": 18.0,
        "tx_frequency_monthly": 320,
        "data_coverage_months": 4
    }])[feature_names]

    shap_vals = explainer(ramesh_features)
    print("\n--- Validation Test on Ramesh (Chai Vendor) ---")
    val_arr = shap_vals.values[0]
    for feat, v in zip(feature_names, val_arr):
        sign = "+" if v >= 0 else "-"
        direction = "Reduces Default Risk" if v >= 0 else "Increases Risk"
        print(f"  {feat:<28}: {sign}{abs(v):.4f} ({direction})")

    # Additivity verification: sum(phi_j) + base_val approx model raw margin
    raw_pred = model.predict(ramesh_features, output_margin=True)[0]
    reconstructed = base_val + np.sum(val_arr)
    diff = abs(raw_pred - reconstructed)
    print(f"\nRaw model margin: {raw_pred:.4f}")
    print(f"Reconstructed:    {reconstructed:.4f}")
    print(f"Difference:       {diff:.6f} (tolerance < 0.01)")
    assert diff < 0.01, f"SHAP additivity verification failed with diff {diff}!"
    print("SHAP Additivity Verified 100%!")

if __name__ == "__main__":
    export_shap_explainer()
