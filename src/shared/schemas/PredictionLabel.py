from enum import Enum

from src.shared.schemas.BaseEnumMeta import BaseEnumMeta


class PredictionLabel(Enum, metaclass=BaseEnumMeta):
    UNKNOWN = 0
    NEGATIVE = 1
    POSITIVE = 2

    @property
    def sentiment(self):
        sentiment_map = {
            PredictionLabel.UNKNOWN: "Desconhecido",
            PredictionLabel.NEGATIVE: "Negativo",
            PredictionLabel.POSITIVE: "Positivo",
        }

        return sentiment_map[self]
