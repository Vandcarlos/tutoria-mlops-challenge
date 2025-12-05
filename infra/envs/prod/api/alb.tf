module "alb_api" {
  source = "../../../modules/alb"

  name_prefix = local.name

  vpc_id     = var.vpc_id
  subnet_ids = var.public_subnet_ids

  internal              = false
  listener_port         = 80
  listener_protocol     = "HTTP"
  target_group_port     = 8000
  target_group_protocol = "HTTP"
  health_check_path     = "/health"

  allowed_ingress_cidrs = [
    "0.0.0.0/0"
  ]

  tags = {
    Environment = var.environment
    Owner       = var.owner
    Service     = "api"
  }
}

output "api_alb_dns_name" {
  description = "DNS name for the API ALB"
  value       = module.alb_api.alb_dns_name
}
