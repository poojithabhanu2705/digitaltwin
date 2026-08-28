# tests/test_risk_propagation_service.py

import pytest
from unittest.mock import Mock, MagicMock
from ml.risk_propagation_service import RiskPropagationService
from core.models import VehicleExposure

class MockPrediction:
    def __init__(self, pred_id, entity_id, risk_score):
        self.prediction_id = pred_id
        self.entity_type = "STATION"
        self.entity_id = entity_id
        self.risk_score = risk_score

class MockDependency:
    def __init__(self, down, weight):
        self.downstream_station_id = down
        self.propagation_weight = weight

class MockVehicleState:
    def __init__(self, vid):
        self.vehicle_id = vid

@pytest.fixture
def risk_repo():
    repo = Mock()
    repo.get_by_source_prediction.return_value = MagicMock(exists=lambda: False)
    repo.bulk_save_exposures.side_effect = lambda exposures: exposures
    repo.get_downstream_stations.return_value = []
    repo.get_vehicles_at_station.return_value = []
    return repo

@pytest.fixture
def service(risk_repo):
    return RiskPropagationService(risk_repo, risk_threshold=0.1, max_depth=3, default_exposure_weight=1.0)

# ===============================================
# TOPOLOGY & PROPAGATION TESTS
# ===============================================

@pytest.mark.parametrize("scenario, graph_map, vehicle_map, start_risk, expected_exposures", [
    # 1. Basic one-hop propagation
    ("one_hop", {"A": [MockDependency("B", 0.5)]}, {"B": ["V1"]}, 0.8, [("V1", "B", 0.4)]),
    # 2. Two-hop propagation
    ("two_hop", {"A": [MockDependency("B", 1.0)], "B": [MockDependency("C", 0.5)]}, {"C": ["V1"]}, 0.8, [("V1", "C", 0.4)]),
    # 3. Multi-hop propagation
    ("multi_hop", {"A": [MockDependency("B", 1.0)], "B": [MockDependency("C", 1.0)], "C": [MockDependency("D", 0.5)]}, {"D": ["V1"]}, 0.8, [("V1", "D", 0.4)]),
    # 4. No downstream nodes
    ("no_down", {"A": []}, {}, 0.8, []),
    # 5. Single-node structure (vehicles at source)
    ("single_node", {"A": []}, {"A": ["V1"]}, 0.8, [("V1", "A", 0.8)]),
    # 6. Branching structure
    ("branching", {"A": [MockDependency("B", 0.5), MockDependency("C", 0.5)]}, {"B": ["V1"], "C": ["V2"]}, 0.8, [("V1", "B", 0.4), ("V2", "C", 0.4)]),
    # 7. Converging structure (Max risk wins: A->B->D (0.2) vs A->C->D (0.72))
    ("converging", {"A": [MockDependency("B", 0.5), MockDependency("C", 0.9)], "B": [MockDependency("D", 0.5)], "C": [MockDependency("D", 0.9)]}, {"D": ["V1"]}, 0.8, [("V1", "D", 0.648)]),
    # 8. Multiple downstream nodes at same level
    ("multi_down", {"A": [MockDependency("B", 1.0), MockDependency("C", 1.0)]}, {"B": ["V1"], "C": ["V2"]}, 0.5, [("V1", "B", 0.5), ("V2", "C", 0.5)]),
    # 9. Correct source station execution
    ("correct_source", {"A": [MockDependency("B", 1.0)], "X": [MockDependency("Y", 1.0)]}, {"B": ["V1"], "Y": ["V2"]}, 0.8, [("V1", "B", 0.8)]),
    # 10. Unknown source station
    ("unknown_source", {"X": [MockDependency("Y", 1.0)]}, {"Y": ["V2"]}, 0.8, []),
    # 11. Zero risk propagation
    ("zero_risk", {"A": [MockDependency("B", 1.0)]}, {"B": ["V1"]}, 0.0, []),
    # 12. Maximum valid risk
    ("max_risk", {"A": [MockDependency("B", 1.0)]}, {"B": ["V1"]}, 1.0, [("V1", "B", 1.0)]),
    # 13. Exact threshold (0.1)
    ("exact_thresh", {"A": [MockDependency("B", 0.125)]}, {"B": ["V1"]}, 0.8, [("V1", "B", 0.1)]),
    # 14. Just below threshold (0.09)
    ("below_thresh", {"A": [MockDependency("B", 0.11)]}, {"B": ["V1"]}, 0.8, []),
    # 15. Just above threshold (0.11)
    ("above_thresh", {"A": [MockDependency("B", 0.1375)]}, {"B": ["V1"]}, 0.8, [("V1", "B", 0.11)]),
    # 16. Maximum propagation depth boundary (depth 3 excluded by default max_depth=3 fixture)
    ("depth_boundary", {"A": [MockDependency("B", 1.0)], "B": [MockDependency("C", 1.0)], "C": [MockDependency("D", 1.0)], "D": [MockDependency("E", 1.0)]}, {"E": ["V1"]}, 1.0, []),
    # 17. Cyclic dependency (A -> B -> A)
    ("cycle", {"A": [MockDependency("B", 0.8)], "B": [MockDependency("A", 0.8)]}, {"B": ["V1"]}, 1.0, [("V1", "B", 0.8)]),
    # 18. Self-loop
    ("self_loop", {"A": [MockDependency("A", 0.5)]}, {"A": ["V1"]}, 1.0, [("V1", "A", 1.0)]),
    # 19. Multiple cycles
    ("multi_cycle", {"A": [MockDependency("B", 0.9)], "B": [MockDependency("A", 0.9), MockDependency("C", 0.9)], "C": [MockDependency("B", 0.9)]}, {"C": ["V1"]}, 1.0, [("V1", "C", 0.81)]),
    # 20. Duplicate edges (max path overrides)
    ("duplicate_edge", {"A": [MockDependency("B", 0.5), MockDependency("B", 0.9)]}, {"B": ["V1"]}, 1.0, [("V1", "B", 0.9)]),
    # 21. Multiple paths to same destination
    ("multi_path_dest", {"A": [MockDependency("B", 0.8), MockDependency("C", 0.5)], "B": [MockDependency("D", 0.8)], "C": [MockDependency("D", 0.5)]}, {"D": ["V1"]}, 1.0, [("V1", "D", 0.64)]),
    # 22. Deep graph termination (cuts off safely)
    ("deep_graph", {"A": [MockDependency("B", 1.0)], "B": [MockDependency("C", 1.0)], "C": [MockDependency("D", 1.0)]}, {"D": ["V1"]}, 1.0, []),
    # 23. Disconnected components
    ("disconnected", {"A": [MockDependency("B", 1.0)], "X": [MockDependency("Y", 1.0)]}, {"Y": ["V1"]}, 1.0, []),
    # 24. Zero edge weight
    ("zero_weight", {"A": [MockDependency("B", 0.0)]}, {"B": ["V1"]}, 1.0, []),
    # 25. Maximum edge weight
    ("max_weight", {"A": [MockDependency("B", 1.0)]}, {"B": ["V1"]}, 1.0, [("V1", "B", 1.0)])
])
def test_topologies(scenario, graph_map, vehicle_map, start_risk, expected_exposures, service, risk_repo):
    prediction = MockPrediction(1, "A", start_risk)
    risk_repo.get_downstream_stations.side_effect = lambda n: graph_map.get(n, [])
    risk_repo.get_vehicles_at_station.side_effect = lambda n: [MockVehicleState(v) for v in vehicle_map.get(n, [])]
    
    results = service.propagate(prediction)
    
    assert len(results) == len(expected_exposures)
    for exp_v, exp_s, exp_r in expected_exposures:
        matched = any(
            r.vehicle_id == exp_v and 
            r.station_id == exp_s and 
            r.propagated_risk == pytest.approx(exp_r)
            for r in results
        )
        assert matched, f"[{scenario}] Missing or incorrect exposure for Vehicle {exp_v} at Station {exp_s}. Expected risk: {exp_r}"

# ===============================================
# VALIDATION & ERROR HANDLING TESTS
# ===============================================

def test_missing_prediction(service): # 26
    with pytest.raises(ValueError, match="Invalid RiskPrediction"):
        service.propagate(None)

def test_missing_prediction_id(service): # 27
    prediction = MockPrediction(None, "A", 0.5)
    del prediction.prediction_id
    with pytest.raises(ValueError, match="Invalid RiskPrediction"):
        service.propagate(prediction)

def test_negative_risk(service): # 28
    with pytest.raises(ValueError, match="out of bounds"):
        service.propagate(MockPrediction(1, "A", -0.1))

def test_risk_above_allowed_maximum(service): # 29
    with pytest.raises(ValueError, match="out of bounds"):
        service.propagate(MockPrediction(1, "A", 1.1))

def test_invalid_entity_type(service): # 30
    prediction = MockPrediction(1, "V1", 0.5)
    prediction.entity_type = "VEHICLE"
    with pytest.raises(ValueError, match="Expected STATION prediction"):
        service.propagate(prediction)

def test_invalid_edge_weight(service, risk_repo): # 31
    prediction = MockPrediction(1, "A", 0.5)
    risk_repo.get_downstream_stations.return_value = [MockDependency("B", -1.0)]
    with pytest.raises(ValueError, match="Invalid negative propagation weight"):
        service.propagate(prediction)

# ===============================================
# BEHAVIOR & IMMUTABILITY TESTS
# ===============================================

def test_input_immutability(service, risk_repo): # 32
    prediction = MockPrediction(1, "A", 0.8)
    risk_repo.get_downstream_stations.return_value = [MockDependency("B", 1.0)]
    
    service.propagate(prediction)
    
    assert prediction.prediction_id == 1
    assert prediction.entity_id == "A"
    assert prediction.risk_score == 0.8
    assert prediction.entity_type == "STATION"

def test_deterministic_repeated_execution(service, risk_repo): # 33
    prediction = MockPrediction(1, "A", 0.8)
    risk_repo.get_downstream_stations.side_effect = lambda n: [MockDependency("B", 0.5)] if n == "A" else []
    risk_repo.get_vehicles_at_station.side_effect = lambda n: [MockVehicleState("V1")] if n == "B" else []
    
    run_1 = service.propagate(prediction)
    
    # Reset iterators
    risk_repo.get_downstream_stations.side_effect = lambda n: [MockDependency("B", 0.5)] if n == "A" else []
    risk_repo.get_vehicles_at_station.side_effect = lambda n: [MockVehicleState("V1")] if n == "B" else []
    
    run_2 = service.propagate(prediction)
    
    assert run_1[0].propagated_risk == run_2[0].propagated_risk
    assert run_1[0].vehicle_id == run_2[0].vehicle_id

def test_idempotency_duplicate_propagation(service, risk_repo): # 34
    prediction = MockPrediction(1, "A", 0.8)
    
    # Mock that it was already processed
    mock_existing = MagicMock()
    mock_existing.exists.return_value = True
    mock_existing.__iter__.return_value = ["EXISTING_RECORD"]
    risk_repo.get_by_source_prediction.return_value = mock_existing
    
    result = service.propagate(prediction)
    
    assert result == ["EXISTING_RECORD"]
    risk_repo.bulk_save_exposures.assert_not_called()

def test_repository_failure_propagation(service, risk_repo): # 35
    prediction = MockPrediction(1, "A", 0.8)
    risk_repo.get_downstream_stations.side_effect = Exception("DB Connection Lost")
    
    with pytest.raises(Exception, match="DB Connection Lost"):
        service.propagate(prediction)