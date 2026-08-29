from core.repositories.feature_repository import FeatureRepository

from core.services.exceptions import (
    NotFoundError,
    ValidationError,
)


class FeatureService:

    def __init__(
        self,
        feature_repository=FeatureRepository,
    ):
        self.feature_repository = feature_repository

    # ============================================================
    # STATION FEATURES
    # ============================================================

    def get_station_feature(self, feature_id):
        feature = (
            self.feature_repository
            .get_station_feature_by_id(feature_id)
        )

        if feature is None:
            raise NotFoundError(
                f"Station feature '{feature_id}' was not found."
            )

        return feature

    def get_latest_station_feature(self, station_id):
        feature = (
            self.feature_repository
            .get_latest_station_feature(station_id)
        )

        if feature is None:
            raise NotFoundError(
                f"No station feature found for station "
                f"'{station_id}'."
            )

        return feature

    def get_station_features(
        self,
        station_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(
            start_time,
            end_time,
        )

        return (
            self.feature_repository
            .get_station_features(
                station_id,
                start_time,
                end_time,
            )
        )

    def get_station_features_latest_first(
        self,
        station_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(
            start_time,
            end_time,
        )

        return (
            self.feature_repository
            .get_station_features_latest_first(
                station_id,
                start_time,
                end_time,
            )
        )

    def save_station_feature(self, **data):
        self._validate_station_feature(data)

        return (
            self.feature_repository
            .save_station_feature(**data)
        )

    def bulk_save_station_features(self, features):
        if not features:
            raise ValidationError(
                "Station feature batch cannot be empty."
            )

        for feature in features:
            data = self._feature_to_dict(feature)

            self._validate_station_feature(data)

        return (
            self.feature_repository
            .bulk_save_station_features(features)
        )

    # ============================================================
    # VEHICLE FEATURES
    # ============================================================

    def get_vehicle_feature(self, feature_id):
        feature = (
            self.feature_repository
            .get_vehicle_feature_by_id(feature_id)
        )

        if feature is None:
            raise NotFoundError(
                f"Vehicle feature '{feature_id}' was not found."
            )

        return feature

    def get_latest_vehicle_feature(self, vehicle_id):
        feature = (
            self.feature_repository
            .get_latest_vehicle_feature(vehicle_id)
        )

        if feature is None:
            raise NotFoundError(
                f"No vehicle feature found for vehicle "
                f"'{vehicle_id}'."
            )

        return feature

    def get_vehicle_features(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(
            start_time,
            end_time,
        )

        return (
            self.feature_repository
            .get_vehicle_features(
                vehicle_id,
                start_time,
                end_time,
            )
        )

    def get_vehicle_features_latest_first(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self._validate_time_range(
            start_time,
            end_time,
        )

        return (
            self.feature_repository
            .get_vehicle_features_latest_first(
                vehicle_id,
                start_time,
                end_time,
            )
        )

    def save_vehicle_feature(self, **data):
        self._validate_vehicle_feature(data)

        return (
            self.feature_repository
            .save_vehicle_feature(**data)
        )

    # ============================================================
    # VALIDATION
    # ============================================================

    @staticmethod
    def _validate_time_range(
        start_time,
        end_time,
    ):
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
    def _validate_station_feature(data):
        if not data.get("timestamp"):
            raise ValidationError(
                "Station feature timestamp is required."
            )

        if (
            not data.get("station")
            and not data.get("station_id")
        ):
            raise ValidationError(
                "Station feature station is required."
            )

        non_negative_fields = (
            "avg_cycle_time",
            "cycle_time_std",
            "avg_torque",
            "torque_deviation",
            "temperature_mean",
            "vibration_mean",
            "alarm_rate",
            "utilization",
            "throughput",
            "wip",
            "blocking_time",
            "starvation_time",
            "sensor_coverage_ratio",
            "data_completeness",
            "imputation_ratio",
            "manual_observation_count",
        )

        FeatureService._validate_non_negative_fields(
            data,
            non_negative_fields,
        )

    @staticmethod
    def _validate_vehicle_feature(data):
        if not data.get("timestamp"):
            raise ValidationError(
                "Vehicle feature timestamp is required."
            )

        if (
            not data.get("vehicle")
            and not data.get("vehicle_id")
        ):
            raise ValidationError(
                "Vehicle feature vehicle is required."
            )

        if not data.get("variant"):
            raise ValidationError(
                "Vehicle feature variant is required."
            )

        non_negative_fields = (
            "avg_cycle_time",
            "cycle_time_deviation",
            "torque_deviation",
            "stations_exposed",
            "degraded_station_count",
            "cumulative_risk",
            "quality_event_count",
            "manual_observation_count",
        )

        FeatureService._validate_non_negative_fields(
            data,
            non_negative_fields,
        )

    @staticmethod
    def _validate_non_negative_fields(
        data,
        fields,
    ):
        for field in fields:
            value = data.get(field)

            if value is None:
                continue

            if value < 0:
                raise ValidationError(
                    f"{field} cannot be negative."
                )

    @staticmethod
    def _feature_to_dict(feature):
        if isinstance(feature, dict):
            return feature

        return {
            field.name: getattr(feature, field.name)
            for field in feature._meta.fields
        }