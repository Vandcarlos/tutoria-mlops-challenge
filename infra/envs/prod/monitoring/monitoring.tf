data "aws_caller_identity" "current" {}

locals {
  aws_account_id = data.aws_caller_identity.current.account_id
}

module "monitoring_training_task" {
  source = "../../../modules/ecs-task"

  name = "${var.project_name}-${var.environment}-monitoring-training"

  cpu    = 1024
  memory = 2048

  container_image = "${module.ecr_training.repository_url}:monitoring-latest"

  cluster_arn        = var.ecs_cluster_arn
  execution_role_arn = module.iam_monitoring.execution_role_arn
  task_role_arn      = module.iam_monitoring.task_role_arn

  log_group_name = "/ecs/${var.project_name}/${var.environment}/monitoring-training"

  environment = {
    ENVIRONMENT = var.environment
    AWS_REGION  = var.aws_region

    MLFLOW_TRACKING_URI          = var.mlflow_tracking_uri
    MLFLOW_EXPERIMENT_NAME       = "amazon-reviews-training"
    S3_DATA_BUCKET               = var.data_bucket_name
    ALLOW_RUNTIME_MODEL_DOWNLOAD = true
  }
}
