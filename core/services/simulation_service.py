import math
import copy
from typing import List, Dict, Any
from django.utils import timezone
from core.models import SimulationRun, SimulationOutcome

class ValidationError(Exception):
    pass

class SimulationService:
    """
    Evaluates scenario parameters against current state, predicted risk, 
    and propagated exposure to determine expected outcomes.
    """

    def __init__(
        self,
        state_repository,
        risk_repository,
        simulation_repository
    ):
        self.state_repo = state_repository
        self.risk_repo = risk_repository
        self.sim_repo = simulation_repository

    def simulate_scenario(
        self,
        plant_id: str,
        line_id: str,
        base_state_timestamp,
        scenario_name: str,
        scenario_type: str,
        parameters: Dict[str, Any],
        horizon_minutes: int,
        number_of_runs: int = 1
    ) -> SimulationRun:
        
        self._validate_numerical_inputs(horizon_minutes, number_of_runs)
        self._validate_parameters(parameters)

        # Retrieve Context
        station_states = self.state_repo.get_station_state_history(line_id, base_state_timestamp, base_state_timestamp)
        if not station_states:
            raise ValidationError(f"No current state found for line {line_id} at {base_state_timestamp}")

        active_predictions = self.risk_repo.get_active_predictions(line_id, base_state_timestamp)
        active_exposures = self.risk_repo.get_active_exposures(line_id, base_state_timestamp)

        # Deep copy to guarantee immutability of inputs
        sim_states = copy.deepcopy(list(station_states))
        sim_preds = copy.deepcopy(list(active_predictions))
        sim_exps = copy.deepcopy(list(active_exposures))

        # Initialize Simulation Run
        run = self.sim_repo.create_run(
            timestamp=timezone.now(),
            plant_id=plant_id,
            line_id=line_id,
            base_state_timestamp=base_state_timestamp,
            scenario_name=scenario_name,
            scenario_type=scenario_type,
            parameters=parameters,
            horizon_minutes=horizon_minutes,
            number_of_runs=number_of_runs,
            status="RUNNING"
        )

        outcomes = []
        target_station_id = parameters.get("target_station_id")
        risk_reduction_pct = parameters.get("risk_reduction_pct", 0.0)
        capacity_modifier = parameters.get("capacity_modifier", 1.0)

        for state in sim_states:
            station_id = state.station_id
            
            # Aggregate base risk and propagated risk
            base_risk = next((p.risk_score for p in sim_preds if p.entity_id == station_id), state.health_risk)
            propagated_risk = sum(e.propagated_risk for e in sim_exps if e.station_id == station_id)
            
            effective_risk = min(1.0, base_risk + propagated_risk)
            base_throughput = state.throughput

            # Apply Scenario Math
            is_target = (station_id == target_station_id)
            final_risk = effective_risk
            mod_capacity = 1.0

            if is_target:
                final_risk = max(0.0, effective_risk * (1.0 - (risk_reduction_pct / 100.0)))
                mod_capacity = capacity_modifier

            # Minimum deterministic formula for throughput impact
            simulated_throughput = base_throughput * mod_capacity * (1.0 - final_risk)
            
            outcomes.append(
                SimulationOutcome(
                    simulation_run=run,
                    station_id=station_id,
                    simulated_throughput=simulated_throughput,
                    simulated_risk=final_risk,
                    throughput_delta=simulated_throughput - base_throughput,
                    risk_delta=final_risk - effective_risk,
                    is_bottleneck=(simulated_throughput < (base_throughput * 0.5))
                )
            )

        self.sim_repo.save_outcomes(outcomes)
        
        run.status = "COMPLETED"
        run.save()
        return run

    def _validate_numerical_inputs(self, horizon, runs):
        if horizon <= 0 or math.isnan(horizon) or math.isinf(horizon):
            raise ValidationError(f"Invalid horizon_minutes: {horizon}")
        if runs <= 0 or math.isnan(runs) or math.isinf(runs):
            raise ValidationError(f"Invalid number_of_runs: {runs}")

    def _validate_parameters(self, params):
        if not params:
            return
            
        risk_red = params.get("risk_reduction_pct")
        if risk_red is not None and (risk_red < 0 or risk_red > 100 or math.isnan(risk_red)):
            raise ValidationError("risk_reduction_pct must be between 0 and 100")
            
        cap_mod = params.get("capacity_modifier")
        if cap_mod is not None and (cap_mod < 0 or math.isnan(cap_mod) or math.isinf(cap_mod)):
            raise ValidationError("capacity_modifier must be a positive finite number")