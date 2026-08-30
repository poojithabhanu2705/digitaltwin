from rest_framework import serializers

from core.models import (
    RiskPrediction,
    PredictionExplanation,
    PredictionRootCause,
    PredictionOutcome,
)


class PredictionExplanationSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = PredictionExplanation

        fields = [
            "id",
            "feature_name",
            "contribution",
            "direction",
        ]


class PredictionRootCauseSerializer(
    serializers.ModelSerializer
):
    root_cause_id = serializers.IntegerField(
        source="root_cause.root_cause_id",
        read_only=True,
    )

    category = serializers.CharField(
        source="root_cause.category",
        read_only=True,
    )

    name = serializers.CharField(
        source="root_cause.name",
        read_only=True,
    )

    description = serializers.CharField(
        source="root_cause.description",
        read_only=True,
    )

    class Meta:
        model = PredictionRootCause

        fields = [
            "id",
            "root_cause_id",
            "category",
            "name",
            "description",
            "contribution",
            "confidence",
            "evidence",
        ]


class PredictionOutcomeSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = PredictionOutcome

        fields = [
            "outcome_id",
            "observed_at",
            "outcome_type",
            "actual_outcome",
            "actual_value",
            "matched",
            "lead_time_minutes",
            "notes",
        ]


class RiskPredictionSerializer(
    serializers.ModelSerializer
):
    explanations = PredictionExplanationSerializer(
        many=True,
        read_only=True,
    )

    root_causes = PredictionRootCauseSerializer(
        many=True,
        read_only=True,
    )

    outcome = PredictionOutcomeSerializer(
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = RiskPrediction

        fields = [
            "prediction_id",
            "timestamp",
            "entity_type",
            "entity_id",
            "risk_type",
            "prediction_target",
            "risk_score",
            "confidence",
            "prediction_horizon_minutes",
            "model_name",
            "model_version",
            "explanations",
            "root_causes",
            "outcome",
        ]