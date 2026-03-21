/**
 * Pipeline Service
 * Calls the async pipeline orchestration endpoint.
 */

import api from "@/lib/axios";
import type { PipelineRequest, PipelineResponse } from "@/types/pipeline";

const API_BASE = "/v1/pipeline";

export const pipelineService = {
  /**
   * Start an async pipeline run.
   * Returns immediately with { pipeline_id, status: "processing" }.
   * Use getStatus() to poll for results.
   */
  async run(request: PipelineRequest): Promise<{ pipeline_id: string; status: string }> {
    const { data } = await api.post(`${API_BASE}/run`, request);
    return data;
  },

  /**
   * Poll for pipeline job status and results.
   */
  async getStatus(pipelineId: string): Promise<PipelineResponse> {
    const { data } = await api.get<PipelineResponse>(`${API_BASE}/status/${pipelineId}`);
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
