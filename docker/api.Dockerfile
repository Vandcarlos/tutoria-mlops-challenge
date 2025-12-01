FROM python:3.13.7-slim

# ----------------------------
# Configure image
# ----------------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app \
    PYTHONPATH="/app"

WORKDIR ${APP_HOME}

EXPOSE 8000

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
COPY requirements-api.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Copy application code
# ----------------------------
COPY src/__init__.py ./src/__init__.py
COPY src/api ./src/api
COPY src/shared ./src/shared

# ----------------------------
# Start command
# ----------------------------
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
