module "mlflow_ecr" {
  source = "../../modules/ecr"

  project_name  = var.project_name
  environment   = var.environment
  service_name  = "mlflow"

  image_mutability = "MUTABLE"
  scan_on_push     = true

  lifecycle_max_images = 15
}
