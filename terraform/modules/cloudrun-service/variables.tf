# ──────────────────────────────────────────────────────────────────────────────
# Cloud Run Service Module — Input Variables
# ──────────────────────────────────────────────────────────────────────────────

variable "service_name" {
  description = "Name of the Cloud Run service (e.g. 'nexar-api')"
  type        = string
}

variable "location" {
  description = "GCP region to deploy the service in"
  type        = string
}

variable "image" {
  description = "Full container image URI including tag (e.g. 'us-central1-docker.pkg.dev/my-project/nexar/api:latest')"
  type        = string
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
}

variable "env_vars" {
  description = "Map of environment variables to set on the container"
  type        = map(string)
  default     = {}
}

variable "cpu" {
  description = "CPU limit for the container (e.g. '1', '2')"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory limit for the container (e.g. '512Mi', '4Gi')"
  type        = string
  default     = "512Mi"
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances (0 = scale to zero)"
  type        = number
  default     = 0
}

variable "timeout_seconds" {
  description = "Request timeout in seconds"
  type        = number
  default     = 300
}

variable "allow_unauthenticated" {
  description = "Whether to allow unauthenticated (public) access"
  type        = bool
  default     = true
}

variable "vpc_connector_id" {
  description = "VPC Access connector ID for private networking (e.g. Memorystore). Leave null to skip."
  type        = string
  default     = null
}

variable "vpc_egress" {
  description = "VPC egress setting when vpc_connector_id is set"
  type        = string
  default     = "PRIVATE_RANGES_ONLY"
}

variable "depends_on_apis" {
  description = "List of google_project_service resources to depend on (ensures APIs are enabled before deploying)"
  type        = list(any)
  default     = []
}
