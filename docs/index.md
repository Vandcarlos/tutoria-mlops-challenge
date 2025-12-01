# Desafio MLOps – Amazon Reviews Sentiment

Este projeto implementa um pipeline de Machine Learning de ponta a ponta
para **análise de sentimento de reviews da Amazon**, usando o dataset:

- `kritanjalijain/amazon-reviews` (Kaggle)

O objetivo é servir como um **projeto vitrine de MLOps**, mostrando:

- Como sair de notebooks/EDA para código de produção em `src/`
- Como organizar **pipelines de dados e treino** (`src.model.data` e `src.model.pipeline`)
- Como usar **MLflow** para rastrear experimentos
- Como empacotar o modelo em uma **imagem Docker** reutilizável
- Como expor uma interface única de execução via **Makefile**

## Premissas do projeto

- O foco é **engenharia de ML**, não só o modelo em si.
- Tudo deve ser executável via **Makefile** (local e Docker).
- O modelo e a API são **containers separados**.
- MLflow é usado como *source of truth* de métricas, parâmetros e artefatos.
- O projeto foi pensado para facilmente evoluir para:
  - orquestração (Airflow / Step Functions),
  - ECS/ECR (treino e inferência),
  - e documentação via GitHub Pages (pasta `docs/`).

---

## Documentação disponível

### Módulo de modelo (`src/model`)

- 👉 [Visão geral do módulo de modelo](model/index.md)  
  Explica qual é a responsabilidade do módulo `src.model` dentro do projeto
  e como ele se encaixa no fluxo de MLOps.

- 👉 [Scripts e comandos do modelo](model/scripts.md)  
  Detalha os comandos do `Makefile` relacionados ao modelo (execução local),
  explicando o que cada alvo faz e exemplos de uso.

- 👉 [Imagem Docker do modelo](model/docker.md)  
  Descreve a imagem `tutoria-mlops-model`, como ela é construída, como os
  comandos `docker-model-*` funcionam e como os dados/MLflow são integrados
  quando rodamos dentro de containers.

---

## Próximas documentações (futuras)

Estas páginas ainda não existem, mas o projeto foi pensado para evoluir para:

- `docs/api/index.md`  
  Descrever a API de inferência (Fase 4), endpoints, contrato de entrada/saída
  e como rodar a API localmente e em Docker/ECS.

- `docs/infra/index.md`  
  Documentar a infraestrutura (Terraform, IAM, ECS, ECR, repositório de artefatos),
  papéis de cada stack e como o CI/CD integra tudo.

Quando essas partes forem implementadas, este `index.md` pode ser atualizado
para linkar diretamente para cada uma delas.
