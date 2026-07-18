/**
 * Pipeline Execution
 * Execution step with live job status polling.
 * Routes to IBM Quantum or Local Classical based on the decision engine recommendation.
 */

import { useState, useEffect } from 'react'
import { Play, Loader2, CheckCircle, XCircle, Clock, Cpu, Atom } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FadeIn } from '@/components/ui/FadeIn'
import { useJobStatus } from '@/hooks/useJobStatus'
import { hardwareService } from '@/services/hardware-service'
import { HardwareType } from '@/types/decision-engine.tp'
import type { HardwareDevice } from '@/types/hardware'

interface PipelineExecutionProps {
  recommendedHardware: string
  code: string
}

type GenericRecord = Record<string, unknown>

function isNumericRecord(value: unknown): value is Record<string, number> {
  if (!value || typeof value !== 'object') return false
  const entries = Object.entries(value as GenericRecord)
  if (entries.length === 0) return false
  return entries.every(([, v]) => typeof v === 'number' && Number.isFinite(v))
}

/** Detects raw OpenQASM source (vs. Python) by its first non-comment line. */
function isQasmCode(code: string): boolean {
  const firstMeaningfulLine = code
    .split('\n')
    .map((line) => line.trim())
    .find((line) => line.length > 0 && !line.startsWith('//'))
  return !!firstMeaningfulLine && /^OPENQASM\b/i.test(firstMeaningfulLine)
}

export function PipelineExecution({ recommendedHardware, code }: PipelineExecutionProps) {
  const [jobId, setJobId] = useState<string | null>(null)
  const [provider, setProvider] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const isQuantum = recommendedHardware === HardwareType.QUANTUM

  const [deviceName, setDeviceName] = useState('')
  const [shots, setShots] = useState(1024)
  const [devices, setDevices] = useState<HardwareDevice[]>([])
  const [devicesLoading, setDevicesLoading] = useState(false)

  useEffect(() => {
    if (!isQuantum) return
    setDevicesLoading(true)
    hardwareService
      .getDevices()
      .then((res) => {
        setDevices(res.devices)
        if (res.devices.length > 0 && !deviceName) {
          setDeviceName(res.devices[0].name)
        }
      })
      .catch(() => setDevices([]))
      .finally(() => setDevicesLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isQuantum])

  const jobStatus = useJobStatus({
    provider: provider ?? '',
    jobId: jobId ?? '',
    enabled: !!provider && !!jobId,
  })

  const handleExecute = async () => {
    setIsSubmitting(true)
    setSubmitError(null)

    try {
      if (isQuantum) {
        if (isQasmCode(code)) {
          // Raw OpenQASM source - submit directly as a circuit
          const result = await hardwareService.submitQuantumCircuit('ibm-quantum', {
            qasm: code,
            device_name: deviceName,
            shots,
          })
          setProvider(result.provider ?? 'ibm-quantum')
          setJobId(result.job_id)
        } else {
          // Python code via execute-python endpoint (must define a `circuit` variable)
          const result = await hardwareService.submitPythonCode({ code, device_name: deviceName, shots })
          setProvider(result.provider ?? 'ibm-quantum')
          setJobId(result.job_id)
        }
      } else {
        const result = await hardwareService.submitClassicalTask('local', { code, language: 'python' })
        setProvider(result.provider ?? 'local')
        setJobId(result.job_id)
      }
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to submit job')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!jobId) {
    return (
      <FadeIn>
        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {isQuantum ? <Atom className="h-5 w-5 text-quantum" /> : <Cpu className="h-5 w-5 text-primary" />}
              Execute on {isQuantum ? 'IBM Quantum' : 'Local Classical'} Backend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {isQuantum ? (
                <>
                  <div className="text-sm text-ink-muted">
                    Your code will be submitted to <Badge variant="quantum">IBM Quantum</Badge> via the Qiskit Runtime. Raw OpenQASM
                    source is submitted directly; Python code must define a{' '}
                    <code className="bg-surface-1 px-1.5 py-0.5 font-mono text-xs">circuit</code> variable (QuantumCircuit).
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label className="text-xs text-ink-muted">Device</Label>
                      <select
                        value={deviceName}
                        onChange={(e) => setDeviceName(e.target.value)}
                        disabled={devicesLoading}
                        className="mt-1 w-full border border-hairline bg-surface-1 px-3 py-2 text-sm font-mono text-ink"
                      >
                        {devicesLoading ? (
                          <option>Loading devices...</option>
                        ) : devices.length === 0 ? (
                          <option>No devices available</option>
                        ) : (
                          <>
                            {devices.filter((d) => !d.is_simulator).length > 0 && (
                              <optgroup label="Real Quantum Hardware">
                                {devices
                                  .filter((d) => !d.is_simulator)
                                  .map((d) => (
                                    <option key={d.name} value={d.name}>
                                      {d.name}
                                      {d.num_qubits ? ` (${d.num_qubits} qubits)` : ''}
                                    </option>
                                  ))}
                              </optgroup>
                            )}
                            {devices.filter((d) => d.is_simulator).length > 0 && (
                              <optgroup label="Simulators">
                                {devices
                                  .filter((d) => d.is_simulator)
                                  .map((d) => (
                                    <option key={d.name} value={d.name}>
                                      {d.name}
                                    </option>
                                  ))}
                              </optgroup>
                            )}
                          </>
                        )}
                      </select>
                    </div>
                    <div>
                      <Label className="text-xs text-ink-muted">Shots</Label>
                      <Input
                        type="number"
                        value={shots}
                        onChange={(e) => setShots(Math.max(1, parseInt(e.target.value) || 1024))}
                        min={1}
                        max={100000}
                        className="mt-1 bg-surface-1 font-mono"
                      />
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-sm text-ink-muted">
                  Your code will be executed on the <Badge variant="classical">Local Classical</Badge> Python runtime. All standard
                  Python libraries and installed packages are available.
                </div>
              )}

              {submitError && (
                <div className="border border-error/40 bg-error/10 p-3">
                  <p className="text-sm text-error">{submitError}</p>
                </div>
              )}

              <Button variant="quantum" onClick={handleExecute} disabled={isSubmitting} className="gap-2">
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Submitting to {isQuantum ? 'IBM Quantum' : 'Local'}...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Execute on {isQuantum ? 'IBM Quantum' : 'Local Python'}
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </FadeIn>
    )
  }

  const statusIcon = () => {
    if (jobStatus.status === 'COMPLETED' || jobStatus.status === 'completed') {
      return <CheckCircle className="h-5 w-5 text-success" />
    }
    if (jobStatus.status === 'FAILED' || jobStatus.status === 'failed') {
      return <XCircle className="h-5 w-5 text-error" />
    }
    return <Loader2 className="h-5 w-5 animate-spin text-primary" />
  }

  const resultEnvelope = (jobStatus.result ?? null) as GenericRecord | null
  const executionResult =
    resultEnvelope && typeof resultEnvelope.result === 'object' ? (resultEnvelope.result as GenericRecord) : null

  const quantumCounts = isNumericRecord(executionResult) ? executionResult : null
  const totalShots = quantumCounts ? Object.values(quantumCounts).reduce((sum, count) => sum + count, 0) : null
  const topOutcomes = quantumCounts
    ? Object.entries(quantumCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
    : []

  const classicalStdout = executionResult && typeof executionResult.stdout === 'string' ? executionResult.stdout : null
  const classicalStderr = executionResult && typeof executionResult.stderr === 'string' ? executionResult.stderr : null
  const classicalVariables =
    executionResult && typeof executionResult.variables === 'object' && executionResult.variables !== null
      ? (executionResult.variables as GenericRecord)
      : null

  return (
    <FadeIn>
      <Card variant="glass">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              {statusIcon()}
              Job Status
            </CardTitle>
            <Badge variant="outline" className="font-mono text-xs">
              {jobId}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between border border-hairline bg-surface-1 p-3">
              <span className="text-sm text-ink-muted">Provider</span>
              <Badge variant={isQuantum ? 'quantum' : 'classical'}>{provider === 'ibm-quantum' ? 'IBM Quantum' : 'Local Classical'}</Badge>
            </div>

            {isQuantum && (
              <div className="flex items-center justify-between border border-hairline bg-surface-1 p-3">
                <span className="text-sm text-ink-muted">Device</span>
                <span className="font-mono text-sm text-ink">{deviceName}</span>
              </div>
            )}

            <div className="flex items-center justify-between border border-hairline bg-surface-1 p-3">
              <span className="text-sm text-ink-muted">Status</span>
              <Badge
                variant={
                  jobStatus.status === 'COMPLETED' || jobStatus.status === 'completed'
                    ? 'quantum'
                    : jobStatus.status === 'FAILED' || jobStatus.status === 'failed'
                      ? 'destructive'
                      : 'outline'
                }
              >
                {jobStatus.status || 'SUBMITTING'}
              </Badge>
            </div>

            {jobStatus.isPolling && (
              <div className="flex items-center gap-2 text-xs text-ink-muted">
                <Clock className="h-3.5 w-3.5 animate-pulse" />
                {isQuantum ? 'Waiting for IBM Quantum (may take minutes in queue)...' : 'Polling every 5 seconds...'}
              </div>
            )}

            {jobStatus.error && (
              <div className="border border-error/40 bg-error/10 p-3">
                <p className="text-sm text-error">{jobStatus.error}</p>
              </div>
            )}

            {jobStatus.result && (
              <div className="border border-primary/30 bg-surface-1 p-3">
                <p className="mb-2 text-sm font-medium text-ink">Execution Results</p>

                {isQuantum && quantumCounts && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between border border-hairline bg-canvas p-3">
                      <span className="text-sm text-ink-muted">Total shots</span>
                      <span className="font-mono text-sm text-ink">{totalShots}</span>
                    </div>
                    <div className="border border-hairline bg-canvas p-3">
                      <p className="mb-2 text-xs font-medium text-ink-muted">Most likely outcomes</p>
                      <div className="space-y-2">
                        {topOutcomes.map(([bitstring, count]) => {
                          const percentage = totalShots && totalShots > 0 ? ((count / totalShots) * 100).toFixed(2) : '0.00'
                          return (
                            <div key={bitstring} className="flex items-center justify-between text-sm">
                              <span className="font-mono text-ink">{bitstring}</span>
                              <span className="font-mono text-ink-muted">
                                {count} ({percentage}%)
                              </span>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  </div>
                )}

                {!isQuantum && executionResult && (
                  <div className="space-y-3">
                    <div className="border border-hairline bg-canvas p-3">
                      <p className="mb-1 text-xs font-medium text-ink-muted">Standard output</p>
                      <pre className="max-h-56 overflow-auto text-xs font-mono whitespace-pre-wrap text-ink">
                        {classicalStdout?.trim() || 'No stdout output'}
                      </pre>
                    </div>
                    {classicalStderr?.trim() && (
                      <div className="border border-error/40 bg-error/10 p-3">
                        <p className="mb-1 text-xs font-medium text-error">Standard error</p>
                        <pre className="max-h-40 overflow-auto text-xs font-mono whitespace-pre-wrap text-error">{classicalStderr}</pre>
                      </div>
                    )}
                    {classicalVariables && Object.keys(classicalVariables).length > 0 && (
                      <div className="border border-hairline bg-canvas p-3">
                        <p className="mb-2 text-xs font-medium text-ink-muted">Variables</p>
                        <div className="space-y-1">
                          {Object.entries(classicalVariables)
                            .slice(0, 10)
                            .map(([k, v]) => (
                              <div key={k} className="flex items-start justify-between gap-3 text-xs">
                                <span className="font-mono text-ink-muted">{k}</span>
                                <span className="max-w-[70%] break-all font-mono text-ink">
                                  {typeof v === 'string' ? v : JSON.stringify(v)}
                                </span>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <details className="mt-3">
                  <summary className="cursor-pointer text-xs text-ink-muted">View raw JSON</summary>
                  <pre className="mt-2 max-h-64 overflow-auto border border-hairline bg-canvas p-2 text-xs font-mono text-ink">
                    {JSON.stringify(jobStatus.result, null, 2)}
                  </pre>
                </details>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </FadeIn>
  )
}
