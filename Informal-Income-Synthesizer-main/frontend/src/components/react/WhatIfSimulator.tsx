import React, { useState, useEffect } from 'react';

interface ActiveProfile {
  key: string;
  name: string;
  business: string;
  type: string;
  gross: number;
  expenses: number;
  surplus: number;
  emi: number;
  fhs: number;
  prob: number;
  cv: number;
  filename: string;
}

export default function WhatIfSimulator() {
  const [profile, setProfile] = useState<ActiveProfile>({
    key: 'arun',
    name: 'Arun Verma',
    business: 'Artisan Carpentry & Woodcraft',
    type: 'Artisan Freelance',
    gross: 32297,
    expenses: 22069,
    surplus: 10228,
    emi: 4500,
    fhs: 67,
    prob: 66.9,
    cv: 0.075,
    filename: 'sample_volatile_freelancer_arun.csv'
  });

  const [activeKey, setActiveKey] = useState<string>('arun');
  const [hasCustomUploaded, setHasCustomUploaded] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  // Sliders for hypothetical deltas
  const [deltaExpense, setDeltaExpense] = useState<number>(-3000);
  const [deltaGross, setDeltaGross] = useState<number>(2500);
  const [deltaEmi, setDeltaEmi] = useState<number>(-1000);
  const [deltaReserve, setDeltaReserve] = useState<number>(5000);

  const loadProfileFromData = (d: any, key: string) => {
    const fn = key === 'arun' ? 'sample_volatile_freelancer_arun.csv' :
               key === 'ramesh' ? 'sample_street_vendor_ramesh.csv' :
               key === 'priya' ? 'sample_gig_delivery_priya.csv' : 'custom_uploaded_statement.csv';

    setProfile({
      key,
      name: d.applicant_name,
      business: d.business_name,
      type: d.business_type.replace('_', ' '),
      gross: Math.round(d.income_synthesis.average_monthly_gross_receipts),
      expenses: Math.round(d.income_synthesis.average_monthly_expenses),
      surplus: Math.round(d.income_synthesis.average_monthly_net_surplus),
      emi: Math.round(d.income_synthesis.average_monthly_debt_emi || 0),
      fhs: d.financial_health_score.overall_score,
      prob: d.credit_risk_ml.repayment_probability_percent,
      cv: Number(d.income_synthesis.income_volatility_cv.toFixed(3)),
      filename: fn
    });
    setActiveKey(key);
  };

  const selectDataset = async (key: string) => {
    setLoading(true);
    if (key === 'uploaded') {
      const cached = localStorage.getItem('equiscore_current_assessment');
      if (cached) {
        try {
          loadProfileFromData(JSON.parse(cached), 'uploaded');
        } catch (e) {}
      }
      setLoading(false);
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/api/assessments/${key}`);
      if (res.ok) {
        const d = await res.json();
        loadProfileFromData(d, key);
        localStorage.setItem('equiscore_current_assessment', JSON.stringify(d));
        window.dispatchEvent(new CustomEvent('equiscore_assessment_updated', { detail: d }));
      }
    } catch (e) {
      console.warn("Could not fetch dataset for simulator", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const queryId = params.get('id');

    if (queryId) {
      fetch(`http://localhost:8000/api/assessments/${queryId}`)
        .then(res => {
          if (!res.ok) throw new Error("Assessment not found");
          return res.json();
        })
        .then(d => {
          loadProfileFromData(d, 'uploaded');
          setHasCustomUploaded(true);
          localStorage.setItem('equiscore_current_assessment', JSON.stringify(d));
          window.dispatchEvent(new CustomEvent('equiscore_assessment_updated', { detail: d }));
        })
        .catch(err => {
          console.warn('Could not fetch assessment for simulator', err);
          // Fall back to localStorage if fetch fails
          const cached = localStorage.getItem('equiscore_current_assessment');
          if (cached) {
            try {
              const d = JSON.parse(cached);
              if (d && d.applicant_name) {
                loadProfileFromData(d, 'uploaded');
                setHasCustomUploaded(true);
                return;
              }
            } catch(e) {}
          }
          selectDataset('arun');
        });
      return;
    }

    const cached = localStorage.getItem('equiscore_current_assessment');
    if (cached) {
      try {
        const d = JSON.parse(cached);
        if (d && d.applicant_name) {
          const k = d.applicant_name.toLowerCase().includes('arun') ? 'arun' :
                    d.applicant_name.toLowerCase().includes('ramesh') ? 'ramesh' :
                    d.applicant_name.toLowerCase().includes('priya') ? 'priya' : 'uploaded';
          loadProfileFromData(d, k);
          if (k === 'uploaded') setHasCustomUploaded(true);
          return;
        }
      } catch (err) {}
    }

    // Default to Arun's CSV dataset
    selectDataset('arun');
  }, []);

  // Base metrics derived directly from the CSV
  const baseGross = profile.gross;
  const baseExpenses = profile.expenses;
  const baseSurplus = profile.surplus;
  const baseEmi = profile.emi;
  const baseFhs = profile.fhs;
  const baseProb = profile.prob;

  // Simulated state
  const simGross = Math.max(0, baseGross + deltaGross);
  const simExpenses = Math.max(0, baseExpenses + deltaExpense);
  const simSurplus = Math.max(0, simGross - simExpenses);
  const simEmi = Math.max(0, baseEmi + deltaEmi);

  // Deterministic 5-pillar recalculation
  const surplusRatio = simGross > 0 ? (simSurplus / simGross) : 0;
  const debtRatio = simSurplus > 0 ? (simEmi / simSurplus) : 1.0;
  const p1 = Math.min(100, Math.max(0, (surplusRatio / 0.35) * 100)) * 0.30;
  const p2 = (1.0 - Math.min(1.0, profile.cv / 0.50)) * 100 * 0.25;
  const p3 = Math.max(0, 100 - (debtRatio * 100)) * 0.20;
  const p4 = Math.min(100, Math.max(0, ((8000 + deltaReserve) / 10000) * 80)) * 0.15;
  const p5 = 85 * 0.10;

  const simFhs = Math.min(100, Math.max(0, Math.round(p1 + p2 + p3 + p4 + p5)));
  const fhsDelta = simFhs - baseFhs;
  const probDelta = Number(((simFhs - baseFhs) * 0.70).toFixed(1));
  const simProb = Math.min(99.0, Math.max(30.0, Number((baseProb + probDelta).toFixed(1))));

  return (
    <div className="space-y-6">


      {/* Main Grid: Controls on left, Side-by-Side Comparison on right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Interactive Delta Sliders */}
        <div className="lg:col-span-6 bg-[#0E0E0E] border border-[#222222] rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-[#222222]">
            <div>
              <h3 className="text-sm font-bold text-white">Hypothetical Financial Levers</h3>
              <p className="text-[11px] text-neutral-400 mt-0.5">Explore score growth pathways without affecting your official records.</p>
            </div>
            <span className="text-xs text-neutral-400 font-mono">Isolated Sandbox</span>
          </div>

          {/* Slider 1: Expenses */}
          <div>
            <div className="flex justify-between text-xs mb-2">
              <span className="text-neutral-400">Trim / Increase Monthly Operating Costs</span>
              <div className="flex items-center gap-1">
                <span className="text-white font-mono font-bold">₹</span>
                <input 
                  type="number" 
                  value={deltaExpense} 
                  onChange={(e) => setDeltaExpense(Number(e.target.value) || 0)}
                  className="bg-[#1A1A1A] text-white font-bold font-mono text-right w-24 outline-none border border-[#333333] focus:border-white rounded-md px-2 py-1 transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none shadow-inner"
                />
              </div>
            </div>
            <input
              type="range"
              min="-10000"
              max="10000"
              step="500"
              value={deltaExpense}
              onChange={(e) => setDeltaExpense(Number(e.target.value))}
              className="w-full h-1 bg-[#262626] rounded-lg appearance-none cursor-pointer accent-white"
            />
            <div className="flex justify-between text-[11px] text-neutral-500 mt-1 font-mono">
              <span>-₹10,000 (Cost Reduction)</span>
              <span>+₹10,000 (Cost Inflation)</span>
            </div>
          </div>

          {/* Slider 2: Gross Receipts */}
          <div>
            <div className="flex justify-between text-xs mb-2">
              <span className="text-neutral-400">Expand Monthly Digital UPI / Customer Receipts</span>
              <div className="flex items-center gap-1">
                <span className="text-white font-mono font-bold">₹</span>
                <input 
                  type="number" 
                  value={deltaGross} 
                  onChange={(e) => setDeltaGross(Number(e.target.value) || 0)}
                  className="bg-[#1A1A1A] text-white font-bold font-mono text-right w-24 outline-none border border-[#333333] focus:border-white rounded-md px-2 py-1 transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none shadow-inner"
                />
              </div>
            </div>
            <input
              type="range"
              min="-10000"
              max="20000"
              step="1000"
              value={deltaGross}
              onChange={(e) => setDeltaGross(Number(e.target.value))}
              className="w-full h-1 bg-[#262626] rounded-lg appearance-none cursor-pointer accent-white"
            />
            <div className="flex justify-between text-[11px] text-neutral-500 mt-1 font-mono">
              <span>-₹10,000 (Seasonal Dip)</span>
              <span>+₹20,000 (Revenue Growth)</span>
            </div>
          </div>

          {/* Slider 3: EMI Paydown */}
          <div>
            <div className="flex justify-between text-xs mb-2">
              <span className="text-neutral-400">Pre-Pay Existing Loan EMI / Commit New EMI</span>
              <div className="flex items-center gap-1">
                <span className="text-white font-mono font-bold">₹</span>
                <input 
                  type="number" 
                  value={deltaEmi} 
                  onChange={(e) => setDeltaEmi(Number(e.target.value) || 0)}
                  className="bg-[#1A1A1A] text-white font-bold font-mono text-right w-24 outline-none border border-[#333333] focus:border-white rounded-md px-2 py-1 transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none shadow-inner"
                />
              </div>
            </div>
            <input
              type="range"
              min={-baseEmi}
              max="5000"
              step="500"
              value={deltaEmi}
              onChange={(e) => setDeltaEmi(Number(e.target.value))}
              className="w-full h-1 bg-[#262626] rounded-lg appearance-none cursor-pointer accent-white"
            />
            <div className="flex justify-between text-[11px] text-neutral-500 mt-1 font-mono">
              <span>-₹{baseEmi.toLocaleString()} (Full Payoff)</span>
              <span>+₹5,000 (New Loan)</span>
            </div>
          </div>

          {/* Slider 4: Emergency Reserve */}
          <div>
            <div className="flex justify-between text-xs mb-2">
              <span className="text-neutral-400">Add to Emergency Liquidity Buffer</span>
              <div className="flex items-center gap-1">
                <span className="text-white font-mono font-bold">₹</span>
                <input 
                  type="number" 
                  value={deltaReserve} 
                  onChange={(e) => setDeltaReserve(Number(e.target.value) || 0)}
                  className="bg-[#1A1A1A] text-white font-bold font-mono text-right w-24 outline-none border border-[#333333] focus:border-white rounded-md px-2 py-1 transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none shadow-inner"
                />
              </div>
            </div>
            <input
              type="range"
              min="0"
              max="25000"
              step="1000"
              value={deltaReserve}
              onChange={(e) => setDeltaReserve(Number(e.target.value))}
              className="w-full h-1 bg-[#262626] rounded-lg appearance-none cursor-pointer accent-white"
            />
            <div className="flex justify-between text-[11px] text-neutral-500 mt-1 font-mono">
              <span>₹0</span>
              <span>+₹25,000 Reserve</span>
            </div>
          </div>

          {/* Reset Button */}
          <button
            type="button"
            onClick={() => {
              setDeltaExpense(0);
              setDeltaGross(0);
              setDeltaEmi(0);
              setDeltaReserve(0);
            }}
            className="w-full btn-dark text-xs py-2.5 cursor-pointer"
          >
            Reset All Sliders to Baseline
          </button>
        </div>

        {/* Right Column: Side-by-Side Comparison */}
        <div className="lg:col-span-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            {/* Baseline Card */}
            <div className="bg-[#0A0A0A] border border-[#222222] rounded-2xl p-6">
              <span className="text-[11px] font-mono text-neutral-500 uppercase">Verified CSV Baseline</span>
              <p className="num-mono text-4xl font-extrabold text-white mt-2">
                {baseFhs}<span className="text-xs text-neutral-500 font-normal">/100</span>
              </p>
              <p className="text-xs text-neutral-400 mt-1 font-mono">Surplus: ₹{baseSurplus.toLocaleString()}</p>
              <div className="mt-4 pt-4 border-t border-[#222222] text-xs">
                <span className="text-neutral-500">Repayment Prob:</span>
                <p className="num-mono font-bold text-white mt-0.5">{baseProb}%</p>
              </div>
            </div>

            {/* Simulated Card */}
            <div className="bg-[#121212] border border-white/30 rounded-2xl p-6 relative overflow-hidden shadow-card-subtle">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono text-white uppercase font-semibold">Simulated State</span>
                <span className="px-2 py-0.5 rounded-full text-xs font-bold font-mono bg-white text-black">
                  {fhsDelta >= 0 ? '+' : ''}{fhsDelta} PTS
                </span>
              </div>
              <p className="num-mono text-4xl font-extrabold text-white mt-2">
                {simFhs}<span className="text-xs text-neutral-500 font-normal">/100</span>
              </p>
              <p className="text-xs text-neutral-300 mt-1 font-mono">New Surplus: ₹{simSurplus.toLocaleString()}</p>
              <div className="mt-4 pt-4 border-t border-[#222222] text-xs">
                <span className="text-neutral-500">Simulated Prob:</span>
                <p className="num-mono font-bold text-white mt-0.5">
                  {simProb}% ({probDelta >= 0 ? '+' : ''}{probDelta}%)
                </p>
              </div>
            </div>
          </div>


        </div>
      </div>
    </div>
  );
}
