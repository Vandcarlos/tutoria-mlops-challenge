from pathlib import Path
import shutil

import kagglehub

import mlflow
from src.model import config as cfg


def ingest() -> dict:
    cfg.DATASET_RAW_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[INGEST] Download dataset: {cfg.KAGGLE_DATASET_NAME}")
    dataset_path = Path(kagglehub.dataset_download(cfg.KAGGLE_DATASET_NAME))

    train_src = dataset_path / cfg.KAGGLE_DATASET_TRAIN_FILENAME
    test_src = dataset_path / cfg.KAGGLE_DATASET_TEST_FILENAME

    if not train_src.exists():
        raise FileNotFoundError(f"Train file not found: {train_src}")

    if not test_src.exists():
        raise FileNotFoundError(f"Test file not found: {test_src}")

    train_dst = cfg.DATASET_RAW_DIR / cfg.KAGGLE_DATASET_TRAIN_FILENAME
    test_dst = cfg.DATASET_RAW_DIR / cfg.KAGGLE_DATASET_TEST_FILENAME

    shutil.copy(train_src, train_dst)
    shutil.copy(test_src, test_dst)

    print(f"[INGEST] train → {train_dst}")
    print(f"[INGEST] test  → {test_dst}")

    return {
        "train": train_dst,
        "test": test_dst,
    }


def main():
    with mlflow.start_run(run_name="data_ingest"):
        output = ingest()

        mlflow.log_param("dataset_name", cfg.KAGGLE_DATASET_NAME)
        mlflow.log_param(
            "train_path", cfg.DATASET_RAW_DIR / cfg.KAGGLE_DATASET_TRAIN_FILENAME
        )
        mlflow.log_param(
            "test_path", cfg.DATASET_RAW_DIR / cfg.KAGGLE_DATASET_TEST_FILENAME
        )

        mlflow.log_artifact(str(output["train"]))
        mlflow.log_artifact(str(output["test"]))


if __name__ == "__main__":
    main()
