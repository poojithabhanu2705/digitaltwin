import { useEffect, useState, useMemo } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  Factory,
  GitBranch,
  Layers3,
  RefreshCw,
} from "lucide-react";

import {
  getLines,
  type ProductionLine,
} from "../api/lines";

export default function Lines() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const plantIdFilter = searchParams.get("plant_id") || "";

  const [lines, setLines] = useState<
    ProductionLine[]
  >([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] =
    useState(false);
  const [error, setError] = useState("");

  async function loadLines(forceRefresh = false) {
    try {
      if (forceRefresh) {
        setRefreshing(true);
      } else if (lines.length === 0) {
        setLoading(true);
      }

      setError("");

      const data = await getLines(forceRefresh);

      setLines(data);
    } catch (err) {
      console.error(
        "Failed to load lines:",
        err,
      );

      setError(
        "Unable to load production lines.",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void loadLines();
  }, []);

  const filteredLines = useMemo(() => {
    if (!plantIdFilter) return lines;
    return lines.filter((line) => line.plant_id === plantIdFilter);
  }, [lines, plantIdFilter]);

  const activeCount = filteredLines.filter(
    (line) =>
      line.status.toUpperCase() === "ACTIVE",
  ).length;

  return (
    <div className="lines-page">
      <header className="page-intro">
        <div>
          <div className="eyebrow">
            03 / PRODUCTION LINES
          </div>

          <h1>Production lines.</h1>

          <p>
            Monitor the production structure and
            operating state of each line.
          </p>
        </div>

        <div className="page-count">
          <span>CONFIGURED LINES</span>

          <strong>
            {String(filteredLines.length).padStart(
              2,
              "0",
            )}
          </strong>

          <small>
            {activeCount} ACTIVE
          </small>
        </div>
      </header>

      {plantIdFilter && (
        <div style={{ marginBottom: "22px", fontSize: "12px", display: "flex", gap: "10px", alignItems: "center" }}>
          <span style={{ color: "var(--brown)", opacity: 0.8 }}>Filtering lines for Plant: <strong>{plantIdFilter}</strong></span>
          <button
            onClick={() => setSearchParams({})}
            style={{
              background: "transparent",
              border: "1px solid rgba(73, 49, 43, 0.4)",
              padding: "4px 8px",
              cursor: "pointer",
              fontSize: "10px",
              fontWeight: "600",
              color: "var(--brown)",
              fontFamily: "var(--font-mono)",
            }}
          >
            CLEAR FILTER
          </button>
        </div>
      )}

      <div className="lines-section-label">
        <span>LINE NETWORK</span>

        {!loading &&
          !error &&
          filteredLines.length > 0 && (
            <span>
              {activeCount} / {filteredLines.length} ACTIVE
            </span>
          )}
      </div>

      {loading && (
        <div className="lines-state">
          <RefreshCw size={20} />

          <strong>
            LOADING PRODUCTION LINES
          </strong>

          <span>
            Retrieving current line
            configuration.
          </span>
        </div>
      )}

      {!loading && error && lines.length === 0 && (
        <div className="lines-state lines-state-error">
          <GitBranch size={22} />

          <strong>{error}</strong>

          <span>
            Check that the backend service is
            running.
          </span>

          <button
            className="lines-retry"
            onClick={() =>
              void loadLines(true)
            }
            type="button"
          >
            TRY AGAIN

            <ArrowRight size={15} />
          </button>
        </div>
      )}

      {!loading &&
        !error &&
        lines.length === 0 && (
          <div className="lines-state">
            <GitBranch size={26} />

            <strong>
              No production lines configured.
            </strong>

            <span>
              Production lines will appear here
              once master data is configured.
            </span>
          </div>
        )}

      {!loading &&
        filteredLines.length > 0 && (
          <section className="lines-grid">
            {filteredLines.map((line, index) => {
              const isActive =
                line.status.toUpperCase() ===
                "ACTIVE";

              return (
                <article
                  className="line-card"
                  key={line.line_id}
                >
                  <div className="line-card-top">
                    <span className="line-index">
                      {String(index + 1).padStart(
                        2,
                        "0",
                      )}
                    </span>

                    <div
                      className={`line-status ${
                        isActive
                          ? "line-status-active"
                          : ""
                      }`}
                    >
                      <span />

                      {line.status}
                    </div>
                  </div>

                  <div className="line-icon">
                    <GitBranch
                      size={22}
                      strokeWidth={1.6}
                    />
                  </div>

                  <div className="line-card-heading">
                    <div>
                      <span className="line-id">
                        {line.line_id}
                      </span>

                      <h2>{line.name}</h2>
                    </div>
                  </div>

                  <div className="line-meta">
                    <div>
                      <Factory
                        size={14}
                        strokeWidth={1.6}
                      />

                      <div>
                        <span>PLANT</span>

                        <strong>
                          {line.plant_name}
                        </strong>
                      </div>
                    </div>

                    <div>
                      <Layers3
                        size={14}
                        strokeWidth={1.6}
                      />

                      <div>
                        <span>
                          LINE TYPE
                        </span>

                        <strong>
                          {line.line_type ||
                            "NOT SPECIFIED"}
                        </strong>
                      </div>
                    </div>
                  </div>

                  {line.description && (
                    <p className="line-description">
                      {line.description}
                    </p>
                  )}

                  <footer className="line-card-footer">
                    <span>
                      LINE CONFIGURATION
                    </span>

                    <button
                      type="button"
                      className="line-open"
                      aria-label={`Open ${line.name}`}
                      onClick={() => navigate(`/stations?line_id=${line.line_id}`)}
                    >
                      <ArrowRight
                        size={16}
                        strokeWidth={1.7}
                      />
                    </button>
                  </footer>
                </article>
              );
            })}
          </section>
        )}

      {!loading && !error && lines.length > 0 && (
        <div
          style={{
            marginTop: "16px",
            display: "flex",
            justifyContent: "flex-end",
          }}
        >
          <button
            type="button"
            onClick={() =>
              void loadLines(true)
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
              opacity: refreshing ? 0.6 : 1,
            }}
          >
            <RefreshCw
              size={13}
              className={
                refreshing ? "spin" : undefined
              }
            />

            {refreshing
              ? "REFRESHING"
              : "REFRESH DATA"}
          </button>
        </div>
      )}
    </div>
  );
}