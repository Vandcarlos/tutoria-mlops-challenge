// variables.tf
// Public interface for the generic application security group module.

variable "name_prefix" {
  description = "Prefix used to name the security group (e.g. mlflow)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the security group will be created"
  type        = string
}

variable "app_port" {
  description = "Application port to allow traffic on (e.g. 5000, 8080)"
  type        = number
}

variable "ingress_from_sg_ids" {
  description = "List of security group IDs allowed to access this application SG on app_port"
  type        = list(string)
  default     = []
}

variable "ingress_cidrs" {
  description = "Optional list of CIDR blocks allowed to access this application SG on app_port"
  type        = list(string)
  default     = []
}

variable "egress_cidrs" {
  description = "List of CIDR blocks allowed for egress traffic"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "tags" {
  description = "Additional tags to apply to the security group"
  type        = map(string)
  default     = {}
}
