from pathlib import Path
from types import SimpleNamespace

import pytest


def _setup_fake_kaggle_dir(tmp_path, ingest_module) -> Path:
    """
    Create a fake Kaggle download directory with train/test files
    matching the filenames expected by the config used in ingest.
    """
    dataset_dir = tmp_path / "kaggle_download"
    dataset_dir.mkdir()

    train_name = ingest_module.cfg.KAGGLE_DATASET_TRAIN_FILENAME
    test_name = ingest_module.cfg.KAGGLE_DATASET_TEST_FILENAME

    (dataset_dir / train_name).write_text("train-data")
    (dataset_dir / test_name).write_text("test-data")

    return dataset_dir


def test_ingest_happy_path_copies_files_to_raw_dir(tmp_path, monkeypatch):
    """
    ingest() must:
    - create DATASET_RAW_DIR
    - copy train/test from Kaggle download dir
    - return the destination paths
    """
    from src.model.data import ingest as ingest_module

    # Redireciona o RAW para um tmp de teste
    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(ingest_module.cfg, "DATASET_RAW_DIR", raw_dir)

    # Cria um diretório fake como se fosse o download do Kaggle
    dataset_dir = _setup_fake_kaggle_dir(tmp_path, ingest_module)

    # Mock do kagglehub.dataset_download para apontar pro nosso diretório fake
    def fake_dataset_download(dataset_name: str) -> str:
        return str(dataset_dir)

    fake_kagglehub = SimpleNamespace(dataset_download=fake_dataset_download)
    monkeypatch.setattr(ingest_module, "kagglehub", fake_kagglehub)

    # Executa
    result = ingest_module.ingest()

    train_name = ingest_module.cfg.KAGGLE_DATASET_TRAIN_FILENAME
    test_name = ingest_module.cfg.KAGGLE_DATASET_TEST_FILENAME

    expected_train = raw_dir / train_name
    expected_test = raw_dir / test_name

    # Verifica paths retornados
    assert result["train"] == expected_train
    assert result["test"] == expected_test

    # Verifica que os arquivos foram copiados
    assert expected_train.read_text() == "train-data"
    assert expected_test.read_text() == "test-data"

    # Verifica que o diretório foi criado
    assert expected_train.parent == raw_dir
    assert raw_dir.exists()


def test_ingest_raises_if_train_missing(tmp_path, monkeypatch):
    """
    Se o arquivo de train não existir no diretório baixado,
    ingest() deve levantar FileNotFoundError.
    """
    from src.model.data import ingest as ingest_module

    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(ingest_module.cfg, "DATASET_RAW_DIR", raw_dir)

    dataset_dir = tmp_path / "kaggle_download"
    dataset_dir.mkdir()

    # Só cria o test, falta o train
    test_name = ingest_module.cfg.KAGGLE_DATASET_TEST_FILENAME
    (dataset_dir / test_name).write_text("test-data")

    def fake_dataset_download(dataset_name: str) -> str:
        return str(dataset_dir)

    fake_kagglehub = SimpleNamespace(dataset_download=fake_dataset_download)
    monkeypatch.setattr(ingest_module, "kagglehub", fake_kagglehub)

    with pytest.raises(FileNotFoundError) as exc:
        ingest_module.ingest()

    assert "Train file not found" in str(exc.value)


def test_ingest_raises_if_test_missing(tmp_path, monkeypatch):
    """
    Se o arquivo de test não existir no diretório baixado,
    ingest() deve levantar FileNotFoundError.
    """
    from src.model.data import ingest as ingest_module

    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(ingest_module.cfg, "DATASET_RAW_DIR", raw_dir)

    dataset_dir = tmp_path / "kaggle_download"
    dataset_dir.mkdir()

    # Só cria o train, falta o test
    train_name = ingest_module.cfg.KAGGLE_DATASET_TRAIN_FILENAME
    (dataset_dir / train_name).write_text("train-data")

    def fake_dataset_download(dataset_name: str) -> str:
        return str(dataset_dir)

    fake_kagglehub = SimpleNamespace(dataset_download=fake_dataset_download)
    monkeypatch.setattr(ingest_module, "kagglehub", fake_kagglehub)

    with pytest.raises(FileNotFoundError) as exc:
        ingest_module.ingest()

    assert "Test file not found" in str(exc.value)


# ... (seus outros testes do ingest ficam aqui em cima) ...


def test_ingest_main_logs_to_mlflow(tmp_path, monkeypatch):
    """
    main() must:
    - start an MLflow run with the expected run_name;
    - call ingest();
    - log dataset_name, train_path and test_path as params;
    - log the train/test files as artifacts.
    """
    from src.model.data import ingest as ingest_module

    # --- Configura paths fake para o cfg usado dentro de ingest.py ---
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    monkeypatch.setattr(ingest_module.cfg, "KAGGLE_DATASET_NAME", "fake/dataset")
    monkeypatch.setattr(ingest_module.cfg, "DATASET_RAW_DIR", raw_dir)
    monkeypatch.setattr(ingest_module.cfg, "KAGGLE_DATASET_TRAIN_FILENAME", "train.csv")
    monkeypatch.setattr(ingest_module.cfg, "KAGGLE_DATASET_TEST_FILENAME", "test.csv")

    # Paths que o fake ingest vai retornar
    train_path = raw_dir / "train.csv"
    test_path = raw_dir / "test.csv"
    train_path.write_text("train-data")
    test_path.write_text("test-data")

    # --- Mock do ingest() para não chamar Kaggle nem copiar nada ---
    def fake_ingest():
        return {"train": train_path, "test": test_path}

    monkeypatch.setattr(ingest_module, "ingest", fake_ingest)

    # --- Mock do mlflow (start_run, log_param, log_artifact) ---
    calls = {
        "start_run": [],
        "log_param": [],
        "log_artifact": [],
    }

    class DummyRun:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False  # não suprime exceções

    def fake_start_run(run_name):
        calls["start_run"].append({"run_name": run_name})
        return DummyRun()

    def fake_log_param(key, value):
        calls["log_param"].append((key, value))

    def fake_log_artifact(path):
        calls["log_artifact"].append(Path(path))

    fake_mlflow = SimpleNamespace(
        start_run=fake_start_run,
        log_param=fake_log_param,
        log_artifact=fake_log_artifact,
    )

    monkeypatch.setattr(ingest_module, "mlflow", fake_mlflow)

    # --- Executa o main() ---
    ingest_module.main()

    # --- Asserts ---

    # 1) start_run chamado corretamente
    assert calls["start_run"] == [{"run_name": "data_ingest"}]

    # 2) log_param: dataset_name, train_path, test_path
    logged_params = dict(calls["log_param"])
    assert logged_params["dataset_name"] == "fake/dataset"
    assert logged_params["train_path"] == raw_dir / "train.csv"
    assert logged_params["test_path"] == raw_dir / "test.csv"

    # 3) log_artifact: paths retornados por ingest()
    assert train_path in calls["log_artifact"]
    assert test_path in calls["log_artifact"]
