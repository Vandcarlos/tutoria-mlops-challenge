import numpy as np
import pandas as pd

from src.monitoring import generate_reference_predictions as grp


def test_load_processed_test_dataset_reads_parquet_and_renames_columns(
    monkeypatch,
    tmp_path,
):
    """When processed test parquet exists, it should be read and columns renamed."""
    processed_path = tmp_path / "processed.parquet"

    # Build a simple processed dataset with two columns
    df_original = pd.DataFrame(
        {
            "col0": [0, 1],
            "col1": ["a", "b"],
        }
    )
    df_original.to_parquet(processed_path)

    monkeypatch.setattr(
        grp, "DATASET_PROCESSED_TEST_PATH", processed_path, raising=True
    )
    monkeypatch.setattr(grp, "USE_S3_DATA", False, raising=True)

    # Act
    df_loaded = grp._load_processed_test_dataset()

    # Assert: columns should be renamed to polarity + full_text
    polarity_col = grp.DATASET_POLARITY_COLUMN
    full_text_col = grp.DATASET_FULL_TEXT_COLUMN

    assert list(df_loaded.columns) == [polarity_col, full_text_col]
    assert df_loaded[polarity_col].tolist() == [0, 1]
    assert df_loaded[full_text_col].tolist() == ["a", "b"]


def test_load_processed_test_dataset_falls_back_to_raw_loader_on_error(
    monkeypatch,
):
    """If processed parquet cannot be read, it must fall back to _load_and_preprocess_raw_test_dataset."""
    # Arrange: force read_parquet to raise and track fallback calls
    fallback_df = pd.DataFrame({"x": [1, 2]})
    fallback_calls = []

    def fake_read_parquet(path):
        raise FileNotFoundError("no processed file")

    def fake_fallback():
        fallback_calls.append("called")
        return fallback_df

    monkeypatch.setattr(grp.pd, "read_parquet", fake_read_parquet, raising=True)
    monkeypatch.setattr(
        grp,
        "_load_and_preprocess_raw_test_dataset",
        fake_fallback,
        raising=True,
    )
    monkeypatch.setattr(grp, "USE_S3_DATA", False, raising=True)

    # Act
    df_loaded = grp._load_processed_test_dataset()

    # Assert
    assert fallback_calls == ["called"]
    pd.testing.assert_frame_equal(df_loaded, fallback_df)


def test_load_and_preprocess_raw_test_dataset_builds_full_text_column(
    monkeypatch,
    tmp_path,
):
    """Raw test parquet must be read, columns renamed and full_text built from title + message."""
    raw_path = tmp_path / "raw.parquet"

    # Build raw dataset with three generic columns; they will be renamed in the function
    df_raw = pd.DataFrame(
        [
            [0, "Great Product", "Really Loved It"],
            [1, "Bad Product", "Hated It"],
        ],
        columns=["c0", "c1", "c2"],
    )
    df_raw.to_parquet(raw_path)

    # Patch config paths and flags
    monkeypatch.setattr(grp, "DATASET_RAW_TEST_PARQUET", raw_path, raising=True)
    monkeypatch.setattr(grp, "USE_S3_DATA", False, raising=True)

    # Act
    df_processed = grp._load_and_preprocess_raw_test_dataset()

    polarity_col = grp.DATASET_POLARITY_COLUMN
    title_col = grp.DATASET_TITLE_COLUMN
    message_col = grp.DATASET_MESSAGE_COLUMN
    full_text_col = grp.DATASET_FULL_TEXT_COLUMN

    # Assert: title and message columns should have been dropped, leaving polarity + full_text
    assert list(df_processed.columns) == [polarity_col, full_text_col]

    # Polarity preserved
    assert df_processed[polarity_col].tolist() == [0, 1]

    # Full-text is lowercase "title message"
    expected_full_text = [
        "great product really loved it",
        "bad product hated it",
    ]
    assert df_processed[full_text_col].tolist() == expected_full_text

    # Sanity check: original title/message columns are gone
    assert title_col not in df_processed.columns
    assert message_col not in df_processed.columns


def test_infer_predictions_with_confidence_uses_predict_and_predict_proba():
    """infer_predictions_with_confidence must call predict and predict_proba and return labels + confidences."""

    class FakeModel:
        def __init__(self):
            self.predict_calls = []
            self.predict_proba_calls = []

        def predict(self, texts):
            self.predict_calls.append(texts)
            return np.array([1, 0])

        def predict_proba(self, texts):
            self.predict_proba_calls.append(texts)
            # Two samples, two classes
            return np.array(
                [
                    [0.2, 0.8],
                    [0.9, 0.1],
                ]
            )

    model = FakeModel()
    texts = ["text-1", "text-2"]

    labels, confidences = grp.infer_predictions_with_confidence(model, texts)

    assert model.predict_calls == [texts]
    assert model.predict_proba_calls == [texts]

    assert np.array_equal(labels, np.array([1, 0]))
    assert np.allclose(confidences, np.array([0.8, 0.9]))


def test_generate_reference_predictions_writes_parquet_and_returns_path(
    monkeypatch,
    tmp_path,
):
    """generate_reference_predictions must write parquet with predicted_label and confidence and return its path."""
    # Patch reference path and disable S3
    ref_path = tmp_path / "ref.parquet"
    monkeypatch.setattr(grp, "REFERENCE_PREDICTIONS_PATH", ref_path, raising=True)
    monkeypatch.setattr(grp, "USE_S3_DATA", False, raising=True)

    # Fake validation dataset
    full_text_col = grp.DATASET_FULL_TEXT_COLUMN
    df_val = pd.DataFrame({full_text_col: ["t1", "t2", "t3"]})

    def fake_load_processed_test_dataset():
        return df_val

    monkeypatch.setattr(
        grp,
        "_load_processed_test_dataset",
        fake_load_processed_test_dataset,
        raising=True,
    )

    # Fake model loading
    class FakeModel:
        pass

    loaded_models = []

    def fake_load_model(model_local_path, allow_runtime_model_download):
        loaded_models.append(
            (model_local_path, allow_runtime_model_download),
        )
        return FakeModel()

    monkeypatch.setattr(grp, "load_model", fake_load_model, raising=True)

    # Fake inference
    def fake_infer_predictions_with_confidence(model, texts):
        assert isinstance(model, FakeModel)
        assert list(texts) == ["t1", "t2", "t3"]
        labels = np.array([1, 0, 1])
        confidences = np.array([0.9, 0.7, 0.95])
        return labels, confidences

    monkeypatch.setattr(
        grp,
        "infer_predictions_with_confidence",
        fake_infer_predictions_with_confidence,
        raising=True,
    )

    # Act
    result_path = grp.generate_reference_predictions()

    # Assert path returned and file existence
    assert result_path == ref_path
    assert ref_path.exists()

    # Validate written parquet content
    df_written = pd.read_parquet(ref_path)
    assert list(df_written.columns) == ["predicted_label", "confidence"]
    assert df_written["predicted_label"].tolist() == [1, 0, 1]
    assert df_written["confidence"].tolist() == [0.9, 0.7, 0.95]


def test_generate_reference_predictions_uploads_to_s3_when_enabled(
    monkeypatch,
    tmp_path,
):
    """When USE_S3_DATA is True, generate_reference_predictions must upload reference parquet to S3."""
    ref_path = tmp_path / "ref.parquet"
    monkeypatch.setattr(grp, "REFERENCE_PREDICTIONS_PATH", ref_path, raising=True)
    monkeypatch.setattr(grp, "USE_S3_DATA", True, raising=True)

    # Reuse same fake validation dataset as above
    full_text_col = grp.DATASET_FULL_TEXT_COLUMN
    df_val = pd.DataFrame({full_text_col: ["t1"]})

    monkeypatch.setattr(
        grp,
        "_load_processed_test_dataset",
        lambda: df_val,
        raising=True,
    )

    class FakeModel:
        pass

    monkeypatch.setattr(
        grp,
        "load_model",
        lambda *args, **kwargs: FakeModel(),
        raising=True,
    )

    def fake_infer_predictions_with_confidence(model, texts):
        return np.array([1]), np.array([0.9])

    monkeypatch.setattr(
        grp,
        "infer_predictions_with_confidence",
        fake_infer_predictions_with_confidence,
        raising=True,
    )

    uploaded = []

    def fake_upload_file_to_s3(file_path, bucket, key):
        uploaded.append((file_path, bucket, key))

    monkeypatch.setattr(
        grp,
        "upload_file_to_s3",
        fake_upload_file_to_s3,
        raising=True,
    )

    # Act
    result_path = grp.generate_reference_predictions()

    # Assert parquet is written
    assert result_path == ref_path
    assert ref_path.exists()

    # Assert S3 upload was called with the patched file path and configured bucket/key
    assert len(uploaded) == 1
    uploaded_path, uploaded_bucket, uploaded_key = uploaded[0]
    assert uploaded_path == ref_path
    assert uploaded_bucket == grp.S3_DATA_BUCKET
    assert uploaded_key == grp.S3_DATA_KEY_MONITORING_REFERENCE
