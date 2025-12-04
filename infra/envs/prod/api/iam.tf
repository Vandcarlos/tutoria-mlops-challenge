module "iam_api" {
  source        = "../../../modules/iam"
  name_prefix   = "${var.project_name}-${var.environment}-api"
  s3_bucket_arn = var.data_bucket_arn
}
