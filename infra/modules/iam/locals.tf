// locals.tf
// Naming helpers and base tags for the IAM resources.

locals {
  task_role_name       = "${var.name_prefix}-task-role"
  execution_role_name  = "${var.name_prefix}-execution-role"
  policy_name          = "${var.name_prefix}-task-policy"

  base_tags = {
    Name       = var.name_prefix
    ManagedBy  = "Terraform"
    Component  = "iam-task"
  }

  merged_tags = merge(local.base_tags, var.tags)
}
