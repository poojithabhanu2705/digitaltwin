from datetime import timedelta

import pytest
from django.utils import timezone

from core.models import (
    Plant,
    ProductionLine,
    Station,
    Vehicle,
)
from core.repositories.state_repository import StateRepository
from core.services.exceptions import NotFoundError, ValidationError
from core.services.state.state_service import StateService


@pytest.fixture
def state_service():
    return StateService(StateRepository)


@pytest.fixture
def station():
    plant = Plant.objects.create(
        plant_id="PL-STATE-TEST",
        name="State Test Plant",
        location="Test Location",
    )

    line = ProductionLine.objects.create(
        line_id="LINE-STATE-TEST",
        plant=plant,
        name="State Test Line",
    )

    return Station.objects.create(
        station_id="ST-STATE-TEST",
        line=line,
        name="State Test Station",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=10.0,
        position=1,
    )


@pytest.fixture
def vehicle(station):
    return Vehicle.objects.create(
        vehicle_id="STATE-TEST-VH-001",
        line=station.line,
        variant="TEST-VARIANT",
        production_order="STATE-TEST-ORDER-001",
        arrival_time=timezone.now(),
        status="IN_PROGRESS",
    )


@pytest.mark.django_db
def test_create_and_get_station_state(state_service, station):
    timestamp = timezone.now()

    state = state_service.save_station_state(
        timestamp=timestamp,
        station=station,
        health_state="HEALTHY",
        health_risk=0.15,
        confidence=0.9,
        wip=5,
        utilization=0.8,
        throughput=120.0,
        blocking_time=1.5,
        starvation_time=0.5,
        sensor_coverage=0.95,
        data_quality=0.98,
    )

    assert state.id is not None
    assert state.station == station
    assert state.health_state == "HEALTHY"

    fetched = state_service.get_station_state(state.id)
    assert fetched.id == state.id
    assert fetched.station == station


@pytest.mark.django_db
def test_get_latest_station_state(state_service, station):
    base_time = timezone.now()

    first = state_service.save_station_state(
        timestamp=base_time,
        station=station,
        health_state="HEALTHY",
        health_risk=0.1,
        confidence=0.8,
        wip=2,
    )

    second = state_service.save_station_state(
        timestamp=base_time + timedelta(minutes=1),
        station=station,
        health_state="WARNING",
        health_risk=0.3,
        confidence=0.7,
        wip=3,
    )

    latest = state_service.get_latest_station_state(station.station_id)
    assert latest.id == second.id
    assert latest.health_state == "WARNING"
    assert first.id != second.id


@pytest.mark.django_db
def test_get_station_state_history(state_service, station):
    base_time = timezone.now()

    first = state_service.save_station_state(
        timestamp=base_time,
        station=station,
        health_state="HEALTHY",
        health_risk=0.1,
        confidence=0.8,
        wip=1,
    )

    second = state_service.save_station_state(
        timestamp=base_time + timedelta(minutes=1),
        station=station,
        health_state="WARNING",
        health_risk=0.2,
        confidence=0.7,
        wip=2,
    )

    history = list(
        state_service.get_station_states(
            station.station_id,
            base_time,
            base_time + timedelta(minutes=2),
        )
    )

    assert len(history) == 2
    assert [record.id for record in history] == [first.id, second.id]


@pytest.mark.django_db
def test_create_and_get_vehicle_state(state_service, vehicle):
    timestamp = timezone.now()

    state = state_service.save_vehicle_state(
        timestamp=timestamp,
        vehicle=vehicle,
        status="IN_PROGRESS",
        quality_risk=0.2,
        confidence=0.9,
        risk_source="SENSOR",
    )

    assert state.id is not None
    assert state.vehicle == vehicle
    assert state.status == "IN_PROGRESS"

    fetched = state_service.get_vehicle_state(state.id)
    assert fetched.id == state.id
    assert fetched.vehicle == vehicle


@pytest.mark.django_db
def test_get_latest_vehicle_state(state_service, vehicle):
    base_time = timezone.now()

    first = state_service.save_vehicle_state(
        timestamp=base_time,
        vehicle=vehicle,
        status="IN_PROGRESS",
        quality_risk=0.1,
        confidence=0.8,
    )

    second = state_service.save_vehicle_state(
        timestamp=base_time + timedelta(minutes=1),
        vehicle=vehicle,
        status="READY",
        quality_risk=0.2,
        confidence=0.7,
    )

    latest = state_service.get_latest_vehicle_state(vehicle.vehicle_id)
    assert latest.id == second.id
    assert latest.status == "READY"
    assert first.id != second.id


@pytest.mark.django_db
def test_get_vehicle_state_history(state_service, vehicle):
    base_time = timezone.now()

    first = state_service.save_vehicle_state(
        timestamp=base_time,
        vehicle=vehicle,
        status="IN_PROGRESS",
        quality_risk=0.1,
        confidence=0.8,
    )

    second = state_service.save_vehicle_state(
        timestamp=base_time + timedelta(minutes=1),
        vehicle=vehicle,
        status="READY",
        quality_risk=0.2,
        confidence=0.7,
    )

    history = list(
        state_service.get_vehicle_states(
            vehicle.vehicle_id,
            base_time,
            base_time + timedelta(minutes=2),
        )
    )

    assert len(history) == 2
    assert [record.id for record in history] == [first.id, second.id]


@pytest.mark.django_db
def test_station_state_requires_timestamp(state_service, station):
    with pytest.raises(ValidationError):
        state_service.save_station_state(
            station=station,
            health_state="HEALTHY",
        )


@pytest.mark.django_db
def test_station_state_requires_station(state_service):
    with pytest.raises(ValidationError):
        state_service.save_station_state(
            timestamp=timezone.now(),
            health_state="HEALTHY",
        )


@pytest.mark.django_db
def test_station_state_requires_health_state(state_service, station):
    with pytest.raises(ValidationError):
        state_service.save_station_state(
            timestamp=timezone.now(),
            station=station,
        )


@pytest.mark.django_db
def test_vehicle_state_requires_status(state_service, vehicle):
    with pytest.raises(ValidationError):
        state_service.save_vehicle_state(
            timestamp=timezone.now(),
            vehicle=vehicle,
        )


@pytest.mark.django_db
def test_history_rejects_invalid_time_range(state_service, station, vehicle):
    start_time = timezone.now()
    end_time = start_time - timedelta(hours=1)

    with pytest.raises(ValidationError):
        state_service.get_station_states(
            station.station_id,
            start_time,
            end_time,
        )

    with pytest.raises(ValidationError):
        state_service.get_vehicle_states(
            vehicle.vehicle_id,
            start_time,
            end_time,
        )


@pytest.mark.django_db
def test_station_state_not_found(state_service):
    with pytest.raises(NotFoundError):
        state_service.get_station_state(999999)


@pytest.mark.django_db
def test_vehicle_state_not_found(state_service):
    with pytest.raises(NotFoundError):
        state_service.get_vehicle_state(999999)
