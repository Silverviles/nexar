# ──────────────────────────────────────────────────────────────────────────────
# Cloud Run Service Module — Main Resource + IAM
# ──────────────────────────────────────────────────────────────────────────────

resource "google_cloud_run_v2_service" "this" {
  name     = var.service_name
  location = var.location

  template {
    max_instance_request_concurrency = 1

    scaling {
      max_instance_count = var.max_instances
      min_instance_count = var.min_instances
    }

    timeout = "${var.timeout_seconds}s"

    # Attach VPC connector if provided (e.g. for Memorystore Redis)
    dynamic "vpc_access" {
      for_each = var.vpc_connector_id != null ? [1] : []
      content {
        connector = var.vpc_connector_id
        egress    = var.vpc_egress
      }
    }

    containers {
      image = var.image

      ports {
        container_port = var.container_port
      }

      resources {
        cpu_idle = true
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }

      # Dynamically create env blocks from the env_vars map
      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      # The GitHub Actions workflow updates the image on every deploy.
      # Ignore it here so Terraform doesn't try to revert to the old tag.
      template[0].containers[0].image,
    ]
  }
}

# ──────────────────────────────────────────────────────────────────────────────
# IAM — Allow Unauthenticated (Public) Access
# ──────────────────────────────────────────────────────────────────────────────

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count = var.allow_unauthenticated ? 1 : 0

  name     = google_cloud_run_v2_service.this.name
  location = google_cloud_run_v2_service.this.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
