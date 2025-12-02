from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from src.monitoring.config import (
    ALLOW_RUNTIME_MODEL_DOWNLOAD,
    MODEL_PATH,
    REFERENCE_PREDICTIONS_PATH,
    TEST_DATA_PATH,
    TEST_FULL_TEXT_COLUMN,
)
from src.shared.model_resolver import load_model


def load_validation_dataset() -> pd.DataFrame:
    """Load the validation dataset from parquet or CSV."""
    print(f"[reference] Loading validation dataset from: {TEST_DATA_PATH}")

    if not TEST_DATA_PATH.exists():
        raise FileNotFoundError(f"Validation dataset not found: {TEST_DATA_PATH}")

    df = pd.read_parquet(TEST_DATA_PATH)

    return df


def infer_predictions_with_confidence(
    model: Pipeline,
    texts: Iterable[str],
) -> tuple[np.ndarray, np.ndarray]:
    """Infer labels and confidence scores using the given model.

    Supports:
      - custom method `predict_with_confidence(texts)`
      - sklearn-like models with `predict_proba` and `predict`
    """
    texts_list = list(texts)

    labels = model.predict(texts_list)

    probas = model.predict_proba(texts_list)
    confidences = np.max(probas, axis=1)

    return labels, confidences


def generate_reference_predictions() -> Path:
    """Generate reference_predictions.parquet from a validation dataset."""
    df_val = load_validation_dataset()
    texts = df_val[TEST_FULL_TEXT_COLUMN]

    print("[reference] Loading model...")
    model = load_model(
        model_local_path=MODEL_PATH,
        allow_runtime_model_download=ALLOW_RUNTIME_MODEL_DOWNLOAD,
    )

    print("[reference] Generating predictions for reference dataset...")
    labels, confidences = infer_predictions_with_confidence(model, texts)

    reference_df = pd.DataFrame(
        {
            "predicted_label": labels,
            "confidence": confidences,
        }
    )

    REFERENCE_PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)

    reference_df.to_parquet(REFERENCE_PREDICTIONS_PATH)

    print(f"[reference] Saved reference predictions to: {REFERENCE_PREDICTIONS_PATH}")
    return REFERENCE_PREDICTIONS_PATH
