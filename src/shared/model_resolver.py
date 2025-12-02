from pathlib import Path
import sys

from mlflow.tracking import MlflowClient
from sklearn.pipeline import Pipeline

import mlflow

MODEL_NAME = "sentiment-logreg-tfidf"
DEFAIULT_STAGE = "Production"


def resolve_model_uri(version: str) -> str:
    """
    Resolve an MLflow model URI.

    Strategy:
    1. If `version` (or MLFLOW_MODEL_VERSION env) is provided, use that version:
       -> models:/<name>/<version>
    2. Otherwise, try to pick a version in `default_stage` (e.g., Production),
       filtering in Python (file-based registry does not support current_stage in filters).
    3. If no staged versions are found, fall back to the highest numeric version.
    """

    # Resolve model name: argument > env > hardcoded default

    # 1) Explicit version wins
    if version:
        return f"models:/{MODEL_NAME}/{version}"

    client = MlflowClient()

    # 2) Fetch all versions for this model name
    all_versions = client.search_model_versions(f"name = '{MODEL_NAME}'")
    if not all_versions:
        raise RuntimeError(f"No model versions found for name '{MODEL_NAME}'")

    # 3) Try to find versions in the desired stage (e.g. Production)
    #    We cannot query by current_stage in the filter string when using file_store,
    #    so we filter in Python instead.
    stage_candidates = [
        mv
        for mv in all_versions
        if getattr(mv, "current_stage", None) == DEFAIULT_STAGE
    ]

    if stage_candidates:
        chosen = max(stage_candidates, key=lambda v: int(v.version))
        return f"models:/{chosen.name}/{chosen.version}"

    # 4) Fallback: highest numeric version
    latest = max(all_versions, key=lambda v: int(v.version))
    print(
        f"[MODEL_RESOLVER] Auto-selected latest version: v{latest.version}",
        file=sys.stderr,
    )
    return f"models:/{latest.name}/{latest.version}"


def _load_model_from_local_path(model_local_path: Path) -> Pipeline:
    print(f"[model_loader] Loading local model from: {model_local_path}")
    return mlflow.sklearn.load_model(str(model_local_path))


def load_model(
    model_local_path: Path,
    version: str | None = None,
    allow_runtime_model_download: bool = False,
) -> Pipeline:
    if model_local_path.exists() and any(model_local_path.iterdir()):
        return _load_model_from_local_path(model_local_path=model_local_path)

    if not allow_runtime_model_download:
        raise RuntimeError(
            f"Model directory {model_local_path} is empty and "
            "allow_runtime_model_download=false. Cannot proceed."
        )

    model_uri = resolve_model_uri(version=version)
    print(f"[model_loader] Resolved model_uri={model_uri}, downloading...")

    mlflow.artifacts.download_artifacts(
        artifact_uri=model_uri,
        dst_path=str(model_local_path),
    )

    return _load_model_from_local_path(model_local_path=model_local_path)
