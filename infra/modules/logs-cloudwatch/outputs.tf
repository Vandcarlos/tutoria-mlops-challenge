// outputs.tf
// Public outputs for the CloudWatch Logs module.

output "log_group_name" {
  description = "Name of the CloudWatch Logs group"
  value       = aws_cloudwatch_log_group.this.name
}

output "log_group_arn" {
  description = "ARN of the CloudWatch Logs group"
  value       = aws_cloudwatch_log_group.this.arn
}
