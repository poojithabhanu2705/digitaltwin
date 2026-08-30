from rest_framework import serializers

from core.models import Plant


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = [
            "plant_id",
            "name",
            "location",
            "timezone",
            "status",
        ]
