module "monitoring_task" {
  source = "../../../modules/ecs-task"

  name = local.name

  cpu    = 1024
  memory = 2048

  container_image = "${module.ecr_monitoring.repository_url}:${local.container_name}-latest"

  cluster_arn        = var.ecs_cluster_arn
  execution_role_arn = module.iam_monitoring.execution_role_arn
  task_role_arn      = module.iam_monitoring.task_role_arn

  log_group_name = module.logs_monitoring.log_group_name

  environment = {
    ENVIRONMENT = var.environment
    AWS_REGION  = local.aws_region

    MLFLOW_TRACKING_URI          = var.mlflow_tracking_uri
    MLFLOW_EXPERIMENT_NAME       = "amazon-reviews-monitoring"
    S3_DATA_BUCKET               = var.data_bucket_name
    ALLOW_RUNTIME_MODEL_DOWNLOAD = true
  }
}
