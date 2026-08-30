import { cachedGet, clearCache } from "./client";

export interface RiskExplanation {
  id: number;
  feature_name: string;
  contribution: number;
  direction: string;
}

export interface RiskRootCause {
  id: number;
  root_cause_id: number;
  category: string;
  name: string;
  description: string;
  contribution: number;
  confidence: number;
  evidence: string;
}

export interface RiskOutcome {
  outcome_id: number;
  observed_at: string;
  outcome_type: string;
  actual_outcome: string;
  actual_value: number | null;
  matched: boolean | null;
  lead_time_minutes: number | null;
  notes: string;
}

export interface RiskPrediction {
  prediction_id: number;
  timestamp: string;
  entity_type: string;
  entity_id: string;
  risk_type: string;
  prediction_target: string;
  risk_score: number;
  confidence: number;
  prediction_horizon_minutes: number | null;
  model_name: string;
  model_version: string;
  explanations: RiskExplanation[];
  root_causes: RiskRootCause[];
  outcome: RiskOutcome | null;
}

const RISKS_CACHE_KEY = "risks";

export async function getRisks(
  forceRefresh = false,
): Promise<RiskPrediction[]> {
  return cachedGet<RiskPrediction[]>(
    RISKS_CACHE_KEY,
    "/risks/?limit=50",
    forceRefresh,
  );
}

export function clearRisksCache(): void {
  clearCache(RISKS_CACHE_KEY);
}