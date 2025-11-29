from unittest.mock import patch

import pytest

from src.shared.model_resolver import resolve_model_uri

# ----------------------------
# Tests
# ----------------------------


def test_explicit_version_argument_overrides_everything():
    uri = resolve_model_uri(model_name="mymodel", version="7")
    assert uri == "models:/mymodel/7"


def test_version_from_env(monkeypatch):
    monkeypatch.setenv("MLFLOW_MODEL_VERSION", "4")

    uri = resolve_model_uri(model_name="modelx")
    assert uri == "models:/modelx/4"


def test_model_name_from_env(monkeypatch, model_version_factory):
    monkeypatch.setenv("MLFLOW_MODEL_NAME", "env_model")

    with patch("src.shared.model_resolver.MlflowClient") as client:
        client.return_value.search_model_versions.return_value = [
            model_version_factory("1", "Production", "env_model")
        ]
        uri = resolve_model_uri()
    assert uri == "models:/env_model/1"


def test_resolves_highest_production_version(model_version_factory):
    mock_versions = [
        model_version_factory("1", "Production", name="sentiment"),
        model_version_factory("2", "Staging", name="sentiment"),
        model_version_factory("5", "Production", name="sentiment"),
        model_version_factory("3", None, name="sentiment"),
    ]

    with patch("src.shared.model_resolver.MlflowClient") as client:
        client.return_value.search_model_versions.return_value = mock_versions
        uri = resolve_model_uri(model_name="sentiment")

    assert uri == "models:/sentiment/5"


def test_resolves_latest_when_no_production(model_version_factory):
    mock_versions = [
        model_version_factory("1", "Staging", name="sentiment"),
        model_version_factory("3", None, name="sentiment"),
        model_version_factory("10", None, name="sentiment"),
    ]

    with patch("src.shared.model_resolver.MlflowClient") as client:
        client.return_value.search_model_versions.return_value = mock_versions
        uri = resolve_model_uri(model_name="sentiment")

    assert uri == "models:/sentiment/10"


def test_no_versions_raises_error():
    with patch("src.shared.model_resolver.MlflowClient") as client:
        client.return_value.search_model_versions.return_value = []
        with pytest.raises(RuntimeError):
            resolve_model_uri("anymodel")
