// main.tf
// Generic RDS PostgreSQL module.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ----------------------------------------
# Security Group for RDS
# ----------------------------------------
resource "aws_security_group" "db_sg" {
  name        = "${local.identifier}-sg"
  description = "Security group for ${local.identifier}"
  vpc_id      = var.vpc_id

  # Allow PostgreSQL from within the VPC CIDR (typical for app traffic inside VPC)
  ingress {
    description = "Allow PostgreSQL from VPC CIDR"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_block]
  }

  # Egress open (DB initiates connections rarely, but kept open for upgrades, etc.)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.merged_tags
}

# ----------------------------------------
# DB Subnet Group
# ----------------------------------------
resource "aws_db_subnet_group" "this" {
  name       = "${local.identifier}-subnets"
  subnet_ids = var.subnet_ids

  tags = local.merged_tags
}

# ----------------------------------------
# RDS PostgreSQL Instance
# ----------------------------------------
resource "aws_db_instance" "this" {
  identifier = local.identifier

  engine         = "postgres"
  engine_version = var.engine_version

  instance_class    = var.instance_class
  allocated_storage = var.allocated_storage

  db_name  = var.db_name
  username = var.username
  password = var.password

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]

  multi_az            = var.multi_az
  publicly_accessible = var.publicly_accessible

  backup_retention_period = var.backup_retention_period

  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot

  apply_immediately = true

  tags = local.merged_tags
}
