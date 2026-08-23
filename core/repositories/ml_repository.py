from core.models import (
    RiskPrediction,
    PredictionExplanation,
    RootCause,
    PredictionRootCause,
    PredictionOutcome,
)


class PredictionRepository:

    @staticmethod
    def get_by_id(prediction_id):
        return (
            RiskPrediction.objects
            .filter(prediction_id=prediction_id)
            .first()
        )

    @staticmethod
    def get_latest(
        entity_type,
        entity_id,
        risk_type,
    ):
        return (
            RiskPrediction.objects
            .filter(
                entity_type=entity_type,
                entity_id=entity_id,
                risk_type=risk_type,
            )
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_history(
        entity_type,
        entity_id,
        risk_type=None,
    ):
        queryset = RiskPrediction.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
        )

        if risk_type is not None:
            queryset = queryset.filter(
                risk_type=risk_type
            )

        return queryset.order_by("-timestamp")

    @staticmethod
    def get_by_risk_type(risk_type):
        return (
            RiskPrediction.objects
            .filter(risk_type=risk_type)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_model(
        model_name,
        model_version=None,
    ):
        queryset = RiskPrediction.objects.filter(
            model_name=model_name
        )

        if model_version is not None:
            queryset = queryset.filter(
                model_version=model_version
            )

        return queryset.order_by("-timestamp")

    @staticmethod
    def get_by_prediction_target(prediction_target):
        return (
            RiskPrediction.objects
            .filter(prediction_target=prediction_target)
            .order_by("-timestamp")
        )

    @staticmethod
    def save_prediction(**data):
        return RiskPrediction.objects.create(**data)

    @staticmethod
    def bulk_save_predictions(predictions):
        return RiskPrediction.objects.bulk_create(
            predictions
        )


class PredictionExplanationRepository:

    @staticmethod
    def get_by_id(explanation_id):
        return (
            PredictionExplanation.objects
            .select_related("prediction")
            .filter(id=explanation_id)
            .first()
        )

    @staticmethod
    def save_explanation(**data):
        return PredictionExplanation.objects.create(
            **data
        )

    @staticmethod
    def bulk_save_explanations(explanations):
        return PredictionExplanation.objects.bulk_create(
            explanations
        )

    @staticmethod
    def get_explanations(prediction_id):
        return (
            PredictionExplanation.objects
            .filter(prediction_id=prediction_id)
            .order_by("-contribution")
        )

    @staticmethod
    def get_by_feature(
        prediction_id,
        feature_name,
    ):
        return (
            PredictionExplanation.objects
            .filter(
                prediction_id=prediction_id,
                feature_name=feature_name,
            )
            .first()
        )


class RootCauseRepository:

    @staticmethod
    def get_by_id(root_cause_id):
        return (
            RootCause.objects
            .filter(root_cause_id=root_cause_id)
            .first()
        )

    @staticmethod
    def get_all():
        return (
            RootCause.objects
            .order_by("category", "name")
        )

    @staticmethod
    def get_by_category(category):
        return (
            RootCause.objects
            .filter(category=category)
            .order_by("name")
        )

    @staticmethod
    def get_by_name(
        category,
        name,
    ):
        return (
            RootCause.objects
            .filter(
                category=category,
                name=name,
            )
            .first()
        )

    @staticmethod
    def create(**data):
        return RootCause.objects.create(**data)

    @staticmethod
    def update(root_cause_id, **data):
        root_cause = (
            RootCause.objects
            .filter(root_cause_id=root_cause_id)
            .first()
        )

        if root_cause is None:
            return None

        for field, value in data.items():
            setattr(root_cause, field, value)

        root_cause.save()

        return root_cause


class PredictionRootCauseRepository:

    @staticmethod
    def get_by_id(link_id):
        return (
            PredictionRootCause.objects
            .select_related(
                "prediction",
                "root_cause",
            )
            .filter(id=link_id)
            .first()
        )

    @staticmethod
    def get_for_prediction(prediction_id):
        return (
            PredictionRootCause.objects
            .select_related("root_cause")
            .filter(prediction_id=prediction_id)
            .order_by("-contribution")
        )

    @staticmethod
    def get_by_root_cause(root_cause_id):
        return (
            PredictionRootCause.objects
            .select_related("prediction")
            .filter(root_cause_id=root_cause_id)
            .order_by("-contribution")
        )

    @staticmethod
    def get_link(
        prediction_id,
        root_cause_id,
    ):
        return (
            PredictionRootCause.objects
            .select_related(
                "prediction",
                "root_cause",
            )
            .filter(
                prediction_id=prediction_id,
                root_cause_id=root_cause_id,
            )
            .first()
        )

    @staticmethod
    def create(**data):
        return PredictionRootCause.objects.create(
            **data
        )

    @staticmethod
    def bulk_create(links):
        return PredictionRootCause.objects.bulk_create(
            links
        )


class PredictionOutcomeRepository:

    @staticmethod
    def get_by_id(outcome_id):
        return (
            PredictionOutcome.objects
            .select_related("prediction")
            .filter(outcome_id=outcome_id)
            .first()
        )

    @staticmethod
    def get_for_prediction(prediction_id):
        return (
            PredictionOutcome.objects
            .select_related("prediction")
            .filter(prediction_id=prediction_id)
            .first()
        )

    @staticmethod
    def get_by_outcome_type(outcome_type):
        return (
            PredictionOutcome.objects
            .filter(outcome_type=outcome_type)
            .order_by("-observed_at")
        )

    @staticmethod
    def get_by_observation_range(
        start_time,
        end_time,
    ):
        return (
            PredictionOutcome.objects
            .filter(
                observed_at__gte=start_time,
                observed_at__lte=end_time,
            )
            .order_by("observed_at")
        )

    @staticmethod
    def create(**data):
        return PredictionOutcome.objects.create(
            **data
        )

    @staticmethod
    def update(outcome_id, **data):
        outcome = (
            PredictionOutcome.objects
            .filter(outcome_id=outcome_id)
            .first()
        )

        if outcome is None:
            return None

        for field, value in data.items():
            setattr(outcome, field, value)

        outcome.save()

        return outcome