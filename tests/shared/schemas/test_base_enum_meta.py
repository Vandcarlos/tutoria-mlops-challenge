from enum import Enum

import pytest

from src.shared.schemas.BaseEnumMeta import BaseEnumMeta


@pytest.mark.parametrize(
    "raw_value, expected_name",
    [
        (0, "UNKNOWN"),
        (1, "ONE"),
        (2, "TWO"),
        (999, "UNKNOWN"),
    ],
)
def test_base_enum_meta_falls_back_to_unknown(raw_value, expected_name):
    """BaseEnumMeta should fall back to UNKNOWN on invalid values."""

    class DummyEnum(Enum, metaclass=BaseEnumMeta):
        UNKNOWN = 0
        ONE = 1
        TWO = 2

    assert DummyEnum(raw_value).name == expected_name
