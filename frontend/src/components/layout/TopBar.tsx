import { ChevronDown, Circle } from "lucide-react";

export default function TopBar() {
  return (
    <header className="topbar">
      <div className="topbar-left">
        <div className="section-marker">
          <span />
          OPERATIONS
        </div>

        <div className="topbar-path">
          PLANT NETWORK
        </div>
      </div>

      <div className="topbar-right">
        <button className="plant-selector">
          <span className="plant-indicator" />

          <span className="plant-selector-label">
            ACTIVE PLANT
          </span>

          <strong>PLANT 01</strong>

          <ChevronDown size={14} strokeWidth={1.7} />
        </button>

        <div className="topbar-clock">
          <span className="clock-label">LOCAL</span>
          <strong>05:42</strong>
        </div>

        <div className="connection-state">
          <Circle size={7} fill="currentColor" strokeWidth={0} />
        </div>
      </div>
    </header>
  );
}
