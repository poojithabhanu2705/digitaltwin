import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  Activity,
  BrainCircuit,
  ChevronRight,
  RefreshCw,
  ShieldAlert,
  TrendingDown,
} from "lucide-react";

import { getStations, type Station } from "../api/stations";

function formatStatus(status?: string | null) {
  if (!status) return "UNKNOWN";

  return status
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export default function RisksPage() {
  const navigate = useNavigate();
  const [stations, setStations] = useState<Station[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadRisks() {
    try {
      setLoading(true);
      setError("");

      const stationData = await getStations();
      setStations(stationData);
    } catch (err) {
      console.error("Failed to load risk page:", err);
      setError(
        "Unable to load station data. Make sure the Django API is running.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRisks();
  }, []);

  /*
   * The backend RiskPrediction API has not been exposed yet.
   *
   * Until that endpoint is added, this page uses station operational
   * state to provide the structural risk view without inventing ML
   * prediction values.
   */
  const operationalStations = useMemo(
    () =>
      stations.filter((station) =>
        ["ACTIVE", "OPERATIONAL", "ONLINE", "RUNNING", "NOMINAL"].includes(
          (station.status ?? "").toUpperCase(),
        ),
      ),
    [stations],
  );

  const nonOperationalStations = useMemo(
    () => stations.filter((station) => !operationalStations.includes(station)),
    [stations, operationalStations],
  );

  if (loading) {
    return (
      <div className="overview">
        <div className="overview-heading">
          <div>
            <div className="eyebrow">02 / RISK INTELLIGENCE</div>
            <h1>Where could operations fail?</h1>
            <p>Loading station risk context...</p>
          </div>

          <div className="overview-live">
            <span className="live-dot" />
            CONNECTING
          </div>
        </div>

        <section className="metric-rail">
          <div className="metric">
            <span className="metric-label">PREDICTIONS</span>
            <div className="metric-value">—</div>
            <div className="metric-note">LOADING</div>
          </div>

          <div className="metric">
            <span className="metric-label">HIGH RISK</span>
            <div className="metric-value">—</div>
            <div className="metric-note">LOADING</div>
          </div>

          <div className="metric">
            <span className="metric-label">EXPOSURES</span>
            <div className="metric-value">—</div>
            <div className="metric-note">LOADING</div>
          </div>

          <div className="metric">
            <span className="metric-label">MODEL</span>
            <div className="metric-value">—</div>
            <div className="metric-note">LOADING</div>
          </div>
        </section>
      </div>
    );
  }

  if (error) {
    return (
      <div className="overview">
        <div className="overview-heading">
          <div>
            <div className="eyebrow">02 / RISK INTELLIGENCE</div>
            <h1>Where could operations fail?</h1>
            <p>{error}</p>
          </div>

          <button
            type="button"
            className="overview-live"
            onClick={loadRisks}
            style={{
              border: "none",
              cursor: "pointer",
              background: "transparent",
            }}
          >
            <RefreshCw size={14} />
            RETRY
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="overview">
      <div className="overview-heading">
        <div>
          <div className="eyebrow">02 / RISK INTELLIGENCE</div>

          <h1>Where could operations fail?</h1>

          <p>
            ML-driven bottleneck and quality-risk analysis across the
            production structure.
          </p>
        </div>

        <div className="overview-live">
          <span className="live-dot" />
          RISK ENGINE
        </div>
      </div>

      <section className="metric-rail">
        <div className="metric">
          <span className="metric-label">STATIONS</span>
          <div className="metric-value">{stations.length}</div>
          <div className="metric-note">RISK TARGETS</div>
        </div>

        <div className="metric">
          <span className="metric-label">OPERATIONAL</span>
          <div className="metric-value">{operationalStations.length}</div>
          <div className="metric-note">CURRENTLY ONLINE</div>
        </div>

        <div className="metric">
          <span className="metric-label">ATTENTION</span>
          <div className="metric-value">{nonOperationalStations.length}</div>
          <div className="metric-note">NON-OPERATIONAL</div>
        </div>

        <div className="metric">
          <span className="metric-label">PREDICTION</span>
          <div className="metric-value">ML</div>
          <div className="metric-note">STATION RISK MODEL</div>
        </div>
      </section>

      <div className="operations-grid">
        <section className="flow-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">RISK PIPELINE</span>
              <h2>Risk intelligence</h2>
            </div>

            <BrainCircuit size={18} strokeWidth={1.5} />
          </div>

          <div className="flow-map">
            <div className="flow-node flow-node-primary">
              <div className="flow-icon">
                <Activity size={17} strokeWidth={1.5} />
              </div>

              <div>
                <strong>LIVE STATE</strong>
                <span>Station telemetry & state</span>
              </div>
            </div>

            <ChevronRight
              className="flow-arrow"
              size={20}
              strokeWidth={1.3}
            />

            <div className="flow-node">
              <div className="flow-icon">
                <BrainCircuit size={17} strokeWidth={1.5} />
              </div>

              <div>
                <strong>ML PREDICTION</strong>
                <span>Station bottleneck risk</span>
              </div>
            </div>

            <ChevronRight
              className="flow-arrow"
              size={20}
              strokeWidth={1.3}
            />

            <div className="flow-node">
              <div className="flow-icon">
                <ShieldAlert size={17} strokeWidth={1.5} />
              </div>

              <div>
                <strong>PROPAGATION</strong>
                <span>Downstream exposure</span>
              </div>
            </div>
          </div>

          <div className="flow-footer">
            <div>
              <span className="small-status-dot" />
              RISK PREDICTION PIPELINE
            </div>

            <button
              type="button"
              onClick={loadRisks}
              style={{
                border: "none",
                background: "transparent",
                cursor: "pointer",
                font: "inherit",
              }}
            >
              <RefreshCw size={13} />
              REFRESH
            </button>
          </div>
        </section>

        <section className="state-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">MODEL STATUS</span>
              <h2>Prediction engine</h2>
            </div>

            <BrainCircuit size={18} strokeWidth={1.5} />
          </div>

          <div className="state-reading">
            <div className="state-number">ML</div>

            <div className="state-copy">
              <strong>Station risk model</strong>

              <span>
                RANDOM FOREST · HIGH-RISK STATE PREDICTION
              </span>
            </div>
          </div>

          <div className="state-bar">
            <div
              className="state-bar-fill"
              style={{ width: "100%" }}
            />
          </div>

          <div className="state-footer">
            <span>MODEL AVAILABLE</span>
            <span>30 MIN HORIZON</span>
          </div>
        </section>

        <section className="activity-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">STATION WATCHLIST</span>
              <h2>Operational exposure</h2>
            </div>

            <AlertTriangle size={18} strokeWidth={1.5} />
          </div>

          <div className="activity-list">
            {stations.length === 0 ? (
              <div className="activity-row">
                <div className="activity-content">
                  <strong>No station data available</strong>
                </div>
              </div>
            ) : (
              stations.slice(0, 8).map((station) => {
                const operational = operationalStations.includes(station);

                return (
                  <div
                    className="activity-row"
                    key={station.station_id}
                  >
                    <div className="activity-marker">
                      <span />
                    </div>

                    <div className="activity-content">
                      <span className="activity-type">
                        {operational ? "OPERATIONAL" : "ATTENTION"}
                      </span>

                      <strong>{station.name}</strong>

                      <span>
                        {formatStatus(station.status)}
                        {station.line_name
                          ? ` · ${station.line_name}`
                          : ""}
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={() => {
                        if (operational) {
                          navigate(`/stations/${station.station_id}`);
                        } else {
                          const params = new URLSearchParams();
                          if (station.line_id) params.set("line_id", station.line_id);
                          params.set("station_id", station.station_id);
                          navigate(`/simulation?${params.toString()}`);
                        }
                      }}
                      style={{
                        marginLeft: "auto",
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                        fontSize: "11px",
                        letterSpacing: "0.08em",
                        border: "none",
                        background: "transparent",
                        cursor: "pointer",
                        font: "inherit",
                        padding: "4px 8px",
                        opacity: 0.85,
                      }}
                    >
                      {operational ? (
                        <>
                          <TrendingDown size={13} />
                          MONITOR
                        </>
                      ) : (
                        <>
                          <AlertTriangle size={13} />
                          SIMULATE
                        </>
                      )}
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </section>
      </div>
    </div>
  );
}