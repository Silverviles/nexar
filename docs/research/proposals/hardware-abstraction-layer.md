# Hardware Abstraction Layer — Research Proposal

**Researcher:** Siriwardhana A H L T S

## Research Objective

Create a provider-agnostic abstraction layer that enables seamless job submission and management across multiple quantum computing providers.

## Key Research Questions

- How can a unified API abstract differences between IBM, AWS, and Azure quantum backends?
- What device management features are required for production quantum workloads?
- How should job lifecycle be tracked across heterogeneous providers?

## Approach

Implement a factory-based architecture supporting IBM Qiskit, AWS Braket, and Azure Quantum SDKs. Provide device discovery, job submission, status tracking, and result retrieval through a single FastAPI interface.

