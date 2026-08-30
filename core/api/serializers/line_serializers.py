from rest_framework import serializers

from core.models import ProductionLine


class ProductionLineSerializer(serializers.ModelSerializer):
    plant_id = serializers.CharField(
        source="plant.plant_id",
        read_only=True,
    )

    plant_name = serializers.CharField(
        source="plant.name",
        read_only=True,
    )

    class Meta:
        model = ProductionLine
        fields = [
            "line_id",
            "plant_id",
            "plant_name",
            "name",
            "line_type",
            "description",
            "status",
        ]
