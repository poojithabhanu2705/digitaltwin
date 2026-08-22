from core.models import SimulationRun, SimulationResult


class SimulationRepository:

    @staticmethod
    def create_run(**data):
        return SimulationRun.objects.create(**data)

    @staticmethod
    def get_by_id(simulation_id):
        return (
            SimulationRun.objects
            .filter(simulation_id=simulation_id)
            .first()
        )

    @staticmethod
    def get_recent_runs(limit=20):
        return (
            SimulationRun.objects
            .order_by("-timestamp")[:limit]
        )

    @staticmethod
    def save_result(**data):
        return SimulationResult.objects.create(**data)

    @staticmethod
    def get_results(simulation_id):
        return (
            SimulationResult.objects
            .filter(simulation_id=simulation_id)
        )