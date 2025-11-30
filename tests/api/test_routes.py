import importlib

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from src.shared.schemas import PredictionLabel  # importa o enum usado na resposta


@pytest.fixture
def api_client(monkeypatch):
    """
    Build a FastAPI app with the API router, using:
    - a fake load_model() so we don't touch MLflow or disk
    - a fake predict_sentiment() so we control the response
    Returns (client, called) where `called` tracks service invocation.
    """

    # --- 1) Patch load_model BEFORE importing routes ---
    def fake_load_model():
        # anything representable as "the model"
        return "FAKE_MODEL"

    monkeypatch.setattr(
        "src.api.model_loader.load_model",
        fake_load_model,
        raising=True,
    )

    # Import (or reload) routes so that model = load_model() use our fake
    import src.api.routes as routes  # noqa: F401

    routes = importlib.reload(routes)

    # --- 2) Patch predict_sentiment BEFORE including router in app ---
    called = {}

    def fake_predict_sentiment(model, req):
        # track inputs
        called["model"] = model
        called["req"] = req

        return {
            "label": PredictionLabel.POSITIVE,
            "confidence": 0.99,
        }

    monkeypatch.setattr(
        routes,
        "predict_sentiment",
        fake_predict_sentiment,
        raising=True,
    )

    app = FastAPI()
    app.include_router(routes.router, prefix="/api/v1")

    client = TestClient(app)
    return client, called


def test_health_endpoint(api_client):
    client, _ = api_client

    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"status": "ok"}


def test_predict_endpoint_calls_service_with_loaded_model(api_client):
    client, called = api_client

    payload = {
        "title": "Great product",
        "message": "I really liked it",
    }

    resp = client.post("/api/v1/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # Confere que o serviço foi chamado com o modelo fake carregado
    assert called["model"] == "FAKE_MODEL"

    # Confere que o PredictRequest recebido é correto
    req_obj = called["req"]
    assert req_obj.title == payload["title"]
    assert req_obj.message == payload["message"]

    # --- Resposta HTTP bate com o fake_predict_sentiment + computed_fields ---
    # label: valor numérico do enum
    assert data["label"] == PredictionLabel.POSITIVE.value
    # label_name: nome do enum (derivado)
    assert data["label_name"] == "POSITIVE"
    # sentiment: string human-friendly (derivada)
    assert data["sentiment"] == "Positivo"
    # confidence: igual ao fake
    assert data["confidence"] == 0.99
