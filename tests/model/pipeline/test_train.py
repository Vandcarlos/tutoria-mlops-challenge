import sys
from types import SimpleNamespace

import pandas as pd
import pytest

import src.model.pipeline.train as train

# ---------------------------------------------------------------------------
# Fake MLflow stack
# ---------------------------------------------------------------------------


class FakeRun:
    def __init__(self, mlflow, run_id: str = "run-123", run_name: str | None = None):
        self._mlflow = mlflow
        self.info = SimpleNamespace(run_id=run_id)
        self.run_name = run_name

    def __enter__(self):
        self._mlflow._active_run = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mlflow._active_run = None


class FakeSklearnSubmodule:
    def __init__(self):
        self.logged_models: list[tuple[object, str, str]] = []

    def log_model(self, sk_model, artifact_path: str, registered_model_name: str):
        self.logged_models.append((sk_model, artifact_path, registered_model_name))


class FakeMlflow:
    def __init__(self):
        self._active_run: FakeRun | None = None
        self.logged_params: list[tuple[str, object]] = []
        self.logged_metrics: list[tuple[str, float]] = []
        self.tags: dict[str, object] = {}
        self.sklearn = FakeSklearnSubmodule()

    # Context / active run
    def start_run(self, run_name: str | None = None):
        return FakeRun(self, run_id="run-123", run_name=run_name)

    def active_run(self):
        return self._active_run

    # Logging
    def log_param(self, name: str, value: object):
        self.logged_params.append((name, value))

    def log_metric(self, name: str, value: float):
        self.logged_metrics.append((name, value))

    def set_tag(self, key: str, value: object):
        self.tags[key] = value


class FakeModelVersion:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version


class FakeMlflowClient:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.search_queries: list[str] = []
        self.version_tags: list[tuple[str, str, str, str]] = []

    def search_model_versions(self, filter_string: str):
        # just register the query and return one fake version
        self.search_queries.append(filter_string)
        return [FakeModelVersion(name=self.model_name, version="7")]

    def set_model_version_tag(self, name: str, version: str, key: str, value: str):
        self.version_tags.append((name, version, key, value))


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_fake_cfg(processed_path=None) -> SimpleNamespace:
    """
    Create a fake config object with only the attributes used in train.py.
    """
    return SimpleNamespace(
        TFIDF_PARAMS=SimpleNamespace(
            max_features=10_000,
            min_df=1,
            ngram_range=(1, 2),
        ),
        CLF_PARAMS=SimpleNamespace(
            C=1.0,
            penalty="l2",
            solver="lbfgs",
            max_iter=100,
        ),
        TRAIN_VAL_SPLIT=SimpleNamespace(
            test_size=0.5,
            random_state=42,
        ),
        DATASET_FULL_TEXT_COLUMN="full_text",
        DATASET_POLARITY_COLUMN="polarity",
        DATASET_PROCESSED_PATH=processed_path,
        MLFLOW_MODEL_NAME="sentiment_model",
    )


@pytest.fixture
def fake_mlflow_and_client(monkeypatch):
    """
    Patch mlflow and MlflowClient inside train module with fakes.
    Returns (fake_mlflow, fake_client, fake_cfg).
    """
    fake_mlflow = FakeMlflow()
    # patch mlflow module inside train
    monkeypatch.setattr(train, "mlflow", fake_mlflow, raising=True)

    # cfg is created per test, so we can pass its model_name to client
    fake_cfg = _make_fake_cfg(processed_path=None)
    monkeypatch.setattr(train, "cfg", fake_cfg, raising=True)

    fake_client = FakeMlflowClient(model_name=fake_cfg.MLFLOW_MODEL_NAME)
    monkeypatch.setattr(train, "MlflowClient", lambda: fake_client, raising=True)

    return fake_mlflow, fake_client, fake_cfg


# ---------------------------------------------------------------------------
# train() tests
# ---------------------------------------------------------------------------


def test_train_runs_pipeline_and_returns_model_uri(monkeypatch, fake_mlflow_and_client):
    fake_mlflow, fake_client, fake_cfg = fake_mlflow_and_client

    # Fake training DataFrame (already processed)
    df_fake = pd.DataFrame(
        {
            fake_cfg.DATASET_FULL_TEXT_COLUMN: ["text A", "text B", "text C", "text D"],
            fake_cfg.DATASET_POLARITY_COLUMN: [1, 0, 1, 0],
        }
    )

    # Don't hit real disk: override _get_train_data_frame
    def fake_get_train_data_frame(batches: list[int]) -> pd.DataFrame:
        # ensure batches is what we expect
        assert batches == [0, 1]
        return df_fake

    monkeypatch.setattr(
        train, "_get_train_data_frame", fake_get_train_data_frame, raising=True
    )

    # Replace _generate_pipeline with a very simple fake pipeline
    class FakePipeline:
        def __init__(self):
            self.fitted = False
            self.fit_args = None

        def fit(self, X, y):
            self.fitted = True
            self.fit_args = (list(X), list(y))

        def predict(self, X):
            # for simplicity, always predict 1
            return [1 for _ in X]

    monkeypatch.setattr(
        train, "_generate_pipeline", lambda: FakePipeline(), raising=True
    )

    # Fake validate: don't depend on sklearn
    class FakeValidationResult:
        def __init__(self, accuracy: float, f1_macro: float):
            self.accuracy = accuracy
            self.f1_macro = f1_macro

    def fake_validate(y_true, y_pred, split_name="val", log_report=False):
        # sanity check: shapes match
        assert len(y_true) == len(y_pred)
        return FakeValidationResult(accuracy=1.0, f1_macro=1.0)

    monkeypatch.setattr(train, "validate", fake_validate, raising=True)

    # Act
    model_uri = train.train(batches=[0, 1])

    # Assert: mlflow run name
    # A run should have been started called "train_model"
    # (we can't inspect directly run_name easily, but we can at least ensure
    # that active_run() is None after the context, meaning it was closed)
    assert fake_mlflow.active_run() is None

    # Assert: a model was logged via sklearn.log_model
    assert len(fake_mlflow.sklearn.logged_models) == 1
    _, artifact_path, registered_name = fake_mlflow.sklearn.logged_models[0]
    assert artifact_path == "model"
    assert registered_name == fake_cfg.MLFLOW_MODEL_NAME

    # Assert: Model registry interaction
    # search_model_versions was called and returns version "7"
    assert len(fake_client.search_queries) == 1
    assert "run_id = 'run-123'" in fake_client.search_queries[0]

    # Tags set on model version
    assert (
        "sentiment_model",
        "7",
        "experiment",
        "weekly_retraining",
    ) in fake_client.version_tags
    # batches_used tag via _generate_tags
    assert (
        "sentiment_model",
        "7",
        "batches_used",
        "[0, 1]",
    ) in fake_client.version_tags

    # Tags on the run itself
    assert fake_mlflow.tags["rows_train_total"] == len(df_fake)
    assert fake_mlflow.tags["batches_used"] == [0, 1]

    # Return value should be a models:/ URI pointing to our fake version
    assert model_uri == f"models:/{fake_cfg.MLFLOW_MODEL_NAME}/7"


# ---------------------------------------------------------------------------
# main() tests - argument parsing / wiring
# ---------------------------------------------------------------------------


def test_main_no_batches_auto_discovers_parquets_and_calls_train(tmp_path, monkeypatch):
    """
    When no --batches is provided, main() should auto-discover
    train_batch_*.parquet files and call train() with the sorted batch ids.
    """
    # Arrange: create fake train_batch_*.parquet files
    (tmp_path / "train_batch_0.parquet").touch()
    (tmp_path / "train_batch_2.parquet").touch()
    (tmp_path / "train_batch_1.parquet").touch()

    # Fake cfg with our tmp_path as DATASET_PROCESSED_PATH
    fake_cfg = _make_fake_cfg(processed_path=tmp_path)
    monkeypatch.setattr(train, "cfg", fake_cfg, raising=True)

    # Fake train() to observe the batches passed
    called = {}

    def fake_train(batches):
        called["batches"] = batches
        return "fake-model-uri"

    monkeypatch.setattr(train, "train", fake_train, raising=True)

    # Simulate CLI: no --batches argument
    monkeypatch.setattr(sys, "argv", ["prog"], raising=True)

    # Act
    result = train.main()

    # Assert
    # Files: 0,1,2  -> batches [0,1,2]
    assert called["batches"] == [0, 1, 2]
    assert result == "fake-model-uri"


def test_main_single_limit_builds_range_and_calls_train(monkeypatch):
    """
    When --batches is a single integer, e.g. 3,
    main() should call train with [0,1,2,3].
    """
    # Fake cfg (DATASET_PROCESSED_PATH not used in this branch)
    fake_cfg = _make_fake_cfg(processed_path=None)
    monkeypatch.setattr(train, "cfg", fake_cfg, raising=True)

    called = {}

    def fake_train(batches):
        called["batches"] = batches
        return "fake-uri"

    monkeypatch.setattr(train, "train", fake_train, raising=True)

    monkeypatch.setattr(sys, "argv", ["prog", "--batches", "3"], raising=True)

    result = train.main()

    assert called["batches"] == [0, 1, 2, 3]
    assert result == "fake-uri"


def test_main_explicit_list_calls_train(monkeypatch):
    """
    When --batches is a comma-separated list, e.g. "1,3,5",
    main() should pass [1,3,5] to train() and not return anything.
    """
    fake_cfg = _make_fake_cfg(processed_path=None)
    monkeypatch.setattr(train, "cfg", fake_cfg, raising=True)

    called = {}

    def fake_train(batches):
        called["batches"] = batches
        # main() does not return this branch; just ignore return.

    monkeypatch.setattr(train, "train", fake_train, raising=True)

    monkeypatch.setattr(sys, "argv", ["prog", "--batches", "1,3, 5"], raising=True)

    result = train.main()

    assert called["batches"] == [1, 3, 5]
    # This branch doesn't return explicit value
    assert result is None
