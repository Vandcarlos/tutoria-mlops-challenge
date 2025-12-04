// locals.tf
// Naming conventions for the monitoring-ecs module.

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  name_prefix    = "${var.project_name}-${var.environment}-monitoring"
  log_group_name = "/ecs/${local.name_prefix}"
  aws_account_id = data.aws_caller_identity.current.account_id
  aws_region     = data.aws_region.current.name

}
