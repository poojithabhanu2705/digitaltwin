# tests/test_recommendation_service.py

import pytest
from unittest.mock import Mock
from django.utils import timezone
from core.models import SimulationRun, Intervention, SimulationOutcome, Recommendation
from core.services.decision.recommendation_service import RecommendationService, ValidationError, NotFoundError

@pytest.fixture
def mock_repo():
    repo = Mock()
    # Echo back the recommendation for saving
    repo.save_recommendation.side_effect = lambda r: r
    return repo

@pytest.fixture
def service(mock_repo):
    return RecommendationService(decision_repository=mock_repo)

def create_mock_sim_run(sim_id):
    return SimulationRun(
        simulation_id=sim_id
    )


def create_mock_intervention(int_id, cost, disruption):
    return Intervention(
        intervention_id=int_id,
        cost=cost,
        disruption_level=disruption
    )

def create_mock_outcome(t_delta, r_delta):
    out = Mock(spec=SimulationOutcome)
    out.throughput_delta = t_delta
    out.risk_delta = r_delta
    return out

def test_empty_candidate_list(service):
    with pytest.raises(ValidationError, match="cannot be empty"):
        service.evaluate_and_recommend([])

def test_missing_candidate_keys(service):
    with pytest.raises(ValidationError, match="must contain 'simulation_run_id'"):
        service.evaluate_and_recommend([{"simulation_run_id": 1}]) # Missing intervention_id

def test_missing_simulation_upstream(service, mock_repo):
    mock_repo.get_simulation_run.return_value = None
    with pytest.raises(NotFoundError, match="SimulationRun with ID 1 not found"):
        service.evaluate_and_recommend([{"simulation_run_id": 1, "intervention_id": 2}])

def test_missing_intervention_upstream(service, mock_repo):
    mock_repo.get_simulation_run.return_value = create_mock_sim_run(1)
    mock_repo.get_intervention.return_value = None
    with pytest.raises(NotFoundError, match="Intervention with ID 2 not found"):
        service.evaluate_and_recommend([{"simulation_run_id": 1, "intervention_id": 2}])

def test_single_candidate_normal_flow(service, mock_repo):
    sim = create_mock_sim_run(1)
    interv = create_mock_intervention(10, cost=500.0, disruption=0.2)
    
    outcomes = [
        create_mock_outcome(t_delta=5.0, r_delta=-0.1),
        create_mock_outcome(t_delta=2.0, r_delta=-0.05)
    ]
    
    mock_repo.get_simulation_run.return_value = sim
    mock_repo.get_intervention.return_value = interv
    mock_repo.get_simulation_outcomes.return_value = outcomes

    rec = service.evaluate_and_recommend([{"simulation_run_id": 1, "intervention_id": 10}])

    # Assertions
    assert rec.simulation == sim
    assert rec.intervention == interv
    assert rec.expected_throughput_gain == pytest.approx(7.0)
    assert rec.expected_risk_reduction == pytest.approx(0.15)
    assert rec.cost == 500.0
    assert rec.status == "PENDING"
    
    # Expected Score: 7.0 + (0.15 * 100) - 500 - (0.2 * 50) = 7 + 15 - 500 - 10 = -488.0
    assert rec.decision_score == pytest.approx(-488.0)

def test_multiple_candidates_best_selection(service, mock_repo):
    sim1 = create_mock_sim_run(1)
    int1 = create_mock_intervention(10, cost=1000.0, disruption=0.5) # Bad
    
    sim2 = create_mock_sim_run(2)
    int2 = create_mock_intervention(20, cost=100.0, disruption=0.1)  # Good
    
    def get_sim_run(sim_id): return sim1 if sim_id == 1 else sim2
    def get_interv(int_id): return int1 if int_id == 10 else int2
    def get_outcomes(sim_id):
        if sim_id == 1:
            return [create_mock_outcome(1.0, -0.01)]
        return [create_mock_outcome(10.0, -0.2)]

    mock_repo.get_simulation_run.side_effect = get_sim_run
    mock_repo.get_intervention.side_effect = get_interv
    mock_repo.get_simulation_outcomes.side_effect = get_outcomes

    candidates = [
        {"simulation_run_id": 1, "intervention_id": 10},
        {"simulation_run_id": 2, "intervention_id": 20}
    ]

    rec = service.evaluate_and_recommend(candidates)

    # Assert Candidate 2 is chosen
    assert rec.simulation.simulation_id == 2
    assert rec.intervention.intervention_id == 20
    assert rec.expected_throughput_gain == pytest.approx(10.0)

def test_tie_breaker_by_cost_and_disruption(service, mock_repo):
    sim1 = create_mock_sim_run(1)
    sim2 = create_mock_sim_run(2)
    
    # Int1 and Int2 produce EXACTLY the same gross score offsets, 
    # but Int2 has lower cost (which the tie breaker prefers if scores perfectly match)
    int1 = create_mock_intervention(10, cost=200.0, disruption=0.0) 
    int2 = create_mock_intervention(20, cost=150.0, disruption=1.0) # wait, score includes cost/disruption. 
    # To trigger a tie, the TOTAL scores must match.
    # Score = T + R*100 - C - D*50.
    # Let T=0, R=0 for both.
    # Int 1: Cost=100, Disruption=1.0 -> -100 - 50 = -150
    # Int 2: Cost=150, Disruption=0.0 -> -150 - 0 = -150
    # Tie! Same score. Tie-breaker favors lower cost -> Int 1.

    int1 = create_mock_intervention(10, cost=100.0, disruption=1.0)
    int2 = create_mock_intervention(20, cost=150.0, disruption=0.0)

    mock_repo.get_simulation_run.side_effect = lambda x: sim1 if x==1 else sim2
    mock_repo.get_intervention.side_effect = lambda x: int1 if x==10 else int2
    mock_repo.get_simulation_outcomes.return_value = [] # Zero T and R

    rec = service.evaluate_and_recommend([
        {"simulation_run_id": 1, "intervention_id": 10},
        {"simulation_run_id": 2, "intervention_id": 20}
    ])

    assert rec.intervention.intervention_id == 10 # Lower cost won the tie