// outputs.tf
// Public outputs for the RDS PostgreSQL module.

output "endpoint" {
  description = "RDS endpoint hostname (without port)"
  value       = aws_db_instance.this.address
}

output "port" {
  description = "RDS endpoint port"
  value       = aws_db_instance.this.port
}

output "db_name" {
  description = "Name of the database"
  value       = aws_db_instance.this.db_name
}

output "username" {
  description = "Master username for the database"
  value       = aws_db_instance.this.username
}

output "security_group_id" {
  description = "Security group ID associated with the RDS instance"
  value       = aws_security_group.db_sg.id
}
