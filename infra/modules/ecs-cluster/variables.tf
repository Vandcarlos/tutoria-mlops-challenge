// variables.tf
// Public interface for the generic ECS cluster module.

variable "project_name" {
  description = "Base project name (e.g. tutoria-mlops)"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g. dev, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region where the ECS cluster will be created (e.g. us-east-1)"
  type        = string
}

variable "enable_container_insights" {
  description = "Enable CloudWatch Container Insights for this ECS cluster"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to apply to the ECS cluster"
  type        = map(string)
  default     = {}
}
