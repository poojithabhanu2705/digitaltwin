import {
  Activity,
  ArrowUpRight,
  Boxes,
  Clock3,
  Factory,
  Radio,
} from "lucide-react";

interface Station {
  id: string;
  name: string;
  line: string;
  type: string;
  state: "ONLINE" | "ATTENTION" | "OFFLINE";
  cycleTime: string;
  telemetry: string;
}

const stations: Station[] = [
  {
    id: "ST-101",
    name: "Component Feed",
    line: "Line 01",
    type: "Material Handling",
    state: "ONLINE",
    cycleTime: "18.4s",
    telemetry: "2s ago",
  },
  {
    id: "ST-114",
    name: "Torque Assembly",
    line: "Line 02",
    type: "Assembly",
    state: "ATTENTION",
    cycleTime: "51.8s",
    telemetry: "4s ago",
  },
  {
    id: "ST-127",
    name: "Vision Inspection",
    line: "Line 02",
    type: "Inspection",
    state: "ONLINE",
    cycleTime: "12.7s",
    telemetry: "1s ago",
  },
  {
    id: "ST-218",
    name: "Body Weld Cell",
    line: "Line 03",
    type: "Robotic Welding",
    state: "ONLINE",
    cycleTime: "58.2s",
    telemetry: "3s ago",
  },
  {
    id: "ST-231",
    name: "Surface Preparation",
    line: "Line 03",
    type: "Treatment",
    state: "ONLINE",
    cycleTime: "34.6s",
    telemetry: "2s ago",
  },
  {
    id: "ST-309",
    name: "Final Inspection",
    line: "Line 04",
    type: "Inspection",
    state: "ATTENTION",
    cycleTime: "46.9s",
    telemetry: "31s ago",
  },
  {
    id: "ST-317",
    name: "Fastener Assembly",
    line: "Line 04",
    type: "Assembly",
    state: "ONLINE",
    cycleTime: "39.8s",
    telemetry: "2s ago",
  },
  {
    id: "ST-402",
    name: "Paint Application",
    line: "Line 05",
    type: "Coating",
    state: "OFFLINE",
    cycleTime: "—",
    telemetry: "14m ago",
  },
];

function stateClass(state: Station["state"]) {
  if (state === "ONLINE") return "station-state-online";
  if (state === "ATTENTION") return "station-state-attention";
  return "station-state-offline";
}

export default function Stations() {
  const online = stations.filter(
    (station) => station.state === "ONLINE",
  ).length;

  const attention = stations.filter(
    (station) => station.state === "ATTENTION",
  ).length;

  const offline = stations.filter(
    (station) => station.state === "OFFLINE",
  ).length;

  return (
    <div className="stations-page">
      <header className="stations-heading">
        <div>
          <div className="stations-eyebrow">
            <span>04</span>
            <span>/</span>
            <span>PRODUCTION STRUCTURE</span>
          </div>

          <h1>Production stations.</h1>

          <p>
            Monitor individual production assets and the signals they are
            currently reporting.
          </p>
        </div>

        <div className="stations-summary">
          <div>
            <span>TOTAL</span>
            <strong>{stations.length}</strong>
          </div>

          <div>
            <span>ONLINE</span>
            <strong>{online}</strong>
          </div>

          <div>
            <span>ATTENTION</span>
            <strong>{attention}</strong>
          </div>

          <div className="stations-summary-offline">
            <span>OFFLINE</span>
            <strong>{offline}</strong>
          </div>
        </div>
      </header>

      <div className="stations-toolbar">
        <div className="stations-section-label">
          <Boxes size={15} strokeWidth={1.7} />
          <span>STATION NETWORK</span>
        </div>

        <div className="stations-filters">
          <button>PLANT 01</button>
          <button>ALL LINES</button>
          <button>ALL STATES</button>
        </div>
      </div>

      <section className="stations-table">
        <div className="stations-table-head">
          <span>STATION</span>
          <span>LINE</span>
          <span>TYPE</span>
          <span>STATE</span>
          <span>CYCLE TIME</span>
          <span>TELEMETRY</span>
          <span />
        </div>

        {stations.map((station) => (
          <div className="station-row" key={station.id}>
            <div className="station-name">
              <div className="station-icon">
                <Factory size={17} strokeWidth={1.7} />
              </div>

              <div>
                <strong>{station.name}</strong>
                <span>{station.id}</span>
              </div>
            </div>

            <div className="station-line">
              {station.line}
            </div>

            <div className="station-type">
              {station.type}
            </div>

            <div className={`station-state ${stateClass(station.state)}`}>
              <i />
              {station.state}
            </div>

            <div className="station-cycle">
              <Clock3 size={14} strokeWidth={1.7} />
              {station.cycleTime}
            </div>

            <div className="station-telemetry">
              <Radio size={14} strokeWidth={1.7} />
              <span>{station.telemetry}</span>
            </div>

            <button
              className="station-open"
              aria-label={`Open ${station.name}`}
            >
              <ArrowUpRight size={16} strokeWidth={1.8} />
            </button>
          </div>
        ))}
      </section>

      <footer className="stations-footer">
        <div>
          <Activity size={14} strokeWidth={1.7} />
          <span>LIVE TELEMETRY</span>
        </div>

        <span>{online} STATIONS REPORTING NOMINALLY</span>

        <span>LAST NETWORK UPDATE 05:38:21</span>
      </footer>
    </div>
  );
}
