import { cachedGet, clearCache } from "./client";

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

export interface SimulationRun {
  simulation_id: number;
  timestamp: string;
  plant_id: string | null;
  line_id: string | null;
  base_state_timestamp: string;
  scenario_name: string;
  scenario_type: string;
  parameters: Record<string, unknown>;
  horizon_minutes: number;
  number_of_runs: number;
  status: string;
  outcomes: SimulationOutcome[];
}

export async function getSimulations(
  forceRefresh = false,
): Promise<SimulationRun[]> {
  return cachedGet<SimulationRun[]>(
    "simulations",
    "/simulations/",
    forceRefresh,
  );
}

export async function getSimulation(
  simulationId: number,
  forceRefresh = false,
): Promise<SimulationRun> {
  return cachedGet<SimulationRun>(
    `simulation:${simulationId}`,
    `/simulations/${simulationId}/`,
    forceRefresh,
  );
}

export function clearSimulationCache(): void {
  clearCache("simulations");
}