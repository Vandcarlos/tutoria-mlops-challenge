// variables.tf
// Public interface for the generic ALB module.

variable "name_prefix" {
  description = "Prefix of project (e.g. mlflow)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the ALB will be created"
  type        = string
}

variable "subnet_ids" {
  description = "Subnets where the ALB will be placed (usually public subnets)"
  type        = list(string)
}

variable "internal" {
  description = "Whether the ALB is internal (true) or internet-facing (false)"
  type        = bool
  default     = false
}

variable "listener_port" {
  description = "Port where the ALB will listen for incoming traffic"
  type        = number
  default     = 80
}

variable "listener_protocol" {
  description = "Protocol for the ALB listener (HTTP or HTTPS)"
  type        = string
  default     = "HTTP"
}

variable "target_group_port" {
  description = "Port used by the target group to route traffic to targets"
  type        = number
  default     = 80
}

variable "target_group_protocol" {
  description = "Protocol used by the target group (HTTP or HTTPS)"
  type        = string
  default     = "HTTP"
}

variable "health_check_path" {
  description = "HTTP path used for health checks by the target group"
  type        = string
  default     = "/"
}

variable "allowed_ingress_cidrs" {
  description = "CIDR blocks allowed to access the ALB listener"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "tags" {
  description = "Additional tags to apply to ALB and related resources"
  type        = map(string)
  default     = {}
}
