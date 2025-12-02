# Here you will call your modules (s3, ecr, iam, etc.).
# For now, keeping it empty is fine – Terraform will just create the remote state backend.

# example in future:
# module "data_bucket" {
#   source      = "../../modules/s3_bucket"
#   bucket_name = "${var.project}-data-prod"
# }
