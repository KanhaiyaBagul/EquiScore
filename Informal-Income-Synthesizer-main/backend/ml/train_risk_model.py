"""
Model Training Module: Calibrated Alternative Credit Risk Classifier (XGBoost)
Trains an alternative credit risk model on non-bureau cashflow & behavioral metrics.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, brier_score_loss, accuracy_score, precision_score, recall_score
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "training_cohort_5000.csv")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "ml", "artifacts")

FEATURE_COLUMNS = [
    "monthly_gross_receipts",
    "monthly_operating_expenses",
    "net_surplus_ratio",
    "income_volatility_cv",
    "debt_to_surplus_ratio",
    "reserve_buffer_days",
    "tx_frequency_monthly",
    "data_coverage_months"
]

TARGET_COLUMN = "repaid_status"

def train_and_export_model():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    print(f"Loading training data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    print(f"Baseline repayment rate in train: {y_train.mean():.3f}")

    # 1. Base XGBoost Classifier
    base_xgb = XGBClassifier(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.07,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        eval_metric="logloss"
    )

    base_xgb.fit(X_train, y_train)

    # 2. Probability Calibration (Sigmoid Platt Scaling)
    calibrated_model = CalibratedClassifierCV(
        estimator=base_xgb,
        method="sigmoid",
        cv="prefit"
    )
    calibrated_model.fit(X_test, y_test)

    # 3. Model Evaluation on Test Set
    y_pred_proba = calibrated_model.predict_proba(X_test)[:, 1]
    y_pred_binary = (y_pred_proba >= 0.50).astype(int)

    auc = float(roc_auc_score(y_test, y_pred_proba))
    brier = float(brier_score_loss(y_test, y_pred_proba))
    acc = float(accuracy_score(y_test, y_pred_binary))
    prec = float(precision_score(y_test, y_pred_binary))
    rec = float(recall_score(y_test, y_pred_binary))

    print("\n--- Model Performance Metrics ---")
    print(f"ROC-AUC Score:      {auc:.4f}")
    print(f"Brier Score (Calib):{brier:.4f} (closer to 0 is better)")
    print(f"Accuracy:           {acc:.4f}")
    print(f"Precision:          {prec:.4f}")
    print(f"Recall:             {rec:.4f}")

    # 4. Export Artifacts
    base_model_path = os.path.join(ARTIFACTS_DIR, "risk_model_xgboost.joblib")
    calibrated_path = os.path.join(ARTIFACTS_DIR, "calibrated_pipeline.joblib")
    features_path = os.path.join(ARTIFACTS_DIR, "feature_names.json")
    metrics_path = os.path.join(ARTIFACTS_DIR, "model_metrics.json")

    joblib.dump(base_xgb, base_model_path)
    joblib.dump(calibrated_model, calibrated_path)

    with open(features_path, "w") as f:
        json.dump(FEATURE_COLUMNS, f, indent=2)

    metrics_payload = {
        "model_name": "XGBoost-AltCredit-v1.0",
        "evaluation_timestamp": "2026-10-09",
        "sample_count": len(df),
        "test_sample_count": len(X_test),
        "roc_auc": round(auc, 4),
        "brier_score": round(brier, 4),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "features": FEATURE_COLUMNS
    }

    with open(metrics_path, "w") as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"\nArtifacts successfully exported to: {ARTIFACTS_DIR}")
    return base_xgb, calibrated_model, X_train

if __name__ == "__main__":
    train_and_export_model()
