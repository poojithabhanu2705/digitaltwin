import pytest
from unittest.mock import MagicMock

from core.services.event.event_service import EventsService
from core.services.exceptions import NotFoundError, ValidationError


@pytest.fixture
def repositories():
    return {
        "production": MagicMock(),
        "history": MagicMock(),
        "manual": MagicMock(),
        "quality": MagicMock(),
        "maintenance": MagicMock(),
    }


@pytest.fixture
def service(repositories):
    return EventsService(
        production_event_repository=repositories["production"],
        vehicle_station_history_repository=repositories["history"],
        manual_observation_repository=repositories["manual"],
        quality_event_repository=repositories["quality"],
        maintenance_event_repository=repositories["maintenance"],
    )


# ============================================================
# PRODUCTION EVENTS
# ============================================================


def test_get_production_event(repositories, service):
    event = MagicMock()
    repositories["production"].get_by_id.return_value = event

    result = service.get_production_event(1)

    assert result == event
    repositories["production"].get_by_id.assert_called_once_with(1)


def test_get_production_event_not_found(repositories, service):
    repositories["production"].get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_production_event(999)

    repositories["production"].get_by_id.assert_called_once_with(999)


def test_create_production_event(repositories, service):
    event = MagicMock()
    repositories["production"].create.return_value = event

    result = service.create_production_event(
        timestamp="2026-08-25T10:00:00Z",
        vehicle_id="VH-001",
        station_id="ST-001",
        event_type="PRODUCTION",
        quantity=1,
        cycle_time=10.5,
    )

    assert result == event
    repositories["production"].create.assert_called_once()


def test_create_production_event_requires_timestamp(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_production_event(
            vehicle_id="VH-001",
            station_id="ST-001",
            event_type="PRODUCTION",
        )

    repositories["production"].create.assert_not_called()


def test_create_production_event_requires_vehicle(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_production_event(
            timestamp="2026-08-25T10:00:00Z",
            station_id="ST-001",
            event_type="PRODUCTION",
        )

    repositories["production"].create.assert_not_called()


def test_create_production_event_requires_station(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_production_event(
            timestamp="2026-08-25T10:00:00Z",
            vehicle_id="VH-001",
            event_type="PRODUCTION",
        )

    repositories["production"].create.assert_not_called()


def test_create_production_event_requires_event_type(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_production_event(
            timestamp="2026-08-25T10:00:00Z",
            vehicle_id="VH-001",
            station_id="ST-001",
        )

    repositories["production"].create.assert_not_called()


def test_create_production_event_rejects_invalid_quantity(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_production_event(
            timestamp="2026-08-25T10:00:00Z",
            vehicle_id="VH-001",
            station_id="ST-001",
            event_type="PRODUCTION",
            quantity=0,
        )

    repositories["production"].create.assert_not_called()


def test_create_production_event_rejects_negative_cycle_time(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_production_event(
            timestamp="2026-08-25T10:00:00Z",
            vehicle_id="VH-001",
            station_id="ST-001",
            event_type="PRODUCTION",
            cycle_time=-1,
        )

    repositories["production"].create.assert_not_called()


@pytest.mark.parametrize(
    "method_name, repository_method, entity_id",
    [
        (
            "get_station_production_events",
            "get_station_events",
            "ST-001",
        ),
        (
            "get_vehicle_production_events",
            "get_vehicle_events",
            "VH-001",
        ),
    ],
)
def test_production_event_range_queries(
    repositories,
    service,
    method_name,
    repository_method,
    entity_id,
):
    result_data = [MagicMock()]

    getattr(
        repositories["production"],
        repository_method,
    ).return_value = result_data

    start = "2026-08-25T10:00:00Z"
    end = "2026-08-25T11:00:00Z"

    result = getattr(service, method_name)(
        entity_id,
        start,
        end,
    )

    assert result == result_data

    getattr(
        repositories["production"],
        repository_method,
    ).assert_called_once_with(
        entity_id,
        start,
        end,
    )


def test_get_production_events_by_type(
    repositories,
    service,
):
    events = [MagicMock()]

    repositories["production"].get_by_event_type.return_value = events

    result = service.get_production_events_by_type(
        "PRODUCTION"
    )

    assert result == events


def test_get_latest_production_event_for_station(
    repositories,
    service,
):
    event = MagicMock()

    repositories[
        "production"
    ].get_latest_for_station.return_value = event

    result = service.get_latest_production_event_for_station(
        "ST-001"
    )

    assert result == event


def test_get_latest_production_event_for_vehicle_not_found(
    repositories,
    service,
):
    repositories[
        "production"
    ].get_latest_for_vehicle.return_value = None

    with pytest.raises(NotFoundError):
        service.get_latest_production_event_for_vehicle(
            "VH-001"
        )


# ============================================================
# VEHICLE-STATION HISTORY
# ============================================================


def test_get_vehicle_station_history(
    repositories,
    service,
):
    history = MagicMock()

    repositories["history"].get_by_id.return_value = history

    result = service.get_vehicle_station_history(1)

    assert result == history
    repositories["history"].get_by_id.assert_called_once_with(1)


def test_get_vehicle_station_history_not_found(
    repositories,
    service,
):
    repositories["history"].get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_vehicle_station_history(999)


def test_get_vehicle_history(
    repositories,
    service,
):
    history = [MagicMock()]
    repositories["history"].get_vehicle_history.return_value = history

    result = service.get_vehicle_history("VH-001")

    assert result == history


def test_get_station_vehicle_history(
    repositories,
    service,
):
    history = [MagicMock()]
    repositories["history"].get_station_history.return_value = history

    result = service.get_station_vehicle_history("ST-001")

    assert result == history


def test_get_current_vehicle_visit(
    repositories,
    service,
):
    history = MagicMock()
    repositories["history"].get_current_visit.return_value = history

    result = service.get_current_vehicle_visit("VH-001")

    assert result == history


def test_get_current_vehicle_visit_not_found(
    repositories,
    service,
):
    repositories["history"].get_current_visit.return_value = None

    with pytest.raises(NotFoundError):
        service.get_current_vehicle_visit("VH-001")


def test_create_vehicle_station_history(
    repositories,
    service,
):
    history = MagicMock()
    repositories["history"].create.return_value = history

    result = service.create_vehicle_station_history(
        vehicle_id="VH-001",
        station_id="ST-001",
        entry_time="2026-08-25T10:00:00Z",
    )

    assert result == history
    repositories["history"].create.assert_called_once()


def test_create_vehicle_station_history_requires_vehicle(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_vehicle_station_history(
            station_id="ST-001",
            entry_time="2026-08-25T10:00:00Z",
        )

    repositories["history"].create.assert_not_called()


def test_create_vehicle_station_history_requires_station(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_vehicle_station_history(
            vehicle_id="VH-001",
            entry_time="2026-08-25T10:00:00Z",
        )

    repositories["history"].create.assert_not_called()


def test_create_vehicle_station_history_rejects_invalid_exit_time(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_vehicle_station_history(
            vehicle_id="VH-001",
            station_id="ST-001",
            entry_time="2026-08-25T12:00:00Z",
            exit_time="2026-08-25T11:00:00Z",
        )

    repositories["history"].create.assert_not_called()


def test_update_vehicle_station_exit_time(
    repositories,
    service,
):
    history = MagicMock()
    history.entry_time = "2026-08-25T10:00:00Z"

    repositories["history"].update_exit_time.return_value = history

    result = service.update_vehicle_station_exit_time(
        1,
        "2026-08-25T11:00:00Z",
    )

    assert result == history


# ============================================================
# MANUAL OBSERVATIONS
# ============================================================


def test_get_manual_observation(
    repositories,
    service,
):
    observation = MagicMock()

    repositories["manual"].get_by_id.return_value = observation

    result = service.get_manual_observation(1)

    assert result == observation


def test_get_manual_observation_not_found(
    repositories,
    service,
):
    repositories["manual"].get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_manual_observation(999)


@pytest.mark.parametrize(
    "method_name, repository_method, value",
    [
        (
            "get_manual_observations_for_station",
            "get_by_station",
            "ST-001",
        ),
        (
            "get_manual_observations_for_vehicle",
            "get_by_vehicle",
            "VH-001",
        ),
        (
            "get_manual_observations_by_check_type",
            "get_by_check_type",
            "VISUAL",
        ),
    ],
)
def test_manual_observation_queries(
    repositories,
    service,
    method_name,
    repository_method,
    value,
):
    result_data = [MagicMock()]

    getattr(
        repositories["manual"],
        repository_method,
    ).return_value = result_data

    result = getattr(service, method_name)(value)

    assert result == result_data


def test_get_manual_observations_by_time_range(
    repositories,
    service,
):
    observations = [MagicMock()]

    repositories["manual"].get_by_time_range.return_value = observations

    start = "2026-08-25T10:00:00Z"
    end = "2026-08-25T11:00:00Z"

    result = service.get_manual_observations_by_time_range(
        start,
        end,
    )

    assert result == observations


def test_create_manual_observation(
    repositories,
    service,
):
    observation = MagicMock()

    repositories["manual"].create.return_value = observation

    result = service.create_manual_observation(
        timestamp="2026-08-25T10:00:00Z",
        station_id="ST-001",
        check_type="VISUAL",
        parameter="SURFACE",
        status="PASS",
    )

    assert result == observation


def test_create_manual_observation_requires_station(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_manual_observation(
            timestamp="2026-08-25T10:00:00Z",
            check_type="VISUAL",
            parameter="SURFACE",
            status="PASS",
        )

    repositories["manual"].create.assert_not_called()


# ============================================================
# QUALITY EVENTS
# ============================================================


def test_get_quality_event(
    repositories,
    service,
):
    event = MagicMock()

    repositories["quality"].get_by_id.return_value = event

    result = service.get_quality_event(1)

    assert result == event


def test_get_quality_event_not_found(
    repositories,
    service,
):
    repositories["quality"].get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_quality_event(999)


@pytest.mark.parametrize(
    "method_name, repository_method, value",
    [
        (
            "get_quality_events_for_vehicle",
            "get_vehicle_events",
            "VH-001",
        ),
        (
            "get_quality_events_for_station",
            "get_station_events",
            "ST-001",
        ),
        (
            "get_quality_events_for_origin_station",
            "get_origin_station_events",
            "ST-001",
        ),
        (
            "get_quality_events_for_detection_station",
            "get_detection_station_events",
            "ST-002",
        ),
    ],
)
def test_quality_event_queries(
    repositories,
    service,
    method_name,
    repository_method,
    value,
):
    events = [MagicMock()]

    getattr(
        repositories["quality"],
        repository_method,
    ).return_value = events

    result = getattr(service, method_name)(value)

    assert result == events


def test_get_quality_defects(
    repositories,
    service,
):
    defects = [MagicMock()]

    repositories["quality"].get_defects.return_value = defects

    result = service.get_quality_defects("VH-001")

    assert result == defects
    repositories["quality"].get_defects.assert_called_once_with(
        "VH-001"
    )


def test_get_quality_events_by_defect_type(
    repositories,
    service,
):
    events = [MagicMock()]

    repositories[
        "quality"
    ].get_by_defect_type.return_value = events

    result = service.get_quality_events_by_defect_type(
        "SCRATCH"
    )

    assert result == events


def test_get_quality_events_by_time_range(
    repositories,
    service,
):
    events = [MagicMock()]

    repositories["quality"].get_by_time_range.return_value = events

    result = service.get_quality_events_by_time_range(
        "2026-08-25T10:00:00Z",
        "2026-08-25T11:00:00Z",
    )

    assert result == events


def test_create_quality_event(
    repositories,
    service,
):
    event = MagicMock()

    repositories["quality"].create.return_value = event

    result = service.create_quality_event(
        timestamp="2026-08-25T10:00:00Z",
        vehicle_id="VH-001",
    )

    assert result == event


def test_create_quality_event_requires_vehicle(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_quality_event(
            timestamp="2026-08-25T10:00:00Z",
        )

    repositories["quality"].create.assert_not_called()


# ============================================================
# MAINTENANCE EVENTS
# ============================================================


def test_get_maintenance_event(
    repositories,
    service,
):
    event = MagicMock()

    repositories["maintenance"].get_by_id.return_value = event

    result = service.get_maintenance_event(1)

    assert result == event


def test_get_maintenance_event_not_found(
    repositories,
    service,
):
    repositories["maintenance"].get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_maintenance_event(999)


@pytest.mark.parametrize(
    "method_name, repository_method, value",
    [
        (
            "get_maintenance_events_for_station",
            "get_station_events",
            "ST-001",
        ),
        (
            "get_maintenance_events_for_equipment",
            "get_equipment_events",
            "EQ-001",
        ),
    ],
)
def test_maintenance_event_queries(
    repositories,
    service,
    method_name,
    repository_method,
    value,
):
    events = [MagicMock()]

    getattr(
        repositories["maintenance"],
        repository_method,
    ).return_value = events

    result = getattr(service, method_name)(value)

    assert result == events


def test_get_maintenance_failures(
    repositories,
    service,
):
    failures = [MagicMock()]

    repositories["maintenance"].get_failures.return_value = failures

    result = service.get_maintenance_failures("ST-001")

    assert result == failures


def test_get_maintenance_events_by_type(
    repositories,
    service,
):
    events = [MagicMock()]

    repositories[
        "maintenance"
    ].get_by_maintenance_type.return_value = events

    result = service.get_maintenance_events_by_type(
        "PREVENTIVE"
    )

    assert result == events


def test_get_maintenance_events_by_time_range(
    repositories,
    service,
):
    events = [MagicMock()]

    repositories["maintenance"].get_by_time_range.return_value = events

    result = service.get_maintenance_events_by_time_range(
        "2026-08-25T10:00:00Z",
        "2026-08-25T11:00:00Z",
    )

    assert result == events


def test_create_maintenance_event(
    repositories,
    service,
):
    event = MagicMock()

    repositories["maintenance"].create.return_value = event

    result = service.create_maintenance_event(
        timestamp="2026-08-25T10:00:00Z",
        station_id="ST-001",
        maintenance_type="PREVENTIVE",
    )

    assert result == event


def test_create_maintenance_event_requires_station(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.create_maintenance_event(
            timestamp="2026-08-25T10:00:00Z",
            maintenance_type="PREVENTIVE",
        )

    repositories["maintenance"].create.assert_not_called()


# ============================================================
# COMMON TIME VALIDATION
# ============================================================


@pytest.mark.parametrize(
    "method_name",
    [
        "get_station_production_events",
        "get_vehicle_production_events",
    ],
)
def test_production_history_rejects_invalid_time_range(
    repositories,
    service,
    method_name,
):
    with pytest.raises(ValidationError):
        getattr(service, method_name)(
            "ID-001",
            "2026-08-25T12:00:00Z",
            "2026-08-25T10:00:00Z",
        )


def test_manual_history_rejects_invalid_time_range(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.get_manual_observations_by_time_range(
            "2026-08-25T12:00:00Z",
            "2026-08-25T10:00:00Z",
        )


def test_quality_history_rejects_invalid_time_range(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.get_quality_events_by_time_range(
            "2026-08-25T12:00:00Z",
            "2026-08-25T10:00:00Z",
        )


def test_maintenance_history_rejects_invalid_time_range(
    repositories,
    service,
):
    with pytest.raises(ValidationError):
        service.get_maintenance_events_by_time_range(
            "2026-08-25T12:00:00Z",
            "2026-08-25T10:00:00Z",
        )