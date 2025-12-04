data "aws_caller_identity" "current" {}

locals {
  mlflow_backend_store_uri = "postgresql+psycopg2://${module.mlflow_db.username}:${var.mlflow_db_password}@${module.mlflow_db.endpoint}:${module.mlflow_db.port}/${module.mlflow_db.db_name}"
  mlflow_artifact_root     = "s3://${module.mlflow_artifacts_bucket.bucket_name}"
  aws_account_id           = data.aws_caller_identity.current.account_id
}

module "mlflow" {
  source = "../../../modules/mlflow-ecs"

  project_name = var.project_name
  environment  = var.environment

  vpc_id             = var.vpc_id
  private_subnet_ids = var.private_subnet_ids

  ecs_cluster_arn = var.ecs_cluster_arn

  alb_target_group_arn  = module.alb_mlflow.target_group_arn
  alb_security_group_id = module.alb_mlflow.security_group_id

  mlflow_backend_store_uri   = local.mlflow_backend_store_uri
  mlflow_artifact_root       = local.mlflow_artifact_root
  mlflow_artifact_bucket_arn = module.mlflow_artifacts_bucket.bucket_arn

  container_image = "${module.ecr_mlflow.repository_url}:mlflow-latest"

  container_cpu    = 512
  container_memory = 1024
  desired_count    = 1
  container_port   = 5000

  log_retention_in_days = 14
}

output "mlflow_ui_url" {
  description = "External URL to access the MLflow UI"
  value       = "http://${module.alb_mlflow.alb_dns_name}"
}
