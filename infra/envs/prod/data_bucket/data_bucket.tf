locals {
    bucket_name = "${var.project_name}-${var.environment}-data-bucket"
}

module "data_bucket" {
  source = "../../../modules/s3-bucket"

  bucket_name   = local.bucket_name
  force_destroy = false

  tags = merge(
    {
      "Name"        = local.bucket_name
      "Component"   = "data"
      "Environment" = var.environment
      "Project"     = var.project_name
    }
  )
}
