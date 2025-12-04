// locals.tf
// Naming conventions for the mlflow-ecs module.

data "aws_region" "current" {}

locals {
  name_prefix    = "${var.project_name}-${var.environment}-mlflow"
  container_name = "mlflow"
  log_group_name = "/ecs/${local.name_prefix}"
  aws_region     = data.aws_region.current.name

}
