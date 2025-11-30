from pathlib import Path
import sys

import pandas as pd
import pytest

from src.model.data import preprocess_batch as pb


@pytest.fixture
def tmp_dataset_dirs(tmp_path, monkeypatch):
    batch_path = tmp_path / "batches"
    processed_path = tmp_path / "processed"

    batch_path.mkdir(parents=True, exist_ok=True)

    # Patch the cfg values used by the module
    monkeypatch.setattr(pb.cfg, "DATASET_BATCH_PATH", batch_path, raising=True)
    monkeypatch.setattr(pb.cfg, "DATASET_PROCESSED_PATH", processed_path, raising=True)

    # Column names expected by the module
    monkeypatch.setattr(pb.cfg, "DATASET_POLARITY_COLUMN", "polarity", raising=True)
    monkeypatch.setattr(pb.cfg, "DATASET_TITLE_COLUMN", "title", raising=True)
    monkeypatch.setattr(pb.cfg, "DATASET_MESSAGE_COLUMN", "message", raising=True)

    return {
        "batch_path": batch_path,
        "processed_path": processed_path,
    }


@pytest.fixture
def mock_data_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            pb.cfg.DATASET_POLARITY_COLUMN: [1, 0],
            pb.cfg.DATASET_TITLE_COLUMN: ["Title A", "Title B"],
            pb.cfg.DATASET_MESSAGE_COLUMN: ["Message A", "Message B"],
        }
    )


def test_preprocess_batch_success_writes_parquet_and_returns_path(
    tmp_dataset_dirs, monkeypatch, mock_data_frame
):
    batch_path = tmp_dataset_dirs["batch_path"]
    processed_path = tmp_dataset_dirs["processed_path"]

    # Create a CSV with no header (header=None in code)
    csv_path = batch_path / "train_batch_0.csv"
    csv_path.write_text("1,Title A,Message A\n0,Title B,Message B\n")

    # Prepare a fake preprocess_df that validates incoming df_raw columns
    def fake_preprocess_df(df_raw):
        # The module sets df_raw.columns to the configured names before calling this
        assert list(df_raw.columns) == [
            pb.cfg.DATASET_POLARITY_COLUMN,
            pb.cfg.DATASET_TITLE_COLUMN,
            pb.cfg.DATASET_MESSAGE_COLUMN,
        ]

        def instance_to_parquet(path, index=False, **kwargs):
            p = Path(path)
            p.write_text("PARQUET_PLACEHOLDER")
            return None

        # Bind the to_parquet function to this instance
        mock_data_frame.to_parquet = instance_to_parquet
        return mock_data_frame

    # Patch preprocess_df used by the module
    monkeypatch.setattr(
        "src.model.data.preprocess_batch.preprocess_df",
        fake_preprocess_df,
        raising=True,
    )

    out_path = pb.preprocess_batch(0)
    assert out_path.exists()
    assert out_path.suffix == ".parquet"
    # Ensure the placeholder content was written
    assert out_path.read_text() == "PARQUET_PLACEHOLDER"
    # ensure processed dir was created
    assert processed_path.exists()


def test_preprocess_batch_missing_file_raises(tmp_dataset_dirs):
    # No file created in batch dir
    with pytest.raises(FileNotFoundError) as exc:
        pb.preprocess_batch(999)
    msg = str(exc.value)
    assert "Batch 999 not found" in msg


def test_main_without_args_raises_systemexit(monkeypatch):
    # Ensure sys.argv has no batch index -> main should raise SystemExit with usage message
    monkeypatch.setattr(sys, "argv", ["prog"], raising=True)
    with pytest.raises(SystemExit) as exc:
        pb.main()
    assert "Usage" in str(exc.value)


def test_main_with_args_runs_preprocess_batch_and_logs(
    monkeypatch, tmp_dataset_dirs, mock_data_frame
):
    batch_path = tmp_dataset_dirs["batch_path"]
    processed_path = tmp_dataset_dirs["processed_path"]

    processed_path.mkdir(parents=True, exist_ok=True)

    # Create a CSV with no header (header=None in code)
    csv_path = batch_path / "train_batch_1.csv"
    csv_path.write_text("1,Title C,Message C\n0,Title D,Message D\n")

    # Patch preprocess_batch to a fake that returns a known path
    fake_out_path = processed_path / "train_batch_1.parquet"
    mock_data_frame.to_parquet(fake_out_path)

    monkeypatch.setattr(
        "src.model.data.preprocess_batch.preprocess_batch",
        lambda batch_idx: fake_out_path,
        raising=True,
    )

    # Patch sys.argv to include batch index
    monkeypatch.setattr(sys, "argv", ["prog", "1"], raising=True)

    # Patch mlflow.start_run to a no-op context manager
    class FakeRunContext:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def fake_start_run(run_name):
        assert run_name == "data_preprocess_batch_1"
        return FakeRunContext()

    monkeypatch.setattr("mlflow.start_run", fake_start_run, raising=True)

    # Run main - should not raise
    pb.main()

    # Ensure the fake output file was created
    assert fake_out_path.exists()

    df = pd.read_parquet(fake_out_path)
    pd.testing.assert_frame_equal(df, mock_data_frame)
