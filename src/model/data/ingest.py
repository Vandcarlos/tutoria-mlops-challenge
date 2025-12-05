from pathlib import Path

import kagglehub
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

import mlflow
from src.model.config import (
    DATASET_RAW_PATH,
    DATASET_RAW_TEST_PARQUET,
    DATASET_RAW_TRAIN_PARQUET,
    KAGGLE_DATASET_NAME,
    KAGGLE_DATASET_TEST_FILENAME,
    KAGGLE_DATASET_TRAIN_FILENAME,
    S3_DATA_BUCKET,
    S3_DATA_KEY_RAW_TEST,
    S3_DATA_KEY_RAW_TRAIN,
    USE_S3_DATA,
)
from src.shared.s3_utils import upload_file_to_s3

print("[INGEST] After imports", flush=True)


def csv_to_parquet_in_chunks(
    csv_path: Path, parquet_path: Path, chunksize: int = 100_000
) -> int:
    """Convert a large CSV to Parquet using small memory footprints."""
    print(
        f"[INGEST] Converting {csv_path} to {parquet_path} in chunks of {chunksize}",
        flush=True,
    )

    rows = 0
    writer = None

    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        rows += len(chunk)

        table = pa.Table.from_pandas(chunk)

        if writer is None:
            writer = pq.ParquetWriter(parquet_path, table.schema)

        writer.write_table(table)

    if writer is not None:
        writer.close()

    print(f"[INGEST] Finished writing {parquet_path} with {rows} rows", flush=True)
    return rows


def ingest() -> dict:
    print("[INGEST] Enter ingest()", flush=True)
    DATASET_RAW_PATH.mkdir(parents=True, exist_ok=True)
    print("[INGEST] Created raw path", flush=True)

    print(f"[INGEST] Download dataset: {KAGGLE_DATASET_NAME}", flush=True)
    dataset_path = Path(kagglehub.dataset_download(KAGGLE_DATASET_NAME))
    print(f"[INGEST] Dataset downloaded to: {dataset_path}", flush=True)

    train_src = dataset_path / KAGGLE_DATASET_TRAIN_FILENAME
    test_src = dataset_path / KAGGLE_DATASET_TEST_FILENAME

    if not train_src.exists():
        raise FileNotFoundError(f"Train file not found: {train_src}")

    if not test_src.exists():
        raise FileNotFoundError(f"Test file not found: {test_src}")

    train_rows = csv_to_parquet_in_chunks(
        train_src, DATASET_RAW_TRAIN_PARQUET, chunksize=100_000
    )
    test_rows = csv_to_parquet_in_chunks(
        test_src, DATASET_RAW_TEST_PARQUET, chunksize=100_000
    )

    print(f"[INGEST] train → {DATASET_RAW_TRAIN_PARQUET}")
    print(f"[INGEST] test  → {DATASET_RAW_TEST_PARQUET}")

    output = {
        "train_path": DATASET_RAW_TRAIN_PARQUET,
        "test_path": DATASET_RAW_TEST_PARQUET,
        "train_rows": train_rows,
        "test_rows": test_rows,
    }

    print(
        f"[INGEST] S3_DATA_BUCKET={S3_DATA_BUCKET!r}, USE_S3_DATA={USE_S3_DATA}",
        flush=True,
    )

    if USE_S3_DATA:
        upload_file_to_s3(
            DATASET_RAW_TRAIN_PARQUET,
            bucket=S3_DATA_BUCKET,
            key=S3_DATA_KEY_RAW_TRAIN,
        )
        upload_file_to_s3(
            DATASET_RAW_TEST_PARQUET,
            bucket=S3_DATA_BUCKET,
            key=S3_DATA_KEY_RAW_TEST,
        )

    return output


def main():
    with mlflow.start_run(run_name="data_ingest"):
        output = ingest()

        mlflow.log_param("dataset_name", KAGGLE_DATASET_NAME)

        for key, value in output.items():
            mlflow.log_param(key, str(value))


if __name__ == "__main__":
    main()
