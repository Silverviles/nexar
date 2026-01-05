
import api from '@/lib/axios';
import type { HardwareDevicesResponse, HardwareStatusResponse } from '@/types/hardware';

const API_BASE = '/v1/hardware';

export const hardwareService = {
  /**
   * Get overall hardware layer status
   */
  async getStatus(): Promise<HardwareStatusResponse> {
    const { data } = await api.get<HardwareStatusResponse>(`${API_BASE}/status`);
    return data;
  },

  /**
   * List all available hardware devices from all providers
   */
  async getDevices(): Promise<HardwareDevicesResponse> {
    const { data } = await api.get<HardwareDevicesResponse>(`${API_BASE}/devices`);
    return data;
  }
};
