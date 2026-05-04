/**
 * usePipelineStatus Hook
 *
 * Polls the pipeline status endpoint until a terminal state is reached.
 * Returns progressive results as each stage completes.
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { pipelineService } from "@/services/pipeline-service";
import type { PipelineResponse, PipelineStatus } from "@/types/pipeline";

const POLL_INTERVAL_MS = 3_000;
const TERMINAL_STATUSES = new Set<PipelineStatus>(["completed", "failed"]);

interface PipelineStatusState {
  status: PipelineStatus | null;
  analysis: PipelineResponse["analysis"];
  decision: PipelineResponse["decision"];
  mappedInput: PipelineResponse["mapped_input"];
  timing: PipelineResponse["timing"] | null;
  error: string | null;
  isPolling: boolean;
  pollError: string | null;
}

interface UsePipelineStatusOptions {
  pipelineId: string;
  enabled?: boolean;
}

export function usePipelineStatus({
  pipelineId,
  enabled = true,
}: UsePipelineStatusOptions): PipelineStatusState {
  const [state, setState] = useState<PipelineStatusState>({
    status: null,
    analysis: null,
    decision: null,
    mappedInput: null,
    timing: null,
    error: null,
    isPolling: false,
    pollError: null,
  });

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setState((prev) => ({ ...prev, isPolling: false }));
  }, []);

  const poll = useCallback(async () => {
    try {
      const job = await pipelineService.getStatus(pipelineId);

      const currentStatus = job.status as PipelineStatus;

      setState((prev) => ({
        ...prev,
        status: currentStatus,
        analysis: job.analysis ?? prev.analysis,
        decision: job.decision ?? prev.decision,
        mappedInput: job.mapped_input ?? prev.mappedInput,
        timing: job.timing ?? prev.timing,
        error: job.error ?? null,
        pollError: null,
      }));

      if (TERMINAL_STATUSES.has(currentStatus)) {
        stopPolling();
      }
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        pollError: error.message || "Failed to fetch pipeline status",
      }));
    }
  }, [pipelineId, stopPolling]);

  useEffect(() => {
    if (!enabled || !pipelineId) return;

    setState({
      status: "processing",
      analysis: null,
      decision: null,
      mappedInput: null,
      timing: null,
      error: null,
      isPolling: true,
      pollError: null,
    });

    // Initial poll immediately
    poll();

    // Set up interval
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [pipelineId, enabled, poll]);

  return state;
}
