"""
seed_line_states.py

Adds StationState records for L2-01 and L3-01 so that those lines
can participate in simulation scenarios.

This command is IDEMPOTENT: it checks whether states already exist
before creating them and does NOT delete or modify any existing data.

Run with:
    python manage.py seed_line_states
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import ProductionLine, Station, StationState


# Per-line baseline profile: (health_state, health_risk, throughput, utilization)
LINE_PROFILES = {
    "L2-01": {
        "health_state": "NOMINAL",
        "health_risk": 0.14,
        "confidence": 0.94,
        "wip": 2,
        "utilization": 0.81,
        "throughput": 68.0,
        "blocking_time": 1.4,
        "starvation_time": 1.0,
        "sensor_coverage": 1.0,
        "data_quality": 0.97,
        "instrumentation_status": "FULL",
    },
    "L3-01": {
        "health_state": "NOMINAL",
        "health_risk": 0.11,
        "confidence": 0.96,
        "wip": 2,
        "utilization": 0.77,
        "throughput": 70.0,
        "blocking_time": 1.1,
        "starvation_time": 0.9,
        "sensor_coverage": 1.0,
        "data_quality": 0.98,
        "instrumentation_status": "FULL",
    },
}

# One station in each secondary line is slightly degraded to make
# simulations interesting.
DEGRADED_STATION_SUFFIX = "S3"

DEGRADED_OVERRIDE = {
    "health_state": "DEGRADED",
    "health_risk": 0.62,
    "confidence": 0.88,
    "wip": 6,
    "utilization": 0.91,
    "throughput": 56.0,
    "blocking_time": 7.2,
    "starvation_time": 0.6,
    "sensor_coverage": 0.82,
    "data_quality": 0.93,
    "instrumentation_status": "PARTIAL",
}


class Command(BaseCommand):
    help = (
        "Add StationState records for L2-01 and L3-01 "
        "so that simulations can run against all production lines."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()

        for line_id, profile in LINE_PROFILES.items():
            try:
                line = ProductionLine.objects.get(line_id=line_id)
            except ProductionLine.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  Line {line_id} not found — skipping.")
                )
                continue

            stations = Station.objects.filter(line=line).order_by("position")

            if not stations.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"  Line {line_id} has no stations — skipping."
                    )
                )
                continue

            existing_count = StationState.objects.filter(
                station__line=line
            ).count()

            if existing_count > 0:
                self.stdout.write(
                    f"  {line_id}: {existing_count} states already exist — skipping."
                )
                continue

            created = 0
            for station in stations:
                is_degraded = station.station_id.endswith(DEGRADED_STATION_SUFFIX)
                fields = DEGRADED_OVERRIDE if is_degraded else profile

                StationState.objects.create(
                    timestamp=now,
                    station=station,
                    health_state=fields["health_state"],
                    health_risk=fields["health_risk"],
                    confidence=fields["confidence"],
                    wip=fields["wip"],
                    utilization=fields["utilization"],
                    throughput=fields["throughput"],
                    blocking_time=fields["blocking_time"],
                    starvation_time=fields["starvation_time"],
                    current_cycle_time=station.base_cycle_time * (
                        1.20 if is_degraded else 1.01
                    ),
                    sensor_coverage=fields["sensor_coverage"],
                    data_quality=fields["data_quality"],
                    instrumentation_status=fields["instrumentation_status"],
                )
                created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  {line_id}: created {created} StationState records."
                )
            )

        total = StationState.objects.count()
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Total StationState records in DB: {total}"
            )
        )
