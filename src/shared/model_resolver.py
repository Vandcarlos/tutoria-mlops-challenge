import os
import sys

from mlflow.tracking import MlflowClient


def resolve_model_uri(
    model_name: str | None = None,
    version: str | None = None,
    default_stage: str = "Production",
) -> str:
    """
    Resolve an MLflow model URI.

    Strategy:
    1. If `version` (or MLFLOW_MODEL_VERSION env) is provided, use that version:
       -> models:/<name>/<version>
    2. Otherwise, try to pick a version in `default_stage` (e.g., Production),
       filtering in Python (file-based registry does not support current_stage in filters).
    3. If no staged versions are found, fall back to the highest numeric version.
    """

    client = MlflowClient()

    # Resolve model name: argument > env > hardcoded default
    name = model_name or os.getenv("MLFLOW_MODEL_NAME", "sentiment-logreg-tfidf")

    # Resolve version: argument > env
    if version is None:
        version = os.getenv("MLFLOW_MODEL_VERSION")

    # 1) Explicit version wins
    if version:
        return f"models:/{name}/{version}"

    # 2) Fetch all versions for this model name
    all_versions = client.search_model_versions(f"name = '{name}'")
    if not all_versions:
        raise RuntimeError(f"No model versions found for name '{name}'")

    # 3) Try to find versions in the desired stage (e.g. Production)
    #    We cannot query by current_stage in the filter string when using file_store,
    #    so we filter in Python instead.
    stage_candidates = [
        mv for mv in all_versions if getattr(mv, "current_stage", None) == default_stage
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
