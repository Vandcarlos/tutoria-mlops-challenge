FROM apache/airflow:2.9.1

# Default user in the base image is already "airflow",
# but we set explicitly to be clear
USER airflow

# Copy requirements from repository root (build context is ".." in docker-compose)
COPY requirements-model.txt /tmp/requirements-model.txt
COPY requirements-api.txt /tmp/requirements-api.txt
COPY requirements-monitoring.txt /tmp/requirements-monitoring.txt

# Install Python dependencies as airflow user
# NOTE: do NOT use --user here; the image already installs into user site-packages
# Good practice: pin apache-airflow to the same version as the base image
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" \
    -r /tmp/requirements-model.txt \
    -r /tmp/requirements-api.txt \
    -r /tmp/requirements-monitoring.txt
