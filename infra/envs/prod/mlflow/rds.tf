module "mlflow_db" {
  source = "../../modules/rds-postgres"

  project_name = "tutoria-mlops"
  environment  = "prod"

  vpc_id        = module.vpc.vpc_id
  subnet_ids    = module.vpc.private_subnet_ids
  vpc_cidr_block = module.vpc.vpc_cidr_block

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
    Project     = "tutoria-mlops"
    Environment = "prod"
    Service     = "mlflow"
  }
}

output "mlflow_db_endpoint" {
  description = "RDS endpoint for MLflow backend store"
  value       = module.mlflow_db.endpoint
}
