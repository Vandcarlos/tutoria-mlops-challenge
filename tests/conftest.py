from unittest.mock import MagicMock

import pytest


@pytest.fixture
def model_version_factory():
    def _factory(version, stage=None, name="sentiment-logreg-tfidf"):
        mv = MagicMock()
        mv.version = str(version)
        mv.current_stage = stage
        mv.name = name
        return mv

    return _factory
