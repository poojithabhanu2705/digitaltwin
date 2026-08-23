from core.models import StationState, VehicleState


class StateRepository:

    # ============================================================
    # STATION STATE
    # ============================================================

    @staticmethod
    def get_station_state_by_id(state_id):
        return (
            StationState.objects
            .select_related("station")
            .filter(id=state_id)
            .first()
        )

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
    def get_station_state_history_latest_first(
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
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_health_state(health_state):
        return (
            StationState.objects
            .filter(health_state=health_state)
            .order_by("-timestamp")
        )

    @staticmethod
    def save_station_state(**data):
        return StationState.objects.create(**data)

    @staticmethod
    def bulk_save_station_states(states):
        return StationState.objects.bulk_create(states)

    # ============================================================
    # VEHICLE STATE
    # ============================================================

    @staticmethod
    def get_vehicle_state_by_id(state_id):
        return (
            VehicleState.objects
            .select_related(
                "vehicle",
                "current_station"
            )
            .filter(id=state_id)
            .first()
        )

    @staticmethod
    def get_latest_vehicle_state(vehicle_id):
        return (
            VehicleState.objects
            .select_related("current_station")
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
            .select_related("current_station")
            .filter(
                vehicle_id=vehicle_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_vehicle_state_history_latest_first(
        vehicle_id,
        start_time,
        end_time
    ):
        return (
            VehicleState.objects
            .select_related("current_station")
            .filter(
                vehicle_id=vehicle_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("-timestamp")
        )

    @staticmethod
    def get_vehicles_at_station(station_id):
        return (
            VehicleState.objects
            .filter(current_station_id=station_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_status(status):
        return (
            VehicleState.objects
            .filter(status=status)
            .order_by("-timestamp")
        )

    @staticmethod
    def save_vehicle_state(**data):
        return VehicleState.objects.create(**data)

    @staticmethod
    def bulk_save_vehicle_states(states):
        return VehicleState.objects.bulk_create(states)