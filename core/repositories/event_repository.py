from core.models import (
    ProductionEvent,
    VehicleStationHistory,
    ManualObservation,
    QualityEvent,
    MaintenanceEvent,
)


class ProductionEventRepository:

    @staticmethod
    def get_by_id(event_id):
        return (
            ProductionEvent.objects
            .select_related(
                "station",
                "vehicle",
            )
            .filter(event_id=event_id)
            .first()
        )

    @staticmethod
    def get_station_events(
        station_id,
        start_time,
        end_time,
    ):
        return (
            ProductionEvent.objects
            .filter(
                station_id=station_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_vehicle_events(
        vehicle_id,
        start_time,
        end_time,
    ):
        return (
            ProductionEvent.objects
            .filter(
                vehicle_id=vehicle_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_by_event_type(event_type):
        return (
            ProductionEvent.objects
            .filter(event_type=event_type)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_latest_for_station(station_id):
        return (
            ProductionEvent.objects
            .filter(station_id=station_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_latest_for_vehicle(vehicle_id):
        return (
            ProductionEvent.objects
            .filter(vehicle_id=vehicle_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def create(**data):
        return ProductionEvent.objects.create(**data)


class VehicleStationHistoryRepository:

    @staticmethod
    def get_by_id(history_id):
        return (
            VehicleStationHistory.objects
            .select_related(
                "vehicle",
                "station",
            )
            .filter(id=history_id)
            .first()
        )

    @staticmethod
    def get_vehicle_history(vehicle_id):
        return (
            VehicleStationHistory.objects
            .select_related("station")
            .filter(vehicle_id=vehicle_id)
            .order_by("sequence_number", "entry_time")
        )

    @staticmethod
    def get_vehicle_history_range(
        vehicle_id,
        start_time,
        end_time,
    ):
        return (
            VehicleStationHistory.objects
            .select_related("station")
            .filter(
                vehicle_id=vehicle_id,
                entry_time__gte=start_time,
                entry_time__lte=end_time,
            )
            .order_by("entry_time")
        )

    @staticmethod
    def get_station_history(station_id):
        return (
            VehicleStationHistory.objects
            .select_related("vehicle")
            .filter(station_id=station_id)
            .order_by("-entry_time")
        )

    @staticmethod
    def get_current_visit(vehicle_id):
        return (
            VehicleStationHistory.objects
            .select_related("station")
            .filter(
                vehicle_id=vehicle_id,
                exit_time__isnull=True,
            )
            .order_by("-entry_time")
            .first()
        )

    @staticmethod
    def create(**data):
        return VehicleStationHistory.objects.create(**data)

    @staticmethod
    def update_exit_time(history_id, exit_time):
        history = (
            VehicleStationHistory.objects
            .filter(id=history_id)
            .first()
        )

        if history is None:
            return None

        history.exit_time = exit_time
        history.save(
            update_fields=["exit_time"]
        )

        return history


class ManualObservationRepository:

    @staticmethod
    def get_by_id(observation_id):
        return (
            ManualObservation.objects
            .select_related(
                "station",
                "vehicle",
            )
            .filter(observation_id=observation_id)
            .first()
        )

    @staticmethod
    def get_by_station(station_id):
        return (
            ManualObservation.objects
            .filter(station_id=station_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_vehicle(vehicle_id):
        return (
            ManualObservation.objects
            .filter(vehicle_id=vehicle_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_check_type(check_type):
        return (
            ManualObservation.objects
            .filter(check_type=check_type)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_time_range(
        start_time,
        end_time,
    ):
        return (
            ManualObservation.objects
            .filter(
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    @staticmethod
    def create(**data):
        return ManualObservation.objects.create(**data)


class QualityEventRepository:

    @staticmethod
    def get_by_id(event_id):
        return (
            QualityEvent.objects
            .select_related(
                "station",
                "vehicle",
                "origin_station",
                "detection_station",
            )
            .filter(quality_event_id=event_id)
            .first()
        )

    @staticmethod
    def get_vehicle_events(vehicle_id):
        return (
            QualityEvent.objects
            .filter(vehicle_id=vehicle_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_station_events(station_id):
        return (
            QualityEvent.objects
            .filter(station_id=station_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_origin_station_events(station_id):
        return (
            QualityEvent.objects
            .filter(origin_station_id=station_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_detection_station_events(station_id):
        return (
            QualityEvent.objects
            .filter(detection_station_id=station_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_defects(vehicle_id=None):
        queryset = QualityEvent.objects.filter(
            is_defect=True
        )

        if vehicle_id is not None:
            queryset = queryset.filter(
                vehicle_id=vehicle_id
            )

        return queryset.order_by("-timestamp")

    @staticmethod
    def get_by_defect_type(defect_type):
        return (
            QualityEvent.objects
            .filter(defect_type=defect_type)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_time_range(
        start_time,
        end_time,
    ):
        return (
            QualityEvent.objects
            .filter(
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    @staticmethod
    def create(**data):
        return QualityEvent.objects.create(**data)


class MaintenanceEventRepository:

    @staticmethod
    def get_by_id(event_id):
        return (
            MaintenanceEvent.objects
            .select_related(
                "station",
                "equipment",
            )
            .filter(maintenance_id=event_id)
            .first()
        )

    @staticmethod
    def get_station_events(station_id):
        return (
            MaintenanceEvent.objects
            .filter(station_id=station_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_equipment_events(equipment_id):
        return (
            MaintenanceEvent.objects
            .filter(equipment_id=equipment_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_failures(station_id=None):
        queryset = MaintenanceEvent.objects.filter(
            maintenance_type="FAILURE"
        )

        if station_id is not None:
            queryset = queryset.filter(
                station_id=station_id
            )

        return queryset.order_by("-timestamp")

    @staticmethod
    def get_by_maintenance_type(maintenance_type):
        return (
            MaintenanceEvent.objects
            .filter(maintenance_type=maintenance_type)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_time_range(
        start_time,
        end_time,
    ):
        return (
            MaintenanceEvent.objects
            .filter(
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    @staticmethod
    def create(**data):
        return MaintenanceEvent.objects.create(**data)