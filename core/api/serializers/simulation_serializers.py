from rest_framework import serializers

from core.models import (
    SimulationRun,
    SimulationOutcome,
    Recommendation,
)


class RecommendationSerializer(
    serializers.ModelSerializer
):
    intervention_id = serializers.IntegerField(
        source="intervention.intervention_id",
        read_only=True,
    )

    intervention_name = serializers.CharField(
        source="intervention.name",
        read_only=True,
    )

    intervention_description = serializers.CharField(
        source="intervention.description",
        read_only=True,
    )

    class Meta:
        model = Recommendation

        fields = [
            "recommendation_id",
            "timestamp",
            "decision_score",
            "expected_throughput_gain",
            "expected_risk_reduction",
            "cost",
            "confidence",
            "status",
            "rationale",
            "intervention_id",
            "intervention_name",
            "intervention_description",
        ]


class SimulationOutcomeSerializer(
    serializers.ModelSerializer
):
    station_id = serializers.CharField(
        source="station.station_id",
        read_only=True,
    )

    station_name = serializers.CharField(
        source="station.name",
        read_only=True,
    )

    class Meta:
        model = SimulationOutcome

        fields = [
            "outcome_id",
            "station_id",
            "station_name",
            "simulated_throughput",
            "simulated_risk",
            "throughput_delta",
            "risk_delta",
            "is_bottleneck",
        ]


class SimulationRunSerializer(
    serializers.ModelSerializer
):
    plant_id = serializers.CharField(
        source="plant.plant_id",
        read_only=True,
        allow_null=True,
    )

    plant_name = serializers.CharField(
        source="plant.name",
        read_only=True,
        allow_null=True,
    )

    line_id = serializers.CharField(
        source="line.line_id",
        read_only=True,
        allow_null=True,
    )

    line_name = serializers.CharField(
        source="line.name",
        read_only=True,
        allow_null=True,
    )

    outcomes = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()

    class Meta:
        model = SimulationRun

        fields = [
            "simulation_id",
            "timestamp",
            "plant_id",
            "plant_name",
            "line_id",
            "line_name",
            "base_state_timestamp",
            "scenario_name",
            "scenario_type",
            "parameters",
            "horizon_minutes",
            "number_of_runs",
            "status",
            "outcomes",
            "recommendations",
        ]

    def get_outcomes(self, obj):
        outcomes = obj.outcomes.all()

        return SimulationOutcomeSerializer(
            outcomes,
            many=True,
        ).data

    def get_recommendations(self, obj):
        recs = obj.recommendations.all()

        return RecommendationSerializer(
            recs,
            many=True,
        ).data