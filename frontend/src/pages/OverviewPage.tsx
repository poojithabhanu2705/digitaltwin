import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  Activity,
  Factory,
  Gauge,
  GitBranch,
  Layers3,
  RefreshCw,
} from "lucide-react";

import { getPlants } from "../api/plants";
import { getLines, type ProductionLine } from "../api/lines";
import { getStations, type Station } from "../api/stations";
import type { Plant } from "../types/api";

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

function formatStatus(status?: string | null) {
  if (!status) return "UNKNOWN";

  return status
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export default function OverviewPage() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [lines, setLines] = useState<ProductionLine[]>([]);
  const [stations, setStations] = useState<Station[]>([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function loadOverview(forceRefresh = false) {
    try {
      if (forceRefresh) {
        setRefreshing(true);
      } else if (
        plants.length === 0 &&
        lines.length === 0 &&
        stations.length === 0
      ) {
        setLoading(true);
      }

      setError("");

      const [plantData, lineData, stationData] =
        await Promise.all([
          getPlants(forceRefresh),
          getLines(forceRefresh),
          getStations(forceRefresh),
        ]);

      setPlants(plantData);
      setLines(lineData);
      setStations(stationData);
    } catch (err) {
      console.error("Failed to load overview:", err);

      setError(
        "Unable to load live plant data. Make sure the Django API is running.",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void loadOverview();
  }, []);

  const activeLines = useMemo(
    () => lines.filter((line) => isActiveStatus(line.status)),
    [lines],
  );

  const operationalStations = useMemo(
    () =>
      stations.filter((station) =>
        isActiveStatus(station.status),
      ),
    [stations],
  );

  const selectedPlant = plants[0];

  const stationCoverage =
    stations.length > 0
      ? Math.round(
          (operationalStations.length / stations.length) * 100,
        )
      : 0;

  const plantLines = selectedPlant
    ? lines.filter(
        (line) => line.plant_id === selectedPlant.plant_id,
      )
    : [];

  const plantStations = selectedPlant
    ? stations.filter((station) => {
        const line = lines.find(
          (item) => item.line_id === station.line_id,
        );

        return line?.plant_id === selectedPlant.plant_id;
      })
    : [];

  const lastStationStatus = stations
    .slice()
    .sort((a, b) => {
      const aSequence =
        a.sequence_number ?? Number.MAX_SAFE_INTEGER;

      const bSequence =
        b.sequence_number ?? Number.MAX_SAFE_INTEGER;

      return aSequence - bSequence;
    })
    .slice(0, 5);

  if (loading) {
    return (
      <div className="overview">
        <div className="overview-heading">
          <div>
            <div className="eyebrow">
              01 / PLANT OVERVIEW
            </div>

            <h1>Operations at a glance.</h1>

            <p>Loading live production structure...</p>
          </div>

          <div className="overview-live">
            <span className="live-dot" />
            CONNECTING
          </div>
        </div>

        <section className="metric-rail">
          {[
            "PLANTS",
            "ACTIVE LINES",
            "STATIONS",
            "COVERAGE",
          ].map((label) => (
            <div className="metric" key={label}>
              <span className="metric-label">{label}</span>

              <div className="metric-value">—</div>

              <div className="metric-note">
                LOADING
              </div>
            </div>
          ))}
        </section>
      </div>
    );
  }

  if (error && plants.length === 0) {
    return (
      <div className="overview">
        <div className="overview-heading">
          <div>
            <div className="eyebrow">
              01 / PLANT OVERVIEW
            </div>

            <h1>Operations at a glance.</h1>

            <p>{error}</p>
          </div>

          <button
            type="button"
            className="overview-live"
            onClick={() => void loadOverview(true)}
            disabled={refreshing}
            style={{
              border: "none",
              cursor: refreshing
                ? "default"
                : "pointer",
              background: "transparent",
              opacity: refreshing ? 0.6 : 1,
            }}
          >
            <RefreshCw
              size={14}
              className={
                refreshing ? "spin" : undefined
              }
            />

            {refreshing ? "REFRESHING" : "RETRY"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="overview">
      <div className="overview-heading">
        <div>
          <div className="eyebrow">
            01 / PLANT OVERVIEW
          </div>

          <h1>Operations at a glance.</h1>

          <p>
            Live production structure and operational
            status from the TwinSight backend.
          </p>
        </div>

        <button
          type="button"
          className="overview-live"
          onClick={() => void loadOverview(true)}
          disabled={refreshing}
          style={{
            border: "none",
            cursor: refreshing
              ? "default"
              : "pointer",
            background: "transparent",
            opacity: refreshing ? 0.6 : 1,
          }}
        >
          <span className="live-dot" />

          {refreshing ? (
            <>
              <RefreshCw
                size={13}
                className="spin"
              />
              REFRESHING
            </>
          ) : (
            "LIVE DATA"
          )}
        </button>
      </div>

      <section className="metric-rail">
        <div className="metric">
          <span className="metric-label">
            PLANTS
          </span>

          <div className="metric-value">
            {plants.length}
          </div>

          <div className="metric-note">
            CONFIGURED FACILITIES
          </div>
        </div>

        <div className="metric">
          <span className="metric-label">
            ACTIVE LINES
          </span>

          <div className="metric-value">
            {activeLines.length}
          </div>

          <div className="metric-note">
            OF {lines.length} CONFIGURED
          </div>
        </div>

        <div className="metric">
          <span className="metric-label">
            STATIONS
          </span>

          <div className="metric-value">
            {stations.length}
          </div>

          <div className="metric-note">
            {operationalStations.length} OPERATIONAL
          </div>
        </div>

        <div className="metric">
          <span className="metric-label">
            COVERAGE
          </span>

          <div className="metric-value">
            {stationCoverage}
            <span className="metric-unit">%</span>
          </div>

          <div className="metric-note">
            OPERATIONAL STATIONS
          </div>
        </div>
      </section>

      <div className="operations-grid">
        <section className="flow-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">
                PRODUCTION STRUCTURE
              </span>

              <h2>Plant flow</h2>
            </div>

            <Factory
              size={18}
              strokeWidth={1.5}
            />
          </div>

          <div className="flow-map">
            <div className="flow-node flow-node-primary">
              <div className="flow-icon">
                <Factory
                  size={17}
                  strokeWidth={1.5}
                />
              </div>

              <div>
                <strong>
                  {selectedPlant?.name ??
                    "NO PLANT"}
                </strong>

                <span>
                  {selectedPlant?.location ??
                    "NO LOCATION"}
                </span>
              </div>
            </div>

            <ArrowRight
              className="flow-arrow"
              size={20}
              strokeWidth={1.3}
            />

            <div className="flow-node">
              <div className="flow-icon">
                <GitBranch
                  size={17}
                  strokeWidth={1.5}
                />
              </div>

              <div>
                <strong>
                  {plantLines.length} LINES
                </strong>

                <span>
                  {
                    plantLines.filter((line) =>
                      isActiveStatus(
                        line.status,
                      ),
                    ).length
                  }{" "}
                  ACTIVE
                </span>
              </div>
            </div>

            <ArrowRight
              className="flow-arrow"
              size={20}
              strokeWidth={1.3}
            />

            <div className="flow-node">
              <div className="flow-icon">
                <Layers3
                  size={17}
                  strokeWidth={1.5}
                />
              </div>

              <div>
                <strong>
                  {plantStations.length} STATIONS
                </strong>

                <span>
                  {
                    plantStations.filter(
                      (station) =>
                        isActiveStatus(
                          station.status,
                        ),
                    ).length
                  }{" "}
                  ONLINE
                </span>
              </div>
            </div>
          </div>

          <div className="flow-footer">
            <div>
              <span className="small-status-dot" />

              {selectedPlant
                ? `${formatStatus(
                    selectedPlant.status,
                  )} OPERATING STATE`
                : "NO PLANT DATA"}
            </div>

            <button
              type="button"
              onClick={() =>
                void loadOverview(true)
              }
              disabled={refreshing}
              style={{
                border: "none",
                background: "transparent",
                cursor: refreshing
                  ? "default"
                  : "pointer",
                font: "inherit",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                opacity: refreshing
                  ? 0.6
                  : 1,
              }}
            >
              <RefreshCw
                size={13}
                className={
                  refreshing
                    ? "spin"
                    : undefined
                }
              />

              {refreshing
                ? "REFRESHING"
                : "REFRESH"}
            </button>
          </div>
        </section>

        <section className="state-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">
                SYSTEM STATE
              </span>

              <h2>
                Operating condition
              </h2>
            </div>

            <Gauge
              size={18}
              strokeWidth={1.5}
            />
          </div>

          <div className="state-reading">
            <div className="state-number">
              {stationCoverage}%
            </div>

            <div className="state-copy">
              <strong>
                Station operational coverage
              </strong>

              <span>
                {operationalStations.length} OF{" "}
                {stations.length} STATIONS
                OPERATIONAL
              </span>
            </div>
          </div>

          <div className="state-bar">
            <div
              className="state-bar-fill"
              style={{
                width: `${stationCoverage}%`,
              }}
            />
          </div>

          <div className="state-footer">
            <span>
              {operationalStations.length} ONLINE
            </span>

            <span>
              {stations.length -
                operationalStations.length}{" "}
              OFFLINE
            </span>
          </div>
        </section>

        <section className="activity-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">
                OPERATIONAL FEED
              </span>

              <h2>Current stations</h2>
            </div>

            <Activity
              size={18}
              strokeWidth={1.5}
            />
          </div>

          <div className="activity-list">
            {lastStationStatus.length === 0 ? (
              <div className="activity-row">
                <div className="activity-content">
                  <strong>
                    No station data available
                  </strong>
                </div>
              </div>
            ) : (
              lastStationStatus.map(
                (station) => (
                  <div
                    className="activity-row"
                    key={station.station_id}
                  >
                    <div className="activity-marker">
                      <span />
                    </div>

                    <div className="activity-content">
                      <span className="activity-type">
                        {formatStatus(
                          station.station_type,
                        )}
                      </span>

                      <strong>
                        {station.name}
                      </strong>

                      <span>
                        {formatStatus(
                          station.status,
                        )}

                        {station.line_name
                          ? ` · ${station.line_name}`
                          : ""}
                      </span>
                    </div>
                  </div>
                ),
              )
            )}
          </div>
        </section>
      </div>

      {error && (
        <div
          style={{
            marginTop: "12px",
            fontSize: "11px",
            opacity: 0.65,
          }}
        >
          Latest refresh failed. Showing previously
          loaded backend data.
        </div>
      )}
    </div>
  );
}