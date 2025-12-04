# Dockerfile for MLflow server on AWS ECS
FROM ghcr.io/mlflow/mlflow:v3.1.1

# Install Postgres driver
RUN pip install --no-cache-dir psycopg2-binary==2.9.9

# Expose MLflow UI port
EXPOSE 5000

# Use bash so we can expand env vars in CMD
SHELL ["/bin/bash", "-lc"]

# Default command: start MLflow server using environment variables
CMD mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri "${MLFLOW_BACKEND_STORE_URI}" \
    --registry-store-uri "${MLFLOW_REGISTRY_STORE_URI}" \
    --serve-artifacts \
    --artifacts-destination "${MLFLOW_ARTIFACTS_DESTINATION}"
