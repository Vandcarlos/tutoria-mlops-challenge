from pydantic import ValidationError
import pytest

from src.api.schemas import PredictRequest


def test_predict_request_accepts_valid_strings():
    req = PredictRequest(title="Great", message="Amazing product")
    assert req.title == "Great"
    assert req.message == "Amazing product"


def test_predict_request_allows_empty_strings():
    req = PredictRequest(title="", message="")
    assert req.title == ""
    assert req.message == ""


def test_predict_request_rejects_none_title():
    with pytest.raises(ValidationError):
        PredictRequest(title=None, message="Valid")


def test_predict_request_rejects_none_message():
    with pytest.raises(ValidationError):
        PredictRequest(title="Valid", message=None)


@pytest.mark.parametrize("bad_value", [123, 12.5, {}, [], True])
def test_predict_request_rejects_invalid_types_for_title(bad_value):
    with pytest.raises(ValidationError):
        PredictRequest(title=bad_value, message="OK")


@pytest.mark.parametrize("bad_value", [123, 12.5, {}, [], True])
def test_predict_request_rejects_invalid_types_for_message(bad_value):
    with pytest.raises(ValidationError):
        PredictRequest(title="OK", message=bad_value)


def test_predict_request_trim_or_normalization_is_not_applied():
    """Just ensuring schema does NOT alter the input data."""
    req = PredictRequest(title=" Hello ", message=" World ")
    assert req.title == " Hello "
    assert req.message == " World "
