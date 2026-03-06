# ──────────────────────────────────────────────────────────────────────────────
# Project & Region
# ──────────────────────────────────────────────────────────────────────────────

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for all resources"
  type        = string
  default     = "us-central1"
}

# ──────────────────────────────────────────────────────────────────────────────
# Artifact Registry
# ──────────────────────────────────────────────────────────────────────────────

variable "artifact_registry_repository" {
  description = "Name of the Artifact Registry Docker repository"
  type        = string
  default     = "nexar"
}

# ──────────────────────────────────────────────────────────────────────────────
# Container Image Tags
# ──────────────────────────────────────────────────────────────────────────────

variable "image_tag" {
  description = "Default image tag for all services (e.g. a Git SHA or 'latest')"
  type        = string
  default     = "latest"
}

variable "image_tags" {
  description = "Per-service image tag overrides. Keys are service names, values are tags. Falls back to var.image_tag if not set."
  type        = map(string)
  default     = {}
}

# ──────────────────────────────────────────────────────────────────────────────
# Cloud Run — global defaults
# ──────────────────────────────────────────────────────────────────────────────

variable "allow_unauthenticated" {
  description = "Whether Cloud Run services allow unauthenticated (public) access"
  type        = bool
  default     = true
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances per service"
  type        = number
  default     = 10
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances per service (0 = scale to zero)"
  type        = number
  default     = 0
}

variable "timeout_seconds" {
  description = "Request timeout in seconds"
  type        = number
  default     = 300
}

# ──────────────────────────────────────────────────────────────────────────────
# Service-specific resource limits
# ──────────────────────────────────────────────────────────────────────────────

variable "service_resources" {
  description = "Per-service CPU/memory limits. Keys are service names."
  type = map(object({
    cpu    = optional(string, "1")
    memory = optional(string, "512Mi")
  }))
  default = {
    api = {
      cpu    = "1"
      memory = "512Mi"
    }
    frontend = {
      cpu    = "1"
      memory = "512Mi"
    }
    ai-code-converter = {
      cpu    = "2"
      memory = "4Gi"
    }
    code-analysis-engine = {
      cpu    = "1"
      memory = "1Gi"
    }
    decision-engine = {
      cpu    = "1"
      memory = "512Mi"
    }
    hardware-abstraction-layer = {
      cpu    = "1"
      memory = "512Mi"
    }
  }
}

# ──────────────────────────────────────────────────────────────────────────────
# Workload Identity Federation (for GitHub Actions)
# ──────────────────────────────────────────────────────────────────────────────

variable "github_org" {
  description = "GitHub owner/org (case-sensitive, must match GitHub exactly)"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "nexar"
}

variable "wif_pool_id" {
  description = "Workload Identity Pool ID"
  type        = string
  default     = "github-pool"
}

variable "wif_provider_id" {
  description = "Workload Identity Provider ID"
  type        = string
  default     = "github-provider"
}

variable "deploy_service_account_id" {
  description = "Service account ID used by GitHub Actions for deployments"
  type        = string
  default     = "github-deploy"
}

# ──────────────────────────────────────────────────────────────────────────────
# GCS — ML Models Bucket
# ──────────────────────────────────────────────────────────────────────────────

variable "models_bucket_name" {
  description = "Name of the GCS bucket for ML model artifacts"
  type        = string
}

variable "models_bucket_location" {
  description = "GCS bucket location (defaults to var.region)"
  type        = string
  default     = ""
}

variable "ai_code_converter_model_gcs_path" {
  description = "GCS path (relative to the models bucket) for the AI Code Converter model folder (e.g. ai-code-converter/codet5-quantum-best-version2)"
  type        = string
  default     = "ai-code-converter/version1"
}

variable "code_analysis_engine_model_gcs_path" {
  description = "GCS path (relative to the models bucket) for the Code Analysis Engine model folder (e.g. code-analysis-engine/trained)"
  type        = string
  default     = "code-analysis-engine/version1"
}

# ──────────────────────────────────────────────────────────────────────────────
# Google OAuth
# ──────────────────────────────────────────────────────────────────────────────

variable "google_oauth_client_id" {
  description = "Google OAuth 2.0 Client ID for user authentication"
  type        = string
}

variable "google_oauth_client_secret" {
  description = "Google OAuth 2.0 Client Secret for user authentication"
  type        = string
  sensitive   = true
}

# ──────────────────────────────────────────────────────────────────────────────
# Frontend
# ──────────────────────────────────────────────────────────────────────────────

variable "frontend_url" {
  description = "Deployed frontend Cloud Run URL (used by the API for OAuth redirects, email verification links, etc.)"
  type        = string
}

variable "frontend_api_url_override" {
  description = "Override the API_URL env var on the frontend. If empty, it is auto-wired to the deployed nexar-api Cloud Run URL."
  type        = string
  default     = ""
}
