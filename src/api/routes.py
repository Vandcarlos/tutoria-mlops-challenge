from fastapi import APIRouter

from src.api.model_loader import load_model
from src.api.schemas import PredictRequest, PredictResponse
from src.api.services import predict_sentiment

router = APIRouter()

# Load model once at module import time
model = load_model()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    return predict_sentiment(model, req)
