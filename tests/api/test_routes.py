import importlib

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from src.api.schemas import PredictRequest, PredictResponse
from src.shared.schemas import PredictionLabel


@pytest.fixture
def api_client(monkeypatch):
    """
    Builds a FastAPI app with the router, injecting:
    - a fake model into app.state.model
    - a fake logger into app.state.prediction_logger
    - a patched predict_sentiment() so we can assert its inputs

    Returns (client, called) where `called` records all parameters passed
    to predict_sentiment().
    """

    # --------------------------
    # 1) Import and reload routes
    # --------------------------
    import src.api.routes as routes

    routes = importlib.reload(routes)

    # --------------------------
    # 2) Prepare tracking dict
    # --------------------------
    called = {}

    def fake_predict_sentiment(req, model, logger):
        """
        Fake service storing everything that was called and returning
        a predictable fixed response.
        """
        called["req"] = req
        called["model"] = model
        called["logger"] = logger

        return PredictResponse(
            prediction_label=PredictionLabel.POSITIVE,
            confidence=0.88,
        )

    # Patch the service used by routes
    monkeypatch.setattr(
        routes,
        "predict_sentiment",
        fake_predict_sentiment,
        raising=True,
    )

    # --------------------------
    # 3) Build FastAPI app
    # --------------------------
    app = FastAPI()

    # Inject fake model + fake logger in app.state
    app.state.model = "FAKE_MODEL"
    app.state.prediction_logger = "FAKE_LOGGER"

    # Register router
    app.include_router(routes.router, prefix="/api/v1")

    return TestClient(app), called


def test_health(api_client):
    client, _ = api_client

    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_predict(api_client):
    client, called = api_client

    payload = {
        "title": "Amazing product",
        "message": "It works perfectly",
    }

    resp = client.post("/api/v1/predict", json=payload)
    assert resp.status_code == 200

    data = resp.json()

    # --------------------------
    # 1) Service was invoked properly
    # --------------------------
    assert called["model"] == "FAKE_MODEL"
    assert called["logger"] == "FAKE_LOGGER"

    req_obj = called["req"]
    assert isinstance(req_obj, PredictRequest)
    assert req_obj.title == payload["title"]
    assert req_obj.message == payload["message"]

    # --------------------------
    # 2) HTTP response structure (PredictResponse)
    # --------------------------
    assert data["prediction_label"] == PredictionLabel.POSITIVE.value
    assert data["prediction_label_name"] == "POSITIVE"
    assert data["sentiment"] == "Positivo"
    assert data["confidence"] == 0.88
