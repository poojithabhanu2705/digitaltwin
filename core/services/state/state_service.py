from core.repositories.state_repository import StateRepository

from core.services.exceptions import (
    NotFoundError,
    ValidationError,
)


class StateService:

    def __init__(
        self,
        state_repository=StateRepository,
    ):
        self.state_repository = state_repository

    # ============================================================
    # STATION STATE
    # ============================================================

    def get_station_state(self, state_id):
        state = (
            self.state_repository
            .get_station_state_by_id(state_id)
        )

        if state is None:
            raise NotFoundError(
                f"Station state '{state_id}' was not found."
            )

        return state

    def get_latest_station_state(self, station_id):
        state = (
            self.state_repository
            .get_latest_station_state(station_id)
        )

        if state is None:
            raise NotFoundError(
                f"No station state found for station "
                f"'{station_id}'."
            )

        return state

    def get_station_states(
        self,
        station_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(start_time, end_time)

        return (
            self.state_repository
            .get_station_state_history(
                station_id,
                start_time,
                end_time,
            )
        )

    def get_station_states_latest_first(
        self,
        station_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(start_time, end_time)

        return (
            self.state_repository
            .get_station_state_history_latest_first(
                station_id,
                start_time,
                end_time,
            )
        )

    def get_station_states_by_health_state(self, health_state):
        if not health_state:
            raise ValidationError(
                "health_state is required."
            )

        return (
            self.state_repository
            .get_by_health_state(health_state)
        )

    def save_station_state(self, **data):
        self._validate_station_state(data)

        return (
            self.state_repository
            .save_station_state(**data)
        )

    def bulk_save_station_states(self, states):
        if not states:
            raise ValidationError(
                "Station state batch cannot be empty."
            )

        for state in states:
            data = self._state_to_dict(state)
            self._validate_station_state(data)

        return (
            self.state_repository
            .bulk_save_station_states(states)
        )

    # ============================================================
    # VEHICLE STATE
    # ============================================================

    def get_vehicle_state(self, state_id):
        state = (
            self.state_repository
            .get_vehicle_state_by_id(state_id)
        )

        if state is None:
            raise NotFoundError(
                f"Vehicle state '{state_id}' was not found."
            )

        return state

    def get_latest_vehicle_state(self, vehicle_id):
        state = (
            self.state_repository
            .get_latest_vehicle_state(vehicle_id)
        )

        if state is None:
            raise NotFoundError(
                f"No vehicle state found for vehicle "
                f"'{vehicle_id}'."
            )

        return state

    def get_vehicle_states(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(start_time, end_time)

        return (
            self.state_repository
            .get_vehicle_state_history(
                vehicle_id,
                start_time,
                end_time,
            )
        )

    def get_vehicle_states_latest_first(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(start_time, end_time)

        return (
            self.state_repository
            .get_vehicle_state_history_latest_first(
                vehicle_id,
                start_time,
                end_time,
            )
        )

    def get_vehicles_at_station(self, station_id):
        return (
            self.state_repository
            .get_vehicles_at_station(station_id)
        )

    def get_vehicle_states_by_status(self, status):
        if not status:
            raise ValidationError(
                "status is required."
            )

        return (
            self.state_repository
            .get_by_status(status)
        )

    def save_vehicle_state(self, **data):
        self._validate_vehicle_state(data)

        return (
            self.state_repository
            .save_vehicle_state(**data)
        )

    def bulk_save_vehicle_states(self, states):
        if not states:
            raise ValidationError(
                "Vehicle state batch cannot be empty."
            )

        for state in states:
            data = self._state_to_dict(state)
            self._validate_vehicle_state(data)

        return (
            self.state_repository
            .bulk_save_vehicle_states(states)
        )

    # ============================================================
    # VALIDATION
    # ============================================================

    @staticmethod
    def _validate_time_range(start_time, end_time):
        if start_time is None or end_time is None:
            raise ValidationError(
                "Both start_time and end_time are required."
            )

        try:
            if start_time > end_time:
                raise ValidationError(
                    "start_time cannot be later than end_time."
                )
        except TypeError:
            pass

    @staticmethod
    def _validate_station_state(data):
        if not data.get("timestamp"):
            raise ValidationError(
                "Station state timestamp is required."
            )

        if (
            not data.get("station")
            and not data.get("station_id")
        ):
            raise ValidationError(
                "Station state station is required."
            )

        if not data.get("health_state"):
            raise ValidationError(
                "Station state health_state is required."
            )

        StateService._validate_non_negative_fields(
            data,
            (
                "health_risk",
                "confidence",
                "wip",
                "utilization",
                "throughput",
                "blocking_time",
                "starvation_time",
                "sensor_coverage",
                "data_quality",
            ),
        )

    @staticmethod
    def _validate_vehicle_state(data):
        if not data.get("timestamp"):
            raise ValidationError(
                "Vehicle state timestamp is required."
            )

        if (
            not data.get("vehicle")
            and not data.get("vehicle_id")
        ):
            raise ValidationError(
                "Vehicle state vehicle is required."
            )

        if not data.get("status"):
            raise ValidationError(
                "Vehicle state status is required."
            )

        StateService._validate_non_negative_fields(
            data,
            (
                "quality_risk",
                "confidence",
            ),
        )

    @staticmethod
    def _validate_non_negative_fields(data, fields):
        for field in fields:
            value = data.get(field)

            if value is None:
                continue

            if value < 0:
                raise ValidationError(
                    f"{field} cannot be negative."
                )

    @staticmethod
    def _state_to_dict(state):
        if isinstance(state, dict):
            return state

        return {
            field.name: getattr(state, field.name)
            for field in state._meta.fields
        }
