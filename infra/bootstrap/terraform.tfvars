project    = "tutoria-mlops-challenge"
aws_region = "us-east-1"

repo = {
  owner     = "Vandcarlos"
  name      = "tutoria-mlops-challenge"
  role_name = "oc-infra-deployer"
}

state_bucket_name = "tfstate-vandcarlos-tutoria-mlops-challenge"
lock_table_name   = "tfstate-ml-locks"
