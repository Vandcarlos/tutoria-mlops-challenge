from datetime import UTC, datetime
import json
import uuid

import src.api.config as cfg


class LocalPredictionLogger:
    """Log prediction events to local filesystem as JSON files."""

    def __init__(self) -> None:
        self.base_path = cfg.MONITORING_BASE_PATH
        self.base_path.mkdir(parents=True, exist_ok=True)

    def log_prediction(
        self,
        title: str,
        message: str,
        full_text: str,
        predicted_label: int,
        predicted_label_name: str,
        confidence: float,
        latency_ms: float,
    ) -> None:
        """Build a prediction event and persist it as a JSON file."""
        now = datetime.now(UTC)
        request_id = str(uuid.uuid4())
        date_str = now.strftime("%Y-%m-%d")

        event = {
            "timestamp": now.isoformat(),
            "request_id": request_id,
            "model_version": cfg.MLFLOW_MODEL_VERSION,
            "mlflow_run_id": cfg.MLFLOW_RUN_ID,
            "input": {
                "title": title,
                "text": message,
                "full_text": full_text,
            },
            "output": {
                "predicted_label": int(predicted_label),
                "predicted_label_name": predicted_label_name,
                "confidence": float(confidence),
            },
            "latency_ms": float(latency_ms),
        }

        # monitoring/predictions/date=YYYY-MM-DD/prediction_<uuid>.json
        dir_path = self.base_path / f"date={date_str}"
        dir_path.mkdir(parents=True, exist_ok=True)

        print(f"[monitoring_logger] Logging prediction event to {dir_path}")

        file_path = dir_path / f"prediction_{request_id}.json"
        file_path.write_text(json.dumps(event), encoding="utf-8")
