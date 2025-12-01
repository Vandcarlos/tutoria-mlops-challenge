from evidently import Report
from evidently.presets import DataDriftPreset
import pandas as pd

import mlflow
from src.monitoring.config import (
    MONITORING_OUTPUT_PATH,
    MONITORING_REPORT_PATH,
    REFERENCE_PREDICTIONS_PATH,
)
from src.monitoring.generate_reference_predictions import generate_reference_predictions
from src.monitoring.log_loader import load_prediction_logs_local


def load_reference_predictions() -> pd.DataFrame:
    """Load the reference predictions dataset used as baseline.

    This should be generated from your validation set:
    - run the model on validation data
    - store predicted_label and confidence in a parquet file
    """

    if not REFERENCE_PREDICTIONS_PATH.exists():
        generate_reference_predictions()

    df = pd.read_parquet(REFERENCE_PREDICTIONS_PATH)

    expected_cols = {"predicted_label", "confidence"}

    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(
            f"Reference dataset is missing columns: {missing}. "
            "Expected at least: predicted_label, confidence."
        )

    return df


def build_prediction_drift_report(
    reference_df: pd.DataFrame,
    current_df: pd.DataFrame,
) -> str:
    """Generate an Evidently data drift report for predictions."""

    MONITORING_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    reference = reference_df[["predicted_label", "confidence"]].copy()
    current = current_df[["predicted_label", "confidence"]].copy()

    report = Report(
        metrics=[
            DataDriftPreset(),
        ]
    )

    snapshot = report.run(reference_data=reference, current_data=current)

    print(snapshot.json())

    MONITORING_REPORT_PATH.touch(exist_ok=True)
    snapshot.save_html(str(MONITORING_REPORT_PATH))

    return MONITORING_REPORT_PATH


def log_monitoring_to_mlflow() -> None:
    """Log monitoring artifacts to MLflow for traceability."""

    with mlflow.start_run(run_name="monitoring_report_local"):
        mlflow.log_artifacts(MONITORING_OUTPUT_PATH, artifact_path="monitoring_reports")


def main() -> None:
    reference_df = load_reference_predictions()
    current_df = load_prediction_logs_local()

    if current_df.empty:
        print("No prediction logs found for the selected period.")
        return

    report_path = build_prediction_drift_report(
        reference_df=reference_df, current_df=current_df
    )

    print(f"Prediction drift report saved at: {report_path}")

    log_monitoring_to_mlflow()


if __name__ == "__main__":
    main()
