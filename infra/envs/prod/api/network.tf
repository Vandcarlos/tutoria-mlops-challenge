// network.tf
// Bindings to the generic sg-app module.
// Responsible for creating the security group used by MLflow ECS tasks.

module "sg_api" {
  source = "../../../modules/sg-app"

  name_prefix         = local.name_prefix
  vpc_id              = var.vpc_id
  app_port            = var.container_port
  ingress_from_sg_ids = [module.alb_api.security_group_id]
}
