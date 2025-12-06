from pathlib import Path

import pandas as pd
import pytest

from src.monitoring import generate_drift_reports as gdr

# ---------------------------------------------------------------------------
# load_reference_predictions
# ---------------------------------------------------------------------------


def test_load_reference_predictions_generates_when_file_missing(monkeypatch, tmp_path):
    """
    If REFERENCE_PREDICTIONS_PATH does not exist, must call generate_reference_predictions()
    and then read the parquet file.
    """
    ref_path = tmp_path / "ref.parquet"
    monkeypatch.setattr(gdr, "REFERENCE_PREDICTIONS_PATH", ref_path, raising=True)

    # Fake generator writes a minimal parquet
    def fake_generate_reference_predictions():
        df = pd.DataFrame(
            {
                "predicted_label": [0, 1],
                "confidence": [0.5, 0.9],
            }
        )
        df.to_parquet(ref_path)
        return ref_path

    monkeypatch.setattr(
        gdr,
        "generate_reference_predictions",
        fake_generate_reference_predictions,
        raising=True,
    )

    df = gdr.load_reference_predictions()
    assert list(df.columns) == ["predicted_label", "confidence"]
    assert len(df) == 2


def test_load_reference_predictions_raises_when_missing_columns(monkeypatch, tmp_path):
    """
    If the parquet exists but does not contain required columns,
    should raise ValueError.
    """
    ref_path = tmp_path / "ref.parquet"
    df = pd.DataFrame({"something_else": [1, 2, 3]})
    df.to_parquet(ref_path)

    monkeypatch.setattr(gdr, "REFERENCE_PREDICTIONS_PATH", ref_path, raising=True)

    with pytest.raises(ValueError) as excinfo:
        gdr.load_reference_predictions()

    assert "Reference dataset is missing columns" in str(excinfo.value)


# ---------------------------------------------------------------------------
# build_prediction_drift_report
# ---------------------------------------------------------------------------


def test_build_prediction_drift_report_runs_evidently_and_writes_html(
    monkeypatch, tmp_path
):
    """
    build_prediction_drift_report must:
    - create MONITORING_REPORTS_FOLDER_PATH
    - call Report.run(reference_data=..., current_data=...)
    - call snapshot.save_html with MONITORING_REPORT_PATH
    - return MONITORING_REPORT_PATH
    """
    output_dir = tmp_path / "monitoring"
    report_path = output_dir / "prediction_drift_report.html"

    # Patch the paths used by the implementation so the test writes only to tmp_path
    monkeypatch.setattr(gdr, "MONITORING_REPORTS_FOLDER_PATH", output_dir, raising=True)
    monkeypatch.setattr(gdr, "MONITORING_REPORT_PATH", report_path, raising=True)

    # Fake Report + snapshot
    class FakeSnapshot:
        def __init__(self, reference_data, current_data):
            self.reference_data = reference_data
            self.current_data = current_data
            self.saved_paths = []

        def json(self):
            return '{"ok": true}'

        def save_html(self, path: str):
            self.saved_paths.append(path)
            Path(path).write_text("<html>test</html>", encoding="utf-8")

    class FakeReport:
        def __init__(self, metrics):
            self.metrics = metrics
            self.last_snapshot: FakeSnapshot | None = None

        def run(self, reference_data, current_data):
            self.last_snapshot = FakeSnapshot(reference_data, current_data)
            return self.last_snapshot

    monkeypatch.setattr(gdr, "Report", FakeReport, raising=True)

    # Dummy dataframes
    reference_df = pd.DataFrame({"predicted_label": [0, 1], "confidence": [0.5, 0.9]})
    current_df = pd.DataFrame({"predicted_label": [1, 1], "confidence": [0.7, 0.95]})

    # Act
    returned_path = gdr.build_prediction_drift_report(reference_df, current_df)

    # Assert path & file
    assert returned_path == report_path
    assert report_path.exists()
    assert report_path.read_text(encoding="utf-8").startswith("<html")

    # Ensure directory was created
    assert output_dir.exists() and output_dir.is_dir()


# ---------------------------------------------------------------------------
# log_monitoring_to_mlflow
# ---------------------------------------------------------------------------


def test_log_monitoring_to_mlflow_uses_log_artifacts(monkeypatch, tmp_path):
    """
    log_monitoring_to_mlflow must:
    - open an MLflow run with name 'monitoring_report_local'
    - call log_artifacts(MONITORING_REPORTS_FOLDER_PATH, artifact_path='monitoring_reports')
    """
    output_dir = tmp_path / "monitoring"
    output_dir.mkdir()

    monkeypatch.setattr(gdr, "MONITORING_REPORTS_FOLDER_PATH", output_dir, raising=True)

    # Fake mlflow-compatible object
    class FakeMlflow:
        def __init__(self):
            self.runs = []
            self.artifacts = []

        class RunCtx:
            def __init__(self, outer, run_name):
                self.outer = outer
                self.run_name = run_name

            def __enter__(self):
                self.outer.runs.append(self.run_name)
                return self

            def __exit__(self, exc_type, exc, tb):
                # nothing special
                pass

        def start_run(self, run_name: str):
            return FakeMlflow.RunCtx(self, run_name)

        def log_artifacts(
            self, local_dir: str | Path, artifact_path: str | None = None
        ):
            self.artifacts.append((str(local_dir), artifact_path))

    fake_mlflow = FakeMlflow()
    monkeypatch.setattr(gdr, "mlflow", fake_mlflow, raising=True)

    # Act
    gdr.log_monitoring_to_mlflow()

    # Assert
    assert fake_mlflow.runs == ["monitoring_report_local"]
    assert len(fake_mlflow.artifacts) == 1
    local_dir, artifact_path = fake_mlflow.artifacts[0]
    assert local_dir == str(output_dir)
    assert artifact_path == "monitoring_reports"
