// locals.tf
// Naming helpers and tag composition.

locals {
  repo_name = "${var.project_name}/${var.environment}/${var.service_name}"

  base_tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = var.service_name
    Component   = "ecr"
    ManagedBy   = "Terraform"
  }

  merged_tags = merge(local.base_tags, var.tags)
}
