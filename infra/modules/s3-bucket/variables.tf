// variables.tf
// Public interface for the generic S3 bucket module.

variable "bucket_name" {
  description = "Name of the S3 bucket (must be globally unique)"
  type        = string
}

variable "versioning_enabled" {
  description = "Whether to enable versioning for the bucket"
  type        = bool
  default     = true
}

variable "force_destroy" {
  description = "Allow Terraform to delete the bucket even if it contains objects"
  type        = bool
  default     = false
}

variable "block_public_acls" {
  description = "Block public ACLs on the bucket"
  type        = bool
  default     = true
}

variable "block_public_policy" {
  description = "Block public bucket policies"
  type        = bool
  default     = true
}

variable "ignore_public_acls" {
  description = "Ignore public ACLs on the bucket"
  type        = bool
  default     = true
}

variable "restrict_public_buckets" {
  description = "Restrict public bucket policies"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to apply to the S3 bucket"
  type        = map(string)
  default     = {}
}
