from src.api.schemas import PredictRequest, PredictResponse
from src.shared.schemas import PredictionLabel


def _build_payload(req: PredictRequest) -> list[str]:
    payload = req.title + req.message

    return [payload]


def predict_sentiment(model, req: PredictRequest) -> PredictResponse:
    """Execute the prediction pipeline using the given model."""

    payload = _build_payload(req=req)

    print("payload", payload)

    prediction = model.predict(payload)[0]
    label = PredictionLabel(prediction)

    proba = model.predict_proba(payload)[0]
    confidence = float(max(proba))

    print("direct prediction", model.predict(payload)[0])

    return PredictResponse(
        label=label,
        confidence=confidence,
    )
