// locals.tf
// Naming helpers and base tags for the ALB resources.

locals {
  name_prefix = "${var.project_name}-${var.environment}-alb"

  base_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Component   = "alb"
  }

  merged_tags = merge(local.base_tags, var.tags)
}
