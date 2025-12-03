// main.tf
// Generic application security group module.
// Allows inbound traffic on app_port from:
// - a set of source security groups (ingress_from_sg_ids)
// - and/or a set of CIDR blocks (ingress_cidrs)

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_security_group" "this" {
  name        = local.sg_name
  description = "Application security group for ${var.name_prefix}"
  vpc_id      = var.vpc_id

  # Ingress from other security groups (e.g. ALB)
  dynamic "ingress" {
    for_each = var.ingress_from_sg_ids
    content {
      description     = "Allow app_port from SG ${ingress.value}"
      from_port       = var.app_port
      to_port         = var.app_port
      protocol        = "tcp"
      security_groups = [ingress.value]
    }
  }

  # Ingress from CIDR blocks (optional)
  dynamic "ingress" {
    for_each = var.ingress_cidrs
    content {
      description = "Allow app_port from CIDR ${ingress.value}"
      from_port   = var.app_port
      to_port     = var.app_port
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  # Egress (default: allow all)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.egress_cidrs
  }

  tags = local.merged_tags
}
