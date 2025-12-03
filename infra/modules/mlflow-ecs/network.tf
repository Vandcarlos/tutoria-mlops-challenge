// network.tf
// Bindings to the generic sg-app module.
// Responsible for creating the security group used by MLflow ECS tasks.

module "mlflow_task_sg" {
  source = "../sg-app"

  name_prefix         = local.name_prefix
  vpc_id              = var.vpc_id
  app_port            = var.container_port
  ingress_from_sg_ids = [var.alb_security_group_id]
}
