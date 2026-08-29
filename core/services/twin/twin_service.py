from core.services.exceptions import (
    NotFoundError,
    ValidationError,
)

from core.services.master.production_structure_service import (
    ProductionStructureService,
)
from core.services.telemetry.telemetry_service import (
    TelemetryService,
)
from core.services.features.feature_service import (
    FeatureService,
)
from core.services.state.state_service import (
    StateService,
)


class TwinService:
    """
    Orchestrates the current Digital Twin view of the production system.

    TwinService does not own persistence. It composes information from
    existing domain services:

        ProductionStructureService
        TelemetryService
        FeatureService
        StateService

    The service provides a unified snapshot for stations and vehicles.
    """

    def __init__(
        self,
        production_structure_service=None,
        telemetry_service=None,
        feature_service=None,
        state_service=None,
    ):
        self.production_structure_service = (
            production_structure_service
            or ProductionStructureService()
        )
        self.telemetry_service = (
            telemetry_service
            or TelemetryService()
        )
        self.feature_service = (
            feature_service
            or FeatureService()
        )
        self.state_service = (
            state_service
            or StateService()
        )

    # ============================================================
    # STATION TWIN
    # ============================================================

    def get_station_twin(self, station_id):
        """
        Return the current digital-twin snapshot for a station.

        The snapshot combines:
            - station master data
            - latest station state
            - latest station features
            - latest station telemetry
        """

        if not station_id:
            raise ValidationError("station_id is required.")

        station = self.production_structure_service.get_station(
            station_id
        )

        state = self._get_optional(
            self.state_service.get_latest_station_state,
            station_id,
        )

        feature = self._get_optional(
            self.feature_service.get_latest_station_feature,
            station_id,
        )

        telemetry = self._get_optional(
            self.telemetry_service.get_latest_for_station,
            station_id,
        )

        return {
            "station": station,
            "state": state,
            "features": feature,
            "telemetry": telemetry,
        }

    # ============================================================
    # VEHICLE TWIN
    # ============================================================

    def get_vehicle_twin(self, vehicle_id):
        """
        Return the current digital-twin snapshot for a vehicle.

        The snapshot combines:
            - latest vehicle state
            - latest vehicle features
            - latest vehicle telemetry
        """

        if not vehicle_id:
            raise ValidationError("vehicle_id is required.")

        state = self._get_optional(
            self.state_service.get_latest_vehicle_state,
            vehicle_id,
        )

        feature = self._get_optional(
            self.feature_service.get_latest_vehicle_feature,
            vehicle_id,
        )

        telemetry = self._get_optional(
            self.telemetry_service.get_latest_for_vehicle,
            vehicle_id,
        )

        # A vehicle twin cannot be meaningfully identified without
        # any current vehicle information.
        if state is None and feature is None and telemetry is None:
            raise NotFoundError(
                f"No twin data found for vehicle '{vehicle_id}'."
            )

        return {
            "vehicle_id": vehicle_id,
            "state": state,
            "features": feature,
            "telemetry": telemetry,
        }

    # ============================================================
    # STATION / VEHICLE RELATIONSHIP
    # ============================================================

    def get_station_vehicles(self, station_id):
        """
        Return the vehicles currently associated with a station.
        """

        if not station_id:
            raise ValidationError("station_id is required.")

        # Validate that the station exists first.
        self.production_structure_service.get_station(station_id)

        return self.state_service.get_vehicles_at_station(
            station_id
        )

    # ============================================================
    # COMPLETE STATION TWIN
    # ============================================================

    def get_station_twin_with_vehicles(self, station_id):
        """
        Return a station twin together with its current vehicles.
        """

        twin = self.get_station_twin(station_id)

        vehicles = self.get_station_vehicles(station_id)

        twin["vehicles"] = [
            self.get_vehicle_twin(vehicle.vehicle_id)
            for vehicle in vehicles
        ]

        return twin

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    @staticmethod
    def _get_optional(method, identifier):
        """
        Call a service getter while treating missing current data
        as an acceptable state for a digital-twin snapshot.
        """

        try:
            return method(identifier)
        except NotFoundError:
            return None