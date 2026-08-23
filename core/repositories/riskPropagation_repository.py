from core.models import (
    StationDependency,
    VehicleExposure,
)


class RiskRepository:

    # ============================================================
    # STATION DEPENDENCIES
    # ============================================================

    @staticmethod
    def get_dependency_by_id(dependency_id):
        return (
            StationDependency.objects
            .select_related(
                "upstream_station",
                "downstream_station",
            )
            .filter(id=dependency_id)
            .first()
        )

    @staticmethod
    def get_downstream_stations(station_id):
        return (
            StationDependency.objects
            .filter(
                upstream_station_id=station_id
            )
            .select_related("downstream_station")
            .order_by("downstream_station_id")
        )

    @staticmethod
    def get_upstream_stations(station_id):
        return (
            StationDependency.objects
            .filter(
                downstream_station_id=station_id
            )
            .select_related("upstream_station")
            .order_by("upstream_station_id")
        )

    @staticmethod
    def get_dependencies_for_station(station_id):
        return (
            StationDependency.objects
            .filter(
                upstream_station_id=station_id
            )
            .select_related("downstream_station")
        )

    @staticmethod
    def get_dependency(
        upstream_station_id,
        downstream_station_id,
    ):
        return (
            StationDependency.objects
            .select_related(
                "upstream_station",
                "downstream_station",
            )
            .filter(
                upstream_station_id=upstream_station_id,
                downstream_station_id=downstream_station_id,
            )
            .first()
        )

    @staticmethod
    def get_by_dependency_type(dependency_type):
        return (
            StationDependency.objects
            .filter(
                dependency_type=dependency_type
            )
            .select_related(
                "upstream_station",
                "downstream_station",
            )
        )

    @staticmethod
    def save_dependency(**data):
        return StationDependency.objects.create(**data)

    @staticmethod
    def bulk_save_dependencies(dependencies):
        return StationDependency.objects.bulk_create(
            dependencies
        )

    # ============================================================
    # VEHICLE EXPOSURES
    # ============================================================

    @staticmethod
    def get_exposure_by_id(exposure_id):
        return (
            VehicleExposure.objects
            .select_related(
                "vehicle",
                "station",
                "source_prediction",
            )
            .filter(id=exposure_id)
            .first()
        )

    @staticmethod
    def get_vehicle_exposure(
        vehicle_id,
        start_time=None,
        end_time=None
    ):
        queryset = (
            VehicleExposure.objects
            .filter(vehicle_id=vehicle_id)
        )

        if start_time is not None:
            queryset = queryset.filter(
                timestamp__gte=start_time
            )

        if end_time is not None:
            queryset = queryset.filter(
                timestamp__lte=end_time
            )

        return queryset.order_by("timestamp")

    @staticmethod
    def get_station_exposure(
        station_id,
        start_time=None,
        end_time=None
    ):
        queryset = (
            VehicleExposure.objects
            .filter(station_id=station_id)
        )

        if start_time is not None:
            queryset = queryset.filter(
                timestamp__gte=start_time
            )

        if end_time is not None:
            queryset = queryset.filter(
                timestamp__lte=end_time
            )

        return queryset.order_by("timestamp")

    @staticmethod
    def get_latest_vehicle_exposure(vehicle_id):
        return (
            VehicleExposure.objects
            .select_related(
                "station",
                "source_prediction",
            )
            .filter(vehicle_id=vehicle_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_latest_station_exposure(station_id):
        return (
            VehicleExposure.objects
            .select_related(
                "vehicle",
                "source_prediction",
            )
            .filter(station_id=station_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_by_source_prediction(prediction_id):
        return (
            VehicleExposure.objects
            .select_related(
                "vehicle",
                "station",
            )
            .filter(
                source_prediction_id=prediction_id
            )
            .order_by("timestamp")
        )

    @staticmethod
    def save_exposure(**data):
        return VehicleExposure.objects.create(
            **data
        )

    @staticmethod
    def bulk_save_exposures(exposures):
        return VehicleExposure.objects.bulk_create(
            exposures
        )