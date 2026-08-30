import {
  Activity,
  ArrowRight,
  Factory,
  Gauge,
  GitBranch,
  Layers3,
  TriangleAlert,
} from "lucide-react";

export default function OverviewPage() {
  return (
    <div className="overview">

      {/* Page heading */}

      <div className="overview-heading">
        <div>
          <div className="eyebrow">01 / PLANT OVERVIEW</div>

          <h1>Operations at a glance.</h1>

          <p>
            A live view of production, assets and emerging operational
            conditions.
          </p>
        </div>

        <div className="overview-live">
          <span className="live-dot" />
          LIVE DATA
        </div>
      </div>

      {/* Metrics */}

      <section className="metric-rail">

        <div className="metric">
          <span className="metric-label">PRODUCTION</span>

          <div className="metric-value">
            84<span className="metric-unit">%</span>
          </div>

          <div className="metric-note">CURRENT THROUGHPUT</div>
        </div>

        <div className="metric">
          <span className="metric-label">ACTIVE LINES</span>

          <div className="metric-value">12</div>

          <div className="metric-note">OF 14 CONFIGURED</div>
        </div>

        <div className="metric">
          <span className="metric-label">STATIONS</span>

          <div className="metric-value">47</div>

          <div className="metric-note">41 OPERATIONAL</div>
        </div>

        <div className="metric">
          <span className="metric-label">OPEN RISKS</span>

          <div className="metric-value">03</div>

          <div className="metric-note">1 HIGH PRIORITY</div>
        </div>

      </section>

      {/* Main dashboard */}

      <div className="operations-grid">

        {/* Plant flow */}

        <section className="flow-panel">

          <div className="panel-heading">
            <div>
              <span className="panel-kicker">
                PRODUCTION STRUCTURE
              </span>

              <h2>Plant flow</h2>
            </div>

            <Factory size={18} strokeWidth={1.5} />
          </div>

          <div className="flow-map">

            <div className="flow-node flow-node-primary">
              <div className="flow-icon">
                <Factory size={17} strokeWidth={1.5} />
              </div>

              <div>
                <strong>PLANT 01</strong>
                <span>MAIN FACILITY</span>
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
                <strong>14 LINES</strong>
                <span>12 ACTIVE</span>
              </div>
            </div>

            <ArrowRight
              className="flow-arrow"
              size={20}
              strokeWidth={1.3}
            />

            <div className="flow-node">
              <div className="flow-icon">
                <Layers3 size={17} strokeWidth={1.5} />
              </div>

              <div>
                <strong>47 STATIONS</strong>
                <span>41 ONLINE</span>
              </div>
            </div>

          </div>

          <div className="flow-footer">
            <div>
              <span className="small-status-dot" />
              NOMINAL OPERATING STATE
            </div>

            <span>LAST SYNC 05:38:21</span>
          </div>

        </section>

        {/* Operating condition */}

        <section className="state-panel">

          <div className="panel-heading">
            <div>
              <span className="panel-kicker">SYSTEM STATE</span>
              <h2>Operating condition</h2>
            </div>

            <Gauge size={18} strokeWidth={1.5} />
          </div>

          <div className="state-reading">

            <div className="state-number">
              84%
            </div>

            <div className="state-copy">
              <strong>Production efficiency</strong>
              <span>+3.2% FROM PREVIOUS SHIFT</span>
            </div>

          </div>

          <div className="state-bar">
            <div className="state-bar-fill" />
          </div>

          <div className="state-footer">
            <span>TARGET 80%</span>
            <span>PEAK 91%</span>
          </div>

        </section>

        {/* Recent activity */}

        <section className="activity-panel">

          <div className="panel-heading">
            <div>
              <span className="panel-kicker">
                OPERATIONAL FEED
              </span>

              <h2>Recent activity</h2>
            </div>

            <Activity size={18} strokeWidth={1.5} />
          </div>

          <div className="activity-list">

            <div className="activity-row">
              <time className="activity-time">05:38</time>

              <div className="activity-marker">
                <span />
              </div>

              <div className="activity-content">
                <span className="activity-type">LINE</span>

                <strong>
                  Assembly Line 04 resumed
                </strong>

                <span>
                  Cycle time returned to nominal range
                </span>
              </div>
            </div>

            <div className="activity-row">
              <time className="activity-time">05:31</time>

              <div className="activity-marker">
                <span />
              </div>

              <div className="activity-content">
                <span className="activity-type">STATION</span>

                <strong>
                  Station ST-218 telemetry received
                </strong>

                <span>
                  All monitored signals within expected range
                </span>
              </div>
            </div>

            <div className="activity-row">
              <time className="activity-time">05:24</time>

              <div className="activity-marker">
                <span />
              </div>

              <div className="activity-content">
                <span className="activity-type">PRODUCTION</span>

                <strong>
                  Throughput target updated
                </strong>

                <span>
                  Shift target increased to 86%
                </span>
              </div>
            </div>

          </div>

        </section>

        {/* Risk board */}

        <section className="risk-panel">

          <div className="panel-heading">
            <div>
              <span className="panel-kicker">
                ATTENTION REQUIRED
              </span>

              <h2>Risk board</h2>
            </div>

            <TriangleAlert size={18} strokeWidth={1.5} />
          </div>

          <div className="risk-count">
            <strong>03</strong>
            <span>OPEN CONDITIONS</span>
          </div>

          <div className="risk-item risk-high">
            <span className="risk-marker" />

            <div>
              <strong>Material availability</strong>
              <span>LINE 07 · HIGH</span>
            </div>
          </div>

          <div className="risk-item">
            <span className="risk-marker" />

            <div>
              <strong>Cycle time variance</strong>
              <span>STATION ST-218 · MEDIUM</span>
            </div>
          </div>

          <div className="risk-item">
            <span className="risk-marker" />

            <div>
              <strong>Telemetry interruption</strong>
              <span>LINE 03 · LOW</span>
            </div>
          </div>

          <button className="risk-link">
            VIEW ALL CONDITIONS
            <ArrowRight size={13} strokeWidth={1.5} />
          </button>

        </section>

      </div>

      <div className="overview-footer">
        <div>
          <span className="small-status-dot" />
          SYSTEM NOMINAL
        </div>

        <span>TWINSIGHT DIGITAL TWIN</span>
      </div>

    </div>
  );
}