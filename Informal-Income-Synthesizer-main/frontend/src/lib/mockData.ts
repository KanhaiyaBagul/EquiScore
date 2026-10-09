/**
 * Mock Data Repository
 * Provides authentic fallback data for instant zero-latency client previews
 * aligned directly with the backend models (Ramesh, Priya, Arun).
 */

export interface PersonaSummary {
  id: string;
  name: string;
  business: string;
  type: string;
  gross: number;
  expenses: number;
  surplus: number;
  emi: number;
  cv: number;
  fhs: number;
  prob: number;
  tier: string;
  decision: string;
}

export const PRESETS: Record<string, PersonaSummary> = {
  ramesh: {
    id: "ramesh",
    name: "Ramesh Kumar",
    business: "Shree Balaji Chai Stall",
    type: "Street Food Vendor",
    gross: 42995,
    expenses: 22928,
    surplus: 20067,
    emi: 3200,
    cv: 0.043,
    fhs: 86,
    prob: 78.2,
    tier: "TIER 1 LOW RISK",
    decision: "ELIGIBLE"
  },
  priya: {
    id: "priya",
    name: "Priya Sharma",
    business: "Swiggy & Zomato Delivery",
    type: "Gig Delivery Partner",
    gross: 28400,
    expenses: 9800,
    surplus: 18600,
    emi: 2100,
    cv: 0.12,
    fhs: 79,
    prob: 72.5,
    tier: "TIER 1 LOW RISK",
    decision: "ELIGIBLE"
  },
  arun: {
    id: "arun",
    name: "Arun Verma",
    business: "Artisan Woodcraft & Carpentry",
    type: "Independent Artisan",
    gross: 32000,
    expenses: 14000,
    surplus: 18000,
    emi: 6500,
    cv: 0.45,
    fhs: 58,
    prob: 54.1,
    tier: "TIER 3 ELEVATED RISK",
    decision: "CONDITIONAL APPROVAL"
  }
};

export const MOCK_SHAP_RAMESH = [
  { feature_label: "Income Volatility (CV)", shap_value: 0.858, impact_direction: "REDUCES_RISK", value_formatted: "0.043 CV" },
  { feature_label: "Debt Burden Ratio", shap_value: 0.158, impact_direction: "REDUCES_RISK", value_formatted: "15.9% of surplus" },
  { feature_label: "Monthly Gross Turnover", shap_value: 0.102, impact_direction: "REDUCES_RISK", value_formatted: "INR 42,995" },
  { feature_label: "Operating Surplus Ratio", shap_value: 0.039, impact_direction: "REDUCES_RISK", value_formatted: "46.7% margin" },
  { feature_label: "Statement Coverage", shap_value: -0.081, impact_direction: "INCREASES_RISK", value_formatted: "4 months" },
  { feature_label: "Monthly UPI Velocity", shap_value: -0.173, impact_direction: "INCREASES_RISK", value_formatted: "315 txns" },
];

export const MOCK_MONTHLY_TREND = [
  { month: "Jun 2026", gross: 43119, expenses: 21012, surplus: 22107 },
  { month: "Jul 2026", gross: 45047, expenses: 25490, surplus: 19556 },
  { month: "Aug 2026", gross: 40555, expenses: 16623, surplus: 23932 },
  { month: "Sep 2026", gross: 43259, expenses: 28588, surplus: 14671 },
];
