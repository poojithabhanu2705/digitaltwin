from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.services.master.plant_service import PlantService
from core.services.master.production_structure_service import ProductionStructureService
from core.services.telemetry.telemetry_service import TelemetryService
from core.services.features.feature_service import FeatureService
from core.services.state.state_service import StateService

from core.services.exceptions import (
    NotFoundError,
    ValidationError,
    ServiceError,
)


def _handle_error(exc):
    if isinstance(exc, ValidationError):
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, NotFoundError):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    return Response(
        {"detail": str(exc)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class PlantListView(APIView):

    def get(self, request):
        try:
            return Response(
                PlantService().get_all_plants(),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class PlantDetailView(APIView):

    def get(self, request, plant_id):
        try:
            return Response(
                PlantService().get_plant(plant_id),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class LineListView(APIView):

    def get(self, request):
        try:
            return Response(
                ProductionStructureService().get_all_lines(),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class LineDetailView(APIView):

    def get(self, request, line_id):
        try:
            return Response(
                ProductionStructureService().get_line(line_id),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class StationListView(APIView):

    def get(self, request):
        try:
            return Response(
                ProductionStructureService().get_all_stations(),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class StationDetailView(APIView):

    def get(self, request, station_id):
        try:
            return Response(
                ProductionStructureService().get_station(station_id),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class LatestStationTelemetryView(APIView):

    def get(self, request, station_id):
        try:
            return Response(
                TelemetryService().get_latest_for_station(station_id),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class LatestVehicleTelemetryView(APIView):

    def get(self, request, vehicle_id):
        try:
            return Response(
                TelemetryService().get_latest_for_vehicle(vehicle_id),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class LatestStationFeatureView(APIView):

    def get(self, request, station_id):
        try:
            return Response(
                FeatureService().get_latest_station_feature(station_id),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class LatestVehicleFeatureView(APIView):

    def get(self, request, vehicle_id):
        try:
            return Response(
                FeatureService().get_latest_vehicle_feature(vehicle_id),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class LatestStationStateView(APIView):

    def get(self, request, station_id):
        try:
            return Response(
                StateService().get_latest_station_state(station_id),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class LatestVehicleStateView(APIView):

    def get(self, request, vehicle_id):
        try:
            return Response(
                StateService().get_latest_vehicle_state(vehicle_id),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)


class StationVehiclesView(APIView):

    def get(self, request, station_id):
        try:
            return Response(
                StateService().get_vehicles_at_station(station_id),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return _handle_error(exc)
