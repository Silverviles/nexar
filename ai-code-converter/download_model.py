"""
Download model files from Google Cloud Storage before the app starts.

Usage:
    python download_model.py

Environment variables:
    GCS_MODEL_URI   — GCS path to the model directory (e.g. gs://nexar_models/ai-code-converter/codet5-quantum-best-version2)
    MODEL_PATH      — Local directory to download the model into (default: /app/models)

On Cloud Run, authentication happens automatically via the default service account.
Locally, set GOOGLE_APPLICATION_CREDENTIALS or run `gcloud auth application-default login`.
"""

import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def download_model_from_gcs(gcs_uri: str, local_dir: str) -> None:
    """
    Download all files under a GCS prefix into a local directory.

    Args:
        gcs_uri:   A gs:// URI, e.g. gs://bucket-name/path/to/model/
        local_dir: Local filesystem path to write files into.
    """
    from google.cloud import storage

    # Parse the gs:// URI
    if not gcs_uri.startswith("gs://"):
        raise ValueError(f"GCS_MODEL_URI must start with gs://, got: {gcs_uri}")

    # Strip trailing slash for consistent prefix handling
    gcs_uri = gcs_uri.rstrip("/")

    # Split into bucket name and prefix
    without_scheme = gcs_uri[len("gs://") :]
    parts = without_scheme.split("/", 1)
    bucket_name = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""

    logger.info(
        "Downloading model from gs://%s/%s → %s", bucket_name, prefix, local_dir
    )

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # List all blobs under the prefix
    blobs = list(bucket.list_blobs(prefix=prefix))

    if not blobs:
        raise RuntimeError(
            f"No files found at gs://{bucket_name}/{prefix}. "
            "Check that the GCS_MODEL_URI is correct and the bucket is accessible."
        )

    downloaded = 0
    for blob in blobs:
        # Skip "directory" markers
        if blob.name.endswith("/"):
            continue

        # Compute relative path from the prefix
        relative_path = blob.name[len(prefix) :].lstrip("/")
        if not relative_path:
            continue

        local_path = os.path.join(local_dir, relative_path)

        # Create parent directories
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        logger.info("  ↓ %s (%s bytes)", relative_path, blob.size)
        blob.download_to_filename(local_path)
        downloaded += 1

    logger.info("Downloaded %d file(s) to %s", downloaded, local_dir)


def main() -> None:
    gcs_uri = os.getenv("GCS_MODEL_URI", "")
    model_path = os.getenv("MODEL_PATH", "/app/models")

    if not gcs_uri:
        logger.info("GCS_MODEL_URI is not set — skipping model download.")
        return

    # If the model directory already has files (e.g. baked into the image), skip
    if os.path.isdir(model_path) and os.listdir(model_path):
        logger.info(
            "Model directory %s already has files — skipping download.", model_path
        )
        return

    os.makedirs(model_path, exist_ok=True)

    try:
        download_model_from_gcs(gcs_uri, model_path)
    except Exception:
        logger.exception("Failed to download model from GCS")
        sys.exit(1)

    logger.info("Model download complete.")


if __name__ == "__main__":
    main()
