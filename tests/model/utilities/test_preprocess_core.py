import pandas as pd
import pytest

import src.model.utilities.preprocess_core as preprocess_core


def _test_title_and_text_null_treatment_fills_no_nulls():
    df_input = pd.DataFrame(
        {
            "title": ["Title 1", None, "Title 3"],
            "message": [None, "Message 2", None],
        }
    )

    df_cleaned = preprocess_core._title_and_text_null_treatment(df_input)

    assert len(df_cleaned) == len(df_input)
    assert df_cleaned["title"].isna().sum() == 0
    assert df_cleaned["message"].isna().sum() == 0


def _test_title_and_text_remove_both_nulls_columns():
    df_input = pd.DataFrame(
        {
            "title": ["Title 1", None, None],
            "message": [None, "Message 2", None],
        }
    )

    df_cleaned = preprocess_core._title_and_text_null_treatment(df_input)

    assert len(df_cleaned) == 1
    assert df_cleaned["title"].isna().sum() == 0
    assert df_cleaned["message"].isna().sum() == 0


def test_title_and_text_null_treatment_raises_keyerror_on_missing_columns():
    df_missing_title = pd.DataFrame({"message": ["Message 1", "Message 2"]})
    df_missing_message = pd.DataFrame({"title": ["Title 1", "Title 2"]})

    with pytest.raises(KeyError):
        preprocess_core._title_and_text_null_treatment(df_missing_title)

    with pytest.raises(KeyError):
        preprocess_core._title_and_text_null_treatment(df_missing_message)


@pytest.mark.parametrize(
    "title, message, expected",
    [
        (
            "Hello World",
            "This is a test message.",
            "hello world this is a test message.",
        ),
        (
            "Check this out",
            "Visit https://example.com for more info.",
            "check this out visit for more info.",
        ),
        (
            "   Leading and trailing spaces   ",
            "   Multiple    spaces   here.   ",
            "leading and trailing spaces multiple spaces here.",
        ),
        ("No URLs here", "Just some text.", "no urls here just some text."),
        ("", "", ""),
    ],
)
def test_preprocess_record(title, message, expected):
    result = preprocess_core._preprocess_record(title, message)
    assert result == expected


def test_build_full_text():
    df_input = pd.DataFrame(
        {
            "title": ["Hello World", "Check this out", "   ", "No URLs here", ""],
            "message": [
                "This is a test message.",
                "Visit https://example.com for more info.",
                "   ",
                "Just some text.",
                "",
            ],
        }
    )

    df_processed = preprocess_core._build_full_text(df_input)

    expected_texts = [
        "hello world this is a test message.",
        "check this out visit for more info.",
        "no urls here just some text.",
    ]

    assert len(df_processed) == len(expected_texts)
    for i, expected in enumerate(expected_texts):
        assert df_processed.iloc[i]["full_text"] == expected


def test_preprocess_df():
    df_input = pd.DataFrame(
        {
            "title": ["Hello World", None, "   ", "No URLs here", ""],
            "message": [
                "This is a test message.",
                "Visit https://example.com for more info.",
                None,
                "Just some text.",
                "",
            ],
        }
    )

    df_processed = preprocess_core.preprocess_df(df_input)

    expected_texts = [
        "hello world this is a test message.",
        "visit for more info.",
        "no urls here just some text.",
    ]

    assert len(df_processed) == len(expected_texts)
    assert len(df_processed.columns) == 1
    for i, expected in enumerate(expected_texts):
        assert df_processed.iloc[i]["full_text"] == expected
