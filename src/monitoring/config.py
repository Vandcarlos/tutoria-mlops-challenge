import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


DATASET_LOCAL_PATH = Path(os.getenv("DATASET_LOCAL_PATH", "./data"))

BASE_MONITORING_PATH = DATASET_LOCAL_PATH / "monitoring"
MONITORING_PREDICTIONS_PATH = BASE_MONITORING_PATH / "predictions"
MONITORING_REPORTS_FOLDER_PATH = BASE_MONITORING_PATH / "reports"
MONITORING_REPORT_PATH = MONITORING_REPORTS_FOLDER_PATH / "prediction_drift_report.html"
MONITORING_LOOKBACK_DAYS = int(os.getenv("MONITORING_LOOKBACK_DAYS", "7"))
ALLOW_RUNTIME_MODEL_DOWNLOAD: bool = _bool("ALLOW_RUNTIME_MODEL_DOWNLOAD", False)

REFERENCE_PREDICTIONS_PATH = BASE_MONITORING_PATH / "reference_predictions.parquet"

DATASET_RAW_TEST_PARQUET = DATASET_LOCAL_PATH / "/raw/test.parquet"
DATASET_PROCESSED_TEST_PATH = DATASET_LOCAL_PATH / "/processed/test.parquet"

DATASET_POLARITY_COLUMN = "polarity"
DATASET_TITLE_COLUMN = "title"
DATASET_MESSAGE_COLUMN = "message"
DATASET_FULL_TEXT_COLUMN = "full_text"

MODEL_PATH = DATASET_LOCAL_PATH / "model"

# Optional S3 data storage configuration
S3_DATA_BUCKET: str | None = os.getenv("S3_DATA_BUCKET")
USE_S3_DATA: bool = S3_DATA_BUCKET is not None

S3_DATA_KEY_PREFIX: str = os.getenv("S3_DATA_PREFIX", "amazon-reviews")
S3_DATA_KEY_MONITORING = f"{S3_DATA_KEY_PREFIX}/monitoring"
S3_DATA_KEY_MONITORING_PREDICTIONS = f"{S3_DATA_KEY_MONITORING}/predictions"
S3_DATA_KEY_MONITORING_REPORTS = f"{S3_DATA_KEY_MONITORING}/reports"
S3_DATA_KEY_MONITORING_REPORTS_ITEM = (
    f"{S3_DATA_KEY_MONITORING_REPORTS}/prediction_drift_report.html"
)
S3_DATA_KEY_MONITORING_REFERENCE = (
    f"{S3_DATA_KEY_MONITORING}/reference_predictions.parquet"
)
S3_DATA_KEY_RAW_TEST = f"{S3_DATA_KEY_PREFIX}/raw/test.parquet"
S3_DATA_KEY_PROCESSED_TEST = f"{S3_DATA_KEY_PREFIX}/processed/test.parquet"
