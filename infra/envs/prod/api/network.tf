// network.tf
// Bindings to the generic sg module.
// Responsible for creating the security group used by MLflow ECS tasks.

module "sg_api" {
  source = "../../../modules/sg"

  name_prefix         = local.name
  vpc_id              = var.vpc_id
  app_port            = 8000
  ingress_from_sg_ids = [module.alb_api.security_group_id]
}
