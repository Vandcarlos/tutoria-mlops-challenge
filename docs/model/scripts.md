# Scripts e Comandos do Modelo (Makefile)

Esta página documenta os **comandos do Makefile** relacionados ao modelo,
focando na execução **local** (sem Docker) e em alguns utilitários de infra.

A ideia é que você nunca precise lembrar dos `python -m ...` na mão:
basta chamar os alvos corretos do `Makefile`.

---

## 1. Infraestrutura – MLflow

O Makefile possui lógica para detectar se o MLflow está no ar
e expõe alguns comandos auxiliares.

### 1.1. Subir e derrubar o MLflow

```bash
make mlflow-up
make mlflow-down
```

- `mlflow-up`  
  Sobe o servidor MLflow usando `mlflow/docker-compose.yml` na porta `5500`.

- `mlflow-down`  
  Derruba o container do MLflow.

### 1.2. Ver status do MLflow

```bash
make mlflow-status
```

Esse comando imprime algo como:

```text
MLflow status: up
```

ou nada se o servidor não estiver no ar.

Internamente, a variável `MLFLOW_ENV` é configurada com:

```text
MLFLOW_TRACKING_URI=http://localhost:5500
```

sempre que o MLflow está disponível, e isso é reaproveitado nos comandos
de modelo locais.

---

## 2. Notebooks

Há um comando de utilitário para aplicar `ruff` (via `nbqa`) em todos
os notebooks:

```bash
make fix-notebooks
```

Ele itera sobre `notebooks/*.ipynb` e roda:

```text
nbqa ruff --fix <notebook>
```

Útil para manter o estilo/qualidade dos notebooks consistente
com o código Python.

---

## 3. Variáveis de conveniência

O Makefile define alguns atalhos para módulos Python:

```make
INGEST=src.model.data.ingest
SPLIT_BATCHES=src.model.data.split_batches
PREPROCESS_BATCH=src.model.data.preprocess_batch $(batch)
TRAIN=src.model.pipeline.train --batches $(batches)
PREPROCESS_TEST=src.model.data.preprocess_test
EVALUATE=src.model.pipeline.evaluate --model_version "$(model_version)"
PREDICT=src.model.pipeline.predict --title "$(title)" --message "$(message)" --model_version "$(model_version)"
```

Esses nomes são reaproveitados nos comandos locais e Docker,
para evitar repetição e manter uma “interface” única.

---

## 4. Comandos locais (sem Docker)

Aqui estão os comandos **locais**, isto é: rodam `python -m ...`
diretamente na sua máquina, com `MLFLOW_TRACKING_URI` configurado
automaticamente quando o MLflow está no ar.

### 4.1. Comandos unitários

```bash
make model-ingest
make model-split-batches
make model-preprocess-batch batch=0
make model-train batches="0 1 2"
make model-preprocess-test
make model-evaluate
```

Explicando:

- `model-ingest`  
  Executa `src.model.data.ingest` e baixa o dataset
  `amazon-reviews`, salvando em `data/raw/train.csv` e `data/raw/test.csv`.

- `model-split-batches`  
  Executa `src.model.data.split_batches`, que divide o `train.csv` em
  vários arquivos `train_batch_N.csv` em `data/batches/`.

- `model-preprocess-batch`  
  Executa `src.model.data.preprocess_batch $(batch)`.

  Exemplo:

  ```bash
  make model-preprocess-batch batch=0
  ```

- `model-train`  
  Executa `src.model.pipeline.train --batches $(batches)`.

  Exemplo:

  ```bash
  make model-train batches="0 1 2"
  ```

- `model-preprocess-test`  
  Executa `src.model.data.preprocess_test`, aplicando o mesmo
  pré-processamento aos dados de teste.

- `model-evaluate`  
  Executa `src.model.pipeline.evaluate --model_version "$(model_version)"`.

  Exemplo:

  ```bash
  make model-evaluate model_version=1
  ```

### 4.2. Pipelines locais

```bash
make model-pipeline-ingest
make model-pipeline-train batch=0
```

- `model-pipeline-ingest`:
  1. `model-ingest`
  2. `model-split-batches`

  Ou seja: baixa o dataset e já divide em batches numa tacada só.

- `model-pipeline-train`:
  1. `model-preprocess-batch` (para o `batch` informado)
  2. `model-train`
  3. `model-preprocess-test`
  4. `model-evaluate`

  Exemplo:

  ```bash
  make model-pipeline-train batch=0
  ```

  Isso executa todo o fluxo de treino para o batch 0.

### 4.3. Predição local

```bash
make model-predict         title="bom demais"         message="produto excelente"         model_version=1
```

Esse comando executa:

```text
src.model.pipeline.predict --title "<title>" --message "<message>" --model_version "<model_version>"
```

Utilizando o modelo/versionamento indicado, e registrando no MLflow se
a configuração do projeto estiver preparada para isso.

---

Em resumo, os comandos `model-*` permitem que você rode toda a lógica
de dados e modelo **direto no host**, com MLflow integrado, sem se
preocupar com o detalhamento dos módulos Python.
