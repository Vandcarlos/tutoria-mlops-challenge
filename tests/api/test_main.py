from fastapi import FastAPI

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

    # --- Arrange: create a fake router to detect inclusion ---
    class FakeRouter:
        def __init__(self):
            self.included = False
            self.prefix_used = None

    fake_router = FakeRouter()

    # patch the router imported in main.py
    monkeypatch.setattr(main, "api_router", fake_router, raising=True)

    # We need to reload main so that include_router() runs again
    import importlib

    import src.api.main as main_reload  # noqa: F401

    main_reloaded = importlib.reload(main)

    # --- Act: inspect the routes registered in FastAPI instance ---
    # FastAPI stores included routes in app.routes
    matches = [
        r
        for r in main_reloaded.app.router.routes
        if getattr(r, "path", "").startswith("/api/v1")
    ]

    # --- Assert ---
    assert len(matches) > 0, "Router should be included under /api/v1"
