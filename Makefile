PYTHON=python3

MLFLOW_PORT=5500
MLFLOW_URI=http://localhost:$(MLFLOW_PORT)

define ML_IS_UP
	$(shell curl -s $(MLFLOW_URI)/api/2.0/mlflow/experiments/list >/dev/null 2>&1 && echo "up")
endef

ifeq ($(call ML_IS_UP),up)
	MLFLOW_ENV=MLFLOW_TRACKING_URI=$(MLFLOW_URI)
else
	MLFLOW_ENV=
endif

# -------------------------------
#  Infrastructure (MLflow)
# -------------------------------

mlflow-up:
	docker compose -f mlflow/docker-compose.yml up -d

mlflow-down:
	docker compose -f mlflow/docker-compose.yml down

mlflow-status:
	@echo "MLflow status: $(call ML_IS_UP)"

# -------------------------------
#  Notebooks
# -------------------------------

fix-notebooks:
	for nb in notebooks/*.ipynb; do \
		nbqa ruff --fix "$$nb"; \
	done

# -------------------------------
#  Model commands
# -------------------------------

INGEST=src.model.data.ingest
SPLIT_BATCHES=src.model.data.split_batches
PREPROCESS_BATCH=src.model.data.preprocess_batch $(batch)
TRAIN=src.model.pipeline.train --batches $(batches)
EVALUATE=src.model.pipeline.evaluate --model_version "$(model_version)"
PREDICT=src.model.pipeline.predict --title "$(title)" --message "$(message)" --model_version "$(model_version)"

# -------------------------------
#  Model local commands
# -------------------------------

model-ingest:
	$(MLFLOW_ENV) $(PYTHON) -m $(INGEST)

model-split-batches:
	$(MLFLOW_ENV) $(PYTHON) -m $(SPLIT_BATCHES)

model-preprocess-batch:
	$(MLFLOW_ENV) $(PYTHON) -m $(PREPROCESS_BATCH)

model-train:
	$(MLFLOW_ENV) $(PYTHON) -m $(TRAIN)

model-evaluate:
	$(MLFLOW_ENV) $(PYTHON) -m $(EVALUATE)

# -------------------------------
#  Model local pipeline commands
# -------------------------------

model-pipeline-ingest:
	$(MLFLOW_ENV) $(PYTHON) -m $(INGEST)
	$(MLFLOW_ENV) $(PYTHON) -m $(SPLIT_BATCHES)
	@echo "Pipeline [INGEST] completa finalizada com sucesso."

model-pipeline-train: batches=$(batch)
model-pipeline-train:
	$(MLFLOW_ENV) $(PYTHON) -m $(PREPROCESS_BATCH)
	$(MLFLOW_ENV) $(PYTHON) -m $(TRAIN)
	$(MLFLOW_ENV) $(PYTHON) -m $(EVALUATE)
	@echo "Pipeline [TRAIN] completa finalizada com sucesso para batch=$(batch)."

model-predict:
	$(MLFLOW_ENV) $(PYTHON) -m $(PREDICT)

# -------------------------------
#  Model Docker
# -------------------------------

MODEL_IMAGE      = tutoria-mlops-model:latest
MODEL_DOCKERFILE = docker/model.Dockerfile
MODEL_LOCALHOST  = http://host.docker.internal

MLFLOW_EXP_NAME  = amazon-reviews-training

define MODEL_DOCKER_RUN
	mkdir -p data/docker
	docker run --rm \
		-e MLFLOW_TRACKING_URI="$(MODEL_LOCALHOST):${MLFLOW_PORT}" \
		-e MLFLOW_EXPERIMENT_NAME="$(MLFLOW_EXP_NAME)" \
		-v $(PWD)/data/docker:/app/data \
		$(MODEL_IMAGE)
endef

docker-model-build:
	docker build -f $(MODEL_DOCKERFILE) -t $(MODEL_IMAGE) .

docker-model-ingest:
	$(MODEL_DOCKER_RUN) $(INGEST)

docker-model-split-batches:
	$(MODEL_DOCKER_RUN) $(SPLIT_BATCHES)

docker-model-preprocess-batch:
	$(MODEL_DOCKER_RUN) $(PREPROCESS_BATCH)

docker-model-train:
	$(MODEL_DOCKER_RUN) $(TRAIN)

docker-model-evaluate:
	$(MODEL_DOCKER_RUN) $(EVALUATE)

docker-model-pipeline-ingest:
	$(MODEL_DOCKER_RUN) $(INGEST)
	$(MODEL_DOCKER_RUN) $(SPLIT_BATCHES)
	@echo "Pipeline [Ingest] (Docker) completa finalizada com sucesso."

docker-model-pipeline-train: batches=$(batch)
docker-model-pipeline-train:
	$(MODEL_DOCKER_RUN) $(PREPROCESS_BATCH)
	$(MODEL_DOCKER_RUN) $(TRAIN)
	$(MODEL_DOCKER_RUN) $(EVALUATE)
	@echo "Pipeline [Ingest] (Docker) completa finalizada com sucesso para batch=$(batch)."

docker-model-predict:
	$(MODEL_DOCKER_RUN) $(PREDICT)


# -------------------------------
#  API commands
# -------------------------------

RUN_API=uvicorn src.api.main:app

# -------------------------------
#  API local commands
# -------------------------------

api-run:
	$(MLFLOW_ENV) $(PYTHON) -m $(RUN_API)

api-predict:
	@curl -X POST "http://localhost:8000/api/v1/predict" \
		-H "Content-Type: application/json" \
		-d '{"title":"$(title)","message":"$(message)"}'

# -------------------------------
#  API Docker
# -------------------------------

API_IMAGE      = tutoria-mlops-api:latest
API_DOCKERFILE = docker/api.Dockerfile
API_PORT       = 8010

MODEL_DIR      = $(PWD)/data/model
MODEL_LOCALHOST = http://host.docker.internal

define API_DOCKER_RUN
	mkdir -p $(MODEL_DIR)
	docker run --rm \
		-p $(API_PORT):8000 \
		-e MLFLOW_TRACKING_URI="$(MODEL_LOCALHOST):$(MLFLOW_PORT)" \
		-e ALLOW_RUNTIME_MODEL_DOWNLOAD=true \
		-v $(MODEL_DIR):/app/data/model \
		$(API_IMAGE)
endef

docker-api-build:
	docker build -f $(API_DOCKERFILE) -t $(API_IMAGE) .

docker-api-run:
	$(API_DOCKER_RUN)


# -------------------------------
#  Monitoring commands
# -------------------------------

MONITORING=src.monitoring.generate_drift_reports

# -------------------------------
#  Monitoring local commands
# -------------------------------

monitoring-generate-report:
	$(MLFLOW_ENV) $(PYTHON) -m $(MONITORING)