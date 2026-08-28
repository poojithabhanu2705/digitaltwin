# tests/test_risk_repository.py

import pytest
from core.models import StationDependency, VehicleExposure, VehicleState, Station, Vehicle, RiskPrediction
from core.repositories.risk_repository import RiskRepository
from django.utils import timezone

@pytest.mark.django_db
class TestRiskRepository:
    
    @pytest.fixture
    def setup_data(self):
        s1 = Station.objects.create(station_id="S1", capacity=1, base_cycle_time=1, position=1)
        s2 = Station.objects.create(station_id="S2", capacity=1, base_cycle_time=1, position=2)
        v1 = Vehicle.objects.create(vehicle_id="V1", arrival_time=timezone.now(), status="ACTIVE")
        
        StationDependency.objects.create(upstream_station=s1, downstream_station=s2, propagation_weight=0.5)
        VehicleState.objects.create(vehicle=v1, current_station=s1, status="ACTIVE", timestamp=timezone.now())
        
        pred = RiskPrediction.objects.create(entity_type="STATION", entity_id="S1", risk_score=0.8, confidence=1.0, timestamp=timezone.now(), model_name="M", model_version="1")
        
        return s1, s2, v1, pred

    def test_get_downstream_stations(self, setup_data):
        s1, s2, _, _ = setup_data
        repo = RiskRepository()
        deps = repo.get_downstream_stations(s1.station_id)
        assert len(deps) == 1
        assert deps[0].downstream_station_id == s2.station_id
        assert deps[0].propagation_weight == 0.5

    def test_get_vehicles_at_station(self, setup_data):
        s1, _, v1, _ = setup_data
        repo = RiskRepository()
        vehicles = repo.get_vehicles_at_station(s1.station_id)
        assert len(vehicles) == 1
        assert vehicles[0].vehicle_id == v1.vehicle_id

    def test_exposure_persistence_and_retrieval(self, setup_data):
        s1, _, v1, pred = setup_data
        repo = RiskRepository()
        
        exposure = VehicleExposure(
            vehicle=v1, station=s1, source_prediction=pred,
            station_risk=0.8, exposure_weight=1.0, propagated_risk=0.8,
            timestamp=timezone.now(), exposure_start_time=timezone.now()
        )
        
        repo.bulk_save_exposures([exposure])
        
        retrieved = repo.get_by_source_prediction(pred.prediction_id)
        assert retrieved.count() == 1
        assert retrieved.first().propagated_risk == 0.8
        assert retrieved.first().vehicle_id == v1.vehicle_id