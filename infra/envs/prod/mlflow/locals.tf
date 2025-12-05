data "aws_caller_identity" "current" {}

locals {
  component = "mlflow"
  name      = "${local.component}-${var.environment}"

  mlflow_backend_store_uri = "postgresql+psycopg2://${module.mlflow_db.username}:${var.mlflow_db_password}@${module.mlflow_db.endpoint}:${module.mlflow_db.port}/${module.mlflow_db.db_name}"
  mlflow_artifact_root     = "s3://${module.mlflow_artifacts_bucket.bucket_name}"
  aws_account_id           = data.aws_caller_identity.current.account_id
}
