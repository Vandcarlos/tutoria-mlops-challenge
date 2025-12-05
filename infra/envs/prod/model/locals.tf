// locals.tf
// Naming conventions for the monitoring-ecs module.

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  component             = "model"
  name                  = "${var.environment}-${local.component}"
  container_name        = local.component
  log_group_name_prefix = "/ecs/${local.name}"
  aws_account_id        = data.aws_caller_identity.current.account_id
  aws_region            = data.aws_region.current.name
}
