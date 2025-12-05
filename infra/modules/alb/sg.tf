# ----------------------------------------
# Security Group for the ALB
# ----------------------------------------

module "sg_alb" {
  source = "../sg"

  name_prefix   = local.name
  vpc_id        = var.vpc_id
  app_port      = var.listener_port
  ingress_cidrs = var.allowed_ingress_cidrs
}
