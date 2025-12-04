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
    S3_DATA_BUCKET,
    S3_DATA_KEY_BATCH_ITEM,
    S3_DATA_KEY_PROCESSED_ITEM,
    USE_S3_DATA,
)
from src.model.utilities.preprocess_core import preprocess_df
from src.shared.s3_utils import download_file_from_s3, upload_file_to_s3


def preprocess_batch(batch_idx: int) -> dict[str:any]:
    batch_item_path = DATASET_BATCH_ITEM_PATH(batch_idx=batch_idx)

    if USE_S3_DATA:
        download_file_from_s3(
            file_path=batch_item_path,
            bucket=S3_DATA_BUCKET,
            key=S3_DATA_KEY_BATCH_ITEM(batch_idx=batch_idx),
        )

    DATASET_PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

    raw_batch_path = batch_item_path

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

    if USE_S3_DATA:
        upload_file_to_s3(
            file_path=processed_batch_path,
            bucket=S3_DATA_BUCKET,
            key=S3_DATA_KEY_PROCESSED_ITEM(batch_idx=batch_idx),
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
