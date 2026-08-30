import { useEffect, useState } from "react";
import { getPlants, type Plant } from "./api/plant";

function App() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadPlants() {
      try {
        const data = await getPlants();
        setPlants(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load plants from Django API.");
      } finally {
        setLoading(false);
      }
    }

    loadPlants();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">
          TwinSight
        </h1>

        <p className="text-slate-400 mb-8">
          Digital Twin Dashboard
        </p>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-xl font-semibold mb-4">
            Plants
          </h2>

          {loading && (
            <p className="text-slate-400">
              Loading plants...
            </p>
          )}

          {error && (
            <p className="text-red-400">
              {error}
            </p>
          )}

          {!loading && !error && plants.length === 0 && (
            <p className="text-slate-400">
              No plants found.
            </p>
          )}

          {!loading && !error && plants.length > 0 && (
            <div className="space-y-3">
              {plants.map((plant) => (
                <div
                  key={plant.plant_id}
                  className="rounded-lg border border-slate-800 bg-slate-950 p-4"
                >
                  <div className="font-medium">
                    {plant.name}
                  </div>

                  <div className="text-sm text-slate-400">
                    {plant.plant_id}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;