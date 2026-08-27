import pytest

from core.models import Plant
from core.services.exceptions import NotFoundError
from core.services.master.plant_service import PlantService


@pytest.fixture
def plant_service():
    return PlantService()


@pytest.mark.django_db
def test_create_and_get_plant(plant_service):
    created = plant_service.create_plant(
        plant_id="TEST-P001",
        name="Test Plant",
        location="Kharagpur",
        timezone="UTC",
        status="ACTIVE",
    )

    assert created.plant_id == "TEST-P001"
    assert created.name == "Test Plant"

    retrieved = plant_service.get_plant("TEST-P001")

    assert retrieved.plant_id == "TEST-P001"
    assert retrieved.name == "Test Plant"


@pytest.mark.django_db
def test_get_all_plants(plant_service):
    plant_service.create_plant(
        plant_id="TEST-P001",
        name="Plant One",
        location="Location One",
        timezone="UTC",
        status="ACTIVE",
    )

    plant_service.create_plant(
        plant_id="TEST-P002",
        name="Plant Two",
        location="Location Two",
        timezone="UTC",
        status="ACTIVE",
    )

    plants = plant_service.get_all_plants()

    assert plants.count() == 2
    assert plants.filter(plant_id="TEST-P001").exists()
    assert plants.filter(plant_id="TEST-P002").exists()


@pytest.mark.django_db
def test_get_plants_by_status(plant_service):
    plant_service.create_plant(
        plant_id="TEST-P001",
        name="Active Plant",
        location="Location",
        timezone="UTC",
        status="ACTIVE",
    )

    plants = plant_service.get_plants_by_status("ACTIVE")

    assert plants.count() == 1
    assert plants.first().plant_id == "TEST-P001"


@pytest.mark.django_db
def test_update_plant(plant_service):
    plant_service.create_plant(
        plant_id="TEST-P001",
        name="Original Plant",
        location="Original Location",
        timezone="UTC",
        status="ACTIVE",
    )

    updated = plant_service.update_plant(
        "TEST-P001",
        name="Updated Plant",
        location="Updated Location",
    )

    assert updated.name == "Updated Plant"
    assert updated.location == "Updated Location"

    # Verify the update was actually persisted.
    retrieved = plant_service.get_plant("TEST-P001")

    assert retrieved.name == "Updated Plant"
    assert retrieved.location == "Updated Location"


@pytest.mark.django_db
def test_get_missing_plant_raises_not_found(plant_service):
    with pytest.raises(NotFoundError):
        plant_service.get_plant("DOES-NOT-EXIST")


@pytest.mark.django_db
def test_update_missing_plant_raises_not_found(plant_service):
    with pytest.raises(NotFoundError):
        plant_service.update_plant(
            "DOES-NOT-EXIST",
            name="Updated Name",
        )