module "ecr_mlflow" {
  source = "../../../modules/ecr"

  project_name = var.project_name
  environment  = var.environment
  service_name = local.component

  image_mutability = "MUTABLE"
  scan_on_push     = true

  lifecycle_max_images = 15
}
