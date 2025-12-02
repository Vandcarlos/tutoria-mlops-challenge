from pathlib import Path

import kagglehub
import pandas as pd

import mlflow
from src.model.config import (
    DATASET_RAW_PATH,
    DATASET_RAW_TEST_PARQUET,
    DATASET_RAW_TRAIN_PARQUET,
    KAGGLE_DATASET_NAME,
    KAGGLE_DATASET_TEST_FILENAME,
    KAGGLE_DATASET_TRAIN_FILENAME,
)


def ingest() -> dict:
    DATASET_RAW_PATH.mkdir(parents=True, exist_ok=True)

    print(f"[INGEST] Download dataset: {KAGGLE_DATASET_NAME}")
    dataset_path = Path(kagglehub.dataset_download(KAGGLE_DATASET_NAME))

    train_src = dataset_path / KAGGLE_DATASET_TRAIN_FILENAME
    test_src = dataset_path / KAGGLE_DATASET_TEST_FILENAME

    if not train_src.exists():
        raise FileNotFoundError(f"Train file not found: {train_src}")

    if not test_src.exists():
        raise FileNotFoundError(f"Test file not found: {test_src}")

    df_train = pd.read_csv(train_src)
    df_test = pd.read_csv(test_src)

    train_rows = len(df_train)
    test_rows = len(df_test)

    df_train.to_parquet(DATASET_RAW_TRAIN_PARQUET, index=False)
    df_test.to_parquet(DATASET_RAW_TEST_PARQUET, index=False)

    print(f"[INGEST] train → {DATASET_RAW_TRAIN_PARQUET}")
    print(f"[INGEST] test  → {DATASET_RAW_TEST_PARQUET}")

    return {
        "train_path": DATASET_RAW_TRAIN_PARQUET,
        "test_path": DATASET_RAW_TEST_PARQUET,
        "train_rows": train_rows,
        "test_rows": test_rows,
    }


def main():
    with mlflow.start_run(run_name="data_ingest"):
        output = ingest()

        mlflow.log_param("dataset_name", KAGGLE_DATASET_NAME)

        for key, value in output.items():
            mlflow.log_param(key, str(value))


if __name__ == "__main__":
    main()
