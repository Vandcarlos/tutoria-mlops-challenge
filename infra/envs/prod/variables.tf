variable "project" {
  type        = string
  description = "Main project identifier used in tags and resource names."
}

variable "aws_region" {
  type        = string
  description = "Default AWS region where resources will be created."
}

variable "mlflow_db_password" {
  description = "Master password for the MLflow RDS database"
  type        = string
  sensitive   = true
}

variable "mlflow_container_image" {
  type        = string
  description = "ECR image URL used by the MLflow ECS service"
}