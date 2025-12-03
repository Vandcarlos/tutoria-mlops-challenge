// outputs.tf
// Public outputs for the IAM task module.

output "task_role_arn" {
  description = "ARN of the IAM role assumed by the ECS task (application role)"
  value       = aws_iam_role.task_role.arn
}

output "task_role_name" {
  description = "Name of the IAM task role"
  value       = aws_iam_role.task_role.name
}

output "execution_role_arn" {
  description = "ARN of the IAM execution role used by ECS agent"
  value       = aws_iam_role.execution_role.arn
}

output "execution_role_name" {
  description = "Name of the IAM execution role"
  value       = aws_iam_role.execution_role.name
}
