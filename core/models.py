from django.db import models


# ============================================================
# 1. PLANT / LINE / MASTER DATA
# ============================================================


class Plant(models.Model):
    plant_id = models.CharField(
        max_length=30,
        primary_key=True
    )

    name = models.CharField(max_length=100)

    location = models.CharField(
        max_length=200,
        blank=True
    )

    timezone = models.CharField(
        max_length=50,
        default="UTC"
    )

    status = models.CharField(
        max_length=30,
        default="ACTIVE"
    )

    class Meta:
        db_table = "plants"
        ordering = ["name"]

    def __str__(self):
        return f"{self.plant_id} - {self.name}"


class ProductionLine(models.Model):
    line_id = models.CharField(
        max_length=30,
        primary_key=True
    )

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name="production_lines"
    )

    name = models.CharField(max_length=100)

    line_type = models.CharField(
        max_length=50,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=30,
        default="ACTIVE"
    )

    class Meta:
        db_table = "production_lines"
        ordering = ["plant", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["plant", "name"],
                name="unique_line_name_per_plant"
            )
        ]

    def __str__(self):
        return f"{self.plant.plant_id} - {self.name}"


class Station(models.Model):
    station_id = models.CharField(
        max_length=30,
        primary_key=True
    )

    line = models.ForeignKey(
        ProductionLine,
        on_delete=models.CASCADE,
        related_name="stations"
    )

    name = models.CharField(max_length=100)

    station_type = models.CharField(
        max_length=50
    )

    capacity = models.PositiveIntegerField()

    base_cycle_time = models.FloatField()

    position = models.PositiveIntegerField()

    instrumentation_status = models.CharField(
        max_length=30,
        default="PARTIAL"
    )

    description = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "stations"
        ordering = ["line", "position"]

        constraints = [
            models.UniqueConstraint(
                fields=["line", "position"],
                name="unique_station_position_per_line"
            ),
            models.UniqueConstraint(
                fields=["line", "name"],
                name="unique_station_name_per_line"
            )
        ]

    def __str__(self):
        return f"{self.station_id} - {self.name}"


class Equipment(models.Model):
    equipment_id = models.CharField(
        max_length=50,
        primary_key=True
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="equipment"
    )

    name = models.CharField(
        max_length=100
    )

    equipment_type = models.CharField(
        max_length=50
    )

    manufacturer = models.CharField(
        max_length=100,
        blank=True
    )

    model_number = models.CharField(
        max_length=100,
        blank=True
    )

    installation_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    vintage_category = models.CharField(
        max_length=30,
        default="MODERN"
    )

    status = models.CharField(
        max_length=30,
        default="ACTIVE"
    )

    class Meta:
        db_table = "equipment"
        ordering = ["station", "name"]

    def __str__(self):
        return f"{self.equipment_id} - {self.name}"


class DataSource(models.Model):
    source_id = models.CharField(
        max_length=50,
        primary_key=True
    )

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name="data_sources",
        null=True,
        blank=True
    )

    line = models.ForeignKey(
        ProductionLine,
        on_delete=models.CASCADE,
        related_name="data_sources",
        null=True,
        blank=True
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="data_sources",
        null=True,
        blank=True
    )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="data_sources",
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100
    )

    source_type = models.CharField(
        max_length=40
    )

    connection_type = models.CharField(
        max_length=50,
        blank=True
    )

    protocol = models.CharField(
        max_length=50,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        default="ACTIVE"
    )

    metadata = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = "data_sources"
        ordering = ["name"]

    def __str__(self):
        return f"{self.source_id} - {self.name}"


class Sensor(models.Model):
    sensor_id = models.CharField(
        max_length=50,
        primary_key=True
    )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="sensors"
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="sensors",
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100
    )

    sensor_type = models.CharField(
        max_length=50
    )

    measurement_type = models.CharField(
        max_length=50
    )

    unit = models.CharField(
        max_length=30,
        blank=True
    )

    sampling_rate = models.FloatField(
        null=True,
        blank=True
    )

    installation_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        default="ACTIVE"
    )

    is_required = models.BooleanField(
        default=False
    )

    class Meta:
        db_table = "sensors"
        ordering = ["equipment", "name"]

    def __str__(self):
        return f"{self.sensor_id} - {self.name}"


class Vehicle(models.Model):
    vehicle_id = models.CharField(
        max_length=50,
        primary_key=True
    )

    line = models.ForeignKey(
        ProductionLine,
        on_delete=models.CASCADE,
        related_name="vehicles"
    )

    variant = models.CharField(
        max_length=50
    )

    production_order = models.CharField(
        max_length=100
    )

    arrival_time = models.DateTimeField(
        db_index=True
    )

    completion_time = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=30
    )

    class Meta:
        db_table = "vehicles"

    def __str__(self):
        return self.vehicle_id


class Route(models.Model):
    route_id = models.BigAutoField(
        primary_key=True
    )

    line = models.ForeignKey(
        ProductionLine,
        on_delete=models.CASCADE,
        related_name="routes"
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="routes"
    )

    sequence_number = models.PositiveIntegerField()

    class Meta:
        db_table = "routes"
        ordering = ["line", "sequence_number"]

        constraints = [
            models.UniqueConstraint(
                fields=["line", "sequence_number"],
                name="unique_route_sequence_per_line"
            ),
            models.UniqueConstraint(
                fields=["line", "station"],
                name="unique_route_station_per_line"
            )
        ]

    def __str__(self):
        return (
            f"{self.line.line_id} - "
            f"{self.sequence_number}: "
            f"{self.station.station_id}"
        )


# ============================================================
# 2. RAW / EVENT DATA
# ============================================================


class Telemetry(models.Model):
    telemetry_id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="telemetry"
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="telemetry",
        null=True,
        blank=True
    )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        related_name="telemetry",
        null=True,
        blank=True
    )

    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.SET_NULL,
        related_name="telemetry",
        null=True,
        blank=True
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="telemetry",
        null=True,
        blank=True
    )

    cycle_time = models.FloatField(
        null=True,
        blank=True
    )

    torque = models.FloatField(
        null=True,
        blank=True
    )

    temperature = models.FloatField(
        null=True,
        blank=True
    )

    vibration = models.FloatField(
        null=True,
        blank=True
    )

    throughput = models.FloatField(
        null=True,
        blank=True
    )

    machine_state = models.CharField(
        max_length=30,
        blank=True
    )

    alarm_count = models.PositiveIntegerField(
        default=0
    )

    data_quality = models.CharField(
        max_length=30,
        default="VALID"
    )

    is_imputed = models.BooleanField(
        default=False
    )

    class Meta:
        db_table = "telemetry"

        indexes = [
            models.Index(
                fields=["station", "timestamp"],
                name="telemetry_station_time_idx"
            ),
            models.Index(
                fields=["vehicle", "timestamp"],
                name="telemetry_vehicle_time_idx"
            ),
            models.Index(
                fields=["equipment", "timestamp"],
                name="telemetry_equipment_time_idx"
            ),
            models.Index(
                fields=["data_source", "timestamp"],
                name="telemetry_source_time_idx"
            )
        ]


class ProductionEvent(models.Model):
    event_id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="production_events"
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="production_events"
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="production_events",
        null=True,
        blank=True
    )

    event_type = models.CharField(
        max_length=30
    )

    cycle_time = models.FloatField(
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    status = models.CharField(
        max_length=30,
        blank=True
    )

    class Meta:
        db_table = "production_events"

        indexes = [
            models.Index(
                fields=["station", "timestamp"],
                name="prod_event_station_time_idx"
            ),
            models.Index(
                fields=["vehicle", "timestamp"],
                name="prod_event_vehicle_time_idx"
            )
        ]


class VehicleStationHistory(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="station_history"
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="vehicle_history"
    )

    sequence_number = models.PositiveIntegerField()

    entry_time = models.DateTimeField(
        db_index=True
    )

    exit_time = models.DateTimeField(
        null=True,
        blank=True
    )

    cycle_time = models.FloatField(
        null=True,
        blank=True
    )

    visit_type = models.CharField(
        max_length=30,
        default="NORMAL"
    )

    class Meta:
        db_table = "vehicle_station_history"

        indexes = [
            models.Index(
                fields=["vehicle", "entry_time"],
                name="vhist_vehicle_time_idx"
            ),
            models.Index(
                fields=["station", "entry_time"],
                name="vhist_station_time_idx"
            )
        ]


class ManualObservation(models.Model):
    observation_id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="manual_observations"
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        related_name="manual_observations",
        null=True,
        blank=True
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="manual_observations",
        null=True,
        blank=True
    )

    operator_reference = models.CharField(
        max_length=100,
        blank=True
    )

    check_type = models.CharField(
        max_length=50
    )

    parameter = models.CharField(
        max_length=100
    )

    value = models.CharField(
        max_length=255,
        blank=True
    )

    status = models.CharField(
        max_length=30
    )

    notes = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "manual_observations"

        indexes = [
            models.Index(
                fields=["station", "timestamp"],
                name="manual_obs_station_time_idx"
            ),
            models.Index(
                fields=["vehicle", "timestamp"],
                name="manual_obs_vehicle_time_idx"
            )
        ]


class QualityEvent(models.Model):
    quality_event_id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="quality_events"
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        related_name="quality_events",
        null=True,
        blank=True
    )

    origin_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        related_name="originated_quality_events",
        null=True,
        blank=True
    )

    detection_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        related_name="detected_quality_events",
        null=True,
        blank=True
    )

    defect_flag = models.BooleanField(
        default=False
    )

    defect_type = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    defect_severity = models.CharField(
        max_length=30,
        null=True,
        blank=True
    )

    rework_flag = models.BooleanField(
        default=False
    )

    scrap_flag = models.BooleanField(
        default=False
    )

    inspection_method = models.CharField(
        max_length=50,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "quality_events"

        indexes = [
            models.Index(
                fields=["vehicle", "timestamp"],
                name="quality_vehicle_time_idx"
            ),
            models.Index(
                fields=["station", "timestamp"],
                name="quality_station_time_idx"
            ),
            models.Index(
                fields=["defect_type", "timestamp"],
                name="quality_defect_time_idx"
            )
        ]


class MaintenanceEvent(models.Model):
    maintenance_id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="maintenance_events"
    )

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.SET_NULL,
        related_name="maintenance_events",
        null=True,
        blank=True
    )

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        related_name="maintenance_events",
        null=True,
        blank=True
    )

    maintenance_type = models.CharField(
        max_length=50
    )

    failure_type = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    duration = models.FloatField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        default="COMPLETED"
    )

    notes = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "maintenance_events"

        indexes = [
            models.Index(
                fields=["station", "timestamp"],
                name="maintenance_station_time_idx"
            ),
            models.Index(
                fields=["equipment", "timestamp"],
                name="maintenance_equipment_time_idx"
            )
        ]


# ============================================================
# 3. FEATURE DATA
# ============================================================


class StationFeature(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="features"
    )

    avg_cycle_time = models.FloatField(
        null=True,
        blank=True
    )

    cycle_time_std = models.FloatField(
        null=True,
        blank=True
    )

    cycle_time_trend = models.FloatField(
        null=True,
        blank=True
    )

    avg_torque = models.FloatField(
        null=True,
        blank=True
    )

    torque_deviation = models.FloatField(
        null=True,
        blank=True
    )

    temperature_mean = models.FloatField(
        null=True,
        blank=True
    )

    vibration_mean = models.FloatField(
        null=True,
        blank=True
    )

    alarm_rate = models.FloatField(
        default=0.0
    )

    utilization = models.FloatField(
        default=0.0
    )

    throughput = models.FloatField(
        default=0.0
    )

    wip = models.FloatField(
        default=0.0
    )

    blocking_time = models.FloatField(
        default=0.0
    )

    starvation_time = models.FloatField(
        default=0.0
    )

    sensor_coverage_ratio = models.FloatField(
        default=0.0
    )

    data_completeness = models.FloatField(
        default=0.0
    )

    imputation_ratio = models.FloatField(
        default=0.0
    )

    manual_observation_count = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        db_table = "station_features"

        indexes = [
            models.Index(
                fields=["station", "timestamp"],
                name="station_feature_time_idx"
            )
        ]


class VehicleFeature(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="features"
    )

    variant = models.CharField(
        max_length=50
    )

    avg_cycle_time = models.FloatField(
        null=True,
        blank=True
    )

    cycle_time_deviation = models.FloatField(
        null=True,
        blank=True
    )

    torque_deviation = models.FloatField(
        null=True,
        blank=True
    )

    stations_exposed = models.PositiveIntegerField(
        default=0
    )

    degraded_station_count = models.PositiveIntegerField(
        default=0
    )

    cumulative_risk = models.FloatField(
        default=0.0
    )

    quality_event_count = models.PositiveIntegerField(
        default=0
    )

    manual_observation_count = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        db_table = "vehicle_features"

        indexes = [
            models.Index(
                fields=["vehicle", "timestamp"],
                name="vehicle_feature_time_idx"
            )
        ]


# ============================================================
# 4. DIGITAL TWIN STATE
# ============================================================


class StationState(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="states"
    )

    health_state = models.CharField(
        max_length=30
    )

    health_risk = models.FloatField(
        default=0.0
    )

    confidence = models.FloatField(
        default=0.0
    )

    wip = models.PositiveIntegerField(
        default=0
    )

    utilization = models.FloatField(
        default=0.0
    )

    throughput = models.FloatField(
        default=0.0
    )

    blocking_time = models.FloatField(
        default=0.0
    )

    starvation_time = models.FloatField(
        default=0.0
    )

    current_cycle_time = models.FloatField(
        null=True,
        blank=True
    )

    sensor_coverage = models.FloatField(
        default=0.0
    )

    data_quality = models.FloatField(
        default=0.0
    )

    instrumentation_status = models.CharField(
        max_length=30,
        default="PARTIAL"
    )

    class Meta:
        db_table = "station_state"

        indexes = [
            models.Index(
                fields=["station", "timestamp"],
                name="station_state_time_idx"
            )
        ]


class VehicleState(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="states"
    )

    current_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_vehicle_states"
    )

    status = models.CharField(
        max_length=30
    )

    quality_risk = models.FloatField(
        default=0.0
    )

    confidence = models.FloatField(
        default=0.0
    )

    risk_source = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        db_table = "vehicle_state"

        indexes = [
            models.Index(
                fields=["vehicle", "timestamp"],
                name="vehicle_state_time_idx"
            )
        ]


# ============================================================
# 5. ML / PREDICTION DATA
# ============================================================


class RiskPrediction(models.Model):
    prediction_id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    entity_type = models.CharField(
        max_length=20
    )

    entity_id = models.CharField(
        max_length=100
    )

    risk_type = models.CharField(
        max_length=50
    )

    prediction_target = models.CharField(
        max_length=100,
        blank=True
    )

    risk_score = models.FloatField()

    confidence = models.FloatField()

    prediction_horizon_minutes = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    model_name = models.CharField(
        max_length=100
    )

    model_version = models.CharField(
        max_length=50
    )

    class Meta:
        db_table = "risk_predictions"

        indexes = [
            models.Index(
                fields=["entity_type", "entity_id", "timestamp"],
                name="risk_entity_time_idx"
            ),
            models.Index(
                fields=["risk_type", "timestamp"],
                name="risk_type_time_idx"
            )
        ]


class PredictionExplanation(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    prediction = models.ForeignKey(
        RiskPrediction,
        on_delete=models.CASCADE,
        related_name="explanations"
    )

    feature_name = models.CharField(
        max_length=100
    )

    contribution = models.FloatField()

    direction = models.CharField(
        max_length=20,
        default="POSITIVE"
    )

    class Meta:
        db_table = "prediction_explanations"

        indexes = [
            models.Index(
                fields=["prediction", "feature_name"],
                name="prediction_feature_idx"
            )
        ]


# ============================================================
# 6. ROOT CAUSE ANALYSIS
# ============================================================


class RootCause(models.Model):
    root_cause_id = models.BigAutoField(
        primary_key=True
    )

    category = models.CharField(
        max_length=50
    )

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "root_causes"

        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"],
                name="unique_root_cause"
            )
        ]

    def __str__(self):
        return self.name


class PredictionRootCause(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    prediction = models.ForeignKey(
        RiskPrediction,
        on_delete=models.CASCADE,
        related_name="root_causes"
    )

    root_cause = models.ForeignKey(
        RootCause,
        on_delete=models.CASCADE,
        related_name="prediction_links"
    )

    contribution = models.FloatField()

    confidence = models.FloatField()

    evidence = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "prediction_root_causes"

        constraints = [
            models.UniqueConstraint(
                fields=["prediction", "root_cause"],
                name="unique_prediction_root_cause"
            )
        ]


class PredictionOutcome(models.Model):
    outcome_id = models.BigAutoField(
        primary_key=True
    )

    prediction = models.OneToOneField(
        RiskPrediction,
        on_delete=models.CASCADE,
        related_name="outcome"
    )

    observed_at = models.DateTimeField(
        db_index=True
    )

    outcome_type = models.CharField(
        max_length=50
    )

    actual_outcome = models.CharField(
        max_length=100
    )

    actual_value = models.FloatField(
        null=True,
        blank=True
    )

    matched = models.BooleanField(
        null=True,
        blank=True
    )

    lead_time_minutes = models.FloatField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "prediction_outcomes"

        indexes = [
            models.Index(
                fields=["outcome_type", "observed_at"],
                name="prediction_outcome_type_idx"
            )
        ]


# ============================================================
# 7. RISK PROPAGATION
# ============================================================


class StationDependency(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    upstream_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="downstream_dependencies"
    )

    downstream_station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="upstream_dependencies"
    )

    dependency_type = models.CharField(
        max_length=40,
        default="PROCESS"
    )

    propagation_weight = models.FloatField()

    propagation_delay_minutes = models.FloatField(
        null=True,
        blank=True
    )

    confidence = models.FloatField(
        default=0.0
    )

    class Meta:
        db_table = "station_dependencies"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "upstream_station",
                    "downstream_station"
                ],
                name="unique_station_dependency"
            )
        ]


class VehicleExposure(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="exposures"
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="vehicle_exposures"
    )

    source_prediction = models.ForeignKey(
        RiskPrediction,
        on_delete=models.SET_NULL,
        related_name="vehicle_exposures",
        null=True,
        blank=True
    )

    station_risk = models.FloatField()

    exposure_weight = models.FloatField()

    propagated_risk = models.FloatField()

    exposure_start_time = models.DateTimeField(
        null=True,
        blank=True
    )

    exposure_end_time = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = "vehicle_exposure"

        indexes = [
            models.Index(
                fields=["vehicle", "timestamp"],
                name="exposure_vehicle_time_idx"
            ),
            models.Index(
                fields=["station", "timestamp"],
                name="exposure_station_time_idx"
            )
        ]


# ============================================================
# 8. SIMULATION
# ============================================================


class SimulationRun(models.Model):
    simulation_id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    plant = models.ForeignKey(
        Plant,
        on_delete=models.SET_NULL,
        related_name="simulation_runs",
        null=True,
        blank=True
    )

    line = models.ForeignKey(
        ProductionLine,
        on_delete=models.SET_NULL,
        related_name="simulation_runs",
        null=True,
        blank=True
    )

    base_state_timestamp = models.DateTimeField()

    scenario_name = models.CharField(
        max_length=100
    )

    scenario_type = models.CharField(
        max_length=50,
        default="WHAT_IF"
    )

    parameters = models.JSONField(
        default=dict,
        blank=True
    )

    horizon_minutes = models.PositiveIntegerField()

    number_of_runs = models.PositiveIntegerField()

    status = models.CharField(
        max_length=30,
        default="COMPLETED"
    )

    class Meta:
        db_table = "simulation_runs"

        indexes = [
            models.Index(
                fields=["line", "timestamp"],
                name="sim_line_time_idx"
            ),
            models.Index(
                fields=["plant", "timestamp"],
                name="sim_plant_time_idx"
            )
        ]
class SimulationOutcome(models.Model):
    outcome_id = models.BigAutoField(
        primary_key=True
    )

    simulation_run = models.ForeignKey(
        SimulationRun,
        on_delete=models.CASCADE,
        related_name="outcomes"
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="simulation_outcomes"
    )

    simulated_throughput = models.FloatField()
    
    simulated_risk = models.FloatField()
    
    throughput_delta = models.FloatField()
    
    risk_delta = models.FloatField()

    is_bottleneck = models.BooleanField(
        default=False
    )

    class Meta:
        db_table = "simulation_outcomes"
        indexes = [
            models.Index(
                fields=["simulation_run", "station"],
                name="sim_outcome_run_station_idx"
            )
        ]




# ============================================================
# 9. DECISION ENGINE
# ============================================================


class Intervention(models.Model):
    intervention_id = models.BigAutoField(
        primary_key=True
    )

    name = models.CharField(
        max_length=100
    )

    description = models.TextField()

    intervention_type = models.CharField(
        max_length=50,
        default="GENERAL"
    )

    applicable_station_type = models.CharField(
        max_length=50,
        blank=True
    )

    cost = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    disruption_level = models.FloatField()

    estimated_duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = "interventions"

    def __str__(self):
        return self.name





class Recommendation(models.Model):
    recommendation_id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    simulation = models.ForeignKey(
        SimulationRun,
        on_delete=models.CASCADE,
        related_name="recommendations"
    )

    intervention = models.ForeignKey(
        Intervention,
        on_delete=models.CASCADE,
        related_name="recommendations"
    )

    decision_score = models.FloatField()

    expected_throughput_gain = models.FloatField()

    expected_risk_reduction = models.FloatField()

    cost = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    confidence = models.FloatField()

    status = models.CharField(
        max_length=20,
        default="PENDING"
    )

    rationale = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "recommendations"

        indexes = [
            models.Index(
                fields=["timestamp", "status"],
                name="recommendation_status_time_idx"
            )
        ]
        
class InterventionExecution(models.Model):
    execution_id = models.BigAutoField(
        primary_key=True
    )

    timestamp = models.DateTimeField(
        db_index=True
    )

    recommendation = models.OneToOneField(
        Recommendation,
        on_delete=models.CASCADE,
        related_name="execution"
    )

    status = models.CharField(
        max_length=30,
        default="SUCCESS"
    )

    execution_notes = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "intervention_executions"
        indexes = [
            models.Index(
                fields=["timestamp", "status"],
                name="interv_exec_time_idx"
            )
        ]