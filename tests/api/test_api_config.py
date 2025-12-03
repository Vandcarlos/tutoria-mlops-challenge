import importlib
from pathlib import Path

import pytest

import src.api.config as config  # ajuste o path se estiver diferente


# --------------------------------------------------------------------
# Helper para recarregar o módulo com envs diferentes
# --------------------------------------------------------------------
def _reload_config(monkeypatch, **env_overrides):
    """
    Reload src.api.config applying a clean env for the keys it uses.

    Usage:
        cfg = _reload_config(monkeypatch, ENVIRONMENT="prod", MODEL_DIR="/tmp/model")
    """
    # Limpa as variáveis que o config usa
    for key in [
        "ENVIRONMENT",
        "MLFLOW_TRACKING_URI",
        "MLFLOW_MODEL_VERSION",
        "MODEL_PATH",
        "ALLOW_RUNTIME_MODEL_DOWNLOAD",
    ]:
        monkeypatch.delenv(key, raising=False)

    # Aplica overrides para este cenário de teste
    for k, v in env_overrides.items():
        monkeypatch.setenv(k, v)

    # Reimporta / recarrega o módulo
    import src.api.config as cfg

    return importlib.reload(cfg)


# --------------------------------------------------------------------
# Testes do helper _bool
# --------------------------------------------------------------------
def test_bool_returns_default_when_env_missing(monkeypatch):
    monkeypatch.delenv("SOME_FLAG", raising=False)
    # Usa o módulo já importado, não precisa recarregar
    assert config._bool("SOME_FLAG", default=True) is True
    assert config._bool("SOME_FLAG", default=False) is False


@pytest.mark.parametrize(
    "value,expected",
    [
        ("1", True),
        ("true", True),
        ("TRUE", True),
        ("yes", True),
        ("Y", True),
        ("0", False),
        ("false", False),
        ("no", False),
        ("n", False),
        ("", False),
        ("  true  ", True),
    ],
)
def test_bool_parses_common_truthy_and_falsy_values(monkeypatch, value, expected):
    monkeypatch.setenv("FLAG_TEST", value)
    assert config._bool("FLAG_TEST") is expected


def test_environment_default_is_local(monkeypatch):
    cfg = _reload_config(monkeypatch)
    assert cfg.ENVIRONMENT == "local"


def test_environment_can_be_overridden_by_env(monkeypatch):
    cfg = _reload_config(monkeypatch, ENVIRONMENT="prod")
    assert cfg.ENVIRONMENT == "prod"


def test_mlflow_defaults_when_env_not_set(monkeypatch):
    cfg = _reload_config(monkeypatch)
    assert cfg.MLFLOW_TRACKING_URI == "file:./mlruns"
    assert cfg.MLFLOW_MODEL_VERSION is None


def test_mlflow_env_overrides(monkeypatch):
    cfg = _reload_config(
        monkeypatch,
        MLFLOW_TRACKING_URI="http://mlflow:5000",
        MLFLOW_MODEL_VERSION="7",
    )
    assert cfg.MLFLOW_TRACKING_URI == "http://mlflow:5000"
    assert cfg.MLFLOW_MODEL_VERSION == "7"


def test_model_path_respects_env_and_is_resolved(monkeypatch, tmp_path):
    model_path_env = tmp_path / "custom_model_path"
    cfg = _reload_config(monkeypatch, MODEL_PATH=str(model_path_env))

    assert isinstance(cfg.MODEL_PATH, Path)
    # resolve() é chamado no código original
    assert cfg.MODEL_PATH == model_path_env.resolve()


def test_model_dir_default_is_data_model_relative(monkeypatch):
    cfg = _reload_config(monkeypatch)
    expected = Path("./data/model").resolve()
    assert cfg.MODEL_PATH == expected


def test_allow_runtime_model_download_default_true_for_local(monkeypatch):
    # ENVIRONMENT default = "local", e ALLOW_RUNTIME_MODEL_DOWNLOAD não setado
    cfg = _reload_config(monkeypatch)
    assert cfg.ENVIRONMENT == "local"
    assert cfg.ALLOW_RUNTIME_MODEL_DOWNLOAD is True


def test_allow_runtime_model_download_default_false_for_prod(monkeypatch):
    # Em prod, default deve ser False
    cfg = _reload_config(monkeypatch, ENVIRONMENT="prod")
    assert cfg.ENVIRONMENT == "prod"
    assert cfg.ALLOW_RUNTIME_MODEL_DOWNLOAD is False


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "Y"])
def test_allow_runtime_model_download_can_be_forced_true(monkeypatch, value):
    cfg = _reload_config(
        monkeypatch,
        ENVIRONMENT="prod",  # mesmo em prod
        ALLOW_RUNTIME_MODEL_DOWNLOAD=value,
    )
    assert cfg.ENVIRONMENT == "prod"
    assert cfg.ALLOW_RUNTIME_MODEL_DOWNLOAD is True


@pytest.mark.parametrize("value", ["0", "false", "FALSE", "no", "N", ""])
def test_allow_runtime_model_download_can_be_forced_false(monkeypatch, value):
    cfg = _reload_config(
        monkeypatch,
        ENVIRONMENT="local",  # mesmo em local
        ALLOW_RUNTIME_MODEL_DOWNLOAD=value,
    )
    assert cfg.ENVIRONMENT == "local"
    assert cfg.ALLOW_RUNTIME_MODEL_DOWNLOAD is False
