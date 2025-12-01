import json
import sys

import pytest

import src.model.pipeline.predict as predict


class FakePredObj:
    def __init__(self, label_id: int, confidence: float):
        self.label_id = label_id
        self.confidence = confidence


class FakeModel:
    def __init__(self):
        self.called_with = None

    def predict(self, model_input):
        # ensure the input dict is what we expect
        self.called_with = model_input
        return [FakePredObj(label_id=1, confidence=0.85)]


class FakePyFunc:
    def __init__(self):
        self.last_model_uri = None
        self.model = FakeModel()

    def load_model(self, model_uri: str):
        self.last_model_uri = model_uri
        return self.model


class FakeMlflow:
    def __init__(self):
        self.pyfunc = FakePyFunc()


@pytest.fixture
def fake_mlflow(monkeypatch):
    """
    Replace the mlflow object inside predict module with a fake one,
    so no real MLflow tracking/model loading is triggered.
    """
    fake = FakeMlflow()
    monkeypatch.setattr(predict, "mlflow", fake, raising=True)
    return fake


def test_predict_returns_expected_structure(monkeypatch, fake_mlflow):
    # --- Arrange ---
    # Fake resolve_model_uri
    def fake_resolve_model_uri(model_version: str | None) -> str:
        return f"models:/sentiment_model/{model_version or 'latest'}"

    monkeypatch.setattr(
        predict, "resolve_model_uri", fake_resolve_model_uri, raising=True
    )

    # Fake preprocess_df: just to avoid depending on real preprocessing
    def fake_preprocess_df(df):
        df = df.copy()
        df["full_text"] = (
            df[predict.DATASET_TITLE_COLUMN] + " " + df[predict.DATASET_MESSAGE_COLUMN]
        )
        return df

    monkeypatch.setattr(predict, "preprocess_df", fake_preprocess_df, raising=True)

    # Fake PredictionLabel to decouple from real enum
    class FakePredictionLabel:
        def __init__(self, label_id: int):
            self.label_id = label_id
            self.name = "POSITIVE" if label_id == 1 else "NEGATIVE"
            self.sentiment = "positive" if label_id == 1 else "negative"

    monkeypatch.setattr(predict, "PredictionLabel", FakePredictionLabel, raising=True)

    title = "Great product"
    message = "I really liked it"

    # --- Act ---
    result = predict.predict(
        model_version="5",
        title=title,
        message=message,
    )

    # --- Assert ---

    # 1) Check if load_model was called with the correct URI
    assert fake_mlflow.pyfunc.last_model_uri == "models:/sentiment_model/5"

    # 2) Check overall structure
    assert set(result.keys()) == {"input", "preprocessed", "model_uri", "prediction"}

    assert result["input"]["title"] == title
    assert result["input"]["message"] == message

    assert result["model_uri"] == "models:/sentiment_model/5"

    prediction = result["prediction"]
    assert prediction["label_id"] == 1
    assert prediction["label"] == "POSITIVE"
    assert prediction["sentiment"] == "positive"
    assert prediction["confidence"] == 0.85

    preprocessed = result["preprocessed"]
    assert predict.DATASET_TITLE_COLUMN in preprocessed
    assert predict.DATASET_MESSAGE_COLUMN in preprocessed
    assert "full_text" in preprocessed


def test_predict_raises_value_error_when_both_title_and_message_empty(
    monkeypatch,
    fake_mlflow,
):
    # resolve_model_uri fake (URI format não importa, pois mlflow é fake)
    monkeypatch.setattr(
        predict, "resolve_model_uri", lambda ver: "models:/dummy/latest", raising=True
    )

    # preprocess_df identity (não será chamado se o ValueError vier antes,
    # mas deixamos por segurança)
    monkeypatch.setattr(predict, "preprocess_df", lambda df: df, raising=True)

    # Fake PredictionLabel (também não deve ser usado nesse cenário)
    class FakePredictionLabel:
        def __init__(self, label_id: int):
            self.label_id = label_id
            self.name = "NEGATIVE"
            self.sentiment = "negative"

    monkeypatch.setattr(predict, "PredictionLabel", FakePredictionLabel, raising=True)

    with pytest.raises(ValueError, match="Both title and message cannot be empty"):
        predict.predict(model_version=None, title=None, message=None)


def test_main_success(monkeypatch, capsys):
    # --- Arrange ---
    # Simulate CLI arguments
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "--title", "Nice", "--message", "Works", "--model_version", "2"],
        raising=True,
    )

    # Fake predict so we don't hit any real logic or MLflow
    def fake_predict(model_version, title, message):
        assert model_version == "2"
        assert title == "Nice"
        assert message == "Works"
        return {
            "input": {"title": title, "message": message},
            "preprocessed": {"title": title, "message": message},
            "model_uri": "models:/sentiment_model/2",
            "prediction": {
                "label": "POSITIVE",
                "label_id": 1,
                "sentiment": "positive",
                "confidence": 0.99,
            },
        }

    monkeypatch.setattr(predict, "predict", fake_predict, raising=True)

    # --- Act ---
    predict.main()
    captured = capsys.readouterr()

    # --- Assert ---
    # output should be JSON on stdout
    output = captured.out.strip()
    data = json.loads(output)

    assert data["input"]["title"] == "Nice"
    assert data["prediction"]["label"] == "POSITIVE"
    assert "PREDICT][ERROR" not in captured.err
    assert "PREDICT][FATAL" not in captured.err


def test_main_exits_with_code_1_on_validation_error(monkeypatch, capsys):
    # --- Arrange ---
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "--title", "", "--message", ""],
        raising=True,
    )

    def fake_predict(model_version, title, message):
        # Simulate _preprocess_input raising
        raise ValueError("Both title and message cannot be empty.")

    monkeypatch.setattr(predict, "predict", fake_predict, raising=True)

    # --- Act & Assert ---
    with pytest.raises(SystemExit) as excinfo:
        predict.main()

    assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "[PREDICT][ERROR]" in captured.err
    assert "Both title and message cannot be empty" in captured.err
