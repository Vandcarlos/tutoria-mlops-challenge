from pydantic import BaseModel


class PredictRequest(BaseModel):
    title: str
    message: str
