// main.tf
// Root terraform configuration for the mlflow-ecs composition module.
// All concrete resources are created by sibling generic modules (ecs-service, iam-task, etc.)

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

// The actual module composition is split across:
// - iam.tf       -> task IAM roles and policies
// - logs.tf      -> CloudWatch Logs group
// - network.tf   -> security group for ECS tasks
// - ecs.tf       -> ECS task definition + service
