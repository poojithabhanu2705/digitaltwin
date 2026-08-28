# ml/risk_propagation_service.py

import logging
from collections import deque
from django.utils import timezone
from core.models import VehicleExposure

logger = logging.getLogger(__name__)

class RiskPropagationService:
    """
    Consumes ML RiskPredictions, propagates risk through the production 
    structure (StationDependencies), and generates VehicleExposure records.
    
    Implementation Rules Applied:
    - Multiple paths: Maximization (path yielding highest risk overwrites lower risks).
    - Cycles: Safely broken via visited risk tracking.
    - Missing constraints: Threshold defaults to 0.05, max depth to 5.
    - Edge weight attenuation: propagated_risk = risk * edge.propagation_weight.
    """

    def __init__(
        self,
        risk_repository,
        risk_threshold: float = 0.05,
        max_depth: int = 5,
        default_exposure_weight: float = 1.0
    ):
        self.risk_repo = risk_repository
        self.risk_threshold = risk_threshold
        self.max_depth = max_depth
        self.default_exposure_weight = default_exposure_weight

    def propagate(self, prediction):
        """
        Determines downstream vehicle exposure for a given RiskPrediction.
        """
        self._validate_prediction(prediction)

        # Idempotency Check
        existing_exposures = self.risk_repo.get_by_source_prediction(prediction.prediction_id)
        if existing_exposures.exists():
            logger.info(f"Prediction {prediction.prediction_id} already propagated.")
            return list(existing_exposures)

        source_station = prediction.entity_id
        initial_risk = prediction.risk_score

        if initial_risk < self.risk_threshold:
            logger.info("Initial risk is below propagation threshold.")
            return []

        # Queue: (station_id, current_risk, depth)
        queue = deque([(source_station, initial_risk, 0)])
        
        # Track maximum risk seen per station to handle multiple paths and cycles
        visited_station_risks = {source_station: initial_risk}

        while queue:
            curr_station, curr_risk, depth = queue.popleft()

            if depth >= self.max_depth:
                continue

            dependencies = self.risk_repo.get_downstream_stations(curr_station)

            for dep in dependencies:
                self._validate_edge(dep)
                downstream_station = dep.downstream_station_id
                
                propagated_risk = curr_risk * dep.propagation_weight

                if propagated_risk < self.risk_threshold:
                    continue

                # Cycle & Multiple Path Protection:
                # Only proceed if we found a path that yields a STRICTLY HIGHER risk score
                if downstream_station in visited_station_risks and visited_station_risks[downstream_station] >= propagated_risk:
                    continue

                visited_station_risks[downstream_station] = propagated_risk
                queue.append((downstream_station, propagated_risk, depth + 1))

        return self._generate_and_persist_exposures(prediction, visited_station_risks)

    def _generate_and_persist_exposures(self, prediction, visited_station_risks):
        exposures_to_create = []
        timestamp = timezone.now()
        
        for station_id, station_risk in visited_station_risks.items():
            vehicles = self.risk_repo.get_vehicles_at_station(station_id)
            
            for v_state in vehicles:
                propagated_vehicle_risk = station_risk * self.default_exposure_weight
                
                exposure = VehicleExposure(
                    timestamp=timestamp,
                    vehicle_id=v_state.vehicle_id,
                    station_id=station_id,
                    source_prediction_id=prediction.prediction_id,
                    station_risk=station_risk,
                    exposure_weight=self.default_exposure_weight,
                    propagated_risk=propagated_vehicle_risk,
                    exposure_start_time=timestamp
                )
                exposures_to_create.append(exposure)

        if exposures_to_create:
            return self.risk_repo.bulk_save_exposures(exposures_to_create)
            
        return []

    def _validate_prediction(self, prediction):
        if not prediction or not hasattr(prediction, 'prediction_id'):
            raise ValueError("Invalid RiskPrediction object provided.")
        if getattr(prediction, 'entity_type', None) != "STATION":
            raise ValueError(f"Expected STATION prediction, got {getattr(prediction, 'entity_type', None)}")
        if not (0.0 <= prediction.risk_score <= 1.0):
            raise ValueError(f"Risk score {prediction.risk_score} is out of bounds [0, 1].")

    def _validate_edge(self, edge):
        if getattr(edge, 'propagation_weight', -1.0) < 0:
            raise ValueError(f"Invalid negative propagation weight on edge to {edge.downstream_station_id}.")