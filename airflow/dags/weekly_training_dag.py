from __future__ import annotations

from datetime import datetime, timedelta

from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from airflow import DAG

"""
Weekly training DAG for the Amazon Reviews sentiment model.

Strategy:
- Keep an Airflow Variable "current_batch_index" that indicates which batch
  should be added to the training set on this run.
- Each run:
    1) Read current_batch_index (default=0)
    2) Preprocess only that batch (src.model.pipeline.preprocess_batch)
    3) Train model with all batches from 0..current_batch_index
       (using train.py --batches <current_batch_index>)
    4) Evaluate model on the global test set (evaluate.py)
    5) Increment current_batch_index for the next run
"""


DEFAULT_OWNER = "mlops-challenge"
BATCH_INDEX_VARIABLE = "current_batch_index"


def get_current_batch_index(**context) -> int:
    """
    Read the current batch index from Airflow Variables.
    If not set, start from 0.

    The value is pushed to XCom so that other tasks can use it.
    """
    current_value = Variable.get(BATCH_INDEX_VARIABLE, default_var="0")
    batch_index = int(current_value)

    print(f"[DAG] Using current_batch_index={batch_index}")
    context["ti"].xcom_push(key="batch_index", value=batch_index)

    return batch_index


def increment_batch_index(**context) -> None:
    """
    Increment the batch index after a successful training cycle.
    """
    ti = context["ti"]
    batch_index = int(
        ti.xcom_pull(task_ids="get_current_batch_index", key="batch_index")
    )

    next_index = batch_index + 1
    print(f"[DAG] Updating {BATCH_INDEX_VARIABLE} from {batch_index} → {next_index}")
    Variable.set(BATCH_INDEX_VARIABLE, str(next_index))


with DAG(
    dag_id="weekly_training_dag",
    description="Weekly incremental training pipeline using batches (0..k).",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 9 * * MON",  # Every Monday at 09:00
    catchup=False,
    default_args={
        "owner": DEFAULT_OWNER,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["mlops", "training", "retraining"],
) as dag:
    # 1) Decide which batch index we are going to process this week
    get_current_batch_index_task = PythonOperator(
        task_id="get_current_batch_index",
        python_callable=get_current_batch_index,
        provide_context=True,
    )

    # 2) Preprocess ONLY that batch (calls your existing CLI script)
    preprocess_batch_task = BashOperator(
        task_id="preprocess_batch",
        bash_command=(
            "cd /opt/airflow && "
            "python -m src.model.pipeline.preprocess_batch "
            "{{ ti.xcom_pull(task_ids='get_current_batch_index', key='batch_index') }}"
        ),
    )

    # 3) Train model using batches 0..current_batch_index
    #    This leverages train.py logic: --batches N -> uses range(0..N)
    train_model_task = BashOperator(
        task_id="train_model",
        bash_command=(
            "cd /opt/airflow && "
            "python -m src.model.pipeline.train "
            "--batches {{ ti.xcom_pull(task_ids='get_current_batch_index', key='batch_index') }}"
        ),
    )

    # 4) Evaluate model on test set (uses your evaluate.py logic)
    evaluate_model_task = BashOperator(
        task_id="evaluate_model",
        bash_command=("cd /opt/airflow && python -m src.model.pipeline.evaluate"),
    )

    # 5) Update Airflow Variable for the next run
    increment_batch_index_task = PythonOperator(
        task_id="increment_batch_index",
        python_callable=increment_batch_index,
        provide_context=True,
    )

    (
        get_current_batch_index_task
        >> preprocess_batch_task
        >> train_model_task
        >> evaluate_model_task
        >> increment_batch_index_task
    )
