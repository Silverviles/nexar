# Nexar — Cloud Run Deployment Guide

This guide walks you through deploying all 6 Nexar micro-services to
**Google Cloud Run** with **automatic deployment on every push to `main`** and
**manual deployment from any branch** via GitHub's workflow dispatch UI.

On push, only the services whose source files actually changed are rebuilt and
deployed, so CI stays fast and cheap. Manual runs let you pick a branch and
choose which service(s) to deploy — including an "all" option.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Step 1 — Create a GCP Project](#step-1--create-a-gcp-project-or-pick-an-existing-one)
4. [Step 2 — Enable Required GCP APIs](#step-2--enable-required-gcp-apis)
5. [Step 3 — Create an Artifact Registry Repository](#step-3--create-an-artifact-registry-repository)
6. [Step 4 — Upload ML Models to Cloud Storage](#step-4--upload-ml-models-to-cloud-storage)
7. [Step 5 — Set up Workload Identity Federation](#step-5--set-up-workload-identity-federation-keyless-github--gcp-auth)
8. [Step 6 — Add GitHub Secrets](#step-6--add-github-secrets)
9. [Step 7 — Add the GitHub Actions Workflows](#step-7--add-the-github-actions-workflows)
10. [Step 8 — Push to main and Watch it Deploy](#step-8--push-to-main-and-watch-it-deploy)
11. [Step 8b — Manual Deployment from Any Branch](#step-8b--manual-deployment-from-any-branch)
12. [Step 9 — Wire Up Service-to-Service URLs](#step-9--post-deploy-wire-up-service-to-service-urls)
13. [Step 10 — Set Up Redis](#step-10--set-up-redis-for-hardware-abstraction-layer)
14. [Appendix A — Full Workflow Files](#appendix-a--full-workflow-files)
15. [Appendix B — Rollback](#appendix-b--rollback)
16. [Troubleshooting](#troubleshooting)

---

## 1. Architecture Overview

```
GitHub (push to main)                GitHub (manual dispatch — any branch)
        │                                       │
        ▼                                       ▼
GitHub Actions ── paths-filter ──┐   GitHub Actions ── user picks service(s) ──┐
                                 │                                              │
                                 └──────────────────┬───────────────────────────┘
                                                    │
                                                    ▼
                                          deploy-service.yml
                                                    │
        ┌───────────────────────────────────────────┼──────────────────────────────────┐
        │                    │                      │                │                  │
        ▼                    ▼                      ▼                ▼                  ▼
  nexar-api        nexar-frontend     nexar-ai-code-converter   nexar-code-      nexar-decision-
  (Cloud Run)      (Cloud Run)        (Cloud Run + GCS models)  analysis-engine  engine (Cloud Run)
                                                                (Cloud Run +        ...
                                                                 GCS models)   nexar-hardware-
                                                                               abstraction-layer
```

| Trigger | Branch | Services deployed |
|---|---|---|
| `push` | `main` only | Auto-detected from changed files |
| `workflow_dispatch` | Any branch (user picks in UI) | User picks from dropdown (`all` or a single service) |

| Service | Language | Port | Needs ML Models from GCS? |
|---|---|---|---|
| `api` | Node.js / Express | 3000 | No |
| `frontend` | React + Vite → nginx | 80 | No |
| `ai-code-converter` | Python / FastAPI | 8001 | **Yes** — CodeT5 model weights |
| `code-analysis-engine` | Python / FastAPI | 8002 | **Yes** — sklearn `.pkl` files |
| `decision-engine` | Python / FastAPI | 8003 | No (models committed in repo) |
| `hardware-abstraction-layer` | Python / FastAPI | 8004 | No |

---

## 2. Prerequisites

Before you start, make sure you have:

- [ ] A **GitHub repository** containing the Nexar mono-repo.
- [ ] A **Google Cloud account** with billing enabled.
- [ ] The **`gcloud` CLI** installed and authenticated:
  ```bash
  gcloud --version          # confirm it's installed
  gcloud auth login         # log in to your account
  ```
- [ ] The ML model files on your local machine:
  - `codet5-quantum-best/` — the HuggingFace model directory for ai-code-converter
  - `random_forest.pkl`, `gradient_boosting.pkl`, `scaler.pkl`, `label_encoder.pkl`,
    `feature_names.json` — for code-analysis-engine

---

## Step 1 — Create a GCP Project (or pick an existing one)

If you already have a project, skip the create command.

```bash
gcloud projects create nexar-prod --name="Nexar Production"
gcloud config set project nexar-prod
```

Set shell variables so the rest of this guide is copy-pastable:

```bash
export PROJECT_ID="nexar-prod"       # ← replace with your actual project ID
export REGION="us-central1"          # ← pick your preferred region
```

Get your numeric project number (needed in Step 5):

```bash
export PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" \
  --format='value(projectNumber)')
echo "Project number: $PROJECT_NUMBER"
```

---

## Step 2 — Enable Required GCP APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  storage.googleapis.com \
  --project="$PROJECT_ID"
```

Wait a minute or two for the APIs to propagate.

---

## Step 3 — Create an Artifact Registry Repository

This is where your Docker images will be stored.

```bash
gcloud artifacts repositories create nexar \
  --repository-format=docker \
  --location="$REGION" \
  --description="Nexar service images" \
  --project="$PROJECT_ID"
```

Verify it was created:

```bash
gcloud artifacts repositories list --location="$REGION" --project="$PROJECT_ID"
```

You should see `nexar` in the list.

---

## Step 4 — Upload ML Models to Cloud Storage

Two services need ML model files that are too large or too sensitive to commit
to Git. During CI, the workflow downloads these from a GCS bucket and places
them in the Docker build context so `COPY . .` in each Dockerfile bakes them
into the image.

### 4a. Create a GCS bucket

```bash
export MODELS_BUCKET="gs://${PROJECT_ID}-ml-models"

gsutil mb -l "$REGION" -p "$PROJECT_ID" "$MODELS_BUCKET"
```

### 4b. Organize & upload the models

Your bucket should end up with this layout:

```
gs://<PROJECT_ID>-ml-models/
├── ai-code-converter/
│   └── models/                      ← CodeT5 HuggingFace model files
│       ├── config.json
│       ├── tokenizer.json
│       ├── tokenizer_config.json
│       ├── special_tokens_map.json
│       ├── spiece.model
│       └── model.safetensors        (or pytorch_model.bin)
│
└── code-analysis-engine/
    └── models/
        └── trained/                 ← sklearn .pkl files
            ├── random_forest.pkl
            ├── gradient_boosting.pkl
            ├── scaler.pkl
            ├── label_encoder.pkl
            └── feature_names.json
```

Upload from your local machine:

```bash
# Upload the ai-code-converter model
# Replace the path with wherever your codet5-quantum-best directory is
gsutil -m cp -r /path/to/codet5-quantum-best/* \
  "$MODELS_BUCKET/ai-code-converter/models/"

# Upload the code-analysis-engine models
gsutil -m cp \
  /path/to/models/trained/random_forest.pkl \
  /path/to/models/trained/gradient_boosting.pkl \
  /path/to/models/trained/scaler.pkl \
  /path/to/models/trained/label_encoder.pkl \
  /path/to/models/trained/feature_names.json \
  "$MODELS_BUCKET/code-analysis-engine/models/trained/"
```

Verify everything is there:

```bash
gsutil ls -r "$MODELS_BUCKET"
```

### How the models end up in Docker images

During CI, the GitHub Actions workflow runs `gsutil` to download the model
files into the service's source directory **before** `docker build`. Since
each Dockerfile does `COPY . .`, the models are included in the image
automatically — no Dockerfile changes required.

For example, for `code-analysis-engine`:
1. Workflow downloads `.pkl` files into `code-analysis-engine/models/trained/`.
2. `docker build code-analysis-engine/` runs.
3. `COPY . .` in the Dockerfile picks up `models/trained/*.pkl`.
4. At runtime the code in `modules/ml_algorithm_classifier.py` loads from
   `models/trained/` which resolves to `/app/models/trained/` inside the container.

---

## Step 5 — Set up Workload Identity Federation (keyless GitHub ↔ GCP auth)

This lets GitHub Actions authenticate to GCP **without** storing a
service-account JSON key as a secret. It is the Google-recommended approach.

### 5a. Set variables

```bash
export GITHUB_ORG="your-github-username-or-org"   # ← replace this
export GITHUB_REPO="nexar"                          # ← replace if different
export SA_NAME="github-deploy"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
```

### 5b. Create a Workload Identity Pool

```bash
gcloud iam workload-identity-pools create "github-pool" \
  --project="$PROJECT_ID" \
  --location="global" \
  --display-name="GitHub Actions Pool"
```

### 5c. Create an OIDC Provider in the pool

> **⚠️ Important:** The `--attribute-condition` flag is **required** by Google.
> It restricts token acceptance to only your specific repository. If you omit
> it you will get the error:
> `INVALID_ARGUMENT: The attribute condition must reference one of the provider's claims`

```bash
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="$PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="attribute.repository == '${GITHUB_ORG}/${GITHUB_REPO}'" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

### 5d. Create a Service Account for deployments

```bash
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="GitHub Actions Deploy SA" \
  --project="$PROJECT_ID"
```

### 5e. Grant the Service Account required roles

```bash
# Deploy and manage Cloud Run services
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.admin"

# Push images to Artifact Registry
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/artifactregistry.writer"

# Read model files from Cloud Storage
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectViewer"

# Allow Cloud Run to use this SA (actAs permission)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountUser"
```

### 5f. Allow GitHub to impersonate this Service Account

```bash
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --project="$PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}"
```

### 5g. Note down the two values for GitHub Secrets

```bash
# WIF_PROVIDER — copy this entire output:
echo "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/providers/github-provider"

# WIF_SERVICE_ACCOUNT — copy this:
echo "$SA_EMAIL"
```

Save these two values — you will paste them in the next step.

---

## Step 6 — Add GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** →
**Actions** → **New repository secret**.

Add these **5** secrets:

| Secret Name | Example Value | Description |
|---|---|---|
| `GCP_PROJECT_ID` | `nexar-prod` | Your GCP project ID |
| `GCP_REGION` | `us-central1` | Region for Cloud Run and Artifact Registry |
| `GCS_MODELS_BUCKET` | `gs://nexar-prod-ml-models` | Full `gs://` URI of your models bucket |
| `WIF_PROVIDER` | `projects/123456/locations/global/workloadIdentityPools/github-pool/providers/github-provider` | Output from Step 5g |
| `WIF_SERVICE_ACCOUNT` | `github-deploy@nexar-prod.iam.gserviceaccount.com` | Output from Step 5g |

---

## Step 7 — Add the GitHub Actions Workflows

Create these two files in your repository. Full contents are in
[Appendix A](#appendix-a--full-workflow-files).

```
your-repo/
├── .github/
│   └── workflows/
│       ├── deploy-cloudrun.yml    ← main orchestrator (push + manual dispatch)
│       └── deploy-service.yml     ← reusable per-service builder/deployer
├── api/
├── frontend/
├── ai-code-converter/
├── code-analysis-engine/
├── decision-engine/
└── hardware-abstraction-layer/
```

**`deploy-cloudrun.yml`** (orchestrator):
- **Automatic (push):** Triggers on pushes to `main`. Uses
  [`dorny/paths-filter`](https://github.com/dorny/paths-filter) to detect
  which service directories had file changes. Only changed services are deployed.
- **Manual (workflow_dispatch):** Can be triggered from any branch via the
  GitHub Actions UI. The user selects which service to deploy from a dropdown
  (or picks `all` to deploy everything). No paths-filter is used — the
  selected services are deployed unconditionally from the chosen branch.
- Unchanged / unselected services are skipped entirely — no wasted build time.
- Writes a summary table to the Actions run showing which services will be deployed.

**`deploy-service.yml`** (reusable, called once per changed service):
1. Checks out the code.
2. Authenticates to GCP via Workload Identity Federation (no JSON keys).
3. If the service needs models: downloads them from GCS into the build context.
4. Builds the Docker image and pushes it to Artifact Registry (tagged with
   the Git commit SHA and `latest`).
5. Deploys the new image to Cloud Run.

---

## Step 8 — Push to `main` and Watch it Deploy

```bash
git add .github/
git commit -m "ci: add Cloud Run auto-deploy on push to main"
git push origin main
```

Go to your repository → **Actions** tab. You should see the
**"Deploy to Cloud Run"** workflow running.

> **First-run note:** The very first push will trigger a deploy for every
> service because the change-detection compares against the previous commit
> and all paths are effectively "new". After that, only genuinely changed
> services will re-deploy.

If a service is skipped, its job will be greyed out with
"Skipping — condition not met".

---

## Step 8b — Manual Deployment from Any Branch

You can trigger a deployment manually from **any branch** — useful for testing
feature branches, force-redeploying after config changes, or deploying hotfixes
without merging to `main` first.

### How to trigger a manual deployment

1. Go to your repository on GitHub.
2. Click the **Actions** tab.
3. In the left sidebar, click **"Deploy to Cloud Run"**.
4. Click the **"Run workflow"** button (top-right).
5. In the dialog that appears:
   - **Use workflow from:** select the branch you want to deploy.
   - **Services to deploy:** pick a single service or `all`.
6. Click **"Run workflow"**.

![Manual dispatch UI](https://docs.github.com/assets/cb-29573/mw-1440/images/help/actions/actions-manually-run-workflow.webp)

### Available options

| Option | Deploys |
|--------|---------|
| `all` | All 6 services from the selected branch |
| `api` | Only the `api` service |
| `frontend` | Only the `frontend` service |
| `ai-code-converter` | Only `ai-code-converter` (downloads models from GCS) |
| `code-analysis-engine` | Only `code-analysis-engine` (downloads models from GCS) |
| `decision-engine` | Only the `decision-engine` service |
| `hardware-abstraction-layer` | Only the `hardware-abstraction-layer` service |

### Behavior differences from automatic deployment

| | Push to `main` | Manual dispatch |
|---|---|---|
| **Branch** | Always `main` | Any branch you choose |
| **Service selection** | Auto-detected from changed files | You choose from dropdown |
| **Paths filter** | Active — only changed dirs deploy | Skipped — your selection always deploys |
| **Models download** | Yes, for services that need them | Yes, for services that need them |

> **Tip:** The run summary (visible in the Actions UI) shows a table of which
> services are targeted for deployment, so you can confirm before watching the
> build logs.

---

## Step 9 — Post-Deploy: Wire Up Service-to-Service URLs

In Docker Compose, services talk via internal hostnames like
`http://decision-engine:8003`. On Cloud Run, each service gets a unique
public URL like `https://nexar-api-abc123-uc.a.run.app`.

### 9a. Get the deployed URLs

```bash
for svc in api frontend ai-code-converter code-analysis-engine decision-engine hardware-abstraction-layer; do
  echo "nexar-$svc:"
  gcloud run services describe "nexar-$svc" \
    --region="$REGION" \
    --format='value(status.url)' \
    2>/dev/null || echo "  (not deployed yet)"
done
```

### 9b. Set environment variables on the API service

The `api` service needs to know where to find the backend services. Replace
each URL placeholder with the actual URL from step 9a:

```bash
gcloud run services update nexar-api \
  --region="$REGION" \
  --set-env-vars="\
PORT=3000,\
DECISION_ENGINE_URL=https://nexar-decision-engine-XXXXX-uc.a.run.app,\
AI_CODE_CONVERTER_URL=https://nexar-ai-code-converter-XXXXX-uc.a.run.app,\
CODE_ANALYSIS_ENGINE_URL=https://nexar-code-analysis-engine-XXXXX-uc.a.run.app,\
HARDWARE_LAYER_URL=https://nexar-hardware-abstraction-layer-XXXXX-uc.a.run.app"
```

### 9c. Frontend → API connection

The frontend's `VITE_API_BASE_URL` is baked in at build time via the
Dockerfile's `ARG`. You have two options:

**Option A — Build arg in CI:** Add a `--build-arg` to the `docker build`
command for the frontend service in the workflow.

**Option B — Nginx reverse proxy (recommended):** Configure the frontend's
`nginx.conf` to proxy `/api` requests to the Cloud Run API URL. This avoids
CORS issues and keeps the frontend build generic.

---

## Step 10 — Set Up Redis (for Hardware Abstraction Layer)

The `hardware-abstraction-layer` service requires Redis. Cloud Run doesn't
run Redis as a sidecar, so you need an external option.

### Option A: Google Cloud Memorystore (recommended for production)

```bash
# Create a Serverless VPC Access connector first
gcloud compute networks vpc-access connectors create nexar-connector \
  --region="$REGION" \
  --range="10.8.0.0/28"

# Create a Redis instance
gcloud redis instances create nexar-redis \
  --size=1 \
  --region="$REGION" \
  --redis-version=redis_7_0 \
  --project="$PROJECT_ID"

# Get the Redis IP
REDIS_HOST=$(gcloud redis instances describe nexar-redis \
  --region="$REGION" \
  --format='value(host)')

# Update the HAL service with Redis connection and VPC connector
gcloud run services update nexar-hardware-abstraction-layer \
  --region="$REGION" \
  --set-env-vars="REDIS_HOST=$REDIS_HOST,REDIS_PORT=6379" \
  --vpc-connector=nexar-connector
```

> Memorystore requires a **Serverless VPC Access connector** so Cloud Run can
> reach it. See the
> [official docs](https://cloud.google.com/memorystore/docs/redis/connect-redis-instance-cloud-run).

### Option B: Redis Cloud (simpler, free tier available)

Sign up at [redis.com](https://redis.com), create a free database, and set
`REDIS_HOST` / `REDIS_PORT` env vars on the Cloud Run service:

```bash
gcloud run services update nexar-hardware-abstraction-layer \
  --region="$REGION" \
  --set-env-vars="REDIS_HOST=your-redis-cloud-host.com,REDIS_PORT=12345"
```

---

## Appendix A — Full Workflow Files

### `.github/workflows/deploy-cloudrun.yml`

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

  workflow_dispatch:
    inputs:
      services:
        description: "Services to deploy (comma-separated, or 'all')"
        required: true
        default: "all"
        type: choice
        options:
          - all
          - api
          - frontend
          - ai-code-converter
          - code-analysis-engine
          - decision-engine
          - hardware-abstraction-layer

permissions:
  contents: read
  id-token: write

env:
  GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  GCP_REGION: ${{ secrets.GCP_REGION }}
  GAR_REPOSITORY: nexar
  MODELS_BUCKET: ${{ secrets.GCS_MODELS_BUCKET }}

jobs:
  # ─── Detect which service directories changed ────────────────────
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.set-outputs.outputs.api }}
      frontend: ${{ steps.set-outputs.outputs.frontend }}
      ai-code-converter: ${{ steps.set-outputs.outputs.ai-code-converter }}
      code-analysis-engine: ${{ steps.set-outputs.outputs.code-analysis-engine }}
      decision-engine: ${{ steps.set-outputs.outputs.decision-engine }}
      hardware-abstraction-layer: ${{ steps.set-outputs.outputs.hardware-abstraction-layer }}
    steps:
      - uses: actions/checkout@v4

      # Path-based detection for push events
      - uses: dorny/paths-filter@v3
        id: changes
        if: github.event_name == 'push'
        with:
          filters: |
            api:
              - 'api/**'
            frontend:
              - 'frontend/**'
            ai-code-converter:
              - 'ai-code-converter/**'
            code-analysis-engine:
              - 'code-analysis-engine/**'
            decision-engine:
              - 'decision-engine/**'
            hardware-abstraction-layer:
              - 'hardware-abstraction-layer/**'

      # Merge push detection + manual dispatch into unified outputs
      - name: Set outputs
        id: set-outputs
        shell: bash
        run: |
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            SELECTED="${{ github.event.inputs.services }}"
            echo "🔧 Manual dispatch — selected services: ${SELECTED}"

            ALL_SERVICES="api frontend ai-code-converter code-analysis-engine decision-engine hardware-abstraction-layer"

            for svc in ${ALL_SERVICES}; do
              if [[ "${SELECTED}" == "all" || "${SELECTED}" == "${svc}" ]]; then
                echo "${svc}=true" >> "$GITHUB_OUTPUT"
              else
                echo "${svc}=false" >> "$GITHUB_OUTPUT"
              fi
            done
          else
            echo "🔍 Push event — using paths-filter results"
            echo "api=${{ steps.changes.outputs.api }}" >> "$GITHUB_OUTPUT"
            echo "frontend=${{ steps.changes.outputs.frontend }}" >> "$GITHUB_OUTPUT"
            echo "ai-code-converter=${{ steps.changes.outputs.ai-code-converter }}" >> "$GITHUB_OUTPUT"
            echo "code-analysis-engine=${{ steps.changes.outputs.code-analysis-engine }}" >> "$GITHUB_OUTPUT"
            echo "decision-engine=${{ steps.changes.outputs.decision-engine }}" >> "$GITHUB_OUTPUT"
            echo "hardware-abstraction-layer=${{ steps.changes.outputs.hardware-abstraction-layer }}" >> "$GITHUB_OUTPUT"
          fi

      - name: Summary
        shell: bash
        run: |
          echo "### Deployment targets" >> "$GITHUB_STEP_SUMMARY"
          echo "| Service | Deploy |" >> "$GITHUB_STEP_SUMMARY"
          echo "|---------|--------|" >> "$GITHUB_STEP_SUMMARY"
          echo "| api | \`${{ steps.set-outputs.outputs.api }}\` |" >> "$GITHUB_STEP_SUMMARY"
          echo "| frontend | \`${{ steps.set-outputs.outputs.frontend }}\` |" >> "$GITHUB_STEP_SUMMARY"
          echo "| ai-code-converter | \`${{ steps.set-outputs.outputs.ai-code-converter }}\` |" >> "$GITHUB_STEP_SUMMARY"
          echo "| code-analysis-engine | \`${{ steps.set-outputs.outputs.code-analysis-engine }}\` |" >> "$GITHUB_STEP_SUMMARY"
          echo "| decision-engine | \`${{ steps.set-outputs.outputs.decision-engine }}\` |" >> "$GITHUB_STEP_SUMMARY"
          echo "| hardware-abstraction-layer | \`${{ steps.set-outputs.outputs.hardware-abstraction-layer }}\` |" >> "$GITHUB_STEP_SUMMARY"

  # ─── Deploy each changed service ─────────────────────────────────

  deploy-api:
    needs: detect-changes
    if: needs.detect-changes.outputs.api == 'true'
    uses: ./.github/workflows/deploy-service.yml
    with:
      service_name: api
      service_dir: api
      port: "3000"
      needs_models: false
    secrets: inherit

  deploy-frontend:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    uses: ./.github/workflows/deploy-service.yml
    with:
      service_name: frontend
      service_dir: frontend
      port: "80"
      needs_models: false
    secrets: inherit

  deploy-ai-code-converter:
    needs: detect-changes
    if: needs.detect-changes.outputs.ai-code-converter == 'true'
    uses: ./.github/workflows/deploy-service.yml
    with:
      service_name: ai-code-converter
      service_dir: ai-code-converter
      port: "8001"
      needs_models: true
      models_gcs_path: "ai-code-converter/models"
      models_dest_path: "models"
    secrets: inherit

  deploy-code-analysis-engine:
    needs: detect-changes
    if: needs.detect-changes.outputs.code-analysis-engine == 'true'
    uses: ./.github/workflows/deploy-service.yml
    with:
      service_name: code-analysis-engine
      service_dir: code-analysis-engine
      port: "8002"
      needs_models: true
      models_gcs_path: "code-analysis-engine/models/trained"
      models_dest_path: "models/trained"
    secrets: inherit

  deploy-decision-engine:
    needs: detect-changes
    if: needs.detect-changes.outputs.decision-engine == 'true'
    uses: ./.github/workflows/deploy-service.yml
    with:
      service_name: decision-engine
      service_dir: decision-engine
      port: "8003"
      needs_models: false
    secrets: inherit

  deploy-hardware-abstraction-layer:
    needs: detect-changes
    if: needs.detect-changes.outputs.hardware-abstraction-layer == 'true'
    uses: ./.github/workflows/deploy-service.yml
    with:
      service_name: hardware-abstraction-layer
      service_dir: hardware-abstraction-layer
      port: "8004"
      needs_models: false
    secrets: inherit
```

### `.github/workflows/deploy-service.yml`

```yaml
name: Deploy Single Service to Cloud Run

on:
  workflow_call:
    inputs:
      service_name:
        required: true
        type: string
      service_dir:
        required: true
        type: string
      port:
        required: true
        type: string
      needs_models:
        required: true
        type: boolean
      models_gcs_path:
        required: false
        type: string
        default: ""
      models_dest_path:
        required: false
        type: string
        default: ""

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write   # required for Workload Identity Federation

    steps:
      # ── Check out the repo ────────────────────────────────────
      - name: Checkout code
        uses: actions/checkout@v4

      # ── Authenticate to GCP (keyless via WIF) ─────────────────
      - name: Authenticate to Google Cloud
        id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}

      # ── Set up gcloud CLI ─────────────────────────────────────
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      # ── Configure Docker for Artifact Registry ────────────────
      - name: Configure Docker for GAR
        run: |
          gcloud auth configure-docker \
            "${{ secrets.GCP_REGION }}-docker.pkg.dev" --quiet

      # ── Download models from GCS (only when needed) ───────────
      - name: Download ML models from GCS
        if: inputs.needs_models
        run: |
          echo "📦 Downloading models from ${{ secrets.GCS_MODELS_BUCKET }}/${{ inputs.models_gcs_path }} ..."
          mkdir -p "${{ inputs.service_dir }}/${{ inputs.models_dest_path }}"
          gsutil -m cp -r \
            "${{ secrets.GCS_MODELS_BUCKET }}/${{ inputs.models_gcs_path }}/*" \
            "${{ inputs.service_dir }}/${{ inputs.models_dest_path }}/"
          echo "✅ Models downloaded:"
          ls -lhR "${{ inputs.service_dir }}/${{ inputs.models_dest_path }}/"

      # ── Build & push the Docker image ─────────────────────────
      - name: Build and push Docker image
        run: |
          IMAGE="${{ secrets.GCP_REGION }}-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/nexar/${{ inputs.service_name }}"
          TAG="${IMAGE}:${{ github.sha }}"
          TAG_LATEST="${IMAGE}:latest"

          echo "🐳 Building ${TAG} ..."
          docker build \
            -t "${TAG}" \
            -t "${TAG_LATEST}" \
            "${{ inputs.service_dir }}"

          echo "📤 Pushing images ..."
          docker push "${TAG}"
          docker push "${TAG_LATEST}"

      # ── Deploy to Cloud Run ───────────────────────────────────
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: nexar-${{ inputs.service_name }}
          region: ${{ secrets.GCP_REGION }}
          image: ${{ secrets.GCP_REGION }}-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/nexar/${{ inputs.service_name }}:${{ github.sha }}
          flags: |
            --port=${{ inputs.port }}
            --allow-unauthenticated
```

---

## Appendix B — Rollback

Every image is tagged with the Git commit SHA, so you can roll back to any
previous version instantly.

```bash
# 1. List recent images for a service
gcloud artifacts docker images list \
  "$REGION-docker.pkg.dev/$PROJECT_ID/nexar/api" \
  --sort-by="~UPDATE_TIME" --limit=5

# 2. Deploy a previous version by its commit SHA tag
gcloud run deploy nexar-api \
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/nexar/api:PREVIOUS_COMMIT_SHA" \
  --region="$REGION"
```

---

## Troubleshooting

### "INVALID_ARGUMENT: The attribute condition must reference one of the provider's claims"

When creating the OIDC provider in Step 5c, you **must** include the
`--attribute-condition` flag. Google now requires it for security. Make sure the
command includes:

```
--attribute-condition="attribute.repository == 'YOUR_ORG/YOUR_REPO'"
```

The value must exactly match `owner/repo` as it appears on GitHub
(case-sensitive).

### "Permission denied" during gsutil cp

The deploy service account needs `roles/storage.objectViewer`:

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectViewer"
```

### "Could not find image" during Cloud Run deploy

Ensure the Artifact Registry repository and Cloud Run service are in the
**same region** (both use the `GCP_REGION` secret).

### Cloud Run service can't reach another service

- Verify the `api` service has the correct backend URLs set as env vars
  (see Step 9).
- All services are deployed with `--allow-unauthenticated` by default. If you
  removed that flag, configure IAM invoker roles for service-to-service auth:
  ```bash
  gcloud run services add-iam-policy-binding nexar-decision-engine \
    --region="$REGION" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.invoker"
  ```

### Build is slow for ai-code-converter

The ai-code-converter installs PyTorch which is ~800 MB. The first build takes
5–10 minutes. Subsequent builds are faster because Docker caches the pip install
layer (it only re-runs if `requirements.txt` changes).

### Models not found at runtime

Check that:

1. **GCS paths match the bucket structure.** The `models_gcs_path` values in
   `deploy-cloudrun.yml` must match the prefixes you uploaded to in Step 4.
2. **Destination paths match what the code expects:**
   - `ai-code-converter`: env var `MODEL_PATH=/app/models` (set in Dockerfile).
     The workflow downloads into `ai-code-converter/models/` which becomes
     `/app/models/` in the container.
   - `code-analysis-engine`: hardcoded `models/trained/` in
     `modules/ml_algorithm_classifier.py`. The workflow downloads into
     `code-analysis-engine/models/trained/` which becomes
     `/app/models/trained/` in the container.
3. **`.dockerignore` doesn't exclude model files.** The current `.dockerignore`
   files for both services do not exclude `.pkl` or model files — verify you
   haven't added any exclusions.

### Nothing deployed — "condition not met" on all jobs

**On push:** This means no files changed inside any of the 6 service
directories. This is expected if you only changed the README, deployment docs,
or `docker-compose.yml`.

**Fix:** Use the manual dispatch to deploy the services you need — no code
changes required. See
[Step 8b — Manual Deployment from Any Branch](#step-8b--manual-deployment-from-any-branch).

Alternatively, you can still deploy a single service via `gcloud` directly:

```bash
gcloud run deploy nexar-api \
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/nexar/api:latest" \
  --region="$REGION"
```

### How to redeploy ALL services at once

The easiest way is to use the **manual dispatch**:

1. Go to **Actions** → **"Deploy to Cloud Run"** → **"Run workflow"**.
2. Select the branch (e.g., `main`).
3. Select **`all`** from the services dropdown.
4. Click **"Run workflow"**.

This will deploy all 6 services from the selected branch without needing any
code changes or dummy commits.

> **Alternative (push-based):** If you prefer triggering via a push, you can
> still touch a file in each service directory:
>
> ```bash
> for dir in api frontend ai-code-converter code-analysis-engine decision-engine hardware-abstraction-layer; do
>   touch "$dir/.deploy-trigger"
> done
> git add -A
> git commit -m "ci: force redeploy all services"
> git push origin main
> ```
>
> Keep these `.deploy-trigger` files tracked but empty so paths-filter picks
> them up.