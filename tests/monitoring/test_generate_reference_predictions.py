import numpy as np
import pandas as pd
import pytest

from src.monitoring import generate_reference_predictions as grp

# ---------------------------------------------------------------------------
# load_validation_dataset
# ---------------------------------------------------------------------------


def test_load_validation_dataset_raises_when_file_missing(monkeypatch, tmp_path):
    """
    If TEST_DATA_PATH does not exist, load_validation_dataset must raise FileNotFoundError.
    """
    fake_path = tmp_path / "missing.parquet"
    monkeypatch.setattr(grp, "TEST_DATA_PATH", fake_path, raising=True)

    with pytest.raises(FileNotFoundError):
        grp.load_validation_dataset()


def test_load_validation_dataset_reads_parquet(monkeypatch, tmp_path):
    """
    When TEST_DATA_PATH exists, load_validation_dataset should read it as parquet.
    """
    df_original = pd.DataFrame({"full_text": ["a", "b", "c"]})
    test_path = tmp_path / "val.parquet"
    df_original.to_parquet(test_path)

    monkeypatch.setattr(grp, "TEST_DATA_PATH", test_path, raising=True)

    df_loaded = grp.load_validation_dataset()
    pd.testing.assert_frame_equal(df_loaded, df_original)


# ---------------------------------------------------------------------------
# infer_predictions_with_confidence
# ---------------------------------------------------------------------------


def test_infer_predictions_with_confidence_uses_predict_and_predict_proba():
    """
    infer_predictions_with_confidence must:
    - call model.predict and model.predict_proba with the list(texts)
    - return labels and confidences (max of probs per row)
    """

    class FakeModel:
        def __init__(self):
            self.predict_calls = []
            self.predict_proba_calls = []

        def predict(self, texts):
            self.predict_calls.append(list(texts))
            return np.array([1, 0])

        def predict_proba(self, texts):
            self.predict_proba_calls.append(list(texts))
            return np.array(
                [
                    [0.2, 0.8],  # max -> 0.8
                    [0.9, 0.1],  # max -> 0.9
                ]
            )

    model = FakeModel()
    texts = ["text-1", "text-2"]

    labels, confidences = grp.infer_predictions_with_confidence(model, texts)

    assert model.predict_calls == [texts]
    assert model.predict_proba_calls == [texts]

    assert np.array_equal(labels, np.array([1, 0]))
    assert np.allclose(confidences, np.array([0.8, 0.9]))


# ---------------------------------------------------------------------------
# generate_reference_predictions
# ---------------------------------------------------------------------------


def test_generate_reference_predictions_writes_parquet(monkeypatch, tmp_path):
    """
    generate_reference_predictions must:
    - load validation dataset
    - load model via load_model(MODEL_PATH)
    - call infer_predictions_with_confidence(model, texts)
    - write a parquet with predicted_label and confidence
    - return REFERENCE_PREDICTIONS_PATH
    """
    # 1) Patch paths
    ref_path = tmp_path / "ref.parquet"
    model_path = tmp_path / "model_dir"

    monkeypatch.setattr(grp, "REFERENCE_PREDICTIONS_PATH", ref_path, raising=True)
    monkeypatch.setattr(grp, "MODEL_PATH", model_path, raising=True)

    # 2) Fake validation dataset
    df_val = pd.DataFrame({"full_text": ["t1", "t2", "t3"]})

    def fake_load_validation_dataset():
        return df_val

    monkeypatch.setattr(
        grp, "load_validation_dataset", fake_load_validation_dataset, raising=True
    )

    # 3) Fake model + load_model
    class FakeModel:
        pass

    fake_model = FakeModel()

    def fake_load_model(model_local_path, allow_runtime_model_download):
        assert model_local_path == model_path
        return fake_model

    monkeypatch.setattr(grp, "load_model", fake_load_model, raising=True)

    def fake_infer_predictions_with_confidence(model, texts):
        assert model is fake_model
        assert list(texts) == df_val["full_text"].tolist()
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

    # Validate written parquet
    df_written = pd.read_parquet(ref_path)
    assert list(df_written.columns) == ["predicted_label", "confidence"]
    assert df_written["predicted_label"].tolist() == [1, 0, 1]
    assert df_written["confidence"].tolist() == [0.9, 0.7, 0.95]
