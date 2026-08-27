import pytest
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from django.utils import timezone

from core.models import RiskPrediction, PredictionExplanation
from core.repositories.ml_repository import PredictionExplanationRepository
from ml.explanation_service import ExplanationService
from ml.prediction_service import PredictionService

@pytest.fixture
def real_trained_model():
    # Train a deterministic mock model so SHAP can parse the actual tree structure
    X = np.random.rand(100, 8)
    y = np.random.randint(2, size=100)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model

@pytest.fixture
def sample_prediction():
    return RiskPrediction.objects.create(
        timestamp=timezone.now(),
        entity_type="STATION",
        entity_id="ST-101",
        risk_type="BOTTLENECK",
        risk_score=0.85,
        confidence=0.90,
        model_name="TestRF",
        model_version="v1"
    )

@pytest.mark.django_db
def test_explanation_service_database_integration(real_trained_model, sample_prediction):
    # 1. Arrange: Setup service with real repository and trained model
    service = ExplanationService(
        explanation_repository=PredictionExplanationRepository,
        risk_model=real_trained_model
    )
    
    feature_vector = [35.2, 1.1, 0.5, 95.0, 45.0, 0.2, 0.88, 36.1]

    # 2. Act: Execute explanation
    explanations = service.explain(sample_prediction, feature_vector)

    # 3. Assert: Verify database interactions and correctness
    saved_explanations = list(PredictionExplanationRepository.get_explanations(sample_prediction.prediction_id))
    
    assert len(saved_explanations) == 8
    
    # Assert ranking consistency
    assert abs(saved_explanations[0].contribution) >= abs(saved_explanations[-1].contribution)
    
    # Ensure foreign keys are linked properly
    assert saved_explanations[0].prediction.prediction_id == sample_prediction.prediction_id
    
    # Ensure specific features match the domain definition
    feature_names = [e.feature_name for e in saved_explanations]
    assert "avg_cycle_time" in feature_names
    assert "utilization" in feature_names