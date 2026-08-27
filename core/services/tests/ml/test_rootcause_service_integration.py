from core.repositories.ml_repository import RootCauseRepository, PredictionRootCauseRepository
from ml.root_cause_service import RootCauseService

@pytest.mark.django_db
def test_end_to_end_ml_pipeline(real_trained_model, sample_prediction):
    # This tests Prediction -> Explanation -> RootCause integration
    
    # 1. Generate Explanations
    explanation_service = ExplanationService(PredictionExplanationRepository, risk_model=real_trained_model)
    feature_vector = [35.2, 1.1, 0.5, 95.0, 45.0, 0.2, 0.88, 36.1]
    
    explanations = explanation_service.explain(sample_prediction, feature_vector)
    
    # 2. Mock upstream Features/State required by RootCause
    feature_obj = StationFeature.objects.create(
        station_id="ST-101", timestamp=timezone.now(), vibration_mean=0.88
    )
    state_obj = StationState.objects.create(
        station_id="ST-101", timestamp=timezone.now(), health_state="DEGRADED"
    )
    
    # 3. Generate Root Cause
    rc_service = RootCauseService(RootCauseRepository, PredictionRootCauseRepository)
    root_cause = rc_service.analyze(sample_prediction, explanations, feature_obj, state_obj)
    
    # 4. Assertions ensuring chain continuity and DB writes
    assert root_cause.prediction.prediction_id == sample_prediction.prediction_id
    
    # Check that root cause was persisted correctly via repository
    saved_prc = PredictionRootCauseRepository.get_for_prediction(sample_prediction.prediction_id).first()
    assert saved_prc is not None
    assert saved_prc.prediction.prediction_id == sample_prediction.prediction_id
    
    # Check evidence traceability (since State was DEGRADED, it must be in the evidence)
    assert "DEGRADED health" in saved_prc.evidence
    
    # Verify no prediction mutation occurred throughout the pipeline
    assert sample_prediction.risk_score == 0.85