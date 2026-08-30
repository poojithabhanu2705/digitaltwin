import apiClient, { cachedGet, clearCache } from "./client";

export interface SimulationOutcome {
  outcome_id: number;
  station_id: string;
  station_name: string;
  simulated_throughput: number;
  simulated_risk: number;
  throughput_delta: number;
  risk_delta: number;
  is_bottleneck: boolean;
}

export interface Recommendation {
  recommendation_id: number;
  timestamp: string;
  decision_score: number;
  expected_throughput_gain: number;
  expected_risk_reduction: number;
  cost: string;
  confidence: number;
  status: string;
  rationale: string;
  intervention_id: number;
  intervention_name: string;
  intervention_description: string;
}

export interface SimulationRun {
  simulation_id: number;
  timestamp: string;
  plant_id: string | null;
  plant_name: string | null;
  line_id: string | null;
  line_name: string | null;
  base_state_timestamp: string;
  scenario_name: string;
  scenario_type: string;
  parameters: Record<string, unknown>;
  horizon_minutes: number;
  number_of_runs: number;
  status: string;
  outcomes: SimulationOutcome[];
  recommendations?: Recommendation[];
}

export interface RunSimulationParams {
  line_id: string;
  target_station_id?: string;
  capacity_modifier?: number;
  risk_reduction_pct?: number;
  scenario_name?: string;
  scenario_type?: string;
  horizon_minutes?: number;
}

export async function getSimulations(
  forceRefresh = false,
): Promise<SimulationRun[]> {
  return cachedGet<SimulationRun[]>(
    "simulations",
    "/simulation/",
    forceRefresh,
  );
}

export async function getSimulation(
  simulationId: number,
  forceRefresh = false,
): Promise<SimulationRun> {
  return cachedGet<SimulationRun>(
    `simulation:${simulationId}`,
    `/simulation/${simulationId}/`,
    forceRefresh,
  );
}

export async function runSimulation(
  params: RunSimulationParams,
): Promise<SimulationRun> {
  const response = await apiClient.post<SimulationRun>("/simulation/", params);
  return response.data;
}

export function clearSimulationCache(): void {
  clearCache("simulations");
}