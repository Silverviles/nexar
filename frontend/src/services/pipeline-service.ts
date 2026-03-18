/**
 * Pipeline Service
 * Calls the unified pipeline orchestration endpoint.
 */

import api from "@/lib/axios";
import type { PipelineRequest, PipelineResponse } from "@/types/pipeline";

const API_BASE = "/v1/pipeline";

export const pipelineService = {
  /**
   * Run the full pipeline: analyze code → map → decide hardware.
   * Returns a unified response with analysis + decision results.
   */
  async run(request: PipelineRequest): Promise<PipelineResponse> {
    const { data } = await api.post<PipelineResponse>(`${API_BASE}/run`, request, {
      timeout: 60_000, // Pipeline chains two services, allow more time
    });
    return data;
  },

  /**
   * Check health of all pipeline services.
   */
  async healthCheck(): Promise<{
    status: string;
    services: Record<string, string>;
  }> {
    const { data } = await api.get(`${API_BASE}/health`);
    return data;
  },
};
