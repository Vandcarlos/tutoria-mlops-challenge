import argparse

import pandas as pd

import mlflow
from src.model.config import (
    DATASET_FULL_TEXT_COLUMN,
    DATASET_MESSAGE_COLUMN,
    DATASET_POLARITY_COLUMN,
    DATASET_PROCESSED_PATH,
    DATASET_PROCESSED_TEST_PATH,
    DATASET_RAW_TEST_PARQUET,
    DATASET_TITLE_COLUMN,
    S3_DATA_BUCKET,
    S3_DATA_KEY_PROCESSED_TEST,
    S3_DATA_KEY_RAW_TEST,
    USE_S3_DATA,
)
from src.model.utilities.metrics_helper import validate
from src.model.utilities.preprocess_core import preprocess_df
from src.shared.model_resolver import resolve_model_uri
from src.shared.s3_utils import download_file_from_s3, upload_file_to_s3


def _load_processed_test_dataset() -> pd.DataFrame:
    try:
        print("[EVAL] load processed test dataset")
        if USE_S3_DATA:
            download_file_from_s3(
                bucket=S3_DATA_BUCKET,
                key=S3_DATA_KEY_PROCESSED_TEST,
                file_path=DATASET_PROCESSED_TEST_PATH,
            )

        df_test_processed = pd.read_parquet(DATASET_PROCESSED_TEST_PATH)
        print("[EVAL] loaded processed test dataset")

    except Exception:
        print("[EVAL] processed dataset not exists")
        df_test_raw = _load_raw_test_dataset()

        print("[EVAL] processeing raw dataset")
        df_test_processed = preprocess_df(df_test_raw)
        print("[EVAL] processed raw dataset")

    df_test_processed.columns = [
        DATASET_POLARITY_COLUMN,
        DATASET_FULL_TEXT_COLUMN,
    ]

    return df_test_processed


def _load_raw_test_dataset() -> pd.DataFrame:
    print("[EVAL] load raw test dataset")
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

    print("[EVAL] loaded raw test dataset")

    return df


def _save_processed_test_dataset(df_test_processed: pd.DataFrame):
    """
    Save processed test dataset to be reused by monitoring.

    It writes the file to:
        ./data/processed/test_processed.parquet
    (or to the path defined by DATASET_PROCESSED_PATH)
    """
    DATASET_PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

    df_test_processed.to_parquet(DATASET_PROCESSED_TEST_PATH)

    print(f"[EVAL] Saved processed test dataset to: {DATASET_PROCESSED_TEST_PATH}")

    if USE_S3_DATA:
        upload_file_to_s3(
            file_path=DATASET_PROCESSED_TEST_PATH,
            bucket=S3_DATA_BUCKET,
            key=S3_DATA_KEY_PROCESSED_TEST,
        )


def evaluate(model_version: str | None = None) -> None:
    """
    Load model (pipeline) from MLflow and evaluate with test_processed.parquet.
    """
    df_test_processed = _load_processed_test_dataset()
    _save_processed_test_dataset(df_test_processed)

    model_uri = resolve_model_uri(model_version)

    print(f"[EVAL] Loading model: {model_uri}")
    model = mlflow.pyfunc.load_model(model_uri)
    print(f"[EVAL] Load model: {model_uri}")

    print(f"[EVAL] Preditings test dataset: {model_uri}")
    y_true_pred = model.predict(df_test_processed[DATASET_FULL_TEXT_COLUMN])
    print(f"[EVAL] Predicted test dataset: {model_uri}")

    y_true_test = df_test_processed[DATASET_POLARITY_COLUMN].to_numpy()

    with mlflow.start_run(run_name="evaluate", nested=True):
        mlflow.log_param("model_uri", model_uri)

        result = validate(
            y_true=y_true_test,
            y_pred=y_true_pred,
            split_name="test",
            log_report=True,
        )

        print("[EVAL] Result on test:", result)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate a registered model on the test set."
    )
    parser.add_argument(
        "--model_version",
        type=str,
        required=False,
        help="Optional specific model version (e.g. 3). \
            If not provided, uses Production or latest.",
    )
    args = parser.parse_args()

    evaluate(model_version=args.model_version)


if __name__ == "__main__":
    main()
