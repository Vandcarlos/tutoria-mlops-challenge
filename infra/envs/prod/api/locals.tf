// locals.tf
// Naming conventions for the api-ecs module.
data "aws_region" "current" {}

locals {
  name_prefix     = "${var.project_name}-${var.environment}-api"
  container_name  = "api"
  log_group_name  = "/ecs/${local.name_prefix}"
  aws_region     = data.aws_region.current.name
}
