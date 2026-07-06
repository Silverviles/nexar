/**
 * Polls the hardware service for job status until a terminal state is reached.
 * Terminal states: COMPLETED, FAILED, CANCELLED
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { hardwareService } from '@/services/hardware-service'

const POLL_INTERVAL_MS = 5_000
const TERMINAL_STATUSES = new Set(['COMPLETED', 'FAILED', 'CANCELLED', 'completed', 'failed', 'cancelled'])

interface JobStatusState {
  status: string | null
  result: Record<string, unknown> | null
  isPolling: boolean
  error: string | null
}

interface UseJobStatusOptions {
  provider: string
  jobId: string
  enabled?: boolean
}

export function useJobStatus({ provider, jobId, enabled = true }: UseJobStatusOptions): JobStatusState {
  const [state, setState] = useState<JobStatusState>({
    status: null,
    result: null,
    isPolling: false,
    error: null,
  })

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    setState((prev) => ({ ...prev, isPolling: false }))
  }, [])

  const poll = useCallback(async () => {
    try {
      const statusResponse = await hardwareService.getJobStatus(provider, jobId)
      const currentStatus = statusResponse.status ?? statusResponse.state ?? 'UNKNOWN'

      if (TERMINAL_STATUSES.has(currentStatus)) {
        let result: Record<string, unknown> | null = null
        if (currentStatus === 'COMPLETED' || currentStatus === 'completed') {
          try {
            const jobResult = await hardwareService.getJobResult(provider, jobId)
            result = jobResult as unknown as Record<string, unknown>
          } catch {
            // Result may not be available yet
          }
        }

        setState({ status: currentStatus, result, isPolling: false, error: null })
        stopPolling()
      } else {
        setState((prev) => ({ ...prev, status: currentStatus, error: null }))
      }
    } catch (error) {
      setState((prev) => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to check job status',
      }))
    }
  }, [provider, jobId, stopPolling])

  useEffect(() => {
    if (!enabled || !provider || !jobId) return

    setState({ status: null, result: null, isPolling: true, error: null })

    poll()
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [provider, jobId, enabled, poll])

  return state
}
