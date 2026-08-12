import { useState } from 'react';
import { BarChart3, Activity, AlertTriangle, TrendingUp } from 'lucide-react';

export default function Monitoring() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Monitoring Dashboard</h1>
      
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'overview' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab('metrics')}
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'metrics' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          Metrics
        </button>
        <button
          onClick={() => setActiveTab('alerts')}
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'alerts' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          Alerts
        </button>
        <button
          onClick={() => setActiveTab('slos')}
          className={`px-4 py-2 rounded-lg ${
            activeTab === 'slos' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          SLOs
        </button>
      </div>

      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'metrics' && <MetricsTab />}
      {activeTab === 'alerts' && <AlertsTab />}
      {activeTab === 'slos' && <SLOsTab />}
    </div>
  );
}

function OverviewTab() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Uptime</h3>
            <Activity className="text-green-500" size={24} />
          </div>
          <p className="text-3xl font-bold">99.95%</p>
          <p className="text-sm text-gray-600">Last 30 days</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Error Rate</h3>
            <AlertTriangle className="text-yellow-500" size={24} />
          </div>
          <p className="text-3xl font-bold">0.05%</p>
          <p className="text-sm text-gray-600">Last 24h</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Latency</h3>
            <TrendingUp className="text-blue-500" size={24} />
          </div>
          <p className="text-3xl font-bold">45ms</p>
          <p className="text-sm text-gray-600">p95 latency</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Requests</h3>
            <BarChart3 className="text-purple-500" size={24} />
          </div>
          <p className="text-3xl font-bold">12.5k</p>
          <p className="text-sm text-gray-600">Requests/min</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Grafana Dashboard</h2>
        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-600 mb-4">Grafana Dashboard Integration</p>
            <a
              href="http://localhost:3000"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Open Grafana
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricsTab() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">System Metrics</h2>
        <div className="space-y-4">
          <div className="p-4 bg-gray-50 rounded">
            <h3 className="font-medium mb-2">CPU Usage</h3>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div className="bg-blue-500 h-4 rounded-full" style={{ width: '45%' }}></div>
            </div>
            <p className="text-sm text-gray-600 mt-2">45% average</p>
          </div>

          <div className="p-4 bg-gray-50 rounded">
            <h3 className="font-medium mb-2">Memory Usage</h3>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div className="bg-green-500 h-4 rounded-full" style={{ width: '62%' }}></div>
            </div>
            <p className="text-sm text-gray-600 mt-2">62% average</p>
          </div>

          <div className="p-4 bg-gray-50 rounded">
            <h3 className="font-medium mb-2">Disk I/O</h3>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div className="bg-yellow-500 h-4 rounded-full" style={{ width: '28%' }}></div>
            </div>
            <p className="text-sm text-gray-600 mt-2">28% average</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function AlertsTab() {
  const alerts = [
    { id: 1, severity: 'critical', message: 'High error rate detected in auth service', time: '5 min ago' },
    { id: 2, severity: 'warning', message: 'Memory usage above 80% on catalog service', time: '15 min ago' },
    { id: 3, severity: 'info', message: 'Scheduled maintenance window starting in 1 hour', time: '1 hour ago' },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Active Alerts</h2>
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border-l-4 ${
                alert.severity === 'critical'
                  ? 'bg-red-50 border-red-500'
                  : alert.severity === 'warning'
                  ? 'bg-yellow-50 border-yellow-500'
                  : 'bg-blue-50 border-blue-500'
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium">{alert.message}</p>
                  <p className="text-sm text-gray-600 mt-1">{alert.time}</p>
                </div>
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    alert.severity === 'critical'
                      ? 'bg-red-100 text-red-700'
                      : alert.severity === 'warning'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-blue-100 text-blue-700'
                  }`}
                >
                  {alert.severity.toUpperCase()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function SLOsTab() {
  const slos = [
    { name: 'API Availability', target: '99.9%', current: '99.95%', status: 'healthy' },
    { name: 'Response Time (p95)', target: '<200ms', current: '45ms', status: 'healthy' },
    { name: 'Error Rate', target: '<0.1%', current: '0.05%', status: 'healthy' },
    { name: 'Throughput', target: '>10k req/min', current: '12.5k', status: 'healthy' },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Service Level Objectives</h2>
        <div className="space-y-4">
          {slos.map((slo, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-medium">{slo.name}</h3>
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    slo.status === 'healthy'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {slo.status.toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Target: {slo.target}</span>
                <span className="font-medium">Current: {slo.current}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Error Budget</h2>
        <div className="p-4 bg-gray-50 rounded">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-medium">Monthly Error Budget</h3>
            <span className="text-2xl font-bold text-green-600">85.2%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div className="bg-green-500 h-4 rounded-full" style={{ width: '85.2%' }}></div>
          </div>
          <p className="text-sm text-gray-600 mt-2">14.8% error budget remaining this month</p>
        </div>
      </div>
    </div>
  );
}
