const INFEASIBLE_MS_THRESHOLD = 1e12

function toFiniteNumber(value: unknown): number | null {
  if (value === null || value === undefined) return null
  const num = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(num)) return null
  return num
}

export function formatDurationMs(value: unknown): string {
  const ms = toFiniteNumber(value)
  if (ms === null || ms < 0) return 'N/A'
  if (ms > INFEASIBLE_MS_THRESHOLD) return 'Infeasible'

  const seconds = ms / 1000
  if (seconds < 1) return `${Math.round(ms)}ms`
  if (seconds < 60) return `${seconds.toFixed(2)}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`
  const days = seconds / 86400
  if (days < 365) return `${days.toFixed(1)} days`
  return `${(days / 365).toFixed(1)} years`
}

export function formatMilliseconds(value: unknown): string {
  const ms = toFiniteNumber(value)
  if (ms === null || ms < 0 || ms > INFEASIBLE_MS_THRESHOLD) return 'N/A'
  return `${Math.round(ms)}ms`
}

export function formatSignedMilliseconds(value: unknown): string {
  const ms = toFiniteNumber(value)
  if (ms === null || ms === 0 || Math.abs(ms) > INFEASIBLE_MS_THRESHOLD) return 'N/A'
  const rounded = Math.round(ms)
  return `${rounded > 0 ? '+' : ''}${rounded}ms`
}
