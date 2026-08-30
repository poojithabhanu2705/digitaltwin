from core.repositories.simulation_repository import SimulationRepository
from core.services.exceptions import ValidationError


class SimulationDashboardService:
    """
    Read-only service for exposing persisted simulation runs
    and their outcomes to the API/dashboard.

    This service does NOT create or execute simulations.
    """

    def __init__(
        self,
        simulation_repository=SimulationRepository,
    ):
        self.simulation_repository = simulation_repository

    def get_recent_runs(self, limit=20):
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            raise ValidationError("limit must be an integer.")

        if limit < 1:
            raise ValidationError("limit must be greater than 0.")

        if limit > 100:
            limit = 100

        return self.simulation_repository.get_recent_runs(
            limit=limit
        )

    def get_run(self, simulation_id):
        run = self.simulation_repository.get_by_id(
            simulation_id
        )

        if run is None:
            from core.services.exceptions import NotFoundError

            raise NotFoundError(
                f"Simulation run {simulation_id} not found."
            )

        return run

    def get_outcomes(self, simulation_id):
        run = self.get_run(simulation_id)

        return self.simulation_repository.get_outcomes_for_run(
            run.simulation_id
        )