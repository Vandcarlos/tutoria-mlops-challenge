import re

import pandas as pd

import mlflow
from src.model import config as cfg


def _title_and_text_null_treatment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handles null values in title and text columns.

    - Removes rows where BOTH title and text are null.
    - Fills remaining null values (title OR text individually null) with empty strings.
    - Logs metrics to MLflow for auditing and reproducibility.

    Returns:
        pd.DataFrame: cleaned dataframe with valid title/text content.
    """

    if cfg.DATASET_TITLE_COLUMN not in df.columns:
        raise KeyError(f"Column '{cfg.DATASET_TITLE_COLUMN}' not found in DataFrame")

    if cfg.DATASET_MESSAGE_COLUMN not in df.columns:
        raise KeyError(f"Column '{cfg.DATASET_MESSAGE_COLUMN}' not found in DataFrame")

    ## Remove rows when both is null
    mask_both_null = (
        df[cfg.DATASET_TITLE_COLUMN].isna() & df[cfg.DATASET_MESSAGE_COLUMN].isna()
    )
    rows_to_remove_count = int(mask_both_null.sum())

    df = df.loc[~mask_both_null].copy()

    ## Fill empty remaing rows
    title_null_count = df[cfg.DATASET_TITLE_COLUMN].isna().sum()
    text_null_count = df[cfg.DATASET_MESSAGE_COLUMN].isna().sum()
    df[cfg.DATASET_TITLE_COLUMN] = df[cfg.DATASET_TITLE_COLUMN].fillna("")
    df[cfg.DATASET_MESSAGE_COLUMN] = df[cfg.DATASET_MESSAGE_COLUMN].fillna("")

    mlflow.log_metric("rows_dropped_title_text_null", rows_to_remove_count)
    mlflow.log_metric("rows_title_null_filled", title_null_count)
    mlflow.log_metric("rows_text_null_filled", text_null_count)

    return df


def _preprocess_record(title: str, message: str) -> str:
    """
    Combines title and message into a single string and applies basic normalization:
    - lowercasing
    - removal of URLs
    - normalization of whitespace

    Returns:
        str: new text concactaned title and message, and removed withspaces and URLs
    """

    combined = f"{title} {message}".strip().lower()

    # Remove URLs
    combined = re.sub(r"http\S+", "", combined)

    # Normalize whitespace
    combined = re.sub(r"\s+", " ", combined)

    return combined


def _build_full_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a new 'full_text' column containing the normalized combination
    of title + text. Removes the original title/text columns afterwards.

    Returns:
        pd.DataFrame: dataframe containing only full_text instead of title/text.
    """
    df[cfg.DATASET_FULL_TEXT_COLUMN] = df.apply(
        lambda row: _preprocess_record(
            title=row[cfg.DATASET_TITLE_COLUMN], message=row[cfg.DATASET_MESSAGE_COLUMN]
        ),
        axis=1,
    )

    rows_before = len(df)
    df = df[df[cfg.DATASET_FULL_TEXT_COLUMN].str.len() > 0].copy()
    rows_after = len(df)

    df = df.drop(columns=[cfg.DATASET_TITLE_COLUMN, cfg.DATASET_MESSAGE_COLUMN])

    mlflow.log_metric("rows_dropped_empty_full_text", rows_before - rows_after)

    return df


def preprocess_df(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the df_raw.
    """

    df = _title_and_text_null_treatment(df=df_raw)
    df = _build_full_text(df=df)

    return df
