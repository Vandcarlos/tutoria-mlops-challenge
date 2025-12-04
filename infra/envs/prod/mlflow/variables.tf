variable "owner" {
  type        = string
  description = "Me"
}

variable "project_name" {
  type        = string
  description = "Main project identifier used in tags and resource names."
}

variable "environment" {
  type        = string
  description = "The environment for resource naming and tagging."
}

variable "mlflow_db_password" {
  description = "Master password for the MLflow RDS database"
  type        = string
  sensitive   = true
}

variable "vpc_id" {
  description = "VPC ID where MLflow will run"
  type        = string
}

variable "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for ALB"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS tasks and RDS"
  type        = list(string)
}

variable "ecs_cluster_arn" {
  description = "ARN of the ECS cluster for MLflow service"
  type        = string
}
