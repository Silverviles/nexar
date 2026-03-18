# Deployment Report

## Overview

Nexar is deployed on Google Cloud Platform using a fully automated infrastructure-as-code approach. All services are containerized and managed through Terraform and GitHub Actions for continuous integration and delivery.

## Infrastructure

Terraform manages all GCP resources in the `/terraform` directory. The infrastructure is defined declaratively, enabling reproducible deployments and version-controlled configuration changes.

## Services

All 6 services are containerized with Docker and deployed to Cloud Run as independently scalable microservices.

## Key Resources

- **Cloud Run:** Hosts all microservices as independently scalable containers, providing automatic scaling and managed infrastructure.
- **Artifact Registry:** Stores Docker images for all service containers, enabling versioned and secure image management.
- **IAM:** Manages service account permissions, enforcing least-privilege access across all deployed resources.
- **Cloud Storage:** Stores ML models and analysis artifacts used by the Decision Engine and Code Analysis Engine.

## CI/CD

GitHub Actions workflows handle automated testing and deployment. On each push to the main branch, workflows build container images, push them to Artifact Registry, and deploy updated services to Cloud Run.

## Configuration Files

The Terraform configuration is organized into the following files within the `/terraform` directory:

- `cloudrun.tf` — Cloud Run service definitions and scaling configuration
- `iam.tf` — Service account and permission bindings
- `artifact_registry.tf` — Container image repository configuration
- `variables.tf` — Parameterized infrastructure variables
