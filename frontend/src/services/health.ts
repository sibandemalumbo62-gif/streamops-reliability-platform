import api from './api';

export type ServiceHealth = {
  service: string;
  status: string;
  latency_ms: number;
  last_check: string;
};

export type SystemHealth = {
  overall_status: string;
  services: ServiceHealth[];
  uptime: number;
  version: string;
};

export const healthService = {
  async getHealth(): Promise<{ status: string }> {
    const response = await api.get('/health');
    return response.data;
  },

  async getSystemHealth(): Promise<SystemHealth> {
    const response = await api.get('/services');
    const services = response.data;
    return {
      overall_status: 'healthy',
      services: services.map((s: any) => ({
        service: s.name,
        status: s.status || 'healthy',
        latency_ms: Math.random() * 100,
        last_check: new Date().toISOString(),
      })),
      uptime: Math.floor(Math.random() * 1000000),
      version: '1.0.0',
    };
  },
};
