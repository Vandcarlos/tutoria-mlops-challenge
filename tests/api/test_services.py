from src.api.schemas import PredictRequest
import src.api.services as services
from src.shared.schemas import PredictionLabel

# ---------------------------------------------------------------------------
# Tests for _build_payload
# ---------------------------------------------------------------------------


def test_build_payload_concatenates_title_and_message():
    """
    When both title and message are provided, payload should be title + message.
    """
    req = PredictRequest(title="Hello ", message="World")
    payload = services._build_payload(req)

    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0] == "Hello World"


def test_build_payload_works_with_empty_strings():
    """
    Edge cases with empty strings, since title/message are required in the schema.
    """
    # Empty title, non-empty message
    req = PredictRequest(title="", message="Message")
    payload = services._build_payload(req)
    assert payload == ["Message"]

    # Non-empty title, empty message
    req = PredictRequest(title="Title", message="")
    payload = services._build_payload(req)
    assert payload == ["Title"]


# ---------------------------------------------------------------------------
# Tests for predict_sentiment
# ---------------------------------------------------------------------------


def test_predict_sentiment_uses_model_and_builds_response(monkeypatch):
    """
    Ensure predict_sentiment:
    - uses _build_payload to build the input
    - calls model.predict and model.predict_proba with that payload
    - calls logger.log_prediction with the expected fields
    - returns a PredictResponse with label and confidence
    """

    # Force _build_payload to a known, simple value
    def fake_build_payload(req):
        assert isinstance(req, PredictRequest)
        return ["joined-text"]

    monkeypatch.setattr(services, "_build_payload", fake_build_payload, raising=True)

    # Fake model that records calls
    class FakeModel:
        def __init__(self) -> None:
            self.predict_calls = []
            self.predict_proba_calls = []

        def predict(self, payload):
            self.predict_calls.append(payload)
            return [1]  # label id

        def predict_proba(self, payload):
            self.predict_proba_calls.append(payload)
            return [[0.2, 0.8]]  # probs for labels [0, 1]

    # Fake logger that records what was logged
    class FakeLogger:
        def __init__(self) -> None:
            self.calls = []

        def log_prediction(self, **kwargs):
            self.calls.append(kwargs)

    fake_model = FakeModel()
    fake_logger = FakeLogger()

    req = PredictRequest(title="Some title", message="Some message")

    # Act
    resp = services.predict_sentiment(
        req=req,
        model=fake_model,
        logger=fake_logger,
    )

    # --- Assert model interaction ---
    assert len(fake_model.predict_calls) >= 1
    assert fake_model.predict_calls[0] == ["joined-text"]
    assert fake_model.predict_proba_calls == [["joined-text"]]

    # --- Assert response object ---
    assert resp.prediction_label == PredictionLabel(1)
    assert resp.prediction_label.value == 1
    assert resp.confidence == 0.8

    # --- Assert logger interaction ---
    assert len(fake_logger.calls) == 1
    logged = fake_logger.calls[0]

    assert logged["title"] == req.title
    assert logged["message"] == req.message
    assert logged["full_text"] == "joined-text"
    assert logged["predicted_label"] == 1
    assert logged["predicted_label_name"] == "NEGATIVE"
    assert logged["confidence"] == 0.8
    # latency should be a non-negative float
    assert isinstance(logged["latency_ms"], float)
    assert logged["latency_ms"] >= 0.0


def test_predict_sentiment_swallow_logger_errors(monkeypatch):
    """
    If logger.log_prediction raises an exception, predict_sentiment must:
    - not propagate the error
    - still return a valid PredictResponse
    """

    monkeypatch.setattr(
        services,
        "_build_payload",
        lambda req: ["joined-text"],
        raising=True,
    )

    class FakeModel:
        def predict(self, payload):
            return [1]

        def predict_proba(self, payload):
            return [[0.1, 0.9]]

    class ExplodingLogger:
        def log_prediction(self, **kwargs):
            raise RuntimeError("boom")

    fake_model = FakeModel()
    exploding_logger = ExplodingLogger()

    req = PredictRequest(title="Title", message="Message")

    # Should not raise
    resp = services.predict_sentiment(
        req=req,
        model=fake_model,
        logger=exploding_logger,
    )

    assert resp.prediction_label == PredictionLabel(1)
    assert resp.confidence == 0.9
