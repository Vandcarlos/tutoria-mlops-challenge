import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(), override=False)


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


ENVIRONMENT = os.getenv("ENVIRONMENT", "local")  # local | prod

# MLflow tracking
MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
MLFLOW_MODEL_VERSION: str | None = os.getenv("MLFLOW_MODEL_VERSION")
MLFLOW_RUN_ID: str | None = os.getenv("MLFLOW_RUN_ID")

MODEL_PATH: Path = Path(os.getenv("MODEL_PATH", "./data/model")).resolve()

# Monitoring
MONITORING_BASE_PATH = Path(
    os.getenv("MONITORING_BASE_PATH", "./data/monitoring/predictions")
).resolve()

ALLOW_RUNTIME_MODEL_DOWNLOAD: bool = _bool(
    "ALLOW_RUNTIME_MODEL_DOWNLOAD",
    default=(ENVIRONMENT == "local"),
)

# Optional S3 data storage configuration

S3_DATA_BUCKET: str | None = os.getenv("S3_DATA_BUCKET")
USE_S3_DATA: bool = S3_DATA_BUCKET is not None

S3_DATA_KEY_PREFIX: str = os.getenv("S3_DATA_PREFIX", "amazon-reviews")
S3_DATA_KEY_MONITORING = f"{S3_DATA_KEY_PREFIX}/monitoring/predictions"
