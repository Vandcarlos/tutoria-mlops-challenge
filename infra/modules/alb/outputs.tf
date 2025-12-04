// outputs.tf
// Public outputs for the ALB module.

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.this.arn
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.this.dns_name
}

output "security_group_id" {
  description = "Security group ID associated with the ALB"
  value       = module.sg_alb.security_group_id
}

output "target_group_arn" {
  description = "ARN of the default target group associated with the ALB"
  value       = aws_lb_target_group.this.arn
}

output "listener_arn" {
  description = "ARN of the ALB listener"
  value       = aws_lb_listener.this.arn
}
