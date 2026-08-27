from core.repositories.telemetry_repository import TelemetryRepository
from core.services.exceptions import NotFoundError, ValidationError


class TelemetryService:

    def __init__(self, telemetry_repository=TelemetryRepository):
        self.telemetry_repository = telemetry_repository

    def create_telemetry(self, **data):
        self._validate_telemetry_data(data)

        return self.telemetry_repository.create(**data)

    def bulk_create_telemetry(self, readings):
        if not readings:
            raise ValidationError(
                "Telemetry batch cannot be empty."
            )

        for reading in readings:
            self._validate_telemetry_data(reading)

        return self.telemetry_repository.bulk_create(readings)

    def get_telemetry(self, telemetry_id):
        telemetry = self.telemetry_repository.get_by_id(
            telemetry_id
        )

        if telemetry is None:
            raise NotFoundError(
                f"Telemetry '{telemetry_id}' was not found."
            )

        return telemetry

    def get_latest_for_station(self, station_id):
        telemetry = (
            self.telemetry_repository
            .get_latest_for_station(station_id)
        )

        if telemetry is None:
            raise NotFoundError(
                f"No telemetry found for station '{station_id}'."
            )

        return telemetry

    def get_latest_for_vehicle(self, vehicle_id):
        telemetry = (
            self.telemetry_repository
            .get_latest_for_vehicle(vehicle_id)
        )

        if telemetry is None:
            raise NotFoundError(
                f"No telemetry found for vehicle '{vehicle_id}'."
            )

        return telemetry

    def get_latest_for_equipment(self, equipment_id):
        telemetry = (
            self.telemetry_repository
            .get_latest_for_equipment(equipment_id)
        )

        if telemetry is None:
            raise NotFoundError(
                f"No telemetry found for equipment '{equipment_id}'."
            )

        return telemetry

    def get_latest_for_sensor(self, sensor_id):
        telemetry = (
            self.telemetry_repository
            .get_latest_for_sensor(sensor_id)
        )

        if telemetry is None:
            raise NotFoundError(
                f"No telemetry found for sensor '{sensor_id}'."
            )

        return telemetry

    def get_latest_for_data_source(self, data_source_id):
        telemetry = (
            self.telemetry_repository
            .get_latest_for_data_source(data_source_id)
        )

        if telemetry is None:
            raise NotFoundError(
                f"No telemetry found for data source "
                f"'{data_source_id}'."
            )

        return telemetry

    def get_station_history(
        self,
        station_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(
            start_time,
            end_time,
        )

        return self.telemetry_repository.get_station_history(
            station_id,
            start_time,
            end_time,
        )

    def get_vehicle_history(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(
            start_time,
            end_time,
        )

        return self.telemetry_repository.get_vehicle_history(
            vehicle_id,
            start_time,
            end_time,
        )

    def get_equipment_history(
        self,
        equipment_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(
            start_time,
            end_time,
        )

        return self.telemetry_repository.get_equipment_history(
            equipment_id,
            start_time,
            end_time,
        )

    def get_sensor_history(
        self,
        sensor_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(
            start_time,
            end_time,
        )

        return self.telemetry_repository.get_sensor_history(
            sensor_id,
            start_time,
            end_time,
        )

    def get_data_source_history(
        self,
        data_source_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(
            start_time,
            end_time,
        )

        return self.telemetry_repository.get_data_source_history(
            data_source_id,
            start_time,
            end_time,
        )

    @staticmethod
    def _validate_time_range(start_time, end_time):
        if start_time is None or end_time is None:
            raise ValidationError(
                "Both start_time and end_time are required."
            )

        if start_time > end_time:
            raise ValidationError(
                "start_time cannot be later than end_time."
            )

    @staticmethod
    def _validate_telemetry_data(data):
        if not data.get("timestamp"):
            raise ValidationError(
                "Telemetry timestamp is required."
            )

        if not data.get("station") and not data.get("station_id"):
            raise ValidationError(
                "Telemetry station is required."
            )

        non_negative_fields = (
            "cycle_time",
            "vibration",
            "throughput",
            "alarm_count",
        )

        for field in non_negative_fields:
            value = data.get(field)

            if value is not None and value < 0:
                raise ValidationError(
                    f"{field} cannot be negative."
                )