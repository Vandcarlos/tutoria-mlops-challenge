// logs.tf
// Bindings to the generic logs-cloudwatch module.
// Responsible for creating a CloudWatch Logs group for the MLflow ECS service.

module "logs_model" {
  source = "../../../modules/logs-cloudwatch"

  name_prefix       = local.log_group_name_prefix
  retention_in_days = 14
}
