module "iam_model" {
  source        = "../../../modules/iam"
  name_prefix   = local.name
  s3_bucket_arn = var.data_bucket_arn
}
