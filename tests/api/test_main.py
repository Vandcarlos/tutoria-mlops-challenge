from fastapi import FastAPI
from fastapi.testclient import TestClient

import src.api.main as main


def test_app_is_fastapi_instance():
    """
    Ensure the app object is a FastAPI instance.
    """
    assert isinstance(main.app, FastAPI)
    assert main.app.title == "Sentiment API"


def test_router_is_included_with_prefix(monkeypatch):
    """
    Ensure the router from src.api.routes is included with prefix /api/v1.
    """

    class FakeRouter:
        def __init__(self):
            self.included = False
            self.prefix_used = None

    fake_router = FakeRouter()

    monkeypatch.setattr(main, "router", fake_router, raising=True)

    matches = [
        r
        for r in main.app.router.routes
        if getattr(r, "path", "").startswith("/api/v1")
    ]

    # --- Assert ---
    assert len(matches) > 0, "Router should be included under /api/v1"


class FakeModel:
    def predict(self, X):
        return [1 for _ in X]

    def predict_proba(self, X):
        return [[0.1, 0.9] for _ in X]


def test_predict_endpoint(monkeypatch):
    def fake_load_model(*args, **kwargs):
        return FakeModel()

    monkeypatch.setattr(main, "load_model", fake_load_model)

    with TestClient(main.app) as client:
        resp = client.post(
            "/api/v1/predict",
            json={"title": "Great", "message": "Awesome product"},
        )

        assert resp.status_code == 200
