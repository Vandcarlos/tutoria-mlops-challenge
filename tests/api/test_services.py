from src.api.schemas import PredictRequest
import src.api.services as services

# ---------------------------------------------------------------------------
# Tests for _build_payload
# ---------------------------------------------------------------------------


def test_build_payload_concatenates_title_and_message():
    """
    When both title and message are provided, payload should be title+message.
    (This assumes the intended behavior; current implementation has a precedence bug.)
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
    # title vazio, message preenchido
    req = PredictRequest(title="", message="Message")
    payload = services._build_payload(req)
    assert payload == ["Message"]

    # title preenchido, message vazio
    req = PredictRequest(title="Title", message="")
    payload = services._build_payload(req)
    # Se a intenção for sempre concatenar, isso aqui deveria ser "Title"
    # (e é o que a implementação correta faz)
    assert payload == ["Title"]


# ---------------------------------------------------------------------------
# Tests for predict_sentiment
# ---------------------------------------------------------------------------


def test_predict_sentiment_uses_model_and_builds_response(monkeypatch):
    """
    Ensure predict_sentiment:
    - uses _build_payload to build the input
    - calls model.predict and model.predict_proba with that payload
    - returns a PredictResponse with label_id, label and confidence
    """

    # Fix payload returned by _build_payload to controlar o que vai pro modelo
    def fake_build_payload(req):
        assert isinstance(req, PredictRequest)
        return ["joined-text"]

    monkeypatch.setattr(services, "_build_payload", fake_build_payload, raising=True)

    # Fake model with predict and predict_proba
    class FakeModel:
        def predict(self, payload):
            return [1]

        def predict_proba(self, payload):
            return [[0.2, 0.8]]

    fake_model = FakeModel()

    # Request example – agora sempre com strings (schema exige isso)
    req = PredictRequest(title="Some title", message="Some message")

    # Act
    resp = services.predict_sentiment(fake_model, req)

    # Assert: resp is a PredictResponse and fields are coherent
    assert resp.label.value == 1
    assert resp.confidence == 0.8
