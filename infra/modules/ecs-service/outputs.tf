// outputs.tf
// Public outputs for the ECS service module.

output "service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.this.name
}

output "service_id" {
  description = "ARN of the ECS service"
  value       = aws_ecs_service.this.id
}

output "task_definition_arn" {
  description = "ARN of the current task definition"
  value       = aws_ecs_task_definition.this.arn
}

output "task_family" {
  description = "Task definition family name"
  value       = aws_ecs_task_definition.this.family
}
