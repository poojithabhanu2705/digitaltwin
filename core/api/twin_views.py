from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from core.services.twin.twin_service import TwinService
from core.api.serializers.twin_serializers import TwinSnapshotSerializer, VehicleTwinSerializer
from core.services.exceptions import (
    NotFoundError,
    ValidationError,
    ServiceError,
)


class StationTwinView(APIView):
    def get(self, request, station_id):
        try:
            twin = TwinService().get_station_twin_with_vehicles(station_id)
            serializer = TwinSnapshotSerializer(twin)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except NotFoundError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except ServiceError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VehicleTwinView(APIView):
    def get(self, request, vehicle_id):
        try:
            twin = TwinService().get_vehicle_twin(vehicle_id)
            serializer = VehicleTwinSerializer(twin)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except NotFoundError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except ServiceError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

