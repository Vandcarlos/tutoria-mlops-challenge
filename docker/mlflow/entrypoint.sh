#!/usr/bin/env bash
set -euo pipefail

# Ensure required env vars are set
: "${MLFLOW_BACKEND_STORE_URI:?MLFLOW_BACKEND_STORE_URI is not set}"
: "${MLFLOW_ARTIFACT_ROOT:?MLFLOW_ARTIFACT_ROOT is not set}"

echo "[MLFLOW] Backend store URI: ${MLFLOW_BACKEND_STORE_URI}"
echo "[MLFLOW] Artifact root: ${MLFLOW_ARTIFACT_ROOT}"

echo "[MLFLOW] Running DB migrations..."
mlflow db upgrade "${MLFLOW_BACKEND_STORE_URI}"

echo "[MLFLOW] Starting MLflow server..."
mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri "${MLFLOW_BACKEND_STORE_URI}" \
  --serve-artifacts \
  --artifacts-destination "${MLFLOW_ARTIFACT_ROOT}"
