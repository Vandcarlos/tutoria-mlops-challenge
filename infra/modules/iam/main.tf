// main.tf
// Creates IAM roles and policies for ECS tasks:
// - Task role: assumed by the application container (app permissions, e.g. S3).
// - Execution role: used by the ECS agent (pull images, push logs).

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}