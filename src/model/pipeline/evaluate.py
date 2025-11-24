import argparse

import pandas as pd

import mlflow
from src.model import config as cfg
from src.model.pipeline.metrics_helper import validate
from src.shared.model_resolver import resolve_model_uri


def evaluate(model_version: str | None = None) -> None:
    """
    Load model (pipeline) from MLflow and evaluate with test_processed.parquet.
    """
    model_uri = resolve_model_uri(model_version)
    test_path = cfg.DATASET_PROCESSED_DIR / "test_processed.parquet"
    df_test = pd.read_parquet(test_path)

    X_test = df_test[cfg.DATASET_FULL_TEXT_COLUMN].values
    y_test = df_test[cfg.DATASET_POLARITY_COLUMN].values

    print(f"[EVAL] Test load from {test_path} ({len(df_test)} rows)")
    print(f"[EVAL] Load model: {model_uri}")

    model = mlflow.sklearn.load_model(model_uri)

    with mlflow.start_run(run_name="evaluate_on_test"):
        mlflow.log_param("model_uri", model_uri)

        result = validate(
            estimator_pipeline=model,
            X_data=X_test,
            y_data=y_test,
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
