import pytest
from core.models import SimulationRun, SimulationOutcome, Plant, ProductionLine, Station
from core.repositories.simulation_repository import SimulationRepository
from django.utils import timezone

@pytest.mark.django_db
def test_save_outcomes_persistence():
    plant = Plant.objects.create(plant_id="P1", name="Plant 1")
    line = ProductionLine.objects.create(line_id="L1", plant=plant, name="Line 1")
    station = Station.objects.create(station_id="ST1", line=line, name="St1", station_type="A", capacity=100, base_cycle_time=1.0, position=1)
    
    run = SimulationRun.objects.create(
        timestamp=timezone.now(),
        plant=plant, line=line,
        base_state_timestamp=timezone.now(),
        scenario_name="Test",
        horizon_minutes=60,
        number_of_runs=1
    )
    
    outcome = SimulationOutcome(
        simulation_run=run,
        station=station,
        simulated_throughput=90.0,
        simulated_risk=0.1,
        throughput_delta=-10.0,
        risk_delta=0.0
    )
    
    result = SimulationRepository.save_outcomes([outcome])
    
    assert len(result) == 1
    assert SimulationOutcome.objects.count() == 1
    
    fetched = SimulationRepository.get_outcomes_for_run(run.simulation_id)
    assert len(fetched) == 1
    assert fetched[0].simulated_throughput == 90.0