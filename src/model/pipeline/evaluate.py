import argparse

import pandas as pd

import mlflow
from src.model import config as cfg
from src.model.data.preprocess_core import preprocess_df
from src.model.pipeline.metrics_helper import validate
from src.shared.model_resolver import resolve_model_uri


def _load_test_dataset() -> pd.DataFrame:
    test_path = cfg.DATASET_RAW_DIR / "test.csv"
    df_test = pd.read_csv(test_path, header=None)
    df_test.columns = [
        cfg.DATASET_POLARITY_COLUMN,
        cfg.DATASET_TITLE_COLUMN,
        cfg.DATASET_MESSAGE_COLUMN,
    ]

    print(f"[EVAL] Test load from {test_path} ({len(df_test)} rows)")

    return df_test


def evaluate(model_version: str | None = None) -> None:
    """
    Load model (pipeline) from MLflow and evaluate with test_processed.parquet.
    """
    df_test = _load_test_dataset()

    model_uri = resolve_model_uri(model_version)
    model = mlflow.pyfunc.load_model(model_uri)
    print(f"[EVAL] Load model: {model_uri}")

    X_test = preprocess_df(df_raw=df_test)

    y_true_pred = model.predict(X_test[cfg.DATASET_FULL_TEXT_COLUMN])
    y_true_test = df_test[cfg.DATASET_POLARITY_COLUMN].to_numpy()

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
