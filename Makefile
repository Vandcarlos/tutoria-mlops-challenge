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
#  Step 1 — Ingest + Split Batches
# -------------------------------

ingest:
	$(MLFLOW_ENV) $(PYTHON) -m src.model.data.ingest

split-batches:
	$(MLFLOW_ENV) $(PYTHON) -m src.model.data.split_batches

# -------------------------------
#  Step 2 — Pipeline ML
# -------------------------------

preprocess-batch:
	$(TRACKING_ENV) $(PYTHON) -m src.model.data.preprocess_batch $(batch)

train:
	$(MLFLOW_ENV) $(PYTHON) -m src.model.pipeline.train --batches $(batches)

preprocess-test:
	$(TRACKING_ENV) $(PYTHON) -m src.model.data.preprocess_test

evaluate:
	$(TRACKING_ENV) $(PYTHON) -m src.model.pipeline.evaluate --model_version "$(model-version)""

pipeline:
	$(TRACKING_ENV) $(PYTHON) -m src.model.data.preprocess_batch $(batch)
	$(TRACKING_ENV) $(PYTHON) -m src.model.pipeline.train --batches $(batch)
	$(TRACKING_ENV) $(PYTHON) -m src.model.data.preprocess_test
	$(TRACKING_ENV) $(PYTHON) -m src.model.pipeline.evaluate
	@echo "Pipeline completa finalizada com sucesso para batch=$(batch)."

# -------------------------------
#  Inference
# -------------------------------

predict:
	$(TRACKING_ENV) $(PYTHON) -m src.model.pipeline.predict \
		--title "$(title)" --message "$(message)" --model_version "$(model_version)"
