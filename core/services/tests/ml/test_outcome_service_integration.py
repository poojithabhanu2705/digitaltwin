import pytest
from datetime import timedelta
from django.utils import timezone

from core.models import (
    Plant, ProductionLine, Station, Vehicle, QualityEvent, 
    RiskPrediction, PredictionOutcome
)
from core.repositories.ml_repository import PredictionOutcomeRepository, PredictionRepository
from core.services.ml.prediction_service import PredictionService
from core.services.ml.outcome_service import OutcomeService

@pytest.mark.django_db
class TestPipelineIntegration:
    
    @pytest.fixture
    def setup_data(self):
        plant = Plant.objects.create(plant_id="P1", name="Plant 1")
        line = ProductionLine.objects.create(line_id="L1", plant=plant, name="Line 1")
        station = Station.objects.create(
            station_id="S1", line=line, name="Station 1", 
            capacity=1, base_cycle_time=60, position=1
        )
        vehicle = Vehicle.objects.create(
            vehicle_id="V1", line=line, variant="Sedan", 
            production_order="PO-1", arrival_time=timezone.now(), status="ACTIVE"
        )
        return station, vehicle

    def test_end_to_end_evaluation_true_positive(self, setup_data):
        station, vehicle = setup_data
        base_time = timezone.now()
        
        # 1. Create Prediction (Simulating PredictionService output)
        prediction = RiskPrediction.objects.create(
            timestamp=base_time,
            entity_type="VEHICLE",
            entity_id=vehicle.vehicle_id,
            risk_type="DEFECT",
            prediction_target="QUALITY_DEFECT",
            risk_score=0.85,
            confidence=0.9,
            prediction_horizon_minutes=60,
            model_name="DefectModel",
            model_version="1.0"
        )
        
        # 2. Simulate Actual Event (Quality Event with defect flag)
        event_time = base_time + timedelta(minutes=15)
        actual_event = QualityEvent.objects.create(
            timestamp=event_time,
            vehicle=vehicle,
            station=station,
            defect_flag=True,
            defect_type="Paint Scratch"
        )
        
        # 3. Evaluate Outcome
        outcome_repo = PredictionOutcomeRepository()
        outcome_service = OutcomeService(outcome_repository=outcome_repo)
        
        outcome = outcome_service.evaluate(
            prediction=prediction,
            actual_event=actual_event,
            actual_event_occurred=actual_event.defect_flag,
            event_timestamp=actual_event.timestamp,
            entity_id=actual_event.vehicle.vehicle_id
        )
        
        # 4. Verify Database Persistence and Logic
        assert outcome.outcome_id is not None
        assert outcome.matched is True
        assert outcome.outcome_type == "TRUE_POSITIVE"
        assert outcome.prediction.prediction_id == prediction.prediction_id
        
        # Original prediction remains unchanged
        refreshed_prediction = RiskPrediction.objects.get(prediction_id=prediction.prediction_id)
        assert refreshed_prediction.risk_score == 0.85

    def test_duplicate_evaluation_returns_existing(self, setup_data):
        station, vehicle = setup_data
        base_time = timezone.now()
        
        prediction = RiskPrediction.objects.create(
            timestamp=base_time,
            entity_type="VEHICLE",
            entity_id=vehicle.vehicle_id,
            risk_type="DEFECT",
            risk_score=0.85,
            confidence=0.9,
            prediction_horizon_minutes=60,
            model_name="DefectModel",
            model_version="1.0"
        )
        
        actual_event = QualityEvent.objects.create(
            timestamp=base_time + timedelta(minutes=15),
            vehicle=vehicle,
            defect_flag=True
        )
        
        outcome_service = OutcomeService(PredictionOutcomeRepository())
        
        first_outcome = outcome_service.evaluate(
            prediction, actual_event, actual_event.defect_flag, actual_event.timestamp, actual_event.vehicle.vehicle_id
        )
        
        second_outcome = outcome_service.evaluate(
            prediction, actual_event, actual_event.defect_flag, actual_event.timestamp, actual_event.vehicle.vehicle_id
        )
        
        assert first_outcome.outcome_id == second_outcome.outcome_id
        assert PredictionOutcome.objects.count() == 1