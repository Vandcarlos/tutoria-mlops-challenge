import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MONITORING_BASE_PATH = Path(
    os.getenv("MONITORING_BASE_PATH", "./data/monitoring/predictions")
).resolve()
MONITORING_OUTPUT_PATH = Path(
    os.getenv("MONITORING_OUTPUT_PATH", "./data/monitoring/reports")
).resolve()
MONITORING_REPORT_PATH = MONITORING_OUTPUT_PATH / "prediction_drift_report.html"
MONITORING_LOOKBACK_DAYS = int(os.getenv("MONITORING_LOOKBACK_DAYS", "7"))

REFERENCE_PREDICTIONS_PATH = Path(
    os.getenv(
        "REFERENCE_PREDICTIONS_PATH",
        "./data/monitoring/reference_predictions.parquet",
    )
).resolve()

TEST_DATA_PATH = Path(
    os.getenv(
        "TEST_DATA_PATH",
        "./data/processed/test_processed.parquet",
    )
).resolve()
TEST_FULL_TEXT_COLUMN = "full_text"

MODEL_PATH: Path = Path(os.getenv("MODEL_PATH", "./data/model")).resolve()
