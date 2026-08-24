import pytest

from core.models import Plant
from core.services.exceptions import NotFoundError, ValidationError
from core.services.production_structure_service import (
    ProductionStructureService,
)


@pytest.fixture
def production_structure_service():
    return ProductionStructureService()


@pytest.fixture
def plant():
    return Plant.objects.create(
        plant_id="TEST-P001",
        name="Test Plant",
    )


@pytest.fixture
def line(production_structure_service, plant):
    return production_structure_service.create_line(
        line_id="TEST-L001",
        plant=plant,
        name="Test Line",
        status="ACTIVE",
    )


@pytest.fixture
def station(production_structure_service, line):
    return production_structure_service.create_station(
        station_id="TEST-S001",
        line=line,
        name="Test Station",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=5.0,
        position=1,
        status="ACTIVE",
    )


@pytest.mark.django_db
def test_create_and_get_line(
    production_structure_service,
    plant,
):
    line = production_structure_service.create_line(
        line_id="TEST-L001",
        plant=plant,
        name="Test Line",
        status="ACTIVE",
    )

    assert line.line_id == "TEST-L001"
    assert line.name == "Test Line"
    assert line.plant_id == plant.plant_id

    retrieved = production_structure_service.get_line(
        "TEST-L001"
    )

    assert retrieved.line_id == "TEST-L001"
    assert retrieved.name == "Test Line"
    assert retrieved.plant_id == plant.plant_id


@pytest.mark.django_db
def test_get_all_lines(
    production_structure_service,
    plant,
):
    production_structure_service.create_line(
        line_id="TEST-L001",
        plant=plant,
        name="Line One",
        status="ACTIVE",
    )

    production_structure_service.create_line(
        line_id="TEST-L002",
        plant=plant,
        name="Line Two",
        status="ACTIVE",
    )

    lines = production_structure_service.get_all_lines()

    assert lines.count() == 2
    assert lines.filter(line_id="TEST-L001").exists()
    assert lines.filter(line_id="TEST-L002").exists()


@pytest.mark.django_db
def test_get_lines_by_plant(
    production_structure_service,
    plant,
):
    production_structure_service.create_line(
        line_id="TEST-L001",
        plant=plant,
        name="Line One",
        status="ACTIVE",
    )

    lines = production_structure_service.get_lines_by_plant(
        plant.plant_id
    )

    assert lines.count() == 1
    assert lines.first().line_id == "TEST-L001"


@pytest.mark.django_db
def test_update_line(
    production_structure_service,
    line,
):
    updated = production_structure_service.update_line(
        line.line_id,
        name="Updated Line",
    )

    assert updated.name == "Updated Line"

    retrieved = production_structure_service.get_line(
        line.line_id
    )

    assert retrieved.name == "Updated Line"


@pytest.mark.django_db
def test_missing_line_raises_not_found(
    production_structure_service,
):
    with pytest.raises(NotFoundError):
        production_structure_service.get_line(
            "DOES-NOT-EXIST"
        )


# ---------------------------------------------------------
# Station
# ---------------------------------------------------------


@pytest.mark.django_db
def test_create_station_and_get_station(
    production_structure_service,
    line,
):
    station = production_structure_service.create_station(
        station_id="TEST-S001",
        line=line,
        name="Test Station",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=5.0,
        position=1,
        status="ACTIVE",
    )

    assert station.station_id == "TEST-S001"
    assert station.name == "Test Station"
    assert station.line_id == line.line_id

    retrieved = production_structure_service.get_station(
        "TEST-S001"
    )

    assert retrieved.station_id == "TEST-S001"
    assert retrieved.line_id == line.line_id


@pytest.mark.django_db
def test_get_all_stations(
    production_structure_service,
    line,
):
    production_structure_service.create_station(
        station_id="TEST-S001",
        line=line,
        name="Station One",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=5.0,
        position=1,
        status="ACTIVE",
    )

    production_structure_service.create_station(
        station_id="TEST-S002",
        line=line,
        name="Station Two",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=5.0,
        position=2,
        status="ACTIVE",
    )

    stations = production_structure_service.get_all_stations()

    assert stations.count() == 2
    assert stations.filter(
        station_id="TEST-S001"
    ).exists()
    assert stations.filter(
        station_id="TEST-S002"
    ).exists()


@pytest.mark.django_db
def test_get_stations_by_line(
    production_structure_service,
    line,
    station,
):
    stations = production_structure_service.get_stations_by_line(
        line.line_id
    )

    assert stations.count() == 1
    assert stations.first().station_id == station.station_id


@pytest.mark.django_db
def test_get_stations_ordered(
    production_structure_service,
    line,
):
    production_structure_service.create_station(
        station_id="TEST-S002",
        line=line,
        name="Station Two",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=5.0,
        position=2,
        status="ACTIVE",
    )

    production_structure_service.create_station(
        station_id="TEST-S001",
        line=line,
        name="Station One",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=5.0,
        position=1,
        status="ACTIVE",
    )

    stations = production_structure_service.get_stations_ordered()

    assert stations.count() == 2
    assert stations[0].station_id == "TEST-S001"
    assert stations[1].station_id == "TEST-S002"


@pytest.mark.django_db
def test_get_stations_by_type(
    production_structure_service,
    station,
):
    stations = production_structure_service.get_stations_by_type(
        "ASSEMBLY"
    )

    assert stations.count() == 1
    assert stations.first().station_id == station.station_id


@pytest.mark.django_db
def test_get_stations_by_status(
    production_structure_service,
    station,
):
    stations = production_structure_service.get_stations_by_status(
        "ACTIVE"
    )

    assert stations.count() == 1
    assert stations.first().station_id == station.station_id


@pytest.mark.django_db
def test_update_station(
    production_structure_service,
    station,
):
    updated = production_structure_service.update_station(
        station.station_id,
        name="Updated Station",
    )

    assert updated.name == "Updated Station"

    retrieved = production_structure_service.get_station(
        station.station_id
    )

    assert retrieved.name == "Updated Station"


@pytest.mark.django_db
def test_missing_station_raises_not_found(
    production_structure_service,
):
    with pytest.raises(NotFoundError):
        production_structure_service.get_station(
            "DOES-NOT-EXIST"
        )


# ---------------------------------------------------------
# Equipment
# ---------------------------------------------------------


@pytest.mark.django_db
def test_create_equipment_and_get_equipment(
    production_structure_service,
    station,
):
    equipment = production_structure_service.create_equipment(
        equipment_id="TEST-E001",
        station=station,
        name="Test Equipment",
        equipment_type="MACHINE",
    )

    assert equipment.equipment_id == "TEST-E001"
    assert equipment.name == "Test Equipment"
    assert equipment.station_id == station.station_id

    retrieved = production_structure_service.get_equipment(
        "TEST-E001"
    )

    assert retrieved.equipment_id == "TEST-E001"
    assert retrieved.station_id == station.station_id


@pytest.mark.django_db
def test_get_all_equipment(
    production_structure_service,
    station,
):
    production_structure_service.create_equipment(
        equipment_id="TEST-E001",
        station=station,
        name="Equipment One",
        equipment_type="MACHINE",
    )

    production_structure_service.create_equipment(
        equipment_id="TEST-E002",
        station=station,
        name="Equipment Two",
        equipment_type="MACHINE",
    )

    equipment = production_structure_service.get_all_equipment()

    assert equipment.count() == 2
    assert equipment.filter(
        equipment_id="TEST-E001"
    ).exists()
    assert equipment.filter(
        equipment_id="TEST-E002"
    ).exists()


@pytest.mark.django_db
def test_get_equipment_by_station(
    production_structure_service,
    station,
):
    equipment = production_structure_service.create_equipment(
        equipment_id="TEST-E001",
        station=station,
        name="Test Equipment",
        equipment_type="MACHINE",
    )

    result = production_structure_service.get_equipment_by_station(
        station.station_id
    )

    assert result.count() == 1
    assert result.first().equipment_id == equipment.equipment_id


@pytest.mark.django_db
def test_get_equipment_by_type(
    production_structure_service,
    station,
):
    equipment = production_structure_service.create_equipment(
        equipment_id="TEST-E001",
        station=station,
        name="Test Equipment",
        equipment_type="MACHINE",
    )

    result = production_structure_service.get_equipment_by_type(
        "MACHINE"
    )

    assert result.count() == 1
    assert result.first().equipment_id == equipment.equipment_id


@pytest.mark.django_db
def test_get_equipment_by_status(
    production_structure_service,
    station,
):
    equipment = production_structure_service.create_equipment(
        equipment_id="TEST-E001",
        station=station,
        name="Test Equipment",
        equipment_type="MACHINE",
    )

    result = production_structure_service.get_equipment_by_status(
        "ACTIVE"
    )

    assert result.count() == 1
    assert result.first().equipment_id == equipment.equipment_id


@pytest.mark.django_db
def test_update_equipment(
    production_structure_service,
    station,
):
    equipment = production_structure_service.create_equipment(
        equipment_id="TEST-E001",
        station=station,
        name="Original Equipment",
        equipment_type="MACHINE",
    )

    updated = production_structure_service.update_equipment(
        equipment.equipment_id,
        name="Updated Equipment",
    )

    assert updated.name == "Updated Equipment"

    retrieved = production_structure_service.get_equipment(
        equipment.equipment_id
    )

    assert retrieved.name == "Updated Equipment"


@pytest.mark.django_db
def test_missing_equipment_raises_not_found(
    production_structure_service,
):
    with pytest.raises(NotFoundError):
        production_structure_service.get_equipment(
            "DOES-NOT-EXIST"
        )


# ---------------------------------------------------------
# Route
# ---------------------------------------------------------


@pytest.mark.django_db
def test_create_route_and_get_route(
    production_structure_service,
    line,
    station,
):
    route = production_structure_service.create_route(
        line=line,
        station=station,
        sequence_number=1,
    )

    assert route.line_id == line.line_id
    assert route.station_id == station.station_id
    assert route.sequence_number == 1

    retrieved = production_structure_service.get_route(
        route.route_id
    )

    assert retrieved.route_id == route.route_id


@pytest.mark.django_db
def test_get_all_routes(
    production_structure_service,
    line,
    station,
):
    production_structure_service.create_route(
        line=line,
        station=station,
        sequence_number=1,
    )

    routes = production_structure_service.get_all_routes()

    assert routes.count() == 1


@pytest.mark.django_db
def test_get_routes_by_line(
    production_structure_service,
    line,
    station,
):
    route = production_structure_service.create_route(
        line=line,
        station=station,
        sequence_number=1,
    )

    routes = production_structure_service.get_routes_by_line(
        line.line_id
    )

    assert routes.count() == 1
    assert routes.first().route_id == route.route_id


@pytest.mark.django_db
def test_get_route_sequence(
    production_structure_service,
    line,
    station,
):
    result = production_structure_service.create_route(
        line=line,
        station=station,
        sequence_number=1,
    )

    sequence = production_structure_service.get_route_sequence(
        line.line_id
    )

    assert sequence.count() == 1
    assert sequence.first().station_id == station.station_id


@pytest.mark.django_db
def test_get_route_at_sequence(
    production_structure_service,
    line,
    station,
):
    production_structure_service.create_route(
        line=line,
        station=station,
        sequence_number=1,
    )

    route = production_structure_service.get_route_at_sequence(
        line.line_id,
        1,
    )

    assert route.station_id == station.station_id
    assert route.sequence_number == 1


@pytest.mark.django_db
def test_create_route_rejects_station_from_different_line(
    production_structure_service,
    plant,
):
    line_one = production_structure_service.create_line(
        line_id="TEST-L001",
        plant=plant,
        name="Line One",
        status="ACTIVE",
    )

    line_two = production_structure_service.create_line(
        line_id="TEST-L002",
        plant=plant,
        name="Line Two",
        status="ACTIVE",
    )

    station_two = production_structure_service.create_station(
        station_id="TEST-S001",
        line=line_two,
        name="Station Two",
        station_type="ASSEMBLY",
        capacity=10,
        base_cycle_time=5.0,
        position=1,
        status="ACTIVE",
    )

    with pytest.raises(ValidationError):
        production_structure_service.create_route(
            line=line_one,
            station=station_two,
            sequence_number=1,
        )


@pytest.mark.django_db
def test_missing_route_raises_not_found(
    production_structure_service,
):
    with pytest.raises(NotFoundError):
        production_structure_service.get_route(999999)


@pytest.mark.django_db
def test_missing_route_sequence_raises_not_found(
    production_structure_service,
    line,
):
    with pytest.raises(NotFoundError):
        production_structure_service.get_route_at_sequence(
            line.line_id,
            999,
        )