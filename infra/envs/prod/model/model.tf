module "model_task" {
  source = "../../../modules/ecs-task"

  name = "${var.project_name}-${var.environment}-model-model"

  cpu    = 1024
  memory = 2048

  container_image = "${module.ecr_model.repository_url}:model-latest"

  cluster_arn        = var.ecs_cluster_arn
  execution_role_arn = module.iam_model.execution_role_arn
  task_role_arn      = module.iam_model.task_role_arn

  log_group_name     = module.logs_api.log_group_name

  environment = {
    ENVIRONMENT = var.environment
    AWS_REGION  = local.aws_region

    MLFLOW_TRACKING_URI    = var.mlflow_tracking_uri
    MLFLOW_EXPERIMENT_NAME = "amazon-reviews-model"
    S3_DATA_BUCKET         = var.data_bucket_name
  }
}
