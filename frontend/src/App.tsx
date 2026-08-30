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
import StationDetail from "./pages/StationDetail";
import Risks from "./pages/Risks";
import Simulation from "./pages/Simulation";

import "./App.css";


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
            path="/stations/:stationId"
            element={<StationDetail />}
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
              <Navigate
                to="/"
                replace
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