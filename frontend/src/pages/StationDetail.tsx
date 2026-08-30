import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Activity,
  Cpu,
  FlaskConical,
  Gauge,
  Layers,
  MapPin,
  RefreshCw,
  ShieldAlert,
  Thermometer,
} from "lucide-react";

import { getStationTwin } from "../api/stations";

interface VehicleTwin {
  vehicle_id: string;
  state?: Record<string, any>;
  features?: Record<string, any>;
  telemetry?: Record<string, any>;
}

interface StationTwinSnapshot {
  station?: {
    station_id: string;
    name: string;
    line_id?: string;
    line_name?: string;
    plant_id?: string;
    plant_name?: string;
    station_type?: string;
    capacity?: number;
    base_cycle_time?: number;
    description?: string;
    position?: number;
    instrumentation_status?: string;
  };
  state?: {
    health_state?: string;
    health_risk?: number;
    confidence?: number;
    wip?: number;
    utilization?: number;
    throughput?: number;
    blocking_time?: number;
    starvation_time?: number;
    current_cycle_time?: number;
    sensor_coverage?: number;
    data_quality?: number;
  };
  features?: {
    avg_cycle_time?: number;
    cycle_time_std?: number;
    cycle_time_trend?: number;
    avg_torque?: number;
    torque_deviation?: number;
    temperature_mean?: number;
    vibration_mean?: number;
    alarm_rate?: number;
    utilization?: number;
    throughput?: number;
    wip?: number;
    blocking_time?: number;
  };
  telemetry?: {
    timestamp?: string;
    cycle_time?: number;
    torque?: number;
    temperature?: number;
    vibration?: number;
    throughput?: number;
    machine_state?: string;
    alarm_count?: number;
    data_quality?: string;
  };
  vehicles?: VehicleTwin[];
}

export default function StationDetail() {
  const { stationId } = useParams<{ stationId: string }>();
  const navigate = useNavigate();

  const [twin, setTwin] = useState<StationTwinSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadTwinData() {
    if (!stationId) return;
    try {
      setLoading(true);
      setError("");
      const data = await getStationTwin(stationId, true);
      setTwin(data as StationTwinSnapshot);
    } catch (err) {
      console.error("Failed to load station twin:", err);
      setError("Unable to retrieve station twin data from the backend.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTwinData();
  }, [stationId]);

  if (loading) {
    return (
      <div className="overview">
        <div className="lines-state">
          <RefreshCw size={24} className="animate-spin" />
          <strong>LOADING STATION DATA</strong>
          <span>Synchronizing digital twin snapshot...</span>
        </div>
      </div>
    );
  }

  if (error || !twin || !twin.station) {
    return (
      <div className="overview">
        <div className="lines-state lines-state-error">
          <strong>ERROR ACCESSING STATION</strong>
          <span>{error || "Station not found."}</span>
          <button
            className="lines-retry"
            onClick={() => navigate("/stations")}
            type="button"
            style={{ marginTop: "14px" }}
          >
            <ArrowLeft size={14} /> BACK TO STATIONS
          </button>
        </div>
      </div>
    );
  }

  const { station, state, features, telemetry, vehicles = [] } = twin;
  const isHealthy = state?.health_state?.toUpperCase() === "NOMINAL";

  return (
    <div className="overview">
      {/* Navigation and Actions Row */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <button
          onClick={() => navigate("/stations")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            background: "transparent",
            border: "1px solid rgba(73, 49, 43, 0.2)",
            color: "var(--brown)",
            cursor: "pointer",
            padding: "8px 16px",
            fontFamily: "var(--font-sans)",
            fontSize: "12px",
            fontWeight: "500",
          }}
        >
          <ArrowLeft size={14} /> BACK TO STATIONS
        </button>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={() =>
              navigate(
                `/simulation?line_id=${station.line_id}&station_id=${station.station_id}`
              )
            }
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              background: "var(--brown)",
              color: "var(--cream)",
              border: "none",
              cursor: "pointer",
              padding: "8px 16px",
              fontFamily: "var(--font-sans)",
              fontSize: "12px",
              fontWeight: "500",
            }}
          >
            <FlaskConical size={14} /> RUN SCENARIO SIMULATION
          </button>
          
          <button
            onClick={() => navigate("/risks")}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              background: "transparent",
              border: "1px solid rgba(73, 49, 43, 0.4)",
              color: "var(--brown)",
              cursor: "pointer",
              padding: "8px 16px",
              fontFamily: "var(--font-sans)",
              fontSize: "12px",
              fontWeight: "500",
            }}
          >
            <ShieldAlert size={14} /> VIEW ACTIVE RISKS
          </button>
        </div>
      </div>

      {/* Header Info */}
      <div className="overview-heading" style={{ marginBottom: "26px" }}>
        <div>
          <div className="eyebrow">
            <span>02</span>
            <span>/</span>
            <span>STATION DRILLDOWN</span>
            <span>/</span>
            <span>{station.station_id}</span>
          </div>

          <h1>{station.name}</h1>
          <p style={{ marginTop: "6px" }}>
            {station.description || "Digital twin interface for manufacturing station."}
          </p>
        </div>

        <div className="overview-live">
          <span
            className="live-dot"
            style={{ background: isHealthy ? "#95c096" : "#d0786a" }}
          />
          {state?.health_state || "UNKNOWN"}
        </div>
      </div>

      {/* Main Attributes Grid */}
      <div className="operations-grid" style={{ marginBottom: "24px" }}>
        {/* PANEL 1: IDENTITY & CONTEXT */}
        <section className="flow-panel" style={{ minHeight: "auto" }}>
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">CONTEXT & SETUP</span>
              <h2>Station Attributes</h2>
            </div>
            <Cpu size={16} />
          </div>

          <div style={{ padding: "20px 24px", display: "grid", gap: "16px" }}>
            <div>
              <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                PARENT PLANT
              </label>
              <div style={{ fontSize: "14px", fontWeight: "600", display: "flex", alignItems: "center", gap: "6px" }}>
                <MapPin size={14} style={{ opacity: 0.6 }} />
                {station.plant_name || "Pune Assembly Facility"}
              </div>
            </div>

            <div>
              <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                PRODUCTION LINE
              </label>
              <div style={{ fontSize: "14px", fontWeight: "600" }}>
                {station.line_name || "Assembly Line L1"} (ID: {station.line_id})
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                  STATION TYPE
                </label>
                <div style={{ fontSize: "13px", fontWeight: "600" }}>{station.station_type || "—"}</div>
              </div>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                  LINE SEQUENCE
                </label>
                <div style={{ fontSize: "13px", fontWeight: "600" }}>
                  Position #{station.position != null ? station.position : "—"}
                </div>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                  BASE CYCLE TIME
                </label>
                <div style={{ fontSize: "13px", fontWeight: "600" }}>
                  {station.base_cycle_time != null ? `${station.base_cycle_time}s` : "—"}
                </div>
              </div>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                  CAPACITY LIMIT
                </label>
                <div style={{ fontSize: "13px", fontWeight: "600" }}>
                  {station.capacity != null ? `${station.capacity} units` : "—"}
                </div>
              </div>
            </div>

            <div>
              <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                DIAGNOSTIC INSTRUMENTATION
              </label>
              <div
                style={{
                  fontSize: "11px",
                  fontWeight: "600",
                  display: "inline-block",
                  padding: "4px 8px",
                  background: station.instrumentation_status === "FULL" ? "rgba(149, 192, 150, 0.2)" : "rgba(224, 187, 126, 0.2)",
                  color: station.instrumentation_status === "FULL" ? "#4a7a4c" : "#946f2c",
                }}
              >
                {station.instrumentation_status || "UNKNOWN"} COVERAGE
              </div>
            </div>
          </div>
        </section>

        {/* PANEL 2: TWIN STATE */}
        <section className="state-panel" style={{ minHeight: "auto" }}>
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">PROGNOSTIC STATE</span>
              <h2>Digital Twin State</h2>
            </div>
            <Activity size={16} />
          </div>

          <div style={{ padding: "20px 24px", display: "grid", gap: "16px" }}>
            <div>
              <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                HEALTH STATE
              </label>
              <div
                style={{
                  fontSize: "16px",
                  fontWeight: "700",
                  color: isHealthy ? "#4a7a4c" : "#b04a43",
                }}
              >
                {state?.health_state || "NOMINAL"}
              </div>
            </div>

            <div>
              <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                HEALTH RISK SCORE
              </label>
              <div style={{ fontSize: "28px", fontWeight: "600", lineHeight: "1", margin: "4px 0" }}>
                {state?.health_risk != null ? `${Math.round(state.health_risk * 100)}%` : "—"}
              </div>
              <div className="state-bar" style={{ margin: "8px 0 0", height: "6px" }}>
                <div
                  className="state-bar-fill"
                  style={{
                    width: `${state?.health_risk ? Math.min(100, state.health_risk * 100) : 0}%`,
                    background: isHealthy ? "var(--brown)" : "#b04a43",
                  }}
                />
              </div>
              <span style={{ fontSize: "8px", opacity: 0.5, fontStyle: "italic" }}>
                Algorithm Confidence: {state?.confidence != null ? `${Math.round(state.confidence * 100)}%` : "—"}
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginTop: "4px" }}>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "2px" }}>
                  UTILIZATION RATE
                </label>
                <div style={{ fontSize: "14px", fontWeight: "600" }}>
                  {state?.utilization != null ? `${Math.round(state.utilization * 100)}%` : "—"}
                </div>
              </div>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "2px" }}>
                  BUFFER LOAD (WIP)
                </label>
                <div style={{ fontSize: "14px", fontWeight: "600" }}>
                  {state?.wip != null ? `${state.wip} / ${station.capacity || 4} units` : "—"}
                </div>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "2px" }}>
                  BLOCKING TIME
                </label>
                <div style={{ fontSize: "13px", fontWeight: "600" }}>
                  {state?.blocking_time != null ? `${state.blocking_time} min` : "—"}
                </div>
              </div>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "2px" }}>
                  STARVATION TIME
                </label>
                <div style={{ fontSize: "13px", fontWeight: "600" }}>
                  {state?.starvation_time != null ? `${state.starvation_time} min` : "—"}
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* Telemetry and Feature Details */}
      <div className="operations-grid" style={{ marginBottom: "24px" }}>
        {/* PANEL 3: TELEMETRY */}
        <section className="flow-panel" style={{ minHeight: "auto" }}>
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">SENSOR RUNTIME</span>
              <h2>Real-time Telemetry</h2>
            </div>
            <Gauge size={16} />
          </div>

          <div style={{ padding: "20px 24px", display: "grid", gap: "16px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                  CURRENT CYCLE TIME
                </label>
                <div style={{ fontSize: "16px", fontWeight: "600" }}>
                  {telemetry?.cycle_time != null ? `${telemetry.cycle_time.toFixed(1)}s` : "—"}
                </div>
                <span style={{ fontSize: "9px", opacity: 0.5, fontStyle: "italic" }}>
                  Baseline avg: {features?.avg_cycle_time?.toFixed(1) || "—"}s
                </span>
              </div>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                  SENSING THERMAL
                </label>
                <div style={{ fontSize: "16px", fontWeight: "600", display: "flex", alignItems: "center", gap: "4px" }}>
                  <Thermometer size={14} style={{ opacity: 0.6 }} />
                  {telemetry?.temperature != null ? `${telemetry.temperature.toFixed(1)}°C` : "—"}
                </div>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                  APPLIED TORQUE
                </label>
                <div style={{ fontSize: "16px", fontWeight: "600" }}>
                  {telemetry?.torque != null ? `${telemetry.torque.toFixed(1)} Nm` : "—"}
                </div>
                <span style={{ fontSize: "9px", opacity: 0.5, fontStyle: "italic" }}>
                  Avg: {features?.avg_torque?.toFixed(1) || "—"} Nm
                </span>
              </div>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                  VIBRATION SIGNALS
                </label>
                <div style={{ fontSize: "16px", fontWeight: "600" }}>
                  {telemetry?.vibration != null ? `${telemetry.vibration.toFixed(1)} mm/s` : "N/A (Sensor Absent)"}
                </div>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                  OPERATIONAL RUNTIME
                </label>
                <div style={{ fontSize: "14px", fontWeight: "600" }}>
                  {telemetry?.machine_state || "RUNNING"}
                </div>
              </div>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "4px" }}>
                  ACTIVE SYSTEM ALARMS
                </label>
                <div
                  style={{
                    fontSize: "14px",
                    fontWeight: "700",
                    color: telemetry?.alarm_count ? "#b04a43" : "inherit",
                  }}
                >
                  {telemetry?.alarm_count != null ? `${telemetry.alarm_count} unresolved` : "0 alarms"}
                </div>
              </div>
            </div>

            <div style={{ borderTop: "1px solid rgba(73, 49, 43, 0.08)", paddingTop: "12px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "2px" }}>
                  DATA QUALITY INDEX
                </label>
                <div style={{ fontSize: "12px", fontWeight: "600" }}>
                  {state?.data_quality != null ? `${Math.round(state.data_quality * 100)}% Match` : "—"}
                </div>
              </div>
              <div>
                <label className="metric-label" style={{ display: "block", marginBottom: "2px" }}>
                  SENSOR COVERAGE
                </label>
                <div style={{ fontSize: "12px", fontWeight: "600" }}>
                  {state?.sensor_coverage != null ? `${Math.round(state.sensor_coverage * 100)}% Active` : "—"}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* PANEL 4: VEHICLES LIST */}
        <section className="activity-panel" style={{ minHeight: "auto" }}>
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">VEHICLE TRACKING</span>
              <h2>Active Products ({vehicles.length})</h2>
            </div>
            <Layers size={16} />
          </div>

          <div style={{ padding: "12px 0" }}>
            {vehicles.length === 0 ? (
              <div style={{ padding: "34px", textAlign: "center", opacity: 0.6 }}>
                No vehicles currently docked at this station.
              </div>
            ) : (
              <div style={{ maxHeight: "280px", overflowY: "auto", padding: "0 24px" }}>
                {vehicles.map((v, idx) => (
                  <div
                    key={v.vehicle_id || idx}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "12px 0",
                      borderBottom: idx < vehicles.length - 1 ? "1.5px solid rgba(73, 49, 43, 0.08)" : "none",
                    }}
                  >
                    <div>
                      <div style={{ fontSize: "13px", fontWeight: "600" }}>{v.vehicle_id}</div>
                      <div style={{ fontSize: "9px", opacity: 0.5, fontFamily: "var(--font-mono)" }}>
                        VARIANT: {v.features?.variant || "Sedan"}
                      </div>
                    </div>

                    <div style={{ textAlign: "right" }}>
                      <div
                        style={{
                          fontSize: "11px",
                          fontWeight: "500",
                          color: (v.state?.quality_risk ?? 0) > 0.4 ? "#b04a43" : "inherit",
                        }}
                      >
                        Risk: {v.state?.quality_risk != null ? `${Math.round(v.state.quality_risk * 100)}%` : "—"}
                      </div>
                      <div style={{ fontSize: "9px", opacity: 0.5 }}>
                        Cycle: {v.telemetry?.cycle_time != null ? `${v.telemetry.cycle_time.toFixed(1)}s` : "—"}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
