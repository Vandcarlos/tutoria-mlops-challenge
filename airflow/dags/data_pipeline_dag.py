from datetime import datetime

from airflow.operators.bash import BashOperator
from config import (
    AWS_MODEL_ECS_CONTAINER_NAME,
    AWS_MODEL_ECS_TASK_DEFINITION,
    AWS_MODEL_NETWORK_CONFIGURATION,
    DEFAULT_OWNER,
    LOCAL,
)
from factories.ecs_operator_factory import ecs_operator_factory

from airflow import DAG

INGEST_STEP_NAME = "ingest"
SPLIT_STEP_NAME = "split_batches"

with DAG(
    dag_id="data_pipeline_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args={
        "owner": DEFAULT_OWNER,
    },
    tags=["mlops", "data"],
) as dag:
    if LOCAL:
        ingest_raw_data = BashOperator(
            task_id=INGEST_STEP_NAME,
            bash_command=f"cd /opt/airflow && python -m src.model.dispatcher {INGEST_STEP_NAME}",
        )

        split_train_into_batches = BashOperator(
            task_id=SPLIT_STEP_NAME,
            bash_command=f"cd /opt/airflow && python -m src.model.dispatcher {SPLIT_STEP_NAME}",
        )
    else:
        ingest_raw_data = ecs_operator_factory(
            step_name=INGEST_STEP_NAME,
            task_definition=AWS_MODEL_ECS_TASK_DEFINITION,
            container_name=AWS_MODEL_ECS_CONTAINER_NAME,
            network_configuration=AWS_MODEL_NETWORK_CONFIGURATION,
        )

        split_train_into_batches = ecs_operator_factory(
            step_name=SPLIT_STEP_NAME,
            task_definition=AWS_MODEL_ECS_TASK_DEFINITION,
            container_name=AWS_MODEL_ECS_CONTAINER_NAME,
            network_configuration=AWS_MODEL_NETWORK_CONFIGURATION,
        )

    ingest_raw_data >> split_train_into_batches
