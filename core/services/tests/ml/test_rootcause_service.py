import pytest
from unittest.mock import Mock
from ml.rootcause_service import RootCauseService

@pytest.fixture
def mock_repos():
    rc_repo = Mock()
    rc_repo.get_by_name.return_value = Mock(root_cause_id=1, category="MOCK", name="MOCK")
    
    prc_repo = Mock()
    prc_repo.create.side_effect = lambda **kwargs: Mock(**kwargs)
    
    return rc_repo, prc_repo

@pytest.fixture
def base_inputs():
    prediction = Mock(prediction_id=100)
    features = Mock(vibration_mean=0.8)
    state = Mock(health_state="NOMINAL")
    return prediction, features, state

def test_1_basic_root_cause(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    rc_repo, prc_repo = mock_repos
    
    exp1 = Mock(prediction_id=100, feature_name="vibration_mean", contribution=0.5, direction="POSITIVE")
    service = RootCauseService(rc_repo, prc_repo)
    
    result = service.analyze(prediction, [exp1], features, state)
    
    assert result.contribution == 0.5
    assert result.prediction == prediction
    prc_repo.create.assert_called_once()

def test_2_equipment_degradation(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    state.health_state = "DEGRADED"  # Adds 0.3 to EQUIPMENT_DEGRADATION
    
    exp1 = Mock(prediction_id=100, feature_name="vibration_mean", contribution=0.4, direction="POSITIVE")
    
    service = RootCauseService(*mock_repos)
    result = service.analyze(prediction, [exp1], features, state)
    
    mock_repos[0].get_by_name.assert_called_with("EQUIPMENT_DEGRADATION", "Abnormal Vibration")
    assert "DEGRADED health" in result.evidence
    assert result.contribution == 0.7  # 0.4 (SHAP) + 0.3 (State)

def test_3_and_4_thermal_and_quality(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    exp_thermal = Mock(prediction_id=100, feature_name="temperature_mean", contribution=0.6, direction="POSITIVE")
    
    service = RootCauseService(*mock_repos)
    service.analyze(prediction, [exp_thermal], features, state)
    mock_repos[0].get_by_name.assert_called_with("THERMAL_ISSUE", "Overheating")

def test_5_and_6_explanation_contributions(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    # Positive contributes to score
    exp_pos = Mock(prediction_id=100, feature_name="vibration_mean", contribution=0.4, direction="POSITIVE")
    # Negative should be ignored by the engine
    exp_neg = Mock(prediction_id=100, feature_name="temperature_mean", contribution=-0.3, direction="NEGATIVE")
    
    service = RootCauseService(*mock_repos)
    result = service.analyze(prediction, [exp_pos, exp_neg], features, state)
    
    # Thermal issue should NOT be queried
    mock_repos[0].get_by_name.assert_called_with("EQUIPMENT_DEGRADATION", "Abnormal Vibration")
    assert "temperature_mean" not in result.evidence

def test_7_evidence_traceability(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    exp = Mock(prediction_id=100, feature_name="utilization", contribution=0.25, direction="POSITIVE")
    
    service = RootCauseService(*mock_repos)
    result = service.analyze(prediction, [exp], features, state)
    
    # Must explicitly mention the exact inputs used
    assert "utilization" in result.evidence
    assert "+0.25" in result.evidence

def test_8_insufficient_evidence(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    service = RootCauseService(*mock_repos)
    
    # No explanations, no degraded state
    result = service.analyze(prediction, [], features, state)
    mock_repos[0].get_by_name.assert_called_with("UNKNOWN", "Insufficient Evidence")
    assert result.contribution == 0.0

def test_9_confidence_range(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    exp = Mock(prediction_id=100, feature_name="vibration_mean", contribution=0.5, direction="POSITIVE")
    
    service = RootCauseService(*mock_repos)
    result = service.analyze(prediction, [exp], features, state)
    
    assert 0.0 <= result.confidence <= 1.0

def test_10_prediction_mismatch(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    exp = Mock(prediction_id=999) # Mismatched ID
    
    service = RootCauseService(*mock_repos)
    with pytest.raises(ValueError, match="Mismatch"):
        service.analyze(prediction, [exp], features, state)

def test_11_missing_optional_events(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    exp = Mock(prediction_id=100, feature_name="vibration_mean", contribution=0.5, direction="POSITIVE")
    service = RootCauseService(*mock_repos)
    
    # Called without events param
    result = service.analyze(prediction, [exp], features, state)
    assert result is not None

def test_12_invalid_feature():
    service = RootCauseService(Mock(), Mock())
    with pytest.raises(ValueError):
        service.analyze(Mock(prediction_id=1), [], None, Mock())

def test_13_repository_persistence(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    service = RootCauseService(*mock_repos)
    service.analyze(prediction, [], features, state)
    
    # Ensure save was called directly on repo
    mock_repos[1].create.assert_called_once()

def test_14_no_prediction_mutation(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    original_id = prediction.prediction_id
    
    service = RootCauseService(*mock_repos)
    service.analyze(prediction, [], features, state)
    
    # Ensure prediction wasn't mutated
    assert prediction.prediction_id == original_id

def test_15_determinism(mock_repos, base_inputs):
    prediction, features, state = base_inputs
    exp = Mock(prediction_id=100, feature_name="vibration_mean", contribution=0.5, direction="POSITIVE")
    service = RootCauseService(*mock_repos)
    
    res1 = service.analyze(prediction, [exp], features, state)
    res2 = service.analyze(prediction, [exp], features, state)
    
    assert res1.evidence == res2.evidence
    assert res1.contribution == res2.contribution
    assert res1.confidence == res2.confidence