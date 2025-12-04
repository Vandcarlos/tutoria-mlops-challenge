// locals.tf
// Naming helpers and base tags for the application security group.

locals {
  component = "sg"
  name    = "${var.name_prefix}-${local.component}"

  base_tags = {
    Name      = local.name
    Component = local.component
  }

  merged_tags = merge(local.base_tags, var.tags)
}
