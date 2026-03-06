# ──────────────────────────────────────────────────────────────────────────────
# Artifact Registry — Docker Repository
# ──────────────────────────────────────────────────────────────────────────────

resource "google_artifact_registry_repository" "nexar" {
  location      = var.region
  repository_id = var.artifact_registry_repository
  description   = "Nexar service Docker images"
  format        = "DOCKER"

  depends_on = [google_project_service.apis["artifactregistry.googleapis.com"]]
}
