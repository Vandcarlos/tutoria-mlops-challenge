import numpy as np
import pytest
from sklearn.metrics import accuracy_score, f1_score

import src.model.pipeline.metrics_helper as metrics_helper


def test_validate_returns_correct_metrics_and_logs_to_mlflow(monkeypatch):
    y_true = np.array([0, 1, 1, 0])
    y_pred = np.array([0, 1, 0, 0])
    split_name = "val"

    logged_metrics: list[tuple[str, float]] = []
    logged_texts: list[tuple[str, str]] = []

    def fake_log_metric(name: str, value: float) -> None:
        logged_metrics.append((name, value))

    def fake_log_text(text: str, artifact_file: str) -> None:
        logged_texts.append((text, artifact_file))

    monkeypatch.setattr(
        metrics_helper.mlflow, "log_metric", fake_log_metric, raising=True
    )
    monkeypatch.setattr(metrics_helper.mlflow, "log_text", fake_log_text, raising=True)

    result = metrics_helper.validate(
        y_true=y_true,
        y_pred=y_pred,
        split_name=split_name,
        log_report=True,
    )

    expected_acc = accuracy_score(y_true, y_pred)
    expected_f1 = f1_score(y_true, y_pred, average="macro")

    assert pytest.approx(result.accuracy) == expected_acc
    assert pytest.approx(result.f1_macro) == expected_f1

    metric_names = {name for (name, _) in logged_metrics}
    assert f"{split_name}_accuracy" in metric_names
    assert f"{split_name}_f1_macro" in metric_names

    metrics_dict = {name: value for (name, value) in logged_metrics}
    assert pytest.approx(metrics_dict[f"{split_name}_accuracy"]) == expected_acc
    assert pytest.approx(metrics_dict[f"{split_name}_f1_macro"]) == expected_f1

    assert len(logged_texts) == 1
    text, artifact_file = logged_texts[0]
    assert artifact_file == f"{split_name}_classification_report.txt"

    assert len(text.strip()) > 0


def test_validate_does_not_log_report_when_log_report_false(monkeypatch):
    y_true = np.array([0, 1])
    y_pred = np.array([0, 1])

    logged_metrics: list[tuple[str, float]] = []
    logged_texts: list[tuple[str, str]] = []

    def fake_log_metric(name: str, value: float) -> None:
        logged_metrics.append((name, value))

    def fake_log_text(text: str, artifact_file: str) -> None:
        logged_texts.append((text, artifact_file))

    monkeypatch.setattr(
        metrics_helper.mlflow, "log_metric", fake_log_metric, raising=True
    )
    monkeypatch.setattr(metrics_helper.mlflow, "log_text", fake_log_text, raising=True)

    result = metrics_helper.validate(
        y_true=y_true,
        y_pred=y_pred,
        split_name="test",
        log_report=False,
    )

    assert len(logged_metrics) == 2
    assert logged_texts == []

    # sanity check that metrics make sense (perfect prediction)
    assert pytest.approx(result.accuracy) == 1.0
    assert pytest.approx(result.f1_macro) == 1.0
