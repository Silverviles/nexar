export const STATS = [
  { value: '99.9%', label: 'Uptime' },
  { value: '10K+', label: 'Decisions Processed' },
  { value: '50ms', label: 'Average Response Time' },
  { value: '24/7', label: 'Support' },
]

export const PIPELINE_STEPS = [
  {
    step: '01',
    title: 'Analyze',
    service: 'code-analysis-engine',
    description:
      'Multi-language detection across Python, Qiskit, Cirq, Q#, and OpenQASM, with AST complexity analysis and quantum circuit metrics — qubits, depth, gate count, entanglement score.',
  },
  {
    step: '02',
    title: 'Detect & Convert',
    service: 'ai-code-converter',
    description:
      'AI detects quantum-suitable patterns in classical code and translates them into quantum circuits, scoring suitability HIGH, MEDIUM, or LOW.',
  },
  {
    step: '03',
    title: 'Decide',
    service: 'decision-engine',
    description:
      'An ML classifier recommends quantum or classical execution with a confidence score, cost estimate, and rationale.',
  },
  {
    step: '04',
    title: 'Execute',
    service: 'hardware-abstraction-layer',
    description: 'Runs on IBM Qiskit, AWS Braket, or Azure Quantum through one unified interface.',
  },
]

export const HARDWARE_PROVIDERS = [
  {
    name: 'IBM Qiskit',
    description: 'Simulators and IBM’s real quantum processors.',
  },
  {
    name: 'AWS Braket',
    description: 'Amazon’s managed quantum service across multiple hardware providers.',
  },
  {
    name: 'Azure Quantum',
    description: 'Microsoft’s quantum computing service with topological and partner hardware.',
  },
]

export const PRICING_TIERS = [
  {
    name: 'Free',
    price: '$0',
    period: '/mo',
    description: 'Get started with routing your first workloads.',
    features: [
      '50 analyses / month',
      'IBM Qiskit simulator only',
      'Basic decision rationale',
      'Community support',
    ],
    cta: 'Start free',
    href: '/signup',
    highlight: false,
  },
  {
    name: 'Pro',
    price: '$49',
    period: '/mo',
    description: 'For teams routing production workloads regularly.',
    features: [
      '2,000 analyses / month',
      'IBM Qiskit + AWS Braket + Azure Quantum',
      'Full ML confidence, rationale & cost estimates',
      'Priority email support',
    ],
    cta: 'Start free trial',
    href: '/signup',
    highlight: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For organizations with dedicated hardware and support needs.',
    features: [
      'Unlimited analyses',
      'All hardware providers + dedicated capacity',
      'Custom decision-engine tuning',
      'Dedicated support & SLA',
    ],
    cta: 'Contact sales',
    href: '/contact',
    highlight: false,
  },
]

export const FAQS = [
  {
    question: 'Do I need quantum computing expertise to use Nexar?',
    answer:
      'No. Nexar’s decision engine and hardware abstraction layer handle circuit-level and provider-level complexity for you — you submit code or problem parameters and get a routing recommendation back.',
  },
  {
    question: 'Which quantum providers are supported?',
    answer: 'IBM Qiskit, AWS Braket, and Azure Quantum today, through one unified execution interface.',
  },
  {
    question: 'How does Nexar decide between quantum and classical execution?',
    answer:
      'An ML classifier scores problem type, qubit count, circuit depth, gate count, and entanglement/superposition metrics, then returns a recommendation with a confidence score and rationale.',
  },
  {
    question: 'What algorithms can Nexar detect and convert automatically?',
    answer:
      'Patterns like linear search, optimization, majority voting, factorization, and database search map to Grover’s, QAOA, Deutsch-Jozsa, Shor’s, and amplitude amplification respectively.',
  },
  {
    question: 'What happens if a job fails on real quantum hardware?',
    answer:
      'Jobs are tracked through to completion or failure via status polling, so you can inspect the outcome and result of every job you submit.',
  },
  {
    question: 'Is my code and data secure?',
    answer:
      'All API access is authenticated with bearer tokens, and your analysis and decision history is scoped to your account.',
  },
]

export const USE_CASES = [
  {
    pattern: 'Linear Search',
    algorithm: "Grover's Algorithm",
    speedup: '2x speedup',
    why: 'An unstructured scan over N items collapses to roughly √N queries under amplitude amplification.',
  },
  {
    pattern: 'Optimization Problems',
    algorithm: 'QAOA',
    speedup: '1.5x speedup',
    why: 'Combinatorial cost functions are encoded as a Hamiltonian and explored via parameterized quantum circuits.',
  },
  {
    pattern: 'Majority Voting',
    algorithm: 'Deutsch-Jozsa',
    speedup: '2x speedup',
    why: 'Determining constant-vs-balanced behavior across inputs is resolved in a single query instead of N/2+1.',
  },
  {
    pattern: 'Factorization',
    algorithm: "Shor's Algorithm",
    speedup: 'Exponential speedup',
    why: 'Period-finding via the quantum Fourier transform breaks factorization out of classical sub-exponential time.',
  },
  {
    pattern: 'Database Search',
    algorithm: 'Amplitude Amplification',
    speedup: 'Faster unstructured search',
    why: 'Iteratively boosts the probability of measuring the correct record without needing an index or sort order.',
  },
]

export const PROBLEM_TYPES = [
  'Search',
  'Optimization',
  'Simulation',
  'Machine Learning',
  'Factorization',
  'Cryptography',
  'Sampling',
  'Classical',
]
