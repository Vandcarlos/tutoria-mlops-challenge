#!/usr/bin/env bash
set -euo pipefail

# Always run from this script directory
cd "$(dirname "$0")"

echo "[BOOTSTRAP] Initializing Terraform..."
terraform init -upgrade

echo "[BOOTSTRAP] Validating configuration..."
terraform validate

echo "[BOOTSTRAP] Planning changes..."
terraform plan

echo "[BOOTSTRAP] Applying changes..."
terraform apply -auto-approve

echo "[BOOTSTRAP] Done. Outputs:"
terraform output
