from core.models import (
    StationDependency,
    VehicleExposure,
)


class RiskRepository:

    @staticmethod
    def get_downstream_stations(station_id):
        return (
            StationDependency.objects
            .filter(upstream_station_id=station_id)
            .select_related("downstream_station")
        )

    @staticmethod
    def get_upstream_stations(station_id):
        return (
            StationDependency.objects
            .filter(downstream_station_id=station_id)
            .select_related("upstream_station")
        )

    @staticmethod
    def save_dependency(**data):
        return StationDependency.objects.create(**data)

    @staticmethod
    def get_vehicle_exposure(
        vehicle_id,
        start_time=None,
        end_time=None
    ):
        queryset = VehicleExposure.objects.filter(
            vehicle_id=vehicle_id
        )

        if start_time:
            queryset = queryset.filter(
                timestamp__gte=start_time
            )

        if end_time:
            queryset = queryset.filter(
                timestamp__lte=end_time
            )

        return queryset.order_by("timestamp")

    @staticmethod
    def save_exposure(**data):
        return VehicleExposure.objects.create(**data)