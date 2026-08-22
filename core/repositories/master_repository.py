from core.models import Station, Vehicle, Route


class StationRepository:

    @staticmethod
    def get_by_id(station_id):
        return Station.objects.filter(
            station_id=station_id
        ).first()

    @staticmethod
    def get_all():
        return Station.objects.all()

    @staticmethod
    def get_ordered():
        return Station.objects.order_by("position")

    @staticmethod
    def create(**data):
        return Station.objects.create(**data)


class VehicleRepository:

    @staticmethod
    def get_by_id(vehicle_id):
        return Vehicle.objects.filter(
            vehicle_id=vehicle_id
        ).first()

    @staticmethod
    def get_by_status(status):
        return Vehicle.objects.filter(
            status=status
        )

    @staticmethod
    def get_by_variant(variant):
        return Vehicle.objects.filter(
            variant=variant
        )

    @staticmethod
    def get_recent_arrivals(start_time):
        return Vehicle.objects.filter(
            arrival_time__gte=start_time
        ).order_by("arrival_time")

    @staticmethod
    def create(**data):
        return Vehicle.objects.create(**data)


class RouteRepository:

    @staticmethod
    def get_all():
        return Route.objects.select_related(
            "station"
        ).order_by("sequence_number")

    @staticmethod
    def get_station_sequence():
        return (
            Route.objects
            .select_related("station")
            .order_by("sequence_number")
        )