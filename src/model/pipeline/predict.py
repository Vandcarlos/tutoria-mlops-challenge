import argparse
import json
import sys
from typing import Any

import pandas as pd

import mlflow
from src.model.data.preprocess_core import preprocess_df
from src.shared.model_resolver import resolve_model_uri
from src.shared.schemas import PredictionLabel

DATASET_TITLE_COLUMN = "title"
DATASET_MESSAGE_COLUMN = "message"


def _preprocess_input(title: str | None, message: str | None) -> pd.DataFrame:
    title = title or ""
    message = message or ""

    if title.strip() == "" and message.strip() == "":
        raise ValueError("Both title and message cannot be empty.")

    df = pd.DataFrame(
        [
            {
                DATASET_TITLE_COLUMN: title,
                DATASET_MESSAGE_COLUMN: message,
            }
        ]
    )

    df = preprocess_df(df)
    return df


def predict(
    model_version: str | None,
    title: str | None,
    message: str | None,
) -> dict[str:Any]:
    """
    Preprocess the input and execute prediction using the MLflow model.
    """
    # Prediction
    model_input = {"title": title, "message": message}

    model_uri = resolve_model_uri(model_version)
    model = mlflow.pyfunc.load_model(model_uri)

    pred_obj = model.predict(model_input)[0]

    # Prediction parse
    prediction_label = PredictionLabel(pred_obj.label_id)

    # Input processing
    df_preprocessed = _preprocess_input(title=title, message=message)
    preprocessed_record = df_preprocessed.to_dict(orient="records")[0]

    result = {
        "input": {
            "title": title,
            "message": message,
        },
        "preprocessed": preprocessed_record,
        "model_uri": model_uri,
        "prediction": {
            "label": prediction_label.name,
            "label_id": pred_obj.label_id,
            "sentiment": prediction_label.sentiment,
            "confidence": pred_obj.confidence,
        },
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
