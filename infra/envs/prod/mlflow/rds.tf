module "mlflow_db" {
  source = "../../../modules/rds-postgres"

  project_name = var.project_name
  environment  = var.environment

  vpc_id        = var.vpc_id
  subnet_ids    = var.private_subnet_ids
  vpc_cidr_block = var.vpc_cidr_block

  db_name  = "mlflow"
  username = "mlflow_user"
  password = var.mlflow_db_password   # defina var sensível em prod

  instance_class        = "db.t3.micro"
  allocated_storage     = 20
  engine_version        = "15.4"
  multi_az              = false
  publicly_accessible   = false
  backup_retention_period = 7
  deletion_protection   = true
  skip_final_snapshot   = false

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    Service     = "mlflow"
  }
}

output "mlflow_db_endpoint" {
  description = "RDS endpoint for MLflow backend store"
  value       = module.mlflow_db.endpoint
}
