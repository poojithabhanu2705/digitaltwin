import pytest
from unittest.mock import MagicMock

from core.services.exceptions import NotFoundError, ValidationError
from core.services.telemetry.telemetry_service import TelemetryService


@pytest.fixture
def repository():
    return MagicMock()


@pytest.fixture
def service(repository):
    return TelemetryService(repository)


# ============================================================
# CREATE
# ============================================================


def test_create_telemetry(repository, service):
    telemetry = MagicMock()

    repository.create.return_value = telemetry

    result = service.create_telemetry(
        timestamp="2026-08-25T10:00:00Z",
        station_id="ST-001",
        cycle_time=12.5,
        temperature=65.0,
        vibration=2.1,
        throughput=10.0,
        alarm_count=0,
    )

    assert result == telemetry
    repository.create.assert_called_once()


def test_create_telemetry_requires_timestamp(repository, service):
    with pytest.raises(ValidationError):
        service.create_telemetry(
            station_id="ST-001",
            cycle_time=12.5,
        )

    repository.create.assert_not_called()


def test_create_telemetry_requires_station(repository, service):
    with pytest.raises(ValidationError):
        service.create_telemetry(
            timestamp="2026-08-25T10:00:00Z",
            cycle_time=12.5,
        )

    repository.create.assert_not_called()


@pytest.mark.parametrize(
    "field",
    [
        "cycle_time",
        "vibration",
        "throughput",
        "alarm_count",
    ],
)
def test_create_telemetry_rejects_negative_values(
    repository,
    service,
    field,
):
    data = {
        "timestamp": "2026-08-25T10:00:00Z",
        "station_id": "ST-001",
        field: -1,
    }

    with pytest.raises(ValidationError):
        service.create_telemetry(**data)

    repository.create.assert_not_called()


# ============================================================
# BULK CREATE
# ============================================================


def test_bulk_create_telemetry(repository, service):
    readings = [
        {
            "timestamp": "2026-08-25T10:00:00Z",
            "station_id": "ST-001",
            "cycle_time": 10.0,
        },
        {
            "timestamp": "2026-08-25T10:01:00Z",
            "station_id": "ST-001",
            "cycle_time": 11.0,
        },
    ]

    created = [MagicMock(), MagicMock()]

    repository.bulk_create.return_value = created

    result = service.bulk_create_telemetry(readings)

    assert result == created
    repository.bulk_create.assert_called_once_with(readings)


def test_bulk_create_rejects_empty_batch(repository, service):
    with pytest.raises(ValidationError):
        service.bulk_create_telemetry([])

    repository.bulk_create.assert_not_called()


def test_bulk_create_validates_each_reading(repository, service):
    readings = [
        {
            "timestamp": "2026-08-25T10:00:00Z",
            "station_id": "ST-001",
            "cycle_time": 10.0,
        },
        {
            "station_id": "ST-001",
            "cycle_time": 11.0,
        },
    ]

    with pytest.raises(ValidationError):
        service.bulk_create_telemetry(readings)

    repository.bulk_create.assert_not_called()


# ============================================================
# GET BY ID
# ============================================================


def test_get_telemetry(repository, service):
    telemetry = MagicMock()

    repository.get_by_id.return_value = telemetry

    result = service.get_telemetry(1)

    assert result == telemetry
    repository.get_by_id.assert_called_once_with(1)


def test_get_telemetry_raises_not_found(repository, service):
    repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_telemetry(999)

    repository.get_by_id.assert_called_once_with(999)


# ============================================================
# LATEST TELEMETRY
# ============================================================


@pytest.mark.parametrize(
    "method_name, repository_method, entity_id",
    [
        (
            "get_latest_for_station",
            "get_latest_for_station",
            "ST-001",
        ),
        (
            "get_latest_for_vehicle",
            "get_latest_for_vehicle",
            "VH-001",
        ),
        (
            "get_latest_for_equipment",
            "get_latest_for_equipment",
            "EQ-001",
        ),
        (
            "get_latest_for_sensor",
            "get_latest_for_sensor",
            "SN-001",
        ),
        (
            "get_latest_for_data_source",
            "get_latest_for_data_source",
            "SRC-001",
        ),
    ],
)
def test_get_latest(
    repository,
    service,
    method_name,
    repository_method,
    entity_id,
):
    telemetry = MagicMock()

    getattr(repository, repository_method).return_value = telemetry

    result = getattr(service, method_name)(entity_id)

    assert result == telemetry
    getattr(repository, repository_method).assert_called_once_with(
        entity_id
    )


@pytest.mark.parametrize(
    "method_name, repository_method, entity_id",
    [
        (
            "get_latest_for_station",
            "get_latest_for_station",
            "ST-001",
        ),
        (
            "get_latest_for_vehicle",
            "get_latest_for_vehicle",
            "VH-001",
        ),
        (
            "get_latest_for_equipment",
            "get_latest_for_equipment",
            "EQ-001",
        ),
        (
            "get_latest_for_sensor",
            "get_latest_for_sensor",
            "SN-001",
        ),
        (
            "get_latest_for_data_source",
            "get_latest_for_data_source",
            "SRC-001",
        ),
    ],
)
def test_get_latest_raises_not_found(
    repository,
    service,
    method_name,
    repository_method,
    entity_id,
):
    getattr(repository, repository_method).return_value = None

    with pytest.raises(NotFoundError):
        getattr(service, method_name)(entity_id)


# ============================================================
# HISTORY
# ============================================================


@pytest.mark.parametrize(
    "method_name, repository_method, entity_id",
    [
        (
            "get_station_history",
            "get_station_history",
            "ST-001",
        ),
        (
            "get_vehicle_history",
            "get_vehicle_history",
            "VH-001",
        ),
        (
            "get_equipment_history",
            "get_equipment_history",
            "EQ-001",
        ),
        (
            "get_sensor_history",
            "get_sensor_history",
            "SN-001",
        ),
        (
            "get_data_source_history",
            "get_data_source_history",
            "SRC-001",
        ),
    ],
)
def test_get_history(
    repository,
    service,
    method_name,
    repository_method,
    entity_id,
):
    history = [MagicMock(), MagicMock()]

    repository_method_mock = getattr(repository, repository_method)
    repository_method_mock.return_value = history

    start_time = "2026-08-25T10:00:00Z"
    end_time = "2026-08-25T11:00:00Z"

    result = getattr(service, method_name)(
        entity_id,
        start_time,
        end_time,
    )

    assert result == history

    repository_method_mock.assert_called_once_with(
        entity_id,
        start_time,
        end_time,
    )


def test_history_rejects_invalid_time_range(repository, service):
    with pytest.raises(ValidationError):
        service.get_station_history(
            "ST-001",
            "2026-08-25T12:00:00Z",
            "2026-08-25T10:00:00Z",
        )

    repository.get_station_history.assert_not_called()