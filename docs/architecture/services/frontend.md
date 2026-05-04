# Frontend

| | |
|---|---|
| **Directory** | `/frontend` |
| **Stack** | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| **Port** | 5173 |

## Overview

The Frontend is a single-page application that provides the user-facing interface for the Nexar platform. It communicates exclusively with the API Gateway, presenting code analysis results, routing decisions, execution outputs, and hardware status in a cohesive experience. The application is built with React 18 and TypeScript, bundled with Vite, and styled using Tailwind CSS with shadcn/ui components.

## Key Capabilities

### Code Submission and Analysis

Users write or paste code into a syntax-highlighted editor and submit it for analysis. The editor supports multiple languages and quantum frameworks. Once analysis completes, the results are displayed inline, including language detection, complexity metrics, algorithm classification, and optimization suggestions.

### Decision Visualization

After the Decision Engine routes the code, the frontend renders the routing decision alongside the metrics that influenced it. Users can see whether their code was directed to a quantum device, simulator, or classical machine, along with the confidence score and the feature values that drove the decision.

### Hardware Monitoring

A dedicated view displays live device status and specifications for all quantum backends managed by the Hardware Abstraction Layer. Users can inspect qubit counts, connectivity maps, gate sets, and availability before submitting jobs to a specific device.

### Execution History

Past jobs are listed with their results and performance data, including measurement distributions, execution times, and provider details. Users can revisit previous analyses and compare outcomes across different execution targets.

### AI Code Conversion Interface

Users can invoke the AI Code Converter directly from the frontend to translate classical Python into quantum circuits. The interface displays the generated circuit alongside suitability scores and expected speedup estimates, and allows users to execute the converted circuit without leaving the page.

### AST Pattern Analyser

An interactive view allows users to explore the Abstract Syntax Tree of their submitted code and see which patterns the platform identified as quantum-amenable. This transparency helps users understand why their code was routed to a particular backend.

## UI Libraries

The frontend relies on the following libraries for its component layer and data management:

- **Radix UI** -- Accessible, unstyled primitive components used as the foundation for shadcn/ui.
- **TanStack Query** -- Server state management for data fetching, caching, and synchronisation with backend services.
- **Recharts** -- Charting library used for visualising measurement distributions, complexity metrics, and performance data.
- **Zod** -- Schema validation for form inputs and API response parsing.
- **React Router** -- Client-side routing for navigation between views.
