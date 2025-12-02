from datetime import datetime

from airflow.operators.bash import BashOperator

from airflow import DAG

with DAG(
    dag_id="data_pipeline_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["mlops", "data"],
) as dag:
    ingest_raw_data = BashOperator(
        task_id="ingest_raw_data",
        bash_command="cd /opt/airflow && python -m src.model.data.ingest",
    )

    split_train_into_batches = BashOperator(
        task_id="split_train_into_batches",
        bash_command="cd /opt/airflow && python -m src.model.data.split_batches",
    )

    ingest_raw_data >> split_train_into_batches
