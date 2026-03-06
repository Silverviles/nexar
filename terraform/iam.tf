# ──────────────────────────────────────────────────────────────────────────────
# Service Account — GitHub Actions Deployments
# ──────────────────────────────────────────────────────────────────────────────

resource "google_service_account" "github_deploy" {
  account_id   = var.deploy_service_account_id
  display_name = "GitHub Actions Deploy"
  description  = "Used by GitHub Actions to build, push, and deploy to Cloud Run"

  depends_on = [google_project_service.apis["iam.googleapis.com"]]
}

# ──────────────────────────────────────────────────────────────────────────────
# Project-Level IAM Roles for the Deploy Service Account
# ──────────────────────────────────────────────────────────────────────────────

locals {
  deploy_sa_roles = [
    "roles/run.admin",               # Deploy to Cloud Run
    "roles/artifactregistry.writer",  # Push Docker images
    "roles/storage.objectAdmin",      # Read/write GCS (ML models + Terraform state)
    "roles/iam.serviceAccountUser",   # Act as the Cloud Run runtime SA
  ]
}

resource "google_project_iam_member" "deploy_sa_roles" {
  for_each = toset(local.deploy_sa_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.github_deploy.email}"
}

# ──────────────────────────────────────────────────────────────────────────────
# Workload Identity Federation — Keyless GitHub ↔ GCP Auth
# ──────────────────────────────────────────────────────────────────────────────

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = var.wif_pool_id
  display_name              = "GitHub Actions Pool"
  description               = "Pool for GitHub Actions OIDC tokens"

  depends_on = [google_project_service.apis["iam.googleapis.com"]]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = var.wif_provider_id
  display_name                       = "GitHub Provider"

  # Map GitHub OIDC claims to Google attributes
  attribute_mapping = {
    "google.subject"             = "assertion.sub"
    "attribute.repository"       = "assertion.repository"
    "attribute.repository_owner" = "assertion.repository_owner"
  }

  # IMPORTANT: case-sensitive — must match exact GitHub owner/repo
  attribute_condition = "attribute.repository == '${var.github_org}/${var.github_repo}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# ──────────────────────────────────────────────────────────────────────────────
# WIF Binding — Allow GitHub Actions to Impersonate the Deploy SA
# ──────────────────────────────────────────────────────────────────────────────

resource "google_service_account_iam_member" "wif_binding" {
  service_account_id = google_service_account.github_deploy.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_org}/${var.github_repo}"
}
