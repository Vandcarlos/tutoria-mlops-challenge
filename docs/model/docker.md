# Docker da Imagem de Modelo

Esta página documenta a **imagem Docker** usada para executar os
scripts do módulo `src.model` em containers, bem como os comandos
`docker-model-*` disponíveis no `Makefile`.

A imagem é pensada para rodar:

- ingestão de dados,
- split em batches,
- pré-processamento,
- treino,
- avaliação,
- e predição,

de forma isolada, facilitando a execução em ambientes como **ECS/ECR**.

---

## 1. Definições no Makefile

A seção de Docker do Makefile define:

```make
MODEL_IMAGE      = tutoria-mlops-model:latest
MODEL_DOCKERFILE = docker/model.Dockerfile
MODEL_LOCALHOST  = http://host.docker.internal

MLFLOW_EXP_NAME  = amazon-reviews-training
```

E o helper `DOCKER_RUN`:

```make
define DOCKER_RUN
	mkdir -p data/docker
	docker run --rm \
		-e MLFLOW_TRACKING_URI="$(MODEL_LOCALHOST):${MLFLOW_PORT}" \
		-e MLFLOW_EXPERIMENT_NAME="$(MLFLOW_EXP_NAME)" \
		-v $(PWD)/data/docker:/app/data \
		$(MODEL_IMAGE)
endef
```

Pontos importantes:

- `MLFLOW_TRACKING_URI` aponta para o MLflow rodando no host
  (`http://host.docker.internal:5500`).
- Um volume é montado:
  - `$(PWD)/data/docker` (no host)
  - `/app/data` (no container)
- Isso garante que arquivos produzidos por um container (por exemplo,
  `ingest`) possam ser consumidos por outro (`split_batches`, `train` etc.).

---

## 2. Build da imagem

A imagem é construída a partir de `docker/model.Dockerfile`.

Para buildar:

```bash
make docker-model-build
```

Internamente:

```bash
docker build -f docker/model.Dockerfile -t tutoria-mlops-model:latest .
```

O Dockerfile inclui:

- Python base (ex.: `python:3.11-slim`)
- instalação de dependências a partir de `requirements-model.txt` (copiado
  como `requirements.txt` dentro da imagem),
- cópia de `src/model` + `src/__init__.py`,
- `ENTRYPOINT ["python", "-m"]`, permitindo chamar qualquer módulo Python
  via `docker run ... <modulo>`.

---

## 3. Comandos `docker-model-*` (unitários)

Depois de buildar a imagem, você pode executar os scripts de modelo
dentro de containers usando os seguintes comandos:

```bash
make docker-model-ingest
make docker-model-split-batches
make docker-model-preprocess-batch batch=0
make docker-model-train batches="0 1 2"
make docker-model-preprocess-test
make docker-model-evaluate
```

Equivalência:

- `docker-model-ingest`  
  Roda `src.model.data.ingest` dentro do container.

- `docker-model-split-batches`  
  Roda `src.model.data.split_batches`, lendo `data/docker/raw/train.csv`
  (montado como `/app/data/raw/train.csv` no container) e escrevendo
  `train_batch_N.csv` em `data/docker/batches/`.

- `docker-model-preprocess-batch`  
  Roda `src.model.data.preprocess_batch $(batch)` dentro do container.

  Exemplo:

  ```bash
  make docker-model-preprocess-batch batch=0
  ```

- `docker-model-train`  
  Roda `src.model.pipeline.train --batches $(batches)`.

  Exemplo:

  ```bash
  make docker-model-train batches="0 1 2"
  ```

- `docker-model-preprocess-test`  
  Roda `src.model.data.preprocess_test`.

- `docker-model-evaluate`  
  Roda `src.model.pipeline.evaluate --model_version "$(model_version)"`.

  Exemplo:

  ```bash
  make docker-model-evaluate model_version=1
  ```

Todos esses comandos:

- usam o volume `data/docker` ↔ `/app/data`,
- usam `MLFLOW_TRACKING_URI` e `MLFLOW_EXPERIMENT_NAME`,
- registram runs no MLflow da mesma forma que o código local,
  mas dentro de um ambiente containerizado.

---

## 4. Pipelines `docker-model-*`

Para facilitar execução end-to-end dentro de containers, existem:

```bash
make docker-model-pipeline-ingest
make docker-model-pipeline-train batch=0
```

- `docker-model-pipeline-ingest`:
  1. `docker-model-ingest`
  2. `docker-model-split-batches`

  Ou seja: baixa e prepara os CSVs de treino/teste e já divide o treino
  em batches na pasta `data/docker`.

- `docker-model-pipeline-train`:
  1. `docker-model-preprocess-batch` (para o `batch` informado)
  2. `docker-model-train`
  3. `docker-model-preprocess-test`
  4. `docker-model-evaluate`

  Exemplo:

  ```bash
  make docker-model-pipeline-train batch=0
  ```

Isso executa todo o pipeline de treino dentro de containers,
usando os dados compartilhados via volume.

---

## 5. Predição via Docker

Por fim, é possível fazer predição rodando o pipeline de inferência
dentro de um container:

```bash
make docker-model-predict         title="bom demais"         message="produto excelente"         model_version=1
```

Equivale a chamar:

```text
src.model.pipeline.predict --title "<title>" --message "<message>" --model_version "<model_version>"
```

Usando:

- a imagem `tutoria-mlops-model`,
- o volume `data/docker` (caso o pipeline dependa de artefatos em disco),
- e o MLflow apontando para o host (para logging/consulta de modelos).

---

Em resumo, a combinação de:

- `docker/model.Dockerfile`
- variáveis `MODEL_*` no Makefile
- helper `DOCKER_RUN`
- targets `docker-model-*`

fornece uma forma padronizada e reproduzível de rodar todo o pipeline
de modelo em containers, preparando o terreno para rodar esses mesmos
comandos em ambientes de orquestração como ECS, Batch ou Airflow.
