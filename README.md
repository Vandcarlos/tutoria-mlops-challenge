# tutoria-mlops-challenge

Este repositório contém a implementação completa do desafio final da Tutoria MLOps, com o objetivo de construir um **pipeline de Machine Learning reprodutível, rastreável, versionado e pronto para produção**, seguindo boas práticas de MLOps Nível 0 → Nível 1.

O projeto envolve:

- ingestão e preparação de dados de sentimento da Amazon (Kaggle),
- versionamento e armazenamento em S3,
- treinamento e rastreamento de modelos com MLflow,
- deploy de API de inferência na AWS (Lambda ou ECS),
- simulação de retraining em batch via Airflow,
- infraestrutura como código com Terraform,
- CI/CD com GitHub Actions e OIDC.

---

# 🧩 Premissas

- Linguagem principal: **Python 3.10+**
- Dataset: **Amazon Reviews Polarity** (supervisionado, binário)
- Armazenamento de dados: **S3**
- MLflow:
  - **Fase inicial:** execução local (docker-compose)
  - **Fase avançada:** servidor MLflow em ECS Fargate (tracking server)
  - Artifact store: **S3**
- Airflow:
  - Executado **localmente via Docker** (para evitar custo MWAA)
  - Orquestra pipelines remotos (ECS Tasks)
- API de inferência: **FastAPI** + Docker + AWS
- Infraestrutura via **Terraform** usando OIDC para GitHub Actions
- Dataset será dividido em **10 batches** para simular ingestão semanal
- Apenas **scripts de data engineering** rodam local;
  treinamento e serving rodam em **containers dedicados**

---

# 📅 Planejamento do Projeto (Fases Evolutivas)

A execução segue uma progressão clara:

---

## ✔ Fase 1 — EDA e Baselines (Notebook)

Objetivo: entender os dados e selecionar o modelo baseline.

### MLflow Setup
- Rodando via Docker local:
  - UI disponível em `http://localhost:5000`
  - Backend local
  - Artifacts local

### `notebooks/eda_01.ipynb`
- Baixar amostra do dataset
- Explorar classes, tamanhos e exemplos
- Definir qual tipo(s) de modelo será utilizado
- Criar `full_text = title + text`
- Treinar 2 modelos baseline: (na etapa de definição dos modelos optou-se por modelos lineares)
   - TF-IDF + LogisticRegression
   - TF-IDF + LinearSVC
- Avaliar métricas:
   - Accuracy
   - Precision
   - Recall
   - F1-Macro
   - Confusion Matrix
- Selecionar modelo “v1”
- Registrar runs no MLflow local

---

## ✔ Fase 2 — Data Pipeline (Scripts Modulares)

Transformar código do notebook em scripts reusáveis:

### `src/model/data/ingest.py`
- Baixa dataset (local)
- Salva raw em `data/raw/`

### `src/model/data/split_batches.py`
- Divide dataset em **10 batches** iguais
- Salva em `data/batches/batch_0..9.parquet`

### `src/model/data/preprocess_core.py`
- Limpeza e padronização
- Concatenação de texto
- Salva Parquet em `data/processed/`

### `src/model/data/preprocess_test.py`
- Aplica o `preprocess_core` no dado de teste
- Salva Parquet em `data/processed/`

---

## ✔ Fase 3 — Treinamento com MLflow (Nível 0 → 1)

Implementar um pipeline reprodutível:

### `src/model/data/preprocess_batch.py`
- Aplica o `preprocess_core` em um batch específico
- Salva Parquet em `data/processed/`

### `src/model/pipeline/train.py`
- Recebe `--batches 0..k`
- Concatena batches
    > TF-IDF e modelos lineares não suportam aprendizado incremental nativo; por isso, o retraining sempre usa batch₀..batchₖ, garantindo vocabulário consistente.
- Split interno 80/20 (train/val)
- Treina modelo baseline
- Loga métricas no MLflow
- Salva artefatos do modelo no MLflow → S3

### `src/model/pipeline/evaluate.py`
- Avalia no test set global
- Loga métricas no MLflow

### `src/model/pipeline/predict.py`
- Recebe `--title "title" --message "message"`
- Formata o input
- Faz predição do valor

### Training Container
- Dockerfile para treinar em ECS Task

---

## ✔ Fase 4 — Serving (API de Inferência)

Implementar API FastAPI que carrega modelo do MLflow/S3:

### `src/serving/app.py`
- API FastAPI com endpoints:
  - `POST /predict`
  - `GET /health`
- Carregamento do modelo latest do S3/MLflow, via MLflow Model Artifact

---

## ✔ Fase 5 — Monitoramento

Monitorar:

- Distribuição de predições (drift)

## ✔ Fase 6 — Deploy e IaC (Terraform + CI/CD)

Containers:
- MlFlow
- Model
- Training
- Monitoring

Infra via Terraform:

- S3 (datasets + artifacts)
- ECR (imagens de treino e serving)
- ECS Fargate para serving
- IAM Roles + GitHub OIDC
- MLflow Tracking Server em ECS Fargate

GitHub Actions:
- build & push de imagens
- terraform plan/apply
- deploy automatizado da API
- testes com 80% de cobertura
- lint com ruff

---

## ✔ Fase 7 — Airflow (Orquestração do Pipeline)

Airflow rodará *local*, mas orquestrará tarefas na AWS:

- ingestão (manual)
- batch split
- preprocess
- treino inicial
- retraining semanal:
  `batch_0 → batch_0..1 → batch_0..2 → …`
- geração de report de drift

Cada etapa de ML é executada via **ECS Task**.
Serão 3 Dags

---

# 🧭 Estrutura Final do Projeto (Tree “v1”)

```text
tutoria-mlops-challenge/
├── notebooks/          # EDA e experimentação
├── src/                # Código de ingestão, preprocess, treino, serving
│   ├── data/           # Scripts de pipeline de dados
│   ├── models/         # Treinamento e avaliação
│   └── serving/        # API FastAPI
├── airflow/            # Orquestração local via docker-compose
├── mlflow/             # MLflow local via docker-compose
├── infra/              # Terraform (AWS S3, ECR, ECS, IAM, OIDC)
├── docker/             # Dockerfiles e configurações auxiliares
├── Makefile            # Comandos úteis
├── requirements.txt    # Dependências
└── README.md
```

# 🙏 Agradecimentos

Agradeço aos tutores pelo apoio, didática e incentivo:
- Manoel Veríssimo – [verissimomanoel](https://github.com/verissimomanoel)
- Douglas Batista – [dougbatista](https://github.com/dougbatista)
- Rafael Teru