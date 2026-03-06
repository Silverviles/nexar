# ──────────────────────────────────────────────────────────────────────────────
# Cloud Run Service URLs
# ──────────────────────────────────────────────────────────────────────────────

output "api_url" {
  description = "URL of the deployed nexar-api Cloud Run service"
  value       = module.api.uri
}

output "frontend_url" {
  description = "URL of the deployed nexar-frontend Cloud Run service"
  value       = module.frontend.uri
}

output "ai_code_converter_url" {
  description = "URL of the deployed nexar-ai-code-converter Cloud Run service"
  value       = module.ai_code_converter.uri
}

output "code_analysis_engine_url" {
  description = "URL of the deployed nexar-code-analysis-engine Cloud Run service"
  value       = module.code_analysis_engine.uri
}

output "decision_engine_url" {
  description = "URL of the deployed nexar-decision-engine Cloud Run service"
  value       = module.decision_engine.uri
}

output "hardware_abstraction_layer_url" {
  description = "URL of the deployed nexar-hardware-abstraction-layer Cloud Run service"
  value       = module.hardware_abstraction_layer.uri
}

output "all_service_urls" {
  description = "Map of all service names to their deployed Cloud Run URLs"
  value = {
    api                        = module.api.uri
    frontend                   = module.frontend.uri
    ai-code-converter          = module.ai_code_converter.uri
    code-analysis-engine       = module.code_analysis_engine.uri
    decision-engine            = module.decision_engine.uri
    hardware-abstraction-layer = module.hardware_abstraction_layer.uri
  }
}

# ──────────────────────────────────────────────────────────────────────────────
# Workload Identity Federation — Values for GitHub Secrets
# ──────────────────────────────────────────────────────────────────────────────

output "wif_provider" {
  description = "Full resource name of the WIF provider — set this as the WIF_PROVIDER GitHub Secret"
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "wif_service_account" {
  description = "Email of the deploy service account — set this as the WIF_SERVICE_ACCOUNT GitHub Secret"
  value       = google_service_account.github_deploy.email
}

# ──────────────────────────────────────────────────────────────────────────────
# Artifact Registry
# ──────────────────────────────────────────────────────────────────────────────

output "artifact_registry_url" {
  description = "Base URL for pushing Docker images to Artifact Registry"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.nexar.repository_id}"
}

# ──────────────────────────────────────────────────────────────────────────────
# GCS Models Bucket
# ──────────────────────────────────────────────────────────────────────────────

output "models_bucket" {
  description = "Name of the GCS bucket for ML model artifacts — set this as the GCS_MODELS_BUCKET GitHub Secret (prefix with gs://)"
  value       = google_storage_bucket.models.name
}

output "models_bucket_uri" {
  description = "gs:// URI of the models bucket"
  value       = "gs://${google_storage_bucket.models.name}"
}

# ──────────────────────────────────────────────────────────────────────────────
# GitHub Secrets Summary
#
# After running `terraform apply`, set these GitHub repository secrets:
#
#   GCP_PROJECT_ID       = var.project_id
#   GCP_REGION           = var.region
#   GCS_MODELS_BUCKET    = gs://<models_bucket>
#   WIF_PROVIDER         = <wif_provider>
#   WIF_SERVICE_ACCOUNT  = <wif_service_account>
# ──────────────────────────────────────────────────────────────────────────────

output "github_secrets_summary" {
  description = "Copy these values into your GitHub repository secrets"
  value = {
    GCP_PROJECT_ID      = var.project_id
    GCP_REGION          = var.region
    GCS_MODELS_BUCKET   = "gs://${google_storage_bucket.models.name}"
    WIF_PROVIDER        = google_iam_workload_identity_pool_provider.github.name
    WIF_SERVICE_ACCOUNT = google_service_account.github_deploy.email
  }
}
