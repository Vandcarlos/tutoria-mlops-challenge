import logging

from airflow.models import Variable

LOCAL = Variable.get("LOCAL_MODE", default_var="true") == "true"
DEFAULT_OWNER = "mlops-challenge"
AWS_CONN_ID = "aws_default"
AWS_ECS_CLUSTER = "tutoria-mlops-challenge-prod-cluster"
AWS_ECS_LAUNCH_TYPE = "FARGATE"

AWS_NETWORK_CONFIGURATION = {
    "awsvpcConfiguration": {
        "subnets": ["subnet-08324cf27c208f988", "subnet-07228b09bd91629d1"],
        "securityGroups": ["sg-0ea21ef4fcaf3b116"],
        "assignPublicIp": "DISABLED",
    }
}

AWS_MODEL_ECS_TASK_DEFINITION = Variable.get(
    "AWS_MODEL_ECS_TASK_DEFINITION", default_var="prod-model:5"
)
AWS_MODEL_ECS_CONTAINER_NAME = Variable.get(
    "AWS_MODEL_ECS_CONTAINER_NAME", default_var="prod-model"
)
AWS_MONITORING_ECS_TASK_DEFINITION = Variable.get(
    "AWS_MONITORING_ECS_TASK_DEFINITION", default_var="prod-monitoring:2"
)
AWS_MONITORING_ECS_CONTAINER_NAME = Variable.get(
    "AWS_MONITORING_ECS_CONTAINER_NAME", default_var="prod-monitoring"
)

if LOCAL:
    logging.info("[CONFIG]: Runing local mode")
else:
    logging.info("[CONFIG]: Runing cloud mode")
