// main.tf
// Generic Application Load Balancer module with a single HTTP listener
// and a single target group.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ----------------------------------------
# Security Group for the ALB
# ----------------------------------------
resource "aws_security_group" "alb_sg" {
  name        = substr("${local.name_prefix}-tg", 0, 32)
  description = "Security group for ${local.name_prefix}"
  vpc_id      = var.vpc_id

  # Ingress from CIDR blocks on listener_port
  dynamic "ingress" {
    for_each = var.allowed_ingress_cidrs
    content {
      description = "Allow ${var.listener_protocol} on port ${var.listener_port} from ${ingress.value}"
      from_port   = var.listener_port
      to_port     = var.listener_port
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  # Egress open to world (can be restricted if needed)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.merged_tags
}

# ----------------------------------------
# Application Load Balancer
# ----------------------------------------
resource "aws_lb" "this" {
  name               = local.name_prefix
  internal           = var.internal
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = var.subnet_ids

  tags = local.merged_tags
}

# ----------------------------------------
# Target Group
# ----------------------------------------
resource "aws_lb_target_group" "this" {
  name        = "${local.name_prefix}-tg"
  port        = var.target_group_port
  protocol    = var.target_group_protocol
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    path                = var.health_check_path
    protocol            = var.target_group_protocol
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = local.merged_tags
}

# ----------------------------------------
# Listener
# ----------------------------------------
resource "aws_lb_listener" "this" {
  load_balancer_arn = aws_lb.this.arn
  port              = var.listener_port
  protocol          = var.listener_protocol

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}
