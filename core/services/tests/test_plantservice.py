from unittest.mock import Mock

import pytest

from core.services.master.plant_service import PlantService
from core.services.exceptions import NotFoundError


@pytest.fixture
def plant_repository():
    return Mock()


@pytest.fixture
def plant_service(plant_repository):
    return PlantService(plant_repository)


def test_get_plant_returns_plant(
    plant_service,
    plant_repository,
):
    plant = Mock(plant_id="P001")

    plant_repository.get_by_id.return_value = plant

    result = plant_service.get_plant("P001")

    assert result == plant
    plant_repository.get_by_id.assert_called_once_with("P001")


def test_get_plant_raises_not_found(
    plant_service,
    plant_repository,
):
    plant_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        plant_service.get_plant("P001")

    plant_repository.get_by_id.assert_called_once_with("P001")


def test_get_all_plants(
    plant_service,
    plant_repository,
):
    plants = [Mock(), Mock()]

    plant_repository.get_all.return_value = plants

    result = plant_service.get_all_plants()

    assert result == plants
    plant_repository.get_all.assert_called_once_with()


def test_get_plants_by_status(
    plant_service,
    plant_repository,
):
    plants = [Mock(), Mock()]

    plant_repository.get_by_status.return_value = plants

    result = plant_service.get_plants_by_status("ACTIVE")

    assert result == plants
    plant_repository.get_by_status.assert_called_once_with(
        "ACTIVE"
    )


def test_create_plant(
    plant_service,
    plant_repository,
):
    plant = Mock(plant_id="P001")

    plant_repository.create.return_value = plant

    result = plant_service.create_plant(
        plant_id="P001",
        name="Plant 1",
        status="ACTIVE",
    )

    assert result == plant

    plant_repository.create.assert_called_once_with(
        plant_id="P001",
        name="Plant 1",
        status="ACTIVE",
    )


def test_update_plant(
    plant_service,
    plant_repository,
):
    plant = Mock(plant_id="P001")

    plant_repository.update.return_value = plant

    result = plant_service.update_plant(
        "P001",
        name="Updated Plant",
    )

    assert result == plant

    plant_repository.update.assert_called_once_with(
        "P001",
        name="Updated Plant",
    )


def test_update_plant_raises_not_found(
    plant_service,
    plant_repository,
):
    plant_repository.update.return_value = None

    with pytest.raises(NotFoundError):
        plant_service.update_plant(
            "P999",
            name="Updated Plant",
        )

    plant_repository.update.assert_called_once_with(
        "P999",
        name="Updated Plant",
    )