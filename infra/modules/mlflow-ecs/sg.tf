// network.tf
// Bindings to the generic sg module.
// Responsible for creating the security group used by MLflow ECS tasks.

module "mlflow_task_sg" {
  source = "../sg"

  name_prefix         = local.name
  vpc_id              = var.vpc_id
  app_port            = var.container_port
  ingress_from_sg_ids = [var.alb_security_group_id]
  tags = {

    Environment = var.environment
    ManagedBy = "Terraform"
  }
}
