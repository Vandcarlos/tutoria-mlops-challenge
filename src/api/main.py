from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.config import (
    ALLOW_RUNTIME_MODEL_DOWNLOAD,
    MLFLOW_MODEL_VERSION,
    MODEL_PATH,
)
from src.api.monitoring_logger import LocalPredictionLogger
from src.api.routes import router
from src.shared.model_resolver import load_model


def create_app() -> FastAPI:
    prediction_logger = LocalPredictionLogger()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.prediction_logger = prediction_logger

        model = load_model(
            model_local_path=MODEL_PATH,
            version=MLFLOW_MODEL_VERSION,
            allow_runtime_model_download=ALLOW_RUNTIME_MODEL_DOWNLOAD,
        )
        app.state.model = model

        yield

    app = FastAPI(
        title="Sentiment API",
        lifespan=lifespan,
    )
    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()
