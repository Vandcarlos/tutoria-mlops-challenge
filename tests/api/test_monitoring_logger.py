from datetime import UTC, datetime
import json
import uuid

import src.api.monitoring_logger as monitoring_logger


def test_local_prediction_logger_creates_base_dir(tmp_path, monkeypatch):
    """
    LocalPredictionLogger.__init__ must create MONITORING_BASE_PATH if it does not exist.
    """
    base_path = tmp_path / "monitoring"

    # Patch config path
    monkeypatch.setattr(
        monitoring_logger.cfg,
        "MONITORING_BASE_PATH",
        base_path,
        raising=True,
    )

    logger = monitoring_logger.LocalPredictionLogger()

    assert logger.base_path == base_path
    assert logger.base_path.exists()
    assert logger.base_path.is_dir()


def test_log_prediction_writes_json_event(tmp_path, monkeypatch):
    """
    log_prediction must:
    - create a date=YYYY-MM-DD subdirectory under MONITORING_BASE_PATH
    - write a JSON file with the correct structure and values
    """

    base_path = tmp_path / "monitoring"
    monkeypatch.setattr(
        monitoring_logger.cfg,
        "MONITORING_BASE_PATH",
        base_path,
        raising=True,
    )
    monkeypatch.setattr(
        monitoring_logger.cfg,
        "MLFLOW_MODEL_VERSION",
        "v42",
        raising=True,
    )
    monkeypatch.setattr(
        monitoring_logger.cfg,
        "MLFLOW_RUN_ID",
        "run-123",
        raising=True,
    )

    # Fix datetime.now(UTC)
    fixed_dt = datetime(2025, 1, 2, 3, 4, 5, tzinfo=UTC)

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            # tz is expected to be UTC in this use-case
            return fixed_dt

    monkeypatch.setattr(
        monitoring_logger,
        "datetime",
        FixedDatetime,
        raising=True,
    )

    # Fix UUID
    fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")

    monkeypatch.setattr(
        monitoring_logger.uuid,
        "uuid4",
        lambda: fixed_uuid,
        raising=True,
    )

    logger = monitoring_logger.LocalPredictionLogger()

    # Act
    logger.log_prediction(
        title="T",
        message="M",
        full_text="T M",
        predicted_label=1,
        predicted_label_name="POSITIVE",
        confidence=0.9,
        latency_ms=12.34,
    )

    # Assert directory structure: base/date=YYYY-MM-DD/...
    date_dir = base_path / "date=2025-01-02"
    assert date_dir.exists()
    assert date_dir.is_dir()

    files = list(date_dir.iterdir())
    assert len(files) == 1
    file_path = files[0]

    # Assert file name pattern
    assert file_path.name == f"prediction_{fixed_uuid}.json"

    # Load JSON and validate content
    content = json.loads(file_path.read_text(encoding="utf-8"))

    assert content["timestamp"] == fixed_dt.isoformat()
    assert content["request_id"] == str(fixed_uuid)
    assert content["model_version"] == "v42"
    assert content["mlflow_run_id"] == "run-123"

    assert content["input"] == {
        "title": "T",
        "text": "M",
        "full_text": "T M",
    }

    assert content["output"]["predicted_label"] == 1
    assert content["output"]["predicted_label_name"] == "POSITIVE"
    assert content["output"]["confidence"] == 0.9

    assert isinstance(content["latency_ms"], float)
    assert content["latency_ms"] == 12.34
