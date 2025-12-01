import argparse
import json
import sys

import mlflow
from src import config as cfg
from src.model.data.preprocess_input import preprocess_input
from src.model.pipeline.model_resolver import resolve_model_uri


def predict(model_version: str | None, title: str | None, message: str | None) -> dict:
    """
    Preprocess the input and execute prediction using the MLflow model.
    """
    df = preprocess_input(title=title, message=message)

    model_uri = resolve_model_uri(model_version)

    model = mlflow.sklearn.load_model(model_uri)

    X = df[cfg.DATASET_FULL_TEXT_COLUMN].values
    pred = int(model.predict(X)[0])

    if pred == 1:
        label = "negative"
    elif pred == 2:
        label = "positive"
    else:
        label = f"unknown({pred})"

    result = {
        "input": {
            "title": title,
            "message": message,
        },
        "preprocessed": df.to_dict(orient="records")[0],
        "model_uri": model_uri,
        "prediction": pred,
        "label": label,
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run sentiment prediction using the trained model"
    )
    parser.add_argument(
        "--title",
        type=str,
        required=False,
        help="Optional title for inference",
    )
    parser.add_argument(
        "--message",
        type=str,
        required=False,
        help="Optional message for inference",
    )
    parser.add_argument(
        "--model_version",
        type=str,
        required=False,
        help="Optional specific model version (e.g. 3). \
            If not provided, uses highest version.",
    )

    args = parser.parse_args()

    try:
        result = predict(
            model_version=args.model_version,
            title=args.title,
            message=args.message,
        )
    except ValueError as e:
        # title e message vazios
        print(f"[PREDICT][ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[PREDICT][FATAL] {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
