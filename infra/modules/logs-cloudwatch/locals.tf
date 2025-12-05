// locals.tf
// Base tags for the CloudWatch Logs group.

locals {
  component = "logs-cloudwatch"
  name      = "${var.name_prefix}-${local.component}"

  base_tags = {
    Component = local.component
  }

  merged_tags = merge(local.base_tags, var.tags)
}
