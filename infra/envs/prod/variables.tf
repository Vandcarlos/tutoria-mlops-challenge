variable "project" {
  type        = string
  description = "Main project identifier used in tags and resource names."
}

variable "aws_region" {
  type        = string
  description = "Default AWS region where resources will be created."
}
