import pytest

from django.utils import timezone

from core.models import (
    Plant,
    ProductionLine,
    Station,
    Vehicle,
    StationFeature,
    StationState,
    VehicleFeature,
    VehicleState,
    RiskPrediction,
)

from core.repositories.prediction_repository import PredictionRepository
from core.services.ml.prediction_service import PredictionService


@pytest.mark.django_db
def test_real_station_model_inference():
    """
    End-to-end test using the REAL trained Station Risk model.

    Flow:

        Database records
            ↓
        PredictionService
            ↓
        MLModelLoader
            ↓
        Real StationRiskRandomForest
            ↓
        PredictionRepository
            ↓
        RiskPrediction
    """

    # ============================================================
    # 1. Create hierarchy
    # ============================================================

    plant = Plant.objects.create(
        plant_id="ML-PL-01",
        name="ML Test Plant",
    )

    line = ProductionLine.objects.create(
        line_id="ML-LN-01",
        plant=plant,
        name="ML Test Line",
    )

    station = Station.objects.create(
        station_id="ML-ST-01",
        line=line,
        name="ML Test Station",
        station_type="ASSEMBLY",
        capacity=1,
        base_cycle_time=30.0,
        position=1,
    )

    # ============================================================
    # 2. Create realistic station features
    # ============================================================

    feature = StationFeature.objects.create(
        timestamp=timezone.now(),
        station=station,
        avg_cycle_time=42.0,
        cycle_time_std=5.5,
        cycle_time_trend=3.2,
        throughput=72.0,
        temperature_mean=58.0,
        vibration_mean=1.8,
        utilization=0.91,
    )

    # ============================================================
    # 3. Create current station state
    # ============================================================

    state = StationState.objects.create(
        timestamp=timezone.now(),
        station=station,
        health_state="WARNING",
        current_cycle_time=47.0,
    )

    # ============================================================
    # 4. Create PredictionService
    #
    # No model is injected here.
    #
    # Therefore PredictionService must load the REAL model
    # through MLModelLoader.
    # ============================================================

    service = PredictionService(
        prediction_repository=PredictionRepository,
        model_version="1.0",
    )

    # ============================================================
    # 5. Execute REAL station inference
    # ============================================================

    prediction = service.predict(
        station_features=feature,
        station_state=state,
    )

    # ============================================================
    # 6. Validate returned database object
    # ============================================================

    assert prediction is not None

    assert isinstance(
        prediction,
        RiskPrediction,
    )

    assert prediction.entity_type == "STATION"
    assert prediction.entity_id == station.station_id

    assert prediction.risk_type == "BOTTLENECK"
    assert prediction.prediction_target == "HIGH_RISK_STATE"

    assert 0.0 <= prediction.risk_score <= 1.0
    assert 0.0 <= prediction.confidence <= 1.0

    assert prediction.model_name == "StationRiskRandomForest"
    assert prediction.model_version == "1.0"

    assert prediction.prediction_horizon_minutes == 30

    # ============================================================
    # 7. Confirm persistence
    # ============================================================

    assert RiskPrediction.objects.filter(
        prediction_id=prediction.prediction_id
    ).exists()


@pytest.mark.django_db
def test_real_vehicle_defect_model_inference():
    """
    End-to-end test using the REAL trained Vehicle Defect model.

    Flow:

        Database records
            ↓
        PredictionService
            ↓
        MLModelLoader
            ↓
        Real VehicleDefectRandomForest
            ↓
        PredictionRepository
            ↓
        RiskPrediction
    """

    # ============================================================
    # 1. Create hierarchy
    # ============================================================

    plant = Plant.objects.create(
        plant_id="ML-PL-02",
        name="ML Vehicle Test Plant",
    )

    line = ProductionLine.objects.create(
        line_id="ML-LN-02",
        plant=plant,
        name="ML Vehicle Test Line",
    )

    station = Station.objects.create(
        station_id="ML-ST-02",
        line=line,
        name="ML Vehicle Test Station",
        station_type="ASSEMBLY",
        capacity=1,
        base_cycle_time=30.0,
        position=1,
    )

    vehicle = Vehicle.objects.create(
        vehicle_id="ML-VH-01",
        line=line,
        variant="TEST-VARIANT",
        production_order="ML-ORDER-01",
        arrival_time=timezone.now(),
        status="IN_PROGRESS",
    )

    # ============================================================
    # 2. Create station features
    #
    # These are the first five inputs required by the vehicle
    # defect model.
    # ============================================================

    station_feature = StationFeature.objects.create(
        timestamp=timezone.now(),
        station=station,
        avg_cycle_time=42.0,
        cycle_time_std=5.5,
        cycle_time_trend=3.2,
        throughput=72.0,
        temperature_mean=58.0,
        vibration_mean=1.8,
        utilization=0.91,
    )

    # ============================================================
    # 3. Create station state
    # ============================================================

    station_state = StationState.objects.create(
        timestamp=timezone.now(),
        station=station,
        health_state="WARNING",
        current_cycle_time=47.0,
    )

    # ============================================================
    # 4. Create vehicle features
    #
    # These provide the vehicle-specific inputs:
    #
    # vehicle_avg_cycle_time
    # vehicle_cycle_time_deviation
    # vehicle_quality_event_count
    # ============================================================

    vehicle_feature = VehicleFeature.objects.create(
        timestamp=timezone.now(),
        vehicle=vehicle,
        variant="TEST-VARIANT",
        avg_cycle_time=39.0,
        cycle_time_deviation=8.5,
        torque_deviation=2.0,
        stations_exposed=3,
        degraded_station_count=1,
        cumulative_risk=0.35,
        quality_event_count=2,
        manual_observation_count=1,
    )

    # ============================================================
    # 5. Create vehicle state
    # ============================================================

    vehicle_state = VehicleState.objects.create(
        timestamp=timezone.now(),
        vehicle=vehicle,
        current_station=station,
        status="IN_PROGRESS",
        quality_risk=0.25,
        confidence=0.90,
        risk_source="ML_TEST",
    )

    # ============================================================
    # 6. Create PredictionService
    #
    # No model is injected.
    #
    # This forces the service to load the REAL trained models.
    # ============================================================

    service = PredictionService(
        prediction_repository=PredictionRepository,
        model_version="1.0",
    )

    # ============================================================
    # 7. Execute REAL vehicle defect inference
    # ============================================================

    prediction = service.predict(
        station_features=station_feature,
        station_state=station_state,
        vehicle_features=vehicle_feature,
        vehicle_state=vehicle_state,
    )

    # ============================================================
    # 8. Validate returned database object
    # ============================================================

    assert prediction is not None

    assert isinstance(
        prediction,
        RiskPrediction,
    )

    assert prediction.entity_type == "VEHICLE"
    assert prediction.entity_id == vehicle.vehicle_id

    assert prediction.risk_type == "DEFECT"
    assert prediction.prediction_target == "QUALITY_DEFECT"

    assert 0.0 <= prediction.risk_score <= 1.0
    assert 0.0 <= prediction.confidence <= 1.0

    assert prediction.model_name == "VehicleDefectRandomForest"
    assert prediction.model_version == "1.0"

    assert prediction.prediction_horizon_minutes == 30

    # ============================================================
    # 9. Confirm persistence
    # ============================================================

    assert RiskPrediction.objects.filter(
        prediction_id=prediction.prediction_id
    ).exists()