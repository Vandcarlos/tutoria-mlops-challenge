import importlib
from pathlib import Path

ENV_VARS = [
    "DATASET_LOCAL_PATH",
    "MONITORING_LOOKBACK_DAYS",
    "ALLOW_RUNTIME_MODEL_DOWNLOAD",
    "S3_DATA_BUCKET",
    "S3_DATA_PREFIX",
]


def _clear_monitoring_env(monkeypatch):
    """Helper para limpar todas as env vars usadas pelo módulo de config."""
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)


def test_config_uses_default_values_when_env_not_set(monkeypatch):
    """
    Quando nenhuma env var relevante está setada, o módulo deve usar
    os valores padrão definidos em código.
    """
    _clear_monitoring_env(monkeypatch)

    import src.monitoring.config as cfg

    cfg = importlib.reload(cfg)

    # DATASET_LOCAL_PATH padrão
    expected_dataset_path = Path("./data")
    assert cfg.DATASET_LOCAL_PATH == expected_dataset_path

    # Paths de monitoring derivados do DATASET_LOCAL_PATH
    expected_base_monitoring = expected_dataset_path / "monitoring"
    assert cfg.BASE_MONITORING_PATH == expected_base_monitoring
    assert cfg.MONITORING_PREDICTIONS_PATH == expected_base_monitoring / "predictions"
    assert cfg.MONITORING_REPORTS_FOLDER_PATH == expected_base_monitoring / "reports"
    assert (
        cfg.MONITORING_REPORT_PATH
        == expected_base_monitoring / "reports" / "prediction_drift_report.html"
    )

    # LOOKBACK padrão
    assert isinstance(cfg.MONITORING_LOOKBACK_DAYS, int)
    assert cfg.MONITORING_LOOKBACK_DAYS == 7

    # Caminho de referência
    assert (
        cfg.REFERENCE_PREDICTIONS_PATH
        == expected_base_monitoring / "reference_predictions.parquet"
    )

    # Colunas do dataset
    assert cfg.DATASET_POLARITY_COLUMN == "polarity"
    assert cfg.DATASET_TITLE_COLUMN == "title"
    assert cfg.DATASET_MESSAGE_COLUMN == "message"
    assert cfg.DATASET_FULL_TEXT_COLUMN == "full_text"

    # Caminhos de teste: hoje são absolutos, independentes do DATASET_LOCAL_PATH
    assert cfg.DATASET_RAW_TEST_PARQUET == Path("/raw/test.parquet")
    assert cfg.DATASET_PROCESSED_TEST_PATH == Path("/processed/test.parquet")

    # Modelo local
    assert cfg.MODEL_PATH == expected_dataset_path / "model"

    # Configuração S3 padrão
    assert cfg.S3_DATA_BUCKET is None
    assert cfg.USE_S3_DATA is False
    assert cfg.S3_DATA_KEY_PREFIX == "amazon-reviews"
    assert cfg.S3_DATA_KEY_MONITORING == "amazon-reviews/monitoring"
    assert (
        cfg.S3_DATA_KEY_MONITORING_PREDICTIONS
        == "amazon-reviews/monitoring/predictions"
    )
    assert cfg.S3_DATA_KEY_MONITORING_REPORTS == "amazon-reviews/monitoring/reports"
    assert (
        cfg.S3_DATA_KEY_MONITORING_REPORTS_ITEM
        == "amazon-reviews/monitoring/reports/prediction_drift_report.html"
    )
    assert (
        cfg.S3_DATA_KEY_MONITORING_REFERENCE
        == "amazon-reviews/monitoring/reference_predictions.parquet"
    )
    assert cfg.S3_DATA_KEY_RAW_TEST == "amazon-reviews/raw/test.parquet"
    assert cfg.S3_DATA_KEY_PROCESSED_TEST == "amazon-reviews/processed/test.parquet"

    # Flag de download em runtime padrão: False
    assert cfg.ALLOW_RUNTIME_MODEL_DOWNLOAD is False


def test_config_reads_values_from_environment(monkeypatch, tmp_path):
    """
    Quando env vars são fornecidas, o módulo deve respeitar esses valores
    em vez dos defaults.
    """
    _clear_monitoring_env(monkeypatch)

    # Custom base dataset path
    dataset_path = tmp_path / "custom_data"
    monkeypatch.setenv("DATASET_LOCAL_PATH", str(dataset_path))

    # Lookback customizado
    monkeypatch.setenv("MONITORING_LOOKBACK_DAYS", "30")

    # Habilita download em runtime via helper _bool (truthy)
    monkeypatch.setenv("ALLOW_RUNTIME_MODEL_DOWNLOAD", "1")

    # Configuração S3 customizada
    monkeypatch.setenv("S3_DATA_BUCKET", "my-bucket")
    monkeypatch.setenv("S3_DATA_PREFIX", "my-prefix")

    import src.monitoring.config as cfg

    cfg = importlib.reload(cfg)

    # DATASET_LOCAL_PATH a partir da env var
    assert cfg.DATASET_LOCAL_PATH == dataset_path

    # Monitoring derivado do dataset_path
    expected_base_monitoring = dataset_path / "monitoring"
    assert cfg.BASE_MONITORING_PATH == expected_base_monitoring
    assert cfg.MONITORING_PREDICTIONS_PATH == expected_base_monitoring / "predictions"
    assert cfg.MONITORING_REPORTS_FOLDER_PATH == expected_base_monitoring / "reports"
    assert (
        cfg.MONITORING_REPORT_PATH
        == expected_base_monitoring / "reports" / "prediction_drift_report.html"
    )
    assert (
        cfg.REFERENCE_PREDICTIONS_PATH
        == expected_base_monitoring / "reference_predictions.parquet"
    )

    # Lookback lido como int
    assert cfg.MONITORING_LOOKBACK_DAYS == 30
    assert isinstance(cfg.MONITORING_LOOKBACK_DAYS, int)

    # Caminhos de teste: continuam absolutos, independentes da env
    assert cfg.DATASET_RAW_TEST_PARQUET == Path("/raw/test.parquet")
    assert cfg.DATASET_PROCESSED_TEST_PATH == Path("/processed/test.parquet")

    # Modelo local acompanhando o dataset_path
    assert cfg.MODEL_PATH == dataset_path / "model"

    # Flags e S3
    assert cfg.ALLOW_RUNTIME_MODEL_DOWNLOAD is True
    assert cfg.S3_DATA_BUCKET == "my-bucket"
    assert cfg.USE_S3_DATA is True

    assert cfg.S3_DATA_KEY_PREFIX == "my-prefix"
    assert cfg.S3_DATA_KEY_MONITORING == "my-prefix/monitoring"
    assert cfg.S3_DATA_KEY_MONITORING_PREDICTIONS == "my-prefix/monitoring/predictions"
    assert cfg.S3_DATA_KEY_MONITORING_REPORTS == "my-prefix/monitoring/reports"
    assert (
        cfg.S3_DATA_KEY_MONITORING_REPORTS_ITEM
        == "my-prefix/monitoring/reports/prediction_drift_report.html"
    )
    assert (
        cfg.S3_DATA_KEY_MONITORING_REFERENCE
        == "my-prefix/monitoring/reference_predictions.parquet"
    )
    assert cfg.S3_DATA_KEY_RAW_TEST == "my-prefix/raw/test.parquet"
    assert cfg.S3_DATA_KEY_PROCESSED_TEST == "my-prefix/processed/test.parquet"


def test_bool_helper_interprets_truthy_and_falsy(monkeypatch):
    """
    Garante que o helper _bool interprete corretamente valores truthy/falsy
    e respeite o default quando a env não existe.
    """
    import src.monitoring.config as cfg

    # Sem env var: usa o default
    monkeypatch.delenv("FLAG_X", raising=False)
    assert cfg._bool("FLAG_X", default=True) is True
    assert cfg._bool("FLAG_X", default=False) is False

    # Valores explicitamente falsos
    for value in ["0", "false", "False", "no", "NO", "n", "N", ""]:
        monkeypatch.setenv("FLAG_X", value)
        assert cfg._bool("FLAG_X", default=True) is False

    # Valores explicitamente verdadeiros
    for value in ["1", "true", "True", "YES", "yes", "y", "Y"]:
        monkeypatch.setenv("FLAG_X", value)
        assert cfg._bool("FLAG_X", default=False) is True
