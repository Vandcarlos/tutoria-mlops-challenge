from pathlib import Path

import pytest

import src.api.model_loader as model_loader

# ---------------------------------------------------------------------------
# Fake mlflow stack
# ---------------------------------------------------------------------------


class FakeModel:
    def __init__(self, name: str = "fake-model"):
        self.name = name


class FakeSklearnSubmodule:
    def __init__(self):
        self.loaded_paths: list[str] = []

    def load_model(self, path: str):
        self.loaded_paths.append(path)
        return FakeModel(name=f"loaded-from-{path}")


class FakeArtifactsSubmodule:
    def __init__(self):
        self.download_calls: list[tuple[str, str]] = []

    def download_artifacts(self, artifact_uri: str, dst_path: str):
        self.download_calls.append((artifact_uri, dst_path))


class FakeMlflow:
    def __init__(self):
        self.tracking_uri: str | None = None
        self.sklearn = FakeSklearnSubmodule()
        self.artifacts = FakeArtifactsSubmodule()

    def set_tracking_uri(self, uri: str):
        self.tracking_uri = uri


@pytest.fixture
def fake_mlflow(monkeypatch):
    """
    Replace the mlflow object inside model_loader with a fake one.
    """
    fake = FakeMlflow()
    monkeypatch.setattr(model_loader, "mlflow", fake, raising=True)
    return fake


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _patch_config(
    monkeypatch,
    *,
    model_dir: Path,
    allow_download: bool,
    tracking_uri: str = "file:./mlruns",
    model_name: str = "sentiment-logreg-tfidf",
    model_version: str | None = None,
):
    """
    Patch config-like constants imported in model_loader.
    """
    monkeypatch.setattr(model_loader, "MODEL_DIR", model_dir, raising=True)
    monkeypatch.setattr(
        model_loader, "ALLOW_RUNTIME_MODEL_DOWNLOAD", allow_download, raising=True
    )
    monkeypatch.setattr(model_loader, "MLFLOW_TRACKING_URI", tracking_uri, raising=True)
    monkeypatch.setattr(model_loader, "MLFLOW_MODEL_NAME", model_name, raising=True)
    monkeypatch.setattr(
        model_loader, "MLFLOW_MODEL_VERSION", model_version, raising=True
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_load_model_uses_local_dir_when_not_empty(tmp_path, monkeypatch, fake_mlflow):
    """
    If MODEL_DIR exists and is not empty, load_model() must:
    - not call artifacts.download_artifacts
    - call sklearn.load_model with MODEL_DIR
    - return the model loaded from that path
    """
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    # create any file to make directory non-empty
    (model_dir / "dummy.bin").write_text("x")

    _patch_config(
        monkeypatch,
        model_dir=model_dir,
        allow_download=True,  # valor não importa aqui, pois nem chega a usar
    )

    # resolve_model_uri não deve ser chamado nesse cenário, mas vamos
    # ainda assim mockar por segurança: se for chamado, falha o teste
    def fake_resolve_model_uri(*args, **kwargs):
        raise AssertionError(
            "resolve_model_uri should not be called when local model exists"
        )

    monkeypatch.setattr(
        model_loader, "resolve_model_uri", fake_resolve_model_uri, raising=True
    )

    # Act
    model = model_loader.load_model()

    # Assert
    assert isinstance(model, FakeModel)
    # sklearn.load_model deve ter sido chamado uma vez com MODEL_DIR
    assert fake_mlflow.sklearn.loaded_paths == [str(model_dir)]
    # Nenhum download deve ter sido feito
    assert fake_mlflow.artifacts.download_calls == []
    # Tracking URI deve ter sido configurado
    assert fake_mlflow.tracking_uri == "file:./mlruns"


def test_load_model_raises_when_dir_empty_and_download_not_allowed(
    tmp_path, monkeypatch, fake_mlflow
):
    """
    If MODEL_DIR is empty and ALLOW_RUNTIME_MODEL_DOWNLOAD=False,
    load_model() must raise RuntimeError and not download anything.
    """
    model_dir = tmp_path / "model"
    model_dir.mkdir()  # empty dir

    _patch_config(
        monkeypatch,
        model_dir=model_dir,
        allow_download=False,
    )

    # resolve_model_uri e download_artifacts não devem ser chamados
    def fake_resolve_model_uri(*args, **kwargs):
        raise AssertionError(
            "resolve_model_uri should not be called when download is disabled"
        )

    monkeypatch.setattr(
        model_loader, "resolve_model_uri", fake_resolve_model_uri, raising=True
    )

    with pytest.raises(RuntimeError) as excinfo:
        model_loader.load_model()

    assert "ALLOW_RUNTIME_MODEL_DOWNLOAD=false" in str(excinfo.value)

    # Nenhum download
    assert fake_mlflow.artifacts.download_calls == []
    # sklearn.load_model também não deve ser chamado
    assert fake_mlflow.sklearn.loaded_paths == []


def test_load_model_downloads_and_then_loads_from_dir(
    tmp_path, monkeypatch, fake_mlflow
):
    """
    If MODEL_DIR is empty and ALLOW_RUNTIME_MODEL_DOWNLOAD=True,
    load_model() must:
    - resolve the model URI
    - call mlflow.artifacts.download_artifacts with that URI and MODEL_DIR
    - then load the model from MODEL_DIR via sklearn.load_model
    """
    model_dir = tmp_path / "model"
    model_dir.mkdir()  # empty at the start

    _patch_config(
        monkeypatch,
        model_dir=model_dir,
        allow_download=True,
        tracking_uri="http://mlflow:5000",
        model_name="my-sentiment-model",
        model_version="7",
    )

    # Fake resolve_model_uri
    def fake_resolve_model_uri(model_name: str, version: str | None):
        assert model_name == "my-sentiment-model"
        assert version == "7"
        return f"models:/{model_name}/{version}"

    monkeypatch.setattr(
        model_loader, "resolve_model_uri", fake_resolve_model_uri, raising=True
    )

    # Act
    model = model_loader.load_model()

    # Assert model returned
    assert isinstance(model, FakeModel)
    # Tracking URI
    assert fake_mlflow.tracking_uri == "http://mlflow:5000"

    # Download artifacts should have been called once
    assert len(fake_mlflow.artifacts.download_calls) == 1
    artifact_uri, dst_path = fake_mlflow.artifacts.download_calls[0]
    assert artifact_uri == "models:/my-sentiment-model/7"
    assert dst_path == str(model_dir)

    # And then load_model must have been called once with MODEL_DIR
    assert fake_mlflow.sklearn.loaded_paths == [str(model_dir)]
