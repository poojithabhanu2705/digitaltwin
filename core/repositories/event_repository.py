from core.models import (
    ProductionEvent,
    QualityEvent,
    MaintenanceEvent,
)


class ProductionEventRepository:

    @staticmethod
    def get_station_events(
        station_id,
        start_time,
        end_time
    ):
        return (
            ProductionEvent.objects
            .filter(
                station_id=station_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_vehicle_events(
        vehicle_id,
        start_time,
        end_time
    ):
        return (
            ProductionEvent.objects
            .filter(
                vehicle_id=vehicle_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("timestamp")
        )

    @staticmethod
    def create(**data):
        return ProductionEvent.objects.create(**data)


class QualityEventRepository:

    @staticmethod
    def get_vehicle_events(vehicle_id):
        return (
            QualityEvent.objects
            .filter(vehicle_id=vehicle_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_defects(vehicle_id=None):
        queryset = QualityEvent.objects.filter(
            defect_flag=True
        )

        if vehicle_id:
            queryset = queryset.filter(
                vehicle_id=vehicle_id
            )

        return queryset.order_by("-timestamp")


class MaintenanceEventRepository:

    @staticmethod
    def get_station_events(station_id):
        return (
            MaintenanceEvent.objects
            .filter(station_id=station_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_failures(station_id=None):
        queryset = MaintenanceEvent.objects.filter(
            failure_type__isnull=False
        )

        if station_id:
            queryset = queryset.filter(
                station_id=station_id
            )

        return queryset.order_by("-timestamp")