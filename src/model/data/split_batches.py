from pathlib import Path

import pandas as pd

import mlflow
from src.model import config as cfg


def split_raw_train() -> list[Path]:
    cfg.DATASET_BATCH_PATH.mkdir(parents=True, exist_ok=True)

    train_raw_path = cfg.DATASET_RAW_PATH / cfg.KAGGLE_DATASET_TRAIN_FILENAME

    if not train_raw_path.exists():
        raise FileNotFoundError(f"[SPLIT_RAW] train.csv not found: {train_raw_path}")

    df = pd.read_csv(train_raw_path)
    total_rows = len(df)

    batch_size = total_rows // cfg.DATASET_SPLIT_COUNT
    outputs: list[Path] = []

    for i in range(cfg.DATASET_SPLIT_COUNT):
        start = i * batch_size
        end = (i + 1) * batch_size if i < cfg.DATASET_SPLIT_COUNT - 1 else total_rows

        batch_df = df.iloc[start:end]
        out = cfg.DATASET_BATCH_PATH / f"train_batch_{i}.csv"
        batch_df.to_csv(out, index=False)

        outputs.append(out)
        print(f"[SPLIT_RAW] batch_{i}: {start} → {end} rows → {out}")

    return outputs


def main():
    with mlflow.start_run(run_name="data_split_raw_train"):
        outputs = split_raw_train()

        mlflow.log_param(
            "train_raw_input",
            str(cfg.DATASET_RAW_PATH / cfg.KAGGLE_DATASET_TRAIN_FILENAME),
        )
        mlflow.log_param("n_batches", cfg.DATASET_SPLIT_COUNT)

        df = pd.read_csv(cfg.DATASET_RAW_PATH / cfg.KAGGLE_DATASET_TRAIN_FILENAME)

        df_size = len(df)
        batch_size = df_size // cfg.DATASET_SPLIT_COUNT

        mlflow.log_metric("train_raw_rows", df_size)
        mlflow.log_metric("train_batch_size", batch_size)

        manifest = cfg.DATASET_BATCH_PATH / "train_raw_batches_manifest.txt"
        with open(manifest, "w") as f:
            for p in outputs:
                f.write(str(p) + "\n")

        mlflow.log_artifact(str(manifest))


if __name__ == "__main__":
    main()
