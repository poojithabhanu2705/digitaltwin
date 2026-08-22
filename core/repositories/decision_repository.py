from core.models import Intervention, Recommendation


class DecisionRepository:

    @staticmethod
    def get_interventions():
        return Intervention.objects.all()

    @staticmethod
    def get_intervention(intervention_id):
        return (
            Intervention.objects
            .filter(intervention_id=intervention_id)
            .first()
        )

    @staticmethod
    def save_intervention(**data):
        return Intervention.objects.create(**data)

    @staticmethod
    def save_recommendation(**data):
        return Recommendation.objects.create(**data)

    @staticmethod
    def get_simulation_recommendations(simulation_id):
        return (
            Recommendation.objects
            .filter(simulation_id=simulation_id)
            .select_related("intervention")
            .order_by("-decision_score")
        )

    @staticmethod
    def get_top_recommendations(limit=5):
        return (
            Recommendation.objects
            .select_related("intervention")
            .order_by("-decision_score")[:limit]
        )