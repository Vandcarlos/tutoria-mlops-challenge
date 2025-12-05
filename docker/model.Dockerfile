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
        build-essential \
        gcc \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*

# ----------------------------
# Install Python dependencies
# ----------------------------
COPY requirements-model.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Copy application code
# ----------------------------
COPY src/__init__.py ./src/__init__.py
COPY src/model ./src/model
COPY src/shared ./src/shared

# ----------------------------
# Start command
# ----------------------------
ENTRYPOINT ["python", "-m", "src.model.dispatcher"]
