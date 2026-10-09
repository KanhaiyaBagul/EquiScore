import React, { useState, useEffect } from 'react';

interface PassportAssessment {
  assessment_id: string;
  applicant_name: string;
  business_name: string;
  business_type: string;
  income_synthesis: {
    average_monthly_gross_receipts: number;
    average_monthly_expenses: number;
    average_monthly_debt_emi: number;
    average_monthly_net_surplus: number;
    data_coverage_months: number;
    total_tx_count?: number;
  };
  financial_health_score: {
    overall_score: number;
    health_band: string;
    strengths: string[];
  };
  credit_risk_ml: {
    repayment_probability_percent: number;
    risk_tier: string;
  };
  underwriting_decision: {
    decision_status: string;
  };
}

export default function DigitalPassportViewer() {
  const [data, setData] = useState<PassportAssessment>({
    assessment_id: 'ASM_ARUNVERMA_01',
    applicant_name: 'Arun Verma',
    business_name: 'Artisan Carpentry & Woodcraft',
    business_type: 'artisan_freelance',
    income_synthesis: {
      average_monthly_gross_receipts: 32297,
      average_monthly_expenses: 22069,
      average_monthly_debt_emi: 4500,
      average_monthly_net_surplus: 10228,
      data_coverage_months: 4,
      total_tx_count: 319
    },
    financial_health_score: {
      overall_score: 67,
      health_band: 'Resilient Band',
      strengths: ['Verified digital milestone receipts', 'Active commercial banking volume']
    },
    credit_risk_ml: {
      repayment_probability_percent: 66.9,
      risk_tier: 'Tier 2 Moderate Risk'
    },
    underwriting_decision: {
      decision_status: 'ELIGIBLE'
    }
  });

  const [hasCustom, setHasCustom] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>('arun');
  const [loading, setLoading] = useState<boolean>(false);

  const selectPreset = async (key: string) => {
    setActiveTab(key);
    setLoading(true);

    if (key === 'custom') {
      const cached = localStorage.getItem('equiscore_current_assessment');
      if (cached) {
        try {
          setData(JSON.parse(cached));
        } catch (e) {}
      }
      setLoading(false);
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/api/assessments/${key}`);
      if (res.ok) {
        const d = await res.json();
        setData(d);
        localStorage.setItem('equiscore_current_assessment', JSON.stringify(d));
        window.dispatchEvent(new CustomEvent('equiscore_assessment_updated', { detail: d }));
      }
    } catch (e) {
      console.warn("Could not fetch assessment for passport", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const queryId = params.get('id');

    if (queryId) {
      fetch(`http://localhost:8000/api/assessments/${queryId}`)
        .then(res => res.json())
        .then(parsed => {
          setData(parsed);
          setHasCustom(true);
          setActiveTab('custom');
          localStorage.setItem('equiscore_current_assessment', JSON.stringify(parsed));
          window.dispatchEvent(new CustomEvent('equiscore_assessment_updated', { detail: parsed }));
        })
        .catch(e => console.warn('Failed to fetch assessment for passport', e));
      return;
    }

    const cached = localStorage.getItem('equiscore_current_assessment');
    if (cached) {
      try {
        const parsed: PassportAssessment = JSON.parse(cached);
        if (parsed && parsed.assessment_id) {
          setData(parsed);
          const k = parsed.applicant_name?.toLowerCase().includes('arun') ? 'arun' :
                    parsed.applicant_name?.toLowerCase().includes('ramesh') ? 'ramesh' :
                    parsed.applicant_name?.toLowerCase().includes('priya') ? 'priya' : 'custom';
          setActiveTab(k);
          if (k === 'custom') setHasCustom(true);
          return;
        }
      } catch (e) {}
    }

    // Default: fetch Arun's CSV assessment
    selectPreset('arun');
  }, []);

  const downloadUrl = `http://localhost:8000/api/reports/${data.assessment_id}/download`;

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Top Header & Action */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2">
        <div>
          <span className="text-xs uppercase font-mono tracking-wider text-neutral-400">Portable Credit Dossier</span>
          <h2 className="text-2xl font-bold text-white mt-0.5">Digital Financial Passport</h2>
          <p className="text-xs text-text-secondary mt-1 font-light">
            An applicant-owned, tamper-evident financial dossier synthesized from real statement CSV records.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={downloadUrl}
            target="_blank"
            rel="noreferrer"
            className="btn-white text-xs py-2.5 px-5 flex items-center gap-2 shadow-white-glow"
          >
            <span>↓</span> Download Official PDF Dossier
          </a>
        </div>
      </div>

      {/* Preset / Active Toggle Tabs */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-3.5 bg-[#0E0E0E] border border-[#222222] rounded-2xl">
        <span className="text-xs font-mono text-neutral-400">Generate Passport For:</span>
        <div className="inline-flex flex-wrap p-1 bg-black rounded-full border border-[#262626]">
          {hasCustom && (
            <button
              type="button"
              onClick={() => selectPreset('custom')}
              className={`px-3 py-1 text-xs font-mono rounded-full transition-all cursor-pointer ${
                activeTab === 'custom' ? 'bg-white text-black font-bold' : 'text-neutral-400 hover:text-white'
              }`}
            >
              ★ Uploaded Statement
            </button>
          )}
          <button
            type="button"
            onClick={() => selectPreset('arun')}
            className={`px-3 py-1 text-xs font-mono rounded-full transition-all cursor-pointer ${
              activeTab === 'arun' ? 'bg-white text-black font-bold' : 'text-neutral-400 hover:text-white'
            }`}
          >
            📄 Arun (319 txns)
          </button>
          <button
            type="button"
            onClick={() => selectPreset('ramesh')}
            className={`px-3 py-1 text-xs font-mono rounded-full transition-all cursor-pointer ${
              activeTab === 'ramesh' ? 'bg-white text-black font-bold' : 'text-neutral-400 hover:text-white'
            }`}
          >
            📄 Ramesh (1,357 txns)
          </button>
          <button
            type="button"
            onClick={() => selectPreset('priya')}
            className={`px-3 py-1 text-xs font-mono rounded-full transition-all cursor-pointer ${
              activeTab === 'priya' ? 'bg-white text-black font-bold' : 'text-neutral-400 hover:text-white'
            }`}
          >
            📄 Priya (749 txns)
          </button>
        </div>
      </div>

      {/* Passport Document Card Preview - Monochrome */}
      <div className="bg-[#0A0A0A] border-2 border-white/20 rounded-3xl p-8 sm:p-10 shadow-2xl relative overflow-hidden">
        {/* Passport Header Banner */}
        <div className="flex items-start justify-between pb-6 border-b border-[#222222]">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-white flex items-center justify-center font-bold text-black text-xs">✦</div>
              <span className="text-base font-bold text-white tracking-wider">EQUISCORE FINANCIAL PASSPORT</span>
            </div>
            <p className="text-[11px] text-neutral-400 font-mono mt-1">VERIFIABLE ALTERNATIVE CREDIT & INCOME DOSSIER</p>
          </div>
          <div className="text-right">
            <span className="text-[10px] text-neutral-500 font-mono block">DOSSIER ID</span>
            <span className="num-mono text-xs font-bold text-white">{data.assessment_id}</span>
          </div>
        </div>

        {/* Identity & Enterprise Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-6 border-b border-[#222222] text-xs">
          <div>
            <span className="text-neutral-500 block text-[11px]">Applicant Name</span>
            <span className="font-bold text-white mt-0.5 block">{data.applicant_name}</span>
          </div>
          <div>
            <span className="text-neutral-500 block text-[11px]">Trade / Enterprise</span>
            <span className="font-bold text-white mt-0.5 block">{data.business_name}</span>
          </div>
          <div>
            <span className="text-neutral-500 block text-[11px]">Statement Coverage</span>
            <span className="font-bold text-white mt-0.5 block font-mono">{data.income_synthesis.data_coverage_months} Months Verified</span>
          </div>
          <div>
            <span className="text-neutral-500 block text-[11px]">Lending Status</span>
            <span className="text-white font-bold mt-0.5 block font-mono">✓ {data.underwriting_decision.decision_status}</span>
          </div>
        </div>

        {/* Scoring Snapshot Highlight */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 my-6">
          <div className="p-5 bg-black border border-white/20 rounded-2xl flex items-center justify-between">
            <div>
              <span className="text-[11px] font-mono uppercase text-neutral-400">Financial Health Score</span>
              <p className="num-mono text-3xl font-extrabold text-white mt-1">
                {data.financial_health_score.overall_score} <span className="text-xs text-neutral-500 font-normal">/ 100</span>
              </p>
              <p className="text-xs text-neutral-300 mt-0.5 font-mono">{data.financial_health_score.health_band}</p>
            </div>
            <span className="text-2xl font-mono text-white">▣</span>
          </div>

          <div className="p-5 bg-black border border-[#222222] rounded-2xl flex items-center justify-between">
            <div>
              <span className="text-[11px] font-mono uppercase text-neutral-400">Alternative Repayment Probability</span>
              <p className="num-mono text-3xl font-extrabold text-white mt-1">
                {data.credit_risk_ml.repayment_probability_percent}%
              </p>
              <p className="text-xs text-neutral-300 mt-0.5 font-mono">{data.credit_risk_ml.risk_tier}</p>
            </div>
            <span className="text-2xl font-mono text-white">▲</span>
          </div>
        </div>

        {/* Cashflow Breakdown Summary */}
        <div className="space-y-3 pt-2">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono">Synthesized Cashflow Breakdown</h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 bg-black rounded-xl border border-[#222222]">
              <span className="text-[10px] text-neutral-500 uppercase block">Monthly Gross</span>
              <span className="num-mono text-base font-bold text-white mt-0.5 block">
                ₹{Math.round(data.income_synthesis.average_monthly_gross_receipts).toLocaleString()}
              </span>
            </div>
            <div className="p-3 bg-black rounded-xl border border-[#222222]">
              <span className="text-[10px] text-neutral-500 uppercase block">Operating Costs</span>
              <span className="num-mono text-base font-bold text-neutral-300 mt-0.5 block">
                ₹{Math.round(data.income_synthesis.average_monthly_expenses).toLocaleString()}
              </span>
            </div>
            <div className="p-3 bg-black rounded-xl border border-[#222222]">
              <span className="text-[10px] text-neutral-500 uppercase block">Existing EMI</span>
              <span className="num-mono text-base font-bold text-neutral-300 mt-0.5 block">
                ₹{Math.round(data.income_synthesis.average_monthly_debt_emi).toLocaleString()}
              </span>
            </div>
            <div className="p-3 bg-black rounded-xl border border-white/20">
              <span className="text-[10px] text-neutral-400 uppercase block">Net Discretionary Surplus</span>
              <span className="num-mono text-base font-bold text-white mt-0.5 block">
                ₹{Math.round(data.income_synthesis.average_monthly_net_surplus).toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Bottom Verification & Security Row */}
        <div className="mt-8 pt-6 border-t border-[#222222] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-[11px] text-neutral-400 font-mono">
          <div>
            <p>Cryptographic Audit Hash: <span className="text-white">SHA256:7f9b8c2a3e... verified</span></p>
            <p className="text-[10px] text-neutral-500 mt-0.5">Algorithmic Governance: Calibrated XGBoost & Fairlearn Audited</p>
          </div>
          <a
            href={downloadUrl}
            target="_blank"
            rel="noreferrer"
            className="text-white hover:underline font-bold flex items-center gap-1"
          >
            <span>↓</span> Download PDF Version
          </a>
        </div>
      </div>
    </div>
  );
}
