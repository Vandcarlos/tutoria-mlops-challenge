// variables.tf
// Public interface for the generic IAM task module.
// This module creates the application task role and the ECS execution role.

variable "name_prefix" {
  description = "Prefix used for naming IAM roles and policies (e.g. tutoria-mlops-prod-mlflow)"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket that the task is allowed to access (e.g. arn:aws:s3:::my-bucket)"
  type        = string
}

variable "tags" {
  description = "Additional tags to apply to IAM resources where supported"
  type        = map(string)
  default     = {}
}
