module "model_task" {
  source = "../../../modules/ecs-task"

  name = local.name

  cpu    = 1024
  memory = 4096

  container_image = "${module.ecr_model.repository_url}:${local.container_name}-latest"

  cluster_arn        = var.ecs_cluster_arn
  execution_role_arn = module.iam_model.execution_role_arn
  task_role_arn      = module.iam_model.task_role_arn

  log_group_name = module.logs_model.log_group_name

  environment = {
    ENVIRONMENT      = var.environment
    AWS_REGION       = local.aws_region
    PYTHONUNBUFFERED = "1"

    MLFLOW_TRACKING_URI    = var.mlflow_tracking_uri
    MLFLOW_EXPERIMENT_NAME = "amazon-reviews-model"
    S3_DATA_BUCKET         = var.data_bucket_name
  }
}
