from pydantic import BaseModel, computed_field, field_serializer

from src.shared.schemas import PredictionLabel


class PredictResponse(BaseModel):
    prediction_label: PredictionLabel
    confidence: float

    @field_serializer("prediction_label")
    def serialize_label(self, label: PredictionLabel):
        return label.value

    @computed_field(return_type=str)
    @property
    def prediction_label_name(self) -> str:
        return self.prediction_label.name

    @computed_field(return_type=str)
    @property
    def sentiment(self) -> str:
        return self.prediction_label.sentiment
