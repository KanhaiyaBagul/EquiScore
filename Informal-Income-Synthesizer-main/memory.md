# Project Memory & Living Implementation Log

**Codename:** EquiScore / VeritasCredit  
**Domain:** Alternative Credit Scoring & Explainable AI for the Informal Economy  
**Active Execution Strategy:** **Option 1 — ML & Engine First (The Brain Pipeline)**  
**Design Reference:** Meiro SaaS UI Style (Obsidian Dark `#0A0B0D` + Electric Lime `#D2FC38`)

---

## 1. Architectural Strategy & Decision Memory

### Key Decision: Why Option 1 (ML & Data Core First)?
1. **Model-Grounded Authenticity:** By training the alternative credit risk model, building the synthetic transaction datasets, and generating true SHAP values first, our frontend dashboard and landing page widgets will never display fake, dummy, or hardcoded mock placeholders.
2. **Deterministic & Explainable Pipeline Validation:** The two core engines:
   - **Engine A: Deterministic Financial Health Score (FHS)** (Formula-based, 0–100, no training required).
   - **Engine B: Alternative Credit Risk Model (XGBoost)** (Trained on cashflow features, evaluated with SHAP TreeExplainer and Fairlearn).
   are verified mathematically before writing UI code.
3. **Reproducibility Guarantee:** Any borrower evaluation in the UI can be audited back to the raw transaction CSV, feature extraction, model inference, SHAP attribution, and underwriting policy rules.

---

## 2. Machine Learning Specifications & Artifact Registry

### 2.1 Model Architecture & Hyperparameters
- **Primary Model:** Calibrated XGBoost Classifier (`XGBClassifier` with `CalibratedClassifierCV(method='sigmoid')`).
- **Target Variable ($y$):** `repaid_status` (1 = Loan successfully repaid without 30+ day default, 0 = Default / severely delinquent).
- **Objective:** `binary:logistic`, evaluated using ROC-AUC, Brier Score (calibration), and Log-Loss.
- **Estimated Baseline ($\phi_0$):** Expected value of the training distribution (approx. 0.65 – 0.75 repayment probability).

### 2.2 Feature Dictionary (Alternative Cashflow Features)
| Feature Name | Type | Description | Range / Units |
| :--- | :--- | :--- | :--- |
| `monthly_gross_receipts` | Float | Average monthly digital/cash income turnover | ₹10,000 – ₹150,000 |
| `monthly_operating_expenses` | Float | Average monthly direct business costs | ₹5,000 – ₹90,000 |
| `net_surplus_ratio` | Float | $\frac{\text{Net Surplus}}{\text{Gross Receipts}} = \frac{R_m - E_m}{R_m}$ | 0.05 – 0.70 |
| `income_volatility_cv` | Float | Coefficient of Variation ($\sigma / \mu$) of monthly receipts | 0.05 – 0.65 (Lower is better) |
| `debt_to_surplus_ratio` | Float | Existing monthly loan EMIs divided by net monthly surplus | 0.00 – 0.90 |
| `reserve_buffer_days` | Float | Liquidity runway: $\frac{\text{Min Ledger Balance}}{\text{Daily Avg Expenses}}$ | 0 – 60 days |
| `tx_frequency_monthly` | Integer| Number of customer transactions per month (UPI velocity) | 15 – 450 transactions |
| `data_coverage_months` | Integer| Number of contiguous months of financial data provided | 2 – 12 months |

### 2.3 Fairlearn Audit & Sensitive Group Attributes
To audit algorithmic fairness without leaking protected features into model training:
- **Protected Features (Excluded from Training, Tracked for Auditing Only):**
  - `gender_group` (`female`, `male`, `unspecified`)
  - `geography_tier` (`tier_1_metro`, `tier_2_urban`, `tier_3_rural`)
  - `business_category` (`street_food`, `grocery_kirana`, `gig_delivery`, `artisan_freelance`)
- **Fairness Metrics Thresholds:**
  - Demographic Parity Difference $< 0.10$
  - Equalized Odds Difference $< 0.10$

---

## 3. Visual Design System & Color Tokens (Black & White Minimalist)

**Active Git Branch:** `feature/black-and-white-ui`  
**Design Style:** Stark Monochrome Minimalist (High contrast, editorial Swiss design, Apple/Vercel/Linear precision)

```
+-----------------------------------------------------------------------------------------+
|                                    PALETTE SWATCHES                                     |
+--------------------+--------------------+--------------------+--------------------------+
| Canvas Pitch Black | Elevated Surface   | Border / Stroke    | Stark White Accent       |
| #000000            | #0A0A0A / #121212  | #222222 / #333333  | #FFFFFF                  |
+--------------------+--------------------+--------------------+--------------------------+
| Text Primary       | Text Secondary     | Text Muted         | Status Indicators        |
| #FFFFFF            | #A1A1AA (Zinc 400) | #71717A (Zinc 500) | #FFFFFF / #D4D4D8        |
+-----------------------------------------------------------------------------------------+
```

### Exact CSS Variables
```css
:root {
  --bg-canvas: #000000;
  --bg-surface: #0A0A0A;
  --bg-card: #121212;
  --bg-card-hover: #181818;
  --border-subtle: #222222;
  --border-focus: #333333;
  --border-strong: #444444;
  --accent-white: #FFFFFF;
  --accent-text: #000000;
  --text-primary: #FFFFFF;
  --text-secondary: #A1A1AA;
  --text-muted: #71717A;
}
```

---

## 4. Typography & Font Hierarchy
- **Body & Headings:** `Outfit` or `Plus Jakarta Sans`
- **Numbers, Metrics & Code:** `JetBrains Mono`

---

## 5. Implementation Log & Brain Status

| Timestamp | Phase | Task ID | Work Item Completed | Artifact / Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **2026-10-09** | Architecture | Strategic Setup | Created `objective.md`, `memory.md`, `architecture.md`, `tasks.md`. | Foundational specification established. |
| **2026-10-09** | Decision | Strategy Alignment | Selected **Option 1: ML & Engine First** pipeline. | Updated all project markdown files. |
| **2026-10-09** | Phase 1 | Task 1.1 | Installed data science & backend dependencies (`xgboost`, `shap`, `fairlearn`, `reportlab`). | `backend/requirements.txt` |
| **2026-10-09** | Phase 1 | Task 1.2 | Generated authentic synthetic datasets (Ramesh 1,357 txns, Priya 749 txns, Arun 319 txns, Cohort 5,000). | `backend/data/` |
| **2026-10-09** | Phase 1 | Task 1.3 | Trained Calibrated XGBoost credit risk model (Sigmoid Platt scaling). | `backend/ml/artifacts/calibrated_pipeline.joblib` |
| **2026-10-09** | Phase 1 | Task 1.4 | Initialized and exported SHAP `TreeExplainer` & verified additivity ($ diff < 0.01 $). | `backend/ml/artifacts/shap_explainer.joblib` |
| **2026-10-09** | Phase 1 | Task 1.5 | Conducted Fairlearn algorithmic disparity audit across gender, geography, and business categories. | `backend/ml/artifacts/fairness_audit_report.json` |
| **2026-10-09** | Phase 1 | Task 1.6 | Implemented deterministic 5-pillar Financial Health Score (FHS) formula (0–100 scale). | `backend/app/services/financial_health_service.py` |
| **2026-10-09** | Phase 2 | Tasks 2.1–2.4 | Built FastAPI backend (`income_service.py`, `scenario_service.py`, `decision_service.py`, `passport_service.py`, `main.py`). | `backend/main.py` (All endpoints tested 200 OK) |
| **2026-10-09** | Phase 3 | Tasks 3.1–3.3 | Initialized Astro 5.x project with Tailwind, React, and Meiro Obsidian-Lime tokens. | `frontend/src/styles/global.css` |
| **2026-10-09** | Phase 4 | Tasks 4.1–4.5 | Built high-converting Landing Page with Hero, FeatureGrid, HowItWorks, VendorStory, and interactive `ScoreTeaser.tsx`. | `frontend/src/pages/index.astro` |
| **2026-10-09** | Phase 5 | Tasks 5.1–5.4 | Built Meiro Applicant Dashboard, SHAP attributions, What-If Sandbox (`simulator.astro`), and Fairlearn portal (`fairness.astro`). | `frontend/src/pages/dashboard.astro`, `simulator.astro`, `fairness.astro` |
| **2026-10-09** | Phase 6 | Tasks 6.1–6.3 | Built Digital Financial Passport preview & ReportLab PDF download (`passport.astro`), verified build (5 static pages in 5.33s). | `frontend/src/pages/passport.astro`, `frontend/dist/` |
| **2026-10-09** | Phase 7 | Dynamic Data & Upload | Replaced all static placeholders across Dashboard, What-If Simulator, and Passport with real dynamic data from uploaded/preset CSVs. Enhanced CSV schema normalization, added `/api/sample-csv` download endpoint, and created `LiveDashboard.tsx` & `DigitalPassportViewer.tsx`. | `feature/dynamic-uploaded-data` |
