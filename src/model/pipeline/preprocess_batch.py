import sys

import pandas as pd

import mlflow
from src.model.config import (
    DATASET_BATCH_ITEM_PATH,
    DATASET_MESSAGE_COLUMN,
    DATASET_POLARITY_COLUMN,
    DATASET_PROCESSED_BATCH_ITEM_PATH,
    DATASET_PROCESSED_PATH,
    DATASET_TITLE_COLUMN,
)
from src.model.utilities.preprocess_core import preprocess_df


def preprocess_batch(batch_idx: int) -> dict[str:any]:
    DATASET_PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

    raw_batch_path = DATASET_BATCH_ITEM_PATH(batch_idx=batch_idx)

    if not raw_batch_path.exists():
        raise FileNotFoundError(
            f"[PREPROCESS_BATCH] Batch {batch_idx} not found: {raw_batch_path}"
        )

    df_raw = pd.read_parquet(raw_batch_path)
    df_raw.columns = [
        DATASET_POLARITY_COLUMN,
        DATASET_TITLE_COLUMN,
        DATASET_MESSAGE_COLUMN,
    ]

    df_processed = preprocess_df(df_raw=df_raw)

    processed_batch_path = DATASET_PROCESSED_BATCH_ITEM_PATH(batch_idx=batch_idx)
    df_processed.to_parquet(processed_batch_path, index=False)

    print(
        f"[PREPROCESS_BATCH] Batch {batch_idx} processed → {processed_batch_path}\
            ({len(df_processed)} raws)"
    )

    return {
        "input_path": raw_batch_path,
        "output_path": processed_batch_path,
        "n_rows": len(df_processed),
    }


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m src.data.preprocess_batch <batch_idx>")

    batch_idx = int(sys.argv[1])

    with mlflow.start_run(run_name=f"data_preprocess_batch_{batch_idx}"):
        result = preprocess_batch(batch_idx)

        for key, value in result.items():
            mlflow.log_param(key, str(value))


if __name__ == "__main__":
    main()
