from core.models import Telemetry


class TelemetryRepository:

    @staticmethod
    def get_by_id(telemetry_id):
        return (
            Telemetry.objects
            .select_related(
                "station",
                "vehicle",
                "equipment",
                "sensor",
                "data_source",
            )
            .filter(telemetry_id=telemetry_id)
            .first()
        )

    @staticmethod
    def get_latest_for_station(station_id):
        return (
            Telemetry.objects
            .select_related(
                "station",
                "vehicle",
                "equipment",
                "sensor",
                "data_source",
            )
            .filter(station_id=station_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_latest_for_vehicle(vehicle_id):
        return (
            Telemetry.objects
            .select_related(
                "station",
                "vehicle",
                "equipment",
                "sensor",
                "data_source",
            )
            .filter(vehicle_id=vehicle_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_latest_for_equipment(equipment_id):
        return (
            Telemetry.objects
            .select_related(
                "station",
                "vehicle",
                "equipment",
                "sensor",
                "data_source",
            )
            .filter(equipment_id=equipment_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_latest_for_sensor(sensor_id):
        return (
            Telemetry.objects
            .select_related(
                "station",
                "vehicle",
                "equipment",
                "sensor",
                "data_source",
            )
            .filter(sensor_id=sensor_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_latest_for_data_source(data_source_id):
        return (
            Telemetry.objects
            .select_related(
                "station",
                "vehicle",
                "equipment",
                "sensor",
                "data_source",
            )
            .filter(data_source_id=data_source_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_station_history(
        station_id,
        start_time,
        end_time,
    ):
        return (
            Telemetry.objects
            .filter(
                station_id=station_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_vehicle_history(
        vehicle_id,
        start_time,
        end_time,
    ):
        return (
            Telemetry.objects
            .filter(
                vehicle_id=vehicle_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_equipment_history(
        equipment_id,
        start_time,
        end_time,
    ):
        return (
            Telemetry.objects
            .filter(
                equipment_id=equipment_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_sensor_history(
        sensor_id,
        start_time,
        end_time,
    ):
        return (
            Telemetry.objects
            .filter(
                sensor_id=sensor_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_data_source_history(
        data_source_id,
        start_time,
        end_time,
    ):
        return (
            Telemetry.objects
            .filter(
                data_source_id=data_source_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    @staticmethod
    def create(**data):
        return Telemetry.objects.create(**data)

    @staticmethod
    def bulk_create(readings):
        return Telemetry.objects.bulk_create(readings)