"""
Synthetic Data Generation Module
Generates realistic transaction-level CSV statements for informal economy worker personas
and a 5,000-sample alternative credit feature cohort with Fairlearn audit tags.
"""

import os
import random
import datetime
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_vendor_transactions(
    persona_id: str,
    vendor_name: str,
    business_type: str,
    months: int = 4,
    monthly_receipts_target: float = 38000.0,
    monthly_expense_target: float = 18000.0,
    emi_amount: float = 3000.0,
    daily_tx_count_range: tuple = (4, 12),
    volatility_factor: float = 0.15
):
    """
    Generates realistic daily transaction logs simulating digital UPI receipts,
    supplier inventory debits, and personal utility/EMI expenses.
    """
    records = []
    base_date = datetime.date(2026, 6, 1) # 4 months up to Sep 30, 2026
    total_days = months * 30

    upi_handles = [
        "paytm@upi", "gpay@okaxis", "phonepe@ybl", "bharatpe@icici",
        "kirana_supplier@upi", "dairy_distributor@icici", "subzi_mandi@axis"
    ]

    for day in range(total_days):
        current_date = base_date + datetime.timedelta(days=day)
        
        # Seasonal/day-of-week variation (weekends have 20% higher sales for street food)
        is_weekend = current_date.weekday() >= 5
        day_mult = (1.25 if is_weekend else 0.95) * (1.0 + random.uniform(-volatility_factor, volatility_factor))

        # Daily customer UPI receipts (micro-transactions)
        daily_tx_count = random.randint(*daily_tx_count_range)
        target_daily_receipts = (monthly_receipts_target / 30.0) * day_mult
        
        for _ in range(daily_tx_count):
            # Typical chai / snack / small retail payments: ₹20 to ₹250
            amt = round(max(10.0, np.random.exponential(scale=target_daily_receipts / daily_tx_count)), 2)
            txn_id = f"UPI{current_date.strftime('%Y%m%d')}{random.randint(100000, 999999)}"
            records.append({
                "txn_id": txn_id,
                "date": current_date.strftime("%Y-%m-%d"),
                "direction": "CREDIT",
                "amount": amt,
                "category": "CUSTOMER_RECEIPT",
                "description": f"UPI-QR Payment received {random.choice(upi_handles[:4])}",
                "counterparty": f"Customer_{random.randint(100, 999)}"
            })

        # Supplier / inventory purchases every 2-3 days
        if day % random.choice([2, 3]) == 0:
            supplier_amt = round(random.uniform(800.0, 2200.0), 2)
            records.append({
                "txn_id": f"UPI{current_date.strftime('%Y%m%d')}{random.randint(100000, 999999)}",
                "date": current_date.strftime("%Y-%m-%d"),
                "direction": "DEBIT",
                "amount": supplier_amt,
                "category": "BUSINESS_EXPENSE",
                "description": "Inventory purchase (Tea, milk, spices, packaging)",
                "counterparty": random.choice(upi_handles[4:])
            })

        # Monthly EMI on the 5th of each month
        if current_date.day == 5 and emi_amount > 0:
            records.append({
                "txn_id": f"ACH{current_date.strftime('%Y%m%d')}{random.randint(100000, 999999)}",
                "date": current_date.strftime("%Y-%m-%d"),
                "direction": "DEBIT",
                "amount": emi_amount,
                "category": "EMI_DEBT",
                "description": "Equipment Micro-Loan Auto-Debit EMI",
                "counterparty": "MFI_Lending_NBFC"
            })

        # Monthly Utility / Stall Rent on the 10th
        if current_date.day == 10:
            records.append({
                "txn_id": f"UPI{current_date.strftime('%Y%m%d')}{random.randint(100000, 999999)}",
                "date": current_date.strftime("%Y-%m-%d"),
                "direction": "DEBIT",
                "amount": round(random.uniform(2500.0, 4000.0), 2),
                "category": "BUSINESS_EXPENSE",
                "description": "Monthly Stall Fee & Electricity Bill",
                "counterparty": "Municipal_Stall_Board"
            })

    df = pd.DataFrame(records)
    # Sort chronologically
    df = df.sort_values(by=["date", "txn_id"]).reset_index(drop=True)
    return df


def generate_cohort_dataset(num_samples: int = 5000):
    """
    Generates a 5,000-sample training dataset of alternative cashflow features
    along with calibrated repayment ground truth and protected fairness cohorts.
    """
    rows = []
    
    business_categories = ["street_food", "grocery_kirana", "gig_delivery", "artisan_freelance"]
    geography_tiers = ["tier_1_metro", "tier_2_urban", "tier_3_rural"]
    gender_groups = ["female", "male"]

    for i in range(num_samples):
        biz = random.choice(business_categories)
        geo = random.choices(geography_tiers, weights=[0.45, 0.35, 0.20])[0]
        gender = random.choices(gender_groups, weights=[0.38, 0.62])[0]

        # Monthly gross based on business archetype
        if biz == "grocery_kirana":
            gross = np.random.normal(55000, 12000)
            margin = np.random.uniform(0.18, 0.32)
            cv = np.random.uniform(0.08, 0.22)
            tx_count = np.random.randint(150, 400)
        elif biz == "street_food":
            gross = np.random.normal(38000, 8000)
            margin = np.random.uniform(0.35, 0.55)
            cv = np.random.uniform(0.12, 0.28)
            tx_count = np.random.randint(180, 450)
        elif biz == "gig_delivery":
            gross = np.random.normal(27000, 5000)
            margin = np.random.uniform(0.50, 0.65)
            cv = np.random.uniform(0.15, 0.32)
            tx_count = np.random.randint(80, 200)
        else: # artisan_freelance
            gross = np.random.normal(32000, 10000)
            margin = np.random.uniform(0.40, 0.70)
            cv = np.random.uniform(0.25, 0.55) # Higher lumpiness
            tx_count = np.random.randint(20, 90)

        gross = max(12000.0, float(gross))
        expenses = gross * (1.0 - margin)
        surplus = gross - expenses
        surplus_ratio = surplus / gross

        # Debt obligations
        has_debt = random.random() < 0.65
        emi = random.uniform(1500, surplus * 0.75) if has_debt else 0.0
        debt_to_surplus = emi / max(100.0, surplus)

        # Buffer days
        daily_burn = expenses / 30.0
        buffer_days = float(np.random.exponential(scale=14.0))
        buffer_days = min(60.0, max(1.0, buffer_days))

        # Data coverage
        coverage_months = random.choices([2, 3, 4, 6, 9, 12], weights=[0.1, 0.2, 0.3, 0.2, 0.1, 0.1])[0]

        # Repayment probability calculation (ground truth underlying latent score)
        # High surplus, low CV, low debt, high buffer -> high probability
        z = (
            2.2 * surplus_ratio
            - 2.5 * cv
            - 1.8 * min(1.0, debt_to_surplus)
            + 0.04 * min(30.0, buffer_days)
            + 0.15 * min(6, coverage_months)
            - 0.5
        )
        # Logit link
        prob_repaid = 1.0 / (1.0 + np.exp(-z))
        prob_repaid = float(np.clip(prob_repaid, 0.05, 0.98))

        # Bernoulli outcome
        repaid_status = 1 if random.random() < prob_repaid else 0

        rows.append({
            "applicant_id": f"APP_{10000 + i}",
            "monthly_gross_receipts": round(gross, 2),
            "monthly_operating_expenses": round(expenses, 2),
            "net_surplus_ratio": round(surplus_ratio, 4),
            "income_volatility_cv": round(cv, 4),
            "debt_to_surplus_ratio": round(debt_to_surplus, 4),
            "reserve_buffer_days": round(buffer_days, 1),
            "tx_frequency_monthly": tx_count,
            "data_coverage_months": coverage_months,
            "repaid_status": repaid_status,
            # Protected attributes for Fairlearn audit
            "gender_group": gender,
            "geography_tier": geo,
            "business_category": biz
        })

    return pd.DataFrame(rows)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print("Generating synthetic datasets...")

    # 1. Street Vendor Ramesh
    df_ramesh = generate_vendor_transactions(
        persona_id="ramesh_chai",
        vendor_name="Ramesh Kumar (Shree Balaji Chai Stall)",
        business_type="street_food",
        months=4,
        monthly_receipts_target=41500.0,
        monthly_expense_target=19200.0,
        emi_amount=3200.0,
        daily_tx_count_range=(6, 16),
        volatility_factor=0.12
    )
    ramesh_path = os.path.join(DATA_DIR, "sample_street_vendor_ramesh.csv")
    df_ramesh.to_csv(ramesh_path, index=False)
    print(f"Generated Ramesh's dataset: {len(df_ramesh)} transactions -> {ramesh_path}")

    # 2. Gig Delivery Priya
    df_priya = generate_vendor_transactions(
        persona_id="priya_delivery",
        vendor_name="Priya Sharma (Swiggy/Zomato Delivery Partner)",
        business_type="gig_delivery",
        months=4,
        monthly_receipts_target=28400.0,
        monthly_expense_target=9800.0,
        emi_amount=2100.0,
        daily_tx_count_range=(3, 8),
        volatility_factor=0.18
    )
    priya_path = os.path.join(DATA_DIR, "sample_gig_delivery_priya.csv")
    df_priya.to_csv(priya_path, index=False)
    print(f"Generated Priya's dataset: {len(df_priya)} transactions -> {priya_path}")

    # 3. Volatile Freelancer Arun
    df_arun = generate_vendor_transactions(
        persona_id="arun_freelancer",
        vendor_name="Arun Verma (Independent Artisan & Carpenter)",
        business_type="artisan_freelance",
        months=4,
        monthly_receipts_target=32000.0,
        monthly_expense_target=14000.0,
        emi_amount=4500.0,
        daily_tx_count_range=(1, 3),
        volatility_factor=0.45
    )
    arun_path = os.path.join(DATA_DIR, "sample_volatile_freelancer_arun.csv")
    df_arun.to_csv(arun_path, index=False)
    print(f"Generated Arun's dataset: {len(df_arun)} transactions -> {arun_path}")

    # 4. Training Cohort of 5,000 applicants
    df_cohort = generate_cohort_dataset(num_samples=5000)
    cohort_path = os.path.join(DATA_DIR, "training_cohort_5000.csv")
    df_cohort.to_csv(cohort_path, index=False)
    print(f"Generated Training Cohort: {len(df_cohort)} applicants -> {cohort_path}")


if __name__ == "__main__":
    main()
