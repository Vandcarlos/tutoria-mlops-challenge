from dataclasses import dataclass

from sklearn.metrics import accuracy_score, classification_report, f1_score

import mlflow


@dataclass
class ValidationResult:
    accuracy: float
    f1_macro: float


def validate(
    estimator_pipeline,
    X_data,
    y_data,
    split_name: str = "val",
    log_report: bool = False,
) -> ValidationResult:
    y_pred = estimator_pipeline.predict(X_data)

    acc = accuracy_score(y_data, y_pred)
    f1 = f1_score(y_data, y_pred, average="macro")

    mlflow.log_metric(f"{split_name}_accuracy", acc)
    mlflow.log_metric(f"{split_name}_f1_macro", f1)

    print(f"[{split_name}] Accuracy:", acc)
    print(f"[{split_name}] F1 macro:", f1)

    report = classification_report(y_data, y_pred)
    print(report)

    if log_report:
        mlflow.log_text(report, f"{split_name}_classification_report.txt")

    return ValidationResult(accuracy=acc, f1_macro=f1)
