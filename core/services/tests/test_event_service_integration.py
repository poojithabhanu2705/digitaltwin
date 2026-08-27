from datetime import timedelta

import pytest
from django.utils import timezone

from core.models import (
    Plant,
    ProductionLine,
    Station,
    Vehicle,
)

from core.repositories.event_repository import (
    ProductionEventRepository,
    VehicleStationHistoryRepository,
    ManualObservationRepository,
    QualityEventRepository,
    MaintenanceEventRepository,
)

from core.services.event.event_service import EventsService
from core.services.exceptions import NotFoundError, ValidationError


# ============================================================
# SERVICE FIXTURE
# ============================================================


@pytest.fixture
def events_service():
    return EventsService(
        production_event_repository=ProductionEventRepository,
        vehicle_station_history_repository=(
            VehicleStationHistoryRepository
        ),
        manual_observation_repository=(
            ManualObservationRepository
        ),
        quality_event_repository=QualityEventRepository,
        maintenance_event_repository=(
            MaintenanceEventRepository
        ),
    )


# ============================================================
# STATION FIXTURE
# ============================================================


@pytest.fixture
def station():
    plant = Plant.objects.create(
        plant_id="PL-EVENT-TEST",
        name="Event Test Plant",
        location="Test Location",
    )

    line = ProductionLine.objects.create(
        line_id="LINE-EVENT-TEST",
        plant=plant,
        name="Event Test Line",
    )

    return Station.objects.create(
        station_id="ST-EVENT-TEST",
        line=line,
        name="Event Test Station",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=10.0,
        position=1,
    )


# ============================================================
# VEHICLE FIXTURE
# ============================================================


@pytest.fixture
def vehicle(station):
    return Vehicle.objects.create(
        vehicle_id="EVENT-TEST-VH-001",
        line=station.line,
        variant="TEST-VARIANT",
        production_order="EVENT-TEST-ORDER-001",
        arrival_time=timezone.now(),
        status="IN_PROGRESS",
    )


# ============================================================
# PRODUCTION EVENT
# ============================================================


@pytest.mark.django_db
def test_create_and_get_production_event(
    events_service,
    station,
    vehicle,
):
    timestamp = timezone.now()

    event = events_service.create_production_event(
        timestamp=timestamp,
        vehicle=vehicle,
        station=station,
        event_type="PRODUCTION",
        cycle_time=10.5,
        quantity=1,
        status="COMPLETED",
    )

    assert event.event_id is not None
    assert event.vehicle == vehicle
    assert event.station == station

    fetched = events_service.get_production_event(
        event.event_id
    )

    assert fetched.event_id == event.event_id


@pytest.mark.django_db
def test_get_missing_production_event(
    events_service,
):
    with pytest.raises(NotFoundError):
        events_service.get_production_event(999999)


@pytest.mark.django_db
def test_get_station_production_events(
    events_service,
    station,
    vehicle,
):
    timestamp = timezone.now()

    events_service.create_production_event(
        timestamp=timestamp,
        vehicle=vehicle,
        station=station,
        event_type="PRODUCTION",
        quantity=1,
    )

    events = events_service.get_station_production_events(
        station.station_id,
        timestamp - timedelta(minutes=1),
        timestamp + timedelta(minutes=1),
    )

    assert events.count() == 1


# ============================================================
# VEHICLE-STATION HISTORY
# ============================================================


@pytest.mark.django_db
def test_create_and_get_vehicle_station_history(
    events_service,
    station,
    vehicle,
):
    entry_time = timezone.now()

    history = events_service.create_vehicle_station_history(
        vehicle=vehicle,
        station=station,
        entry_time=entry_time,
        sequence_number=1,
    )

    assert history.id is not None
    assert history.vehicle == vehicle
    assert history.station == station
    assert history.sequence_number == 1

    fetched = events_service.get_vehicle_station_history(
        history.id
    )

    assert fetched.id == history.id


@pytest.mark.django_db
def test_current_vehicle_visit(
    events_service,
    station,
    vehicle,
):
    entry_time = timezone.now()

    history = events_service.create_vehicle_station_history(
        vehicle=vehicle,
        station=station,
        entry_time=entry_time,
        sequence_number=1,
    )

    current = events_service.get_current_vehicle_visit(
        vehicle.vehicle_id
    )

    assert current.id == history.id
    assert current.vehicle == vehicle
    assert current.station == station
    assert current.exit_time is None


# ============================================================
# MANUAL OBSERVATION
# ============================================================


@pytest.mark.django_db
def test_create_and_get_manual_observation(
    events_service,
    station,
):
    timestamp = timezone.now()

    observation = events_service.create_manual_observation(
        timestamp=timestamp,
        station=station,
        check_type="VISUAL",
        parameter="SURFACE",
        status="PASS",
    )

    assert observation.observation_id is not None

    fetched = events_service.get_manual_observation(
        observation.observation_id
    )

    assert (
        fetched.observation_id
        == observation.observation_id
    )


# ============================================================
# QUALITY EVENT
# ============================================================


@pytest.mark.django_db
def test_create_and_get_quality_event(
    events_service,
    vehicle,
):
    timestamp = timezone.now()

    event = events_service.create_quality_event(
        timestamp=timestamp,
        vehicle=vehicle,
    )

    assert event.quality_event_id is not None

    fetched = events_service.get_quality_event(
        event.quality_event_id
    )

    assert (
        fetched.quality_event_id
        == event.quality_event_id
    )


# ============================================================
# MAINTENANCE EVENT
# ============================================================


@pytest.mark.django_db
def test_create_and_get_maintenance_event(
    events_service,
    station,
):
    timestamp = timezone.now()

    event = events_service.create_maintenance_event(
        timestamp=timestamp,
        station=station,
        maintenance_type="PREVENTIVE",
    )

    assert event.maintenance_id is not None

    fetched = events_service.get_maintenance_event(
        event.maintenance_id
    )

    assert (
        fetched.maintenance_id
        == event.maintenance_id
    )


# ============================================================
# VALIDATION
# ============================================================


@pytest.mark.django_db
def test_production_event_rejects_missing_vehicle(
    events_service,
    station,
):
    with pytest.raises(ValidationError):
        events_service.create_production_event(
            timestamp=timezone.now(),
            station=station,
            event_type="PRODUCTION",
        )


@pytest.mark.django_db
def test_vehicle_station_history_rejects_invalid_times(
    events_service,
    station,
    vehicle,
):
    entry_time = timezone.now()
    exit_time = entry_time - timedelta(hours=1)

    with pytest.raises(ValidationError):
        events_service.create_vehicle_station_history(
            vehicle=vehicle,
            station=station,
            entry_time=entry_time,
            exit_time=exit_time,
            sequence_number=1,
        )


@pytest.mark.django_db
def test_manual_observation_requires_check_type(
    events_service,
    station,
):
    with pytest.raises(ValidationError):
        events_service.create_manual_observation(
            timestamp=timezone.now(),
            station=station,
            parameter="SURFACE",
            status="PASS",
        )


@pytest.mark.django_db
def test_maintenance_event_requires_type(
    events_service,
    station,
):
    with pytest.raises(ValidationError):
        events_service.create_maintenance_event(
            timestamp=timezone.now(),
            station=station,
        )
        