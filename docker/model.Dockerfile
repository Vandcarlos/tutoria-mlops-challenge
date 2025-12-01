FROM python:3.13.7-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-model.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY src/__init__.py ./src/__init__.py
COPY src/model ./src/model

ENV PYTHONPATH="${APP_HOME}"

ENTRYPOINT ["python", "-m"]
