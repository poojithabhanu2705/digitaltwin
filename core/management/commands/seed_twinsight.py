from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import (
    Plant,
    ProductionLine,
    Station,
    Equipment,
    DataSource,
    Sensor,
    Vehicle,
    Route,
    Telemetry,
    ProductionEvent,
    VehicleStationHistory,
    ManualObservation,
    QualityEvent,
    MaintenanceEvent,
    StationFeature,
    VehicleFeature,
    StationState,
    VehicleState,
    RiskPrediction,
    PredictionExplanation,
    RootCause,
    PredictionRootCause,
    PredictionOutcome,
    StationDependency,
    VehicleExposure,
    SimulationRun,
    SimulationOutcome,
    Intervention,
    Recommendation,
    InterventionExecution,
)


class Command(BaseCommand):
    help = "Populate TwinSight with a coherent synthetic automotive factory."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Clearing existing TwinSight demo data...")

        # Delete in dependency-safe order.
        InterventionExecution.objects.all().delete()
        Recommendation.objects.all().delete()
        SimulationOutcome.objects.all().delete()
        SimulationRun.objects.all().delete()
        VehicleExposure.objects.all().delete()
        PredictionOutcome.objects.all().delete()
        PredictionRootCause.objects.all().delete()
        PredictionExplanation.objects.all().delete()
        RiskPrediction.objects.all().delete()
        RootCause.objects.all().delete()
        VehicleState.objects.all().delete()
        StationState.objects.all().delete()
        VehicleFeature.objects.all().delete()
        StationFeature.objects.all().delete()
        MaintenanceEvent.objects.all().delete()
        QualityEvent.objects.all().delete()
        ManualObservation.objects.all().delete()
        VehicleStationHistory.objects.all().delete()
        ProductionEvent.objects.all().delete()
        Telemetry.objects.all().delete()
        Route.objects.all().delete()
        Vehicle.objects.all().delete()
        Sensor.objects.all().delete()
        DataSource.objects.all().delete()
        Equipment.objects.all().delete()
        StationDependency.objects.all().delete()
        Station.objects.all().delete()
        ProductionLine.objects.all().delete()
        Plant.objects.all().delete()

        now = timezone.now()

        # ============================================================
        # 1. PLANTS
        # ============================================================

        plant_a = Plant.objects.create(
            plant_id="PLANT-01",
            name="Pune Vehicle Assembly",
            location="Pune, Maharashtra",
            timezone="Asia/Kolkata",
            status="ACTIVE",
        )

        plant_b = Plant.objects.create(
            plant_id="PLANT-02",
            name="Chennai Vehicle Assembly",
            location="Chennai, Tamil Nadu",
            timezone="Asia/Kolkata",
            status="ACTIVE",
        )

        # ============================================================
        # 2. PRODUCTION LINES
        # ============================================================

        lines = []

        for plant, prefix in [
            (plant_a, "L1"),
            (plant_a, "L2"),
            (plant_b, "L3"),
        ]:
            line = ProductionLine.objects.create(
                line_id=f"{prefix}-01",
                plant=plant,
                name=f"{plant.name} / Assembly Line {prefix[-1]}",
                line_type="AUTOMOTIVE_ASSEMBLY",
                description="Synthetic vehicle assembly production line.",
                status="ACTIVE",
            )
            lines.append(line)

        # Main demonstration line.
        main_line = lines[0]

        # ============================================================
        # 3. STATIONS
        # ============================================================

        station_specs = [
            ("S1", "Body Framing", "BODY_ASSEMBLY", 4, 42.0),
            ("S2", "Paint Preparation", "PAINT_PREP", 3, 47.0),
            ("S3", "Powertrain Fitment", "POWERTRAIN", 3, 51.0),
            ("S4", "Final Torque & Inspection", "INSPECTION", 2, 58.0),
            ("S5", "Wheel & Brake Assembly", "CHASSIS", 3, 46.0),
            ("S6", "Final Assembly", "FINAL_ASSEMBLY", 4, 43.0),
        ]

        stations = {}

        for sid, name, station_type, capacity, cycle in station_specs:
            instrumentation = "PARTIAL" if sid == "S4" else "FULL"

            stations[sid] = Station.objects.create(
                station_id=f"{main_line.line_id}-{sid}",
                line=main_line,
                name=name,
                station_type=station_type,
                capacity=capacity,
                base_cycle_time=cycle,
                position=int(sid[1:]),
                instrumentation_status=instrumentation,
                description=(
                    "Sensor-poor demonstration station with vibration sensor intentionally absent."
                    if sid == "S4"
                    else "Instrumented production station."
                ),
            )

        # Stations for secondary lines.
        for line_index, line in enumerate(lines[1:], start=2):
            for position in range(1, 7):
                sid = f"{line.line_id}-S{position}"
                Station.objects.create(
                    station_id=sid,
                    line=line,
                    name=f"Assembly Station {position}",
                    station_type="ASSEMBLY",
                    capacity=3,
                    base_cycle_time=44.0 + position,
                    position=position,
                    instrumentation_status="FULL",
                    description="Instrumented synthetic assembly station.",
                )

        # ============================================================
        # 4. ROUTE
        # ============================================================

        for position in range(1, 7):
            Route.objects.create(
                line=main_line,
                station=stations[f"S{position}"],
                sequence_number=position,
            )

        for line in lines[1:]:
            for station in Station.objects.filter(line=line).order_by("position"):
                Route.objects.create(
                    line=line,
                    station=station,
                    sequence_number=station.position,
                )

        # ============================================================
        # 5. STATION DEPENDENCIES
        # ============================================================

        for a, b, weight in [
            ("S1", "S2", 0.72),
            ("S2", "S3", 0.76),
            ("S3", "S4", 0.84),
            ("S4", "S5", 0.92),
            ("S5", "S6", 0.81),
        ]:
            StationDependency.objects.create(
                upstream_station=stations[a],
                downstream_station=stations[b],
                dependency_type="PROCESS",
                propagation_weight=weight,
                propagation_delay_minutes=2.0,
                confidence=0.94,
            )

        # ============================================================
        # 6. EQUIPMENT / DATA SOURCES / SENSORS
        # ============================================================

        equipment_by_station = {}

        for sid, station in stations.items():
            eq = Equipment.objects.create(
                equipment_id=f"EQ-{sid}",
                station=station,
                name=(
                    "Final Torque Controller"
                    if sid == "S4"
                    else f"{station.name} Controller"
                ),
                equipment_type=(
                    "TORQUE_CONTROLLER"
                    if sid == "S4"
                    else "ASSEMBLY_MACHINE"
                ),
                manufacturer="TwinSight Industrial",
                model_number=f"TS-{sid}-2026",
                installation_year=2022 if sid == "S4" else 2024,
                vintage_category="AGING" if sid == "S4" else "MODERN",
                status="ACTIVE",
            )

            equipment_by_station[sid] = eq

            source = DataSource.objects.create(
                source_id=f"DS-{sid}",
                plant=main_line.plant,
                line=main_line,
                station=station,
                equipment=eq,
                name=f"{station.name} PLC",
                source_type="PLC",
                connection_type="OPC-UA",
                protocol="OPC-UA",
                status="ACTIVE",
                metadata={"synthetic": True},
            )

            sensor_specs = [
                ("CYCLE", "cycle_time", "seconds"),
                ("TORQUE", "torque", "Nm"),
                ("TEMP", "temperature", "C"),
                ("ALARM", "alarm_count", "count"),
            ]

            # S4 intentionally has no vibration sensor.
            if sid != "S4":
                sensor_specs.append(("VIB", "vibration", "mm/s"))

            for suffix, measurement, unit in sensor_specs:
                Sensor.objects.create(
                    sensor_id=f"SNS-{sid}-{suffix}",
                    equipment=eq,
                    data_source=source,
                    name=f"{station.name} {measurement.replace('_', ' ').title()}",
                    sensor_type="INDUSTRIAL",
                    measurement_type=measurement,
                    unit=unit,
                    sampling_rate=1.0,
                    installation_date=timezone.now().date(),
                    status="ACTIVE",
                    is_required=measurement in ("cycle_time", "torque"),
                )

        # ============================================================
        # 7. VEHICLES
        # ============================================================

        variants = ["Sedan", "SUV", "Hatchback"]

        vehicles = []

        for i in range(1, 31):
            vehicle = Vehicle.objects.create(
                vehicle_id=f"VH-{i:04d}",
                line=main_line,
                variant=variants[(i - 1) % len(variants)],
                production_order=f"PO-{2026:04d}-{i:05d}",
                arrival_time=now - timedelta(minutes=(31 - i) * 18),
                completion_time=None,
                status="ACTIVE" if i > 5 else "COMPLETED",
            )
            vehicles.append(vehicle)

        # ============================================================
        # 8. TELEMETRY + PRODUCTION EVENTS + GENEALOGY
        # ============================================================

        main_stations = list(
            Station.objects.filter(line=main_line).order_by("position")
        )

        telemetry_rows = []
        production_rows = []
        history_rows = []

        for vehicle_index, vehicle in enumerate(vehicles):
            vehicle_start = now - timedelta(minutes=(30 - vehicle_index) * 18)

            for position, station in enumerate(main_stations, start=1):
                ts = vehicle_start + timedelta(minutes=(position - 1) * 4)

                # Controlled S4 degradation.
                degradation = (
                    max(0.0, (vehicle_index - 8) / 30.0)
                    if station.station_id.endswith("S4")
                    else 0.0
                )

                cycle = station.base_cycle_time * (1.0 + 0.30 * degradation)
                torque = 100.0 + 8.0 * degradation
                temperature = 65.0 + 10.0 * degradation
                vibration = None if station.station_id.endswith("S4") else (
                    1.8 + 2.5 * degradation
                )

                telemetry_rows.append(
                    Telemetry(
                        timestamp=ts,
                        station=station,
                        vehicle=vehicle,
                        equipment=equipment_by_station.get(
                            station.station_id.split("-")[-1]
                        ),
                        cycle_time=cycle,
                        torque=torque,
                        temperature=temperature,
                        vibration=vibration,
                        throughput=max(0.1, 3600.0 / cycle),
                        machine_state="DEGRADED" if degradation > 0.15 else "RUNNING",
                        alarm_count=2 if degradation > 0.20 else 0,
                        data_quality="VALID",
                        is_imputed=False,
                    )
                )

                production_rows.append(
                    ProductionEvent(
                        timestamp=ts,
                        vehicle=vehicle,
                        station=station,
                        event_type="STATION_COMPLETED",
                        cycle_time=cycle,
                        quantity=1,
                        status="COMPLETED",
                    )
                )

                exit_time = ts + timedelta(seconds=cycle)

                history_rows.append(
                    VehicleStationHistory(
                        vehicle=vehicle,
                        station=station,
                        sequence_number=position,
                        entry_time=ts,
                        exit_time=exit_time,
                        cycle_time=cycle,
                        visit_type="NORMAL",
                    )
                )

        Telemetry.objects.bulk_create(telemetry_rows, batch_size=500)
        ProductionEvent.objects.bulk_create(production_rows, batch_size=500)
        VehicleStationHistory.objects.bulk_create(history_rows, batch_size=500)

        # ============================================================
        # 9. MANUAL OBSERVATIONS
        # ============================================================

        ManualObservation.objects.create(
            timestamp=now - timedelta(hours=1),
            station=stations["S4"],
            vehicle=vehicles[-1],
            data_source=DataSource.objects.get(source_id="DS-S4"),
            operator_reference="OP-104",
            check_type="TORQUE_CHECK",
            parameter="Torque consistency",
            value="Elevated deviation observed",
            status="FLAGGED",
            notes="Operator observed inconsistent torque behavior.",
        )

        # ============================================================
        # 10. QUALITY EVENTS
        # ============================================================

        quality_events = []

        for i, vehicle in enumerate(vehicles[-8:], start=1):
            quality_events.append(
                QualityEvent(
                    timestamp=now - timedelta(minutes=i * 7),
                    vehicle=vehicle,
                    station=stations["S4"],
                    origin_station=stations["S4"],
                    detection_station=stations["S6"],
                    defect_flag=True,
                    defect_type="TORQUE_VARIATION",
                    defect_severity="MAJOR" if i <= 3 else "MINOR",
                    rework_flag=i <= 5,
                    scrap_flag=False,
                    inspection_method="FINAL_INSPECTION",
                    notes="Synthetic quality event linked to S4 degradation scenario.",
                )
            )

        QualityEvent.objects.bulk_create(quality_events)

        # ============================================================
        # 11. MAINTENANCE
        # ============================================================

        MaintenanceEvent.objects.create(
            timestamp=now - timedelta(hours=3),
            station=stations["S4"],
            equipment=equipment_by_station["S4"],
            data_source=DataSource.objects.get(source_id="DS-S4"),
            maintenance_type="CORRECTIVE",
            failure_type="TORQUE_DRIFT",
            duration=42.0,
            status="COMPLETED",
            notes="Torque controller recalibration performed.",
        )

        MaintenanceEvent.objects.create(
            timestamp=now - timedelta(days=2),
            station=stations["S2"],
            equipment=equipment_by_station["S2"],
            data_source=DataSource.objects.get(source_id="DS-S2"),
            maintenance_type="PREVENTIVE",
            failure_type=None,
            duration=25.0,
            status="COMPLETED",
            notes="Scheduled preventive maintenance.",
        )

        # ============================================================
        # 12. STATION FEATURES
        # ============================================================

        for station in main_stations:
            degraded = station.station_id.endswith("S4")

            StationFeature.objects.create(
                timestamp=now,
                station=station,
                avg_cycle_time=(
                    station.base_cycle_time * 1.24
                    if degraded
                    else station.base_cycle_time * 1.02
                ),
                cycle_time_std=8.7 if degraded else 2.8,
                cycle_time_trend=0.18 if degraded else 0.01,
                avg_torque=108.5 if degraded else 100.4,
                torque_deviation=8.4 if degraded else 1.7,
                temperature_mean=74.5 if degraded else 65.8,
                vibration_mean=None if degraded else 2.1,
                alarm_rate=0.21 if degraded else 0.025,
                utilization=0.93 if degraded else 0.79,
                throughput=54.0 if degraded else 71.0,
                wip=8.0 if degraded else 3.0,
                blocking_time=9.5 if degraded else 1.2,
                starvation_time=0.8 if degraded else 1.1,
                sensor_coverage_ratio=0.78 if degraded else 1.0,
                data_completeness=0.91 if degraded else 0.98,
                imputation_ratio=0.09 if degraded else 0.02,
                manual_observation_count=1 if degraded else 0,
            )

        # ============================================================
        # 13. VEHICLE FEATURES
        # ============================================================

        for vehicle in vehicles:
            exposed = vehicle in vehicles[-8:]

            VehicleFeature.objects.create(
                timestamp=now,
                vehicle=vehicle,
                variant=vehicle.variant,
                avg_cycle_time=58.0 if exposed else 47.0,
                cycle_time_deviation=0.21 if exposed else 0.03,
                torque_deviation=8.1 if exposed else 1.2,
                stations_exposed=4 if exposed else 6,
                degraded_station_count=1 if exposed else 0,
                cumulative_risk=0.76 if exposed else 0.12,
                quality_event_count=1 if exposed else 0,
                manual_observation_count=1 if exposed else 0,
            )

        # ============================================================
        # 14. CURRENT STATION STATES
        # ============================================================

        for station in main_stations:
            degraded = station.station_id.endswith("S4")

            StationState.objects.create(
                timestamp=now,
                station=station,
                health_state="DEGRADED" if degraded else "NOMINAL",
                health_risk=0.86 if degraded else 0.12,
                confidence=0.91 if degraded else 0.97,
                wip=8 if degraded else 2,
                utilization=0.93 if degraded else 0.79,
                throughput=54.0 if degraded else 71.0,
                blocking_time=9.5 if degraded else 1.2,
                starvation_time=0.8 if degraded else 1.1,
                current_cycle_time=72.0 if degraded else station.base_cycle_time,
                sensor_coverage=0.78 if degraded else 1.0,
                data_quality=0.91 if degraded else 0.98,
                instrumentation_status="PARTIAL" if degraded else "FULL",
            )

        # ============================================================
        # 15. CURRENT VEHICLE STATES
        # ============================================================

        for i, vehicle in enumerate(vehicles):
            current_station = main_stations[min(i % 6, 5)]

            VehicleState.objects.create(
                timestamp=now,
                vehicle=vehicle,
                current_station=current_station,
                status=vehicle.status,
                quality_risk=0.76 if vehicle in vehicles[-8:] else 0.11,
                confidence=0.88 if vehicle in vehicles[-8:] else 0.96,
                risk_source="STATION_EXPOSURE" if vehicle in vehicles[-8:] else "",
            )

        # ============================================================
        # 16. RISK PREDICTION
        # ============================================================

        prediction = RiskPrediction.objects.create(
            timestamp=now,
            entity_type="STATION",
            entity_id=stations["S4"].station_id,
            risk_type="DEGRADATION",
            prediction_target="STATION_HEALTH",
            risk_score=0.86,
            confidence=0.91,
            prediction_horizon_minutes=60,
            model_name="station_risk_model",
            model_version="1.0.0",
        )

        # ============================================================
        # 17. EXPLANATIONS
        # ============================================================

        PredictionExplanation.objects.bulk_create([
            PredictionExplanation(
                prediction=prediction,
                feature_name="cycle_time_trend",
                contribution=0.34,
                direction="POSITIVE",
            ),
            PredictionExplanation(
                prediction=prediction,
                feature_name="torque_deviation",
                contribution=0.27,
                direction="POSITIVE",
            ),
            PredictionExplanation(
                prediction=prediction,
                feature_name="alarm_rate",
                contribution=0.18,
                direction="POSITIVE",
            ),
            PredictionExplanation(
                prediction=prediction,
                feature_name="utilization",
                contribution=0.11,
                direction="POSITIVE",
            ),
        ])

        # ============================================================
        # 18. ROOT CAUSES
        # ============================================================

        torque_root = RootCause.objects.create(
            category="EQUIPMENT",
            name="Torque controller degradation",
            description="Increasing torque deviation is consistent with controller degradation.",
        )

        process_root = RootCause.objects.create(
            category="PROCESS",
            name="Cycle-time degradation",
            description="Increasing cycle time is creating downstream production pressure.",
        )

        PredictionRootCause.objects.bulk_create([
            PredictionRootCause(
                prediction=prediction,
                root_cause=torque_root,
                contribution=0.52,
                confidence=0.90,
                evidence="Torque deviation increased while S4 cycle time also trended upward.",
            ),
            PredictionRootCause(
                prediction=prediction,
                root_cause=process_root,
                contribution=0.31,
                confidence=0.86,
                evidence="S4 cycle time is materially above its baseline.",
            ),
        ])

        # ============================================================
        # 19. VEHICLE EXPOSURE
        # ============================================================

        exposure_rows = []

        for vehicle in vehicles[-8:]:
            exposure_rows.append(
                VehicleExposure(
                    timestamp=now,
                    vehicle=vehicle,
                    station=stations["S4"],
                    source_prediction=prediction,
                    station_risk=0.86,
                    exposure_weight=0.90,
                    propagated_risk=0.77,
                    exposure_start_time=now - timedelta(minutes=20),
                    exposure_end_time=now,
                )
            )

        VehicleExposure.objects.bulk_create(exposure_rows)

        # ============================================================
        # 20. SIMULATION
        # ============================================================

        simulation = SimulationRun.objects.create(
            timestamp=now,
            plant=plant_a,
            line=main_line,
            base_state_timestamp=now,
            scenario_name="S4 Torque Controller Maintenance",
            scenario_type="WHAT_IF",
            parameters={
                "target_station": stations["S4"].station_id,
                "maintenance": True,
                "cycle_time_reduction": 0.18,
            },
            horizon_minutes=60,
            number_of_runs=100,
            status="COMPLETED",
        )

        for station in main_stations:
            is_s4 = station.station_id.endswith("S4")

            SimulationOutcome.objects.create(
                simulation_run=simulation,
                station=station,
                simulated_throughput=(
                    65.0 if is_s4 else 72.0
                ),
                simulated_risk=(
                    0.31 if is_s4 else 0.10
                ),
                throughput_delta=(
                    11.0 if is_s4 else 1.0
                ),
                risk_delta=(
                    -0.55 if is_s4 else -0.02
                ),
                is_bottleneck=is_s4,
            )

        # ============================================================
        # 21. INTERVENTIONS
        # ============================================================

        maintenance_intervention = Intervention.objects.create(
            name="Recalibrate S4 Torque Controller",
            description="Perform corrective recalibration of the degraded S4 torque controller.",
            intervention_type="MAINTENANCE",
            applicable_station_type="INSPECTION",
            cost=Decimal("4200.00"),
            disruption_level=0.18,
            estimated_duration_minutes=45,
        )

        operator_intervention = Intervention.objects.create(
            name="Add Temporary S4 Operator",
            description="Add temporary operator capacity to stabilize the degraded station.",
            intervention_type="OPERATOR",
            applicable_station_type="INSPECTION",
            cost=Decimal("1800.00"),
            disruption_level=0.05,
            estimated_duration_minutes=120,
        )

        Recommendation.objects.create(
            timestamp=now,
            simulation=simulation,
            intervention=maintenance_intervention,
            decision_score=0.91,
            expected_throughput_gain=11.0,
            expected_risk_reduction=0.55,
            cost=Decimal("4200.00"),
            confidence=0.90,
            status="PENDING",
            rationale="Highest risk reduction with acceptable disruption and strong simulated throughput recovery.",
        )

        Recommendation.objects.create(
            timestamp=now,
            simulation=simulation,
            intervention=operator_intervention,
            decision_score=0.73,
            expected_throughput_gain=6.0,
            expected_risk_reduction=0.28,
            cost=Decimal("1800.00"),
            confidence=0.84,
            status="PENDING",
            rationale="Lower-cost fallback option with smaller risk reduction.",
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("TwinSight database populated successfully."))
        self.stdout.write("")
        self.stdout.write(f"Plants:             {Plant.objects.count()}")
        self.stdout.write(f"Lines:              {ProductionLine.objects.count()}")
        self.stdout.write(f"Stations:            {Station.objects.count()}")
        self.stdout.write(f"Equipment:           {Equipment.objects.count()}")
        self.stdout.write(f"Sensors:             {Sensor.objects.count()}")
        self.stdout.write(f"Vehicles:            {Vehicle.objects.count()}")
        self.stdout.write(f"Telemetry:           {Telemetry.objects.count()}")
        self.stdout.write(f"Production events:   {ProductionEvent.objects.count()}")
        self.stdout.write(f"Quality events:      {QualityEvent.objects.count()}")
        self.stdout.write(f"Maintenance events:  {MaintenanceEvent.objects.count()}")
        self.stdout.write(f"Station features:    {StationFeature.objects.count()}")
        self.stdout.write(f"Vehicle features:    {VehicleFeature.objects.count()}")
        self.stdout.write(f"Station states:      {StationState.objects.count()}")
        self.stdout.write(f"Vehicle states:      {VehicleState.objects.count()}")
        self.stdout.write(f"Risk predictions:    {RiskPrediction.objects.count()}")
        self.stdout.write(f"Simulations:         {SimulationRun.objects.count()}")
        self.stdout.write(f"Recommendations:     {Recommendation.objects.count()}")
