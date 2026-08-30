from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.services.ml.risk_dashboard_service import (
    RiskDashboardService,
)
from core.api.serializers.risk_serializers import (
    RiskPredictionSerializer,
)
from core.services.exceptions import (
    NotFoundError,
    ValidationError,
    ServiceError,
)


def _handle_risk_error(exc):
    if isinstance(exc, ValidationError):
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, NotFoundError):
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, ServiceError):
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {"detail": str(exc)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class RiskListView(APIView):
    """
    GET /risks/

    Return recent operational risk predictions.
    """

    def get(self, request):
        try:
            limit = request.query_params.get(
                "limit",
                50,
            )

            predictions = (
                RiskDashboardService()
                .get_recent_predictions(limit)
            )

            serializer = RiskPredictionSerializer(
                predictions,
                many=True,
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return _handle_risk_error(exc)