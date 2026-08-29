import pytest

from datetime import timedelta

from django.utils import timezone

from core.models import (
    Plant,
    ProductionLine,
    Station,
    StationFeature,
    Vehicle,
    VehicleFeature,
)

from core.services.exceptions import (
    NotFoundError,
    ValidationError,
)

from core.services.features.feature_service import (
    FeatureService,
)


# ================================================================
# FIXTURES
# ================================================================


@pytest.fixture
def feature_service():
    return FeatureService()


@pytest.fixture
def station(db):
    plant = Plant.objects.create(
        plant_id="PL-FEATURE-TEST",
        name="Feature Test Plant",
        location="Test Location",
    )

    line = ProductionLine.objects.create(
        line_id="LINE-FEATURE-TEST",
        plant=plant,
        name="Feature Test Line",
    )

    return Station.objects.create(
        station_id="ST-FEATURE-TEST",
        line=line,
        name="Feature Test Station",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=15.0,
        position=1,
    )


@pytest.fixture
def vehicle(station):
    return Vehicle.objects.create(
        vehicle_id="FEATURE-TEST-VH-001",
        line=station.line,
        variant="SUV",
        production_order="FEATURE-TEST-ORDER-001",
        arrival_time=timezone.now(),
        status="IN_PROGRESS",
    )


# ================================================================
# STATION FEATURES
# ================================================================


@pytest.mark.django_db
def test_create_and_get_station_feature(
    feature_service,
    station,
):
    timestamp = timezone.now()

    feature = feature_service.save_station_feature(
        timestamp=timestamp,
        station=station,
        avg_cycle_time=42.5,
        cycle_time_std=2.5,
        cycle_time_trend=0.2,
        avg_torque=100.0,
        torque_deviation=5.0,
        temperature_mean=70.0,
        vibration_mean=1.2,
        alarm_rate=0.05,
        utilization=0.8,
        throughput=120.0,
        wip=4.0,
        blocking_time=2.0,
        starvation_time=1.0,
        sensor_coverage_ratio=0.95,
        data_completeness=0.98,
        imputation_ratio=0.02,
        manual_observation_count=3,
    )

    assert feature.id is not None
    assert feature.station == station
    assert feature.timestamp == timestamp
    assert feature.avg_cycle_time == 42.5

    fetched = feature_service.get_station_feature(feature.id)

    assert fetched.id == feature.id
    assert fetched.station == station
    assert fetched.avg_cycle_time == 42.5


@pytest.mark.django_db
def test_get_latest_station_feature(
    feature_service,
    station,
):
    first_time = timezone.now()
    second_time = first_time + timedelta(minutes=1)

    first = feature_service.save_station_feature(
        timestamp=first_time,
        station=station,
        avg_cycle_time=40.0,
    )

    second = feature_service.save_station_feature(
        timestamp=second_time,
        station=station,
        avg_cycle_time=50.0,
    )

    latest = feature_service.get_latest_station_feature(
        station.station_id
    )

    assert latest.id == second.id
    assert latest.id != first.id
    assert latest.avg_cycle_time == 50.0


@pytest.mark.django_db
def test_get_station_features_range(
    feature_service,
    station,
):
    first_time = timezone.now()
    second_time = first_time + timedelta(minutes=1)

    first = feature_service.save_station_feature(
        timestamp=first_time,
        station=station,
        avg_cycle_time=40.0,
    )

    second = feature_service.save_station_feature(
        timestamp=second_time,
        station=station,
        avg_cycle_time=50.0,
    )

    features = list(
        feature_service.get_station_features(
            station.station_id,
            first_time,
            second_time,
        )
    )

    assert len(features) == 2
    assert [feature.id for feature in features] == [first.id, second.id]


@pytest.mark.django_db
def test_get_station_features_latest_first(
    feature_service,
    station,
):
    first_time = timezone.now()
    second_time = first_time + timedelta(minutes=1)

    first = feature_service.save_station_feature(
        timestamp=first_time,
        station=station,
        avg_cycle_time=40.0,
    )

    second = feature_service.save_station_feature(
        timestamp=second_time,
        station=station,
        avg_cycle_time=50.0,
    )

    features = list(
        feature_service.get_station_features_latest_first(
            station.station_id,
            first_time,
            second_time,
        )
    )

    assert len(features) == 2
    assert [feature.id for feature in features] == [second.id, first.id]


@pytest.mark.django_db
def test_bulk_save_station_features(
    feature_service,
    station,
):
    base_time = timezone.now()

    features = [
        StationFeature(
            timestamp=base_time,
            station=station,
            utilization=0.5,
            throughput=100.0,
        ),
        StationFeature(
            timestamp=base_time + timedelta(minutes=1),
            station=station,
            utilization=0.7,
            throughput=125.0,
        ),
    ]

    created = feature_service.bulk_save_station_features(features)

    assert len(created) == 2
    assert created[0].station == station
    assert created[1].station == station
    assert created[0].utilization == 0.5
    assert created[1].throughput == 125.0


# ================================================================
# VEHICLE FEATURES
# ================================================================


@pytest.mark.django_db
def test_create_and_get_vehicle_feature(
    feature_service,
    vehicle,
):
    timestamp = timezone.now()

    feature = feature_service.save_vehicle_feature(
        timestamp=timestamp,
        vehicle=vehicle,
        variant="SUV",
        avg_cycle_time=45.0,
        cycle_time_deviation=3.0,
        torque_deviation=4.0,
        stations_exposed=8,
        degraded_station_count=2,
        cumulative_risk=0.35,
        quality_event_count=3,
        manual_observation_count=2,
    )

    assert feature.id is not None
    assert feature.vehicle == vehicle
    assert feature.variant == "SUV"

    fetched = feature_service.get_vehicle_feature(feature.id)

    assert fetched.id == feature.id
    assert fetched.vehicle == vehicle
    assert fetched.variant == "SUV"
    assert fetched.cumulative_risk == 0.35


@pytest.mark.django_db
def test_get_latest_vehicle_feature(
    feature_service,
    vehicle,
):
    first_time = timezone.now()
    second_time = first_time + timedelta(minutes=1)

    first = feature_service.save_vehicle_feature(
        timestamp=first_time,
        vehicle=vehicle,
        variant="SUV",
        cumulative_risk=0.2,
    )

    second = feature_service.save_vehicle_feature(
        timestamp=second_time,
        vehicle=vehicle,
        variant="SUV",
        cumulative_risk=0.5,
    )

    latest = feature_service.get_latest_vehicle_feature(
        vehicle.vehicle_id
    )

    assert latest.id == second.id
    assert latest.id != first.id
    assert latest.cumulative_risk == 0.5


@pytest.mark.django_db
def test_get_vehicle_features_range(
    feature_service,
    vehicle,
):
    first_time = timezone.now()
    second_time = first_time + timedelta(minutes=1)

    first = feature_service.save_vehicle_feature(
        timestamp=first_time,
        vehicle=vehicle,
        variant="SUV",
        cumulative_risk=0.2,
    )

    second = feature_service.save_vehicle_feature(
        timestamp=second_time,
        vehicle=vehicle,
        variant="SUV",
        cumulative_risk=0.4,
    )

    features = list(
        feature_service.get_vehicle_features(
            vehicle.vehicle_id,
            first_time,
            second_time,
        )
    )

    assert len(features) == 2
    assert [feature.id for feature in features] == [first.id, second.id]


@pytest.mark.django_db
def test_get_vehicle_features_latest_first(
    feature_service,
    vehicle,
):
    first_time = timezone.now()
    second_time = first_time + timedelta(minutes=1)

    first = feature_service.save_vehicle_feature(
        timestamp=first_time,
        vehicle=vehicle,
        variant="SUV",
        cumulative_risk=0.2,
    )

    second = feature_service.save_vehicle_feature(
        timestamp=second_time,
        vehicle=vehicle,
        variant="SUV",
        cumulative_risk=0.4,
    )

    features = list(
        feature_service.get_vehicle_features_latest_first(
            vehicle.vehicle_id,
            first_time,
            second_time,
        )
    )

    assert len(features) == 2
    assert [feature.id for feature in features] == [second.id, first.id]


# ================================================================
# NOT FOUND
# ================================================================


@pytest.mark.django_db
def test_get_missing_station_feature(
    feature_service,
):
    with pytest.raises(NotFoundError):
        feature_service.get_station_feature(999999)


@pytest.mark.django_db
def test_get_missing_vehicle_feature(
    feature_service,
):
    with pytest.raises(NotFoundError):
        feature_service.get_vehicle_feature(999999)


@pytest.mark.django_db
def test_get_missing_latest_station_feature(
    feature_service,
):
    with pytest.raises(NotFoundError):
        feature_service.get_latest_station_feature("NO-STATION")


@pytest.mark.django_db
def test_get_missing_latest_vehicle_feature(
    feature_service,
):
    with pytest.raises(NotFoundError):
        feature_service.get_latest_vehicle_feature("NO-VEHICLE")


# ================================================================
# VALIDATION
# ================================================================


@pytest.mark.django_db
def test_station_feature_requires_timestamp(
    feature_service,
    station,
):
    with pytest.raises(ValidationError, match="timestamp"):
        feature_service.save_station_feature(
            station=station,
        )


@pytest.mark.django_db
def test_station_feature_requires_station(
    feature_service,
):
    with pytest.raises(ValidationError, match="station"):
        feature_service.save_station_feature(
            timestamp=timezone.now(),
        )


@pytest.mark.django_db
def test_station_feature_rejects_negative_value(
    feature_service,
    station,
):
    with pytest.raises(ValidationError, match="utilization"):
        feature_service.save_station_feature(
            timestamp=timezone.now(),
            station=station,
            utilization=-1,
        )


@pytest.mark.django_db
def test_vehicle_feature_requires_timestamp(
    feature_service,
    vehicle,
):
    with pytest.raises(ValidationError, match="timestamp"):
        feature_service.save_vehicle_feature(
            vehicle=vehicle,
            variant="SUV",
        )


@pytest.mark.django_db
def test_vehicle_feature_requires_vehicle(
    feature_service,
):
    with pytest.raises(ValidationError, match="vehicle"):
        feature_service.save_vehicle_feature(
            timestamp=timezone.now(),
            variant="SUV",
        )


@pytest.mark.django_db
def test_vehicle_feature_requires_variant(
    feature_service,
    vehicle,
):
    with pytest.raises(ValidationError, match="variant"):
        feature_service.save_vehicle_feature(
            timestamp=timezone.now(),
            vehicle=vehicle,
        )


@pytest.mark.django_db
def test_vehicle_feature_rejects_negative_value(
    feature_service,
    vehicle,
):
    with pytest.raises(ValidationError, match="cumulative_risk"):
        feature_service.save_vehicle_feature(
            timestamp=timezone.now(),
            vehicle=vehicle,
            variant="SUV",
            cumulative_risk=-1,
        )


@pytest.mark.django_db
def test_station_feature_rejects_invalid_time_range(
    feature_service,
    station,
):
    start_time = timezone.now()
    end_time = start_time - timedelta(days=1)

    with pytest.raises(ValidationError, match="start_time cannot be later"):
        feature_service.get_station_features(
            station.station_id,
            start_time,
            end_time,
        )


@pytest.mark.django_db
def test_vehicle_feature_rejects_invalid_time_range(
    feature_service,
    vehicle,
):
    start_time = timezone.now()
    end_time = start_time - timedelta(days=1)

    with pytest.raises(ValidationError, match="start_time cannot be later"):
        feature_service.get_vehicle_features(
            vehicle.vehicle_id,
            start_time,
            end_time,
        )
