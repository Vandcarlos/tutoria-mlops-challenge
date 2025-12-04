// logs.tf
// Bindings to the generic logs-cloudwatch module.
// Responsible for creating a CloudWatch Logs group for the MLflow ECS service.

module "logs_model" {
  source = "../../../modules/logs-cloudwatch"

  log_group_name    = local.log_group_name
  retention_in_days = 14
}
