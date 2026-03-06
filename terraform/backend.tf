# ──────────────────────────────────────────────────────────────────────────────
# Remote Backend — GCS Bucket for Terraform State
#
# Stores the Terraform state file in a GCS bucket so that:
#   1. GitHub Actions CI can read/write state (no local state in ephemeral runners)
#   2. Multiple team members can collaborate without state conflicts
#   3. State locking prevents concurrent modifications
#
# Prerequisites:
#   Create the bucket ONCE before running `terraform init`:
#
#     gcloud storage buckets create gs://YOUR_PROJECT_ID-terraform-state \
#       --location=us-central1 \
#       --uniform-bucket-level-access \
#       --project=YOUR_PROJECT_ID
#
#     gcloud storage buckets update gs://YOUR_PROJECT_ID-terraform-state \
#       --versioning \
#       --project=YOUR_PROJECT_ID
#
#   The deploy service account (github-deploy) needs
#   roles/storage.objectAdmin on this bucket:
#
#     gcloud storage buckets add-iam-policy-binding \
#       gs://YOUR_PROJECT_ID-terraform-state \
#       --member="serviceAccount:github-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
#       --role="roles/storage.objectAdmin"
#
# IMPORTANT:
#   The "bucket" value below CANNOT use variables — it must be a literal string.
#   Replace "YOUR_PROJECT_ID-terraform-state" with your actual bucket name.
#
#   Alternatively, pass the bucket at init time (recommended for CI):
#     terraform init -backend-config="bucket=my-actual-bucket-name"
#
# ──────────────────────────────────────────────────────────────────────────────

terraform {
  backend "gcs" {
    # This placeholder is overridden at init time via:
    #   terraform init -backend-config="bucket=<actual-bucket>"
    # Set the TF_STATE_BUCKET GitHub secret and the CI workflow will handle it.
    bucket = ""
    prefix = "nexar/terraform/state"
  }
}
