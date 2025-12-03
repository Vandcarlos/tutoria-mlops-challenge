// logs.tf
// Bindings to the generic logs-cloudwatch module.
// Responsible for creating a CloudWatch Logs group for the MLflow ECS service.

module "mlflow_logs" {
  source = "../logs-cloudwatch"

  log_group_name    = local.log_group_name
  retention_in_days = var.log_retention_in_days
}
