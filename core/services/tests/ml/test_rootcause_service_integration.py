import pytest
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from django.utils import timezone

from core.models import (
    Plant,
    ProductionLine,
    Station,
    StationFeature,
    StationState,
    RiskPrediction,
    MaintenanceEvent
)

from core.repositories.ml_repository import PredictionExplanationRepository, RootCauseRepository, PredictionRootCauseRepository
from core.services.ml.explanation_service import ExplanationService
from core.services.ml.rootcause_service import RootCauseService

@pytest.fixture
def real_trained_model():
    X = np.random.rand(100, 8)
    y = np.random.randint(2, size=100)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model

@pytest.fixture
def db_context():
    """Sets up the required physical hierarchy for the database foreign keys."""
    plant = Plant.objects.create(plant_id="PL-01", name="Test Plant")
    line = ProductionLine.objects.create(line_id="LN-01", plant=plant, name="Test Line")
    station = Station.objects.create(
        station_id="ST-101", 
        line=line, 
        name="Test Station", 
        station_type="ASSEMBLY", 
        capacity=1, 
        base_cycle_time=30.0, 
        position=1
    )
    
    prediction = RiskPrediction.objects.create(
        timestamp=timezone.now(),
        entity_type="STATION",
        entity_id="ST-101",
        risk_type="BOTTLENECK",
        risk_score=0.85,
        confidence=0.90,
        model_name="TestRF",
        model_version="v1"
    )
    
    return station, prediction

@pytest.mark.django_db
def test_integration_1_equipment_degradation(real_trained_model, db_context):
    station, prediction = db_context
    
    feature_vector = [35.2, 1.1, 0.5, 95.0, 45.0, 0.2, 0.88, 36.1]
    
    explanation_service = ExplanationService(PredictionExplanationRepository, risk_model=real_trained_model)
    explanations = explanation_service.explain(prediction, feature_vector)
    
    feature_obj = StationFeature.objects.create(station=station, timestamp=timezone.now(), vibration_mean=0.88)
    state_obj = StationState.objects.create(station=station, timestamp=timezone.now(), health_state="DEGRADED")
    
    rc_service = RootCauseService(RootCauseRepository, PredictionRootCauseRepository)
    root_cause = rc_service.analyze(prediction, explanations, feature_obj, state_obj)
    
    saved_prc = PredictionRootCauseRepository.get_for_prediction(prediction.prediction_id).first()
    assert saved_prc is not None
    assert saved_prc.root_cause.category in ["EQUIPMENT_DEGRADATION", "PROCESS_DEGRADATION"]
    assert "DEGRADED health" in saved_prc.evidence

@pytest.mark.django_db
def test_integration_2_insufficient_evidence(real_trained_model, db_context):
    station, prediction = db_context

    # Use a valid feature vector for the real model.
    feature_vector = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    explanation_service = ExplanationService(
        PredictionExplanationRepository,
        risk_model=real_trained_model,
    )

    explanations = explanation_service.explain(
        prediction,
        feature_vector,
    )

    # This test is specifically about RootCauseService's
    # insufficient-evidence behavior. Make the ML evidence
    # deterministic rather than depending on random SHAP output.
    for exp in explanations:
        exp.contribution = 0.0
        exp.direction = "NEGATIVE"

    feature_obj = StationFeature.objects.create(
        station=station,
        timestamp=timezone.now(),
    )

    state_obj = StationState.objects.create(
        station=station,
        timestamp=timezone.now(),
        health_state="NOMINAL",
    )

    rc_service = RootCauseService(
        RootCauseRepository,
        PredictionRootCauseRepository,
    )

    root_cause = rc_service.analyze(
        prediction,
        explanations,
        feature_obj,
        state_obj,
    )

    saved_prc = (
        PredictionRootCauseRepository
        .get_for_prediction(prediction.prediction_id)
        .first()
    )

    assert saved_prc.root_cause.category == "UNKNOWN"
    
@pytest.mark.django_db
def test_integration_3_with_maintenance_events(real_trained_model, db_context):
    station, prediction = db_context
    feature_vector = [35.2, 1.1, 0.5, 95.0, 45.0, 0.2, 0.88, 36.1]
    
    explanation_service = ExplanationService(PredictionExplanationRepository, risk_model=real_trained_model)
    explanations = explanation_service.explain(prediction, feature_vector)
    
    feature_obj = StationFeature.objects.create(station=station, timestamp=timezone.now())
    state_obj = StationState.objects.create(station=station, timestamp=timezone.now(), health_state="NOMINAL")
    
    # Inject a maintenance event
    event = MaintenanceEvent.objects.create(
        station=station, timestamp=timezone.now(), maintenance_type="EMERGENCY_REPAIR"
    )
    
    rc_service = RootCauseService(RootCauseRepository, PredictionRootCauseRepository)
    root_cause = rc_service.analyze(prediction, explanations, feature_obj, state_obj, events=[event])
    
    saved_prc = PredictionRootCauseRepository.get_for_prediction(prediction.prediction_id).first()
    assert "Recent maintenance event recorded: EMERGENCY_REPAIR" in saved_prc.evidence

@pytest.mark.django_db
def test_integration_4_process_degradation(real_trained_model, db_context):
    station, prediction = db_context
    
    # Feature vector that highly emphasizes cycle time (position 0 and 7)
    feature_vector = [99.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 99.9]
    
    explanation_service = ExplanationService(PredictionExplanationRepository, risk_model=real_trained_model)
    explanations = explanation_service.explain(prediction, feature_vector)
    
    # Manually force a high positive explanation for cycle time for this specific test
    for exp in explanations:
        if exp.feature_name == "avg_cycle_time":
            exp.contribution = 0.95
            exp.direction = "POSITIVE"
            
    feature_obj = StationFeature.objects.create(station=station, timestamp=timezone.now(), avg_cycle_time=99.9)
    state_obj = StationState.objects.create(station=station, timestamp=timezone.now(), health_state="NOMINAL")
    
    rc_service = RootCauseService(RootCauseRepository, PredictionRootCauseRepository)
    rc_service.analyze(prediction, explanations, feature_obj, state_obj)
    
    saved_prc = PredictionRootCauseRepository.get_for_prediction(prediction.prediction_id).first()
    assert saved_prc.root_cause.category == "PROCESS_DEGRADATION"

@pytest.mark.django_db
def test_integration_5_mismatched_prediction_fails(real_trained_model, db_context):
    station, prediction = db_context
    
    feature_vector = [35.2, 1.1, 0.5, 95.0, 45.0, 0.2, 0.88, 36.1]
    
    explanation_service = ExplanationService(PredictionExplanationRepository, risk_model=real_trained_model)
    explanations = explanation_service.explain(prediction, feature_vector)
    
    # Alter the prediction ID so the Root Cause service rejects it
    fake_prediction = RiskPrediction(prediction_id=9999)
    
    feature_obj = StationFeature.objects.create(station=station, timestamp=timezone.now())
    state_obj = StationState.objects.create(station=station, timestamp=timezone.now())
    
    rc_service = RootCauseService(RootCauseRepository, PredictionRootCauseRepository)
    
    with pytest.raises(ValueError, match="Mismatch"):
        rc_service.analyze(fake_prediction, explanations, feature_obj, state_obj)