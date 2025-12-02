from pathlib import Path

import pandas as pd

import mlflow
from src.model.config import (
    DATASET_BATCH_ITEM_PATH,
    DATASET_BATCH_PATH,
    DATASET_RAW_TRAIN_PARQUET,
    DATASET_SPLIT_COUNT,
)


def split_raw_train() -> dict[str:any]:
    DATASET_BATCH_PATH.mkdir(parents=True, exist_ok=True)

    if not DATASET_RAW_TRAIN_PARQUET.exists():
        raise FileNotFoundError(
            f"[SPLIT_RAW] train.parquet not found: {DATASET_RAW_TRAIN_PARQUET}"
        )

    df = pd.read_parquet(DATASET_RAW_TRAIN_PARQUET)
    total_rows = len(df)

    batch_size = total_rows // DATASET_SPLIT_COUNT
    outputs: list[Path] = []

    for i in range(DATASET_SPLIT_COUNT):
        start = i * batch_size
        end = (i + 1) * batch_size if i < DATASET_SPLIT_COUNT - 1 else total_rows

        batch_df = df.iloc[start:end]
        out = DATASET_BATCH_ITEM_PATH(batch_idx=i)
        batch_df.to_parquet(out, index=False)

        outputs.append(out)
        print(f"[SPLIT_RAW] batch_{i}: {start} → {end} rows → {out}")

    return {
        "input_path": DATASET_RAW_TRAIN_PARQUET,
        "outputs_path": outputs,
        "n_batches": DATASET_SPLIT_COUNT,
        "batch_size": batch_size,
        "total_rows": total_rows,
        "batch_row_size": len(df) // DATASET_SPLIT_COUNT,
    }


def main():
    with mlflow.start_run(run_name="data_split_raw_train"):
        result = split_raw_train()

        for key, value in result.items():
            mlflow.log_param(key, str(value))


if __name__ == "__main__":
    main()
