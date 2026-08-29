# tests/test_intervention_integration.py

import pytest
from django.utils import timezone
from core.models import (
    Plant, ProductionLine, Station, SimulationRun, Intervention, 
    Recommendation, InterventionExecution
)
from core.repositories.intervention_repository import InterventionRepository
from core.services.intervention_service import InterventionService
from core.services.exceptions import ConflictError, InvalidStateTransitionError

@pytest.fixture
def service():
    return InterventionService(InterventionRepository())

@pytest.fixture
def setup_data():
    plant = Plant.objects.create(plant_id="P1", name="Plant 1")
    line = ProductionLine.objects.create(line_id="L1", plant=plant, name="Line 1")
    sim = SimulationRun.objects.create(
        timestamp=timezone.now(), base_state_timestamp=timezone.now(),
        scenario_name="Test", horizon_minutes=30, number_of_runs=1
    )
    intervention = Intervention.objects.create(
        name="Tune Torque", description="Adjust parameter", cost=0.0, disruption_level=0.0
    )
    return sim, intervention

@pytest.mark.django_db
def test_integration_1_normal_flow(service, setup_data):
    sim, intervention = setup_data
    rec = Recommendation.objects.create(
        timestamp=timezone.now(), simulation=sim, intervention=intervention,
        decision_score=0.9, expected_throughput_gain=0.0, expected_risk_reduction=0.8,
        cost=0.0, confidence=0.95, status="PENDING"
    )

    # Execute
    exec_record = service.execute_intervention(rec.recommendation_id, "Applied settings")

    # Verify
    assert exec_record.execution_id is not None
    
    rec.refresh_from_db()
    assert rec.status == "EXECUTED"
    
    fetched_exec = InterventionExecution.objects.get(recommendation=rec)
    assert fetched_exec.execution_notes == "Applied settings"
    assert fetched_exec.status == "SUCCESS"

@pytest.mark.django_db
def test_integration_2_idempotency(service, setup_data):
    sim, intervention = setup_data
    rec = Recommendation.objects.create(
        timestamp=timezone.now(), simulation=sim, intervention=intervention,
        decision_score=0.9, expected_throughput_gain=0.0, expected_risk_reduction=0.8,
        cost=0.0, confidence=0.95, status="PENDING"
    )

    service.execute_intervention(rec.recommendation_id)

    # Attempt second execution
    with pytest.raises(ConflictError):
        service.execute_intervention(rec.recommendation_id)

@pytest.mark.django_db
def test_integration_3_state_transitions(service, setup_data):
    sim, intervention = setup_data
    rec = Recommendation.objects.create(
        timestamp=timezone.now(), simulation=sim, intervention=intervention,
        decision_score=0.5, expected_throughput_gain=1.0, expected_risk_reduction=0.1,
        cost=1000.0, confidence=0.5, status="PENDING"
    )

    # Reject
    service.reject_recommendation(rec.recommendation_id, "Not worth the cost")
    
    rec.refresh_from_db()
    assert rec.status == "REJECTED"

    # Attempt execute on rejected
    with pytest.raises(InvalidStateTransitionError):
        service.execute_intervention(rec.recommendation_id)