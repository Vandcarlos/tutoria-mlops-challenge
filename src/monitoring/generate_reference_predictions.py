from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from src.monitoring.config import (
    ALLOW_RUNTIME_MODEL_DOWNLOAD,
    DATASET_FULL_TEXT_COLUMN,
    DATASET_MESSAGE_COLUMN,
    DATASET_POLARITY_COLUMN,
    DATASET_PROCESSED_TEST_PATH,
    DATASET_RAW_TEST_PARQUET,
    DATASET_TITLE_COLUMN,
    MODEL_PATH,
    REFERENCE_PREDICTIONS_PATH,
    S3_DATA_BUCKET,
    S3_DATA_KEY_MONITORING_REFERENCE,
    S3_DATA_KEY_PROCESSED_TEST,
    S3_DATA_KEY_RAW_TEST,
    USE_S3_DATA,
)
from src.shared.model_resolver import load_model
from src.shared.s3_utils import download_file_from_s3, upload_file_to_s3


def _load_processed_test_dataset() -> pd.DataFrame:
    try:
        print("[REFERENCE] load processed test dataset")
        if USE_S3_DATA:
            download_file_from_s3(
                bucket=S3_DATA_BUCKET,
                key=S3_DATA_KEY_PROCESSED_TEST,
                file_path=DATASET_PROCESSED_TEST_PATH,
            )

        df_test_processed = pd.read_parquet(DATASET_PROCESSED_TEST_PATH)
        df_test_processed.columns = [
            DATASET_POLARITY_COLUMN,
            DATASET_FULL_TEXT_COLUMN,
        ]
        print("[REFERENCE] loaded processed test dataset")

    except Exception:
        print("[REFERENCE] processed dataset not exists")
        df_test_processed = _load_and_preprocess_raw_test_dataset()

    return df_test_processed


def _load_and_preprocess_raw_test_dataset() -> pd.DataFrame:
    print("[REFERENCE] load raw test dataset")
    if USE_S3_DATA:
        download_file_from_s3(
            bucket=S3_DATA_BUCKET,
            key=S3_DATA_KEY_RAW_TEST,
            file_path=DATASET_RAW_TEST_PARQUET,
        )

    df = pd.read_parquet(DATASET_RAW_TEST_PARQUET)

    df.columns = [
        DATASET_POLARITY_COLUMN,
        DATASET_TITLE_COLUMN,
        DATASET_MESSAGE_COLUMN,
    ]

    df[DATASET_FULL_TEXT_COLUMN] = df.apply(
        lambda row: f"{row[DATASET_TITLE_COLUMN]} {row[DATASET_MESSAGE_COLUMN]}".strip().lower(),
        axis=1,
    )

    df = df.drop(columns=[DATASET_TITLE_COLUMN, DATASET_MESSAGE_COLUMN])

    print("[REFERENCE] loaded raw test dataset")

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
    df_val = _load_processed_test_dataset()
    texts = df_val[DATASET_FULL_TEXT_COLUMN]

    print("[REFERENCE] Loading model")
    model = load_model(
        model_local_path=MODEL_PATH,
        allow_runtime_model_download=ALLOW_RUNTIME_MODEL_DOWNLOAD,
    )
    print("[REFERENCE] Loaded model")

    print("[REFERENCE] Generating predictions for reference dataset")
    labels, confidences = infer_predictions_with_confidence(model, texts)
    print("[REFERENCE] Generated predictions for reference dataset")

    reference_df = pd.DataFrame(
        {
            "predicted_label": labels,
            "confidence": confidences,
        }
    )

    REFERENCE_PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)

    reference_df.to_parquet(REFERENCE_PREDICTIONS_PATH)

    if USE_S3_DATA:
        upload_file_to_s3(
            file_path=REFERENCE_PREDICTIONS_PATH,
            bucket=S3_DATA_BUCKET,
            key=S3_DATA_KEY_MONITORING_REFERENCE,
        )

    print(f"[reference] Saved reference predictions to: {REFERENCE_PREDICTIONS_PATH}")
    return REFERENCE_PREDICTIONS_PATH
