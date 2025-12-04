import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


BASE_PATH = Path(os.getenv("BASE_PATH", "./data/monitoring")).resolve()

MONITORING_BASE_PATH = BASE_PATH / "predictions"
MONITORING_OUTPUT_PATH = BASE_PATH / "reports"
MONITORING_REPORT_PATH = MONITORING_OUTPUT_PATH / "prediction_drift_report.html"
MONITORING_LOOKBACK_DAYS = int(os.getenv("MONITORING_LOOKBACK_DAYS", "7"))
ALLOW_RUNTIME_MODEL_DOWNLOAD: bool = _bool("ALLOW_RUNTIME_MODEL_DOWNLOAD", False)

REFERENCE_PREDICTIONS_PATH = BASE_PATH / "reference_predictions.parquet"

TEST_DATA_PATH = Path(
    os.getenv(
        "TEST_DATA_PATH",
        "./data/processed/test.parquet",
    )
).resolve()
TEST_FULL_TEXT_COLUMN = "full_text"
MODEL_PATH: Path = Path(os.getenv("MODEL_PATH", "./data/model")).resolve()

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
S3_DATA_KEY_TEST_DATA = f"{S3_DATA_KEY_PREFIX}/processed/test.parquet"
