variable "owner" {
  type        = string
  description = "Me"
}

variable "project_name" {
  type        = string
  description = "Main project identifier used in tags and resource names."
}

variable "environment" {
  type        = string
  description = "The environment for resource naming and tagging."
}
