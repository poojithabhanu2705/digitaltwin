from rest_framework import serializers

from core.models import StationState, StationFeature, Telemetry, VehicleState, VehicleFeature
from core.api.serializers.station_serializers import StationSerializer


# ── Station-level sub-serializers ───────────────────────────────────────────

class StationStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationState
        fields = [
            "health_state",
            "health_risk",
            "confidence",
            "wip",
            "utilization",
            "throughput",
            "blocking_time",
            "starvation_time",
            "current_cycle_time",
            "sensor_coverage",
            "data_quality",
            "timestamp",
        ]


class StationFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationFeature
        fields = [
            "avg_cycle_time",
            "cycle_time_std",
            "cycle_time_trend",
            "avg_torque",
            "torque_deviation",
            "temperature_mean",
            "vibration_mean",
            "alarm_rate",
            "utilization",
            "throughput",
            "wip",
            "blocking_time",
            "timestamp",
        ]


class TelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Telemetry
        fields = [
            "cycle_time",
            "torque",
            "temperature",
            "vibration",
            "throughput",
            "machine_state",
            "alarm_count",
            "data_quality",
            "timestamp",
        ]


# ── Vehicle-level sub-serializers ────────────────────────────────────────────

class VehicleStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleState
        fields = [
            "status",
            "quality_risk",
            "confidence",
            "risk_source",
            "timestamp",
        ]


class VehicleFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleFeature
        fields = [
            "variant",
            "avg_cycle_time",
            "cycle_time_deviation",
            "torque_deviation",
            "stations_exposed",
            "degraded_station_count",
            "cumulative_risk",
            "quality_event_count",
            "timestamp",
        ]


class VehicleTwinSerializer(serializers.Serializer):
    vehicle_id = serializers.CharField()
    state = VehicleStateSerializer(required=False, allow_null=True)
    features = VehicleFeatureSerializer(required=False, allow_null=True)
    telemetry = TelemetrySerializer(required=False, allow_null=True)


# ── Top-level station twin snapshot ─────────────────────────────────────────

class TwinSnapshotSerializer(serializers.Serializer):
    station = StationSerializer(required=False, allow_null=True)
    state = StationStateSerializer(required=False, allow_null=True)
    features = StationFeatureSerializer(required=False, allow_null=True)
    telemetry = TelemetrySerializer(required=False, allow_null=True)
    vehicle_id = serializers.CharField(required=False, allow_null=True)
    vehicles = VehicleTwinSerializer(many=True, required=False)


