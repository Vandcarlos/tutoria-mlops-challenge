// variables.tf
// Public interface for the mlflow-ecs module.
// This module assumes that VPC, ALB, ECS Cluster, RDS and S3 buckets
// are created by other modules. Here we only compose ECS service + IAM + SG + Logs.

variable "project_name" {
  description = "Base project name (e.g. tutoria-mlops)"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g. dev, prod)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the ECS tasks will run"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for ECS tasks"
  type        = list(string)
}

variable "alb_target_group_arn" {
  description = "ARN of the ALB target group used by the MLflow ECS service"
  type        = string
}

variable "alb_security_group_id" {
  description = "Security group ID attached to the ALB that fronts MLflow"
  type        = string
}

variable "ecs_cluster_arn" {
  description = "ARN of the ECS cluster where MLflow service will be deployed"
  type        = string
}

variable "mlflow_backend_store_uri" {
  description = "MLflow backend store URI (e.g. postgresql+psycopg2://user:pass@host:5432/db)"
  type        = string
}

variable "mlflow_artifact_root" {
  description = "MLflow artifact root (e.g. s3://my-mlflow-artifacts)"
  type        = string
}

variable "mlflow_artifact_bucket_arn" {
  description = "ARN of the S3 bucket used as MLflow artifact store (e.g. arn:aws:s3:::my-mlflow-artifacts)"
  type        = string
}

variable "container_image" {
  description = "Docker image for the MLflow server (e.g. <account>.dkr.ecr.<region>.amazonaws.com/mlflow:latest)"
  type        = string
}

variable "container_cpu" {
  description = "CPU units for the Fargate task (256 = 0.25 vCPU, 512 = 0.5 vCPU, etc.)"
  type        = number
  default     = 512
}

variable "container_memory" {
  description = "Memory in MiB for the Fargate task (e.g. 1024, 2048)"
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "Desired number of MLflow ECS tasks"
  type        = number
  default     = 1
}

variable "container_port" {
  description = "Port exposed by the MLflow container"
  type        = number
  default     = 5000
}

variable "log_retention_in_days" {
  description = "CloudWatch Logs retention in days for the MLflow log group"
  type        = number
  default     = 14
}
