// variables.tf
// Public interface for the generic ECS service module.
// This module creates an ECS Fargate Task Definition and Service
// for a single-container workload behind an existing ALB target group.

variable "name_prefix" {
  description = "Prefix used for ECS resources (e.g. tutoria-mlops-prod-mlflow)"
  type        = string
}

variable "cluster_arn" {
  description = "ARN of the ECS cluster where the service will be deployed"
  type        = string
}

variable "cpu" {
  description = "Fargate task CPU units (e.g. 256, 512, 1024)"
  type        = number
}

variable "memory" {
  description = "Fargate task memory in MiB (e.g. 512, 1024, 2048)"
  type        = number
}

variable "subnet_ids" {
  description = "Subnets where ECS tasks will run (usually private subnets)"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security Groups attached to the ECS tasks ENIs"
  type        = list(string)
}

variable "container_image" {
  description = "Container image to run (e.g. ECR image URL)"
  type        = string
}

variable "container_name" {
  description = "Name of the container inside the task definition"
  type        = string
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
}

variable "desired_count" {
  description = "Desired number of tasks for the ECS service"
  type        = number
  default     = 1
}

variable "target_group_arn" {
  description = "ARN of the ALB target group where the service is registered"
  type        = string
}

variable "task_role_arn" {
  description = "IAM role ARN assumed by the ECS task (application role)"
  type        = string
}

variable "execution_role_arn" {
  description = "IAM execution role ARN used by ECS agent (pull image, push logs)"
  type        = string
}

variable "log_group_name" {
  description = "CloudWatch Logs group name to store container logs"
  type        = string
}

variable "assign_public_ip" {
  description = "Whether to assign a public IP to the tasks' ENIs"
  type        = bool
  default     = false
}

variable "environment" {
  description = "Environment variables for the container"
  type        = map(string)
  default     = {}
}

variable "platform_version" {
  description = "Fargate platform version (e.g. LATEST, 1.4.0, 1.5.0)"
  type        = string
  default     = "LATEST"
}

variable "deployment_minimum_healthy_percent" {
  description = "Minimum healthy percent during deployment"
  type        = number
  default     = 100
}

variable "deployment_maximum_percent" {
  description = "Maximum percent during deployment"
  type        = number
  default     = 200
}
