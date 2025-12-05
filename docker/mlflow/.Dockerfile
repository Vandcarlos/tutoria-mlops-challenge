# Dockerfile for MLflow server on AWS ECS
FROM ghcr.io/mlflow/mlflow:v3.1.1

# Install Postgres driver
RUN pip install --no-cache-dir psycopg2-binary==2.9.9

# Expose MLflow UI port
EXPOSE 5000

# Use bash so we can expand env vars
SHELL ["/bin/bash", "-lc"]

# Copy custom entrypoint
COPY docker/mlflow/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
