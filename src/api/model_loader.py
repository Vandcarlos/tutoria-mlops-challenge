import mlflow.pyfunc

import mlflow
from src.api.config import (
    ALLOW_RUNTIME_MODEL_DOWNLOAD,
    MLFLOW_MODEL_NAME,
    MLFLOW_MODEL_VERSION,
    MLFLOW_TRACKING_URI,
    MODEL_DIR,
)
from src.shared.model_resolver import resolve_model_uri


def _load_model_from_dir() -> mlflow.pyfunc.PyFuncModel:
    print(f"[model_loader] Loading local model from: {MODEL_DIR}")
    return mlflow.pyfunc.load_model(str(MODEL_DIR))


def load_model() -> mlflow.pyfunc.PyFuncModel:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    if MODEL_DIR.exists() and any(MODEL_DIR.iterdir()):
        return _load_model_from_dir()

    if not ALLOW_RUNTIME_MODEL_DOWNLOAD:
        raise RuntimeError(
            f"Model directory {MODEL_DIR} is empty and "
            "ALLOW_RUNTIME_MODEL_DOWNLOAD=false. Cannot proceed."
        )

    model_uri = resolve_model_uri(
        model_name=MLFLOW_MODEL_NAME,
        version=MLFLOW_MODEL_VERSION,
    )
    print(f"[model_loader] Resolved model_uri={model_uri}, downloading...")

    mlflow.artifacts.download_artifacts(
        artifact_uri=model_uri,
        dst_path=str(MODEL_DIR),
    )

    return _load_model_from_dir()
