from core.models import (
    RiskPrediction,
    PredictionExplanation,
)


class PredictionRepository:

    @staticmethod
    def get_latest(entity_type, entity_id, risk_type):
        return (
            RiskPrediction.objects
            .filter(
                entity_type=entity_type,
                entity_id=entity_id,
                risk_type=risk_type
            )
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_history(
        entity_type,
        entity_id,
        risk_type=None
    ):
        queryset = RiskPrediction.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        )

        if risk_type:
            queryset = queryset.filter(
                risk_type=risk_type
            )

        return queryset.order_by("-timestamp")

    @staticmethod
    def save_prediction(**data):
        return RiskPrediction.objects.create(**data)

    @staticmethod
    def save_explanation(**data):
        return PredictionExplanation.objects.create(**data)

    @staticmethod
    def get_explanations(prediction_id):
        return (
            PredictionExplanation.objects
            .filter(prediction_id=prediction_id)
            .order_by("-contribution")
        )