from itertools import chain

from core.repositories.ml_repository import PredictionRepository
from core.services.exceptions import ValidationError


class RiskDashboardService:
    """
    Read-only service used by the API/dashboard layer to expose
    recent operational risk predictions.

    No ML inference happens here.
    Predictions are already persisted by PredictionService.
    """

    def __init__(
        self,
        prediction_repository=PredictionRepository,
    ):
        self.prediction_repository = prediction_repository

    def get_recent_predictions(self, limit=50):
        """
        Return the most recent BOTTLENECK and DEFECT predictions.
        """

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            raise ValidationError("limit must be an integer.")

        if limit < 1:
            raise ValidationError("limit must be greater than 0.")

        if limit > 100:
            limit = 100

        bottleneck_predictions = list(
            self.prediction_repository.get_by_risk_type(
                "BOTTLENECK"
            )
        )

        defect_predictions = list(
            self.prediction_repository.get_by_risk_type(
                "DEFECT"
            )
        )

        predictions = list(
            chain(
                bottleneck_predictions,
                defect_predictions,
            )
        )

        predictions.sort(
            key=lambda prediction: prediction.timestamp,
            reverse=True,
        )

        return predictions[:limit]