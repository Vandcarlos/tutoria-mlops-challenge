FROM python:3.13.7-slim

# ----------------------------
# Configure image
# ----------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app \
    PYTHONPATH="/app"

WORKDIR ${APP_HOME}


# ----------------------------
# Install dependencies
# ----------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*

# ----------------------------
# Install Python dependencies
# ----------------------------
COPY requirements-monitoring.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Copy application code
# ----------------------------
COPY src/__init__.py ./src/__init__.py
COPY src/monitoring ./src/monitoring
COPY src/shared ./src/shared

# ----------------------------
# Non-root user (opcional, mas recomendado)
# ----------------------------
RUN useradd -m appuser
USER appuser

# ----------------------------
# Start command
# ----------------------------
ENTRYPOINT ["python", "-m", "src.monitoring.generate_drift_reports"]
