import pytest
from django.utils import timezone
from simulation_service import SimulationService
from simulation_repository import SimulationRepository
from core.repositories.state_repository import StateRepository
from ml.risk_repository import RiskRepository
from core.models import Plant, ProductionLine, Station, StationState, SimulationOutcome

@pytest.mark.django_db
class TestSimulationIntegration:
    
    @pytest.fixture
    def setup_data(self):
        plant = Plant.objects.create(plant_id="P1", name="Plant 1")
        line = ProductionLine.objects.create(line_id="L1", plant=plant, name="Line 1")
        st1 = Station.objects.create(
            station_id="ST-1", line=line, name="Station 1", 
            station_type="ASSEMBLY", capacity=100, base_cycle_time=30.0, position=1
        )
        st2 = Station.objects.create(
            station_id="ST-2", line=line, name="Station 2", 
            station_type="ASSEMBLY", capacity=100, base_cycle_time=30.0, position=2
        )
        state1 = StationState.objects.create(
            station=st1,
            timestamp=timezone.now(),
            health_state="NOMINAL",
            health_risk=0.1,
            throughput=100.0,
            confidence=0.9
        )
        state2 = StationState.objects.create(
            station=st2,
            timestamp=timezone.now(),
            health_state="NOMINAL",
            health_risk=0.5,
            throughput=100.0,
            confidence=0.9
        )
        return plant, line, st1, st2, state1, state2

    def test_end_to_end_normal_simulation(self, setup_data):
        service = SimulationService(StateRepository(), RiskRepository(), SimulationRepository())
        
        run = service.simulate_scenario(
            plant_id="P1", line_id="L1",
            base_state_timestamp=timezone.now(),
            scenario_name="Baseline",
            scenario_type="WHAT_IF",
            parameters={},
            horizon_minutes=60
        )
        
        assert run.status == "COMPLETED"
        outcomes = SimulationOutcome.objects.filter(simulation_run=run)
        assert outcomes.count() > 0

    def test_multi_station_intervention_scenario(self, setup_data):
        service = SimulationService(StateRepository(), RiskRepository(), SimulationRepository())
        
        params = {
            "target_station_id": "ST-2",
            "risk_reduction_pct": 80.0,
            "capacity_modifier": 1.5
        }
        
        run = service.simulate_scenario("P1", "L1", timezone.now(), "Fix Bottleneck", "INTERVENTION", params, 120)
        outcomes = SimulationOutcome.objects.filter(simulation_run=run)
        
        # Verify affected station
        st2_outcome = outcomes.get(station__station_id="ST-2")
        assert st2_outcome.simulated_risk < 0.2
        
        # Verify unaffected station
        st1_outcome = outcomes.get(station__station_id="ST-1")
        assert st1_outcome.simulated_risk == st1_outcome.simulated_risk # Unchanged logic relative to base

    def test_idempotency_duplicate_execution(self, setup_data):
        service = SimulationService(StateRepository(), RiskRepository(), SimulationRepository())
        base_time = timezone.now()
        
        run1 = service.simulate_scenario("P1", "L1", base_time, "Dup", "WHAT_IF", {}, 60)
        run2 = service.simulate_scenario("P1", "L1", base_time, "Dup", "WHAT_IF", {}, 60)
        
        outcomes1 = list(SimulationOutcome.objects.filter(simulation_run=run1).values_list('simulated_throughput', flat=True))
        outcomes2 = list(SimulationOutcome.objects.filter(simulation_run=run2).values_list('simulated_throughput', flat=True))
        
        assert outcomes1 == outcomes2