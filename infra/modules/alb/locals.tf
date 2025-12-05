// locals.tf
// Naming helpers and base tags for the ALB resources.

locals {
  component = "alb"
  name      = "${var.name_prefix}-${local.component}"
  tg_name   = "${local.name}-tg"

  base_tags = {
    Name      = local.name
    Component = local.component
  }

  merged_tags = merge(local.base_tags, var.tags)
}
