import { useEffect, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  Boxes,
  Factory,
  RefreshCw,
} from "lucide-react";

import {
  getStations,
} from "../api/stations";

import type { Station } from "../types/api";

function normalizedStatus(
  station: Station,
) {
  const value = String(
    station.status ?? "",
  ).toUpperCase();

  if (
    [
      "ONLINE",
      "ACTIVE",
      "NOMINAL",
      "OPERATIONAL",
    ].includes(value)
  ) {
    return "ONLINE";
  }

  if (
    ["OFFLINE", "INACTIVE", "DOWN"].includes(
      value,
    )
  ) {
    return "OFFLINE";
  }

  return value
    ? "ATTENTION"
    : "UNKNOWN";
}

export default function Stations() {
  const [stations, setStations] =
    useState<Station[]>([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] =
    useState(false);
  const [error, setError] = useState("");

  async function load(
    forceRefresh = false,
  ) {
    try {
      if (forceRefresh) {
        setRefreshing(true);
      } else if (stations.length === 0) {
        setLoading(true);
      }

      setError("");

      const data =
        await getStations(forceRefresh);

      setStations(data);
    } catch (err) {
      console.error(
        "Failed to load stations:",
        err,
      );

      setError(
        "Unable to load production stations.",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const online = stations.filter(
    (station) =>
      normalizedStatus(station) ===
      "ONLINE",
  ).length;

  const attention = stations.filter(
    (station) =>
      normalizedStatus(station) ===
      "ATTENTION",
  ).length;

  const offline = stations.filter(
    (station) =>
      normalizedStatus(station) ===
      "OFFLINE",
  ).length;

  return (
    <div className="stations-page">
      <header className="stations-heading">
        <div>
          <div className="stations-eyebrow">
            <span>04</span>
            <span>/</span>
            <span>
              PRODUCTION STRUCTURE
            </span>
          </div>

          <h1>Production stations.</h1>

          <p>
            Monitor individual production assets
            and their current configuration.
          </p>
        </div>

        <div className="stations-summary">
          <div>
            <span>TOTAL</span>

            <strong>
              {loading
                ? "—"
                : stations.length}
            </strong>
          </div>

          <div>
            <span>ONLINE</span>

            <strong>
              {loading ? "—" : online}
            </strong>
          </div>

          <div>
            <span>ATTENTION</span>

            <strong>
              {loading
                ? "—"
                : attention}
            </strong>
          </div>

          <div className="stations-summary-offline">
            <span>OFFLINE</span>

            <strong>
              {loading
                ? "—"
                : offline}
            </strong>
          </div>
        </div>
      </header>

      <div className="stations-toolbar">
        <div className="stations-section-label">
          <Boxes
            size={15}
            strokeWidth={1.7}
          />

          <span>STATION NETWORK</span>
        </div>

        {!loading && !error && (
          <span>
            {stations.length} BACKEND RECORDS
          </span>
        )}
      </div>

      {loading && (
        <div className="lines-state">
          <RefreshCw size={20} />

          <strong>
            LOADING STATIONS
          </strong>

          <span>
            Retrieving production structure.
          </span>
        </div>
      )}

      {!loading &&
        error &&
        stations.length === 0 && (
          <div className="lines-state lines-state-error">
            <strong>{error}</strong>

            <button
              className="lines-retry"
              onClick={() =>
                void load(true)
              }
              type="button"
            >
              TRY AGAIN

              <ArrowUpRight size={15} />
            </button>
          </div>
        )}

      {!loading &&
        stations.length > 0 && (
          <section className="stations-table">
            <div className="stations-table-head">
              <span>STATION</span>
              <span>LINE</span>
              <span>TYPE</span>
              <span>STATE</span>
              <span>SEQUENCE</span>
              <span>ID</span>
              <span />
            </div>

            {stations.map((station) => {
              const state =
                normalizedStatus(station);

              return (
                <div
                  className="station-row"
                  key={station.station_id}
                >
                  <div className="station-name">
                    <div className="station-icon">
                      <Factory
                        size={17}
                        strokeWidth={1.7}
                      />
                    </div>

                    <div>
                      <strong>
                        {station.name}
                      </strong>

                      <span>
                        {station.station_id}
                      </span>
                    </div>
                  </div>

                  <div className="station-line">
                    {station.line_name ||
                      station.line_id ||
                      "—"}
                  </div>

                  <div className="station-type">
                    {String(
                      station.station_type ??
                        "—",
                    )}
                  </div>

                  <div
                    className={`station-state station-state-${state.toLowerCase()}`}
                  >
                    <i />

                    {state}
                  </div>

                  <div className="station-cycle">
                    {station.sequence_number ??
                      "—"}
                  </div>

                  <div className="station-telemetry">
                    <Activity size={14} />

                    <span>
                      {station.station_id}
                    </span>
                  </div>

                  <button
                    className="station-open"
                    aria-label={`Open ${station.name}`}
                    type="button"
                  >
                    <ArrowUpRight
                      size={16}
                      strokeWidth={1.8}
                    />
                  </button>
                </div>
              );
            })}
          </section>
        )}

      {!loading &&
        !error &&
        stations.length > 0 && (
          <>
            <footer className="stations-footer">
              <div>
                <Activity size={14} />

                <span>
                  LIVE BACKEND DATA
                </span>
              </div>

              <span>
                {stations.length} STATIONS
                LOADED
              </span>

              <span>DJANGO API</span>

              <button
                type="button"
                onClick={() =>
                  void load(true)
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
            </footer>
          </>
        )}
    </div>
  );
}