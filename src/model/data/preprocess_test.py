from pathlib import Path

import pandas as pd

import mlflow
from src.model import config as cfg
from src.model.data.preprocess_core import preprocess_df


def preprocess_test() -> Path:
    cfg.DATASET_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw_test_path = cfg.DATASET_RAW_DIR / cfg.KAGGLE_DATASET_TEST_FILENAME

    if not raw_test_path.exists():
        raise FileNotFoundError(
            f"[PREPROCESS_TEST] Test file not found: {raw_test_path}"
        )

    df_raw = pd.read_csv(raw_test_path, header=None)
    df_raw.columns = cfg.DATASET_CLEAR_COLUMNS

    df_processed = preprocess_df(df_raw=df_raw)

    out = cfg.DATASET_PROCESSED_DIR / "test_processed.parquet"
    df_processed.to_parquet(out, index=False)

    print(f"[PREPROCESS_TEST] test_processed → {out} ({len(df_processed)} rows)")
    return out


def main():
    with mlflow.start_run(run_name="data_preprocess_test"):
        out = preprocess_test()

        mlflow.log_param(
            "test_raw_input",
            str(cfg.DATASET_RAW_DIR / cfg.KAGGLE_DATASET_TEST_FILENAME),
        )
        mlflow.log_param("test_processed_output", str(out))

        df = pd.read_parquet(out)
        mlflow.log_metric("test_processed_rows", len(df))

        mlflow.log_artifact(str(out))


if __name__ == "__main__":
    main()
