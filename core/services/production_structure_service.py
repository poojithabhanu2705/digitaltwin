from core.repositories.master_repository import (
    ProductionLineRepository,
    StationRepository,
    EquipmentRepository,
    RouteRepository,
)
from core.services.exceptions import (
    NotFoundError,
    ValidationError,
    ConflictError,
)


class ProductionStructureService:

    def __init__(
        self,
        production_line_repository=ProductionLineRepository,
        station_repository=StationRepository,
        equipment_repository=EquipmentRepository,
        route_repository=RouteRepository,
    ):
        self.production_line_repository = production_line_repository
        self.station_repository = station_repository
        self.equipment_repository = equipment_repository
        self.route_repository = route_repository

    # ---------------------------------------------------------
    # Production Line
    # ---------------------------------------------------------

    def create_line(self, **data):
        """
        Create a production line.
        """
        return self.production_line_repository.create(**data)

    def get_line(self, line_id):
        """
        Retrieve a production line by ID.

        Raises:
            NotFoundError: If the line does not exist.
        """
        line = self.production_line_repository.get_by_id(line_id)

        if line is None:
            raise NotFoundError(
                f"Production line '{line_id}' was not found."
            )

        return line

    def get_all_lines(self):
        """Retrieve all production lines."""
        return self.production_line_repository.get_all()

    def get_lines_by_plant(self, plant_id):
        """Retrieve production lines belonging to a plant."""
        return self.production_line_repository.get_by_plant(plant_id)

    def get_lines_by_status(self, status):
        """Retrieve production lines filtered by status."""
        return self.production_line_repository.get_by_status(status)

    def update_line(self, line_id, **data):
        """
        Update an existing production line.

        Raises:
            NotFoundError: If the line does not exist.
        """
        line = self.production_line_repository.update(
            line_id,
            **data,
        )

        if line is None:
            raise NotFoundError(
                f"Production line '{line_id}' was not found."
            )

        return line

    # ---------------------------------------------------------
    # Station
    # ---------------------------------------------------------

    def create_station(self, **data):
        """
        Create a station.

        Validates that the referenced production line exists.
        """
        line_id = data.get("line")

        if line_id is not None:
            self.get_line(line_id.pk if hasattr(line_id, 'pk') else line_id)

        if "status" in data:
            data["instrumentation_status"] = data.pop("status")

        return self.station_repository.create(**data)

    def get_station(self, station_id):
        """
        Retrieve a station by ID.

        Raises:
            NotFoundError: If the station does not exist.
        """
        station = self.station_repository.get_by_id(station_id)

        if station is None:
            raise NotFoundError(
                f"Station '{station_id}' was not found."
            )

        return station

    def get_all_stations(self):
        """Retrieve all stations."""
        return self.station_repository.get_all()

    def get_stations_ordered(self):
        """Retrieve stations ordered by production structure."""
        return self.station_repository.get_ordered()

    def get_stations_by_line(self, line_id):
        """Retrieve stations belonging to a production line."""
        return self.station_repository.get_by_line(line_id)

    def get_stations_by_type(self, station_type):
        """Retrieve stations filtered by type."""
        return self.station_repository.get_by_type(station_type)

    def get_stations_by_status(self, status):
        """Retrieve stations filtered by status."""
        return self.station_repository.get_by_status(status)

    def update_station(self, station_id, **data):
        """
        Update an existing station.

        If the line is changed, validates that the new line exists.
        """
        if "line" in data and data["line"] is not None:
            self.get_line(data["line"])

        station = self.station_repository.update(
            station_id,
            **data,
        )

        if station is None:
            raise NotFoundError(
                f"Station '{station_id}' was not found."
            )

        return station

    # ---------------------------------------------------------
    # Equipment
    # ---------------------------------------------------------

    def create_equipment(self, **data):
        """
        Create equipment.

        Validates that the referenced station exists.
        """
        station_id = data.get("station")

        if station_id is not None:
            self.get_station(station_id.pk if hasattr(station_id, 'pk') else station_id)

        return self.equipment_repository.create(**data)

    def get_equipment(self, equipment_id):
        """
        Retrieve equipment by ID.

        Raises:
            NotFoundError: If the equipment does not exist.
        """
        equipment = self.equipment_repository.get_by_id(equipment_id)

        if equipment is None:
            raise NotFoundError(
                f"Equipment '{equipment_id}' was not found."
            )

        return equipment

    def get_all_equipment(self):
        """Retrieve all equipment."""
        return self.equipment_repository.get_all()

    def get_equipment_by_station(self, station_id):
        """Retrieve equipment belonging to a station."""
        return self.equipment_repository.get_by_station(station_id)

    def get_equipment_by_type(self, equipment_type):
        """Retrieve equipment filtered by type."""
        return self.equipment_repository.get_by_type(equipment_type)

    def get_equipment_by_status(self, status):
        """Retrieve equipment filtered by status."""
        return self.equipment_repository.get_by_status(status)

    def update_equipment(self, equipment_id, **data):
        """
        Update existing equipment.

        If the station is changed, validates that the new station exists.
        """
        if "station" in data and data["station"] is not None:
            self.get_station(data["station"])

        equipment = self.equipment_repository.update(
            equipment_id,
            **data,
        )

        if equipment is None:
            raise NotFoundError(
                f"Equipment '{equipment_id}' was not found."
            )

        return equipment

    # ---------------------------------------------------------
    # Route
    # ---------------------------------------------------------

    def create_route(self, **data):
        """
        Create a route entry.

        Validates:
        - referenced production line exists
        - referenced station exists
        - station belongs to the specified production line
        """
        line_id = data.get("line")
        station_id = data.get("station")

        line = None
        station = None

        if line_id is not None:
            line = self.get_line(line_id.pk if hasattr(line_id, 'pk') else line_id)

        if station_id is not None:
            station = self.get_station(station_id.pk if hasattr(station_id, 'pk') else station_id)

        if line is not None and station is not None:
            if station.line_id != line.line_id:
                raise ValidationError(
                    "Route station must belong to the specified "
                    "production line."
                )

        return self.route_repository.create(**data)

    def get_route(self, route_id):
        """
        Retrieve a route by ID.

        Raises:
            NotFoundError: If the route does not exist.
        """
        route = self.route_repository.get_by_id(route_id)

        if route is None:
            raise NotFoundError(
                f"Route '{route_id}' was not found."
            )

        return route

    def get_all_routes(self):
        """Retrieve all routes."""
        return self.route_repository.get_all()

    def get_routes_by_line(self, line_id):
        """Retrieve routes belonging to a production line."""
        return self.route_repository.get_by_line(line_id)

    def get_route_sequence(self, line_id):
        """Retrieve the ordered station sequence for a line."""
        return self.route_repository.get_station_sequence(line_id)

    def get_route_at_sequence(self, line_id, sequence_number):
        """
        Retrieve the station at a specific sequence number.
        """
        route = self.route_repository.get_station_at_sequence(
            line_id,
            sequence_number,
        )

        if route is None:
            raise NotFoundError(
                f"No route was found for line '{line_id}' "
                f"at sequence '{sequence_number}'."
            )

        return route