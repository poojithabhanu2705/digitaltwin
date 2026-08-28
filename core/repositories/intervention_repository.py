# decision/intervention_repository.py

from django.db import transaction
from core.models import Recommendation, InterventionExecution

class InterventionRepository:
    def get_recommendation_by_id(self, recommendation_id: int):
        return Recommendation.objects.filter(recommendation_id=recommendation_id).first()

    def save_recommendation(self, recommendation: Recommendation) -> Recommendation:
        recommendation.save()
        return recommendation

    @transaction.atomic
    def save_execution_transaction(
        self, 
        recommendation: Recommendation, 
        execution: InterventionExecution
    ) -> InterventionExecution:
        recommendation.save()
        execution.save()
        return execution