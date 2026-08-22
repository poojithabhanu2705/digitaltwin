from core.models import StationFeature, VehicleFeature


class FeatureRepository:

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
    def save_station_feature(**data):
        return StationFeature.objects.create(**data)

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
    def save_vehicle_feature(**data):
        return VehicleFeature.objects.create(**data)