# Hardware Abstraction Layer

| | |
|---|---|
| **Directory** | `/hardware-abstraction-layer` |
| **Stack** | FastAPI, Python, Qiskit, Amazon Braket SDK, Azure Quantum SDK |
| **Port** | 8004 |

## Overview

The Hardware Abstraction Layer (HAL) provides a provider-agnostic interface to quantum backends. It decouples the rest of the Nexar platform from the specifics of any single quantum cloud provider, allowing circuits to be submitted, monitored, and retrieved through a unified API regardless of whether the underlying hardware is IBM, AWS, or Azure.

## Supported Providers

The HAL integrates with three major quantum cloud providers:

- **IBM Qiskit** -- Access to IBM Quantum real devices and simulators. Circuits are transpiled using the Qiskit transpiler to match the target device's gate set and connectivity.
- **AWS Braket** -- Access to Amazon Braket managed quantum devices and on-demand simulators. The HAL uses the Amazon Braket SDK to submit tasks and retrieve results.
- **Azure Quantum** -- Access to Microsoft Azure Quantum backends. The HAL uses the Azure Quantum SDK to interact with available quantum hardware and simulators.

## Device Management

The HAL maintains an up-to-date view of available quantum devices across all providers. For each device, it exposes:

- **Qubit count** -- The number of qubits available on the device.
- **Status** -- Whether the device is online, offline, or undergoing maintenance.
- **Connectivity** -- The qubit coupling map, describing which qubits can interact directly.
- **Gate set** -- The native gate set supported by the device.

This information allows the Decision Engine and other services to make informed choices about which device to target for a given circuit.

## Job Execution

The HAL accepts quantum circuits or classical code and submits them to the selected provider. Key execution parameters include:

- **Target device or simulator** -- Specified by provider and device identifier.
- **Shot count** -- The number of times the circuit is executed, configurable per job.
- **Transpilation options** -- Optimisation level and layout method can be specified for providers that support transpilation.

The HAL translates the submission into the provider's native format, handles authentication with the provider's API, and returns a job identifier for tracking.

## Job Lifecycle

Each submitted job follows a managed lifecycle:

- **Submission** -- The job is dispatched to the provider and a unique job ID is returned.
- **Status Tracking** -- The HAL polls the provider for job status updates (queued, running, completed, failed) and exposes this through its API.
- **Result Retrieval** -- Once a job completes, the HAL fetches the measurement results and normalises them into a standard format.
- **Performance Monitoring** -- Execution metadata (queue time, execution time, shot count, provider-reported fidelity) is recorded for each job.

## Project Structure

The service is organised under the `/app` directory with the following layout:

- **api/routes/** -- FastAPI route definitions for device listing, job submission, status checks, and result retrieval.
- **providers/** -- Provider-specific adapters for IBM Qiskit, AWS Braket, and Azure Quantum, each implementing a common interface.
- **services/factory** -- Factory pattern for instantiating the correct provider adapter based on the requested backend.
- **models/** -- Pydantic models for request/response schemas, device specifications, and job metadata.
- **messaging/** -- Internal messaging utilities for asynchronous job notifications.
- **core/** -- Shared configuration, constants, and utility functions.
