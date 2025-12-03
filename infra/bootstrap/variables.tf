variable "project" {
  type        = string
  description = "Main project identifier used in tags and resource names."
}

variable "aws_region" {
  type        = string
  description = "Default AWS region where resources will be created."
}

variable "repo" {
  description = "GitHub repository allowed to assume the oc-infra-deployer role via OIDC."
  type = object({
    owner     = string
    name      = string
    role_name = string
  })
}

variable "state_bucket_name" {
  type        = string
  description = "Name of the S3 bucket used to store the Terraform remote state."
}

variable "lock_table_name" {
  type        = string
  description = "Name of the DynamoDB table used for Terraform state locking."
}
