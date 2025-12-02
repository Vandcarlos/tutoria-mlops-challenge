from dataclasses import dataclass

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, f1_score

import mlflow


@dataclass
class ValidationResult:
    accuracy: float
    f1_macro: float


def validate(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    split_name: str = "val",
    log_report: bool = False,
) -> ValidationResult:
    """
    Compute and optionally log classification metrics.

    Parameters
    ----------
    y_true :
        Ground-truth labels (array-like).
    y_pred :
        Predicted labels (array-like).
    split_name : str
        Name of the data split ("train", "val", "test", etc.).
    log_mlflow : bool, default True
        Whether to log metrics to MLflow.

    Returns
    -------
    ValidationResult:
        Class with the computed metrics.
    """
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average="macro")

    mlflow.log_metric(f"{split_name}_accuracy", acc)
    mlflow.log_metric(f"{split_name}_f1_macro", f1)

    print(f"[{split_name}] Accuracy:", acc)
    print(f"[{split_name}] F1 macro:", f1)

    report = classification_report(y_true, y_pred)
    print(report)

    if log_report:
        mlflow.log_text(report, f"{split_name}_classification_report.txt")

    return ValidationResult(accuracy=acc, f1_macro=f1)
