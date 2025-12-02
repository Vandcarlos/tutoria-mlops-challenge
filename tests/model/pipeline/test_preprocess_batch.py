from pathlib import Path
import sys
from types import SimpleNamespace

import pandas as pd
import pytest

import src.model.pipeline.preprocess_batch as preprocess_batch


@pytest.fixture
def tmp_dataset_dirs(tmp_path, monkeypatch):
    """
    Setup temporary batch and processed directories and patch
    the config-like constants used by preprocess_batch.
    """
    batch_dir = tmp_path / "batches"
    processed_dir = tmp_path / "processed"

    batch_dir.mkdir(parents=True, exist_ok=True)

    # Patch directory-like paths
    monkeypatch.setattr(
        preprocess_batch, "DATASET_PROCESSED_PATH", processed_dir, raising=True
    )

    # Patch the path factories for input/output batches
    def fake_batch_item_path(batch_idx: int) -> Path:
        return batch_dir / f"train_batch_{batch_idx}.parquet"

    def fake_processed_item_path(batch_idx: int) -> Path:
        return processed_dir / f"train_batch_{batch_idx}.parquet"

    monkeypatch.setattr(
        preprocess_batch,
        "DATASET_BATCH_ITEM_PATH",
        fake_batch_item_path,
        raising=True,
    )
    monkeypatch.setattr(
        preprocess_batch,
        "DATASET_PROCESSED_BATCH_ITEM_PATH",
        fake_processed_item_path,
        raising=True,
    )

    # Column names expected by the module
    monkeypatch.setattr(
        preprocess_batch, "DATASET_POLARITY_COLUMN", "polarity", raising=True
    )
    monkeypatch.setattr(preprocess_batch, "DATASET_TITLE_COLUMN", "title", raising=True)
    monkeypatch.setattr(
        preprocess_batch, "DATASET_MESSAGE_COLUMN", "message", raising=True
    )

    return {
        "batch_dir": batch_dir,
        "processed_dir": processed_dir,
    }


@pytest.fixture
def mock_data_frame() -> pd.DataFrame:
    """
    Return a small DataFrame that represents the processed output.
    """
    return pd.DataFrame(
        {
            preprocess_batch.DATASET_POLARITY_COLUMN: [1, 0],
            preprocess_batch.DATASET_TITLE_COLUMN: ["Title A", "Title B"],
            preprocess_batch.DATASET_MESSAGE_COLUMN: ["Message A", "Message B"],
        }
    )


def test_preprocess_batch_success_writes_parquet_and_returns_metadata(
    tmp_dataset_dirs, monkeypatch, mock_data_frame
):
    """
    preprocess_batch() must:
    - read the raw batch parquet file,
    - rename columns to the configured names,
    - call preprocess_df,
    - write the processed parquet file,
    - return metadata dict with paths and row count.
    """
    batch_dir = tmp_dataset_dirs["batch_dir"]
    processed_dir = tmp_dataset_dirs["processed_dir"]

    # Create a raw parquet file (columns will be overwritten in the function)
    raw_path = batch_dir / "train_batch_0.parquet"
    df_raw = pd.DataFrame(
        [
            [1, "Title A", "Message A"],
            [0, "Title B", "Message B"],
        ]
    )
    df_raw.to_parquet(raw_path, index=False)

    # Fake preprocess_df that checks the incoming columns and returns mock_data_frame
    def fake_preprocess_df(df_raw):
        assert list(df_raw.columns) == [
            preprocess_batch.DATASET_POLARITY_COLUMN,
            preprocess_batch.DATASET_TITLE_COLUMN,
            preprocess_batch.DATASET_MESSAGE_COLUMN,
        ]

        # Replace to_parquet on the returned df to avoid depending on parquet engine
        def fake_to_parquet(path, index=False, **kwargs):
            p = Path(path)
            p.write_text("PARQUET_PLACEHOLDER")

        mock_data_frame.to_parquet = fake_to_parquet
        return mock_data_frame

    monkeypatch.setattr(
        preprocess_batch, "preprocess_df", fake_preprocess_df, raising=True
    )

    result = preprocess_batch.preprocess_batch(0)

    expected_output = processed_dir / "train_batch_0.parquet"

    # Returned paths and count
    assert result["input_path"] == raw_path
    assert result["output_path"] == expected_output
    assert result["n_rows"] == len(mock_data_frame)

    # Check that output file was created by fake_to_parquet
    assert expected_output.exists()
    assert expected_output.read_text() == "PARQUET_PLACEHOLDER"
    assert processed_dir.exists()


def test_preprocess_batch_missing_file_raises(tmp_dataset_dirs):
    """
    If the input batch file does not exist, preprocess_batch() must raise
    FileNotFoundError with a helpful message.
    """
    # No raw parquet created for this batch index
    with pytest.raises(FileNotFoundError) as exc:
        preprocess_batch.preprocess_batch(999)

    msg = str(exc.value)
    assert "Batch 999 not found" in msg


def test_main_without_args_raises_systemexit(monkeypatch):
    """
    main() must raise SystemExit with a usage message if no batch index
    is provided on the command line.
    """
    monkeypatch.setattr(sys, "argv", ["prog"], raising=True)

    with pytest.raises(SystemExit) as exc:
        preprocess_batch.main()

    assert "Usage" in str(exc.value)


def test_main_with_args_runs_preprocess_batch_and_logs(monkeypatch, tmp_dataset_dirs):
    """
    main() must:
    - parse batch_idx from sys.argv,
    - open an MLflow run with the expected name,
    - call preprocess_batch(),
    - log all returned keys as params.
    """
    processed_dir = tmp_dataset_dirs["processed_dir"]
    processed_dir.mkdir(parents=True, exist_ok=True)

    fake_output_path = processed_dir / "train_batch_1.parquet"

    # Fake result returned by preprocess_batch()
    fake_result = {
        "input_path": Path("/fake/input.parquet"),
        "output_path": fake_output_path,
        "n_rows": 2,
    }

    def fake_preprocess_batch(batch_idx: int):
        # Ensure correct batch index is passed
        assert batch_idx == 1
        # Create the fake output file so the test can assert it exists
        fake_output_path.write_text("PARQUET_PLACEHOLDER_MAIN")
        return fake_result

    monkeypatch.setattr(
        preprocess_batch,
        "preprocess_batch",
        fake_preprocess_batch,
        raising=True,
    )

    # Patch sys.argv to include the batch index
    monkeypatch.setattr(sys, "argv", ["prog", "1"], raising=True)

    # Track mlflow calls
    calls = {"start_run": [], "log_param": []}

    class FakeRunContext:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False  # do not suppress exceptions

    def fake_start_run(run_name):
        calls["start_run"].append(run_name)
        return FakeRunContext()

    def fake_log_param(key, value):
        calls["log_param"].append((key, value))

    fake_mlflow = SimpleNamespace(
        start_run=fake_start_run,
        log_param=fake_log_param,
    )

    monkeypatch.setattr(preprocess_batch, "mlflow", fake_mlflow, raising=True)

    # Run main - should not raise
    preprocess_batch.main()

    # Assert MLflow run name
    assert calls["start_run"] == ["data_preprocess_batch_1"]

    # Assert all params were logged as strings
    logged_params = dict(calls["log_param"])
    for key, value in fake_result.items():
        assert logged_params[key] == str(value)

    # Ensure the fake output file was created
    assert fake_output_path.exists()
    assert fake_output_path.read_text() == "PARQUET_PLACEHOLDER_MAIN"
