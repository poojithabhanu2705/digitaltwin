from core.models import Telemetry


class TelemetryRepository:

    @staticmethod
    def get_latest_for_station(station_id):
        return (
            Telemetry.objects
            .filter(station_id=station_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_latest_for_vehicle(vehicle_id):
        return (
            Telemetry.objects
            .filter(vehicle_id=vehicle_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_station_history(
        station_id,
        start_time,
        end_time
    ):
        return (
            Telemetry.objects
            .filter(
                station_id=station_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_vehicle_history(
        vehicle_id,
        start_time,
        end_time
    ):
        return (
            Telemetry.objects
            .filter(
                vehicle_id=vehicle_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("timestamp")
        )

    @staticmethod
    def create(**data):
        return Telemetry.objects.create(**data)

    @staticmethod
    def bulk_create(readings):
        return Telemetry.objects.bulk_create(readings)