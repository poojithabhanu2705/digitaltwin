from rest_framework import serializers


class TwinSnapshotSerializer(serializers.Serializer):
    station = serializers.JSONField(required=False, allow_null=True)
    state = serializers.JSONField(required=False, allow_null=True)
    features = serializers.JSONField(required=False, allow_null=True)
    telemetry = serializers.JSONField(required=False, allow_null=True)
    vehicle_id = serializers.CharField(required=False, allow_null=True)
    vehicles = serializers.ListField(required=False)
