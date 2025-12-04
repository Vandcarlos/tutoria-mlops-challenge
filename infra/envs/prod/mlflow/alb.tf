module "alb_mlflow" {
  source = "../../../modules/alb"

  project_name = var.project_name
  environment  = var.environment

  vpc_id     = var.vpc_id
  subnet_ids = var.public_subnet_ids

  internal              = false
  listener_port         = 80
  listener_protocol     = "HTTP"
  target_group_port     = 5000
  target_group_protocol = "HTTP"
  health_check_path     = "/"

  allowed_ingress_cidrs = [
    "0.0.0.0/0"
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    Service     = "mlflow"
  }
}

output "mlflow_alb_dns_name" {
  description = "DNS name for the MLflow ALB"
  value       = module.alb_mlflow.alb_dns_name
}
