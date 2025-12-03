module "shared" {
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
