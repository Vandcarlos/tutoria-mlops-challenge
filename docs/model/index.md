# Módulo de Modelo (`src/model`)

O módulo `src.model` concentra toda a lógica relacionada ao **modelo de análise
de sentimento**, desde a ingestão dos dados até a predição.

Ele está organizado em dois submódulos principais:

- `src.model.data` – Responsável pelo **pipeline de dados**
  - Ingestão do dataset bruto (Kaggle)
  - Split em batches menores para treino incremental
  - Pré-processamento de batches e do conjunto de teste
  - Pré-processamento de entradas para inferência

- `src.model.pipeline` – Responsável pelo **pipeline de modelo**
  - Treino do modelo com base nos batches pré-processados
  - Avaliação do modelo em dados de teste
  - Predição a partir de `title` + `message`
  - Resolução da melhor versão de modelo registrada

## Papel do módulo no projeto

Dentro do contexto do projeto:

- `src.model` é a **camada de domínio de ML**.
- Tudo que diz respeito a **dados, features, treino, métrica, escolha de modelo**
  fica aqui.
- A API (quando existir) deve depender deste módulo para:
  - carregar modelo/versão correta,
  - pré-processar entradas,
  - chamar o código de predição.

Em termos de MLOps:

- `src.model.data` e `src.model.pipeline` são usados tanto em:
  - execuções locais (`python -m ...` / `make model-*`)
  - quanto dentro da imagem Docker (`make docker-model-*`).
- MLflow é usado para registrar:
  - runs de ingest, split e treino,
  - parâmetros e métricas,
  - artefatos relevantes (ex.: dataset derivado, modelo treinado).

## Fluxo lógico de alto nível

De forma simplificada, o fluxo é:

1. **Ingestão**  
   `src.model.data.ingest` baixa o dataset `amazon-reviews`,
   extrai e grava arquivos CSV em `data/raw/train.csv` e `data/raw/test.csv`.

2. **Split em batches**  
   `src.model.data.split_batches` lê o `train.csv` bruto e divide
   em arquivos `train_batch_N.csv` (por exemplo, 10 batches),
   gravando em `data/batches/`.

3. **Pré-processamento de batch**  
   `src.model.data.preprocess_batch` aplica:
   - limpeza de texto,
   - normalização,
   - seleção de colunas,
   - geração de features necessárias para o modelo.

4. **Treino**  
   `src.model.pipeline.train` consome um ou mais batches pré-processados
   e treina o modelo (por exemplo, um modelo linear com vetorização de texto),
   registrando tudo no MLflow.

5. **Pré-processamento de teste**  
   `src.model.data.preprocess_test` aplica o mesmo pipeline de transformação
   aos dados de teste.

6. **Avaliação**  
   `src.model.pipeline.evaluate` avalia o modelo usando o conjunto de teste
   pré-processado, gera métricas (accuracy, F1 macro etc.) e registra no MLflow.

7. **Predição**  
   `src.model.pipeline.predict` é usado para inferência pontual: recebe
   `title` + `message`, aplica o mesmo pré-processamento e usa o modelo
   configurado/resolve o modelo correto para devolver a predição de sentimento.

## Interface com outras camadas

- **Makefile**  
  Expõe comandos amigáveis (`model-*` e `docker-model-*`) para orquestrar os
  scripts do módulo sem precisar lembrar todos os `python -m ...`.

- **Docker**  
  A imagem `tutoria-mlops-model` inclui apenas `src/model` + dependências,
  permitindo reutilizar o módulo em jobs de treino e, no futuro, também na API.

- **API (futuro)**  
  Quando a camada de API for criada (`src/api`), ela deve se basear neste módulo
  para:
  - validar e pré-processar requests,
  - chamar `src.model.pipeline.predict`,
  - possivelmente consultar MLflow ou repositórios de modelos.

Essa separação deixa claro que o **coração do ML** está em `src/model`,
e tudo ao redor (infra, API, UI) são “consumidores” dessa camada.
