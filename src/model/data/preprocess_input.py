import argparse
import json

import pandas as pd

from src.model import config as cfg
from src.model.data.preprocess_core import preprocess_df


def preprocess_input(title: str | None, message: str | None) -> pd.DataFrame:
    title = title or ""
    message = message or ""

    if title.strip() == "" and message.strip() == "":
        raise ValueError("Both title and message cannot be empty.")

    df = pd.DataFrame(
        [
            {
                cfg.DATASET_TITLE_COLUMN: title,
                cfg.DATASET_MESSAGE_COLUMN: message,
            }
        ]
    )

    df = preprocess_df(df)
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess a single input for inference"
    )

    parser.add_argument(
        "--title",
        type=str,
        required=False,
        help="Title to preprocess for inference",
    )

    parser.add_argument(
        "--message",
        type=str,
        required=False,
        help="Message to preprocess for inference",
    )

    args = parser.parse_args()

    df = preprocess_input(args.title, args.message)

    print(json.dumps(df.to_dict(orient="records"), indent=4, ensure_ascii=False))
    return df


if __name__ == "__main__":
    main()
