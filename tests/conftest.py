from unittest.mock import MagicMock

import pytest

import mlflow


@pytest.fixture(autouse=True)
def cleanup_mlflow_runs():
    """
    Ensure there is no active MLflow run leaking between tests.
    """
    # deixa o teste rodar
    yield

    # teardown: encerra qualquer run que tenha sobrado
    while mlflow.active_run() is not None:
        mlflow.end_run()


@pytest.fixture
def model_version_factory():
    def _factory(version, stage=None, name="sentiment-logreg-tfidf"):
        mv = MagicMock()
        mv.version = str(version)
        mv.current_stage = stage
        mv.name = name
        return mv

    return _factory


@pytest.fixture
def datasets_dir_factory(tmp_path, monkeypatch):
    import src.model.config as cfg

    def _factory(cfg: cfg):
        batch_dir = tmp_path / "batches"
        raw_dir = tmp_path / "raw"
        batch_dir.mkdir()
        raw_dir.mkdir()

        # Patch the cfg values used by the module
        monkeypatch.setattr(cfg, "DATASET_BATCH_DIR", batch_dir, raising=True)
        monkeypatch.setattr(cfg, "DATASET_RAW_DIR", raw_dir, raising=True)

    return _factory
