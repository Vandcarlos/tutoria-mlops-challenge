// outputs.tf
// Public outputs for the VPC module.

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.this.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.this.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = [for s in aws_subnet.public : s.id]
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = [for s in aws_subnet.private : s.id]
}

output "public_subnet_arns" {
  description = "List of public subnet ARNs"
  value       = [for s in aws_subnet.public : s.arn]
}

output "private_subnet_arns" {
  description = "List of private subnet ARNs"
  value       = [for s in aws_subnet.private : s.arn]
}
