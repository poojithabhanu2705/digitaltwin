from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.services.master.plant_service import PlantService
from core.services.master.production_structure_service import (
    ProductionStructureService,
)
from core.services.telemetry.telemetry_service import TelemetryService
from core.services.features.feature_service import FeatureService
from core.services.state.state_service import StateService

from core.services.exceptions import (
    NotFoundError,
    ValidationError,
    ServiceError,
)


# ============================================================
# ERROR HANDLING
# ============================================================

def _handle_error(exc):
    """
    Convert Service Layer exceptions into HTTP responses.

    Service Layer
        |
        +-- ValidationError -> 400 Bad Request
        |
        +-- NotFoundError   -> 404 Not Found
        |
        +-- ServiceError    -> 500 Internal Server Error
        |
        +-- unexpected      -> 500 Internal Server Error
    """

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

    # Defensive fallback for unexpected exceptions.
    return Response(
        {"detail": str(exc)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# ============================================================
# PLANT
# ============================================================

class PlantListView(APIView):
    """
    GET /plants/

    Return all plants.
    """

    def get(self, request):
        try:
            return Response(
                PlantService().get_all_plants(),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


class PlantDetailView(APIView):
    """
    GET /plants/<plant_id>/

    Return a single plant.
    """

    def get(self, request, plant_id):
        try:
            return Response(
                PlantService().get_plant(plant_id),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


# ============================================================
# PRODUCTION STRUCTURE
# ============================================================

class LineListView(APIView):
    """
    GET /lines/

    Return all production lines.
    """

    def get(self, request):
        try:
            return Response(
                ProductionStructureService().get_all_lines(),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


class LineDetailView(APIView):
    """
    GET /lines/<line_id>/

    Return a single production line.
    """

    def get(self, request, line_id):
        try:
            return Response(
                ProductionStructureService().get_line(line_id),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


class StationListView(APIView):
    """
    GET /stations/

    Return all stations.
    """

    def get(self, request):
        try:
            return Response(
                ProductionStructureService().get_all_stations(),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


class StationDetailView(APIView):
    """
    GET /stations/<station_id>/

    Return a single station.
    """

    def get(self, request, station_id):
        try:
            return Response(
                ProductionStructureService().get_station(station_id),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


# ============================================================
# TELEMETRY
# ============================================================

class LatestStationTelemetryView(APIView):
    """
    GET /stations/<station_id>/telemetry/latest/

    Return the latest telemetry record for a station.
    """

    def get(self, request, station_id):
        try:
            return Response(
                TelemetryService().get_latest_for_station(station_id),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


class LatestVehicleTelemetryView(APIView):
    """
    GET /vehicles/<vehicle_id>/telemetry/latest/

    Return the latest telemetry record for a vehicle.
    """

    def get(self, request, vehicle_id):
        try:
            return Response(
                TelemetryService().get_latest_for_vehicle(vehicle_id),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


# ============================================================
# FEATURES
# ============================================================

class LatestStationFeatureView(APIView):
    """
    GET /stations/<station_id>/features/latest/

    Return the latest feature record for a station.
    """

    def get(self, request, station_id):
        try:
            return Response(
                FeatureService().get_latest_station_feature(station_id),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


class LatestVehicleFeatureView(APIView):
    """
    GET /vehicles/<vehicle_id>/features/latest/

    Return the latest feature record for a vehicle.
    """

    def get(self, request, vehicle_id):
        try:
            return Response(
                FeatureService().get_latest_vehicle_feature(vehicle_id),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


# ============================================================
# DIGITAL TWIN STATE
# ============================================================

class LatestStationStateView(APIView):
    """
    GET /stations/<station_id>/state/latest/

    Return the latest state for a station.
    """

    def get(self, request, station_id):
        try:
            return Response(
                StateService().get_latest_station_state(station_id),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


class LatestVehicleStateView(APIView):
    """
    GET /vehicles/<vehicle_id>/state/latest/

    Return the latest state for a vehicle.
    """

    def get(self, request, vehicle_id):
        try:
            return Response(
                StateService().get_latest_vehicle_state(vehicle_id),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)


# ============================================================
# VEHICLE / STATION RELATIONSHIP
# ============================================================

class StationVehiclesView(APIView):
    """
    GET /stations/<station_id>/vehicles/

    Return vehicles currently associated with a station.
    """

    def get(self, request, station_id):
        try:
            return Response(
                StateService().get_vehicles_at_station(station_id),
                status=status.HTTP_200_OK,
            )
        except (ValidationError, NotFoundError, ServiceError) as exc:
            return _handle_error(exc)