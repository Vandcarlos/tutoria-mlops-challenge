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
)
from src.model.utilities.metrics_helper import validate
from src.model.utilities.preprocess_core import preprocess_df
from src.shared.model_resolver import resolve_model_uri


def _load_test_dataset() -> pd.DataFrame:
    df_test = pd.read_parquet(DATASET_RAW_TEST_PARQUET)
    df_test.columns = [
        DATASET_POLARITY_COLUMN,
        DATASET_TITLE_COLUMN,
        DATASET_MESSAGE_COLUMN,
    ]

    print(f"[EVAL] Test load from {DATASET_RAW_TEST_PARQUET} ({len(df_test)} rows)")

    return df_test


def _save_processed_test_dataset(df_test_processed: pd.DataFrame):
    """
    Save processed test dataset to be reused by monitoring.

    It writes the file to:
        ./data/processed/test_processed.parquet
    (or to the path defined by DATASET_PROCESSED_PATH)
    """
    DATASET_PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

    df_test_processed.to_parquet(DATASET_PROCESSED_TEST_PATH)

    print(f"[evaluate] Saved processed test dataset to: {DATASET_PROCESSED_TEST_PATH}")


def evaluate(model_version: str | None = None) -> None:
    """
    Load model (pipeline) from MLflow and evaluate with test_processed.parquet.
    """
    df_test = _load_test_dataset()

    df_test_processed = preprocess_df(df_test)
    _save_processed_test_dataset(df_test_processed)

    model_uri = resolve_model_uri(model_version)
    model = mlflow.pyfunc.load_model(model_uri)
    print(f"[EVAL] Load model: {model_uri}")

    y_true_pred = model.predict(df_test_processed[DATASET_FULL_TEXT_COLUMN])
    y_true_test = df_test[DATASET_POLARITY_COLUMN].to_numpy()

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
