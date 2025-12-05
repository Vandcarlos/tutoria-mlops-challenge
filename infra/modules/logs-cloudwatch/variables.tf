// variables.tf
// Public interface for the generic CloudWatch Logs module.

variable "name_prefix" {
  description = "prefix name of the CloudWatch Logs group (e.g. /ecs/tutoria-mlops-prod-mlflow)"
  type        = string
}

variable "retention_in_days" {
  description = "Retention period in days for the log group"
  type        = number
  default     = 14
}

variable "kms_key_id" {
  description = "Optional KMS key ID or ARN to encrypt the log group. If empty, no custom KMS is used."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags to apply to the CloudWatch Logs group"
  type        = map(string)
  default     = {}
}
