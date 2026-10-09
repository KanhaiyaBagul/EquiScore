import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import joblib

class AutonomousRiskAgent:
    def __init__(self, data_path):
        self.data_path = data_path
        self.model = None
        self.scaler = StandardScaler()
        self.outlier_detector = IsolationForest(contamination=0.05, random_state=42) # Expect ~5% noisy data

    def run_pipeline(self):
        print("[Autonomous Agent] Starting execution cycle...")
        
        # 1. Ingest Data
        df = self.ingest_data()
        
        # 2. Detect and Remove Noisy Data
        clean_df = self.clean_noisy_data(df)
        
        # 3. Feature Engineering & Preprocessing
        X_train, X_test, y_train, y_test = self.preprocess(clean_df)
        
        # 4. Train Model
        self.train_model(X_train, y_train)
        
        # 5. Evaluate
        self.evaluate(X_test, y_test)
        
        print("[Autonomous Agent] Cycle complete. System is ready for live predictions.")

    def ingest_data(self):
        print(f"[Agent] Ingesting data from {self.data_path}...")
        df = pd.read_csv(self.data_path)
        print(f"   -> Loaded {len(df)} records.")
        return df

    def clean_noisy_data(self, df):
        print("[Agent] Scanning for noisy data and outliers...")
        # We only use features for outlier detection, not the target label
        features = df.drop('default_risk', axis=1)
        
        # Predict anomalies (-1 for outliers, 1 for inliers)
        outlier_labels = self.outlier_detector.fit_predict(features)
        
        # Filter out the noisy data
        clean_df = df[outlier_labels == 1].copy()
        noise_count = len(df) - len(clean_df)
        
        print(f"   -> Detected and removed {noise_count} noisy/anomalous records.")
        return clean_df

    def preprocess(self, df):
        print("[Agent] Scaling features and splitting data...")
        X = df.drop('default_risk', axis=1)
        y = df['default_risk']
        
        # Scale features
        X_scaled = pd.DataFrame(self.scaler.fit_transform(X), columns=X.columns)
        
        # Save scaler for frontend use
        joblib.dump(self.scaler, 'agent_scaler.pkl')
        
        return train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    def train_model(self, X_train, y_train):
        print("[Agent] Training XGBoost Engine on clean data...")
        self.model = xgb.XGBClassifier(
            n_estimators=100, 
            learning_rate=0.1, 
            max_depth=5, 
            random_state=42,
            eval_metric='logloss'
        )
        self.model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(self.model, 'agent_xgboost_model.pkl')
        print("   -> Model updated and saved to 'agent_xgboost_model.pkl'.")

    def evaluate(self, X_test, y_test):
        print("[Agent] Evaluating performance...")
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"   -> Accuracy achieved: {acc * 100:.2f}%")

if __name__ == "__main__":
    agent = AutonomousRiskAgent('train_data.csv')
    agent.run_pipeline()
