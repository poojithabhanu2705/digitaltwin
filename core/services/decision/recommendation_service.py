# service/recommendation_service.py

import logging
from typing import List, Dict, Any
from django.utils import timezone

from core.models import Recommendation, SimulationRun, Intervention, SimulationOutcome

# Assuming shared exceptions exist as per architecture
class ValidationError(Exception):
    pass

class NotFoundError(Exception):
    pass

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Evaluates simulated scenario outcomes against candidate interventions 
    to generate an optimal, deterministic recommendation.
    """

    def __init__(self, decision_repository):
        # We use an injected repository to strictly adhere to the service/repo boundary
        self.repo = decision_repository

    def evaluate_and_recommend(self, candidates: List[Dict[str, Any]]) -> Recommendation:
        """
        Evaluates a list of candidate scenarios and produces a Recommendation.
        
        Expected candidate format:
        [
            {"simulation_run_id": 1, "intervention_id": 2},
            ...
        ]
        """
        if not candidates:
            raise ValidationError("Candidate list cannot be empty.")

        best_score = -float('inf')
        best_candidate_data = None

        for cand in candidates:
            sim_id = cand.get("simulation_run_id")
            int_id = cand.get("intervention_id")

            if sim_id is None or int_id is None:
                raise ValidationError("All candidates must contain 'simulation_run_id' and 'intervention_id'.")

            # Fetch immutable upstream references
            sim_run = self.repo.get_simulation_run(sim_id)
            intervention = self.repo.get_intervention(int_id)
            
            if not sim_run:
                raise NotFoundError(f"SimulationRun with ID {sim_id} not found.")
            if not intervention:
                raise NotFoundError(f"Intervention with ID {int_id} not found.")

            outcomes = self.repo.get_simulation_outcomes(sim_id)
            if not outcomes:
                logger.warning(f"SimulationRun {sim_id} has no outcomes. Proceeding with zero gains.")
            
            # 1. Aggregate Simulation Deltas
            throughput_gain = sum(float(o.throughput_delta) for o in outcomes)
            risk_reduction = sum(-float(o.risk_delta) for o in outcomes)

            # 2. Deterministic Scoring Logic
            # Normalizing factors assumed to balance units
            score = (
                throughput_gain 
                + (risk_reduction * 100.0) 
                - float(intervention.cost) 
                - (float(intervention.disruption_level) * 50.0)
            )

            # 3. Deterministic Ranking & Tie-breaking
            is_better = False
            if score > best_score:
                is_better = True
            elif score == best_score and best_candidate_data is not None:
                # Tie-breaker 1: Lowest Cost
                if float(intervention.cost) < best_candidate_data["cost"]:
                    is_better = True
                # Tie-breaker 2: Lowest Disruption
                elif float(intervention.cost) == best_candidate_data["cost"]:
                    if float(intervention.disruption_level) < best_candidate_data["disruption"]:
                        is_better = True
                    # Tie-breaker 3: Lowest ID
                    elif float(intervention.disruption_level) == best_candidate_data["disruption"]:
                        if int_id < best_candidate_data["intervention"].intervention_id:
                            is_better = True

            if is_better or best_candidate_data is None:
                best_score = score
                best_candidate_data = {
                    "simulation": sim_run,
                    "intervention": intervention,
                    "score": score,
                    "throughput_gain": throughput_gain,
                    "risk_reduction": risk_reduction,
                    "cost": intervention.cost,
                    "disruption": float(intervention.disruption_level)
                }

        # 4. Generate Output Recommendation
        rec = Recommendation(
            timestamp=timezone.now(),
            simulation=best_candidate_data["simulation"],
            intervention=best_candidate_data["intervention"],
            decision_score=best_candidate_data["score"],
            expected_throughput_gain=best_candidate_data["throughput_gain"],
            expected_risk_reduction=best_candidate_data["risk_reduction"],
            cost=best_candidate_data["cost"],
            confidence=0.9,  # Base static confidence, as ML inference logic is forbidden here
            status="PENDING",
            rationale=f"Selected candidate with deterministic score: {best_candidate_data['score']:.2f}"
        )

        return self.repo.save_recommendation(rec)