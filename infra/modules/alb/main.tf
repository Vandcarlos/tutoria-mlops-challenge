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
# Application Load Balancer
# ----------------------------------------
resource "aws_lb" "this" {
  name               = local.name
  internal           = var.internal
  load_balancer_type = "application"
  security_groups    = [module.sg_alb.security_group_id]
  subnets            = var.subnet_ids

  tags = local.merged_tags
}

# ----------------------------------------
# Target Group
# ----------------------------------------
resource "aws_lb_target_group" "this" {
  name        = local.tg_name
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
