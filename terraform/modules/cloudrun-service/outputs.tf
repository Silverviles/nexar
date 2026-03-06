# ──────────────────────────────────────────────────────────────────────────────
# Cloud Run Service Module — Outputs
# ──────────────────────────────────────────────────────────────────────────────

output "service_id" {
  description = "The fully qualified resource ID of the Cloud Run service"
  value       = google_cloud_run_v2_service.this.id
}

output "service_name" {
  description = "The name of the Cloud Run service"
  value       = google_cloud_run_v2_service.this.name
}

output "uri" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.this.uri
}

output "location" {
  description = "The region the service is deployed in"
  value       = google_cloud_run_v2_service.this.location
}

output "revision" {
  description = "The latest revision name of the Cloud Run service"
  value       = google_cloud_run_v2_service.this.latest_ready_revision
}
