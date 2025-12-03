// locals.tf
// Naming helpers and base tags for the application security group.

locals {
  sg_name = "${var.name_prefix}-sg"

  base_tags = {
    Name      = local.sg_name
    ManagedBy = "Terraform"
    Component = "sg-app"
  }

  merged_tags = merge(local.base_tags, var.tags)
}
