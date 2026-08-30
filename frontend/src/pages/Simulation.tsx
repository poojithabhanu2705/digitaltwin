import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  FlaskConical,
  Gauge,
  GitBranch,
  Play,
  RotateCcw,
  ShieldCheck,
  TrendingDown,
  Zap,
} from "lucide-react";

import { getLines, type ProductionLine } from "../api/lines";
import { getStations, type Station } from "../api/stations";

function isActiveStatus(status?: string | null) {
  if (!status) return false;

  return [
    "ACTIVE",
    "OPERATIONAL",
    "ONLINE",
    "RUNNING",
    "NOMINAL",
  ].includes(status.toUpperCase());
}

export default function SimulationPage() {
  const [lines, setLines] = useState<ProductionLine[]>([]);
  const [stations, setStations] = useState<Station[]>([]);

  const [selectedLine, setSelectedLine] = useState("");
  const [selectedStation, setSelectedStation] = useState("");

  const [capacityModifier, setCapacityModifier] = useState(100);
  const [riskReduction, setRiskReduction] = useState(0);

  const [hasRun, setHasRun] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadSimulationContext() {
    try {
      setLoading(true);
      setError("");

      const [lineData, stationData] = await Promise.all([
        getLines(),
        getStations(),
      ]);

      setLines(lineData);
      setStations(stationData);

      if (lineData.length > 0) {
        setSelectedLine(lineData[0].line_id);
      }
    } catch (err) {
      console.error("Failed to load simulation context:", err);
      setError(
        "Unable to load simulation context. Make sure the Django API is running.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSimulationContext();
  }, []);

  const lineStations = useMemo(
    () =>
      stations.filter((station) => station.line_id === selectedLine),
    [stations, selectedLine],
  );

  useEffect(() => {
    if (lineStations.length > 0) {
      setSelectedStation(lineStations[0].station_id);
    } else {
      setSelectedStation("");
    }
  }, [selectedLine, lineStations]);

  const selectedStationObject = stations.find(
    (station) => station.station_id === selectedStation,
  );

  /*
   * These values are deliberately presentation-level estimates until
   * SimulationService is exposed through a backend API endpoint.
   *
   * The actual backend SimulationService calculates:
   *
   * simulated_risk =
   *   effective_risk * (1 - risk_reduction_pct / 100)
   *
   * simulated_throughput =
   *   base_throughput * mod_capacity * (1 - final_risk)
   */

  const baselineRisk = selectedStationObject
    ? isActiveStatus(selectedStationObject.status)
      ? 0.25
      : 0.65
    : 0;

  const simulatedRisk =
    baselineRisk * (1 - riskReduction / 100);

  const riskDelta = simulatedRisk - baselineRisk;

  const baselineThroughput = 100;

  const simulatedThroughput =
    baselineThroughput *
    (capacityModifier / 100) *
    (1 - simulatedRisk);

  const throughputDelta =
    simulatedThroughput -
    baselineThroughput * (1 - baselineRisk);

  function runSimulation() {
    setHasRun(true);
  }

  function resetSimulation() {
    setCapacityModifier(100);
    setRiskReduction(0);
    setHasRun(false);
  }

  if (loading) {
    return (
      <div className="overview">
        <div className="overview-heading">
          <div>
            <div className="eyebrow">03 / SCENARIO SIMULATION</div>
            <h1>Test the future state.</h1>
            <p>Loading simulation context...</p>
          </div>

          <div className="overview-live">
            <span className="live-dot" />
            CONNECTING
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="overview">
        <div className="overview-heading">
          <div>
            <div className="eyebrow">03 / SCENARIO SIMULATION</div>
            <h1>Test the future state.</h1>
            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="overview">
      <div className="overview-heading">
        <div>
          <div className="eyebrow">03 / SCENARIO SIMULATION</div>

          <h1>Test the future state.</h1>

          <p>
            Model production changes before applying an intervention to the
            live system.
          </p>
        </div>

        <div className="overview-live">
          <span className="live-dot" />
          SIMULATION READY
        </div>
      </div>

      <div className="operations-grid">
        {/* Scenario controls */}

        <section className="flow-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">SCENARIO INPUT</span>
              <h2>Build a scenario</h2>
            </div>

            <FlaskConical size={18} strokeWidth={1.5} />
          </div>

          <div
            style={{
              display: "grid",
              gap: "22px",
              padding: "10px 0",
            }}
          >
            <label
              style={{
                display: "grid",
                gap: "8px",
              }}
            >
              <span className="metric-label">PRODUCTION LINE</span>

              <select
                value={selectedLine}
                onChange={(event) =>
                  setSelectedLine(event.target.value)
                }
                style={{
                  width: "100%",
                  padding: "12px",
                  background: "transparent",
                  border: "1px solid var(--border, #d8d3c8)",
                  font: "inherit",
                }}
              >
                {lines.map((line) => (
                  <option
                    key={line.line_id}
                    value={line.line_id}
                  >
                    {line.name}
                  </option>
                ))}
              </select>
            </label>

            <label
              style={{
                display: "grid",
                gap: "8px",
              }}
            >
              <span className="metric-label">TARGET STATION</span>

              <select
                value={selectedStation}
                onChange={(event) =>
                  setSelectedStation(event.target.value)
                }
                style={{
                  width: "100%",
                  padding: "12px",
                  background: "transparent",
                  border: "1px solid var(--border, #d8d3c8)",
                  font: "inherit",
                }}
              >
                {lineStations.length === 0 ? (
                  <option value="">No stations</option>
                ) : (
                  lineStations.map((station) => (
                    <option
                      key={station.station_id}
                      value={station.station_id}
                    >
                      {station.name}
                    </option>
                  ))
                )}
              </select>
            </label>

            <label
              style={{
                display: "grid",
                gap: "10px",
              }}
            >
              <span className="metric-label">
                CAPACITY MODIFIER · {capacityModifier}%
              </span>

              <input
                type="range"
                min="50"
                max="150"
                step="5"
                value={capacityModifier}
                onChange={(event) =>
                  setCapacityModifier(Number(event.target.value))
                }
              />

              <div className="state-footer">
                <span>50%</span>
                <span>150%</span>
              </div>
            </label>

            <label
              style={{
                display: "grid",
                gap: "10px",
              }}
            >
              <span className="metric-label">
                RISK REDUCTION · {riskReduction}%
              </span>

              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={riskReduction}
                onChange={(event) =>
                  setRiskReduction(Number(event.target.value))
                }
              />

              <div className="state-footer">
                <span>0%</span>
                <span>100%</span>
              </div>
            </label>
          </div>

          <div className="flow-footer">
            <button
              type="button"
              onClick={resetSimulation}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "7px",
                border: "none",
                background: "transparent",
                cursor: "pointer",
                font: "inherit",
              }}
            >
              <RotateCcw size={13} />
              RESET
            </button>

            <button
              type="button"
              onClick={runSimulation}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "7px",
                border: "none",
                background: "transparent",
                cursor: "pointer",
                font: "inherit",
              }}
            >
              <Play size={13} />
              RUN SIMULATION
            </button>
          </div>
        </section>

        {/* Scenario visualization */}

        <section className="state-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">SCENARIO</span>
              <h2>Propagation model</h2>
            </div>

            <GitBranch size={18} strokeWidth={1.5} />
          </div>

          <div className="flow-map">
            <div className="flow-node flow-node-primary">
              <div className="flow-icon">
                <Zap size={17} strokeWidth={1.5} />
              </div>

              <div>
                <strong>BASE STATE</strong>
                <span>{Math.round(baselineRisk * 100)}% risk</span>
              </div>
            </div>

            <ArrowRight
              className="flow-arrow"
              size={20}
              strokeWidth={1.3}
            />

            <div className="flow-node">
              <div className="flow-icon">
                <GitBranch size={17} strokeWidth={1.5} />
              </div>

              <div>
                <strong>INTERVENTION</strong>
                <span>{riskReduction}% risk reduction</span>
              </div>
            </div>

            <ArrowRight
              className="flow-arrow"
              size={20}
              strokeWidth={1.3}
            />

            <div className="flow-node">
              <div className="flow-icon">
                <Gauge size={17} strokeWidth={1.5} />
              </div>

              <div>
                <strong>FINAL STATE</strong>
                <span>{Math.round(simulatedRisk * 100)}% risk</span>
              </div>
            </div>
          </div>

          <div className="state-bar">
            <div
              className="state-bar-fill"
              style={{
                width: `${Math.min(100, simulatedRisk * 100)}%`,
              }}
            />
          </div>

          <div className="state-footer">
            <span>BASE {Math.round(baselineRisk * 100)}%</span>
            <span>
              SIMULATED {Math.round(simulatedRisk * 100)}%
            </span>
          </div>
        </section>

        {/* Results */}

        <section className="activity-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">SIMULATION OUTCOME</span>
              <h2>Decision impact</h2>
            </div>

            <ShieldCheck size={18} strokeWidth={1.5} />
          </div>

          {!hasRun ? (
            <div
              style={{
                padding: "35px 0",
                textAlign: "center",
              }}
            >
              <FlaskConical
                size={28}
                strokeWidth={1.2}
              />

              <p
                style={{
                  marginTop: "14px",
                  opacity: 0.65,
                }}
              >
                Configure a scenario and run the simulation to evaluate
                the projected outcome.
              </p>
            </div>
          ) : (
            <div className="activity-list">
              <div className="activity-row">
                <div className="activity-marker">
                  <span />
                </div>

                <div className="activity-content">
                  <span className="activity-type">
                    SIMULATED RISK
                  </span>

                  <strong>
                    {Math.round(simulatedRisk * 100)}%
                  </strong>

                  <span>
                    {riskDelta < 0
                      ? `${Math.abs(Math.round(riskDelta * 100))}% reduction`
                      : "No reduction"}
                  </span>
                </div>

                <TrendingDown size={16} />
              </div>

              <div className="activity-row">
                <div className="activity-marker">
                  <span />
                </div>

                <div className="activity-content">
                  <span className="activity-type">
                    SIMULATED THROUGHPUT
                  </span>

                  <strong>
                    {Math.round(simulatedThroughput)}%
                  </strong>

                  <span>
                    {throughputDelta >= 0 ? "+" : ""}
                    {Math.round(throughputDelta)} pts vs baseline
                  </span>
                </div>

                <Gauge size={16} />
              </div>

              <div className="activity-row">
                <div className="activity-marker">
                  <span />
                </div>

                <div className="activity-content">
                  <span className="activity-type">
                    INTERVENTION
                  </span>

                  <strong>
                    {capacityModifier}% CAPACITY
                  </strong>

                  <span>
                    {riskReduction}% risk reduction applied
                  </span>
                </div>

                <ShieldCheck size={16} />
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}