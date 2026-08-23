from core.models import SimulationRun


class SimulationRepository:

    # ============================================================
    # BASIC RETRIEVAL
    # ============================================================

    @staticmethod
    def get_by_id(simulation_id):
        return (
            SimulationRun.objects
            .select_related(
                "plant",
                "line",
            )
            .filter(simulation_id=simulation_id)
            .first()
        )

    @staticmethod
    def create_run(**data):
        return SimulationRun.objects.create(**data)

    # ============================================================
    # RECENT / LATEST RUNS
    # ============================================================

    @staticmethod
    def get_recent_runs(limit=20):
        return (
            SimulationRun.objects
            .select_related(
                "plant",
                "line",
            )
            .order_by("-timestamp")[:limit]
        )

    @staticmethod
    def get_latest_run_for_plant(plant_id):
        return (
            SimulationRun.objects
            .select_related("line")
            .filter(plant_id=plant_id)
            .order_by("-timestamp")
            .first()
        )

    @staticmethod
    def get_latest_run_for_line(line_id):
        return (
            SimulationRun.objects
            .select_related("plant")
            .filter(line_id=line_id)
            .order_by("-timestamp")
            .first()
        )

    # ============================================================
    # HISTORY
    # ============================================================

    @staticmethod
    def get_plant_runs(
        plant_id,
        start_time=None,
        end_time=None,
    ):
        queryset = (
            SimulationRun.objects
            .filter(plant_id=plant_id)
        )

        if start_time is not None:
            queryset = queryset.filter(
                timestamp__gte=start_time
            )

        if end_time is not None:
            queryset = queryset.filter(
                timestamp__lte=end_time
            )

        return (
            queryset
            .select_related("line")
            .order_by("-timestamp")
        )

    @staticmethod
    def get_line_runs(
        line_id,
        start_time=None,
        end_time=None,
    ):
        queryset = (
            SimulationRun.objects
            .filter(line_id=line_id)
        )

        if start_time is not None:
            queryset = queryset.filter(
                timestamp__gte=start_time
            )

        if end_time is not None:
            queryset = queryset.filter(
                timestamp__lte=end_time
            )

        return (
            queryset
            .select_related("plant")
            .order_by("-timestamp")
        )

    # ============================================================
    # SCENARIO QUERIES
    # ============================================================

    @staticmethod
    def get_by_scenario_type(scenario_type):
        return (
            SimulationRun.objects
            .select_related(
                "plant",
                "line",
            )
            .filter(
                scenario_type=scenario_type
            )
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_scenario_name(scenario_name):
        return (
            SimulationRun.objects
            .select_related(
                "plant",
                "line",
            )
            .filter(
                scenario_name=scenario_name
            )
            .order_by("-timestamp")
        )

    @staticmethod
    def get_by_status(status):
        return (
            SimulationRun.objects
            .select_related(
                "plant",
                "line",
            )
            .filter(status=status)
            .order_by("-timestamp")
        )

    # ============================================================
    # BASE STATE / EXECUTION QUERIES
    # ============================================================

    @staticmethod
    def get_runs_from_base_state(
        base_state_timestamp,
    ):
        return (
            SimulationRun.objects
            .select_related(
                "plant",
                "line",
            )
            .filter(
                base_state_timestamp=base_state_timestamp
            )
            .order_by("-timestamp")
        )

    @staticmethod
    def get_runs_with_horizon(
        minimum_horizon_minutes,
    ):
        return (
            SimulationRun.objects
            .select_related(
                "plant",
                "line",
            )
            .filter(
                horizon_minutes__gte=minimum_horizon_minutes
            )
            .order_by("-timestamp")
        )