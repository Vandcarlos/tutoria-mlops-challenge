from src.api.schemas import PredictResponse
from src.shared.schemas import PredictionLabel


def test_predict_response_accepts_valid_fields():
    label_enum = PredictionLabel(1)
    resp = PredictResponse(prediction_label=label_enum, confidence=0.85)

    assert resp.prediction_label.value == 1
    assert resp.prediction_label is label_enum
    assert resp.confidence == 0.85
    # computed field deve bater com o enum
    assert resp.sentiment == label_enum.sentiment


def test_predict_response_serializes_label_as_enum_value():
    label_enum = PredictionLabel(1)
    resp = PredictResponse(prediction_label=label_enum, confidence=0.9)

    data = resp.model_dump()

    assert data["prediction_label"] == label_enum.value
    assert data["prediction_label_name"] == label_enum.name
    assert data["sentiment"] == label_enum.sentiment
    assert data["confidence"] == 0.9


def test_predict_response_json_structure():
    label_enum = PredictionLabel(0)
    resp = PredictResponse(prediction_label=label_enum, confidence=1.0)

    data = resp.model_dump()

    assert set(data.keys()) == {
        "prediction_label",
        "prediction_label_name",
        "confidence",
        "sentiment",
    }


def test_predict_response_coerces_int_to_prediction_label():
    """
    Pydantic deve conseguir converter um int para o enum PredictionLabel,
    já que o tipo do campo é PredictionLabel.
    """
    resp = PredictResponse(prediction_label=1, confidence=0.5)

    assert isinstance(resp.prediction_label, PredictionLabel)
    assert resp.prediction_label == PredictionLabel(1)
    assert resp.sentiment == resp.prediction_label.sentiment


def test_predict_response_coerces_confidence_to_float():
    resp = PredictResponse(prediction_label=PredictionLabel(1), confidence=1)
    assert isinstance(resp.confidence, float)
    assert resp.confidence == 1.0
