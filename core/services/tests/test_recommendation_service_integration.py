# tests/test_recommendation_integration.py

import pytest
from django.utils import timezone
from core.models import Plant, ProductionLine, Station, SimulationRun, Intervention, SimulationOutcome, Recommendation
from core.services.recommendation_service import RecommendationService

# Minimal Inline Repository to satisfy constraint of not creating new repos in production code,
# while allowing integration tests to access DB.
class TestDecisionRepository:
    def get_simulation_run(self, sim_id):
        return SimulationRun.objects.filter(simulation_id=sim_id).first()
    def get_intervention(self, int_id):
        return Intervention.objects.filter(intervention_id=int_id).first()
    def get_simulation_outcomes(self, sim_id):
        return list(SimulationOutcome.objects.filter(simulation_run_id=sim_id))
    def save_recommendation(self, rec: Recommendation):
        rec.save()
        return rec

@pytest.fixture
def service():
    return RecommendationService(TestDecisionRepository())

@pytest.fixture
def base_data():
    plant = Plant.objects.create(plant_id="P1", name="Plant")
    line = ProductionLine.objects.create(line_id="L1", plant=plant, name="Line")
    station = Station.objects.create(
        station_id="S1", line=line, name="Station 1", 
        station_type="WELD", capacity=10, base_cycle_time=60, position=1
    )
    
    sim = SimulationRun.objects.create(
        timestamp=timezone.now(), base_state_timestamp=timezone.now(),
        scenario_name="Scenario A", horizon_minutes=30, number_of_runs=1
    )
    
    interv = Intervention.objects.create(
        name="Reduce Speed", description="test", cost=100.0, disruption_level=0.1
    )
    
    SimulationOutcome.objects.create(
        simulation_run=sim, station=station,
        simulated_throughput=90.0, simulated_risk=0.1,
        throughput_delta=5.0, risk_delta=-0.2, is_bottleneck=False
    )
    
    return sim, interv, station

@pytest.mark.django_db
def test_integration_normal_flow(service, base_data):
    sim, interv, _ = base_data
    
    candidate = [{"simulation_run_id": sim.simulation_id, "intervention_id": interv.intervention_id}]
    
    rec = service.evaluate_and_recommend(candidate)
    
    assert rec.recommendation_id is not None
    assert rec.status == "PENDING"
    assert rec.expected_throughput_gain == 5.0
    assert rec.expected_risk_reduction == 0.2
    assert rec.cost == 100.0
    # Score = 5.0 + (0.2 * 100) - 100 - (0.1 * 50) = 5 + 20 - 100 - 5 = -80.0
    assert rec.decision_score == -80.0

@pytest.mark.django_db
def test_integration_zero_risk_scenario(service, base_data):
    sim, interv, station = base_data
    # Delete previous outcomes, make a zero-risk outcome
    SimulationOutcome.objects.all().delete()
    
    SimulationOutcome.objects.create(
        simulation_run=sim, station=station,
        simulated_throughput=90.0, simulated_risk=0.0,
        throughput_delta=0.0, risk_delta=0.0, is_bottleneck=False
    )
    
    rec = service.evaluate_and_recommend([{"simulation_run_id": sim.simulation_id, "intervention_id": interv.intervention_id}])
    
    assert rec.expected_throughput_gain == 0.0
    assert rec.expected_risk_reduction == 0.0
    # Score = 0 + 0 - 100 - 5 = -105.0
    assert rec.decision_score == -105.0

@pytest.mark.django_db
def test_integration_immutability(service, base_data):
    sim, interv, _ = base_data
    original_cost = interv.cost
    original_horizon = sim.horizon_minutes
    
    service.evaluate_and_recommend([{"simulation_run_id": sim.simulation_id, "intervention_id": interv.intervention_id}])
    
    # Verify DB objects were not mutated
    interv.refresh_from_db()
    sim.refresh_from_db()
    
    assert interv.cost == original_cost
    assert sim.horizon_minutes == original_horizon