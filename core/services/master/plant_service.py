from core.repositories.master_repository import PlantRepository
from core.services.exceptions import NotFoundError


class PlantService:

    def __init__(self, plant_repository=PlantRepository):
        self.plant_repository = plant_repository

    def create_plant(self, **data):
        """
        Create a new plant.

        Business validation will be added here only where required
        by the Plant model/problem statement.
        """
        return self.plant_repository.create(**data)

    def get_plant(self, plant_id):
        """
        Retrieve a plant by ID.

        Raises:
            NotFoundError: If the plant does not exist.
        """
        plant = self.plant_repository.get_by_id(plant_id)

        if plant is None:
            raise NotFoundError(
                f"Plant '{plant_id}' was not found."
            )

        return plant

    def get_all_plants(self):
        """Retrieve all plants."""
        return self.plant_repository.get_all()

    def get_plants_by_status(self, status):
        """Retrieve plants filtered by status."""
        return self.plant_repository.get_by_status(status)

    def update_plant(self, plant_id, **data):
        """
        Update an existing plant.

        Raises:
            NotFoundError: If the plant does not exist.
        """
        plant = self.plant_repository.update(
            plant_id,
            **data,
        )

        if plant is None:
            raise NotFoundError(
                f"Plant '{plant_id}' was not found."
            )

        return plant