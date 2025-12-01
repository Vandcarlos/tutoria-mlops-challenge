from pathlib import Path
import sys

import pandas as pd

import mlflow
from src.model import config as cfg
from src.model.data.preprocess_core import preprocess_df


def preprocess_batch(batch_idx: int) -> Path:
    cfg.DATASET_PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

    raw_batch_path = cfg.DATASET_BATCH_PATH / f"train_batch_{batch_idx}.csv"

    if not raw_batch_path.exists():
        raise FileNotFoundError(
            f"[PREPROCESS_BATCH] Batch {batch_idx} not found: {raw_batch_path}"
        )

    df_raw = pd.read_csv(raw_batch_path, header=None)
    df_raw.columns = [
        cfg.DATASET_POLARITY_COLUMN,
        cfg.DATASET_TITLE_COLUMN,
        cfg.DATASET_MESSAGE_COLUMN,
    ]

    df_processed = preprocess_df(df_raw=df_raw)

    out = cfg.DATASET_PROCESSED_PATH / f"train_batch_{batch_idx}.parquet"
    df_processed.to_parquet(out, index=False)

    print(
        f"[PREPROCESS_BATCH] Batch {batch_idx} processed → {out}\
            ({len(df_processed)} raws)"
    )
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m src.data.preprocess_batch <batch_idx>")

    batch_idx = int(sys.argv[1])

    with mlflow.start_run(run_name=f"data_preprocess_batch_{batch_idx}"):
        out = preprocess_batch(batch_idx)

        mlflow.log_param("batch_idx", batch_idx)
        mlflow.log_param(
            "raw_batch_input",
            str(cfg.DATASET_BATCH_PATH / f"train_batch_{batch_idx}.csv"),
        )
        mlflow.log_param("processed_batch_output", str(out))

        df = pd.read_parquet(out)
        mlflow.log_metric("processed_rows", len(df))

        mlflow.log_artifact(str(out))


if __name__ == "__main__":
    main()
