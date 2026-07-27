import api from "./api";


export interface ServiceHealth {

  service: string;

  status: string;

  latency_ms: number;

  last_check: string;

}


export interface SystemHealth {

  overall_status: string;

  services: ServiceHealth[];

  uptime: number;

  version: string;

}



export const healthService = {


  async getSystemHealth()
  : Promise<SystemHealth> {


    const response =
      await api.get(
        "/health"
      );


    return response.data;

  }


};