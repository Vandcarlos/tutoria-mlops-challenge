from datetime import UTC, datetime, timedelta
import json

import pandas as pd

from src.monitoring.config import (
    MONITORING_LOOKBACK_DAYS,
    MONITORING_PREDICTIONS_PATH,
    S3_DATA_BUCKET,
    S3_DATA_KEY_MONITORING_PREDICTIONS,
    USE_S3_DATA,
)
from src.shared.s3_utils import download_folder_from_s3


def load_prediction_logs_local() -> pd.DataFrame:
    """Load prediction logs stored locally into a DataFrame.

    It expects files under:
        monitoring/predictions/date=YYYY-MM-DD/prediction_<uuid>.json
    """

    if USE_S3_DATA:
        download_folder_from_s3(
            bucket=S3_DATA_BUCKET,
            folder_key=S3_DATA_KEY_MONITORING_PREDICTIONS,
            folder_path=MONITORING_PREDICTIONS_PATH,
        )

    if not MONITORING_PREDICTIONS_PATH.exists():
        return pd.DataFrame()

    pattern_files = MONITORING_PREDICTIONS_PATH.glob("date=*/prediction_*.json")

    if not pattern_files:
        pattern_files = list(MONITORING_PREDICTIONS_PATH.glob("prediction_*.json"))

    events: list[dict] = []
    cutoff = datetime.now(UTC) - timedelta(days=MONITORING_LOOKBACK_DAYS)

    for file_path in pattern_files:
        raw = file_path.read_text(encoding="utf-8")
        data = json.loads(raw)

        ts = datetime.fromisoformat(data["timestamp"])
        if ts < cutoff:
            continue

        events.append(
            {
                "timestamp": ts,
                "title": data["input"]["title"],
                "text": data["input"]["text"],
                "full_text": data["input"]["full_text"],
                "predicted_label": int(data["output"]["predicted_label"]),
                "predicted_label_name": data["output"]["predicted_label_name"],
                "confidence": float(data["output"]["confidence"]),
                "latency_ms": float(data["latency_ms"]),
            }
        )

    if not events:
        return pd.DataFrame()

    df = pd.DataFrame(events)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
