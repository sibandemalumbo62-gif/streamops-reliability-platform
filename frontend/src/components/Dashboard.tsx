import { useState, useEffect } from 'react';
import { healthService } from '../services/health';
import { Activity, Server, AlertCircle, CheckCircle } from 'lucide-react';

export default function Dashboard() {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHealth();
    const interval = setInterval(loadHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadHealth = async () => {
    try {
      const data = await healthService.getSystemHealth();
      setHealth(data);
      setError('');
    } catch (error: any) {
      console.error('Failed to load health:', error);
      setError('Failed to load system health. Backend may not be running.');
      // Set mock data for demo
      setHealth({
        overall_status: 'healthy',
        services: [
          { service: 'API Gateway', status: 'healthy', latency_ms: 45, last_check: new Date().toISOString() },
          { service: 'Auth Service', status: 'healthy', latency_ms: 32, last_check: new Date().toISOString() },
          { service: 'Catalog Service', status: 'healthy', latency_ms: 28, last_check: new Date().toISOString() },
          { service: 'Playback Service', status: 'healthy', latency_ms: 67, last_check: new Date().toISOString() },
          { service: 'Database', status: 'healthy', latency_ms: 12, last_check: new Date().toISOString() },
        ],
        uptime: 86400,
        version: '1.0.0',
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">MediaStream Platform</h1>
      
      {error && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">System Status</h2>
            {health?.overall_status === 'healthy' ? (
              <CheckCircle className="text-green-500" size={24} />
            ) : (
              <AlertCircle className="text-red-500" size={24} />
            )}
          </div>
          <p className="text-2xl font-bold">{health?.overall_status || 'Unknown'}</p>
          <p className="text-gray-600 text-sm">Uptime: {Math.floor((health?.uptime || 0) / 3600)}h</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Services</h2>
            <Server className="text-blue-500" size={24} />
          </div>
          <p className="text-2xl font-bold">{health?.services?.length || 0}</p>
          <p className="text-gray-600 text-sm">Active services</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Activity</h2>
            <Activity className="text-purple-500" size={24} />
          </div>
          <p className="text-2xl font-bold">Live</p>
          <p className="text-gray-600 text-sm">System monitoring</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Service Health</h2>
        <div className="space-y-3">
          {health?.services?.map((service: any) => (
            <div key={service.service} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div>
                <p className="font-medium">{service.service}</p>
                <p className="text-sm text-gray-600">Latency: {service.latency_ms}ms</p>
              </div>
              <div className="flex items-center">
                {service.status === 'healthy' ? (
                  <CheckCircle className="text-green-500" size={20} />
                ) : (
                  <AlertCircle className="text-red-500" size={20} />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
