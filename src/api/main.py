from fastapi import FastAPI
from pydantic import BaseModel

from .model_loader import load_model

app = FastAPI(title="Sentiment API")

model = load_model()


class PredictRequest(BaseModel):
    title: str
    message: str


class PredictResponse(BaseModel):
    sentiment: str
    score: float | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # Exemplo: concatenar title + message
    text = f"{req.title}. {req.message}"

    # Aqui depende de como seu modelo espera os dados
    preds = model.predict([text])
    pred = preds[0]

    # Ajuste conforme seu modelo (0/1, probas, etc.)
    label = "positive" if pred == 2 else "negative"

    return PredictResponse(sentiment=label, score=None)
