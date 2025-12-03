// locals.tf
// Base tags for the CloudWatch Logs group.

locals {
  base_tags = {
    ManagedBy = "Terraform"
    Component = "logs-cloudwatch"
  }

  merged_tags = merge(local.base_tags, var.tags)
}
