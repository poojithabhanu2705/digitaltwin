import pytest
from unittest.mock import Mock
from django.utils import timezone

from core.models import (
    Plant, 
    ProductionLine, 
    Station, 
    StationFeature, 
    StationState, 
    RiskPrediction
)
from core.repositories.prediction_repository import PredictionRepository
from core.services.ml.prediction_service import PredictionService

# This fixture creates dummy data in your test database before the test runs
@pytest.fixture
def setup_database():
    # 1. Create the master hierarchy (Plant -> Line -> Station)
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
    
    # 2. Create the feature and state data required by the service
    now = timezone.now()
    feature = StationFeature.objects.create(
        station=station,
        timestamp=now,
        avg_cycle_time=32.5,
        cycle_time_std=1.2,
        temperature_mean=45.0,
        vibration_mean=0.5,
        utilization=0.85,
        throughput=100.0
    )
    
    state = StationState.objects.create(
        station=station,
        timestamp=now,
        health_state="NOMINAL",
        current_cycle_time=33.1
    )
    
    return feature, state

# The django_db marker is required for any test that touches the database
@pytest.mark.django_db
def test_prediction_service_database_integration(setup_database):
    # 1. Arrange: Unpack the database records and set up the service
    feature, state = setup_database
    
    # We mock the ML model to avoid loading a heavy .pkl file during testing
    mock_model = Mock()
    mock_model.__class__.__name__ = "IntegrationTestRF"
    # Simulating a scenario where the model predicts a 90% chance of high risk
    mock_model.predict_proba.return_value = [[0.1, 0.9]] 
    
    service = PredictionService(
        prediction_repository=PredictionRepository,
        risk_model=mock_model,
        model_version="v2.0"
    )
    
    # 2. Act: Run the prediction (This should trigger a database save via the repository)
    service.predict(station_features=feature, station_state=state)
    
    # 3. Assert: Verify the data was actually written to the database using the repository
    saved_prediction = PredictionRepository.get_latest(
        entity_type="STATION",
        entity_id="ST-101",
        risk_type="BOTTLENECK"
    )
    
    # Check that the prediction exists and the values match our inputs
    assert saved_prediction is not None, "The prediction was not saved to the database!"
    assert saved_prediction.entity_id == "ST-101"
    assert saved_prediction.risk_score == 0.9
    assert saved_prediction.confidence == 0.9
    assert saved_prediction.model_name == "IntegrationTestRF"
    assert saved_prediction.model_version == "v2.0"