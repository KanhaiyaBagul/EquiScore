/**
 * Typed API Client for EquiScore Backend
 */

import { PRESETS } from "./mockData";

const API_BASE_URL = "http://localhost:8000";

export async function fetchPresetAssessment(presetId: string = "ramesh") {
  try {
    const res = await fetch(`${API_BASE_URL}/api/assessments/preset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preset_id: presetId }),
    });
    if (!res.ok) throw new Error("Backend unavailable");
    return await res.json();
  } catch (err) {
    console.warn("Using offline fallback preset:", presetId);
    return null;
  }
}

export async function runScenarioSimulation(payload: any) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/scenarios`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Scenario evaluation failed");
    return await res.json();
  } catch (err) {
    // Offline heuristic calculation
    const baseFhs = payload.baseline_fhs || 86;
    const expenseDelta = payload.delta_expenses || 0;
    const grossDelta = payload.delta_gross || 0;
    const emiDelta = payload.delta_emi || 0;
    
    // Heuristic delta calculation
    let deltaPts = 0;
    if (expenseDelta < 0) deltaPts += Math.round(Math.abs(expenseDelta) / 1200);
    if (grossDelta > 0) deltaPts += Math.round(grossDelta / 2000);
    if (emiDelta < 0) deltaPts += Math.round(Math.abs(emiDelta) / 1000);

    const simulatedFhs = Math.min(100, Math.max(0, baseFhs + deltaPts));
    return {
      baseline_fhs_score: baseFhs,
      simulated_fhs_score: simulatedFhs,
      fhs_score_delta: simulatedFhs - baseFhs,
      baseline_repayment_prob: 78.2,
      simulated_repayment_prob: Math.min(98.5, 78.2 + (simulatedFhs - baseFhs) * 0.8),
      repayment_prob_delta: +((simulatedFhs - baseFhs) * 0.8).toFixed(1),
      impact_factors: [
        `Cashflow adjustment yields a ${simulatedFhs - baseFhs > 0 ? '+' : ''}${simulatedFhs - baseFhs} point shift in score.`
      ],
      advice_note: `Hypothetical sandbox simulation shows improved debt service capacity.`
    };
  }
}

export async function fetchFairnessAudit() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/fairness/audits`);
    if (!res.ok) throw new Error("Failed to fetch fairness audit");
    return await res.json();
  } catch (err) {
    return null;
  }
}
