from types import SimpleNamespace

import pytest


def _setup_fake_csvs(tmp_path, ingest_module):
    """
    Create a fake Kaggle download directory containing the expected
    train/test CSV files.
    """
    dataset_dir = tmp_path / "kaggle_download"
    dataset_dir.mkdir()

    train_name = ingest_module.KAGGLE_DATASET_TRAIN_FILENAME
    test_name = ingest_module.KAGGLE_DATASET_TEST_FILENAME

    (dataset_dir / train_name).write_text("col\n1\n2\n3\n")
    (dataset_dir / test_name).write_text("col\n7\n8\n9\n")

    return dataset_dir


def test_ingest_happy_path(tmp_path, monkeypatch):
    """
    ingest() must:
    - create DATASET_RAW_PATH
    - read CSV files from Kaggle download dir
    - save them as Parquet in RAW directory
    - return proper output dict with row counts and paths
    """
    from src.model.data import ingest as ingest_module

    # Override RAW path
    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(ingest_module, "DATASET_RAW_PATH", raw_dir)

    # Override parquet output paths
    train_parquet = raw_dir / "train.parquet"
    test_parquet = raw_dir / "test.parquet"

    monkeypatch.setattr(ingest_module, "DATASET_RAW_TRAIN_PARQUET", train_parquet)
    monkeypatch.setattr(ingest_module, "DATASET_RAW_TEST_PARQUET", test_parquet)

    # Create fake kaggle download
    dataset_dir = _setup_fake_csvs(tmp_path, ingest_module)

    # Mock kagglehub
    def fake_download(name):
        return str(dataset_dir)

    monkeypatch.setattr(
        ingest_module, "kagglehub", SimpleNamespace(dataset_download=fake_download)
    )

    # Execute
    result = ingest_module.ingest()

    # Validate directories
    assert raw_dir.exists()

    # Validate parquet files created
    assert train_parquet.exists()
    assert test_parquet.exists()

    # Validate returned dict
    assert result["train_path"] == train_parquet
    assert result["test_path"] == test_parquet
    assert result["train_rows"] == 3
    assert result["test_rows"] == 3


def test_ingest_missing_train(tmp_path, monkeypatch):
    """ingest() must raise FileNotFoundError if train CSV is missing."""
    from src.model.data import ingest as ingest_module

    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(ingest_module, "DATASET_RAW_PATH", raw_dir)

    # Fake kaggle dir
    dataset_dir = tmp_path / "kaggle_download"
    dataset_dir.mkdir()

    # Create only test file
    test_path = dataset_dir / ingest_module.KAGGLE_DATASET_TEST_FILENAME
    test_path.write_text("x")

    def fake_download(name):
        return str(dataset_dir)

    monkeypatch.setattr(
        ingest_module, "kagglehub", SimpleNamespace(dataset_download=fake_download)
    )

    with pytest.raises(FileNotFoundError):
        ingest_module.ingest()


def test_ingest_missing_test(tmp_path, monkeypatch):
    """ingest() must raise FileNotFoundError if test CSV is missing."""
    from src.model.data import ingest as ingest_module

    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(ingest_module, "DATASET_RAW_PATH", raw_dir)

    dataset_dir = tmp_path / "kaggle_download"
    dataset_dir.mkdir()

    train_path = dataset_dir / ingest_module.KAGGLE_DATASET_TRAIN_FILENAME
    train_path.write_text("x")

    def fake_download(name):
        return str(dataset_dir)

    monkeypatch.setattr(
        ingest_module, "kagglehub", SimpleNamespace(dataset_download=fake_download)
    )

    with pytest.raises(FileNotFoundError):
        ingest_module.ingest()


def test_ingest_main_logs_mlflow(tmp_path, monkeypatch):
    """
    main() must:
    - start an MLflow run
    - call ingest()
    - log dataset_name and all returned params
    """
    from src.model.data import ingest as ingest_module

    # Fake raw folder
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    monkeypatch.setattr(ingest_module, "DATASET_RAW_PATH", raw_dir)
    monkeypatch.setattr(ingest_module, "KAGGLE_DATASET_NAME", "fake/dataset")

    # Fake ingest() return
    output = {
        "train_path": raw_dir / "train.parquet",
        "test_path": raw_dir / "test.parquet",
        "train_rows": 10,
        "test_rows": 5,
    }

    monkeypatch.setattr(ingest_module, "ingest", lambda: output)

    # Track MLflow calls
    calls = {"start_run": [], "log_param": []}

    class DummyRun:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_start_run(run_name):
        calls["start_run"].append(run_name)
        return DummyRun()

    def fake_log_param(key, val):
        calls["log_param"].append((key, val))

    monkeypatch.setattr(
        ingest_module,
        "mlflow",
        SimpleNamespace(
            start_run=fake_start_run,
            log_param=fake_log_param,
        ),
    )

    # Execute main()
    ingest_module.main()

    assert calls["start_run"] == ["data_ingest"]

    logged = dict(calls["log_param"])
    assert logged["dataset_name"] == "fake/dataset"
    assert logged["train_path"] == str(output["train_path"])
    assert logged["test_path"] == str(output["test_path"])
    assert logged["train_rows"] == "10"
    assert logged["test_rows"] == "5"
