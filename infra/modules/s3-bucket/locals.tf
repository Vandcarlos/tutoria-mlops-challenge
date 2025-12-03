// locals.tf
// Base tags for the S3 bucket.

locals {
  base_tags = {
    ManagedBy = "Terraform"
    Component = "s3-bucket"
  }

  merged_tags = merge(local.base_tags, var.tags)
}
