import pytest
from unittest.mock import Mock

from core.services.exceptions import NotFoundError, ValidationError
from core.services.twin.twin_service import TwinService


@pytest.fixture
def mock_services():
    production_structure = Mock()
    telemetry = Mock()
    feature = Mock()
    state = Mock()

    return {
        "production_structure": production_structure,
        "telemetry": telemetry,
        "feature": feature,
        "state": state,
    }


@pytest.fixture
def twin_service(mock_services):
    return TwinService(
        production_structure_service=mock_services["production_structure"],
        telemetry_service=mock_services["telemetry"],
        feature_service=mock_services["feature"],
        state_service=mock_services["state"],
    )


# ============================================================
# STATION TWIN
# ============================================================


def test_get_station_twin_returns_composite_snapshot(
    twin_service,
    mock_services,
):
    station = Mock(station_id="ST-101")
    state = Mock()
    feature = Mock()
    telemetry = Mock()

    mock_services["production_structure"].get_station.return_value = station
    mock_services["state"].get_latest_station_state.return_value = state
    mock_services["feature"].get_latest_station_feature.return_value = feature
    mock_services["telemetry"].get_latest_for_station.return_value = telemetry

    result = twin_service.get_station_twin("ST-101")

    assert result == {
        "station": station,
        "state": state,
        "features": feature,
        "telemetry": telemetry,
    }

    mock_services["production_structure"].get_station.assert_called_once_with(
        "ST-101"
    )
    mock_services["state"].get_latest_station_state.assert_called_once_with(
        "ST-101"
    )
    mock_services["feature"].get_latest_station_feature.assert_called_once_with(
        "ST-101"
    )
    mock_services["telemetry"].get_latest_for_station.assert_called_once_with(
        "ST-101"
    )


def test_get_station_twin_allows_missing_current_data(
    twin_service,
    mock_services,
):
    station = Mock(station_id="ST-101")

    mock_services["production_structure"].get_station.return_value = station

    mock_services["state"].get_latest_station_state.side_effect = (
        NotFoundError("No state")
    )

    mock_services["feature"].get_latest_station_feature.side_effect = (
        NotFoundError("No feature")
    )

    mock_services["telemetry"].get_latest_for_station.side_effect = (
        NotFoundError("No telemetry")
    )

    result = twin_service.get_station_twin("ST-101")

    assert result["station"] == station
    assert result["state"] is None
    assert result["features"] is None
    assert result["telemetry"] is None


def test_get_station_twin_requires_station_id(
    twin_service,
):
    with pytest.raises(ValidationError):
        twin_service.get_station_twin(None)


def test_get_station_twin_propagates_missing_station(
    twin_service,
    mock_services,
):
    mock_services["production_structure"].get_station.side_effect = (
        NotFoundError("Station not found")
    )

    with pytest.raises(NotFoundError):
        twin_service.get_station_twin("ST-404")


# ============================================================
# VEHICLE TWIN
# ============================================================


def test_get_vehicle_twin_returns_composite_snapshot(
    twin_service,
    mock_services,
):
    state = Mock()
    feature = Mock()
    telemetry = Mock()

    mock_services["state"].get_latest_vehicle_state.return_value = state
    mock_services["feature"].get_latest_vehicle_feature.return_value = feature
    mock_services["telemetry"].get_latest_for_vehicle.return_value = telemetry

    result = twin_service.get_vehicle_twin("VH-101")

    assert result == {
        "vehicle_id": "VH-101",
        "state": state,
        "features": feature,
        "telemetry": telemetry,
    }

    mock_services["state"].get_latest_vehicle_state.assert_called_once_with(
        "VH-101"
    )
    mock_services["feature"].get_latest_vehicle_feature.assert_called_once_with(
        "VH-101"
    )
    mock_services["telemetry"].get_latest_for_vehicle.assert_called_once_with(
        "VH-101"
    )


def test_get_vehicle_twin_requires_vehicle_id(
    twin_service,
):
    with pytest.raises(ValidationError):
        twin_service.get_vehicle_twin(None)


def test_get_vehicle_twin_raises_when_no_data_exists(
    twin_service,
    mock_services,
):
    mock_services["state"].get_latest_vehicle_state.side_effect = (
        NotFoundError("No state")
    )

    mock_services["feature"].get_latest_vehicle_feature.side_effect = (
        NotFoundError("No feature")
    )

    mock_services["telemetry"].get_latest_for_vehicle.side_effect = (
        NotFoundError("No telemetry")
    )

    with pytest.raises(NotFoundError):
        twin_service.get_vehicle_twin("VH-404")


def test_get_vehicle_twin_allows_partial_data(
    twin_service,
    mock_services,
):
    state = Mock()

    mock_services["state"].get_latest_vehicle_state.return_value = state

    mock_services["feature"].get_latest_vehicle_feature.side_effect = (
        NotFoundError("No feature")
    )

    mock_services["telemetry"].get_latest_for_vehicle.side_effect = (
        NotFoundError("No telemetry")
    )

    result = twin_service.get_vehicle_twin("VH-101")

    assert result["vehicle_id"] == "VH-101"
    assert result["state"] == state
    assert result["features"] is None
    assert result["telemetry"] is None


# ============================================================
# STATION → VEHICLES
# ============================================================


def test_get_station_vehicles_returns_current_vehicles(
    twin_service,
    mock_services,
):
    station = Mock(station_id="ST-101")
    vehicles = [
        Mock(vehicle_id="VH-101"),
        Mock(vehicle_id="VH-102"),
    ]

    mock_services["production_structure"].get_station.return_value = station
    mock_services["state"].get_vehicles_at_station.return_value = vehicles

    result = twin_service.get_station_vehicles("ST-101")

    assert result == vehicles

    mock_services["production_structure"].get_station.assert_called_once_with(
        "ST-101"
    )

    mock_services["state"].get_vehicles_at_station.assert_called_once_with(
        "ST-101"
    )


def test_get_station_vehicles_requires_station_id(
    twin_service,
):
    with pytest.raises(ValidationError):
        twin_service.get_station_vehicles(None)


def test_get_station_vehicles_validates_station_exists(
    twin_service,
    mock_services,
):
    mock_services["production_structure"].get_station.side_effect = (
        NotFoundError("Station not found")
    )

    with pytest.raises(NotFoundError):
        twin_service.get_station_vehicles("ST-404")

    mock_services["state"].get_vehicles_at_station.assert_not_called()


# ============================================================
# COMPLETE STATION TWIN
# ============================================================


def test_get_station_twin_with_vehicles(
    twin_service,
    mock_services,
):
    station = Mock(station_id="ST-101")

    vehicle_1 = Mock(vehicle_id="VH-101")
    vehicle_2 = Mock(vehicle_id="VH-102")

    station_state = Mock()
    station_feature = Mock()
    station_telemetry = Mock()

    vehicle_state_1 = Mock()
    vehicle_feature_1 = Mock()
    vehicle_telemetry_1 = Mock()

    vehicle_state_2 = Mock()
    vehicle_feature_2 = Mock()
    vehicle_telemetry_2 = Mock()

    mock_services["production_structure"].get_station.return_value = station

    mock_services["state"].get_latest_station_state.return_value = station_state
    mock_services["feature"].get_latest_station_feature.return_value = (
        station_feature
    )
    mock_services["telemetry"].get_latest_for_station.return_value = (
        station_telemetry
    )

    mock_services["state"].get_vehicles_at_station.return_value = [
        vehicle_1,
        vehicle_2,
    ]

    mock_services["state"].get_latest_vehicle_state.side_effect = [
        vehicle_state_1,
        vehicle_state_2,
    ]

    mock_services["feature"].get_latest_vehicle_feature.side_effect = [
        vehicle_feature_1,
        vehicle_feature_2,
    ]

    mock_services["telemetry"].get_latest_for_vehicle.side_effect = [
        vehicle_telemetry_1,
        vehicle_telemetry_2,
    ]

    result = twin_service.get_station_twin_with_vehicles("ST-101")

    assert result["station"] == station
    assert result["state"] == station_state
    assert result["features"] == station_feature
    assert result["telemetry"] == station_telemetry

    assert len(result["vehicles"]) == 2

    assert result["vehicles"][0] == {
        "vehicle_id": "VH-101",
        "state": vehicle_state_1,
        "features": vehicle_feature_1,
        "telemetry": vehicle_telemetry_1,
    }

    assert result["vehicles"][1] == {
        "vehicle_id": "VH-102",
        "state": vehicle_state_2,
        "features": vehicle_feature_2,
        "telemetry": vehicle_telemetry_2,
    }


def test_get_station_twin_with_no_vehicles(
    twin_service,
    mock_services,
):
    station = Mock(station_id="ST-101")

    mock_services["production_structure"].get_station.return_value = station
    mock_services["state"].get_latest_station_state.return_value = Mock()
    mock_services["feature"].get_latest_station_feature.return_value = Mock()
    mock_services["telemetry"].get_latest_for_station.return_value = Mock()
    mock_services["state"].get_vehicles_at_station.return_value = []

    result = twin_service.get_station_twin_with_vehicles("ST-101")

    assert result["station"] == station
    assert result["vehicles"] == []


# ============================================================
# OPTIONAL DATA HELPER
# ============================================================


def test_optional_data_returns_none_for_not_found(
    twin_service,
):
    method = Mock(
        side_effect=NotFoundError("Missing")
    )

    result = twin_service._get_optional(
        method,
        "ST-101",
    )

    assert result is None


def test_optional_data_returns_value_when_found(
    twin_service,
):
    expected = Mock()

    method = Mock(return_value=expected)

    result = twin_service._get_optional(
        method,
        "ST-101",
    )

    assert result == expected