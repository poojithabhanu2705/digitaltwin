from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.models import SimulationRun
from core.api.serializers.simulation_serializers import (
    SimulationRunSerializer,
)
from core.services.exceptions import (
    NotFoundError,
    ValidationError,
    ServiceError,
)


def _handle_simulation_error(exc):
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


class SimulationListView(APIView):
    """
    GET /api/simulation/

    Return recent persisted simulation runs.
    """

    def get(self, request):
        try:
            limit = int(
                request.query_params.get("limit", 20)
            )

            if limit <= 0:
                raise ValidationError(
                    "limit must be greater than 0"
                )

            runs = (
                SimulationRun.objects
                .prefetch_related(
                    "outcomes",
                    "recommendations",
                )
                .select_related(
                    "plant",
                    "line",
                )
                .order_by("-timestamp")[:limit]
            )

            serializer = SimulationRunSerializer(
                runs,
                many=True,
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return _handle_simulation_error(exc)


class SimulationDetailView(APIView):
    """
    GET /api/simulation/<simulation_id>/

    Return one simulation run and its outcomes.
    """

    def get(self, request, simulation_id):
        try:
            try:
                run = (
                    SimulationRun.objects
                    .prefetch_related(
                        "outcomes",
                        "recommendations",
                    )
                    .select_related(
                        "plant",
                        "line",
                    )
                    .get(
                        simulation_id=simulation_id
                    )
                )
            except SimulationRun.DoesNotExist:
                raise NotFoundError(
                    f"Simulation {simulation_id} not found."
                )

            serializer = SimulationRunSerializer(run)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return _handle_simulation_error(exc)