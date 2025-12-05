// locals.tf
// Naming conventions for the mlflow-ecs module.

data "aws_region" "current" {}

locals {
  component             = "mlflow"
  name                  = "${local.component}-${var.environment}"
  container_name        = "mlflow"
  log_group_name_prefix = "/ecs/${local.name}"
  aws_region            = data.aws_region.current.name
}
