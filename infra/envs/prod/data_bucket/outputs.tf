output "data_bucket_name" {
  description = "Name of the S3 data bucket"
  value       = module.data_bucket.bucket_name
}

output "data_bucket_arn" {
  description = "ARN of the S3 data bucket"
  value       = module.data_bucket.bucket_arn
}
