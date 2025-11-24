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
PREPROCESS_TEST=src.model.data.preprocess_test
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

model-preprocess-test:
	$(MLFLOW_ENV) $(PYTHON) -m $(PREPROCESS_TEST)

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
	$(MLFLOW_ENV) $(PYTHON) -m $(PREPROCESS_TEST)
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

define DOCKER_RUN
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
	$(DOCKER_RUN) $(INGEST)

docker-model-split-batches:
	$(DOCKER_RUN) $(SPLIT_BATCHES)

docker-model-preprocess-batch:
	$(DOCKER_RUN) $(PREPROCESS_BATCH)

docker-model-train:
	$(DOCKER_RUN) $(TRAIN)

docker-model-preprocess-test:
	$(DOCKER_RUN) $(PREPROCESS_TEST)

docker-model-evaluate:
	$(DOCKER_RUN) $(EVALUATE)

docker-model-pipeline-ingest:
	$(DOCKER_RUN) $(INGEST)
	$(DOCKER_RUN) $(SPLIT_BATCHES)
	@echo "Pipeline [Ingest] (Docker) completa finalizada com sucesso."

docker-model-pipeline-train: batches=$(batch)
docker-model-pipeline-train:
	$(DOCKER_RUN) $(PREPROCESS_BATCH)
	$(DOCKER_RUN) $(TRAIN)
	$(DOCKER_RUN) $(PREPROCESS_TEST)
	$(DOCKER_RUN) $(EVALUATE)
	@echo "Pipeline [Ingest] (Docker) completa finalizada com sucesso para batch=$(batch)."

docker-model-predict:
	$(DOCKER_RUN) $(PREDICT)


# -------------------------------
#  API commands
# -------------------------------

RUN_API=uvicorn src.api.main:app

# -------------------------------
#  API local commands
# -------------------------------

run-api:
	$(MLFLOW_ENV) $(PYTHON) -m $(RUN_API)
