module "ecs_cluster" {
  source = "../../modules/ecs-cluster"

  project_name             = "tutoria-mlops"
  environment              = "prod"
  aws_region               = "us-east-1"
  enable_container_insights = true

  tags = {
    Owner = "vand"
  }
}
