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

variable "ecs_cluster_arn" {
  description = "ARN of the ECS cluster for Monitoring task"
  type        = string
}

variable "data_bucket_arn" {
  description = "ARN of the data bucket"
  type        = string
}

variable "data_bucket_name" {
  description = "Name of the data bucket"
  type        = string
}

variable "mlflow_tracking_uri" {
  description = "The uri of MLFLOW "
  type        = string
}
