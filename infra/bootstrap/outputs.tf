output "infra_role_arn" {
  description = "ARN da role oc-infra-deployer para configurar no GitHub Actions"
  value       = aws_iam_role.oc_infra_deployer.arn
}

output "tf_state_bucket" {
  description = "Name of the S3 bucket used to store the Terraform remote state."
  value       = aws_s3_bucket.tf_state.bucket
}

output "tf_lock_table" {
  description = "Name of the DynamoDB table used for Terraform state locking."
  value       = aws_dynamodb_table.tf_lock.name
}
