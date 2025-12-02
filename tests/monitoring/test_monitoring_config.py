import importlib
from pathlib import Path

ENV_VARS = [
    "BASE_PATHMONITORING_LOOKBACK_DAYS",
    "ALLOW_RUNTIME_MODEL_DOWNLOAD",
    "TEST_DATA_PATH",
    "MODEL_PATH",
]


def _clear_monitoring_env(monkeypatch):
    """Helper to clear all monitoring-related env vars."""
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)


def test_config_uses_default_values_when_env_not_set(monkeypatch):
    """
    When no monitoring-related env vars are set, config must use
    the default paths and values defined in the module.
    """
    _clear_monitoring_env(monkeypatch)

    # Import and reload the module so it re-evaluates os.getenv calls
    import src.monitoring.config as cfg

    cfg = importlib.reload(cfg)

    expected_base_path = Path("./data/monitoring").resolve()
    assert cfg.BASE_PATH == expected_base_path
    assert cfg.MONITORING_BASE_PATH == expected_base_path / "predictions"
    assert cfg.MONITORING_OUTPUT_PATH == expected_base_path / "reports"

    # Defaults from the implementation
    assert (
        cfg.MONITORING_REPORT_PATH
        == expected_base_path / "reports/prediction_drift_report.html"
    )

    # LOOKBACK default
    assert isinstance(cfg.MONITORING_LOOKBACK_DAYS, int)
    assert cfg.MONITORING_LOOKBACK_DAYS == 7

    assert (
        cfg.REFERENCE_PREDICTIONS_PATH
        == expected_base_path / "reference_predictions.parquet"
    )

    assert cfg.TEST_DATA_PATH == Path("./data/processed/test.parquet").resolve()
    assert cfg.TEST_FULL_TEXT_COLUMN == "full_text"

    assert cfg.MODEL_PATH == Path("./data/model").resolve()


def test_config_reads_values_from_environment(monkeypatch, tmp_path):
    """
    When env vars are provided, config must respect them and resolve
    the paths from those values instead of the defaults.
    """
    _clear_monitoring_env(monkeypatch)

    # Create custom paths under tmp_path
    base_path = tmp_path / "custom_predictions"
    test_data_path = tmp_path / "test_proc.parquet"
    model_path = tmp_path / "custom_model"

    # Note: we don't need the files to exist; config only resolves paths.
    monkeypatch.setenv("BASE_PATH", str(base_path))
    monkeypatch.setenv("MONITORING_LOOKBACK_DAYS", "30")
    monkeypatch.setenv("TEST_DATA_PATH", str(test_data_path))
    monkeypatch.setenv("MODEL_PATH", str(model_path))

    import src.monitoring.config as cfg

    cfg = importlib.reload(cfg)

    assert cfg.BASE_PATH == base_path.resolve()
    assert cfg.MONITORING_LOOKBACK_DAYS == 30
    assert isinstance(cfg.MONITORING_LOOKBACK_DAYS, int)

    assert cfg.TEST_DATA_PATH == test_data_path.resolve()
    assert cfg.MODEL_PATH == model_path.resolve()
