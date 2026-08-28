import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from ml.outcome_service import OutcomeService

class MockPrediction:
    def __init__(self, pred_id, ts, ent_type, ent_id, risk_score, horizon):
        self.prediction_id = pred_id
        self.timestamp = ts
        self.entity_type = ent_type
        self.entity_id = ent_id
        self.risk_score = risk_score
        self.prediction_horizon_minutes = horizon

class MockEvent:
    pass

@pytest.fixture
def repo_mock():
    repo = Mock()
    repo.get_for_prediction.return_value = None
    repo.create.side_effect = lambda **kwargs: kwargs
    return repo

@pytest.fixture
def service(repo_mock):
    return OutcomeService(outcome_repository=repo_mock, risk_threshold=0.5)

@pytest.fixture
def base_time():
    return datetime(2023, 1, 1, 10, 0, 0)

def test_correct_positive_prediction(service, repo_mock, base_time):
    prediction = MockPrediction(1, base_time, "VEHICLE", "V1", 0.8, 30)
    event_time = base_time + timedelta(minutes=10)
    
    result = service.evaluate(prediction, MockEvent(), True, event_time, "V1")
    
    assert result["matched"] is True
    assert result["outcome_type"] == "TRUE_POSITIVE"
    assert result["actual_outcome"] == "EVENT_OCCURRED"
    repo_mock.create.assert_called_once()

def test_correct_negative_prediction(service, repo_mock, base_time):
    prediction = MockPrediction(2, base_time, "STATION", "S1", 0.2, 30)
    event_time = base_time + timedelta(minutes=15)
    
    result = service.evaluate(prediction, MockEvent(), False, event_time, "S1")
    
    assert result["matched"] is True
    assert result["outcome_type"] == "TRUE_NEGATIVE"

def test_false_positive(service, repo_mock, base_time):
    prediction = MockPrediction(3, base_time, "VEHICLE", "V2", 0.9, 30)
    event_time = base_time + timedelta(minutes=5)
    
    result = service.evaluate(prediction, MockEvent(), False, event_time, "V2")
    
    assert result["matched"] is False
    assert result["outcome_type"] == "FALSE_POSITIVE"

def test_false_negative(service, repo_mock, base_time):
    prediction = MockPrediction(4, base_time, "STATION", "S2", 0.1, 30)
    event_time = base_time + timedelta(minutes=20)
    
    result = service.evaluate(prediction, MockEvent(), True, event_time, "S2")
    
    assert result["matched"] is False
    assert result["outcome_type"] == "FALSE_NEGATIVE"

def test_probability_boundary(service, repo_mock, base_time):
    # Score equals exactly threshold (0.5) -> should be treated as positive
    prediction = MockPrediction(5, base_time, "VEHICLE", "V3", 0.5, 30)
    event_time = base_time + timedelta(minutes=5)
    
    result = service.evaluate(prediction, MockEvent(), True, event_time, "V3")
    assert result["outcome_type"] == "TRUE_POSITIVE"

def test_probability_0(service, repo_mock, base_time):
    prediction = MockPrediction(6, base_time, "VEHICLE", "V4", 0.0, 30)
    event_time = base_time + timedelta(minutes=5)
    result = service.evaluate(prediction, MockEvent(), False, event_time, "V4")
    assert result["outcome_type"] == "TRUE_NEGATIVE"

def test_probability_1(service, repo_mock, base_time):
    prediction = MockPrediction(7, base_time, "VEHICLE", "V5", 1.0, 30)
    event_time = base_time + timedelta(minutes=5)
    result = service.evaluate(prediction, MockEvent(), True, event_time, "V5")
    assert result["outcome_type"] == "TRUE_POSITIVE"

def test_invalid_probability(service, repo_mock, base_time):
    prediction = MockPrediction(8, base_time, "VEHICLE", "V1", 1.5, 30)
    with pytest.raises(ValueError, match="Invalid prediction risk score"):
        service.evaluate(prediction, MockEvent(), True, base_time + timedelta(minutes=5), "V1")

def test_outcome_before_prediction(service, repo_mock, base_time):
    prediction = MockPrediction(9, base_time, "VEHICLE", "V1", 0.8, 30)
    event_time = base_time - timedelta(minutes=5)
    with pytest.raises(ValueError, match="cannot be earlier than prediction timestamp"):
        service.evaluate(prediction, MockEvent(), True, event_time, "V1")

def test_outcome_outside_horizon(service, repo_mock, base_time):
    prediction = MockPrediction(10, base_time, "VEHICLE", "V1", 0.8, 30)
    event_time = base_time + timedelta(minutes=45)
    with pytest.raises(ValueError, match="outside the prediction horizon"):
        service.evaluate(prediction, MockEvent(), True, event_time, "V1")

def test_wrong_entity(service, repo_mock, base_time):
    prediction = MockPrediction(11, base_time, "STATION", "S1", 0.8, 30)
    with pytest.raises(ValueError, match="Entity ID mismatch"):
        service.evaluate(prediction, MockEvent(), True, base_time + timedelta(minutes=5), "S2")

def test_duplicate_evaluation_idempotency(service, repo_mock, base_time):
    prediction = MockPrediction(12, base_time, "VEHICLE", "V1", 0.8, 30)
    existing_outcome = {"outcome_id": 99, "matched": True}
    repo_mock.get_for_prediction.return_value = existing_outcome
    
    result = service.evaluate(prediction, MockEvent(), True, base_time + timedelta(minutes=5), "V1")
    
    assert result == existing_outcome
    repo_mock.create.assert_not_called()

def test_missing_actual_outcome(service, base_time):
    prediction = MockPrediction(13, base_time, "VEHICLE", "V1", 0.8, 30)
    with pytest.raises(ValueError, match="actual event must be provided"):
        service.evaluate(prediction, None, True, base_time + timedelta(minutes=5), "V1")

def test_prediction_immutability(service, repo_mock, base_time):
    prediction = MockPrediction(14, base_time, "VEHICLE", "V1", 0.8, 30)
    event_time = base_time + timedelta(minutes=5)
    
    service.evaluate(prediction, MockEvent(), True, event_time, "V1")
    
    # Verify properties haven't changed
    assert prediction.risk_score == 0.8
    assert prediction.entity_id == "V1"