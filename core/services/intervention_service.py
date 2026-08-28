# decision/intervention_service.py

import logging
from django.utils import timezone
from django.db import transaction

from core.services.exceptions import (
    NotFoundError,
    ValidationError,
    ConflictError,
    InvalidStateTransitionError,
    ServiceError
)
from core.models import Recommendation, InterventionExecution

logger = logging.getLogger(__name__)


class InterventionService:
    """
    Manages the lifecycle and execution of recommended interventions 
    in the Digital Twin. Enforces state transitions and guarantees idempotency.
    """

    VALID_TRANSITIONS = {
        "PENDING": ["APPROVED", "REJECTED", "EXECUTED"],
        "APPROVED": ["EXECUTED", "REJECTED"],
        "EXECUTED": ["COMPLETED"],
        "REJECTED": [],
        "COMPLETED": []
    }

    def __init__(self, intervention_repository):
        self.repo = intervention_repository

    def approve_recommendation(self, recommendation_id: int, rationale: str = "") -> Recommendation:
        rec = self._get_and_validate_recommendation(recommendation_id)
        self._validate_transition(rec.status, "APPROVED")
        
        rec.status = "APPROVED"
        if rationale:
            rec.rationale = rationale
            
        return self.repo.save_recommendation(rec)

    def reject_recommendation(self, recommendation_id: int, rationale: str = "") -> Recommendation:
        rec = self._get_and_validate_recommendation(recommendation_id)
        self._validate_transition(rec.status, "REJECTED")
        
        rec.status = "REJECTED"
        if rationale:
            rec.rationale = rationale
            
        return self.repo.save_recommendation(rec)

    def execute_intervention(self, recommendation_id: int, execution_notes: str = "") -> InterventionExecution:
        """
        Executes a recommendation, locking its state and generating an execution record 
        for downstream OutcomeService observation.
        """
        rec = self._get_and_validate_recommendation(recommendation_id)

        if rec.status in ["EXECUTED", "COMPLETED"]:
            raise ConflictError(f"Recommendation {recommendation_id} has already been executed.")

        self._validate_transition(rec.status, "EXECUTED")

        execution = InterventionExecution(
            timestamp=timezone.now(),
            recommendation=rec,
            status="SUCCESS",
            execution_notes=execution_notes
        )

        rec.status = "EXECUTED"

        try:
            return self.repo.save_execution_transaction(rec, execution)
        except Exception as e:
            logger.error(f"Failed to persist intervention execution: {e}")
            raise ServiceError(f"Database error during execution persistence: {str(e)}")

    def _get_and_validate_recommendation(self, recommendation_id: int) -> Recommendation:
        if not recommendation_id:
            raise ValidationError("recommendation_id must be provided.")
            
        rec = self.repo.get_recommendation_by_id(recommendation_id)
        if not rec:
            raise NotFoundError(f"Recommendation '{recommendation_id}' was not found.")
        return rec

    def _validate_transition(self, current_status: str, target_status: str):
        allowed = self.VALID_TRANSITIONS.get(current_status, [])
        if target_status not in allowed:
            raise InvalidStateTransitionError(
                f"Cannot transition recommendation from '{current_status}' to '{target_status}'."
            )