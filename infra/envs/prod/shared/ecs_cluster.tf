module "ecs_cluster" {
  source = "../../../modules/ecs-cluster"

  project_name              = var.project_name
  environment               = var.environment
  aws_region                = var.aws_region
  enable_container_insights = true

  tags = {
    Owner = var.owner
  }
}
