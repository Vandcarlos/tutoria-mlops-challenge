import pytest

from src.shared.schemas.PredictionLabel import PredictionLabel


@pytest.mark.parametrize(
    "prediction_label, expected_value, expected_sentiment",
    [
        (PredictionLabel.UNKNOWN, 0, "Desconhecido"),
        (PredictionLabel.NEGATIVE, 1, "Negativo"),
        (PredictionLabel.POSITIVE, 2, "Positivo"),
    ],
)
def test_prediction_label_values(prediction_label, expected_value, expected_sentiment):
    assert prediction_label.value == expected_value
    assert prediction_label.sentiment == expected_sentiment


@pytest.mark.parametrize(
    "raw_value, expected_prediction_label",
    [
        (0, PredictionLabel.UNKNOWN),
        (1, PredictionLabel.NEGATIVE),
        (2, PredictionLabel.POSITIVE),
        (999, PredictionLabel.UNKNOWN),
    ],
)
def test_prediction_label_initializer(raw_value, expected_prediction_label):
    prediction_label = PredictionLabel(raw_value)
    assert prediction_label is expected_prediction_label
