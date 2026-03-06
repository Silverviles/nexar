# ──────────────────────────────────────────────────────────────────────────────
# Terraform Configuration
# ──────────────────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ──────────────────────────────────────────────────────────────────────────────
# Data Sources
# ──────────────────────────────────────────────────────────────────────────────

data "google_project" "current" {
  project_id = var.project_id
}

locals {
  project_number         = data.google_project.current.number
  models_bucket_location = var.models_bucket_location != "" ? var.models_bucket_location : var.region
}

# ──────────────────────────────────────────────────────────────────────────────
# Enable Required GCP APIs
# ──────────────────────────────────────────────────────────────────────────────

resource "google_project_service" "apis" {
  for_each = toset([
    "cloudresourcemanager.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "storage.googleapis.com",
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
