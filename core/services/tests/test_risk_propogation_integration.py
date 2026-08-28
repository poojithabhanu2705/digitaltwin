# tests/test_integration_risk_propagation.py

import pytest
from core.models import RiskPrediction, Station, StationDependency, Vehicle, VehicleState, VehicleExposure
from core.repositories.risk_repository import RiskRepository
from risk_propagation_service import RiskPropagationService
from django.utils import timezone

@pytest.mark.django_db
class TestPropagationIntegration:
    
    @pytest.fixture
    def complex_graph(self):
        # A -> B -> D
        # A -> C -> D
        # D -> A (Cycle)
        sA = Station.objects.create(station_id="A", capacity=1, base_cycle_time=1, position=1)
        sB = Station.objects.create(station_id="B", capacity=1, base_cycle_time=1, position=2)
        sC = Station.objects.create(station_id="C", capacity=1, base_cycle_time=1, position=3)
        sD = Station.objects.create(station_id="D", capacity=1, base_cycle_time=1, position=4)
        
        StationDependency.objects.create(upstream_station=sA, downstream_station=sB, propagation_weight=0.8)
        StationDependency.objects.create(upstream_station=sA, downstream_station=sC, propagation_weight=0.5)
        StationDependency.objects.create(upstream_station=sB, downstream_station=sD, propagation_weight=0.5)
        StationDependency.objects.create(upstream_station=sC, downstream_station=sD, propagation_weight=0.9)
        StationDependency.objects.create(upstream_station=sD, downstream_station=sA, propagation_weight=0.1) # Cycle
        
        vB = Vehicle.objects.create(vehicle_id="V_B", arrival_time=timezone.now(), status="ACTIVE")
        vD = Vehicle.objects.create(vehicle_id="V_D", arrival_time=timezone.now(), status="ACTIVE")
        
        VehicleState.objects.create(vehicle=vB, current_station=sB, status="ACTIVE", timestamp=timezone.now())
        VehicleState.objects.create(vehicle=vD, current_station=sD, status="ACTIVE", timestamp=timezone.now())
        
        return sA, sB, sC, sD, vB, vD

    # INTEGRATION 1, 3, 4, 5, 6 - Normal Flow, Multi-Hop, Branching, Converging, and Cycle
    def test_comprehensive_flow(self, complex_graph):
        sA, sB, sC, sD, vB, vD = complex_graph
        
        prediction = RiskPrediction.objects.create(
            timestamp=timezone.now(), entity_type="STATION", entity_id=sA.station_id,
            risk_score=1.0, confidence=1.0, model_name="M", model_version="1"
        )
        
        service = RiskPropagationService(RiskRepository(), risk_threshold=0.05, max_depth=5)
        service.propagate(prediction)
        
        exposures = VehicleExposure.objects.filter(source_prediction=prediction)
        
        # We expect exposures at B (via A->B) and D (via A->C->D max path)
        assert exposures.count() == 2
        
        exp_B = exposures.get(station=sB)
        assert exp_B.vehicle == vB
        assert exp_B.propagated_risk == pytest.approx(0.8) # 1.0 * 0.8
        
        exp_D = exposures.get(station=sD)
        assert exp_D.vehicle == vD
        # A->B->D = 1.0 * 0.8 * 0.5 = 0.40
        # A->C->D = 1.0 * 0.5 * 0.9 = 0.45 (Max path wins)
        assert exp_D.propagated_risk == pytest.approx(0.45)
        
        # Ensure cycle did not infinitely loop and mutate A's initial exposure logic inappropriately

    # INTEGRATION 7, 8 - Invalid / Unknown Source
    def test_invalid_source_validation(self):
        prediction = RiskPrediction.objects.create(
            timestamp=timezone.now(), entity_type="STATION", entity_id="UNKNOWN",
            risk_score=0.8, confidence=1.0, model_name="M", model_version="1"
        )
        service = RiskPropagationService(RiskRepository())
        results = service.propagate(prediction)
        
        # Validates without crashing, returns empty
        assert len(results) == 0
        assert VehicleExposure.objects.count() == 0

    # INTEGRATION 10 - Duplicate Execution / Idempotency
    def test_idempotent_execution(self, complex_graph):
        sA = complex_graph[0]
        prediction = RiskPrediction.objects.create(
            timestamp=timezone.now(), entity_type="STATION", entity_id=sA.station_id,
            risk_score=1.0, confidence=1.0, model_name="M", model_version="1"
        )
        
        service = RiskPropagationService(RiskRepository(), risk_threshold=0.05, max_depth=5)
        
        # First Run
        service.propagate(prediction)
        count_1 = VehicleExposure.objects.count()
        
        # Second Run
        service.propagate(prediction)
        count_2 = VehicleExposure.objects.count()
        
        assert count_1 > 0
        assert count_1 == count_2 # DB was not mutated twice

    # INTEGRATION 12 - Immutability
    def test_input_immutability(self, complex_graph):
        sA = complex_graph[0]
        prediction = RiskPrediction.objects.create(
            timestamp=timezone.now(), entity_type="STATION", entity_id=sA.station_id,
            risk_score=0.77, confidence=1.0, model_name="M", model_version="1"
        )
        
        service = RiskPropagationService(RiskRepository())
        service.propagate(prediction)
        
        # Refresh from DB to verify it wasn't mutated in memory and saved
        refreshed = RiskPrediction.objects.get(prediction_id=prediction.prediction_id)
        assert refreshed.risk_score == 0.77
        assert refreshed.entity_id == sA.station_id