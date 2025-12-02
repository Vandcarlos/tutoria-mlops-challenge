from __future__ import annotations

from datetime import datetime, timedelta

from airflow.operators.bash import BashOperator

from airflow import DAG

"""
Daily monitoring DAG for prediction drift using Evidently.

This DAG:
- Loads reference predictions (or generates them if missing)
- Loads recent prediction logs
- Builds an Evidently drift report (HTML + JSON snapshot)
- Logs monitoring artifacts to MLflow

All of this is handled inside:
    src.monitoring.generate_drift_reports.main()
"""

DEFAULT_OWNER = "mlops-challenge"


with DAG(
    dag_id="monitoring_data_dag",
    description="Daily prediction drift monitoring using Evidently.",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 3 * * *",  # Every day at 03:00
    catchup=False,
    default_args={
        "owner": DEFAULT_OWNER,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["mlops", "monitoring", "drift"],
) as dag:
    run_prediction_drift_report = BashOperator(
        task_id="run_prediction_drift_report",
        bash_command=(
            "cd /opt/airflow && python -m src.monitoring.generate_drift_reports"
        ),
    )
