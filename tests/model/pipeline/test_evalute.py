import sys

import src.model.pipeline.evaluate as evaluate


def _mock_test_dataset_file(tmp_path, monkeypatch):
    test_path = tmp_path / "test.csv"
    test_path.write_text("1,Title A,Message A\n0,Title B,Message B\n")

    monkeypatch.setattr(evaluate.cfg, "DATASET_RAW_PATH", tmp_path, raising=True)

    return test_path


def test_load_test_dataset(tmp_path, monkeypatch):
    _mock_test_dataset_file(tmp_path, monkeypatch)

    df_test = evaluate._load_test_dataset()

    assert len(df_test) == 2
    assert list(df_test.columns) == [
        evaluate.cfg.DATASET_POLARITY_COLUMN,
        evaluate.cfg.DATASET_TITLE_COLUMN,
        evaluate.cfg.DATASET_MESSAGE_COLUMN,
    ]


def test_evaluate_logs_metrics(tmp_path, monkeypatch):
    _mock_test_dataset_file(tmp_path, monkeypatch)

    class MockModel:
        def predict(self, X):
            return [1]

    def mock_load_model(model_uri):
        return MockModel()

    monkeypatch.setattr(evaluate.mlflow.pyfunc, "load_model", mock_load_model)

    # Capture mlflow logs
    logged_params = {}
    logged_metrics = {}

    def mock_log_param(key, value):
        logged_params[key] = value

    def mock_log_metric(key, value):
        logged_metrics[key] = value

    monkeypatch.setattr(evaluate.mlflow, "log_param", mock_log_param)
    monkeypatch.setattr(evaluate.mlflow, "log_metric", mock_log_metric)

    expected_metrics = {
        "accuracy": 0.5,
        "f1_macro": 0.5,
    }

    def mock_validate(y_true, y_pred, split_name, log_report):
        assert y_true.tolist() == [1, 0]
        assert y_pred.tolist() == [1, 1]

        for key, value in expected_metrics.items():
            evaluate.mlflow.log_metric(f"{split_name}_{key}", value)

        return expected_metrics

    monkeypatch.setattr(evaluate, "validate", mock_validate)
    evaluate.evaluate(model_version=None)

    for key, value in expected_metrics.items():
        assert f"test_{key}" in logged_metrics
        assert logged_metrics[f"test_{key}"] == value


def test_main(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--model_version", "7"])

    called = {}

    def fake_evaluate(model_version):
        called["model_version"] = model_version

    monkeypatch.setattr(evaluate, "evaluate", fake_evaluate, raising=True)

    evaluate.main()

    assert called["model_version"] == "7"
