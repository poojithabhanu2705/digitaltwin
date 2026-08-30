from rest_framework import serializers
from core.api.serializers.station_serializers import StationSerializer


class VehicleTwinSerializer(serializers.Serializer):
    vehicle_id = serializers.CharField()
    state = serializers.JSONField(required=False, allow_null=True)
    features = serializers.JSONField(required=False, allow_null=True)
    telemetry = serializers.JSONField(required=False, allow_null=True)


class TwinSnapshotSerializer(serializers.Serializer):
    station = StationSerializer(required=False, allow_null=True)
    state = serializers.JSONField(required=False, allow_null=True)
    features = serializers.JSONField(required=False, allow_null=True)
    telemetry = serializers.JSONField(required=False, allow_null=True)
    vehicle_id = serializers.CharField(required=False, allow_null=True)
    vehicles = VehicleTwinSerializer(many=True, required=False)

