module "iam_monitoring" {
  source        = "../../../modules/iam"
  name_prefix   = "${var.project_name}-${var.environment}-monitoring"
  s3_bucket_arn = var.data_bucket_arn
}
