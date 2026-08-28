import logging
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

class OutcomeService:
    """
    Evaluates ML predictions against actual production/quality events.
    Persists results to PredictionOutcome without modifying the original RiskPrediction.
    """

    def __init__(
        self,
        outcome_repository,
        risk_threshold=0.5
    ):
        self.outcome_repository = outcome_repository
        self.risk_threshold = risk_threshold

    def evaluate(
        self,
        prediction,
        actual_event,
        actual_event_occurred: bool,
        event_timestamp,
        entity_id: str
    ):
        """
        Evaluates a prediction against an actual event outcome.
        
        Args:
            prediction: The RiskPrediction instance.
            actual_event: The actual event model instance (e.g., QualityEvent, ProductionEvent).
            actual_event_occurred: Boolean indicating if the risk/defect actually manifested.
            event_timestamp: The datetime of the actual event.
            entity_id: The ID of the vehicle or station involved in the event.
        """
        self._validate_inputs(prediction, actual_event, event_timestamp)
        self._validate_entity(prediction, entity_id)
        
        lead_time = self._calculate_and_validate_horizon(prediction, event_timestamp)

        # Idempotency check: Return existing outcome if already evaluated
        existing_outcome = self.outcome_repository.get_for_prediction(prediction.prediction_id)
        if existing_outcome:
            logger.info(f"Outcome already exists for prediction {prediction.prediction_id}.")
            return existing_outcome

        # Evaluate correctness (TP / TN / FP / FN logic)
        predicted_positive = prediction.risk_score >= self.risk_threshold
        matched = (predicted_positive == actual_event_occurred)

        outcome_type = "TRUE_POSITIVE" if predicted_positive and actual_event_occurred else \
                       "TRUE_NEGATIVE" if not predicted_positive and not actual_event_occurred else \
                       "FALSE_POSITIVE" if predicted_positive and not actual_event_occurred else \
                       "FALSE_NEGATIVE"

        # Persist PredictionOutcome
        return self.outcome_repository.create(
            prediction=prediction,
            observed_at=event_timestamp,
            outcome_type=outcome_type,
            actual_outcome="EVENT_OCCURRED" if actual_event_occurred else "NO_EVENT",
            actual_value=1.0 if actual_event_occurred else 0.0,
            matched=matched,
            lead_time_minutes=lead_time
        )

    def _validate_inputs(self, prediction, actual_event, event_timestamp):
        if not prediction or not hasattr(prediction, 'prediction_id'):
            raise ValueError("A valid RiskPrediction must be provided.")
        if not actual_event:
            raise ValueError("An actual event must be provided for evaluation.")
        if not event_timestamp:
            raise ValueError("Event timestamp is required.")
        if not (0.0 <= prediction.risk_score <= 1.0):
            raise ValueError(f"Invalid prediction risk score: {prediction.risk_score}")

    def _validate_entity(self, prediction, event_entity_id):
        if str(prediction.entity_id) != str(event_entity_id):
            raise ValueError(
                f"Entity ID mismatch. Prediction entity: {prediction.entity_id}, "
                f"Event entity: {event_entity_id}"
            )

    def _calculate_and_validate_horizon(self, prediction, event_timestamp):
        if event_timestamp < prediction.timestamp:
            raise ValueError("Outcome timestamp cannot be earlier than prediction timestamp.")
        
        lead_time_td = event_timestamp - prediction.timestamp
        lead_time_minutes = lead_time_td.total_seconds() / 60.0

        if prediction.prediction_horizon_minutes is not None:
            if lead_time_minutes > prediction.prediction_horizon_minutes:
                raise ValueError(
                    f"Event occurred outside the prediction horizon. "
                    f"Lead time: {lead_time_minutes}m, Horizon: {prediction.prediction_horizon_minutes}m."
                )
                
        return lead_time_minutes