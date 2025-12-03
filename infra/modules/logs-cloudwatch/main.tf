// main.tf
// Generic CloudWatch Logs group module.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_cloudwatch_log_group" "this" {
  name              = var.log_group_name
  retention_in_days = var.retention_in_days

  # If kms_key_id is an empty string, AWS provider will ignore it.
  kms_key_id = var.kms_key_id != "" ? var.kms_key_id : null

  tags = local.merged_tags
}
