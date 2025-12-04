// ecs.tf
// Bindings to the generic ecs-service module.
// Responsible for creating ECS Task Definition + Service for MLflow.

module "mlflow_ecs_service" {
  source = "../ecs-service"

  name_prefix        = local.name_prefix
  cluster_arn        = var.ecs_cluster_arn
  cpu                = var.container_cpu
  memory             = var.container_memory
  subnet_ids         = var.private_subnet_ids
  security_group_ids = [module.mlflow_task_sg.security_group_id]

  container_image = var.container_image
  container_name  = local.container_name
  container_port  = var.container_port

  desired_count    = var.desired_count
  target_group_arn = var.alb_target_group_arn

  task_role_arn      = module.mlflow_task_iam.task_role_arn
  execution_role_arn = module.mlflow_task_iam.execution_role_arn
  log_group_name     = module.mlflow_logs.log_group_name
  assign_public_ip   = false

  environment = {
    ENVIRONMENT                  = var.environment
    AWS_REGION                   = local.aws_region
    MLFLOW_BACKEND_STORE_URI     = var.mlflow_backend_store_uri
    MLFLOW_ARTIFACT_ROOT         = var.mlflow_artifact_root
    ALLOW_RUNTIME_MODEL_DOWNLOAD = true
  }
}
