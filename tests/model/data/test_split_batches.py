from pathlib import Path

import pandas as pd

import src.model.data.split_batches as split_batches


def _set_config_helper(tmp_path, monkeypatch) -> dict[str, str]:
    cfg = split_batches.cfg

    monkeypatch.setattr(cfg, "DATASET_BATCH_PATH", tmp_path / "batches", raising=True)
    monkeypatch.setattr(cfg, "DATASET_RAW_PATH", tmp_path / "raw", raising=True)
    monkeypatch.setattr(cfg, "KAGGLE_DATASET_TRAIN_FILENAME", "train.csv", raising=True)
    monkeypatch.setattr(cfg, "DATASET_SPLIT_COUNT", 3, raising=True)

    paths = {
        "batch_path": tmp_path / "batches",
        "raw_path": tmp_path / "raw",
        "train_csv_path": tmp_path / "raw" / "train.csv",
    }

    paths["batch_path"].mkdir(parents=True, exist_ok=True)
    paths["raw_path"].mkdir(parents=True, exist_ok=True)

    return paths


def _make_train_csv(path: Path):
    raw_csv_path = path
    raw_csv_path.write_text(
        "id,polarity,title,message\n"
        + "\n".join(f"{i},1,Title {i},Message {i}" for i in range(10))
    )


def test_split_raw_train_success_creates_batches(tmp_path, monkeypatch):
    configs = _set_config_helper(tmp_path, monkeypatch)
    _make_train_csv(configs["train_csv_path"])

    outputs = split_batches.split_raw_train()

    assert len(outputs) == 3
    for i, out_path in enumerate(outputs):
        assert out_path.exists()
        df_batch = pd.read_csv(out_path)
        if i < 2:
            assert len(df_batch) == 3  # First two batches have 3 rows
        else:
            assert len(df_batch) == 4  # Last batch has 4 rows


def test_split_raw_train_file_not_found(tmp_path, monkeypatch):
    _set_config_helper(tmp_path, monkeypatch)

    try:
        split_batches.split_raw_train()
        raise AssertionError("Expected FileNotFoundError")
    except FileNotFoundError as e:
        assert "train.csv not found" in str(e)


def test_main(tmp_path, monkeypatch):
    configs = _set_config_helper(tmp_path, monkeypatch)
    _make_train_csv(configs["train_csv_path"])
    split_batches.main()

    configs["train_csv_path"].exists()
