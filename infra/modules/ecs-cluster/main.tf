// main.tf
// Generic ECS cluster module for Fargate workloads.
// This module does not create any capacity providers; it simply creates
// a logical ECS cluster that can be used by Fargate services.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_ecs_cluster" "this" {
  name = local.cluster_name

  setting {
    name  = "containerInsights"
    value = var.enable_container_insights ? "enabled" : "disabled"
  }

  tags = local.merged_tags
}
