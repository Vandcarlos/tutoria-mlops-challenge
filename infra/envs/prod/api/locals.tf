// locals.tf
// Naming conventions for the api-ecs module.
data "aws_region" "current" {}

locals {
  component             = "api"
  name                  = "${var.environment}-${local.component}"
  container_name        = local.component
  log_group_name_prefix = "/ecs/${local.name}"
  aws_region            = data.aws_region.current.name
}
