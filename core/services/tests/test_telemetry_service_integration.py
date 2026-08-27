import pytest
from django.utils import timezone

from core.models import (
    Plant,
    ProductionLine,
    Station,
    Telemetry,
)
from core.repositories.telemetry_repository import TelemetryRepository
from core.services.exceptions import NotFoundError, ValidationError
from core.services.telemetry.telemetry_service import TelemetryService


@pytest.fixture
def telemetry_service():
    return TelemetryService(TelemetryRepository)


@pytest.fixture
def station():
    plant = Plant.objects.create(
        plant_id="PL-TEST",
        name="Test Plant",
        location="Test Location",
    )

    line = ProductionLine.objects.create(
        line_id="LINE-TEST",
        plant=plant,
        name="Test Line",
    )

    return Station.objects.create(
        station_id="ST-TEST",
        line=line,
        name="Test Station",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=10.0,
        position=1,
    )


# ============================================================
# CREATE + GET
# ============================================================


@pytest.mark.django_db
def test_create_and_get_telemetry(
    telemetry_service,
    station,
):
    timestamp = timezone.now()

    telemetry = telemetry_service.create_telemetry(
        timestamp=timestamp,
        station=station,
        cycle_time=12.5,
        torque=25.0,
        temperature=65.0,
        vibration=2.5,
        throughput=10.0,
        machine_state="RUNNING",
        alarm_count=0,
        data_quality="VALID",
        is_imputed=False,
    )

    assert telemetry.telemetry_id is not None
    assert telemetry.station == station
    assert telemetry.cycle_time == 12.5

    fetched = telemetry_service.get_telemetry(
        telemetry.telemetry_id
    )

    assert fetched.telemetry_id == telemetry.telemetry_id
    assert fetched.station.station_id == station.station_id


# ============================================================
# NOT FOUND
# ============================================================


@pytest.mark.django_db
def test_get_missing_telemetry_raises_not_found(
    telemetry_service,
):
    with pytest.raises(NotFoundError):
        telemetry_service.get_telemetry(999999)


# ============================================================
# LATEST
# ============================================================


@pytest.mark.django_db
def test_get_latest_for_station(
    telemetry_service,
    station,
):
    first_timestamp = timezone.now()

    first = telemetry_service.create_telemetry(
        timestamp=first_timestamp,
        station=station,
        cycle_time=10.0,
    )

    second = telemetry_service.create_telemetry(
        timestamp=first_timestamp + timezone.timedelta(seconds=10),
        station=station,
        cycle_time=20.0,
    )

    latest = telemetry_service.get_latest_for_station(
        station.station_id
    )

    assert latest.telemetry_id == second.telemetry_id
    assert latest.cycle_time == 20.0


# ============================================================
# HISTORY
# ============================================================


@pytest.mark.django_db
def test_get_station_history(
    telemetry_service,
    station,
):
    base_time = timezone.now()

    telemetry_service.create_telemetry(
        timestamp=base_time,
        station=station,
        cycle_time=10.0,
    )

    telemetry_service.create_telemetry(
        timestamp=base_time + timezone.timedelta(minutes=1),
        station=station,
        cycle_time=20.0,
    )

    history = telemetry_service.get_station_history(
        station.station_id,
        base_time,
        base_time + timezone.timedelta(minutes=1),
    )

    assert history.count() == 2

    values = list(
        history.values_list("cycle_time", flat=True)
    )

    assert values == [10.0, 20.0]


# ============================================================
# VALIDATION
# ============================================================


@pytest.mark.django_db
def test_create_requires_timestamp(
    telemetry_service,
    station,
):
    with pytest.raises(ValidationError):
        telemetry_service.create_telemetry(
            station=station,
            cycle_time=10.0,
        )


@pytest.mark.django_db
def test_create_requires_station(
    telemetry_service,
):
    with pytest.raises(ValidationError):
        telemetry_service.create_telemetry(
            timestamp=timezone.now(),
            cycle_time=10.0,
        )


@pytest.mark.django_db
def test_create_rejects_negative_cycle_time(
    telemetry_service,
    station,
):
    with pytest.raises(ValidationError):
        telemetry_service.create_telemetry(
            timestamp=timezone.now(),
            station=station,
            cycle_time=-1.0,
        )


@pytest.mark.django_db
def test_history_rejects_invalid_time_range(
    telemetry_service,
    station,
):
    start_time = timezone.now()
    end_time = start_time - timezone.timedelta(hours=1)

    with pytest.raises(ValidationError):
        telemetry_service.get_station_history(
            station.station_id,
            start_time,
            end_time,
        )