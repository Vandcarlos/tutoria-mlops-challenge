data "aws_caller_identity" "current" {}

locals {
  component = "mlflow"
  name      = "${local.component}-${var.environment}"

  mlflow_backend_store_uri = format(
    "postgresql+psycopg2://%s:%s@%s:%d/%s",
    module.mlflow_db.username, # "mlflow_user"
    var.mlflow_db_password,    # password from TF var / secret
    module.mlflow_db.endpoint, # RDS hostname
    module.mlflow_db.port,     # usually 5432
    module.mlflow_db.db_name   # "mlflow"
  )

  mlflow_artifact_root = "s3://${module.mlflow_artifacts_bucket.bucket_name}"
  aws_account_id       = data.aws_caller_identity.current.account_id
}
