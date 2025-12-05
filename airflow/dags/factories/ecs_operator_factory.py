from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator
from config import AWS_CONN_ID, AWS_ECS_CLUSTER, AWS_ECS_LAUNCH_TYPE


def ecs_operator_factory(
    step_name: str,
    task_definition: str,
    container_name: str,
    network_configuration: dict,
    extra_args: list[str] = None,
) -> EcsRunTaskOperator:
    if extra_args is None:
        extra_args = []

    commandArgs = [step_name] + extra_args

    return EcsRunTaskOperator(
        task_id=f"{step_name}_task",
        cluster=AWS_ECS_CLUSTER,
        task_definition=task_definition,
        launch_type=AWS_ECS_LAUNCH_TYPE,
        network_configuration=network_configuration,
        aws_conn_id=AWS_CONN_ID,
        overrides={
            "containerOverrides": [
                {
                    "name": container_name,
                    "command": commandArgs,
                }
            ]
        },
    )
