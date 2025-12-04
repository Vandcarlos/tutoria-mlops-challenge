// locals.tf
// Derived values and naming helpers.

data "aws_region" "current" {}

locals {
  task_family  = "${var.name_prefix}-task"
  service_name = "${var.name_prefix}-service"
  aws_region = data.aws_region.current.name
}
