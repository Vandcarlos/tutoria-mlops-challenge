// iam.tf
// Bindings to the generic iam-task module.
// Responsible for creating the IAM roles and policies for the MLflow ECS task.

module "mlflow_task_iam" {
  source = "../iam"

  name_prefix   = local.name_prefix
  s3_bucket_arn = var.mlflow_artifact_bucket_arn
}
