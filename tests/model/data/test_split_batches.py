from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

import src.model.data.split_batches as split_batches


def _setup_parquet_and_config(
    tmp_path, monkeypatch, n_rows: int = 10, n_batches: int = 3
):
    """
    Configure module-level constants for split_batches and create
    a fake raw train parquet file with n_rows rows.
    """
    # Base directories
    raw_dir = tmp_path / "raw"
    batches_dir = tmp_path / "batches"
    raw_dir.mkdir(parents=True, exist_ok=True)
    batches_dir.mkdir(parents=True, exist_ok=True)

    # Fake raw parquet path
    raw_parquet_path = raw_dir / "train.parquet"

    # Create a simple DataFrame with n_rows
    df = pd.DataFrame(
        {
            "id": list(range(n_rows)),
            "polarity": [1] * n_rows,
            "title": [f"Title {i}" for i in range(n_rows)],
            "message": [f"Message {i}" for i in range(n_rows)],
        }
    )
    df.to_parquet(raw_parquet_path, index=False)

    # Patch module-level config constants
    monkeypatch.setattr(
        split_batches, "DATASET_RAW_TRAIN_PARQUET", raw_parquet_path, raising=True
    )
    monkeypatch.setattr(split_batches, "DATASET_BATCH_PATH", batches_dir, raising=True)
    monkeypatch.setattr(split_batches, "DATASET_SPLIT_COUNT", n_batches, raising=True)

    # Define a simple batch item path factory
    def fake_batch_item_path(batch_idx: int) -> Path:
        return batches_dir / f"batch_{batch_idx}.parquet"

    monkeypatch.setattr(
        split_batches, "DATASET_BATCH_ITEM_PATH", fake_batch_item_path, raising=True
    )

    return {
        "raw_dir": raw_dir,
        "batches_dir": batches_dir,
        "raw_parquet_path": raw_parquet_path,
        "n_rows": n_rows,
        "n_batches": n_batches,
    }


def test_split_raw_train_success_creates_parquet_batches(tmp_path, monkeypatch):
    """
    split_raw_train() must:
    - read the raw train parquet
    - split into DATASET_SPLIT_COUNT batches
    - save each batch as parquet
    - return metadata about the split
    """
    cfg = _setup_parquet_and_config(tmp_path, monkeypatch, n_rows=10, n_batches=3)

    result = split_batches.split_raw_train()

    # Basic structure
    assert result["input_path"] == cfg["raw_parquet_path"]
    assert result["n_batches"] == 3
    assert result["total_rows"] == 10
    assert result["batch_size"] == 10 // 3
    assert result["batch_row_size"] == 10 // 3

    outputs = result["outputs_path"]
    assert isinstance(outputs, list)
    assert len(outputs) == 3

    # Check each batch file exists and row counts (3, 3, 4)
    for i, out_path in enumerate(outputs):
        assert isinstance(out_path, Path)
        assert out_path.exists()
        df_batch = pd.read_parquet(out_path)

        if i < 2:
            assert len(df_batch) == 3
        else:
            assert len(df_batch) == 4


def test_split_raw_train_raises_if_raw_parquet_missing(tmp_path, monkeypatch):
    """
    split_raw_train() must raise FileNotFoundError if the raw train
    parquet file does not exist.
    """
    # Configure only paths, do NOT create the parquet file
    raw_dir = tmp_path / "raw"
    batches_dir = tmp_path / "batches"
    raw_dir.mkdir(parents=True, exist_ok=True)
    batches_dir.mkdir(parents=True, exist_ok=True)

    raw_parquet_path = raw_dir / "train.parquet"

    monkeypatch.setattr(
        split_batches, "DATASET_RAW_TRAIN_PARQUET", raw_parquet_path, raising=True
    )
    monkeypatch.setattr(split_batches, "DATASET_BATCH_PATH", batches_dir, raising=True)
    monkeypatch.setattr(split_batches, "DATASET_SPLIT_COUNT", 3, raising=True)

    def fake_batch_item_path(batch_idx: int) -> Path:
        return batches_dir / f"batch_{batch_idx}.parquet"

    monkeypatch.setattr(
        split_batches, "DATASET_BATCH_ITEM_PATH", fake_batch_item_path, raising=True
    )

    with pytest.raises(FileNotFoundError) as exc:
        split_batches.split_raw_train()

    assert "train.parquet not found" in str(exc.value)


def test_main_logs_to_mlflow(tmp_path, monkeypatch):
    """
    main() must:
    - start an MLflow run with the expected run_name
    - call split_raw_train()
    - log all returned keys as params
    """
    # Fake output from split_raw_train()
    fake_output = {
        "input_path": Path("/fake/input.parquet"),
        "outputs_path": [Path("/fake/batch_0.parquet"), Path("/fake/batch_1.parquet")],
        "n_batches": 2,
        "batch_size": 5,
        "total_rows": 10,
        "batch_row_size": 5,
    }

    monkeypatch.setattr(
        split_batches, "split_raw_train", lambda: fake_output, raising=True
    )

    # Track mlflow calls
    calls = {"start_run": [], "log_param": []}

    class DummyRun:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False  # do not suppress exceptions

    def fake_start_run(run_name: str):
        calls["start_run"].append(run_name)
        return DummyRun()

    def fake_log_param(key: str, value: str):
        calls["log_param"].append((key, value))

    fake_mlflow = SimpleNamespace(start_run=fake_start_run, log_param=fake_log_param)
    monkeypatch.setattr(split_batches, "mlflow", fake_mlflow, raising=True)

    # Execute main()
    split_batches.main()

    # Asserts
    assert calls["start_run"] == ["data_split_raw_train"]

    logged_params = dict(calls["log_param"])
    for key, value in fake_output.items():
        # All values are logged as strings
        assert logged_params[key] == str(value)
