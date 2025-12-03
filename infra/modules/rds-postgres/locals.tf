// locals.tf
// Naming helpers and base tags for the RDS PostgreSQL resources.

locals {
  identifier = "${var.project_name}-${var.environment}-postgres"

  base_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Component   = "rds-postgres"
  }

  merged_tags = merge(local.base_tags, var.tags)
}
