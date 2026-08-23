from core.models import Intervention, Recommendation


class DecisionRepository:

    # ============================================================
    # INTERVENTIONS
    # ============================================================

    @staticmethod
    def get_interventions():
        return (
            Intervention.objects
            .order_by("name")
        )

    @staticmethod
    def get_intervention(intervention_id):
        return (
            Intervention.objects
            .filter(intervention_id=intervention_id)
            .first()
        )

    @staticmethod
    def get_interventions_by_type(intervention_type):
        return (
            Intervention.objects
            .filter(intervention_type=intervention_type)
            .order_by("name")
        )

    @staticmethod
    def get_interventions_for_station_type(
        station_type
    ):
        return (
            Intervention.objects
            .filter(
                applicable_station_type=station_type
            )
            .order_by("name")
        )

    @staticmethod
    def save_intervention(**data):
        return Intervention.objects.create(**data)

    # ============================================================
    # RECOMMENDATIONS
    # ============================================================

    @staticmethod
    def get_recommendation(recommendation_id):
        return (
            Recommendation.objects
            .select_related(
                "simulation",
                "intervention",
            )
            .filter(
                recommendation_id=recommendation_id
            )
            .first()
        )

    @staticmethod
    def save_recommendation(**data):
        return Recommendation.objects.create(**data)

    @staticmethod
    def bulk_save_recommendations(
        recommendations
    ):
        return Recommendation.objects.bulk_create(
            recommendations
        )

    # ============================================================
    # SIMULATION RECOMMENDATIONS
    # ============================================================

    @staticmethod
    def get_simulation_recommendations(
        simulation_id
    ):
        return (
            Recommendation.objects
            .filter(
                simulation_id=simulation_id
            )
            .select_related("intervention")
            .order_by("-decision_score")
        )

    @staticmethod
    def get_simulation_recommendations_latest_first(
        simulation_id
    ):
        return (
            Recommendation.objects
            .filter(
                simulation_id=simulation_id
            )
            .select_related("intervention")
            .order_by("-timestamp")
        )

    # ============================================================
    # RECOMMENDATION FILTERS
    # ============================================================

    @staticmethod
    def get_by_status(status):
        return (
            Recommendation.objects
            .select_related(
                "simulation",
                "intervention",
            )
            .filter(status=status)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_intervention(
        intervention_id
    ):
        return (
            Recommendation.objects
            .select_related("simulation")
            .filter(
                intervention_id=intervention_id
            )
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_time_range(
        start_time,
        end_time
    ):
        return (
            Recommendation.objects
            .select_related(
                "simulation",
                "intervention",
            )
            .filter(
                timestamp__gte=start_time,
                timestamp__lte=end_time,
            )
            .order_by("timestamp")
        )

    # ============================================================
    # TOP RECOMMENDATIONS
    # ============================================================

    @staticmethod
    def get_top_recommendations(
        limit=5
    ):
        return (
            Recommendation.objects
            .select_related("intervention")
            .order_by("-decision_score")[:limit]
        )

    @staticmethod
    def get_top_simulation_recommendations(
        simulation_id,
        limit=5
    ):
        return (
            Recommendation.objects
            .filter(
                simulation_id=simulation_id
            )
            .select_related("intervention")
            .order_by("-decision_score")[:limit]
        )