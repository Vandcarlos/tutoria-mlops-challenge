"""
Tests for the src.config module.

These tests ensure that:
- environment-based settings are correctly resolved;
- path constants are built as expected;
- dataclass-based configurations have the expected defaults.
"""

from importlib import reload
from pathlib import Path

import src.model.config as config_module


def _reload_config(monkeypatch, env: dict[str, str] | None = None):
    """
    Helper to reload the config module with a controlled environment.

    It clears relevant environment variables first, then applies
    the ones provided in `env`.
    """
    # Clean all relevant env vars
    for key in [
        "DATASET_LOCAL_PATH",
        "DATASET_SPLIT_COUNT",
        "DATASET_KAGGLE_NAME",
        "DATASET_TRAIN",
        "DATASET_TEST",
        "MLFLOW_MODEL_NAME",
    ]:
        monkeypatch.delenv(key, raising=False)

    # Apply overrides
    env = env or {}
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    # Reload the module so top-level constants are recomputed
    return reload(config_module)


# ---------------------------------------------------------------------------
# Dataset paths and split count
# ---------------------------------------------------------------------------


def test_dataset_default_paths(monkeypatch):
    """Default dataset paths should be relative to ./data when no env is set."""
    cfg = _reload_config(monkeypatch)

    assert cfg.DATASET_LOCAL_PATH == Path("./data")
    assert cfg.DATASET_RAW_DIR == cfg.DATASET_LOCAL_PATH / "raw"
    assert cfg.DATASET_PROCESSED_DIR == cfg.DATASET_LOCAL_PATH / "processed"
    assert cfg.DATASET_BATCH_DIR == cfg.DATASET_LOCAL_PATH / "batches"


def test_dataset_local_path_from_env(monkeypatch):
    """DATASET_LOCAL_PATH should respect the environment variable override."""
    cfg = _reload_config(
        monkeypatch,
        env={"DATASET_LOCAL_PATH": "/tmp/custom-data"},
    )

    assert cfg.DATASET_LOCAL_PATH == Path("/tmp/custom-data")
    assert cfg.DATASET_RAW_DIR == Path("/tmp/custom-data/raw")
    assert cfg.DATASET_PROCESSED_DIR == Path("/tmp/custom-data/processed")
    assert cfg.DATASET_BATCH_DIR == Path("/tmp/custom-data/batches")


def test_dataset_split_count_default_and_env(monkeypatch):
    """DATASET_SPLIT_COUNT should default to 10 and accept an env override."""
    cfg_default = _reload_config(monkeypatch)
    assert cfg_default.DATASET_SPLIT_COUNT == 10

    cfg_overridden = _reload_config(
        monkeypatch,
        env={"DATASET_SPLIT_COUNT": "5"},
    )
    assert cfg_overridden.DATASET_SPLIT_COUNT == 5


# ---------------------------------------------------------------------------
# Kaggle dataset constants
# ---------------------------------------------------------------------------


def test_kaggle_constants_are_hardcoded(monkeypatch):
    """
    Kaggle settings should end up with the hardcoded values,
    regardless of environment variables (due to the second assignment block).
    """
    cfg = _reload_config(
        monkeypatch,
        env={
            "DATASET_KAGGLE_NAME": "someone/else-dataset",
            "DATASET_TRAIN": "train_alt.csv",
            "DATASET_TEST": "test_alt.csv",
        },
    )

    # Final values are the hardcoded constants from the module.
    assert cfg.KAGGLE_DATASET_NAME == "kritanjalijain/amazon-reviews"
    assert cfg.KAGGLE_DATASET_TRAIN_FILENAME == "train.csv"
    assert cfg.KAGGLE_DATASET_TEST_FILENAME == "test.csv"


# ---------------------------------------------------------------------------
# MLflow settings
# ---------------------------------------------------------------------------


def test_mlflow_model_name_default_and_env(monkeypatch):
    """MLFLOW_MODEL_NAME should default to the expected value and respect env override."""
    cfg_default = _reload_config(monkeypatch)
    assert cfg_default.MLFLOW_MODEL_NAME == "sentiment-logreg-tfidf"

    cfg_overridden = _reload_config(
        monkeypatch,
        env={"MLFLOW_MODEL_NAME": "another-model-name"},
    )
    assert cfg_overridden.MLFLOW_MODEL_NAME == "another-model-name"


# ---------------------------------------------------------------------------
# Dataset columns
# ---------------------------------------------------------------------------


def test_dataset_column_names(monkeypatch):
    """Dataset column constants should be stable and explicit."""
    cfg = _reload_config(monkeypatch)

    assert cfg.DATASET_POLARITY_COLUMN == "polarity"
    assert cfg.DATASET_TITLE_COLUMN == "title"
    assert cfg.DATASET_MESSAGE_COLUMN == "message"
    assert cfg.DATASET_FULL_TEXT_COLUMN == "full_text"


# ---------------------------------------------------------------------------
# Dataclasses and config instances
# ---------------------------------------------------------------------------


def test_tfidf_params_defaults(monkeypatch):
    """TfidfParams dataclass and TFIDF_PARAMS instance must share the same defaults."""
    cfg = _reload_config(monkeypatch)

    # Check dataclass defaults
    tfidf_default = cfg.TfidfParams()
    assert tfidf_default.max_features == 50_000
    assert tfidf_default.min_df == 2
    assert tfidf_default.ngram_range == (1, 2)

    # Check instantiated constant
    assert cfg.TFIDF_PARAMS.max_features == 50_000
    assert cfg.TFIDF_PARAMS.min_df == 2
    assert cfg.TFIDF_PARAMS.ngram_range == (1, 2)


def test_clf_params_defaults(monkeypatch):
    """ClfParams dataclass and CLF_PARAMS instance must share the same defaults."""
    cfg = _reload_config(monkeypatch)

    clf_default = cfg.ClfParams()
    assert clf_default.C == 10.0
    assert clf_default.penalty == "l2"
    assert clf_default.solver == "lbfgs"
    assert clf_default.max_iter == 2000

    assert cfg.CLF_PARAMS.C == 10.0
    assert cfg.CLF_PARAMS.penalty == "l2"
    assert cfg.CLF_PARAMS.solver == "lbfgs"
    assert cfg.CLF_PARAMS.max_iter == 2000


def test_train_val_split_defaults(monkeypatch):
    """TrainValSplit dataclass and TRAIN_VAL_SPLIT instance must share the same defaults."""
    cfg = _reload_config(monkeypatch)

    split_default = cfg.TrainValSplit()
    assert split_default.test_size == 0.2
    assert split_default.random_state == 42

    assert cfg.TRAIN_VAL_SPLIT.test_size == 0.2
    assert cfg.TRAIN_VAL_SPLIT.random_state == 42
