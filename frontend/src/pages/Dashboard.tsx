import { useEffect, useState } from "react";
import { Activity, Server, ShieldCheck, RefreshCw } from "lucide-react";

import StatCard from "../components/dashboard/StatCard";
import { healthService } from "../services/health";
import type { SystemHealth } from "../services/health";

export default function Dashboard() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadHealth() {
    try {
      setError("");

      const data = await healthService.getSystemHealth();

      setHealth(data);
    } catch (err) {
      console.error("Health check failed:", err);

      setError("Unable to load system health.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    async function initializeHealth() {
      await loadHealth();
    }

    void initializeHealth();

    const interval = setInterval(() => {
      loadHealth();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[70vh] text-lg">
        Loading system health...
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-xl mx-auto mt-10 rounded-lg bg-red-100 border border-red-300 text-red-700 p-4">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">
            StreamOps Reliability Platform
          </h1>

          <p className="text-slate-500 mt-2">
            Real-time infrastructure monitoring
          </p>
        </div>

        <button
          onClick={loadHealth}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
        >
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="System Status"
          value={health?.overall_status ?? "Unknown"}
          description={`Version ${health?.version ?? "-"}`}
          icon={<ShieldCheck size={28} />}
        />

        <StatCard
          title="Services"
          value={health?.services?.length ?? 0}
          description="Active services"
          icon={<Server size={28} />}
        />

        <StatCard
          title="Uptime"
          value={`${health?.uptime ?? 0}s`}
          description="System running time"
          icon={<Activity size={28} />}
        />
      </div>

      {/* Service Health */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-xl font-bold mb-5">
          Service Health
        </h2>

        {health?.services?.length ? (
          <div className="space-y-4">
            {health.services.map((service) => (
              <div
                key={service.service}
                className="flex justify-between items-center p-4 bg-slate-50 rounded-lg"
              >
                <div>
                  <p className="font-semibold">
                    {service.service}
                  </p>

                  <p className="text-sm text-slate-500">
                    Latency: {service.latency_ms} ms
                  </p>

                  <p className="text-xs text-slate-400">
                    Last Check:{" "}
                    {new Date(service.last_check).toLocaleString()}
                  </p>
                </div>

                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    service.status === "healthy"
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {service.status}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">
            No service information available.
          </p>
        )}
      </div>
    </div>
  );
}