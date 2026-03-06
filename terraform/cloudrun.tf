# ──────────────────────────────────────────────────────────────────────────────
# Cloud Run Services — All 6 Nexar Microservices (via reusable module)
# ──────────────────────────────────────────────────────────────────────────────

locals {
  # Resolve per-service image tags (fall back to var.image_tag)
  image_tag_for = {
    for svc in ["api", "frontend", "ai-code-converter", "code-analysis-engine", "decision-engine", "hardware-abstraction-layer"] :
    svc => lookup(var.image_tags, svc, var.image_tag)
  }

  # Base image URI prefix
  image_prefix = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repository}"

  # Frontend API_URL: use override if set, otherwise auto-wire to the deployed API service URL
  frontend_api_url = (
    var.frontend_api_url_override != ""
    ? var.frontend_api_url_override
    : module.api.uri
  )
}

# ──────────────────────────────────────────────────────────────────────────────
# 1. API (Node.js / Express — port 3000)
#
#    The API gateway that proxies requests to all backend services.
#    Env vars are auto-wired to the other services' Cloud Run URLs.
# ──────────────────────────────────────────────────────────────────────────────

module "api" {
  source = "./modules/cloudrun-service"

  service_name   = "nexar-api"
  location       = var.region
  image          = "${local.image_prefix}/api:${local.image_tag_for["api"]}"
  container_port = 3000

  cpu    = var.service_resources["api"].cpu
  memory = var.service_resources["api"].memory

  max_instances   = var.max_instances
  min_instances   = var.min_instances
  timeout_seconds = var.timeout_seconds

  allow_unauthenticated = var.allow_unauthenticated

  env_vars = {
    DECISION_ENGINE_URL      = module.decision_engine.uri
    AI_CODE_CONVERTER_URL    = module.ai_code_converter.uri
    CODE_ANALYSIS_ENGINE_URL = module.code_analysis_engine.uri
    HARDWARE_LAYER_URL       = module.hardware_abstraction_layer.uri
    FRONTEND_URL             = var.frontend_url
    GOOGLE_CLIENT_ID         = var.google_oauth_client_id
    GOOGLE_CLIENT_SECRET     = var.google_oauth_client_secret
  }
}

# ──────────────────────────────────────────────────────────────────────────────
# 2. Frontend (React + Vite → nginx — port 8080)
#
#    Static SPA served by nginx. The API_URL env var configures the nginx
#    reverse proxy target at container startup via envsubst.
# ──────────────────────────────────────────────────────────────────────────────

module "frontend" {
  source = "./modules/cloudrun-service"

  service_name   = "nexar-frontend"
  location       = var.region
  image          = "${local.image_prefix}/frontend:${local.image_tag_for["frontend"]}"
  container_port = 8080

  cpu    = var.service_resources["frontend"].cpu
  memory = var.service_resources["frontend"].memory

  max_instances   = var.max_instances
  min_instances   = var.min_instances
  timeout_seconds = var.timeout_seconds

  allow_unauthenticated = var.allow_unauthenticated

  env_vars = {
    API_URL = local.frontend_api_url
  }
}

# ──────────────────────────────────────────────────────────────────────────────
# 3. AI Code Converter (Python / FastAPI — port 8001)
#
#    CodeT5 model inference service. Models are baked into the Docker image
#    during CI (downloaded from GCS).
# ──────────────────────────────────────────────────────────────────────────────

module "ai_code_converter" {
  source = "./modules/cloudrun-service"

  service_name   = "nexar-ai-code-converter"
  location       = var.region
  image          = "${local.image_prefix}/ai-code-converter:${local.image_tag_for["ai-code-converter"]}"
  container_port = 8001

  cpu    = var.service_resources["ai-code-converter"].cpu
  memory = var.service_resources["ai-code-converter"].memory

  max_instances   = var.max_instances
  min_instances   = var.min_instances
  timeout_seconds = var.timeout_seconds

  allow_unauthenticated = var.allow_unauthenticated

  env_vars = {
    MODEL_PATH    = "/app/models"
    GCS_MODEL_URI = "gs://${var.models_bucket_name}/${var.ai_code_converter_model_gcs_path}"
  }
}

# ──────────────────────────────────────────────────────────────────────────────
# 4. Code Analysis Engine (Python / FastAPI — port 8002)
#
#    Quantum code analysis with sklearn ML classifiers. Models are baked into
#    the Docker image during CI (downloaded from GCS).
# ──────────────────────────────────────────────────────────────────────────────

module "code_analysis_engine" {
  source = "./modules/cloudrun-service"

  service_name   = "nexar-code-analysis-engine"
  location       = var.region
  image          = "${local.image_prefix}/code-analysis-engine:${local.image_tag_for["code-analysis-engine"]}"
  container_port = 8002

  cpu    = var.service_resources["code-analysis-engine"].cpu
  memory = var.service_resources["code-analysis-engine"].memory

  max_instances   = var.max_instances
  min_instances   = var.min_instances
  timeout_seconds = var.timeout_seconds

  allow_unauthenticated = var.allow_unauthenticated

  env_vars = {
    ML_MODELS_DIR = "models/trained"
    GCS_MODEL_URI = "gs://${var.models_bucket_name}/${var.code_analysis_engine_model_gcs_path}"
  }
}

# ──────────────────────────────────────────────────────────────────────────────
# 5. Decision Engine (Python / FastAPI — port 8003)
#
#    Quantum algorithm selection and optimization recommendations.
#    Models are committed in the repo (no GCS download needed).
# ──────────────────────────────────────────────────────────────────────────────

module "decision_engine" {
  source = "./modules/cloudrun-service"

  service_name   = "nexar-decision-engine"
  location       = var.region
  image          = "${local.image_prefix}/decision-engine:${local.image_tag_for["decision-engine"]}"
  container_port = 8003

  cpu    = var.service_resources["decision-engine"].cpu
  memory = var.service_resources["decision-engine"].memory

  max_instances   = var.max_instances
  min_instances   = var.min_instances
  timeout_seconds = var.timeout_seconds

  allow_unauthenticated = var.allow_unauthenticated

  env_vars = {
    HOST = "0.0.0.0"
  }
}

# ──────────────────────────────────────────────────────────────────────────────
# 6. Hardware Abstraction Layer (Python / FastAPI — port 8004)
#
#    Quantum hardware provider abstraction with job management.
#    Uses in-memory storage for jobs (Redis not required).
# ──────────────────────────────────────────────────────────────────────────────

module "hardware_abstraction_layer" {
  source = "./modules/cloudrun-service"

  service_name   = "nexar-hardware-abstraction-layer"
  location       = var.region
  image          = "${local.image_prefix}/hardware-abstraction-layer:${local.image_tag_for["hardware-abstraction-layer"]}"
  container_port = 8004

  cpu    = var.service_resources["hardware-abstraction-layer"].cpu
  memory = var.service_resources["hardware-abstraction-layer"].memory

  max_instances   = var.max_instances
  min_instances   = var.min_instances
  timeout_seconds = var.timeout_seconds

  allow_unauthenticated = var.allow_unauthenticated
}
