import time

from sklearn.pipeline import Pipeline

from src.api.monitoring_logger import LocalPredictionLogger
from src.api.schemas import PredictRequest, PredictResponse
from src.shared.schemas import PredictionLabel


def _build_payload(req: PredictRequest) -> list[str]:
    payload = req.title + req.message

    return [payload]


def predict_sentiment(
    req: PredictRequest,
    model: Pipeline,
    logger: LocalPredictionLogger,
) -> PredictResponse:
    """Execute the prediction pipeline using the given model."""

    start_time = time.perf_counter()

    payload = _build_payload(req=req)

    print("payload", payload)

    prediction = model.predict(payload)[0]
    prediction_label = PredictionLabel(prediction)

    proba = model.predict_proba(payload)[0]
    confidence = float(max(proba))
    latency_ms = (time.perf_counter() - start_time) * 1000.0

    print("direct prediction", model.predict(payload)[0])

    try:
        logger.log_prediction(
            title=req.title,
            message=req.message,
            full_text=payload[0],
            predicted_label=prediction,
            predicted_label_name=prediction_label.name,
            confidence=confidence,
            latency_ms=latency_ms,
        )
    except Exception as e:
        print(f"Failed to log prediction: {e}")
        pass

    return PredictResponse(
        prediction_label=prediction_label,
        confidence=confidence,
    )
