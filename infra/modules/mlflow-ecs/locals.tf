// locals.tf
// Naming conventions for the mlflow-ecs module.

locals {
  name_prefix     = "${var.project_name}-${var.environment}-mlflow"
  container_name  = "mlflow"
  log_group_name  = "/ecs/${local.name_prefix}"
}
