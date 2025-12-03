// outputs.tf
// Public outputs for the application security group module.

output "security_group_id" {
  description = "ID of the application security group"
  value       = aws_security_group.this.id
}

output "security_group_arn" {
  description = "ARN of the application security group"
  value       = aws_security_group.this.arn
}
