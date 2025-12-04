module "shared_env" {
  source       = "./shared"
  owner        = var.owner
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

}

module "mlflow_env" {
  source       = "./mlflow"
  owner        = var.owner
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  vpc_id             = module.shared.vpc_id
  private_subnet_ids = module.shared.private_subnet_ids
  public_subnet_ids  = module.shared.public_subnet_ids
  vpc_cidr_block     = module.shared.vpc_cidr_block
  ecs_cluster_arn    = module.shared.ecs_cluster_arn

  mlflow_db_password = var.mlflow_db_password
}

module "data_bucket_env" {
  source       = "./data_bucket"
  environment  = var.environment
  project_name = var.project_name
  aws_region   = var.aws_region
}

module "model_env" {
  source       = "./model"
  owner        = var.owner
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  ecs_cluster_arn = module.shared.ecs_cluster_arn

  data_bucket_arn     = module.data_bucket_env.data_bucket_arn
  data_bucket_name    = module.data_bucket_env.data_bucket_name
  mlflow_tracking_uri = module.mlflow_env.mlflow_ui_url
}

module "monitoring_env" {
  source       = "./monitoring"
  owner        = var.owner
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  ecs_cluster_arn = module.shared.ecs_cluster_arn

  data_bucket_arn     = module.data_bucket_env.data_bucket_arn
  data_bucket_name    = module.data_bucket_env.data_bucket_name
  mlflow_tracking_uri = module.mlflow_env.mlflow_ui_url
}

module "api_env" {
  source = "./api"

  owner        = var.owner
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  vpc_id             = module.shared.vpc_id
  private_subnet_ids = module.shared.private_subnet_ids
  public_subnet_ids  = module.shared.public_subnet_ids
  vpc_cidr_block     = module.shared.vpc_cidr_block
  ecs_cluster_arn    = module.shared.ecs_cluster_arn

  data_bucket_arn     = module.data_bucket_env.data_bucket_arn
  data_bucket_name    = module.data_bucket_env.data_bucket_name
  mlflow_tracking_uri = module.mlflow_env.mlflow_ui_url
}
