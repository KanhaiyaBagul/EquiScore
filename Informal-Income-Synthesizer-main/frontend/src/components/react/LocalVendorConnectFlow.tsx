import React, { useState } from 'react';
import { ShieldCheck, Link, UploadCloud, Camera, CheckCircle, ArrowRight, FileText, Banknote } from 'lucide-react';

interface CashTransaction {
  id: string;
  date: string;
  amount: string;
  description: string;
  evidenceAttached: boolean;
}

export const LocalVendorConnectFlow: React.FC = () => {
  const [step, setStep] = useState(1);
  const [cashTransactions, setCashTransactions] = useState<CashTransaction[]>([]);
  const [cashInput, setCashInput] = useState({ date: '', amount: '', description: '', evidence: null as File | null });
  const [error, setError] = useState('');

  const nextStep = () => setStep(prev => prev + 1);

  const handleGeneratePassport = () => {
    if (cashTransactions.length === 0) {
      setError('Please log at least one cash transaction before generating the passport.');
      return;
    }
    setError('');
    nextStep();
  };

  const addCashTransaction = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!cashInput.date || !cashInput.amount) {
      setError('Date and Amount are required fields.');
      return;
    }
    
    setCashTransactions(prev => [...prev, {
      id: Math.random().toString(36).substring(7),
      date: cashInput.date,
      amount: cashInput.amount,
      description: cashInput.description,
      evidenceAttached: cashInput.evidence !== null
    }]);
    setCashInput({ date: '', amount: '', description: '', evidence: null });
  };

  const handleEvidenceUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCashInput({ ...cashInput, evidence: e.target.files[0] });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Progress Header */}
      <div className="bg-[#121212] border border-[#222222] rounded-2xl p-6">
        <h2 className="text-xl font-bold text-white mb-6">Local Vendor Connect Onboarding</h2>
        <div className="flex items-center justify-between">
          {[
            { num: 1, label: "Account Setup" },
            { num: 2, label: "Consent" },
            { num: 3, label: "Digital Bank / AA" },
            { num: 4, label: "Offline Cash Ledger" },
            { num: 5, label: "Financial Passport" }
          ].map((s, idx) => (
            <div key={s.num} className="flex flex-col items-center flex-1 relative">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm mb-2 z-10 transition-colors ${
                step >= s.num ? 'bg-blue-600 text-white shadow-[0_0_15px_rgba(37,99,235,0.5)]' : 'bg-[#222] text-neutral-500'
              }`}>
                {s.num}
              </div>
              <span className={`text-[10px] sm:text-xs font-mono text-center ${step >= s.num ? 'text-blue-400' : 'text-neutral-500'}`}>
                {s.label}
              </span>
              {idx < 4 && (
                <div className={`absolute top-4 left-1/2 w-full h-[2px] -z-0 ${
                  step > s.num ? 'bg-blue-600' : 'bg-[#222]'
                }`}></div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-[#121212] border border-[#222222] rounded-2xl p-8 min-h-[400px] flex flex-col justify-center">
        
        {/* Step 1: Scan & Setup */}
        {step === 1 && (
          <div className="text-center space-y-6 max-w-lg mx-auto">
            <div className="w-20 h-20 bg-blue-900/30 text-blue-400 rounded-full flex items-center justify-center mx-auto">
              <ShieldCheck size={40} />
            </div>
            <h3 className="text-2xl font-bold text-white">Create Vendor Profile</h3>
            <p className="text-neutral-400">You've successfully scanned the onboarding QR code. Let's create your unified profile to build your alternative credit score without needing a traditional credit history.</p>
            <div className="space-y-4 text-left pt-4">
              <input type="text" placeholder="Vendor / Business Name" className="w-full bg-black border border-[#333] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500" defaultValue="Shree Balaji Chai Stall" />
              <input type="text" placeholder="Phone Number" className="w-full bg-black border border-[#333] rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500" defaultValue="+91 98765 43210" />
            </div>
            <button onClick={nextStep} className="w-full bg-white text-black font-bold py-3 px-6 rounded-xl hover:bg-neutral-200 transition-colors flex justify-center items-center gap-2">
              Continue to Consent <ArrowRight size={18} />
            </button>
          </div>
        )}

        {/* Step 2: Informed Consent */}
        {step === 2 && (
          <div className="space-y-6 max-w-xl mx-auto">
            <h3 className="text-2xl font-bold text-white text-center">Informed Data Consent</h3>
            <div className="bg-black border border-[#333] p-5 rounded-xl space-y-4 text-sm text-neutral-300">
              <p>To accurately assess your income stability and provide a Financial Evidence Passport, we require access to your financial data streams.</p>
              <ul className="list-disc pl-5 space-y-2">
                <li><strong className="text-white">What we access:</strong> UPI transaction histories, bank statements, and manually uploaded cash ledgers.</li>
                <li><strong className="text-white">Why we need it:</strong> To categorize sales vs. expenses and generate your explainable underwriting score.</li>
                <li><strong className="text-white">Duration:</strong> One-time read access for the last 6 months. Data is not stored permanently beyond generating the passport.</li>
              </ul>
            </div>
            <label className="flex items-start gap-3 cursor-pointer mt-6">
              <input type="checkbox" className="mt-1 w-4 h-4 rounded text-blue-600 focus:ring-blue-500 bg-black border-gray-700" />
              <span className="text-sm text-neutral-400">I explicitly consent to fetching my financial data from registered Account Aggregators and Banks for credit assessment purposes.</span>
            </label>
            <button onClick={nextStep} className="w-full bg-blue-600 text-white font-bold py-3 px-6 rounded-xl hover:bg-blue-700 transition-colors flex justify-center items-center gap-2 mt-4">
              I Agree & Continue <ArrowRight size={18} />
            </button>
          </div>
        )}

        {/* Step 3: Connect Bank / AA */}
        {step === 3 && (
          <div className="text-center space-y-6 max-w-lg mx-auto">
            <div className="w-20 h-20 bg-green-900/30 text-green-400 rounded-full flex items-center justify-center mx-auto">
              <Link size={40} />
            </div>
            <h3 className="text-2xl font-bold text-white">Connect Digital Data Source</h3>
            <p className="text-neutral-400">Securely link your primary bank account or Account Aggregator (AA) to automatically sync your UPI and digital transfer history.</p>
            
            <div className="grid grid-cols-2 gap-4 pt-4">
              <button onClick={nextStep} className="bg-black border border-[#333] p-4 rounded-xl hover:border-blue-500 transition-colors text-white font-medium">
                Connect via Sahamati AA
              </button>
              <button onClick={nextStep} className="bg-black border border-[#333] p-4 rounded-xl hover:border-blue-500 transition-colors text-white font-medium flex flex-col items-center justify-center gap-2">
                <UploadCloud size={20} />
                Upload CSV Statement
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Cash Transaction Capture System */}
        {step === 4 && (
          <div className="space-y-6 max-w-2xl mx-auto w-full">
            <div className="text-center space-y-2 mb-8">
              <div className="w-16 h-16 bg-yellow-900/30 text-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Banknote size={32} />
              </div>
              <h3 className="text-2xl font-bold text-white">Cash Transaction Capture & Verification</h3>
              <p className="text-neutral-400 text-sm">Not all transactions are digital. Log your daily unrecorded offline cash sales here. Attach photos of your physical ledger or receipts as verifiable evidence.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Add Cash Transaction Form */}
              <div className="bg-black border border-[#222] p-5 rounded-xl">
                <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider">Log Cash Sale</h4>
                {error && <div className="mb-4 text-red-500 text-sm bg-red-950 border border-red-900 rounded p-2">{error}</div>}
                <form onSubmit={addCashTransaction} className="space-y-4">
                  <div>
                    <label className="text-xs text-neutral-500 block mb-1">Date</label>
                    <input type="date" value={cashInput.date} onChange={e => setCashInput({...cashInput, date: e.target.value})} className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2 text-white text-sm focus:border-yellow-500 outline-none" style={{ colorScheme: 'dark' }} required />
                  </div>
                  <div>
                    <label className="text-xs text-neutral-500 block mb-1">Amount (₹)</label>
                    <input type="number" placeholder="5000" value={cashInput.amount} onChange={e => setCashInput({...cashInput, amount: e.target.value})} className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2 text-white placeholder-neutral-500 text-sm focus:border-yellow-500 outline-none" required />
                  </div>
                  <div>
                    <label className="text-xs text-neutral-500 block mb-1">Description</label>
                    <input type="text" placeholder="Daily cash sales sum" value={cashInput.description} onChange={e => setCashInput({...cashInput, description: e.target.value})} className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2 text-white placeholder-neutral-500 text-sm focus:border-yellow-500 outline-none" />
                  </div>
                  <div>
                    <label className="text-xs text-neutral-500 block mb-1">Attach Evidence (Optional)</label>
                    <label className="w-full flex items-center justify-center gap-2 border border-dashed border-[#444] rounded-lg px-3 py-2 cursor-pointer hover:bg-[#181818] transition-colors">
                      <Camera size={16} className="text-neutral-400" />
                      <span className="text-xs text-neutral-300">
                        {cashInput.evidence ? cashInput.evidence.name : "Capture Receipt / Ledger"}
                      </span>
                      <input type="file" className="hidden" accept="image/*" onChange={handleEvidenceUpload} />
                    </label>
                  </div>
                  <button type="submit" className="w-full bg-yellow-600 text-white font-bold py-2 rounded-lg hover:bg-yellow-700 transition-colors text-sm">
                    Add to Ledger
                  </button>
                </form>
              </div>

              {/* Logged Transactions View */}
              <div className="bg-black border border-[#222] p-5 rounded-xl flex flex-col h-full max-h-[400px]">
                <h4 className="text-white font-semibold mb-4 text-sm uppercase tracking-wider flex justify-between">
                  <span>Verified Cash Ledger</span>
                  <span className="text-yellow-500">{cashTransactions.length} items</span>
                </h4>
                
                <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                  {cashTransactions.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-neutral-600 space-y-2">
                      <FileText size={32} />
                      <p className="text-xs">No cash transactions logged yet.</p>
                    </div>
                  ) : (
                    cashTransactions.map(tx => (
                      <div key={tx.id} className="bg-[#111] p-3 rounded-lg border border-[#333] flex justify-between items-center">
                        <div>
                          <p className="text-white text-sm font-medium">₹{tx.amount}</p>
                          <p className="text-xs text-neutral-500">{tx.date} • {tx.description || 'Cash Sale'}</p>
                        </div>
                        {tx.evidenceAttached && (
                          <div className="flex items-center gap-1 text-[10px] text-green-400 bg-green-900/20 px-2 py-1 rounded border border-green-900/50">
                            <CheckCircle size={12} /> Verified
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
                
                <button onClick={handleGeneratePassport} className="w-full bg-white text-black font-bold py-3 mt-4 rounded-xl hover:bg-neutral-200 transition-colors flex justify-center items-center gap-2">
                  Generate Passport <ArrowRight size={18} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Generate Passport */}
        {step === 5 && (
          <div className="text-center space-y-6 max-w-lg mx-auto">
            <div className="w-20 h-20 bg-blue-900/30 text-blue-400 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle size={40} className="animate-pulse" />
            </div>
            <h3 className="text-2xl font-bold text-white">Synthesizing Income Profile...</h3>
            <p className="text-neutral-400">We are combining your digital API data with your manually verified cash ledger to accurately estimate your holistic income stability and calculate your credit score.</p>
            
            <div className="pt-6">
              <a href="/passport" className="inline-block bg-blue-600 text-white font-bold py-3 px-8 rounded-xl hover:bg-blue-700 transition-colors shadow-[0_0_20px_rgba(37,99,235,0.4)]">
                View Financial Evidence Passport
              </a>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
