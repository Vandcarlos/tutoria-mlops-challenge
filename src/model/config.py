from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Environments
DATASET_LOCAL_PATH = Path(os.getenv("DATASET_LOCAL_PATH", "./data"))
DATASET_RAW_PATH = DATASET_LOCAL_PATH / "raw"
DATASET_RAW_TRAIN_PARQUET = DATASET_RAW_PATH / "train.parquet"
DATASET_RAW_TEST_PARQUET = DATASET_RAW_PATH / "test.parquet"
DATASET_BATCH_PATH = DATASET_LOCAL_PATH / "batches"
DATASET_PROCESSED_PATH = DATASET_LOCAL_PATH / "processed"
DATASET_PROCESSED_TEST_PATH = DATASET_PROCESSED_PATH / "test.parquet"
DATASET_SPLIT_COUNT = int(os.getenv("DATASET_SPLIT_COUNT", "10"))

MLFLOW_MODEL_NAME: str = os.getenv("MLFLOW_MODEL_NAME", "sentiment-logreg-tfidf")

# Constants

KAGGLE_DATASET_NAME = "kritanjalijain/amazon-reviews"
KAGGLE_DATASET_TRAIN_FILENAME = "train.csv"
KAGGLE_DATASET_TEST_FILENAME = "test.csv"

DATASET_POLARITY_COLUMN = "polarity"
DATASET_TITLE_COLUMN = "title"
DATASET_MESSAGE_COLUMN = "message"
DATASET_FULL_TEXT_COLUMN = "full_text"


@dataclass
class TfidfParams:
    max_features: int = 50_000
    min_df: int = 2
    ngram_range: tuple[int, int] = (1, 2)


@dataclass
class ClfParams:
    C: float = 10.0
    penalty: str = "l2"
    solver: str = "lbfgs"
    max_iter: int = 2000


@dataclass
class TrainValSplit:
    test_size: float = 0.2
    random_state: int = 42


TFIDF_PARAMS = TfidfParams()
CLF_PARAMS = ClfParams()
TRAIN_VAL_SPLIT = TrainValSplit()


def DATASET_BATCH_ITEM_PATH(batch_idx: int) -> Path:
    return DATASET_BATCH_PATH / f"train_batch_{batch_idx}.parquet"


def DATASET_PROCESSED_BATCH_ITEM_PATH(batch_idx: int) -> Path:
    return DATASET_PROCESSED_PATH / f"train_batch_{batch_idx}.parquet"
