import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import AppShell from "./components/layout/AppShell";

import OverviewPage from "./pages/OverviewPage";
import Plants from "./pages/Plants";
import Lines from "./pages/Lines";
import Stations from "./pages/Stations";
import Risks from "./pages/Risks";
import Simulation from "./pages/Simulation";

import "./App.css";


function Placeholder({
  number,
  title,
}: {
  number: string;
  title: string;
}) {
  return (
    <div className="placeholder-page">

      <div className="eyebrow">
        <span>{number}</span>
        <span>/</span>
        <span>TWINSIGHT OPERATIONS</span>
      </div>

      <h1>{title}</h1>

      <p>
        This operational view is being prepared for
        the TwinSight plant network.
      </p>

    </div>
  );
}


export default function App() {
  return (
    <BrowserRouter>

      <AppShell>

        <Routes>

          <Route
            path="/"
            element={<OverviewPage />}
          />

          <Route
            path="/plants"
            element={<Plants />}
          />

          <Route
            path="/lines"
            element={<Lines />}
          />

          <Route
            path="/stations"
            element={<Stations />}
          />

          <Route
            path="/risks"
            element={<Risks />}
          />

          <Route
            path="/simulation"
            element={<Simulation />}
          />

          <Route
            path="/settings"
            element={
              <Placeholder
                number="07"
                title="System settings."
              />
            }
          />

          <Route
            path="*"
            element={
              <Navigate
                to="/"
                replace
              />
            }
          />

        </Routes>

      </AppShell>

    </BrowserRouter>
  );
}