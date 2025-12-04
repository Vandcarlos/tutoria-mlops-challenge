variable "name" {
  description = "Base name for ECS task definition and log group"
  type        = string
}

variable "cpu" {
  description = "Task CPU units for Fargate"
  type        = number
}

variable "memory" {
  description = "Task memory in MiB for Fargate"
  type        = number
}

variable "container_image" {
  description = "Container image URI for the task"
  type        = string
}

variable "cluster_arn" {
  description = "Cluster ARN (used externally when running the task, not directly here)"
  type        = string
}

variable "execution_role_arn" {
  description = "IAM role ARN for ECS task execution"
  type        = string
}

variable "task_role_arn" {
  description = "IAM role ARN assumed by the container at runtime"
  type        = string
}

variable "log_group_name" {
  description = "CloudWatch Logs group name"
  type        = string
}

variable "environment" {
  description = "Environment variables for the container"
  type        = map(string)
  default     = {}
}

variable "command" {
  description = "Default command for the task (can be overridden by run_task)"
  type        = list(string)
  default     = []
}
