// locals.tf
// Naming conventions and base tags for the ECS cluster.

locals {
  cluster_name = "${var.project_name}-${var.environment}-cluster"

  base_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Component   = "ecs-cluster"
  }

  merged_tags = merge(local.base_tags, var.tags)
}
