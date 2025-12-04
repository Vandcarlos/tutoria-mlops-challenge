// ecs.tf
// Bindings to the generic ecs-service module.
// Responsible for creating ECS Task Definition + Service for API.

module "api_service" {
  source = "../../../modules/ecs-service"

  name_prefix        = local.name_prefix
  cluster_arn        = var.ecs_cluster_arn
  cpu                = 512
  memory             = 1024
  subnet_ids         = var.private_subnet_ids
  security_group_ids = [module.sg_api.security_group_id]

  container_image = "${module.ecr_api.repository_url}:api-latest"
  container_name  = local.container_name
  container_port  = 8000

  desired_count    = 1
  target_group_arn = module.alb_api.target_group_arn

  task_role_arn      = module.iam_api.task_role_arn
  execution_role_arn = module.iam_api.execution_role_arn
  log_group_name     = module.logs_api.log_group_name
  assign_public_ip   = false

  environment = {
    ENVIRONMENT                  = var.environment
    AWS_REGION                   = local.aws_region
    MLFLOW_TRACKING_URI          = var.mlflow_tracking_uri
    MLFLOW_EXPERIMENT_NAME       = "amazon-reviews-api"
    S3_DATA_BUCKET               = var.data_bucket_name
    ALLOW_RUNTIME_MODEL_DOWNLOAD = true
  }
}
