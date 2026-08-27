from core.repositories.event_repository import (
    ProductionEventRepository,
    VehicleStationHistoryRepository,
    ManualObservationRepository,
    QualityEventRepository,
    MaintenanceEventRepository,
)

from core.services.exceptions import (
    NotFoundError,
    ValidationError,
)


class EventsService:

    def __init__(
        self,
        production_event_repository=ProductionEventRepository,
        vehicle_station_history_repository=VehicleStationHistoryRepository,
        manual_observation_repository=ManualObservationRepository,
        quality_event_repository=QualityEventRepository,
        maintenance_event_repository=MaintenanceEventRepository,
    ):
        self.production_event_repository = (
            production_event_repository
        )

        self.vehicle_station_history_repository = (
            vehicle_station_history_repository
        )

        self.manual_observation_repository = (
            manual_observation_repository
        )

        self.quality_event_repository = (
            quality_event_repository
        )

        self.maintenance_event_repository = (
            maintenance_event_repository
        )

    # ============================================================
    # PRODUCTION EVENTS
    # ============================================================

    def get_production_event(self, event_id):
        event = self.production_event_repository.get_by_id(
            event_id
        )

        if event is None:
            raise NotFoundError(
                f"Production event '{event_id}' was not found."
            )

        return event

    def get_station_production_events(
        self,
        station_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(start_time, end_time)

        return self.production_event_repository.get_station_events(
            station_id,
            start_time,
            end_time,
        )

    def get_vehicle_production_events(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(start_time, end_time)

        return self.production_event_repository.get_vehicle_events(
            vehicle_id,
            start_time,
            end_time,
        )

    def get_production_events_by_type(self, event_type):
        if not event_type:
            raise ValidationError(
                "event_type is required."
            )

        return self.production_event_repository.get_by_event_type(
            event_type
        )

    def get_latest_production_event_for_station(
        self,
        station_id,
    ):
        event = (
            self.production_event_repository
            .get_latest_for_station(station_id)
        )

        if event is None:
            raise NotFoundError(
                f"No production event found for station "
                f"'{station_id}'."
            )

        return event

    def get_latest_production_event_for_vehicle(
        self,
        vehicle_id,
    ):
        event = (
            self.production_event_repository
            .get_latest_for_vehicle(vehicle_id)
        )

        if event is None:
            raise NotFoundError(
                f"No production event found for vehicle "
                f"'{vehicle_id}'."
            )

        return event

    def create_production_event(self, **data):
        self._validate_production_event(data)

        return self.production_event_repository.create(
            **data
        )

    # ============================================================
    # VEHICLE-STATION HISTORY
    # ============================================================

    def get_vehicle_station_history(self, history_id):
        history = (
            self.vehicle_station_history_repository
            .get_by_id(history_id)
        )

        if history is None:
            raise NotFoundError(
                f"Vehicle station history '{history_id}' "
                f"was not found."
            )

        return history

    def get_vehicle_history(self, vehicle_id):
        return (
            self.vehicle_station_history_repository
            .get_vehicle_history(vehicle_id)
        )

    def get_vehicle_history_range(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(start_time, end_time)

        return (
            self.vehicle_station_history_repository
            .get_vehicle_history_range(
                vehicle_id,
                start_time,
                end_time,
            )
        )

    def get_station_vehicle_history(self, station_id):
        return (
            self.vehicle_station_history_repository
            .get_station_history(station_id)
        )

    def get_current_vehicle_visit(self, vehicle_id):
        history = (
            self.vehicle_station_history_repository
            .get_current_visit(vehicle_id)
        )

        if history is None:
            raise NotFoundError(
                f"No current station visit found for "
                f"vehicle '{vehicle_id}'."
            )

        return history

    def create_vehicle_station_history(self, **data):
        self._validate_vehicle_station_history(data)

        return (
            self.vehicle_station_history_repository
            .create(**data)
        )

    def update_vehicle_station_exit_time(
        self,
        history_id,
        exit_time,
    ):
        if exit_time is None:
            raise ValidationError(
                "exit_time is required."
            )

        history = (
            self.vehicle_station_history_repository
            .update_exit_time(
                history_id,
                exit_time,
            )
        )

        if history is None:
            raise NotFoundError(
                f"Vehicle station history '{history_id}' "
                f"was not found."
            )

        if (
            history.entry_time is not None
            and exit_time < history.entry_time
        ):
            raise ValidationError(
                "exit_time cannot be earlier than entry_time."
            )

        return history

    # ============================================================
    # MANUAL OBSERVATIONS
    # ============================================================

    def get_manual_observation(self, observation_id):
        observation = (
            self.manual_observation_repository
            .get_by_id(observation_id)
        )

        if observation is None:
            raise NotFoundError(
                f"Manual observation '{observation_id}' "
                f"was not found."
            )

        return observation

    def get_manual_observations_for_station(
        self,
        station_id,
    ):
        return (
            self.manual_observation_repository
            .get_by_station(station_id)
        )

    def get_manual_observations_for_vehicle(
        self,
        vehicle_id,
    ):
        return (
            self.manual_observation_repository
            .get_by_vehicle(vehicle_id)
        )

    def get_manual_observations_by_check_type(
        self,
        check_type,
    ):
        if not check_type:
            raise ValidationError(
                "check_type is required."
            )

        return (
            self.manual_observation_repository
            .get_by_check_type(check_type)
        )

    def get_manual_observations_by_time_range(
        self,
        start_time,
        end_time,
    ):
        self._validate_time_range(start_time, end_time)

        return (
            self.manual_observation_repository
            .get_by_time_range(
                start_time,
                end_time,
            )
        )

    def create_manual_observation(self, **data):
        self._validate_manual_observation(data)

        return (
            self.manual_observation_repository
            .create(**data)
        )

    # ============================================================
    # QUALITY EVENTS
    # ============================================================

    def get_quality_event(self, event_id):
        event = (
            self.quality_event_repository
            .get_by_id(event_id)
        )

        if event is None:
            raise NotFoundError(
                f"Quality event '{event_id}' was not found."
            )

        return event

    def get_quality_events_for_vehicle(self, vehicle_id):
        return (
            self.quality_event_repository
            .get_vehicle_events(vehicle_id)
        )

    def get_quality_events_for_station(self, station_id):
        return (
            self.quality_event_repository
            .get_station_events(station_id)
        )

    def get_quality_events_for_origin_station(
        self,
        station_id,
    ):
        return (
            self.quality_event_repository
            .get_origin_station_events(station_id)
        )

    def get_quality_events_for_detection_station(
        self,
        station_id,
    ):
        return (
            self.quality_event_repository
            .get_detection_station_events(station_id)
        )

    def get_quality_defects(self, vehicle_id=None):
        return (
            self.quality_event_repository
            .get_defects(vehicle_id)
        )

    def get_quality_events_by_defect_type(
        self,
        defect_type,
    ):
        if not defect_type:
            raise ValidationError(
                "defect_type is required."
            )

        return (
            self.quality_event_repository
            .get_by_defect_type(defect_type)
        )

    def get_quality_events_by_time_range(
        self,
        start_time,
        end_time,
    ):
        self._validate_time_range(start_time, end_time)

        return (
            self.quality_event_repository
            .get_by_time_range(
                start_time,
                end_time,
            )
        )

    def create_quality_event(self, **data):
        self._validate_quality_event(data)

        return self.quality_event_repository.create(
            **data
        )

    # ============================================================
    # MAINTENANCE EVENTS
    # ============================================================

    def get_maintenance_event(self, event_id):
        event = (
            self.maintenance_event_repository
            .get_by_id(event_id)
        )

        if event is None:
            raise NotFoundError(
                f"Maintenance event '{event_id}' was not found."
            )

        return event

    def get_maintenance_events_for_station(
        self,
        station_id,
    ):
        return (
            self.maintenance_event_repository
            .get_station_events(station_id)
        )

    def get_maintenance_events_for_equipment(
        self,
        equipment_id,
    ):
        return (
            self.maintenance_event_repository
            .get_equipment_events(equipment_id)
        )

    def get_maintenance_failures(
        self,
        station_id=None,
    ):
        return (
            self.maintenance_event_repository
            .get_failures(station_id)
        )

    def get_maintenance_events_by_type(
        self,
        maintenance_type,
    ):
        if not maintenance_type:
            raise ValidationError(
                "maintenance_type is required."
            )

        return (
            self.maintenance_event_repository
            .get_by_maintenance_type(
                maintenance_type
            )
        )

    def get_maintenance_events_by_time_range(
        self,
        start_time,
        end_time,
    ):
        self._validate_time_range(start_time, end_time)

        return (
            self.maintenance_event_repository
            .get_by_time_range(
                start_time,
                end_time,
            )
        )

    def create_maintenance_event(self, **data):
        self._validate_maintenance_event(data)

        return self.maintenance_event_repository.create(
            **data
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

        if start_time > end_time:
            raise ValidationError(
                "start_time cannot be later than end_time."
            )

    @staticmethod
    def _validate_production_event(data):
        if not data.get("timestamp"):
            raise ValidationError(
                "Production event timestamp is required."
            )

        if not data.get("vehicle") and not data.get("vehicle_id"):
            raise ValidationError(
                "Production event vehicle is required."
            )

        if not data.get("station") and not data.get("station_id"):
            raise ValidationError(
                "Production event station is required."
            )

        if not data.get("event_type"):
            raise ValidationError(
                "Production event event_type is required."
            )

        quantity = data.get("quantity")

        if quantity is not None and quantity < 1:
            raise ValidationError(
                "Production event quantity must be positive."
            )

        cycle_time = data.get("cycle_time")

        if cycle_time is not None and cycle_time < 0:
            raise ValidationError(
                "Production event cycle_time cannot be negative."
            )

    @staticmethod
    def _validate_vehicle_station_history(data):
        if not data.get("vehicle") and not data.get("vehicle_id"):
            raise ValidationError(
                "Vehicle is required."
            )

        if not data.get("station") and not data.get("station_id"):
            raise ValidationError(
                "Station is required."
            )

        if not data.get("entry_time"):
            raise ValidationError(
                "entry_time is required."
            )

        exit_time = data.get("exit_time")

        if (
            exit_time is not None
            and exit_time < data["entry_time"]
        ):
            raise ValidationError(
                "exit_time cannot be earlier than entry_time."
            )

        sequence_number = data.get("sequence_number")

        if sequence_number is not None and sequence_number < 0:
            raise ValidationError(
                "sequence_number cannot be negative."
            )

    @staticmethod
    def _validate_manual_observation(data):
        if not data.get("timestamp"):
            raise ValidationError(
                "Manual observation timestamp is required."
            )

        if not data.get("station") and not data.get("station_id"):
            raise ValidationError(
                "Manual observation station is required."
            )

        if not data.get("check_type"):
            raise ValidationError(
                "Manual observation check_type is required."
            )

        if not data.get("parameter"):
            raise ValidationError(
                "Manual observation parameter is required."
            )

        if not data.get("status"):
            raise ValidationError(
                "Manual observation status is required."
            )

    @staticmethod
    def _validate_quality_event(data):
        if not data.get("timestamp"):
            raise ValidationError(
                "Quality event timestamp is required."
            )

        if not data.get("vehicle") and not data.get("vehicle_id"):
            raise ValidationError(
                "Quality event vehicle is required."
            )

        defect_flag = data.get("defect_flag")

        if defect_flag and not data.get("defect_type"):
            raise ValidationError(
                "defect_type is required when defect_flag is true."
            )

    @staticmethod
    def _validate_maintenance_event(data):
        if not data.get("timestamp"):
            raise ValidationError(
                "Maintenance event timestamp is required."
            )

        if not data.get("station") and not data.get("station_id"):
            raise ValidationError(
                "Maintenance event station is required."
            )

        if not data.get("maintenance_type"):
            raise ValidationError(
                "maintenance_type is required."
            )

        duration = data.get("duration")

        if duration is not None and duration < 0:
            raise ValidationError(
                "Maintenance event duration cannot be negative."
            )