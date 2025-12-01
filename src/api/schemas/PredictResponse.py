from pydantic import BaseModel, computed_field, field_serializer

from src.shared.schemas import PredictionLabel


class PredictResponse(BaseModel):
    label: PredictionLabel
    confidence: float

    @field_serializer("label")
    def serialize_label(self, label: PredictionLabel):
        return label.value

    @computed_field(return_type=str)
    @property
    def label_name(self) -> str:
        return self.label.name

    @computed_field(return_type=str)
    @property
    def sentiment(self) -> str:
        return self.label.sentiment
