from rest_framework import serializers

from core.models import Station


class StationSerializer(serializers.ModelSerializer):
    line_id = serializers.CharField(
        source="line.line_id",
        read_only=True,
    )
    line_name = serializers.CharField(
        source="line.name",
        read_only=True,
    )
    plant_id = serializers.CharField(
        source="line.plant.plant_id",
        read_only=True,
    )
    status = serializers.CharField(
        source="instrumentation_status",
        read_only=True,
    )
    sequence_number = serializers.IntegerField(
        source="position",
        read_only=True,
    )

    class Meta:
        model = Station
        fields = [
            "station_id",
            "name",
            "line_id",
            "line_name",
            "plant_id",
            "station_type",
            "status",
            "sequence_number",
            "capacity",
            "base_cycle_time",
            "description",
        ]
