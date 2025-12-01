from fastapi import APIRouter, Depends, Request
from sklearn.pipeline import Pipeline

from src.api.monitoring_logger import LocalPredictionLogger
from src.api.schemas import PredictRequest, PredictResponse
from src.api.services import predict_sentiment

router = APIRouter()


def get_prediction_logger(request: Request) -> LocalPredictionLogger:
    """FastAPI dependency to fetch the prediction logger from app.state."""
    return request.app.state.prediction_logger


def get_model(request: Request) -> Pipeline:
    """FastAPI dependency to fetch the model from app.state."""
    return request.app.state.model


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/predict", response_model=PredictResponse)
def predict(
    req: PredictRequest,
    model=Depends(get_model),  # noqa: B008
    logger: LocalPredictionLogger = Depends(get_prediction_logger),  # noqa: B008
):
    return predict_sentiment(req=req, model=model, logger=logger)
