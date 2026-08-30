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

    POST /api/simulation/
    Run a new simulation.
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

    def post(self, request):
        try:
            line_id = request.data.get("line_id")
            if not line_id:
                raise ValidationError("line_id is required.")

            from core.models import ProductionLine, Station
            try:
                line = ProductionLine.objects.select_related("plant").get(line_id=line_id)
            except ProductionLine.DoesNotExist:
                raise NotFoundError(f"ProductionLine {line_id} not found.")

            plant_id = line.plant.plant_id if line.plant else None

            # Get target station parameters
            target_station_id = request.data.get("target_station_id")
            if target_station_id == "":
                target_station_id = None

            # Validate target station if provided
            if target_station_id:
                try:
                    Station.objects.get(station_id=target_station_id)
                except Station.DoesNotExist:
                    raise NotFoundError(f"Target station {target_station_id} not found.")

            capacity_modifier_input = request.data.get("capacity_modifier", 100)
            try:
                capacity_modifier = float(capacity_modifier_input)
            except (ValueError, TypeError):
                capacity_modifier = 100.0

            # Convert from percent (e.g. 120%) to multiplier (e.g. 1.2)
            if capacity_modifier > 3.0:
                capacity_modifier = capacity_modifier / 100.0

            risk_reduction_pct_input = request.data.get("risk_reduction_pct") or request.data.get("risk_reduction")
            if risk_reduction_pct_input is None:
                risk_reduction_pct = 0.0
            else:
                try:
                    risk_reduction_pct = float(risk_reduction_pct_input)
                except (ValueError, TypeError):
                    risk_reduction_pct = 0.0

            scenario_name = request.data.get("scenario_name", "Intervention Simulation")
            scenario_type = request.data.get("scenario_type", "INTERVENTION")
            horizon_minutes = int(request.data.get("horizon_minutes", 60))
            number_of_runs = int(request.data.get("number_of_runs", 1))

            # Retrieve base state timestamp
            from core.models import StationState
            latest_state = StationState.objects.filter(station__line_id=line_id).order_by("-timestamp").first()
            if latest_state:
                base_state_timestamp = latest_state.timestamp
            else:
                from django.utils import timezone
                base_state_timestamp = timezone.now()

            parameters = {}
            if target_station_id:
                parameters["target_station_id"] = target_station_id
                parameters["risk_reduction_pct"] = risk_reduction_pct
                parameters["capacity_modifier"] = capacity_modifier

            # Import repositories and service
            from core.services.simulation_service import SimulationService
            from core.repositories.simulation_repository import SimulationRepository
            from core.repositories.state_repository import StateRepository
            from core.repositories.risk_repository import RiskRepository

            service = SimulationService(
                StateRepository(),
                RiskRepository(),
                SimulationRepository()
            )

            run = service.simulate_scenario(
                plant_id=plant_id,
                line_id=line_id,
                base_state_timestamp=base_state_timestamp,
                scenario_name=scenario_name,
                scenario_type=scenario_type,
                parameters=parameters,
                horizon_minutes=horizon_minutes,
                number_of_runs=number_of_runs,
            )

            # Produce recommendations if applicable
            from core.services.decision.recommendation_service import RecommendationService
            from core.repositories.decision_repository import DecisionRepository
            from core.models import Intervention

            rec_service = RecommendationService(DecisionRepository(), SimulationRepository())

            if target_station_id:
                try:
                    station = Station.objects.get(station_id=target_station_id)
                    interventions = Intervention.objects.filter(applicable_station_type=station.station_type)
                except Exception:
                    interventions = Intervention.objects.all()
            else:
                interventions = Intervention.objects.all()

            candidates = [
                {"simulation_run_id": run.simulation_id, "intervention_id": interv.intervention_id}
                for interv in interventions
            ]
            if candidates:
                try:
                    rec_service.evaluate_and_recommend(candidates)
                except Exception:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.exception("Failed to generate recommendation after simulation")

            # Serialize output
            serializer = SimulationRunSerializer(run)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
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