import argparse
from dataclasses import dataclass

from mlflow.entities.model_registry import ModelVersion
from mlflow.tracking import MlflowClient
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

import mlflow
from src.model import config as cfg
from src.model.pipeline.metrics_helper import validate


def _generate_tokeninzer_tfidf() -> TfidfVectorizer:
    tfidf_params = {
        "max_features": cfg.TFIDF_PARAMS.max_features,
        "min_df": cfg.TFIDF_PARAMS.min_df,
        "ngram_range": cfg.TFIDF_PARAMS.ngram_range,
    }

    tfidf = TfidfVectorizer(**tfidf_params)

    for k, v in tfidf_params.items():
        mlflow.log_param(f"tfidf__{k}", v)

    return tfidf


def _generate_estimator_clf() -> LogisticRegression:
    clf_params = {
        "C": cfg.CLF_PARAMS.C,
        "penalty": cfg.CLF_PARAMS.penalty,
        "solver": cfg.CLF_PARAMS.solver,
        "max_iter": cfg.CLF_PARAMS.max_iter,
    }

    clf = LogisticRegression(**clf_params)

    for k, v in clf_params.items():
        mlflow.log_param(f"clf__{k}", v)

    return clf


def _generate_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", _generate_tokeninzer_tfidf()),
            ("clf", _generate_estimator_clf()),
        ]
    )


def _get_train_data_frame(batches: list[int]) -> pd.DataFrame:
    dfs: list[pd.DataFrame] = []

    for batch in batches:
        batch_path = cfg.DATASET_PROCESSED_DIR / f"train_batch_{batch}.parquet"
        batch_df = pd.read_parquet(path=batch_path)
        dfs.append(batch_df)
        print(f"[TRAIN] Loaded batch {batch}: {batch_path} ({len(batch_df)} rows)")

    full_df = pd.concat(dfs, ignore_index=True)

    return full_df


@dataclass
class TrainValValues:
    X_train: list[str]
    y_train: list[int]
    X_val: list[str]
    y_val: list[str]


def _split_train_val(df: pd.DataFrame) -> TrainValValues:
    train_df, val_df = train_test_split(
        df,
        test_size=cfg.TRAIN_VAL_SPLIT.test_size,
        stratify=df[cfg.DATASET_POLARITY_COLUMN],
        random_state=cfg.TRAIN_VAL_SPLIT.random_state,
    )

    mlflow.log_param("split_test_size", cfg.TRAIN_VAL_SPLIT.test_size)
    mlflow.log_param("split_random_state", cfg.TRAIN_VAL_SPLIT.random_state)
    mlflow.log_metric("split_train_len", len(train_df))
    mlflow.log_metric("split_val_len", len(val_df))

    return TrainValValues(
        X_train=train_df[cfg.DATASET_FULL_TEXT_COLUMN].values,
        y_train=train_df[cfg.DATASET_POLARITY_COLUMN].values,
        X_val=val_df[cfg.DATASET_FULL_TEXT_COLUMN].values,
        y_val=val_df[cfg.DATASET_POLARITY_COLUMN].values,
    )


def _get_version() -> ModelVersion:
    run = mlflow.active_run()
    run_id = run.info.run_id

    client = MlflowClient()

    versions = client.search_model_versions(f"run_id = '{run_id}'")

    if not versions:
        raise RuntimeError(f"Version not found in Model Registry to run_id={run_id}")

    return versions[0]


def _generate_tags(batches: list[int], version):
    client = MlflowClient()

    client.set_model_version_tag(
        name=version.name,
        version=version.version,
        key="experiment",
        value="weekly_retraining",
    )

    client.set_model_version_tag(
        name=version.name,
        version=version.version,
        key="batches_used",
        value=str(batches),
    )


def train(batches: list[int]):
    with mlflow.start_run(run_name="train_model"):
        mlflow.log_param("batch_list", batches)

        df = _get_train_data_frame(batches=batches)

        print(f"[TRAIN] Total rows to use on train: {len(df)}")

        trainValValues = _split_train_val(df=df)

        pipeline = _generate_pipeline()
        pipeline.fit(trainValValues.X_train, trainValValues.y_train)

        mlflow.sklearn.log_model(
            sk_model=pipeline,
            artifact_path="model",
            registered_model_name=cfg.MODEL_NAME,
        )

        mlflow.set_tag("rows_train_total", len(df))
        mlflow.set_tag("batches_used", batches)

        version = _get_version()

        _generate_tags(batches=batches, version=version)

        val_result = validate(
            estimator_pipeline=pipeline,
            X_data=trainValValues.X_val,
            y_data=trainValValues.y_val,
        )

        print("[TRAIN] Validation result:", val_result)

        model_uri = f"models:/{cfg.MODEL_NAME}/{version.version}"
        print(f"[TRAIN] Model URI: {model_uri}")
        return model_uri


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--batches",
        type=str,
        required=False,
        help="Batch list OR a single limit. Ex: 5  →  uses 0..5",
    )
    args = parser.parse_args()

    if not args.batches:
        all_paths = sorted(cfg.DATASET_PROCESSED_DIR.glob("train_batch_*.parquet"))
        batches = sorted(int(p.stem.replace("train_batch_", "")) for p in all_paths)
        print(f"[TRAIN] Auto-discovered batches: {batches}")
        return train(batches)

    if "," not in args.batches:
        limit = int(args.batches)
        batches = list(range(0, limit + 1))
        print(f"[TRAIN] Using limit={limit} → batches={batches}")
        return train(batches)

    batches = [int(x.strip()) for x in args.batches.split(",") if x.strip()]
    print(f"[TRAIN] Explicit batches: {batches}")
    train(batches)


if __name__ == "__main__":
    main()
