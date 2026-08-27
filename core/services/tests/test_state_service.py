import pytest

from core.services.exceptions import (
    NotFoundError,
    ValidationError,
)
from core.services.state.state_service import StateService


class FakeStateRepository:

    def __init__(self):
        self.calls = []

    # ------------------------------------------------------------
    # STATION STATE
    # ------------------------------------------------------------

    def get_station_state_by_id(self, state_id):
        self.calls.append(("get_station_state_by_id", state_id))
        return self.station_state

    def get_latest_station_state(self, station_id):
        self.calls.append(("get_latest_station_state", station_id))
        return self.station_state

    def get_station_state_history(
        self,
        station_id,
        start_time,
        end_time,
    ):
        self.calls.append(
            (
                "get_station_state_history",
                station_id,
                start_time,
                end_time,
            )
        )
        return self.station_states

    def get_station_state_history_latest_first(
        self,
        station_id,
        start_time,
        end_time,
    ):
        self.calls.append(
            (
                "get_station_state_history_latest_first",
                station_id,
                start_time,
                end_time,
            )
        )
        return self.station_states

    def get_by_health_state(self, health_state):
        self.calls.append(("get_by_health_state", health_state))
        return self.station_states

    def save_station_state(self, **data):
        self.calls.append(("save_station_state", data))
        return data

    def bulk_save_station_states(self, states):
        self.calls.append(("bulk_save_station_states", states))
        return states

    # ------------------------------------------------------------
    # VEHICLE STATE
    # ------------------------------------------------------------

    def get_vehicle_state_by_id(self, state_id):
        self.calls.append(("get_vehicle_state_by_id", state_id))
        return self.vehicle_state

    def get_latest_vehicle_state(self, vehicle_id):
        self.calls.append(("get_latest_vehicle_state", vehicle_id))
        return self.vehicle_state

    def get_vehicle_state_history(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self.calls.append(
            (
                "get_vehicle_state_history",
                vehicle_id,
                start_time,
                end_time,
            )
        )
        return self.vehicle_states

    def get_vehicle_state_history_latest_first(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self.calls.append(
            (
                "get_vehicle_state_history_latest_first",
                vehicle_id,
                start_time,
                end_time,
            )
        )
        return self.vehicle_states

    def get_vehicles_at_station(self, station_id):
        self.calls.append(("get_vehicles_at_station", station_id))
        return self.vehicle_states

    def get_by_status(self, status):
        self.calls.append(("get_by_status", status))
        return self.vehicle_states

    def save_vehicle_state(self, **data):
        self.calls.append(("save_vehicle_state", data))
        return data

    def bulk_save_vehicle_states(self, states):
        self.calls.append(("bulk_save_vehicle_states", states))
        return states


@pytest.fixture
def repository():
    repo = FakeStateRepository()
    repo.station_state = object()
    repo.vehicle_state = object()
    repo.station_states = [object(), object()]
    repo.vehicle_states = [object(), object()]
    return repo


@pytest.fixture
def service(repository):
    return StateService(state_repository=repository)


# ============================================================
# STATION STATE
# ============================================================


def test_get_station_state(service, repository):
    result = service.get_station_state(10)

    assert result is repository.station_state
    assert repository.calls == [("get_station_state_by_id", 10)]


def test_get_station_state_missing(repository):
    repository.station_state = None
    service = StateService(state_repository=repository)

    with pytest.raises(NotFoundError):
        service.get_station_state(999)


def test_get_latest_station_state(service, repository):
    result = service.get_latest_station_state("ST-001")

    assert result is repository.station_state
    assert repository.calls == [("get_latest_station_state", "ST-001")]


def test_get_latest_station_state_missing(repository):
    repository.station_state = None
    service = StateService(state_repository=repository)

    with pytest.raises(NotFoundError):
        service.get_latest_station_state("ST-001")


def test_get_station_states(service, repository):
    start_time = object()
    end_time = object()

    result = service.get_station_states("ST-001", start_time, end_time)

    assert result is repository.station_states
    assert repository.calls == [
        ("get_station_state_history", "ST-001", start_time, end_time)
    ]


def test_get_station_states_latest_first(service, repository):
    start_time = object()
    end_time = object()

    result = service.get_station_states_latest_first(
        "ST-001",
        start_time,
        end_time,
    )

    assert result is repository.station_states
    assert repository.calls == [
        (
            "get_station_state_history_latest_first",
            "ST-001",
            start_time,
            end_time,
        )
    ]


def test_get_station_states_by_health_state(service, repository):
    result = service.get_station_states_by_health_state("HEALTHY")

    assert result is repository.station_states
    assert repository.calls == [("get_by_health_state", "HEALTHY")]


def test_save_station_state(service, repository):
    state = {
        "timestamp": "2026-08-25T10:00:00Z",
        "station_id": "ST-001",
        "health_state": "HEALTHY",
        "health_risk": 0.2,
        "confidence": 0.9,
        "wip": 3,
        "utilization": 0.75,
    }

    result = service.save_station_state(**state)

    assert result == state
    assert repository.calls == [("save_station_state", state)]


def test_save_station_state_requires_timestamp(service, repository):
    with pytest.raises(ValidationError):
        service.save_station_state(
            station_id="ST-001",
            health_state="HEALTHY",
        )

    repository.calls == []


def test_save_station_state_requires_station(service, repository):
    with pytest.raises(ValidationError):
        service.save_station_state(
            timestamp="2026-08-25T10:00:00Z",
            health_state="HEALTHY",
        )

    assert repository.calls == []


def test_save_station_state_requires_health_state(service, repository):
    with pytest.raises(ValidationError):
        service.save_station_state(
            timestamp="2026-08-25T10:00:00Z",
            station_id="ST-001",
        )

    assert repository.calls == []


def test_bulk_save_station_states(service, repository):
    states = [
        {
            "timestamp": "2026-08-25T10:00:00Z",
            "station_id": "ST-001",
            "health_state": "HEALTHY",
            "health_risk": 0.2,
            "confidence": 0.9,
            "wip": 5,
        },
        {
            "timestamp": "2026-08-25T10:01:00Z",
            "station_id": "ST-001",
            "health_state": "WARNING",
            "health_risk": 0.4,
            "confidence": 0.8,
            "wip": 2,
        },
    ]

    result = service.bulk_save_station_states(states)

    assert result == states
    assert repository.calls == [("bulk_save_station_states", states)]


def test_bulk_save_station_states_rejects_empty_batch(service, repository):
    with pytest.raises(ValidationError):
        service.bulk_save_station_states([])

    assert repository.calls == []


def test_bulk_save_station_states_validates_each_state(service, repository):
    states = [
        {
            "timestamp": "2026-08-25T10:00:00Z",
            "station_id": "ST-001",
            "health_state": "HEALTHY",
        },
        {
            "timestamp": "2026-08-25T10:01:00Z",
            "station_id": "ST-001",
            "health_state": "",
        },
    ]

    with pytest.raises(ValidationError):
        service.bulk_save_station_states(states)

    assert repository.calls == []


# ============================================================
# VEHICLE STATE
# ============================================================


def test_get_vehicle_state(service, repository):
    result = service.get_vehicle_state(7)

    assert result is repository.vehicle_state
    assert repository.calls == [("get_vehicle_state_by_id", 7)]


def test_get_vehicle_state_missing(repository):
    repository.vehicle_state = None
    service = StateService(state_repository=repository)

    with pytest.raises(NotFoundError):
        service.get_vehicle_state(999)


def test_get_latest_vehicle_state(service, repository):
    result = service.get_latest_vehicle_state("VH-001")

    assert result is repository.vehicle_state
    assert repository.calls == [("get_latest_vehicle_state", "VH-001")]


def test_get_latest_vehicle_state_missing(repository):
    repository.vehicle_state = None
    service = StateService(state_repository=repository)

    with pytest.raises(NotFoundError):
        service.get_latest_vehicle_state("VH-001")


def test_get_vehicle_states(service, repository):
    start_time = object()
    end_time = object()

    result = service.get_vehicle_states("VH-001", start_time, end_time)

    assert result is repository.vehicle_states
    assert repository.calls == [
        ("get_vehicle_state_history", "VH-001", start_time, end_time)
    ]


def test_get_vehicle_states_latest_first(service, repository):
    start_time = object()
    end_time = object()

    result = service.get_vehicle_states_latest_first(
        "VH-001",
        start_time,
        end_time,
    )

    assert result is repository.vehicle_states
    assert repository.calls == [
        (
            "get_vehicle_state_history_latest_first",
            "VH-001",
            start_time,
            end_time,
        )
    ]


def test_get_vehicles_at_station(service, repository):
    result = service.get_vehicles_at_station("ST-001")

    assert result is repository.vehicle_states
    assert repository.calls == [("get_vehicles_at_station", "ST-001")]


def test_get_vehicle_states_by_status(service, repository):
    result = service.get_vehicle_states_by_status("IN_PROGRESS")

    assert result is repository.vehicle_states
    assert repository.calls == [("get_by_status", "IN_PROGRESS")]


def test_save_vehicle_state(service, repository):
    state = {
        "timestamp": "2026-08-25T10:00:00Z",
        "vehicle_id": "VH-001",
        "status": "IN_PROGRESS",
        "quality_risk": 0.3,
        "confidence": 0.7,
        "risk_source": "SENSOR",
    }

    result = service.save_vehicle_state(**state)

    assert result == state
    assert repository.calls == [("save_vehicle_state", state)]


def test_save_vehicle_state_requires_timestamp(service, repository):
    with pytest.raises(ValidationError):
        service.save_vehicle_state(
            vehicle_id="VH-001",
            status="IN_PROGRESS",
        )

    assert repository.calls == []


def test_save_vehicle_state_requires_vehicle(service, repository):
    with pytest.raises(ValidationError):
        service.save_vehicle_state(
            timestamp="2026-08-25T10:00:00Z",
            status="IN_PROGRESS",
        )

    assert repository.calls == []


def test_save_vehicle_state_requires_status(service, repository):
    with pytest.raises(ValidationError):
        service.save_vehicle_state(
            timestamp="2026-08-25T10:00:00Z",
            vehicle_id="VH-001",
        )

    assert repository.calls == []


def test_bulk_save_vehicle_states(service, repository):
    states = [
        {
            "timestamp": "2026-08-25T10:00:00Z",
            "vehicle_id": "VH-001",
            "status": "IN_PROGRESS",
            "quality_risk": 0.1,
            "confidence": 0.9,
        },
        {
            "timestamp": "2026-08-25T10:01:00Z",
            "vehicle_id": "VH-001",
            "status": "READY",
            "quality_risk": 0.2,
            "confidence": 0.8,
        },
    ]

    result = service.bulk_save_vehicle_states(states)

    assert result == states
    assert repository.calls == [("bulk_save_vehicle_states", states)]


def test_bulk_save_vehicle_states_rejects_empty_batch(service, repository):
    with pytest.raises(ValidationError):
        service.bulk_save_vehicle_states([])

    assert repository.calls == []


def test_bulk_save_vehicle_states_validates_each_state(service, repository):
    states = [
        {
            "timestamp": "2026-08-25T10:00:00Z",
            "vehicle_id": "VH-001",
            "status": "IN_PROGRESS",
        },
        {
            "timestamp": "2026-08-25T10:01:00Z",
            "vehicle_id": "VH-001",
            "status": "",
        },
    ]

    with pytest.raises(ValidationError):
        service.bulk_save_vehicle_states(states)

    assert repository.calls == []


# ============================================================
# COMMON VALIDATION
# ============================================================


def test_history_rejects_missing_time_range(service):
    with pytest.raises(ValidationError):
        service.get_station_states("ST-001", None, None)

    with pytest.raises(ValidationError):
        service.get_vehicle_states("VH-001", None, None)


def test_history_rejects_invalid_time_range(service):
    start = "2026-08-25T11:00:00Z"
    end = "2026-08-25T10:00:00Z"

    with pytest.raises(ValidationError):
        service.get_station_states("ST-001", start, end)

    with pytest.raises(ValidationError):
        service.get_vehicle_states("VH-001", start, end)
