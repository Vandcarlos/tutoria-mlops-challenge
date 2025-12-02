from pathlib import Path

import pytest

import src.shared.model_resolver as model_resolver

# -------------------------------------------------------------------
# Helpers / Fakes
# -------------------------------------------------------------------


class DummyModelVersion:
    def __init__(self, name: str, version: str, current_stage: str | None):
        self.name = name
        self.version = version
        self.current_stage = current_stage


class FakeModel:
    def __init__(self, name: str = "fake-model"):
        self.name = name


class FakeSklearnSubmodule:
    def __init__(self) -> None:
        self.loaded_paths: list[str] = []

    def load_model(self, path: str) -> FakeModel:
        self.loaded_paths.append(path)
        return FakeModel(name=f"loaded-from-{path}")


class FakeArtifactsSubmodule:
    def __init__(self) -> None:
        self.download_calls: list[tuple[str, str]] = []

    def download_artifacts(self, artifact_uri: str, dst_path: str) -> None:
        self.download_calls.append((artifact_uri, dst_path))


class FakeMlflow:
    """
    Minimal fake mlflow module used in load_model tests.
    """

    def __init__(self) -> None:
        # Mantemos esse atributo só para compatibilidade, mesmo não sendo usado
        self.tracking_uri: str | None = None
        self.sklearn = FakeSklearnSubmodule()
        self.artifacts = FakeArtifactsSubmodule()

    def set_tracking_uri(self, uri: str) -> None:
        # Hoje o código real não chama isso, então não será utilizado,
        # mas deixamos aqui para não quebrar caso no futuro você volte a usar.
        self.tracking_uri = uri


@pytest.fixture
def fake_mlflow(monkeypatch) -> FakeMlflow:
    """
    Replace model_resolver.mlflow by a lightweight fake that lets us assert:
    - which paths were loaded
    - which artifacts were downloaded
    """
    fake = FakeMlflow()
    monkeypatch.setattr(model_resolver, "mlflow", fake, raising=True)
    return fake


@pytest.fixture
def model_version_factory():
    """
    Factory to build DummyModelVersion with defaults aligned
    to the module's constants.
    """

    def _factory(
        version: str,
        stage: str | None,
        name: str | None = None,
    ) -> DummyModelVersion:
        return DummyModelVersion(
            name=name or model_resolver.MODEL_NAME,
            version=version,
            current_stage=stage,
        )

    return _factory


# -------------------------------------------------------------------
# Tests for resolve_model_uri
# -------------------------------------------------------------------


def test_resolve_model_uri_with_explicit_version_does_not_call_client(monkeypatch):
    """
    If version is explicitly provided, resolve_model_uri must return
    models:/<MODEL_NAME>/<version> and must NOT call MlflowClient().
    """

    def fake_client_factory(*args, **kwargs):
        raise AssertionError("MlflowClient should not be called when version is set")

    monkeypatch.setattr(
        model_resolver, "MlflowClient", fake_client_factory, raising=True
    )

    uri = model_resolver.resolve_model_uri(version="7")
    assert uri == f"models:/{model_resolver.MODEL_NAME}/7"


def test_resolve_model_uri_picks_highest_production_version(
    monkeypatch, model_version_factory
):
    """
    When no version is given, the resolver should:
    - fetch all versions
    - select those in DEFAIULT_STAGE ("Production")
    - pick the highest numeric version among them
    """

    mock_versions: list[DummyModelVersion] = [
        model_version_factory("1", "Production"),
        model_version_factory("2", "Staging"),
        model_version_factory("5", "Production"),
        model_version_factory("3", None),
    ]

    class FakeClient:
        def search_model_versions(self, query: str):
            self.query = query
            return mock_versions

    monkeypatch.setattr(
        model_resolver, "MlflowClient", lambda: FakeClient(), raising=True
    )

    uri = model_resolver.resolve_model_uri(version=None)
    assert uri == f"models:/{model_resolver.MODEL_NAME}/5"


def test_resolve_model_uri_falls_back_to_latest_when_no_production(
    monkeypatch, model_version_factory, capsys
):
    """
    If there are no versions in the DEFAIULT_STAGE, resolver must pick
    the highest numeric version overall and log a message to stderr.
    """

    mock_versions = [
        model_version_factory("1", "Staging"),
        model_version_factory("3", None),
        model_version_factory("10", None),
    ]

    class FakeClient:
        def search_model_versions(self, query: str):
            self.query = query
            return mock_versions

    monkeypatch.setattr(
        model_resolver, "MlflowClient", lambda: FakeClient(), raising=True
    )

    uri = model_resolver.resolve_model_uri(version=None)
    assert uri == f"models:/{model_resolver.MODEL_NAME}/10"

    # Optional: check that something was printed to stderr
    captured = capsys.readouterr()
    assert "Auto-selected latest version: v10" in captured.err


def test_resolve_model_uri_raises_when_no_versions(monkeypatch):
    """
    If MlflowClient.search_model_versions returns an empty list,
    resolve_model_uri must raise RuntimeError.
    """

    class FakeClient:
        def search_model_versions(self, query: str):
            self.query = query
            return []

    monkeypatch.setattr(
        model_resolver, "MlflowClient", lambda: FakeClient(), raising=True
    )

    with pytest.raises(RuntimeError):
        model_resolver.resolve_model_uri(version=None)


# -------------------------------------------------------------------
# Tests for load_model
# -------------------------------------------------------------------


def test_load_model_uses_local_directory_when_not_empty(
    tmp_path, monkeypatch, fake_mlflow
):
    """
    If model_local_path exists and is not empty, load_model must:
    - NOT call resolve_model_uri
    - NOT download artifacts
    - load model directly from local path via mlflow.sklearn.load_model
    """

    model_dir: Path = tmp_path / "model"
    model_dir.mkdir()
    # create a dummy file so the directory is considered non-empty
    (model_dir / "dummy.bin").write_text("x")

    # Ensure resolve_model_uri is NOT used
    def fake_resolve_model_uri(*args, **kwargs):
        raise AssertionError("resolve_model_uri should not be called for non-empty dir")

    monkeypatch.setattr(
        model_resolver, "resolve_model_uri", fake_resolve_model_uri, raising=True
    )

    model = model_resolver.load_model(
        model_local_path=model_dir,
        allow_runtime_model_download=True,  # should be ignored because directory is not empty
    )

    # Assertions
    assert isinstance(model, FakeModel)
    assert fake_mlflow.sklearn.loaded_paths == [str(model_dir)]
    assert fake_mlflow.artifacts.download_calls == []


def test_load_model_raises_when_dir_empty_and_download_not_allowed(
    tmp_path, monkeypatch, fake_mlflow
):
    """
    If directory is empty and allow_runtime_model_download=False,
    load_model must raise RuntimeError and NOT call resolve_model_uri
    or download artifacts.
    """

    model_dir: Path = tmp_path / "model"
    model_dir.mkdir()  # empty

    def fake_resolve_model_uri(*args, **kwargs):
        raise AssertionError("resolve_model_uri should not be called")

    monkeypatch.setattr(
        model_resolver, "resolve_model_uri", fake_resolve_model_uri, raising=True
    )

    with pytest.raises(RuntimeError):
        model_resolver.load_model(
            model_local_path=model_dir,
            allow_runtime_model_download=False,
        )

    # No download, no load
    assert fake_mlflow.artifacts.download_calls == []
    assert fake_mlflow.sklearn.loaded_paths == []


def test_load_model_downloads_and_loads_when_allowed(
    tmp_path, monkeypatch, fake_mlflow
):
    """
    If directory is empty and allow_runtime_model_download=True, load_model must:
    - call resolve_model_uri(version=...)
    - download artifacts to the local directory
    - load the model from that local directory
    """

    model_dir: Path = tmp_path / "model"
    model_dir.mkdir()  # empty at start

    # Fake resolve_model_uri to assert arguments and return a fixed URI
    called: dict[str, str | None] = {}

    def fake_resolve_model_uri(version: str | None) -> str:
        called["version"] = version
        return "models:/my-sentiment-model/7"

    monkeypatch.setattr(
        model_resolver, "resolve_model_uri", fake_resolve_model_uri, raising=True
    )

    model = model_resolver.load_model(
        model_local_path=model_dir,
        version="7",
        allow_runtime_model_download=True,
    )

    # Model was returned
    assert isinstance(model, FakeModel)

    # resolve_model_uri was called with the given version
    assert called["version"] == "7"

    # Artifacts were downloaded exactly once
    assert len(fake_mlflow.artifacts.download_calls) == 1
    artifact_uri, dst_path = fake_mlflow.artifacts.download_calls[0]
    assert artifact_uri == "models:/my-sentiment-model/7"
    assert dst_path == str(model_dir)

    # And the local loader was used once with model_dir
    assert fake_mlflow.sklearn.loaded_paths == [str(model_dir)]
