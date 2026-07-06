import { useEffect, useState } from 'react'
import { Sparkles } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { FadeIn } from '@/components/ui/FadeIn'
import { CodeBlock } from '@/components/ui/CodeBlock'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table'
import { MarketingLayout } from '@/components/layout/MarketingLayout'
import { cn } from '@/lib/utils'

type Method = 'GET' | 'POST' | 'DELETE'

const METHOD_BADGE_VARIANT: Record<Method, 'default' | 'success' | 'destructive'> = {
  GET: 'default',
  POST: 'success',
  DELETE: 'destructive',
}

interface Endpoint {
  method: Method
  path: string
  description: string
}

interface Domain {
  id: string
  label: string
  base: string
  intro: string
  endpoints: Endpoint[]
  example?: { method: Method; path: string; request?: string; response: string }
}

const DOMAINS: Domain[] = [
  {
    id: 'auth',
    label: 'Auth',
    base: '/v1/auth',
    intro: 'Account creation and session tokens. These are the only endpoints that don’t require a bearer token.',
    endpoints: [
      { method: 'POST', path: '/register', description: 'Create an account with email, password, and name.' },
      { method: 'POST', path: '/login', description: 'Authenticate and receive a bearer token.' },
      { method: 'POST', path: '/google', description: 'Exchange a Google OAuth code for a session.' },
      { method: 'POST', path: '/resend-verification', description: 'Resend the email verification link.' },
      { method: 'GET', path: '/me', description: 'Get the current authenticated user profile.' },
    ],
    example: {
      method: 'POST',
      path: '/v1/auth/login',
      request: `{
  "email": "you@example.com",
  "password": "••••••••"
}`,
      response: `{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": { "id": "usr_1a2b3c", "name": "Ada Lovelace", "email": "you@example.com" }
}`,
    },
  },
  {
    id: 'decision-engine',
    label: 'Decision Engine',
    base: '/v1/decision-engine',
    intro: 'The core routing service — scores a workload and recommends quantum or classical execution.',
    endpoints: [
      { method: 'GET', path: '/health', description: 'Service health check.' },
      { method: 'POST', path: '/predict', description: 'Get a quantum-vs-classical routing recommendation.' },
      { method: 'GET', path: '/model-info', description: 'Metadata about the active ML model.' },
      { method: 'GET', path: '/history', description: 'Paginated decision history (filter by hardware, status).' },
      { method: 'GET', path: '/history/:id', description: 'Retrieve a single decision record.' },
      { method: 'POST', path: '/feedback/:decisionId', description: 'Submit the real execution outcome for a prior prediction.' },
      { method: 'GET', path: '/accuracy', description: 'Prediction accuracy statistics.' },
      { method: 'GET', path: '/dashboard', description: 'Aggregated dashboard statistics.' },
    ],
    example: {
      method: 'POST',
      path: '/v1/decision-engine/predict',
      request: `{
  "problemType": "optimization",
  "qubits": 12,
  "circuitDepth": 48,
  "gateCount": 210,
  "entanglementScore": 0.62,
  "superpositionScore": 0.71,
  "timeComplexity": "exponential",
  "memoryRequirementMb": 512
}`,
      response: `{
  "recommendedHardware": "quantum",
  "confidence": 0.87,
  "quantumProbability": 0.87,
  "classicalProbability": 0.13,
  "rationale": "High entanglement and superposition scores favor a quantum backend for this problem type.",
  "estimatedExecutionTimeMs": 4200,
  "estimatedCostUsd": 0.42
}`,
    },
  },
  {
    id: 'code-analysis',
    label: 'Code Analysis',
    base: '/v1/code-analysis-engine',
    intro: 'Detects language, complexity, and circuit metrics from a raw code submission.',
    endpoints: [
      { method: 'GET', path: '/supported-languages', description: 'List supported source languages.' },
      { method: 'POST', path: '/analyze', description: 'Run full static/ML analysis on a code submission.' },
      { method: 'POST', path: '/detect-language', description: 'Detect the language of a code snippet.' },
      { method: 'GET', path: '/health', description: 'Service health check.' },
    ],
    example: {
      method: 'POST',
      path: '/v1/code-analysis-engine/analyze',
      request: `{
  "code": "def linear_search(arr, target): ...",
  "language": "python"
}`,
      response: `{
  "language": "python",
  "problemType": "search",
  "qubitsEstimate": 8,
  "circuitDepthEstimate": 32,
  "algorithmDetected": "grover",
  "suitabilityScore": "HIGH"
}`,
    },
  },
  {
    id: 'ai-converter',
    label: 'AI Converter',
    base: '/v1/ai-code-converter',
    intro: 'Detects quantum-suitable patterns in classical code and translates them into runnable quantum circuits.',
    endpoints: [
      { method: 'POST', path: '/quantum/analyze', description: 'Analyze code for quantum-suitable patterns.' },
      { method: 'POST', path: '/translate', description: 'Translate classical Python to quantum (Qiskit) code.' },
      { method: 'POST', path: '/execute', description: 'Execute translated quantum code and return results.' },
    ],
    example: {
      method: 'POST',
      path: '/v1/ai-code-converter/translate',
      request: `{
  "code": "def linear_search(arr, target): ...",
  "targetFramework": "qiskit"
}`,
      response: `{
  "quantumCode": "from qiskit import QuantumCircuit\\n...",
  "algorithm": "Grover's Algorithm",
  "estimatedSpeedup": "2x"
}`,
    },
  },
  {
    id: 'hardware',
    label: 'Hardware',
    base: '/v1/hardware',
    intro: 'One interface across IBM Qiskit, AWS Braket, and Azure Quantum — device listing, execution, and job monitoring.',
    endpoints: [
      { method: 'GET', path: '/status', description: 'Overall hardware layer status.' },
      { method: 'GET', path: '/devices', description: 'List all devices across all providers.' },
      { method: 'GET', path: '/providers', description: 'List registered provider names.' },
      { method: 'GET', path: '/quantum/:provider/devices', description: 'List devices for one provider.' },
      { method: 'POST', path: '/quantum/:provider/execute', description: 'Submit a QASM circuit for execution.' },
      { method: 'POST', path: '/quantum/execute-python', description: 'Submit raw Python defining a circuit, run on IBM Quantum.' },
      { method: 'POST', path: '/classical/:provider/execute', description: 'Submit a classical compute task.' },
      { method: 'POST', path: '/quantum/schedule', description: 'Schedule a future quantum job.' },
      { method: 'GET', path: '/quantum/scheduled-jobs', description: 'List scheduled jobs.' },
      { method: 'DELETE', path: '/quantum/scheduled-jobs/:jobId', description: 'Cancel a scheduled job.' },
      { method: 'GET', path: '/quantum/devices/:device/availability', description: 'Check device availability.' },
      { method: 'GET', path: '/jobs/:provider/:jobId', description: 'Get job status.' },
      { method: 'GET', path: '/jobs/:provider/:jobId/result', description: 'Get job result.' },
    ],
    example: {
      method: 'POST',
      path: '/v1/hardware/quantum/ibm/execute?device_name=ibmq_qasm_simulator&shots=1024',
      request: `{
  "qasm": "OPENQASM 2.0; include \\"qelib1.inc\\"; qreg q[2]; ..."
}`,
      response: `{
  "jobId": "job_8f2a91",
  "provider": "ibm",
  "status": "queued"
}`,
    },
  },
  {
    id: 'pipeline',
    label: 'Pipeline',
    base: '/v1/pipeline',
    intro: 'Orchestrates the full flow — analyze, decide, and execute — behind a single call.',
    endpoints: [
      { method: 'POST', path: '/run', description: 'Kick off an async end-to-end pipeline run (analyze → decide → execute).' },
      { method: 'GET', path: '/status/:pipelineId', description: 'Poll for pipeline run status/result.' },
      { method: 'GET', path: '/health', description: 'Health of all constituent pipeline services.' },
    ],
    example: {
      method: 'POST',
      path: '/v1/pipeline/run',
      request: `{
  "code": "def linear_search(arr, target): ...",
  "language": "python"
}`,
      response: `{
  "pipeline_id": "b7e1e9b0-3c2a-4f1e-9c1a-2d4e5f6a7b8c",
  "status": "processing"
}`,
    },
  },
]

const PREDICT_RESPONSE_FIELDS = [
  { field: 'recommendedHardware', type: 'string', description: '"quantum" or "classical".' },
  { field: 'confidence', type: 'number', description: 'Model confidence, 0–1.' },
  { field: 'quantumProbability', type: 'number', description: 'Probability quantum execution is optimal.' },
  { field: 'classicalProbability', type: 'number', description: 'Probability classical execution is optimal.' },
  { field: 'rationale', type: 'string', description: 'Human-readable explanation for the recommendation.' },
  { field: 'estimatedExecutionTimeMs', type: 'number', description: 'Estimated execution time in milliseconds.' },
  { field: 'estimatedCostUsd', type: 'number', description: 'Estimated cost in USD.' },
]

const NAV_SECTIONS = [
  { id: 'quickstart', label: 'Quickstart' },
  { id: 'authentication', label: 'Authentication' },
  ...DOMAINS.map((d) => ({ id: d.id, label: d.label })),
]
const NAV_SECTION_IDS = NAV_SECTIONS.map((s) => s.id)

function useActiveSection(ids: string[]) {
  const [activeId, setActiveId] = useState(ids[0])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((entry) => entry.isIntersecting)
        if (visible.length > 0) {
          setActiveId(visible[0].target.id)
        }
      },
      { rootMargin: '-100px 0px -66% 0px' }
    )

    ids.forEach((id) => {
      const el = document.getElementById(id)
      if (el) observer.observe(el)
    })

    return () => observer.disconnect()
  }, [ids])

  return activeId
}

function scrollToSection(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function EndpointList({ domain }: { domain: Domain }) {
  return (
    <div className="border border-hairline bg-canvas">
      {domain.endpoints.map((endpoint) => (
        <div
          key={endpoint.method + endpoint.path}
          className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 border-b border-hairline p-4 last:border-b-0"
        >
          <div className="flex items-center gap-3 sm:w-80 shrink-0">
            <Badge variant={METHOD_BADGE_VARIANT[endpoint.method]}>{endpoint.method}</Badge>
            <code className="font-mono text-sm text-ink">
              {domain.base}
              {endpoint.path}
            </code>
          </div>
          <p className="text-sm text-ink-muted">{endpoint.description}</p>
        </div>
      ))}
    </div>
  )
}

function ApiDocs() {
  const activeId = useActiveSection(NAV_SECTION_IDS)

  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="container mx-auto px-6 py-24 md:py-32 text-center">
        <FadeIn>
          <div className="inline-flex items-center gap-2 border border-primary/30 bg-surface-1 px-4 py-2 text-sm font-medium text-primary mb-8">
            <Sparkles className="h-4 w-4" />
            API Documentation
          </div>
          <h1 className="text-5xl md:text-[76px] font-light leading-[1.17] tracking-[-0.5px] text-ink mb-6 max-w-4xl mx-auto">
            Build on the Nexar API
          </h1>
          <p className="text-lg text-ink-muted mb-10 max-w-2xl mx-auto leading-relaxed">
            One gateway in front of four independent services: code analysis, AI conversion, decision-making, and
            hardware execution.
          </p>
        </FadeIn>
      </section>

      <div className="container mx-auto px-6 pb-24">
        <div className="lg:grid lg:grid-cols-[220px_1fr] lg:gap-16">
          {/* Sidebar */}
          <aside className="hidden lg:block">
            <nav className="sticky top-24 flex flex-col gap-0.5">
              {NAV_SECTIONS.map((section) => (
                <button
                  key={section.id}
                  type="button"
                  onClick={() => scrollToSection(section.id)}
                  className={cn(
                    'border-l-2 px-4 py-1.5 text-left text-sm transition-colors',
                    activeId === section.id
                      ? 'border-primary text-ink font-medium'
                      : 'border-transparent text-ink-muted hover:text-ink'
                  )}
                >
                  {section.label}
                </button>
              ))}
            </nav>
          </aside>

          {/* Content */}
          <div className="min-w-0 space-y-20">
            {/* Quickstart */}
            <section id="quickstart" className="scroll-mt-24">
              <h2 className="text-2xl font-normal text-ink mb-2">Quickstart</h2>
              <p className="text-ink-muted mb-8 max-w-2xl">
                Three calls take you from an account to a routing recommendation.
              </p>

              <div className="space-y-8">
                <div>
                  <p className="text-sm text-ink-subtle mb-3">1. Log in and get a token</p>
                  <CodeBlock method="POST" path="/v1/auth/login" code={'{\n  "email": "you@example.com",\n  "password": "••••••••"\n}'} />
                </div>
                <div>
                  <p className="text-sm text-ink-subtle mb-3">2. Call an endpoint with the token</p>
                  <CodeBlock
                    code={'Authorization: Bearer <token>\nContent-Type: application/json'}
                  />
                </div>
                <div>
                  <p className="text-sm text-ink-subtle mb-3">3. Request a routing recommendation</p>
                  <CodeBlock method="POST" path="/v1/decision-engine/predict" code={DOMAINS[1].example!.request!} className="mb-4" />
                  <CodeBlock code={DOMAINS[1].example!.response} />
                </div>
              </div>

              <div className="mt-10 border border-hairline">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Response field</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Description</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {PREDICT_RESPONSE_FIELDS.map((row) => (
                      <TableRow key={row.field}>
                        <TableCell className="font-mono text-sm">{row.field}</TableCell>
                        <TableCell className="text-ink-muted">{row.type}</TableCell>
                        <TableCell className="text-ink-muted">{row.description}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </section>

            {/* Authentication */}
            <section id="authentication" className="scroll-mt-24">
              <h2 className="text-2xl font-normal text-ink mb-4">Authentication</h2>
              <p className="text-ink-muted mb-4 max-w-2xl">
                Every endpoint except <code className="font-mono text-sm text-ink">/v1/auth/*</code> requires a
                bearer token returned from <code className="font-mono text-sm text-ink">POST /v1/auth/login</code>.
              </p>
              <p className="text-ink-muted mb-4 max-w-2xl">Base URL pattern:</p>
              <CodeBlock code="{VITE_API_BASE_URL}/v1/<domain>/<resource>" className="mb-4" />
              <CodeBlock code="Authorization: Bearer <token>" />
            </section>

            {/* Domains */}
            {DOMAINS.map((domain) => (
              <section key={domain.id} id={domain.id} className="scroll-mt-24">
                <h2 className="text-2xl font-normal text-ink mb-2">{domain.label}</h2>
                <p className="text-ink-muted mb-6 max-w-2xl">{domain.intro}</p>

                <EndpointList domain={domain} />

                {domain.example && (
                  <div className="mt-8">
                    <p className="text-sm text-ink-subtle mb-3">Example request</p>
                    <CodeBlock
                      method={domain.example.method}
                      path={domain.example.path}
                      code={domain.example.request ?? domain.example.response}
                      className="mb-4"
                    />
                    {domain.example.request && (
                      <>
                        <p className="text-sm text-ink-subtle mb-3">Example response</p>
                        <CodeBlock code={domain.example.response} />
                      </>
                    )}
                  </div>
                )}
              </section>
            ))}

            <p className="text-sm text-ink-muted max-w-2xl">
              This page is a curated overview. Full interactive Swagger/OpenAPI documentation is available at each
              microservice's own <code className="font-mono text-ink">/docs</code> endpoint (code-analysis-engine,
              ai-code-converter, decision-engine, hardware-abstraction-layer). Request/response field names above
              reflect the documented shape and are illustrative rather than pulled from a published schema.
            </p>
          </div>
        </div>
      </div>
    </MarketingLayout>
  )
}

export default ApiDocs
