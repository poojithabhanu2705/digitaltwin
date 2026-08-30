import {
  Activity,
  Factory,
  Gauge,
  GitBranch,
  Layers3,
  Settings,
  TriangleAlert,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const navigation = [
  { label: "Overview", path: "/", icon: Activity },
  { label: "Plants", path: "/plants", icon: Factory },
  { label: "Lines", path: "/lines", icon: GitBranch },
  { label: "Stations", path: "/stations", icon: Layers3 },
  { label: "Risks", path: "/risks", icon: TriangleAlert },
  { label: "Simulation", path: "/simulation", icon: Gauge },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">TS</div>

        <div>
          <div className="brand-name">TWINSIGHT</div>
          <div className="brand-subtitle">INDUSTRIAL INTELLIGENCE</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigation.map(({ label, path, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `nav-item ${isActive ? "nav-item-active" : ""}`
            }
          >
            <Icon size={17} strokeWidth={1.8} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <NavLink to="/settings" className="nav-item">
          <Settings size={17} strokeWidth={1.8} />
          <span>Settings</span>
        </NavLink>

        <div className="system-status">
          <span className="status-dot" />
          <span>SYSTEM ONLINE</span>
        </div>
      </div>
    </aside>
  );
}
