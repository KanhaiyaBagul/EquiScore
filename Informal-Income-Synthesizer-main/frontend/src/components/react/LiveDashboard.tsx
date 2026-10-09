import React, { useEffect, useState } from 'react';
import { 
  AreaChart, Area, PieChart, Pie, Cell, BarChart, Bar,
  XAxis, YAxis, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';interface MonthlySummary {
  month_period: string;
  gross_receipts: number;
  operating_expenses: number;
  debt_emi_payments: number;
  net_operating_surplus: number;
  customer_tx_count: number;
}

interface ShapAttribution {
  feature_name: string;
  feature_label: string;
  feature_value: number;
  shap_value: number;
  value_formatted?: string;
  feature_value_formatted?: string;
  impact_direction?: string;
}

interface RuleResult {
  rule_id: string;
  rule_name: string;
  is_passed?: boolean;
  passed?: boolean;
  actual_value_formatted?: string;
  actual_value?: any;
  target_threshold?: string;
  threshold_condition?: string;
  description?: string;
}

interface AssessmentData {
  assessment_id: string;
  applicant_name: string;
  business_name: string;
  business_type: string;
  income_synthesis: {
    average_monthly_gross_receipts: number;
    average_monthly_expenses: number;
    average_monthly_debt_emi: number;
    average_monthly_net_surplus: number;
    net_surplus_ratio: number;
    income_volatility_cv: number;
    min_observed_balance: number;
    total_tx_count: number;
    data_coverage_months: number;
    coverage_reliability_percent: number;
    monthly_trend: MonthlySummary[];
    anomaly_flags: string[];
  };
  financial_health_score: {
    overall_score: number;
    health_band: string;
    pillar_scores: Record<string, number>;
    strengths: string[];
    risk_factors: string[];
  };
  credit_risk_ml: {
    repayment_probability_percent: number;
    default_probability_percent: number;
    risk_tier: string;
    model_version: string;
    baseline_expected_probability: number;
    attributions: ShapAttribution[];
    plain_language_narrative?: string;
  };
  underwriting_decision: {
    decision_status: string;
    passed_count?: number;
    rules_passed_count?: number;
    total_rules_count: number;
    criteria_evaluated?: RuleResult[];
    rule_results?: RuleResult[];
    primary_reason_codes?: string[];
    reason_codes?: string[];
    actionable_next_steps?: string[];
    actionable_recommendations?: string[];
  };
}

export default function LiveDashboard() {
  const [assessment, setAssessment] = useState<AssessmentData | null>(null);
  const [activeSource, setActiveSource] = useState<string>('arun');
  const [loading, setLoading] = useState<boolean>(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // Switch between CSV datasets
  const switchCsvDataset = async (key: string) => {
    setActiveSource(key);
    setLoading(true);
    setFetchError(null);
    try {
      const res = await fetch(`http://localhost:8000/api/assessments/${key}`);
      if (res.ok) {
        const data: AssessmentData = await res.json();
        setAssessment(data);
        localStorage.setItem('equiscore_current_assessment', JSON.stringify(data));
        window.dispatchEvent(new CustomEvent('equiscore_assessment_updated', { detail: data }));
      } else {
        throw new Error(`Failed to load dataset: ${res.statusText}`);
      }
    } catch (e: any) {
      setFetchError(e.message || "Could not load dataset from backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setFetchError(null);
      const params = new URLSearchParams(window.location.search);
      const queryId = params.get('id');
      const queryPersona = params.get('persona');

      // 1. If explicit queryId is in URL, fetch that assessment directly from backend
      if (queryId) {
        try {
          const res = await fetch(`http://localhost:8000/api/assessments/${queryId}`);
          if (res.ok) {
            const data: AssessmentData = await res.json();
            setAssessment(data);
            setActiveSource('custom');
            localStorage.setItem('equiscore_current_assessment', JSON.stringify(data));
            window.dispatchEvent(new CustomEvent('equiscore_assessment_updated', { detail: data }));
            setLoading(false);
            return;
          }
        } catch (e) {
          console.warn("Could not fetch queryId assessment", e);
        }
      }

      // 2. If explicit queryPersona is in URL, fetch that persona CSV from backend
      if (queryPersona) {
        try {
          const res = await fetch(`http://localhost:8000/api/assessments/${queryPersona.toLowerCase()}`);
          if (res.ok) {
            const data: AssessmentData = await res.json();
            setAssessment(data);
            setActiveSource(queryPersona.toLowerCase());
            localStorage.setItem('equiscore_current_assessment', JSON.stringify(data));
            window.dispatchEvent(new CustomEvent('equiscore_assessment_updated', { detail: data }));
            setLoading(false);
            return;
          }
        } catch (e) {
          console.warn("Could not fetch queryPersona assessment", e);
        }
      }

      // 3. Check if localStorage has an active uploaded assessment with real ID
      const cached = localStorage.getItem('equiscore_current_assessment');
      if (cached) {
        try {
          const parsed: AssessmentData = JSON.parse(cached);
          if (parsed && parsed.assessment_id && parsed.income_synthesis) {
            setAssessment(parsed);
            if (parsed.applicant_name?.toLowerCase().includes('arun')) setActiveSource('arun');
            else if (parsed.applicant_name?.toLowerCase().includes('ramesh')) setActiveSource('ramesh');
            else if (parsed.applicant_name?.toLowerCase().includes('priya')) setActiveSource('priya');
            else setActiveSource('custom');
            window.dispatchEvent(new CustomEvent('equiscore_assessment_updated', { detail: parsed }));
            setLoading(false);
            return;
          }
        } catch (e) {
          console.warn("Failed to parse cached assessment", e);
        }
      }

      // 4. Fallback: Fetch Arun's real CSV statement directly from backend
      try {
        const res = await fetch('http://localhost:8000/api/assessments/arun');
        if (res.ok) {
          const data: AssessmentData = await res.json();
          setAssessment(data);
          setActiveSource('arun');
          localStorage.setItem('equiscore_current_assessment', JSON.stringify(data));
          window.dispatchEvent(new CustomEvent('equiscore_assessment_updated', { detail: data }));
        } else {
          setFetchError("Unable to load financial assessment from backend.");
        }
      } catch (err: any) {
        setFetchError("Backend server offline. Please verify FastAPI is running at http://localhost:8000.");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center space-y-4">
        <div className="w-8 h-8 rounded-full border-2 border-white border-t-transparent animate-spin"></div>
        <p className="text-sm font-mono text-neutral-400">Loading verified CSV assessment from backend engine...</p>
      </div>
    );
  }

  if (fetchError || !assessment) {
    return (
      <div className="py-16 text-center space-y-4">
        <p className="text-neutral-400 font-mono text-sm">{fetchError || "Assessment data could not be loaded."}</p>
        <button
          onClick={() => switchCsvDataset('arun')}
          className="btn-white text-xs py-2 px-4 shadow-white-glow"
        >
          Retry with sample_volatile_freelancer_arun.csv
        </button>
      </div>
    );
  }

  const { income_synthesis, financial_health_score, credit_risk_ml, underwriting_decision } = assessment;
  const isEligible = underwriting_decision.decision_status.includes('ELIGIBLE') || underwriting_decision.decision_status.includes('PRE-APPROVED');
  const operatingMargin = ((income_synthesis.average_monthly_net_surplus / Math.max(1, income_synthesis.average_monthly_gross_receipts)) * 100).toFixed(1);

  const activeFilename = 
    activeSource === 'arun' ? 'sample_volatile_freelancer_arun.csv' :
    activeSource === 'ramesh' ? 'sample_street_vendor_ramesh.csv' :
    activeSource === 'priya' ? 'sample_gig_delivery_priya.csv' :
    'custom_uploaded_statement.csv';

  return (
    <div className="space-y-6">
      {/* Welcome & Profile Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase font-mono tracking-wider text-neutral-400">Verified Dossier</span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#1A1A1A] text-neutral-300 border border-[#2E2E2E]">
              ID: {assessment.assessment_id}
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white mt-1">
            {assessment.applicant_name} — {assessment.business_name}
          </h2>
          <p className="text-xs text-text-secondary mt-1 font-light">
            Archetype: <span className="text-white font-medium capitalize">{assessment.business_type.replace('_', ' ')}</span> • {income_synthesis.data_coverage_months} Months Verified • {income_synthesis.total_tx_count.toLocaleString()} Normalized Transactions
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className={`px-3 py-1.5 rounded-full text-xs font-semibold font-mono border ${
            isEligible 
              ? 'bg-white text-black border-white' 
              : 'bg-[#181818] text-white border-[#333333]'
          }`}>
            Status: <strong>{underwriting_decision.decision_status}</strong>
          </span>
          <a href="/upload" className="btn-dark text-xs py-1.5 px-3">
            Upload Another Statement
          </a>
          <a 
            href={`http://localhost:8000/api/reports/${assessment.assessment_id}/download`} 
            target="_blank" 
            rel="noreferrer"
            className="btn-white text-xs py-1.5 px-3 flex items-center gap-1.5"
          >
            <span>↓</span> Download PDF Passport
          </a>
        </div>
      </div>

      {/* Top 5 Key Metric Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {/* Card 1: FHS Score */}
        <div className="card-mono flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-neutral-400 mb-2">
            <span>Health Score</span>
            <span className="cursor-pointer text-neutral-500 hover:text-white" title="Deterministic 5-pillar composite index (0-100)">ⓘ</span>
          </div>
          <div>
            <p className="num-mono text-3xl font-extrabold text-white">
              {financial_health_score.overall_score}
              <span className="text-neutral-500 text-sm font-normal">/100</span>
            </p>
            <p className="text-[11px] text-neutral-300 font-semibold mt-1">
              {financial_health_score.health_band}
            </p>
          </div>
        </div>

        {/* Card 2: Monthly Gross Receipts */}
        <div className="card-mono flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-neutral-400 mb-2">
            <span>Monthly Gross</span>
            <span className="cursor-pointer text-neutral-500 hover:text-white" title="Synthesized customer gross revenue">ⓘ</span>
          </div>
          <div>
            <p className="num-mono text-3xl font-extrabold text-white">
              ₹{Math.round(income_synthesis.average_monthly_gross_receipts).toLocaleString()}
            </p>
            <p className="text-[11px] text-neutral-400 mt-1 font-mono">
              {Math.round(income_synthesis.total_tx_count / Math.max(1, income_synthesis.data_coverage_months))} txns/mo avg
            </p>
          </div>
        </div>

        {/* Card 3: Net Cash Surplus */}
        <div className="card-mono flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-neutral-400 mb-2">
            <span>Net Surplus</span>
            <span className="cursor-pointer text-neutral-500 hover:text-white" title="Gross receipts minus operating outflows">ⓘ</span>
          </div>
          <div>
            <p className="num-mono text-3xl font-extrabold text-white">
              ₹{Math.round(income_synthesis.average_monthly_net_surplus).toLocaleString()}
            </p>
            <p className="text-[11px] text-neutral-400 mt-1 font-mono">
              {operatingMargin}% operating margin
            </p>
          </div>
        </div>

        {/* Card 4: Repayment Confidence */}
        <div className="card-mono flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-neutral-400 mb-2">
            <span>ML Confidence</span>
            <span className="cursor-pointer text-neutral-500 hover:text-white" title="Calibrated XGBoost repayment probability">ⓘ</span>
          </div>
          <div>
            <p className="num-mono text-3xl font-extrabold text-white">
              {credit_risk_ml.repayment_probability_percent}%
            </p>
            <p className="text-[11px] text-neutral-300 font-semibold mt-1">
              {credit_risk_ml.risk_tier}
            </p>
          </div>
        </div>

        {/* Card 5: Volatility CV */}
        <div className="card-mono flex flex-col justify-between col-span-2 sm:col-span-1">
          <div className="flex items-center justify-between text-xs text-neutral-400 mb-2">
            <span>Volatility (CV)</span>
            <span className="cursor-pointer text-neutral-500 hover:text-white" title="Month-to-month coefficient of variation">ⓘ</span>
          </div>
          <div>
            <p className="num-mono text-3xl font-extrabold text-white">
              {income_synthesis.income_volatility_cv.toFixed(3)}
            </p>
            <p className="text-[11px] text-neutral-300 font-semibold mt-1">
              {income_synthesis.income_volatility_cv < 0.20 ? 'High Cashflow Stability' : 'Moderate Volatility'}
            </p>
          </div>
        </div>
      </div>

      {/* Reconstructed Monthly Cashflow Ledger */}
      <div className="bg-[#0E0E0E] border border-[#222222] rounded-2xl overflow-hidden shadow-card-subtle">
        <div className="p-6 border-b border-[#222222] flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              Reconstructed Monthly Cashflow Ledger
              <span className="px-2 py-0.5 rounded-full text-xs bg-black text-neutral-400 font-mono border border-[#262626]">
                {income_synthesis.data_coverage_months} Months Verified
              </span>
            </h3>
            <p className="text-xs text-neutral-400 mt-0.5 font-light">
              Aggregated from verified transactions in {activeFilename}.
            </p>
          </div>
          <a 
            href={`http://localhost:8000/api/reports/${assessment.assessment_id}/download`} 
            target="_blank" 
            rel="noreferrer"
            className="text-xs font-semibold text-white hover:underline flex items-center gap-1.5 font-mono"
          >
            <span>↓</span> Official PDF Dossier
          </a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0A0A0A] text-neutral-400 uppercase tracking-wider text-[11px] border-b border-[#222222]">
              <tr>
                <th className="py-3 px-6 font-semibold">Month Period</th>
                <th className="py-3 px-6 font-semibold">Gross Receipts</th>
                <th className="py-3 px-6 font-semibold">Operating Costs</th>
                <th className="py-3 px-6 font-semibold">Debt EMI</th>
                <th className="py-3 px-6 font-semibold">Net Operating Surplus</th>
                <th className="py-3 px-6 font-semibold">Operating Margin</th>
                <th className="py-3 px-6 font-semibold">Fidelity Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#222222] font-medium font-mono">
              {income_synthesis.monthly_trend && income_synthesis.monthly_trend.length > 0 ? (
                income_synthesis.monthly_trend.map((row) => {
                  const margin = row.gross_receipts > 0 
                    ? ((row.net_operating_surplus / row.gross_receipts) * 100).toFixed(1) 
                    : '0.0';
                  return (
                    <tr key={row.month_period} className="hover:bg-[#141414] transition-colors">
                      <td className="py-4 px-6 text-white">{row.month_period}</td>
                      <td className="py-4 px-6 text-white">₹{Math.round(row.gross_receipts).toLocaleString()}</td>
                      <td className="py-4 px-6 text-neutral-400">₹{Math.round(row.operating_expenses).toLocaleString()}</td>
                      <td className="py-4 px-6 text-neutral-400">₹{Math.round(row.debt_emi_payments || 0).toLocaleString()}</td>
                      <td className="py-4 px-6 text-white font-bold">₹{Math.round(row.net_operating_surplus).toLocaleString()}</td>
                      <td className="py-4 px-6 text-neutral-300">{margin}%</td>
                      <td className="py-4 px-6">
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-white/10 text-white border border-white/20">
                          VERIFIED CSV
                        </span>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={7} className="py-4 px-6 text-center text-neutral-500">
                    No monthly breakdown records available.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Explainable AI Visualizations Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8 mb-8">
        {/* Graph 1: Directional Impact Bar Chart */}
        <div className="bg-[#0E0E0E] border border-[#222222] rounded-2xl p-6 shadow-card-subtle">
          <div className="mb-6">
            <span className="text-xs font-mono uppercase text-neutral-400">SHAP Attributions</span>
            <h3 className="text-base font-bold text-white mt-0.5">Impact Direction & Magnitude</h3>
          </div>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart 
                data={credit_risk_ml.attributions.map(a => ({
                  name: a.feature_label.replace(' Consistency', '').replace(' Velocity', '').replace(' Turnover', ''),
                  impact: parseFloat(a.shap_value.toFixed(2))
                }))} 
                layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
              >
                <XAxis type="number" stroke="#666" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis dataKey="name" type="category" stroke="#999" fontSize={10} tickLine={false} axisLine={false} />
                <Tooltip cursor={{fill: '#222'}} contentStyle={{ backgroundColor: '#000', borderColor: '#333', color: '#fff', fontSize: '11px' }} />
                <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
                  {credit_risk_ml.attributions.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.shap_value >= 0 ? '#ffffff' : '#666666'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Graph 2: Absolute Feature Importance Pie Chart */}
        <div className="bg-[#0E0E0E] border border-[#222222] rounded-2xl p-6 shadow-card-subtle">
          <div className="mb-6">
            <span className="text-xs font-mono uppercase text-neutral-400">SHAP Attributions</span>
            <h3 className="text-base font-bold text-white mt-0.5">Absolute Feature Importance</h3>
          </div>
          <div className="w-full h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie 
                  data={credit_risk_ml.attributions.map(a => ({
                    name: a.feature_label,
                    importance: parseFloat(Math.abs(a.shap_value).toFixed(2))
                  }))}
                  dataKey="importance" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={2}
                >
                  {credit_risk_ml.attributions.map((entry, index) => (
                    <Cell key={`pie-cell-${index}`} fill={['#ffffff', '#cccccc', '#999999', '#666666', '#333333'][index % 5]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#000', borderColor: '#333', color: '#fff', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Dual Bottom Section: SHAP Waterfall forces + Underwriting Checklist */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: SHAP Feature Attributions */}
        <div className="lg:col-span-7 bg-[#0E0E0E] border border-[#222222] rounded-2xl p-6 shadow-card-subtle flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-[#222222]">
              <div>
                <span className="text-xs font-mono uppercase text-neutral-400">Explainable AI (XAI)</span>
                <h3 className="text-base font-bold text-white mt-0.5">SHAP Feature Attribution Forces</h3>
              </div>
              <span className="text-xs text-neutral-500 font-mono">TreeExplainer Margin</span>
            </div>

            <p className="text-xs text-neutral-400 my-4 font-light">
              Directional impact of {assessment.applicant_name}'s alternative cashflow features against the baseline model expectation.
            </p>

            {/* Highlighted Wording Format */}
            <div className="space-y-4 pt-2">
              {credit_risk_ml.plain_language_narrative && (
                <div className="p-4 rounded-xl bg-gradient-to-br from-[#1A1A1A] to-black border border-white/20 shadow-white-glow relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-1 h-full bg-white"></div>
                  <p className="text-sm text-white leading-relaxed font-serif tracking-wide italic">"{credit_risk_ml.plain_language_narrative}"</p>
                </div>
              )}
              
              <div className="space-y-3 mt-4">
              {credit_risk_ml.attributions && credit_risk_ml.attributions.length > 0 ? (
                credit_risk_ml.attributions.map((a) => {
                  const isPos = a.shap_value >= 0;
                  const displayVal = (a as any).feature_value_formatted || a.value_formatted || a.feature_value;
                  return (
                    <div key={a.feature_name || a.feature_label} className={`p-3.5 rounded-lg border ${isPos ? 'bg-white/5 border-white/10' : 'bg-black border-[#222222]'}`}>
                      <p className="text-sm text-neutral-300 leading-relaxed font-mono">
                        • The <strong className="text-white font-sans tracking-wide">{a.feature_label}</strong> factor (valued at <span className="text-white">{displayVal}</span>) 
                        <span className={isPos ? "text-white font-bold" : "text-neutral-400 font-bold"}>{isPos ? ' increases' : ' decreases'}</span> the baseline repayment probability expectation by 
                        <strong className={isPos ? "text-white" : "text-neutral-500"}> {Math.abs(a.shap_value).toFixed(2)}%</strong>.
                      </p>
                    </div>
                  );
                })
              ) : (
                <p className="text-xs text-neutral-500">Explanation pending feature extraction.</p>
              )}
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[#222222] text-xs text-neutral-500 font-mono">
            Baseline Expectation: <strong className="text-white">{credit_risk_ml.baseline_expected_probability || 61.5}%</strong> • Calibrated Prediction: <strong className="text-white">{credit_risk_ml.repayment_probability_percent}%</strong>
          </div>
        </div>

        {/* Right Column: Policy Underwriting Checklist */}
        <div className="lg:col-span-5 bg-[#0E0E0E] border border-[#222222] rounded-2xl p-6 shadow-card-subtle flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-[#222222]">
              <div>
                <span className="text-xs font-mono uppercase text-neutral-400">Underwriting Rules</span>
                <h3 className="text-base font-bold text-white mt-0.5">Policy Criteria Checklist</h3>
              </div>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-white/10 text-white border border-white/20 font-mono">
                {underwriting_decision.passed_count ?? underwriting_decision.rules_passed_count ?? 5} / {underwriting_decision.total_rules_count ?? 5} PASSED
              </span>
            </div>

            <div className="divide-y divide-[#222222] text-xs py-2">
              {((underwriting_decision.criteria_evaluated || underwriting_decision.rule_results || []) as any[]).map((r: any) => {
                const isPassed = r.is_passed !== undefined ? r.is_passed : r.passed;
                const thresh = r.target_threshold || r.threshold_condition;
                const actVal = r.actual_value_formatted || r.actual_value;
                return (
                  <div key={r.rule_id} className="py-3 flex items-start justify-between">
                    <div>
                      <p className="font-semibold text-white">{r.rule_name}</p>
                      <p className="text-neutral-500 text-[11px] font-mono">Threshold: {thresh}</p>
                    </div>
                    <span className={`font-bold text-xs font-mono ${isPassed ? 'text-white' : 'text-neutral-500'}`}>
                      {isPassed ? '✓ PASSED' : '✗ FAILED'} ({actVal})
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-[#222222] space-y-2">
            <a 
              href={`/simulator?id=${assessment.assessment_id}`} 
              className="w-full btn-white text-xs py-2.5 flex items-center justify-center"
            >
              Open What-If Simulator for {assessment.applicant_name.split(' ')[0]} ➔
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
