from core.models import StationFeature, VehicleFeature


class FeatureRepository:

    # ============================================================
    # STATION FEATURES
    # ============================================================

    @staticmethod
    def get_station_feature_by_id(feature_id):
        return (
            StationFeature.objects
            .select_related("station")
            .filter(id=feature_id)
            .first()
        )

    @staticmethod
    def get_latest_station_feature(station_id):
        return (
            StationFeature.objects
            .filter(station_id=station_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_station_features(
        station_id,
        start_time,
        end_time
    ):
        return (
            StationFeature.objects
            .filter(
                station_id=station_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_station_features_latest_first(
        station_id,
        start_time,
        end_time
    ):
        return (
            StationFeature.objects
            .filter(
                station_id=station_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("-timestamp")
        )

    @staticmethod
    def save_station_feature(**data):
        return StationFeature.objects.create(**data)

    @staticmethod
    def bulk_save_station_features(features):
        return StationFeature.objects.bulk_create(features)

    # ============================================================
    # VEHICLE FEATURES
    # ============================================================

    @staticmethod
    def get_vehicle_feature_by_id(feature_id):
        return (
            VehicleFeature.objects
            .select_related("vehicle")
            .filter(id=feature_id)
            .first()
        )

    @staticmethod
    def get_latest_vehicle_feature(vehicle_id):
        return (
            VehicleFeature.objects
            .filter(vehicle_id=vehicle_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_vehicle_features(
        vehicle_id,
        start_time,
        end_time
    ):
        return (
            VehicleFeature.objects
            .filter(
                vehicle_id=vehicle_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("timestamp")
        )

    @staticmethod
    def get_vehicle_features_latest_first(
        vehicle_id,
        start_time,
        end_time
    ):
        return (
            VehicleFeature.objects
            .filter(
                vehicle_id=vehicle_id,
                timestamp__gte=start_time,
                timestamp__lte=end_time
            )
            .order_by("-timestamp")
        )

    @staticmethod
    def save_vehicle_feature(**data):
        return VehicleFeature.objects.create(**data)

    @staticmethod
    def bulk_save_vehicle_features(features):
        return VehicleFeature.objects.bulk_create(features)