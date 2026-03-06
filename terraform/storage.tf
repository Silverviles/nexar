# ──────────────────────────────────────────────────────────────────────────────
# GCS Bucket — ML Model Artifacts
#
# Stores model weights downloaded during CI builds:
#   gs://<bucket>/ai-code-converter/models/*       (CodeT5 weights)
#   gs://<bucket>/code-analysis-engine/models/trained/*  (sklearn .pkl files)
# ──────────────────────────────────────────────────────────────────────────────

resource "google_storage_bucket" "models" {
  name                        = var.models_bucket_name
  location                    = local.models_bucket_location
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  depends_on = [google_project_service.apis["storage.googleapis.com"]]
}
