import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  ArrowRight,
  FlaskConical,
  Gauge,
  GitBranch,
  Loader2,
  Play,
  RotateCcw,
  ShieldCheck,
  Zap,
} from "lucide-react";

import { getLines, type ProductionLine } from "../api/lines";
import { getStations, type Station } from "../api/stations";
import {
  runSimulation as runSimulationAPI,
  type SimulationRun,
  type SimulationOutcome,
  type Recommendation,
} from "../api/simulation";

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
  const [searchParams] = useSearchParams();

  const [lines, setLines] = useState<ProductionLine[]>([]);
  const [stations, setStations] = useState<Station[]>([]);

  const [selectedLine, setSelectedLine] = useState("");
  const [selectedStation, setSelectedStation] = useState("");

  const [capacityModifier, setCapacityModifier] = useState(100);
  const [riskReduction, setRiskReduction] = useState(0);

  const [simResult, setSimResult] = useState<SimulationRun | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [simError, setSimError] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Preferred demo line — has the degraded S4 scenario
  const DEMO_LINE = "L1-01";

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

      // Pre-select from URL search params if present
      const urlLineId = searchParams.get("line_id");
      const urlStationId = searchParams.get("station_id");

      if (urlLineId && lineData.some((l) => l.line_id === urlLineId)) {
        setSelectedLine(urlLineId);
      } else {
        // Prefer the demo line (L1-01 with degraded S4 scenario); fall back to first
        const demoLine = lineData.find((l) => l.line_id === DEMO_LINE);
        setSelectedLine(demoLine ? demoLine.line_id : lineData[0]?.line_id ?? "");
      }

      if (urlStationId) {
        setSelectedStation(urlStationId);
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
    // Only auto-select first station if URL didn't pre-select one
    const urlStationId = searchParams.get("station_id");
    if (urlStationId && lineStations.some((s) => s.station_id === urlStationId)) {
      setSelectedStation(urlStationId);
    } else if (lineStations.length > 0) {
      setSelectedStation(lineStations[0].station_id);
    } else {
      setSelectedStation("");
    }
  }, [selectedLine, lineStations]);

  const selectedStationObject = stations.find(
    (station) => station.station_id === selectedStation,
  );

  // --- Outcome data from the backend (if available) ---

  const primaryOutcome: SimulationOutcome | null = useMemo(() => {
    if (!simResult?.outcomes?.length) return null;
    return (
      simResult.outcomes.find(
        (o) => o.station_id === selectedStation,
      ) || simResult.outcomes[0]
    );
  }, [simResult, selectedStation]);

  const recommendations: Recommendation[] = simResult?.recommendations ?? [];

  // --- Computed values for the propagation flow diagram ---
  // Prefer real backend baseline (simulated - delta = original); fall back to status estimate.
  const baselineRisk = primaryOutcome
    ? primaryOutcome.simulated_risk - primaryOutcome.risk_delta
    : selectedStationObject
      ? isActiveStatus(selectedStationObject.status)
        ? 0.25
        : 0.65
      : 0;

  const simulatedRisk = primaryOutcome
    ? primaryOutcome.simulated_risk
    : baselineRisk * (1 - riskReduction / 100);

  // --- Actions ---

  async function handleRunSimulation() {
    if (!selectedLine || !selectedStation) return;

    try {
      setSimulating(true);
      setSimError("");
      setSimResult(null);

      const result = await runSimulationAPI({
        line_id: selectedLine,
        target_station_id: selectedStation,
        capacity_modifier: capacityModifier / 100,
        risk_reduction_pct: riskReduction,
        scenario_name: `Scenario — ${capacityModifier}% cap, ${riskReduction}% risk reduction`,
      });

      setSimResult(result);
    } catch (err: unknown) {
      console.error("Simulation failed:", err);
      // Extract the backend's descriptive error message from Axios response
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const axiosDetail = (err as any)?.response?.data?.detail;
      const msg = axiosDetail
        ? String(axiosDetail)
        : err instanceof Error
          ? err.message
          : "Simulation request failed.";
      setSimError(msg);
    } finally {
      setSimulating(false);
    }
  }

  function resetSimulation() {
    setCapacityModifier(100);
    setRiskReduction(0);
    setSimResult(null);
    setSimError("");
  }

  // --- Render ---

  if (loading) {
    return (
      <div className="overview">
        <div className="overview-heading">
          <div>
            <div className="eyebrow">06 / SCENARIO SIMULATION</div>
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
            <div className="eyebrow">06 / SCENARIO SIMULATION</div>
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
          <div className="eyebrow">06 / SCENARIO SIMULATION</div>

          <h1>Test the future state.</h1>

          <p>
            Model production changes before applying an intervention to the
            live system.
          </p>
        </div>

        <div className="overview-live">
          <span className="live-dot" />
          {simulating ? "SIMULATING…" : simResult ? "SIMULATION COMPLETE" : "SIMULATION READY"}
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

          <div className="sim-input-body">
            <label className="sim-input-group">
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

            <label className="sim-input-group-large">
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

            <label className="sim-slider-group">
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

              <div className="sim-slider-footer">
                <span>50%</span>
                <span>150%</span>
              </div>
            </label>

            <label className="sim-slider-group">
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

              <div className="sim-slider-footer">
                <span>0%</span>
                <span>100%</span>
              </div>
            </label>
          </div>

          <div className="sim-flow-footer">
            <button
              type="button"
              onClick={resetSimulation}
              className="sim-btn sim-btn-secondary"
            >
              <RotateCcw size={13} />
              RESET
            </button>

            <button
              type="button"
              onClick={handleRunSimulation}
              disabled={simulating || !selectedStation}
              className="sim-btn sim-btn-primary"
            >
              {simulating ? (
                <Loader2 size={13} className="sim-btn-spin" />
              ) : (
                <Play size={13} />
              )}
              {simulating ? "RUNNING…" : "RUN SIMULATION"}
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
                <span>
                  {primaryOutcome
                    ? `${Math.round(primaryOutcome.simulated_risk * 100)}% risk`
                    : `${Math.round(simulatedRisk * 100)}% risk`}
                </span>
              </div>
            </div>
          </div>

          <div className="state-bar">
            <div
              className="state-bar-fill"
              style={{
                width: `${Math.min(
                  100,
                  primaryOutcome
                    ? primaryOutcome.simulated_risk * 100
                    : simulatedRisk * 100,
                )}%`,
              }}
            />
          </div>

          <div className="state-footer">
            <span>BASE {Math.round(baselineRisk * 100)}%</span>
            <span>
              SIMULATED{" "}
              {primaryOutcome
                ? Math.round(primaryOutcome.simulated_risk * 100)
                : Math.round(simulatedRisk * 100)}
              %
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

          {simError && (
            <div
              style={{
                padding: "16px 24px",
                borderLeft: "3px solid #b04a43",
                margin: "0 0 4px",
              }}
            >
              <div style={{ fontSize: "10px", fontWeight: "700", color: "#b04a43", letterSpacing: "0.08em", marginBottom: "4px" }}>SIMULATION ERROR</div>
              <div style={{ fontSize: "13px", color: "#b04a43" }}>{simError}</div>
            </div>
          )}

          {!simResult && !simError ? (
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
          ) : simResult ? (
            <div>
              {/* ── STATUS BANNER ── */}
              <div className="sim-status-banner">
                <div>
                  <div className="sim-status-title">SIMULATION COMPLETED</div>
                  <div className="sim-status-name">{simResult.scenario_name}</div>
                </div>
                <ShieldCheck size={18} style={{ color: "#4a7a4c" }} />
              </div>

              <div className="sim-grid-layout">
                {/* ── METRIC CARDS GRID ── */}
                <div className="sim-cards">
                  {/* Card 1: Risk Assessment */}
                  {primaryOutcome && (
                    <div className="sim-card">
                      <div>
                        <div className="sim-card-heading">Risk Assessment</div>
                        <div className="sim-card-comparison">
                          <div className="sim-card-val-box">
                            <span className="sim-card-val-label">BASELINE</span>
                            <span className="sim-card-val">
                              {Math.round((primaryOutcome.simulated_risk - primaryOutcome.risk_delta) * 100)}%
                            </span>
                          </div>
                          <span className="sim-card-arrow">→</span>
                          <div className="sim-card-val-box">
                            <span className="sim-card-val-label">SIMULATED</span>
                            <span className="sim-card-val">
                              {Math.round(primaryOutcome.simulated_risk * 100)}%
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className={`sim-card-change ${primaryOutcome.risk_delta < 0 ? 'sim-change-good' : primaryOutcome.risk_delta === 0 ? 'sim-change-neutral' : 'sim-change-bad'}`}>
                        {primaryOutcome.risk_delta < 0 ? '▼' : primaryOutcome.risk_delta === 0 ? '•' : '▲'}{' '}
                        {Math.abs(Math.round(primaryOutcome.risk_delta * 100))} pp {primaryOutcome.risk_delta < 0 ? 'reduction' : primaryOutcome.risk_delta === 0 ? 'no change' : 'increase'}
                      </div>
                    </div>
                  )}

                  {/* Card 2: Throughput Impact */}
                  {primaryOutcome && (
                    <div className="sim-card">
                      <div>
                        <div className="sim-card-heading">Throughput Impact</div>
                        <div className="sim-card-comparison">
                          <div className="sim-card-val-box">
                            <span className="sim-card-val-label">BASELINE</span>
                            <span className="sim-card-val">
                              {Math.round(primaryOutcome.simulated_throughput - primaryOutcome.throughput_delta)}
                            </span>
                          </div>
                          <span className="sim-card-arrow">→</span>
                          <div className="sim-card-val-box">
                            <span className="sim-card-val-label">SIMULATED</span>
                            <span className="sim-card-val">
                              {Math.round(primaryOutcome.simulated_throughput)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className={`sim-card-change ${primaryOutcome.throughput_delta > 0 ? 'sim-change-good' : primaryOutcome.throughput_delta === 0 ? 'sim-change-neutral' : 'sim-change-bad'}`}>
                        {primaryOutcome.throughput_delta > 0 ? '▲ +' : primaryOutcome.throughput_delta === 0 ? '•' : '▼'}{' '}
                        {Math.round(primaryOutcome.throughput_delta)} units vs baseline
                      </div>
                    </div>
                  )}

                  {/* Card 3: Intervention Applied */}
                  <div className="sim-card">
                    <div>
                      <div className="sim-card-heading">Intervention Applied</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div>
                          <div className="sim-card-val-label">TARGET STATION</div>
                          <div style={{ fontSize: '12px', fontWeight: 600 }}>
                            {selectedStationObject?.name || selectedStation}
                          </div>
                        </div>
                        <div style={{ display: 'flex', gap: '16px' }}>
                          <div>
                            <div className="sim-card-val-label">CAPACITY</div>
                            <div style={{ fontSize: '13px', fontWeight: 600 }}>{capacityModifier}%</div>
                          </div>
                          <div>
                            <div className="sim-card-val-label">RISK REDUCTION</div>
                            <div style={{ fontSize: '13px', fontWeight: 600 }}>{riskReduction}%</div>
                          </div>
                        </div>
                      </div>
                    </div>
                    {primaryOutcome?.is_bottleneck && (
                      <div className="sim-card-change sim-change-bad" style={{ fontSize: '9px', letterSpacing: '0.05em' }}>
                        ⚠️ IDENTIFIED AS BOTTLENECK
                      </div>
                    )}
                  </div>
                </div>

                {/* ── RECOMMENDATIONS SECTION ── */}
                {recommendations.length > 0 && (
                  <div className="sim-rec-section">
                    <div className="sim-rec-title">AI Decision Recommendations</div>
                    
                    {/* Best Recommendation */}
                    <div className="sim-rec-box sim-rec-box-best">
                      <div className="sim-rec-header">
                        <div>
                          <div className="sim-rec-name">{recommendations[0].intervention_name}</div>
                        </div>
                        <div className="sim-rec-badge">BEST CHOICE</div>
                      </div>

                      <div className="sim-rec-metrics">
                        <div className="sim-rec-meta-box">
                          <span className="sim-rec-meta-label">DECISION SCORE</span>
                          <span className="sim-rec-meta-val">{Math.round(recommendations[0].decision_score * 100)}%</span>
                        </div>
                        <div className="sim-rec-meta-box">
                          <span className="sim-rec-meta-label">CONFIDENCE</span>
                          <span className="sim-rec-meta-val">{Math.round(recommendations[0].confidence * 100)}%</span>
                        </div>
                        <div className="sim-rec-meta-box">
                          <span className="sim-rec-meta-label">EST. COST</span>
                          <span className="sim-rec-meta-val">
                            {recommendations[0].cost ? `₹${Number(recommendations[0].cost).toLocaleString()}` : "—"}
                          </span>
                        </div>
                        <div className="sim-rec-meta-box">
                          <span className="sim-rec-meta-label">EXPECTED GAIN</span>
                          <span className="sim-rec-meta-val sim-rec-meta-val-highlight">
                            +{Math.round(recommendations[0].expected_throughput_gain)} units
                          </span>
                        </div>
                        <div className="sim-rec-meta-box">
                          <span className="sim-rec-meta-label">RISK IMPACT</span>
                          <span className="sim-rec-meta-val sim-rec-meta-val-highlight">
                            -{Math.round(recommendations[0].expected_risk_reduction * 100)}%
                          </span>
                        </div>
                      </div>

                      <div className="sim-rec-rationale">
                        <strong>Rationale:</strong> {recommendations[0].rationale}
                      </div>
                    </div>

                    {/* Secondary recommendations */}
                    {recommendations.length > 1 && recommendations.slice(1).map((rec, idx) => (
                      <div className="sim-rec-alt-row" key={rec.recommendation_id}>
                        <div className="sim-rec-alt-name">
                          Alternative {idx + 2}: {rec.intervention_name}
                        </div>
                        <div className="sim-rec-alt-meta">
                          <span>SCORE: {Math.round(rec.decision_score * 100)}%</span>
                          <span>COST: {rec.cost ? `₹${Number(rec.cost).toLocaleString()}` : "—"}</span>
                          <span>GAIN: +{Math.round(rec.expected_throughput_gain)} u</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </section>

        {/* Additional outcomes panel — only when backend data is available */}
        {simResult && simResult.outcomes.length > 1 && (
          <section className="risk-panel">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">STATION-LEVEL IMPACT</span>
                <h2>All affected stations</h2>
              </div>

              <Gauge size={16} />
            </div>

            <div className="sim-station-table-wrapper" style={{ maxHeight: "390px", overflowY: "auto" }}>
              {simResult.outcomes.map((outcome) => (
                <div key={outcome.outcome_id} className="sim-station-row">
                  <div className="sim-station-name-col">
                    <div className="sim-station-title" title={outcome.station_name || outcome.station_id}>
                      {outcome.station_name || outcome.station_id}
                    </div>
                    <div className="sim-station-badge-row">
                      <span className="sim-station-id">{outcome.station_id}</span>
                      {outcome.is_bottleneck && (
                        <span className="sim-station-bottleneck">BOTTLENECK</span>
                      )}
                    </div>
                  </div>

                  <div className="sim-station-metric-col">
                    <span className="sim-station-metric-val">Risk: {Math.round(outcome.simulated_risk * 100)}%</span>
                    <span className="sim-station-metric-delta" style={{ color: outcome.risk_delta < 0 ? "#4a7a4c" : outcome.risk_delta > 0 ? "#b04a43" : "var(--brown)" }}>
                      {outcome.risk_delta < 0 ? "▼" : outcome.risk_delta > 0 ? "▲" : ""} {Math.abs(Math.round(outcome.risk_delta * 100))} pp
                    </span>
                  </div>

                  <div className="sim-station-metric-col">
                    <span className="sim-station-metric-val">TPT: {Math.round(outcome.simulated_throughput)}</span>
                    <span className="sim-station-metric-delta" style={{ color: outcome.throughput_delta > 0 ? "#4a7a4c" : outcome.throughput_delta < 0 ? "#b04a43" : "var(--brown)" }}>
                      {outcome.throughput_delta > 0 ? "▲ +" : outcome.throughput_delta < 0 ? "▼ " : ""}{Math.round(outcome.throughput_delta)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}