import sys

from mlflow.tracking import MlflowClient

from src.model import config as cfg


def resolve_model_uri(model_version: str | None = None) -> str:
    """
    Resolve a MLflow model URI for the configured model name.

    Resolution strategy:
    1. If `model_version` is provided and non-empty, use that exact version.
    2. Else, try to use the `Production` stage if available.
    3. Else, fall back to the highest numeric version in the registry.

    Raises:
        RuntimeError: If no model versions are found in the registry.
    """
    client = MlflowClient()

    # 1) Explicit version provided
    if model_version and model_version.strip():
        version_str = model_version.strip()
        return f"models:/{cfg.MODEL_NAME}/{version_str}"

    # 2) Try Production stage
    latest_versions = client.get_latest_versions(
        name=cfg.MODEL_NAME,
        stages=["Production"],
    )

    if latest_versions:
        v = latest_versions[0]
        print(
            f"[MODEL_RESOLVER] Auto-selected Production version: v{v.version}",
            file=sys.stderr,
        )
        return f"models:/{cfg.MODEL_NAME}/Production"

    # 3) Fallback: highest numeric version
    versions = client.search_model_versions(f"name = '{cfg.MODEL_NAME}'")
    if not versions:
        raise RuntimeError(f"No model versions found for name '{cfg.MODEL_NAME}'")

    latest = max(versions, key=lambda v: int(v.version))
    print(
        f"[MODEL_RESOLVER] Auto-selected latest version: v{latest.version}",
        file=sys.stderr,
    )

    return f"models:/{latest.name}/{latest.version}"
