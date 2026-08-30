import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Activity,
  ArrowRight,
  Factory,
  MapPin,
  RefreshCw,
} from "lucide-react";

import { getPlants } from "../api/plants";
import { getLines } from "../api/lines";
import { getStations } from "../api/stations";

import type { Plant } from "../types/api";

export default function Plants() {
  const navigate = useNavigate();
  const [plants, setPlants] =
    useState<Plant[]>([]);

  const [lineCounts, setLineCounts] =
    useState<Record<string, number>>({});

  const [stationCounts, setStationCounts] =
    useState<Record<string, number>>({});

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState("");

  async function load(
    forceRefresh = false,
  ) {
    try {
      if (forceRefresh) {
        setRefreshing(true);
      } else if (plants.length === 0) {
        setLoading(true);
      }

      setError("");

      const [
        plantData,
        lineData,
        stationData,
      ] = await Promise.all([
        getPlants(forceRefresh),
        getLines(forceRefresh),
        getStations(forceRefresh),
      ]);

      const linesByPlant: Record<
        string,
        number
      > = {};

      lineData.forEach((line) => {
        linesByPlant[line.plant_id] =
          (linesByPlant[line.plant_id] ?? 0) +
          1;
      });

      const stationsByPlant: Record<
        string,
        number
      > = {};

      stationData.forEach((station) => {
        const plantId = String(
          station.plant_id ?? "",
        );

        if (plantId) {
          stationsByPlant[plantId] =
            (stationsByPlant[plantId] ?? 0) +
            1;
        }
      });

      setPlants(plantData);
      setLineCounts(linesByPlant);
      setStationCounts(stationsByPlant);
    } catch (err) {
      console.error(
        "Failed to load plants:",
        err,
      );

      setError(
        "Unable to load plant network.",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const totalLines =
    Object.values(lineCounts).reduce(
      (a, b) => a + b,
      0,
    );

  const totalStations =
    Object.values(stationCounts).reduce(
      (a, b) => a + b,
      0,
    );

  return (
    <div className="plants-page">
      <header className="page-intro">
        <div>
          <div className="eyebrow">
            <span>02</span>
            <span>/</span>
            <span>PLANT NETWORK</span>
          </div>

          <h1>Plant network.</h1>

          <p>
            A consolidated view of connected
            manufacturing facilities.
          </p>
        </div>

        <div className="page-count">
          <span>CONNECTED PLANTS</span>

          <strong>
            {loading
              ? "—"
              : String(plants.length).padStart(
                  2,
                  "0",
                )}
          </strong>

          <small>
            LIVE FROM BACKEND
          </small>
        </div>
      </header>

      {loading && (
        <div className="lines-state">
          <RefreshCw size={20} />

          <strong>
            LOADING PLANT NETWORK
          </strong>

          <span>
            Retrieving current master data.
          </span>
        </div>
      )}

      {!loading &&
        error &&
        plants.length === 0 && (
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

              <ArrowRight size={15} />
            </button>
          </div>
        )}

      {!loading &&
        plants.length > 0 && (
          <>
            <div className="plants-section-label">
              <span>FACILITIES</span>

              <span>
                {plants.length} REGISTERED
              </span>
            </div>

            <section className="plants-grid">
              {plants.map((plant) => {
                const active =
                  String(
                    plant.status,
                  ).toUpperCase() ===
                  "ACTIVE";

                return (
                  <article
                    className="plant-card"
                    key={plant.plant_id}
                  >
                    <div className="plant-card-top">
                      <span className="plant-index">
                        PLANT /{" "}
                        {plant.plant_id}
                      </span>

                      <div
                        className={`plant-status ${
                          active
                            ? "plant-status-active"
                            : ""
                        }`}
                      >
                        <span />

                        {plant.status ||
                          "UNKNOWN"}
                      </div>
                    </div>

                    <div className="plant-icon">
                      <Factory
                        size={23}
                        strokeWidth={1.6}
                      />
                    </div>

                    <h2>{plant.name}</h2>

                    <div className="plant-location">
                      <MapPin
                        size={13}
                        strokeWidth={1.6}
                      />

                      <span>
                        {plant.location ||
                          "LOCATION NOT SET"}
                      </span>
                    </div>

                    <div className="plant-card-footer">
                      <div>
                        <span>
                          LINES
                        </span>

                        <strong>
                          {lineCounts[
                            plant.plant_id
                          ] ?? 0}
                        </strong>
                      </div>

                      <div>
                        <span>
                          STATIONS
                        </span>

                        <strong>
                          {stationCounts[
                            plant.plant_id
                          ] ?? 0}
                        </strong>
                      </div>

                      <div>
                        <span>
                          STATUS
                        </span>

                        <strong>
                          {active
                            ? "ACTIVE"
                            : plant.status ||
                              "—"}
                        </strong>
                      </div>

                      <button
                        className="plant-open"
                        aria-label={`Open ${plant.name}`}
                        type="button"
                        onClick={() => navigate(`/lines?plant_id=${plant.plant_id}`)}
                      >
                        <ArrowRight
                          size={16}
                          strokeWidth={1.7}
                        />
                      </button>
                    </div>
                  </article>
                );
              })}
            </section>

            <section className="plants-network-strip">
              <div className="plants-network-main">
                <div className="plants-network-icon">
                  <Activity
                    size={18}
                    strokeWidth={1.6}
                  />
                </div>

                <div>
                  <div className="panel-kicker">
                    NETWORK STATE
                  </div>

                  <h2>
                    Connected manufacturing
                    network
                  </h2>
                </div>
              </div>

              <div className="plants-network-stats">
                <div>
                  <span>LINES</span>

                  <strong>
                    {totalLines}
                  </strong>
                </div>

                <div>
                  <span>STATIONS</span>

                  <strong>
                    {totalStations}
                  </strong>
                </div>

                <div>
                  <span>PLANTS</span>

                  <strong>
                    {plants.length}
                  </strong>
                </div>
              </div>
            </section>

            <div
              style={{
                marginTop: "16px",
                display: "flex",
                justifyContent:
                  "flex-end",
              }}
            >
              <button
                type="button"
                onClick={() =>
                  void load(true)
                }
                disabled={refreshing}
                style={{
                  border: "none",
                  background:
                    "transparent",
                  cursor: refreshing
                    ? "default"
                    : "pointer",
                  font: "inherit",
                  display: "flex",
                  alignItems:
                    "center",
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
                  : "REFRESH DATA"}
              </button>
            </div>
          </>
        )}
    </div>
  );
}