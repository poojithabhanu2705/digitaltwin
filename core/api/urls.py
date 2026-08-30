from django.urls import path

from core.api.twin_views import (
    StationTwinView,
    VehicleTwinView,
)

from core.api.views.twin_views import (
    StationTwinWithVehiclesView,
)

from core.api.views.domain_views import (
    PlantListView,
    PlantDetailView,
    LineListView,
    LineDetailView,
    StationListView,
    StationDetailView,
    LatestStationTelemetryView,
    LatestVehicleTelemetryView,
    LatestStationFeatureView,
    LatestVehicleFeatureView,
    LatestStationStateView,
    LatestVehicleStateView,
    StationVehiclesView,
)

from core.api.views.risk_views import (
    RiskListView,
)

from core.api.views.simulation_views import (
    SimulationListView,
    SimulationDetailView,
)


urlpatterns = [

    # ============================================================
    # MASTER / PRODUCTION STRUCTURE
    # ============================================================

    path(
        "plants/",
        PlantListView.as_view(),
        name="plant-list",
    ),

    path(
        "plants/<str:plant_id>/",
        PlantDetailView.as_view(),
        name="plant-detail",
    ),

    path(
        "lines/",
        LineListView.as_view(),
        name="line-list",
    ),

    path(
        "lines/<str:line_id>/",
        LineDetailView.as_view(),
        name="line-detail",
    ),

    path(
        "stations/",
        StationListView.as_view(),
        name="station-list",
    ),

    path(
        "stations/<str:station_id>/",
        StationDetailView.as_view(),
        name="station-detail",
    ),

    # ============================================================
    # TELEMETRY
    # ============================================================

    path(
        "stations/<str:station_id>/telemetry/latest/",
        LatestStationTelemetryView.as_view(),
        name="station-telemetry-latest",
    ),

    path(
        "vehicles/<str:vehicle_id>/telemetry/latest/",
        LatestVehicleTelemetryView.as_view(),
        name="vehicle-telemetry-latest",
    ),

    # ============================================================
    # FEATURES
    # ============================================================

    path(
        "stations/<str:station_id>/features/latest/",
        LatestStationFeatureView.as_view(),
        name="station-feature-latest",
    ),

    path(
        "vehicles/<str:vehicle_id>/features/latest/",
        LatestVehicleFeatureView.as_view(),
        name="vehicle-feature-latest",
    ),

    # ============================================================
    # DIGITAL TWIN STATE
    # ============================================================

    path(
        "stations/<str:station_id>/state/latest/",
        LatestStationStateView.as_view(),
        name="station-state-latest",
    ),

    path(
        "vehicles/<str:vehicle_id>/state/latest/",
        LatestVehicleStateView.as_view(),
        name="vehicle-state-latest",
    ),

    # ============================================================
    # VEHICLE / STATION RELATIONSHIP
    # ============================================================

    path(
        "stations/<str:station_id>/vehicles/",
        StationVehiclesView.as_view(),
        name="station-vehicles",
    ),

    # ============================================================
    # DIGITAL TWIN
    # ============================================================

    path(
        "twin/stations/<str:station_id>/",
        StationTwinView.as_view(),
        name="station-twin",
    ),

    path(
        "twin/vehicles/<str:vehicle_id>/",
        VehicleTwinView.as_view(),
        name="vehicle-twin",
    ),

    path(
        "twin/stations/<str:station_id>/vehicles/",
        StationTwinWithVehiclesView.as_view(),
        name="station-twin-with-vehicles",
    ),

    # ============================================================
    # RISK
    # ============================================================

    path(
        "risks/",
        RiskListView.as_view(),
        name="risk-list",
    ),

    # ============================================================
    # SIMULATION
    # ============================================================

    path(
        "simulation/",
        SimulationListView.as_view(),
        name="simulation-list",
    ),

    path(
        "simulation/<int:simulation_id>/",
        SimulationDetailView.as_view(),
        name="simulation-detail",
    ),
]