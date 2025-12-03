module "mlflow_artifacts_bucket" {
  source = "../../../modules/s3-bucket"

  bucket_name        = "tutoria-mlops-prod-mlflow-artifacts" # precisa ser único globalmente
  versioning_enabled = true
  force_destroy      = false

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    Service     = "mlflow"
  }
}

output "mlflow_artifacts_bucket_name" {
  description = "S3 bucket name used to store MLflow artifacts"
  value       = module.mlflow_artifacts_bucket.bucket_name
}
