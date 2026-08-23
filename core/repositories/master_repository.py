from core.models import (
    Plant,
    ProductionLine,
    Station,
    Equipment,
    DataSource,
    Sensor,
    Vehicle,
    Route,
)


class PlantRepository:

    @staticmethod
    def get_by_id(plant_id):
        return (
            Plant.objects
            .filter(plant_id=plant_id)
            .first()
        )

    @staticmethod
    def get_all():
        return Plant.objects.all()

    @staticmethod
    def get_by_status(status):
        return (
            Plant.objects
            .filter(status=status)
        )

    @staticmethod
    def create(**data):
        return Plant.objects.create(**data)

    @staticmethod
    def update(plant_id, **data):
        plant = (
            Plant.objects
            .filter(plant_id=plant_id)
            .first()
        )

        if plant is None:
            return None

        for field, value in data.items():
            setattr(plant, field, value)

        plant.save()

        return plant


class ProductionLineRepository:

    @staticmethod
    def get_by_id(line_id):
        return (
            ProductionLine.objects
            .select_related("plant")
            .filter(line_id=line_id)
            .first()
        )

    @staticmethod
    def get_all():
        return (
            ProductionLine.objects
            .select_related("plant")
            .all()
        )

    @staticmethod
    def get_by_plant(plant_id):
        return (
            ProductionLine.objects
            .filter(plant_id=plant_id)
            .order_by("name")
        )

    @staticmethod
    def get_by_status(status):
        return (
            ProductionLine.objects
            .filter(status=status)
        )

    @staticmethod
    def create(**data):
        return ProductionLine.objects.create(**data)

    @staticmethod
    def update(line_id, **data):
        line = (
            ProductionLine.objects
            .filter(line_id=line_id)
            .first()
        )

        if line is None:
            return None

        for field, value in data.items():
            setattr(line, field, value)

        line.save()

        return line


class StationRepository:

    @staticmethod
    def get_by_id(station_id):
        return (
            Station.objects
            .select_related("line", "line__plant")
            .filter(station_id=station_id)
            .first()
        )

    @staticmethod
    def get_all():
        return (
            Station.objects
            .select_related("line")
            .all()
        )

    @staticmethod
    def get_ordered():
        return (
            Station.objects
            .select_related("line")
            .order_by("line_id", "position")
        )

    @staticmethod
    def get_by_line(line_id):
        return (
            Station.objects
            .filter(line_id=line_id)
            .order_by("position")
        )

    @staticmethod
    def get_by_type(station_type):
        return (
            Station.objects
            .filter(station_type=station_type)
        )

    @staticmethod
    def get_by_status(status):
        return (
            Station.objects
            .filter(instrumentation_status=status)
        )

    @staticmethod
    def create(**data):
        return Station.objects.create(**data)

    @staticmethod
    def update(station_id, **data):
        station = (
            Station.objects
            .filter(station_id=station_id)
            .first()
        )

        if station is None:
            return None

        for field, value in data.items():
            setattr(station, field, value)

        station.save()

        return station


class EquipmentRepository:

    @staticmethod
    def get_by_id(equipment_id):
        return (
            Equipment.objects
            .select_related("station", "station__line")
            .filter(equipment_id=equipment_id)
            .first()
        )

    @staticmethod
    def get_all():
        return (
            Equipment.objects
            .select_related("station")
            .all()
        )

    @staticmethod
    def get_by_station(station_id):
        return (
            Equipment.objects
            .filter(station_id=station_id)
            .order_by("name")
        )

    @staticmethod
    def get_by_type(equipment_type):
        return (
            Equipment.objects
            .filter(equipment_type=equipment_type)
        )

    @staticmethod
    def get_by_status(status):
        return (
            Equipment.objects
            .filter(status=status)
        )

    @staticmethod
    def create(**data):
        return Equipment.objects.create(**data)

    @staticmethod
    def update(equipment_id, **data):
        equipment = (
            Equipment.objects
            .filter(equipment_id=equipment_id)
            .first()
        )

        if equipment is None:
            return None

        for field, value in data.items():
            setattr(equipment, field, value)

        equipment.save()

        return equipment


class DataSourceRepository:

    @staticmethod
    def get_by_id(source_id):
        return (
            DataSource.objects
            .select_related(
                "plant",
                "line",
                "station",
                "equipment",
            )
            .filter(source_id=source_id)
            .first()
        )

    @staticmethod
    def get_all():
        return (
            DataSource.objects
            .select_related(
                "plant",
                "line",
                "station",
                "equipment",
            )
            .all()
        )

    @staticmethod
    def get_by_type(source_type):
        return (
            DataSource.objects
            .filter(source_type=source_type)
        )

    @staticmethod
    def get_by_status(status):
        return (
            DataSource.objects
            .filter(status=status)
        )

    @staticmethod
    def get_for_station(station_id):
        return (
            DataSource.objects
            .filter(station_id=station_id)
            .order_by("name")
        )

    @staticmethod
    def get_for_equipment(equipment_id):
        return (
            DataSource.objects
            .filter(equipment_id=equipment_id)
            .order_by("name")
        )

    @staticmethod
    def create(**data):
        return DataSource.objects.create(**data)

    @staticmethod
    def update(source_id, **data):
        source = (
            DataSource.objects
            .filter(source_id=source_id)
            .first()
        )

        if source is None:
            return None

        for field, value in data.items():
            setattr(source, field, value)

        source.save()

        return source


class SensorRepository:

    @staticmethod
    def get_by_id(sensor_id):
        return (
            Sensor.objects
            .select_related(
                "equipment",
                "equipment__station",
                "data_source",
            )
            .filter(sensor_id=sensor_id)
            .first()
        )

    @staticmethod
    def get_all():
        return (
            Sensor.objects
            .select_related("equipment", "data_source")
            .all()
        )

    @staticmethod
    def get_by_equipment(equipment_id):
        return (
            Sensor.objects
            .filter(equipment_id=equipment_id)
            .order_by("name")
        )

    @staticmethod
    def get_by_type(sensor_type):
        return (
            Sensor.objects
            .filter(sensor_type=sensor_type)
        )

    @staticmethod
    def get_by_measurement_type(measurement_type):
        return (
            Sensor.objects
            .filter(measurement_type=measurement_type)
        )

    @staticmethod
    def get_required_sensors(equipment_id=None):
        queryset = Sensor.objects.filter(
            is_required=True
        )

        if equipment_id:
            queryset = queryset.filter(
                equipment_id=equipment_id
            )

        return queryset.order_by("name")

    @staticmethod
    def get_by_status(status):
        return (
            Sensor.objects
            .filter(status=status)
        )

    @staticmethod
    def create(**data):
        return Sensor.objects.create(**data)

    @staticmethod
    def update(sensor_id, **data):
        sensor = (
            Sensor.objects
            .filter(sensor_id=sensor_id)
            .first()
        )

        if sensor is None:
            return None

        for field, value in data.items():
            setattr(sensor, field, value)

        sensor.save()

        return sensor


class VehicleRepository:

    @staticmethod
    def get_by_id(vehicle_id):
        return (
            Vehicle.objects
            .select_related("line", "line__plant")
            .filter(vehicle_id=vehicle_id)
            .first()
        )

    @staticmethod
    def get_all():
        return (
            Vehicle.objects
            .select_related("line")
            .all()
        )

    @staticmethod
    def get_by_line(line_id):
        return (
            Vehicle.objects
            .filter(line_id=line_id)
            .order_by("arrival_time")
        )

    @staticmethod
    def get_by_status(status):
        return (
            Vehicle.objects
            .filter(status=status)
        )

    @staticmethod
    def get_by_variant(variant):
        return (
            Vehicle.objects
            .filter(variant=variant)
        )

    @staticmethod
    def get_by_production_order(production_order):
        return (
            Vehicle.objects
            .filter(production_order=production_order)
        )

    @staticmethod
    def get_active():
        return (
            Vehicle.objects
            .filter(status="ACTIVE")
            .order_by("arrival_time")
        )

    @staticmethod
    def get_recent_arrivals(start_time):
        return (
            Vehicle.objects
            .filter(arrival_time__gte=start_time)
            .order_by("arrival_time")
        )

    @staticmethod
    def create(**data):
        return Vehicle.objects.create(**data)

    @staticmethod
    def update(vehicle_id, **data):
        vehicle = (
            Vehicle.objects
            .filter(vehicle_id=vehicle_id)
            .first()
        )

        if vehicle is None:
            return None

        for field, value in data.items():
            setattr(vehicle, field, value)

        vehicle.save()

        return vehicle


class RouteRepository:

    @staticmethod
    def get_by_id(route_id):
        return (
            Route.objects
            .select_related("line", "station")
            .filter(route_id=route_id)
            .first()
        )

    @staticmethod
    def get_all():
        return (
            Route.objects
            .select_related("line", "station")
            .order_by("line_id", "sequence_number")
        )

    @staticmethod
    def get_by_line(line_id):
        return (
            Route.objects
            .select_related("station")
            .filter(line_id=line_id)
            .order_by("sequence_number")
        )

    @staticmethod
    def get_station_sequence(line_id):
        return (
            Route.objects
            .select_related("station")
            .filter(line_id=line_id)
            .order_by("sequence_number")
        )

    @staticmethod
    def get_station_at_sequence(line_id, sequence_number):
        return (
            Route.objects
            .select_related("station")
            .filter(
                line_id=line_id,
                sequence_number=sequence_number,
            )
            .first()
        )

    @staticmethod
    def create(**data):
        return Route.objects.create(**data)