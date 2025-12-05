from airflow.models import Variable

LOCAL = Variable.get("LOCAL_MODE", default_var="true") == "true"
DEFAULT_OWNER = "mlops-challenge"
AWS_CONN_ID = "aws_default"
AWS_ECS_CLUSTER = "tutoria-mlops-challenge-prod-cluster"
AWS_ECS_LAUNCH_TYPE = "FARGATE"
AWS_MODEL_ECS_TASK_DEFINITION = "prod-model:1"
AWS_MODEL_ECS_CONTAINER_NAME = "prod-model"
AWS_MODEL_NETWORK_CONFIGURATION = {
    "awsvpcConfiguration": {
        "subnets": ["subnet-0ee212f2eb57a5e12", "subnet-08cc88ca7b3001cb8"],
        "securityGroups": ["sg-0b112a18f84ca8a72"],
        "assignPublicIp": "DISABLED",
    }
}

AWS_MONITORING_ECS_TASK_DEFINITION = "prod-monitoring:1"
AWS_MONITORING_ECS_CONTAINER_NAME = "prod-monitoring"
AWS_MONITORING_NETWORK_CONFIGURATION = {
    "awsvpcConfiguration": {
        "subnets": ["subnet-0ee212f2eb57a5e12", "subnet-08cc88ca7b3001cb8"],
        "securityGroups": ["sg-0b112a18f84ca8a72"],
        "assignPublicIp": "DISABLED",
    }
}
