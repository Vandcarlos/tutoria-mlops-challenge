import sys
from types import SimpleNamespace

import pandas as pd

import src.model.pipeline.evaluate as evaluate


def _mock_test_dataset(monkeypatch):
    """
    Patch evaluate._load_test_dataset to read a small in-memory DataFrame
    by mocking pandas.read_parquet.
    """
    df = pd.DataFrame(
        [
            [1, "Title A", "Message A"],
            [0, "Title B", "Message B"],
        ],
        columns=[
            evaluate.DATASET_POLARITY_COLUMN,
            evaluate.DATASET_TITLE_COLUMN,
            evaluate.DATASET_MESSAGE_COLUMN,
        ],
    )

    def fake_read_parquet(path):
        return df

    monkeypatch.setattr(evaluate.pd, "read_parquet", fake_read_parquet)

    return df


def test_load_test_dataset(monkeypatch):
    df_expected = _mock_test_dataset(monkeypatch)

    df_test = evaluate._load_test_dataset()

    assert len(df_test) == len(df_expected)
    assert list(df_test.columns) == list(df_expected.columns)
    assert df_test[evaluate.DATASET_POLARITY_COLUMN].tolist() == [1, 0]
    assert df_test[evaluate.DATASET_TITLE_COLUMN].tolist() == ["Title A", "Title B"]
    assert df_test[evaluate.DATASET_MESSAGE_COLUMN].tolist() == [
        "Message A",
        "Message B",
    ]


def test_evaluate_logs_metrics(monkeypatch):
    df = _mock_test_dataset(monkeypatch)

    # Dummy model that returns fixed predictions
    class MockModel:
        def predict(self, X):
            return [1, 1]

    # Fake mlflow module
    class DummyRun:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

    class DummyMlflow:
        def __init__(self):
            self.logged_params = {}
            self.logged_metrics = {}
            self.pyfunc = SimpleNamespace(load_model=lambda uri: MockModel())

        def start_run(self, run_name=None, nested=None):
            return DummyRun()

        def log_param(self, key, value):
            self.logged_params[key] = value

        def log_metric(self, key, value):
            self.logged_metrics[key] = value

    dummy_mlflow = DummyMlflow()
    monkeypatch.setattr(evaluate, "mlflow", dummy_mlflow)

    def mock_resolve_model_uri(model_version):
        return "models:/sentiment-analysis/Production"

    monkeypatch.setattr(evaluate, "resolve_model_uri", mock_resolve_model_uri)

    expected_metrics = {
        "accuracy": 0.5,
        "f1_macro": 0.5,
    }

    def mock_validate(y_true, y_pred, split_name, log_report):
        assert y_true.tolist() == df[evaluate.DATASET_POLARITY_COLUMN].tolist()
        assert y_pred == [1, 1]
        assert split_name == "test"
        assert log_report is True

        for key, value in expected_metrics.items():
            dummy_mlflow.log_metric(f"{split_name}_{key}", value)

        return expected_metrics

    monkeypatch.setattr(evaluate, "validate", mock_validate)

    evaluate.evaluate(model_version=None)

    assert "model_uri" in dummy_mlflow.logged_params
    assert (
        dummy_mlflow.logged_params["model_uri"]
        == "models:/sentiment-analysis/Production"
    )

    for key, value in expected_metrics.items():
        metric_key = f"test_{key}"
        assert metric_key in dummy_mlflow.logged_metrics
        assert dummy_mlflow.logged_metrics[metric_key] == value


def test_main(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--model_version", "7"])

    called = {}

    def fake_evaluate(model_version):
        called["model_version"] = model_version

    monkeypatch.setattr(evaluate, "evaluate", fake_evaluate, raising=True)

    evaluate.main()

    assert called["model_version"] == "7"
