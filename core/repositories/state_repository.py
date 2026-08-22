from core.models import StationState, VehicleState


class StateRepository:

    @staticmethod
    def get_latest_station_state(station_id):
        return (
            StationState.objects
            .filter(station_id=station_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_station_state_history(
        station_id,
        start_time,
        end_time
    ):
        return (
            StationState.objects
            .filter(
                station_id=station_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("timestamp")
        )

    @staticmethod
    def save_station_state(**data):
        return StationState.objects.create(**data)

    @staticmethod
    def get_latest_vehicle_state(vehicle_id):
        return (
            VehicleState.objects
            .filter(vehicle_id=vehicle_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_vehicle_state_history(
        vehicle_id,
        start_time,
        end_time
    ):
        return (
            VehicleState.objects
            .filter(
                vehicle_id=vehicle_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("timestamp")
        )

    @staticmethod
    def save_vehicle_state(**data):
        return VehicleState.objects.create(**data)