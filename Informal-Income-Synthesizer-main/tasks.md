# Granular Project Roadmap & Actionable Task Breakdown

**Project:** Explainable Alternative Credit Scoring & Informal Income Synthesizer  
**Execution Strategy:** **Option 1 — ML & Engine First (The Brain Pipeline)**  
**Status Tracking:** `[ ]` Not Started | `[/]` In Progress | `[x]` Completed

---

## Strategic Phase Overview

```
+--------------------------------------------------------------------------------------------------+
|                                    EXECUTION ROADMAP                                             |
+----------------------------------+----------------------------------+----------------------------+
| PHASE 1: DATA & ML BRAIN CORE    | PHASE 2: FASTAPI BACKEND         | PHASE 3: ASTRO 5.x SHELL   |
| Synthetic data, XGBoost model,   | Income Synthesizer, FHS scoring, | Obsidian-Lime tokens,      |
| SHAP Explainer, Fairlearn audit. | SHAP service, Scenario sandbox.  | layouts, Astro components. |
+----------------------------------+----------------------------------+----------------------------+
| PHASE 4: LANDING PAGE & TEASER   | PHASE 5: APPLICANT DASHBOARD     | PHASE 6: PASSPORT & POLISH |
| Hero, quick-bite features,       | Meiro-style analytics, SHAP      | Policy reasons, ReportLab  |
| interactive Score Teaser island. | waterfall, What-If simulator.    | PDF, end-to-end demo test. |
+----------------------------------+----------------------------------+----------------------------+
```

---

## Phase 1: Data & Machine Learning Core (The Brain)

### [x] Task 1.1: Setup Backend Environment & Dependencies
- **Status:** COMPLETED. Installed `xgboost`, `shap`, `fairlearn`, `reportlab`, `pandas`, `fastapi`, and verified imports.

### [x] Task 1.2: Generate Authentic Synthetic Vendor Datasets
- **Status:** COMPLETED. Generated `sample_street_vendor_ramesh.csv`, `sample_gig_delivery_priya.csv`, `sample_volatile_freelancer_arun.csv`, and `training_cohort_5000.csv`.

### [x] Task 1.3: Train Calibrated XGBoost Alternative Credit Risk Model
- **Status:** COMPLETED. Trained calibrated XGBoost classifier and exported artifacts (`risk_model_xgboost.joblib`, `calibrated_pipeline.joblib`, `model_metrics.json`).

### [x] Task 1.4: Build SHAP TreeExplainer & Feature Attribution Exporter
- **Status:** COMPLETED. Exported `shap_explainer.joblib`, `baseline_value.json` and verified additive mathematical consistency.

### [x] Task 1.5: Build Fairlearn Demographic Parity & Bias Audit Engine
- **Status:** COMPLETED. Audited across gender, geography, and business categories; exported `fairness_audit_report.json`.

### [x] Task 1.6: Implement Deterministic Financial Health Score (FHS) Engine
- **Status:** COMPLETED. Implemented `financial_health_service.py` with 5-pillar mathematical formula and unit tests.

---

## Phase 2: FastAPI Backend Services & API Gateway

### [x] Task 2.1: Transaction Service & Informal Income Synthesizer
- **Status:** COMPLETED. Built `transaction_service.py` & `income_service.py` supporting presets and custom CSV uploads.

### [x] Task 2.2: Unified Assessment Orchestrator Endpoint
- **Status:** COMPLETED. Built `backend/main.py` with `/api/assessments/preset` and `/api/assessments/upload`.

### [x] Task 2.3: Isolated What-If Scenario Sandbox Service
- **Status:** COMPLETED. Built `scenario_service.py` & `/api/scenarios` with zero mutation guarantee.

### [x] Task 2.4: Policy Underwriting Rules & Digital Passport PDF Service
- **Status:** COMPLETED. Built `decision_service.py`, `passport_service.py` (ReportLab), and `/api/reports/{id}/download`.

---

## Phase 3: Astro 5.x Frontend Foundation & Meiro UI System

### [x] Task 3.1: Initialize Astro 5.x Project with Tailwind & React Islands
- **Status:** COMPLETED. Astro 5.x project configured with `@astrojs/tailwind` and `@astrojs/react`.

### [x] Task 3.2: Implement Obsidian-Lime Design Tokens & Global Styles
- **Status:** COMPLETED. Built `global.css` and `tailwind.config.cjs` using Meiro palette (`#0A0B0D`, `#D2FC38`).

### [x] Task 3.3: Build Core Reusable Astro Presentation Components
- **Status:** COMPLETED. Built `Navbar.astro`, `Footer.astro`, `Hero.astro`, and `BaseLayout.astro`.

---

## Phase 4: High-Converting Landing Page & Quick-Feature Showcase

### [x] Task 4.1: Build Landing Page Hero Section with Live Trust Ticker
- **Status:** COMPLETED. Built `Hero.astro` with high contrast, trust ticker, and institutional copy.

### [x] Task 4.2: Build Interactive Score Teaser Island (React Island)
- **Status:** COMPLETED. Built `ScoreTeaser.tsx` with persona toggles and reactive real-time sliders.

### [x] Task 4.3: Build 6-Core Innovation Feature Grid
- **Status:** COMPLETED. Built `FeatureGrid.astro` highlighting Synthesizer, FHS, SHAP, Fairness, Sandbox, and Passport.

### [x] Task 4.4: Build Workflow Steps & Vendor Journey Showcase
- **Status:** COMPLETED. Built `HowItWorks.astro` and `VendorStory.astro` (Ramesh case study).

### [x] Task 4.5: Assemble and Polish Landing Page (`index.astro`)
- **Status:** COMPLETED. `index.astro` assembled and compiled with zero build errors.

---

## Phase 5: Applicant Dashboard, SHAP Waterfall & What-If Simulator

### [x] Task 5.1: Build Meiro-Style Applicant Dashboard (`dashboard.astro`)
- **Status:** COMPLETED. Built `dashboard.astro` with Meiro KPI cards, monthly ledger table, and FHS bands.

### [x] Task 5.2: Build SHAP Waterfall Attribution Island & Screen
- **Status:** COMPLETED. Built SHAP feature attribution forces bars and grounded natural language explanations.

### [x] Task 5.3: Build What-If Financial Sandbox Screen (`simulator.astro`)
- **Status:** COMPLETED. Built `simulator.astro` & `WhatIfSimulator.tsx` with dual-column before/after slider comparison.

### [x] Task 5.4: Build Fairlearn Model Governance Portal (`fairness.astro`)
- **Status:** COMPLETED. Built `fairness.astro` with demographic parity metrics and cohort selection rate table.

---

## Phase 6: Underwriting Decisions, Digital Passport & Final Polish

### [x] Task 6.1: Build Transparent Decision Page
- **Status:** COMPLETED. Integrated 5 policy rules checklist and reason codes into `dashboard.astro`.

### [x] Task 6.2: Build Digital Financial Passport Viewer & PDF Export (`passport.astro`)
- **Status:** COMPLETED. Built `passport.astro` preview dossier and direct download hook to ReportLab PDF generator.

### [x] Task 6.3: End-to-End Integration, Testing & Live Demo Verification
- **Status:** COMPLETED. Verified backend API tests (100% 200 OK) and frontend static build (6 pages built in 2.08s).

---

## Phase 7: Dynamic Data Pipeline & Statement Upload

### [x] Task 7.1: Flexible CSV Ingestion & Categorization
- **Status:** COMPLETED. Added support for case-insensitive headers, banking/UPI aliases, and robust debit/credit/loan categorization in `transaction_service.py` and `income_service.py`.
- **Files:** `backend/app/services/transaction_service.py`, `backend/app/services/income_service.py`.

### [x] Task 7.2: Standardized Sample CSV Template Generator
- **Status:** COMPLETED. Added `GET /api/sample-csv` endpoint serving verified vendor statements directly for fast testing.
- **Files:** `backend/main.py`.

### [x] Task 7.3: Dynamic Live Dashboard (Zero Static Placeholders)
- **Status:** COMPLETED. Built `LiveDashboard.tsx` to dynamically query and render active applicant metrics, reconstructed monthly cashflow ledger, SHAP waterfall forces, and underwriting policy criteria checklist.
- **Files:** `frontend/src/components/react/LiveDashboard.tsx`, `frontend/src/pages/dashboard.astro`.

### [x] Task 7.4: Dynamic What-If Sandbox with Uploaded Baseline Support
- **Status:** COMPLETED. Updated `WhatIfSimulator.tsx` to simulate directly against uploaded applicant baseline metrics in isolated memory.
- **Files:** `frontend/src/components/react/WhatIfSimulator.tsx`.

### [x] Task 7.5: Dynamic Digital Financial Passport & ReportLab PDF Hook
- **Status:** COMPLETED. Built `DigitalPassportViewer.tsx` to display active applicant dossier and wire direct download link to `http://localhost:8000/api/reports/{id}/download`.
- **Files:** `frontend/src/components/react/DigitalPassportViewer.tsx`, `frontend/src/pages/passport.astro`.
