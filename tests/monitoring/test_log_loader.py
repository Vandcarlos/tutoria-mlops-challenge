from datetime import UTC, datetime, timedelta
import json
from pathlib import Path

import pandas as pd

from src.monitoring import log_loader


def test_load_prediction_logs_returns_empty_when_base_path_not_exists(
    monkeypatch, tmp_path
):
    """
    Quando MONITORING_PREDICTIONS_PATH não existe, deve retornar DataFrame vazio.
    E, com USE_S3_DATA = False, não deve tentar baixar nada do S3.
    """
    base_path = tmp_path / "does_not_exist"

    monkeypatch.setattr(log_loader, "MONITORING_PREDICTIONS_PATH", base_path)
    monkeypatch.setattr(log_loader, "USE_S3_DATA", False)

    def _fake_download_folder_from_s3(**_kwargs):
        raise AssertionError("download_folder_from_s3 não deveria ser chamado")

    monkeypatch.setattr(
        log_loader, "download_folder_from_s3", _fake_download_folder_from_s3
    )

    df = log_loader.load_prediction_logs_local()

    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_load_prediction_logs_returns_empty_when_no_files_found(monkeypatch, tmp_path):
    """
    Quando a pasta existe mas não há arquivos JSON de log,
    deve retornar DataFrame vazio.
    """
    base_path = tmp_path / "monitoring" / "predictions"
    base_path.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(log_loader, "MONITORING_PREDICTIONS_PATH", base_path)
    monkeypatch.setattr(log_loader, "USE_S3_DATA", False)

    def _fake_download_folder_from_s3(**_kwargs):
        raise AssertionError("download_folder_from_s3 não deveria ser chamado")

    monkeypatch.setattr(
        log_loader, "download_folder_from_s3", _fake_download_folder_from_s3
    )

    df = log_loader.load_prediction_logs_local()

    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_load_prediction_logs_triggers_s3_download_when_enabled(monkeypatch, tmp_path):
    """
    Quando USE_S3_DATA = True, deve chamar download_folder_from_s3 com os
    parâmetros corretos antes de ler os arquivos locais.
    """
    base_path = tmp_path / "monitoring" / "predictions"
    base_path.mkdir(parents=True, exist_ok=True)

    bucket_name = "my-bucket"
    folder_key = "amazon-reviews/monitoring/predictions"

    monkeypatch.setattr(log_loader, "MONITORING_PREDICTIONS_PATH", base_path)
    monkeypatch.setattr(log_loader, "S3_DATA_BUCKET", bucket_name)
    monkeypatch.setattr(log_loader, "S3_DATA_KEY_MONITORING_PREDICTIONS", folder_key)
    monkeypatch.setattr(log_loader, "USE_S3_DATA", True)

    called = {"value": False}

    def _fake_download_folder_from_s3(bucket, folder_key, folder_path):
        called["value"] = True
        assert bucket == bucket_name
        assert folder_key == folder_key
        assert folder_path == base_path

    monkeypatch.setattr(
        log_loader, "download_folder_from_s3", _fake_download_folder_from_s3
    )

    # Sem arquivos, o resultado final ainda é DataFrame vazio,
    # mas o objetivo aqui é garantir que o download foi chamado.
    df = log_loader.load_prediction_logs_local()

    assert called["value"] is True
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def _write_log_file(
    base_path: Path, date_dir: str, filename: str, payload: dict
) -> Path:
    """Helper para escrever um JSON de log no layout esperado."""
    date_path = base_path / f"date={date_dir}"
    date_path.mkdir(parents=True, exist_ok=True)
    file_path = date_path / filename
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)
    return file_path


def test_load_prediction_logs_filters_by_lookback_and_parses_payload(
    monkeypatch, tmp_path
):
    """
    Deve:
    - ler arquivos JSON sob MONITORING_PREDICTIONS_PATH/date=YYYY-MM-DD;
    - aplicar filtro por MONITORING_LOOKBACK_DAYS usando o campo 'timestamp';
    - montar o DataFrame com todas as colunas esperadas;
    - converter 'timestamp' para datetime64[ns].
    """
    base_path = tmp_path / "monitoring" / "predictions"
    base_path.mkdir(parents=True, exist_ok=True)

    # Fixamos um "agora" para o módulo, via monkeypatch do datetime.
    base_now = datetime(2024, 1, 10, tzinfo=UTC)
    monkeypatch.setattr(log_loader, "MONITORING_PREDICTIONS_PATH", base_path)
    monkeypatch.setattr(log_loader, "MONITORING_LOOKBACK_DAYS", 7)
    monkeypatch.setattr(log_loader, "USE_S3_DATA", False)

    class FixedDateTime(datetime):  # type: ignore[misc]
        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return base_now.replace(tzinfo=None)
            return base_now

        def fromisoformat(date_string):
            return datetime.fromisoformat(date_string)

    # substitui a referência 'datetime' importada no módulo
    monkeypatch.setattr(log_loader, "datetime", FixedDateTime)

    # Evento recente (dentro da janela de 7 dias)
    recent_ts = base_now - timedelta(days=2)

    recent_payload = {
        "timestamp": recent_ts.isoformat(),
        "input": {
            "title": "T",
            "text": "M",
            "full_text": "T M",
        },
        "output": {
            "predicted_label": 1,
            "predicted_label_name": "POSITIVE",
            "confidence": 0.9,
        },
        "latency_ms": 10.0,
    }

    _write_log_file(
        base_path=base_path,
        date_dir="2024-01-08",
        filename="prediction_recent.json",
        payload=recent_payload,
    )

    # Evento antigo (fora da janela de 7 dias) – deve ser filtrado
    old_ts = base_now - timedelta(days=10)
    old_payload = {
        "timestamp": old_ts.isoformat(),
        "input": {
            "title": "OLD",
            "text": "MSG",
            "full_text": "OLD MSG",
        },
        "output": {
            "predicted_label": 2,
            "predicted_label_name": "NEGATIVE",
            "confidence": 0.1,
        },
        "latency_ms": 50.0,
    }

    _write_log_file(
        base_path=base_path,
        date_dir="2024-01-01",
        filename="prediction_old.json",
        payload=old_payload,
    )

    def _fake_download_folder_from_s3(**_kwargs):
        raise AssertionError("download_folder_from_s3 não deveria ser chamado")

    monkeypatch.setattr(
        log_loader, "download_folder_from_s3", _fake_download_folder_from_s3
    )

    df = log_loader.load_prediction_logs_local()

    # Só o evento recente deve ter sido mantido
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1

    row = df.iloc[0]

    assert row["title"] == "T"
    assert row["text"] == "M"
    assert row["full_text"] == "T M"
    assert row["predicted_label"] == 1
    assert row["predicted_label_name"] == "POSITIVE"
    assert row["confidence"] == 0.9
    assert row["latency_ms"] == 10.0

    # timestamp deve ser datetime64[ns], convertido a partir de epoch em ms
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])

    expected_recent_ts = datetime.fromtimestamp(recent_ts.timestamp(), tz=UTC)
    # pandas tende a devolver datetime "naive"; normalizamos para comparar
    assert row["timestamp"].to_pydatetime().replace(tzinfo=UTC) == expected_recent_ts


def test_load_prediction_logs_returns_empty_when_all_events_older_than_lookback(
    monkeypatch, tmp_path
):
    """
    Caso todos os eventos estejam fora da janela de MONITORING_LOOKBACK_DAYS,
    a função deve retornar DataFrame vazio (branch do `if not events:`).
    """
    base_path = tmp_path / "monitoring" / "predictions"
    base_path.mkdir(parents=True, exist_ok=True)

    base_now = datetime(2024, 1, 10, tzinfo=UTC)
    monkeypatch.setattr(log_loader, "MONITORING_PREDICTIONS_PATH", base_path)
    monkeypatch.setattr(log_loader, "MONITORING_LOOKBACK_DAYS", 7)
    monkeypatch.setattr(log_loader, "USE_S3_DATA", False)

    class FixedDateTime(datetime):  # type: ignore[misc]
        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return base_now.replace(tzinfo=None)
            return base_now

        def fromisoformat(date: str) -> datetime:
            return datetime(2023, 1, 10, tzinfo=UTC)

    monkeypatch.setattr(log_loader, "datetime", FixedDateTime)

    old_ts = base_now - timedelta(days=30)
    old_ts_ms = int(old_ts.timestamp() * 1000)

    payload = {
        "timestamp": old_ts_ms,
        "input": {
            "title": "OLD",
            "text": "MSG",
            "full_text": "OLD MSG",
        },
        "output": {
            "predicted_label": 2,
            "predicted_label_name": "NEGATIVE",
            "confidence": 0.1,
        },
        "latency_ms": 50.0,
    }

    _write_log_file(
        base_path=base_path,
        date_dir="2023-12-11",
        filename="prediction_old.json",
        payload=payload,
    )

    def _fake_download_folder_from_s3(**_kwargs):
        raise AssertionError("download_folder_from_s3 não deveria ser chamado")

    monkeypatch.setattr(
        log_loader, "download_folder_from_s3", _fake_download_folder_from_s3
    )

    df = log_loader.load_prediction_logs_local()

    assert isinstance(df, pd.DataFrame)
    assert df.empty
