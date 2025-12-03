module "alb_mlflow" {
  source = "../../modules/alb"

  project_name = "tutoria-mlops"
  environment  = "prod"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnet_ids

  # Para o MLflow, vamos expor direto na porta 5000 (externo = interno)
  internal           = false
  listener_port      = 5000
  listener_protocol  = "HTTP"
  target_group_port  = 5000
  target_group_protocol = "HTTP"
  health_check_path  = "/"

  # Em prod, idealmente restringir isso pro seu IP/office/VPN
  allowed_ingress_cidrs = [
    "0.0.0.0/0" # temporariamente; depois você troca por seu /32 ou VPN
  ]

  tags = {
    Service = "mlflow"
  }
}

output "mlflow_alb_dns_name" {
  description = "DNS name for the MLflow ALB"
  value       = module.alb_mlflow.alb_dns_name
}
