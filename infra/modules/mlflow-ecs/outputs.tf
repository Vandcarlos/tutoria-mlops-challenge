// outputs.tf
// Public outputs exposed by the mlflow-ecs module.

output "mlflow_service_name" {
  description = "Name of the ECS service running MLflow"
  value       = module.mlflow_ecs_service.service_name
}

output "mlflow_cluster_arn" {
  description = "ARN of the ECS cluster where MLflow is running"
  value       = var.ecs_cluster_arn
}

output "mlflow_task_security_group_id" {
  description = "Security group ID attached to the MLflow ECS tasks"
  value       = module.mlflow_task_sg.security_group_id
}

output "mlflow_log_group_name" {
  description = "CloudWatch Logs group name used by the MLflow ECS service"
  value       = module.mlflow_logs.log_group_name
}
