from datetime import UTC, datetime, timedelta
import json

import pandas as pd

from src.monitoring import log_loader


def test_load_prediction_logs_returns_empty_when_base_path_not_exists(
    monkeypatch, tmp_path
):
    """
    When MONITORING_BASE_PATH does not exist, should return an empty DataFrame.
    """
    base_path = tmp_path / "does_not_exist"

    # Patch the base path used inside the module
    monkeypatch.setattr(log_loader, "MONITORING_BASE_PATH", base_path, raising=True)

    df = log_loader.load_prediction_logs_local()
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_load_prediction_logs_filters_by_lookback_days(monkeypatch, tmp_path):
    """
    Should:
    - read JSON files under date=YYYY-MM-DD
    - parse timestamps
    - filter out events older than NOW - MONITORING_LOOKBACK_DAYS
    - return a DataFrame with the expected columns and correct types
    """

    base_path = tmp_path / "predictions"
    base_path.mkdir()

    # Patch base path and lookback window
    monkeypatch.setattr(log_loader, "MONITORING_BASE_PATH", base_path, raising=True)
    monkeypatch.setattr(log_loader, "MONITORING_LOOKBACK_DAYS", 7, raising=True)

    # Fix "current time"
    now = datetime(2025, 1, 10, 12, 0, 0, tzinfo=UTC)
    cutoff = now - timedelta(days=7)

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now

    monkeypatch.setattr(log_loader, "datetime", FixedDatetime, raising=True)

    # Create two files: one recent, one older than cutoff
    recent_ts = now - timedelta(days=1)  # should be included
    old_ts = now - timedelta(days=10)  # should be filtered out

    def make_event(ts, label, conf, latency_ms=10.0):
        return {
            "timestamp": ts.isoformat(),
            "request_id": "req",
            "model_version": "v1",
            "mlflow_run_id": "run-1",
            "input": {
                "title": "T",
                "text": "M",
                "full_text": "T M",
            },
            "output": {
                "predicted_label": label,
                "predicted_label_name": "POSITIVE" if label == 1 else "NEGATIVE",
                "confidence": conf,
            },
            "latency_ms": latency_ms,
        }

    # recent file
    recent_dir = base_path / f"date={recent_ts.date().isoformat()}"
    recent_dir.mkdir()
    (recent_dir / "prediction_recent.json").write_text(
        json.dumps(make_event(recent_ts, 1, 0.9)), encoding="utf-8"
    )

    # old file
    old_dir = base_path / f"date={old_ts.date().isoformat()}"
    old_dir.mkdir()
    (old_dir / "prediction_old.json").write_text(
        json.dumps(make_event(old_ts, 0, 0.1)), encoding="utf-8"
    )

    # Act
    df = log_loader.load_prediction_logs_local()

    # Only recent row should be present
    assert len(df) == 1
    row = df.iloc[0]

    assert row["title"] == "T"
    assert row["text"] == "M"
    assert row["full_text"] == "T M"
    assert row["predicted_label"] == 1
    assert row["predicted_label_name"] == "POSITIVE"
    assert row["confidence"] == 0.9
    assert row["latency_ms"] == 10.0

    # timestamp column must be datetime64[ns]
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    assert row["timestamp"].to_pydatetime().replace(tzinfo=UTC) == recent_ts
