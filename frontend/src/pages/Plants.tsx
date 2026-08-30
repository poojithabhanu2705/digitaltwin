import {
  ArrowRight,
  Factory,
  MapPin,
  Activity,
} from "lucide-react";

const plants = [
  {
    id: "01",
    name: "Plant 01",
    location: "Bengaluru, India",
    lines: 14,
    stations: 47,
    throughput: "84%",
    status: "NOMINAL",
    active: true,
  },
  {
    id: "02",
    name: "Plant 02",
    location: "Pune, India",
    lines: 11,
    stations: 39,
    throughput: "78%",
    status: "NOMINAL",
    active: true,
  },
  {
    id: "03",
    name: "Plant 03",
    location: "Chennai, India",
    lines: 16,
    stations: 52,
    throughput: "71%",
    status: "ATTENTION",
    active: false,
  },
];

export default function Plants() {
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
            A consolidated view of connected manufacturing facilities.
          </p>
        </div>

        <div className="page-count">
          <span>CONNECTED PLANTS</span>
          <strong>03</strong>
          <small>ALL FACILITIES</small>
        </div>
      </header>

      <div className="plants-section-label">
        <span>FACILITIES</span>
        <span>3 REGISTERED</span>
      </div>

      <section className="plants-grid">
        {plants.map((plant) => (
          <article className="plant-card" key={plant.id}>
            <div className="plant-card-top">
              <span className="plant-index">PLANT / {plant.id}</span>

              <div
                className={`plant-status ${
                  plant.active ? "plant-status-active" : ""
                }`}
              >
                <span />
                {plant.status}
              </div>
            </div>

            <div className="plant-icon">
              <Factory size={23} strokeWidth={1.6} />
            </div>

            <h2>{plant.name}</h2>

            <div className="plant-location">
              <MapPin size={13} strokeWidth={1.6} />
              <span>{plant.location}</span>
            </div>

            <div className="plant-card-footer">
              <div>
                <span>LINES</span>
                <strong>{plant.lines}</strong>
              </div>

              <div>
                <span>STATIONS</span>
                <strong>{plant.stations}</strong>
              </div>

              <div>
                <span>THROUGHPUT</span>
                <strong>{plant.throughput}</strong>
              </div>

              <button
                className="plant-open"
                aria-label={`Open ${plant.name}`}
              >
                <ArrowRight size={16} strokeWidth={1.7} />
              </button>
            </div>
          </article>
        ))}
      </section>

      <section className="plants-network-strip">
        <div className="plants-network-main">
          <div className="plants-network-icon">
            <Activity size={18} strokeWidth={1.6} />
          </div>

          <div>
            <div className="panel-kicker">NETWORK STATE</div>
            <h2>Connected manufacturing network</h2>
          </div>
        </div>

        <div className="plants-network-stats">
          <div>
            <span>LINES</span>
            <strong>41</strong>
          </div>

          <div>
            <span>STATIONS</span>
            <strong>138</strong>
          </div>

          <div>
            <span>DATA SOURCES</span>
            <strong>138 / 138</strong>
          </div>
        </div>
      </section>
    </div>
  );
}
