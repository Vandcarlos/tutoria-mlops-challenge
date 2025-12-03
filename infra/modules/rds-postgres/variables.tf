// variables.tf
// Public interface for the generic RDS PostgreSQL module.

variable "project_name" {
  description = "Base project name (e.g. tutoria-mlops)"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g. dev, prod)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the RDS instance will be created"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the DB subnet group (use private subnets)"
  type        = list(string)
}

variable "vpc_cidr_block" {
  description = "CIDR block of the VPC (used to allow ingress to the DB SG)"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "username" {
  description = "Master username for the database"
  type        = string
}

variable "password" {
  description = "Master password for the database"
  type        = string
  sensitive   = true
}

variable "instance_class" {
  description = "RDS instance class (e.g. db.t3.micro)"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.10"
}

variable "multi_az" {
  description = "Whether to create a Multi-AZ RDS instance"
  type        = bool
  default     = false
}

variable "publicly_accessible" {
  description = "Whether the RDS instance should be publicly accessible"
  type        = bool
  default     = false
}

variable "backup_retention_period" {
  description = "Number of days to retain automatic backups"
  type        = number
  default     = 7
}

variable "deletion_protection" {
  description = "If true, the DB cannot be deleted by Terraform unless disabled"
  type        = bool
  default     = true
}

variable "skip_final_snapshot" {
  description = "Whether to skip the final snapshot before DB deletion"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags to apply to RDS resources"
  type        = map(string)
  default     = {}
}
