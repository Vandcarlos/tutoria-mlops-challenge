// variables.tf
// Public interface for the generic ECR repository module.

variable "project_name" {
  description = "Base project name (e.g. tutoria-mlops)"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "service_name" {
  description = "Name of the service using this ECR repo (e.g. mlflow, api)"
  type        = string
}

variable "image_mutability" {
  description = "Whether tags can be overwritten (MUTABLE) or not (IMMUTABLE)"
  type        = string
  default     = "MUTABLE"
}

variable "scan_on_push" {
  description = "Whether to enable vulnerability scanning in the ECR repo"
  type        = bool
  default     = true
}

variable "lifecycle_max_images" {
  description = "Maximum number of images to retain in ECR"
  type        = number
  default     = 10
}

variable "tags" {
  description = "Additional tags for the ECR repository"
  type        = map(string)
  default     = {}
}
