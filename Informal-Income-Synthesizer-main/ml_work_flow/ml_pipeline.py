import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import shap
import joblib
import os

def generate_data(num_samples=5000, filename='data.csv'):
    np.random.seed(42)
    
    # Generate features representing unbanked borrowers
    # 1. Utility bill consistency (0.0 to 1.0) - proxy for payment reliability
    utility_bill_consistency = np.random.beta(a=5, b=2, size=num_samples)
    
    # 2. Mobile/UPI transactional velocity (transactions per month, 10 to 500) - proxy for cash flow
    upi_transaction_velocity = np.random.randint(10, 501, size=num_samples)
    
    # 3. Seasonal inventory turnover (1.0 to 12.0) - proxy for business health
    seasonal_inventory_turnover = np.random.uniform(1.0, 12.0, size=num_samples)
    
    # 4. Age of business in months (1 to 120) - proxy for stability
    business_age_months = np.random.randint(1, 121, size=num_samples)
    
    # Calculate a latent risk score (higher score = lower risk of default)
    # Give different weights to the risk factors
    risk_score = (
        (utility_bill_consistency * 2.5) + 
        (upi_transaction_velocity / 100) + 
        (seasonal_inventory_turnover / 2.5) +
        (business_age_months / 40)
    )
    
    # Add some noise to make it realistic
    risk_score += np.random.normal(0, 1.5, size=num_samples)
    
    # Threshold for default (1 = default, 0 = no default)
    # Lower risk score -> higher chance of default
    # Let's target a default rate around ~30%
    threshold = np.percentile(risk_score, 30)
    default_risk = (risk_score < threshold).astype(int)
    
    # Create DataFrame
    df = pd.DataFrame({
        'utility_bill_consistency': utility_bill_consistency,
        'upi_transaction_velocity': upi_transaction_velocity,
        'seasonal_inventory_turnover': seasonal_inventory_turnover,
        'business_age_months': business_age_months,
        'default_risk': default_risk
    })
    
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename} ({num_samples} records)")
    return df

def train_and_evaluate():
    print("Loading data...")
    train_df = pd.read_csv('train_data.csv')
    test_df = pd.read_csv('test_data.csv')
    
    X_train = train_df.drop('default_risk', axis=1)
    y_train = train_df['default_risk']
    
    X_test = test_df.drop('default_risk', axis=1)
    y_test = test_df['default_risk']
    
    print("\nTraining XGBoost model...")
    # Initialize XGBoost Classifier
    model = xgb.XGBClassifier(
        n_estimators=100, 
        learning_rate=0.1, 
        max_depth=5, 
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)
    
    # Save the trained model
    joblib.dump(model, 'credit_xgboost_model.pkl')
    print("Model saved to credit_xgboost_model.pkl")
    
    # Evaluate model
    print("\nEvaluating model on test data...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("ROC AUC Score:", roc_auc_score(y_test, y_prob))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    
    # Explainability with SHAP
    print("\n--- SHAP Explanations ---")
    print("Generating SHAP explanations for the first test instance to simulate underwriting output...")
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    
    # Display explanation for the first instance
    instance_idx = 0
    instance_features = X_test.iloc[instance_idx]
    
    print(f"\nBorrower Profile (Instance {instance_idx}):")
    print(instance_features.to_string())
    print(f"\nTrue Label (Actual Risk): {'Default (1)' if y_test.iloc[instance_idx] == 1 else 'No Default (0)'}")
    
    predicted_label = model.predict(X_test.iloc[[instance_idx]])[0]
    predicted_prob = y_prob[instance_idx]
    print(f"Predicted Risk Label: {'Default (1)' if predicted_label == 1 else 'No Default (0)'} (Probability: {predicted_prob:.2f})")
    
    # For XGBoost, shap_values is a single array where positive values push the prediction towards 1 (Default)
    sv_instance = shap_values[instance_idx]
    
    print("\nFeature Contributions to this specific prediction (SHAP Values):")
    contributions = []
    for feature, value in zip(X_test.columns, sv_instance):
        impact = "Increased Default Risk" if value > 0 else "Decreased Default Risk"
        contributions.append((feature, value, impact))
        
    # Sort by absolute impact
    contributions.sort(key=lambda x: abs(x[1]), reverse=True)
    
    for feature, value, impact in contributions:
        print(f"- {feature}: {value:+.4f} ({impact})")
        
    print("\nThis explanation can be directly fed into the risk portal frontend to show the loan officer WHY a loan was approved or denied.")
    
if __name__ == "__main__":
    print("Step 1: Generating training data for model creation")
    generate_data(10000, 'train_data.csv')
    
    print("\nStep 2: Generating separate testing data for validation")
    generate_data(2000, 'test_data.csv')
    
    print("\nStep 3: Training model and generating SHAP explanations")
    train_and_evaluate()
    print("\nPipeline execution completed successfully!")
