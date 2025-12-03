// outputs.tf

output "repository_name" {
  description = "ECR repository name"
  value       = aws_ecr_repository.this.name
}

output "repository_url" {
  description = "Full ECR repository URL (used on ECS Task Definitions)"
  value       = aws_ecr_repository.this.repository_url
}

output "repository_arn" {
  description = "ARN of the ECR repository"
  value       = aws_ecr_repository.this.arn
}
