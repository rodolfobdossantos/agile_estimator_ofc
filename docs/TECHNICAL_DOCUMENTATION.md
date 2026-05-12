# Agile Estimator v2 — Technical Documentation

**Versão:** 2.0  
**Stack:** Python 3.10+, Scikit-learn, FastAPI, Streamlit, Docker, Render  
**Repositório:** `c:\agile_estimator_ofc`  

---

## 1. Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTE (Browser)                          │
│                    Streamlit App (streamlit_app/)                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ POST /predict
                             │ {function_points, PC1, PC2}
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FastAPI (api/) — Render.com                      │
│              https://agile-estimator-ofc.onrender.com              │
│   /predict → preprocess (feature_order) → model.predict → exp()   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                  ┌──────────┴──────────┐
                  │  Artifacts (api/)   │
                  │  agile_estimator_v2.pkl  (Lasso model)          │
                  │  pca_2.pkl               (PCA n=2)              │
                  │  scaler_pca_features.pkl (StandardScaler)       │
                  └─────────────────────┘

Pré-processamento client-side (Streamlit):
  raw inputs (5 fields)
    → scaler_pca_features.pkl → pca_2.pkl → {PC1, PC2}
    → POST /predict {function_points, PC1, PC2}
    → response {prediction: effort_hours}
```

---

## 2. Dataset — Maxwell

| Atributo | Valor |
|----------|-------|
| **Fonte** | K.D. Maxwell, "Applied Statistics for Software Managers" (2002) |
| **Projetos** | 62 projetos reais de telecomunicações |
| **Após limpeza** | 57 projetos (outliers removidos por IQR em effort_hours) |
| **Caminho** | `model/data/raw/maxx.csv` |

### Colunas relevantes

| Coluna original | Nome canônico | Descrição |
|----------------|---------------|-----------|
| `Size` | `function_points` | Adjusted Function Points (AFP) |
| `Effort` | `effort_hours` | Esforço total em horas-pessoa (variável-alvo) |
| `T03` | `performance_requirements` | Fator de ajuste técnico: performance |
| `T09` | `complex_processing` | Fator de ajuste técnico: complexidade de processamento |
| `T11` | `installation_ease` | Fator de ajuste técnico: facilidade de instalação |
| `T15` | `additional_complexity_factor` | Fator de ajuste técnico: complexidade adicional |

### Remoção de outliers
```python
Q3 = df["effort_hours"].quantile(0.75)
IQR = df["effort_hours"].quantile(0.75) - df["effort_hours"].quantile(0.25)
df = df[df["effort_hours"] <= Q3 + 1.5 * IQR]
# Resultado: 62 → 57 projetos
```

---

## 3. Pipeline de Pré-processamento

### 3.1 Transformação da variável-alvo
```python
y = np.log(df["effort_hours"])  # log-transform para simetria
# No predict: return np.exp(model.predict(X)[0])  # desfaz o log
```

### 3.2 Features de entrada do modelo
O modelo recebe **3 features**, todas padronizadas:
1. `function_points` — padronizado via `scaler_maxx.pkl` (índice 0: mean=514.86, scale=516.24)
2. `PC1` — 1ª componente principal dos 4 fatores de complexidade
3. `PC2` — 2ª componente principal dos 4 fatores de complexidade

> **Importante:** o CSV de treino (`maxx_processed.csv`) já contém `function_points` padronizado. A inferência deve aplicar a mesma transformação antes de enviar à API.

### 3.3 Preprocessing completo (client-side no Streamlit)

```python
BUSINESS_FEATURES = [
    "performance_requirements",  # T03
    "complex_processing",        # T09
    "installation_ease",         # T11
    "additional_complexity_factor", # T15
]

# Passo 1: Padronizar function_points (scaler_maxx.pkl, índice 0)
scaler_fp = joblib.load("api/artifacts/preprocessing/scaler_maxx.pkl")
fp_std = (function_points - scaler_fp.mean_[0]) / scaler_fp.scale_[0]
# mean_[0] = 514.8596, scale_[0] = 516.2373

# Passo 2: StandardScaler nos 4 fatores Likert
scaler = joblib.load("api/artifacts/preprocessing/scaler_pca_features.pkl")
X_scaled = scaler.transform(X[BUSINESS_FEATURES])

# Passo 3: PCA (n_components=2, ~70% da variância explicada)
pca = joblib.load("api/artifacts/preprocessing/pca_2.pkl")
pcs = pca.transform(X_scaled)
PC1, PC2 = pcs[0, 0], pcs[0, 1]

# Payload enviado à API:
payload = {"function_points": fp_std, "PC1": PC1, "PC2": PC2}
```

### 3.4 Parâmetros do scaler_pca_features.pkl

| Feature | Média (mean_) | Desvio (scale_) |
|---------|--------------|-----------------|
| performance_requirements | 3.000 | 0.898 |
| complex_processing | 4.035 | 0.748 |
| installation_ease | 3.316 | 0.940 |
| additional_complexity_factor | 3.298 | 0.748 |

### 3.5 Interpretação dos componentes PCA

| Componente | Interpretação | Principais cargas |
|------------|---------------|------------------|
| PC1 | Complexidade técnica geral | `complex_processing` + `additional_complexity_factor` + `installation_ease` |
| PC2 | Tradeoff performance vs. instalação | `performance_requirements` vs. `installation_ease` |

---

## 4. Modelo

| Atributo | Valor |
|----------|-------|
| **Algoritmo** | Lasso Regression (`sklearn.linear_model.Lasso`) |
| **Seleção** | Menor RMSE entre Ridge, Lasso, SVR, RandomForest, GradientBoosting |
| **Validação** | `RepeatedKFold(n_splits=5, n_repeats=10, random_state=42)` |
| **RMSE** | ~1.877 horas |
| **MAPE** | ~49% |
| **Target** | `log(effort_hours)` — destransformado com `exp()` na resposta da API |
| **Artefato** | `api/artifacts/model/agile_estimator_v2.pkl` |

---

## 5. API — FastAPI

### 5.1 Estrutura

```
api/
├── app/
│   ├── main.py           # FastAPI app, CORS, rotas
│   ├── predict.py        # lógica de inferência
│   ├── model_loader.py   # carrega pkl dos artifacts
│   ├── feature_loader.py # lê features.json
│   └── schemas.py        # Pydantic models
├── artifacts/
│   ├── model/agile_estimator_v2.pkl
│   └── preprocessing/
│       ├── pca_2.pkl
│       ├── scaler_pca_features.pkl
│       └── scaler_maxx.pkl  # legacy, não usado no predict
├── Dockerfile
└── docker-compose.yml
```

### 5.2 Endpoint

```
POST https://agile-estimator-ofc.onrender.com/predict
Content-Type: application/json

Request:
{
  "function_points": 300.0,
  "PC1": 0.42,
  "PC2": -0.17
}

Response:
{
  "prediction": 3428.5
}
```

O valor de `prediction` já é `np.exp(model.predict(...)[0])` — representa horas-pessoa.

### 5.3 Schema Pydantic (`schemas.py`)

```python
class PredictionInput(BaseModel):
    function_points: float
    PC1: float
    PC2: float
```

### 5.4 Fluxo de inferência (`predict.py`)

```python
def predict(input: PredictionInput) -> float:
    features = ["function_points", "PC1", "PC2"]
    df = pd.DataFrame([input.dict()])[features]
    prediction = model.predict(df)
    return float(np.exp(prediction[0]))
```

### 5.5 Deploy

- **Plataforma:** [Render.com](https://render.com) — plano gratuito
- **Containerização:** Docker (`api/Dockerfile`)
- **Cold start:** ~30s se a instância estiver inativa (plano gratuito hiberna após 15min sem tráfego)

---

## 6. Interface Streamlit

### 6.1 Estrutura

```
streamlit_app/
├── app.py
└── scripts_app/
    └── get_public_trello_board.py
```

### 6.2 Fluxo principal

```
1. Usuário insere dados (manual / CSV / Trello)
2. app.py carrega scaler_pca_features.pkl e pca_2.pkl (@st.cache_resource)
3. preprocess_for_api(row): raw features → scaled → PCA → {function_points, PC1, PC2}
4. call_predict_api(payload): POST /predict → effort_hours
5. estimate_batch(df): itera todos os projetos, adiciona colunas de resultado
6. UI exibe tabela + gráficos + download CSV
```

### 6.3 Funções-chave

```python
def preprocess_for_api(row: dict) -> dict:
    X = pd.DataFrame([row])[BUSINESS_FEATURES].astype(float)
    X_scaled = scaler.transform(X)
    pcs = pca.transform(X_scaled)[0]
    # function_points deve ser padronizado para corresponder ao CSV de treino
    fp_std = (float(row["function_points"]) - FP_MEAN) / FP_SCALE
    return {
        "function_points": fp_std,  # padronizado (não raw)
        "PC1": float(pcs[0]),
        "PC2": float(pcs[1]),
    }

def call_predict_api(payload: dict) -> float:
    resp = requests.post(API_URL, json=payload, timeout=30)
    resp.raise_for_status()
    return float(resp.json()["prediction"])
```

### 6.4 Integração com Trello

```python
# get_public_trello_board.py
def get_trello_cards_public(url: str) -> pd.DataFrame:
    board_id = re.match(r"^https://trello\.com/b/([a-zA-Z0-9]+)", url).group(1)
    data = requests.get(f"https://trello.com/b/{board_id}.json", timeout=15).json()

    # Mapeia field_id → nome canônico via _FIELD_ALIASES (case-insensitive)
    # Extrai .value.number de customFieldItems por cartão
    # Retorna DataFrame com project_id + 5 colunas; NaN onde não preenchido
```

Campos esperados no Trello (aceitos em várias grafias):
- `function_points` / `function points`
- `performance_requirements` / `performance requirements`
- `complex_processing` / `complex processing`
- `installation_ease` / `instalation_ease` / variações
- `additional_complexity_factor` / `aditional_complexity_factor` / variações

### 6.5 Calculadora IFPUG embutida

Disponível como expander na aba "Input Manual". Pesos IFPUG padrão:

| Tipo | Simples | Média | Complexa |
|------|---------|-------|----------|
| EI — External Input | 3 | 4 | 6 |
| EO — External Output | 4 | 5 | 7 |
| EQ — External Query | 3 | 4 | 6 |
| ILF — Internal Logical File | 7 | 10 | 15 |
| EIF — External Interface File | 5 | 7 | 10 |

**UFP** = soma de (quantidade × peso) para cada tipo/complexidade  
**AFP** = UFP × VAF, onde **VAF = 0.65 + 0.01 × TDI** (TDI = soma dos 14 fatores, 0–70)

O resultado pode ser transferido diretamente para o campo Function Points com um clique.

---

## 7. Artifacts — Inventário

| Arquivo | Tipo | Onde usado | Observações |
|---------|------|-----------|-------------|
| `api/artifacts/model/agile_estimator_v2.pkl` | `sklearn.linear_model.Lasso` | API `/predict` | Treinado em 57 projetos Maxwell, target = `log(effort)` |
| `api/artifacts/preprocessing/pca_2.pkl` | `sklearn.decomposition.PCA` | Streamlit + API | n_components=2, ~70% variância explicada |
| `api/artifacts/preprocessing/scaler_pca_features.pkl` | `sklearn.preprocessing.StandardScaler` | Streamlit (client-side) | Fitado nas 4 features Maxwell (T03, T09, T11, T15), 57 linhas |
| `api/artifacts/preprocessing/scaler_maxx.pkl` | `sklearn.preprocessing.StandardScaler` | Streamlit (client-side) — apenas índice 0 | Fitado em 9 features Maxwell; índice 0 (`function_points`) é usado para padronizar o AFP antes da inferência |

> **Nota sobre `scaler_maxx.pkl`:** embora seja um scaler de 9 features, somente o índice 0 (`function_points`, mean=514.86, scale=516.24) é utilizado na inferência. Os demais índices correspondem a features não usadas no modelo v2.

---

## 8. Como Retreinar o Modelo

### Passo 1 — Preparar dados

```bash
# Dados brutos em: model/data/raw/maxx.csv
# Notebook de referência: model/notebooks/treino/agile_v2/modelagem-ml.ipynb
```

### Passo 2 — Rodar notebook de modelagem

Abrir e executar `model/notebooks/treino/agile_v2/modelagem-ml.ipynb`.  
O notebook executa:
1. Carregamento e renomeação das colunas do Maxwell
2. Remoção de outliers (IQR em effort_hours)
3. `log(effort_hours)` como target
4. Seleção de features por correlação (|r| > 0.2)
5. StandardScaler → PCA(n=2) nos 4 fatores
6. GridSearchCV com RepeatedKFold para Lasso, Ridge, SVR, RF, GBT
7. Seleção do melhor modelo (Lasso)
8. Salvamento dos artefatos

### Passo 3 — Salvar o scaler correto

O scaler para o pré-processamento dos 4 fatores deve ser salvo **separadamente** dos demais. Após o fit do `StandardScaler` nos 4 fatores:

```python
import joblib
joblib.dump(scaler_business, "api/artifacts/preprocessing/scaler_pca_features.pkl")
joblib.dump(pca, "api/artifacts/preprocessing/pca_2.pkl")
joblib.dump(model, "api/artifacts/model/agile_estimator_v2.pkl")
```

### Passo 4 — Redeploy da API

```bash
# Localmente:
cd api
docker build -t agile-estimator-api .
docker run -p 8000:8000 agile-estimator-api

# Render: push para branch main → Render faz redeploy automático via GitHub
```

---

## 9. Variáveis de Ambiente

A API não requer variáveis de ambiente para o endpoint `/predict`. Todos os artefatos são carregados de caminhos relativos dentro do container.

A interface Streamlit também não requer variáveis de ambiente — a URL da API está hardcoded:
```python
API_URL = "https://agile-estimator-ofc.onrender.com/predict"
```

---

## 10. Como Rodar Localmente

### API
```bash
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# Acesse: http://localhost:8000/docs
```

### Streamlit
```bash
cd streamlit_app
pip install -r ../requirements.txt
streamlit run app.py
```

> Para usar a API local, altere `API_URL` em `app.py` para `http://localhost:8000/predict`.

### Docker (API)
```bash
cd api
docker-compose up --build
```

---

## 11. Testes

```
tests/
```

Para adicionar testes de integração, recomenda-se verificar:
1. `POST /predict` com payload válido → `prediction` > 0
2. `preprocess_for_api` com valores de borda (mínimo Likert = 1, máximo = 5)
3. `get_trello_cards_public` com board de demonstração público

---

## 12. Dependências Principais

| Biblioteca | Versão recomendada | Uso |
|-----------|-------------------|-----|
| `scikit-learn` | ≥ 1.3 | Lasso, StandardScaler, PCA |
| `fastapi` | ≥ 0.100 | API REST |
| `uvicorn` | ≥ 0.22 | ASGI server |
| `streamlit` | ≥ 1.30 | Interface web |
| `joblib` | ≥ 1.3 | Serialização de artefatos |
| `pandas` | ≥ 2.0 | Manipulação de dados |
| `numpy` | ≥ 1.25 | Operações numéricas |
| `altair` | ≥ 5.0 | Visualizações no Streamlit |
| `requests` | ≥ 2.31 | HTTP client (Streamlit → API) |
| `mlflow` | ≥ 2.0 | Rastreamento de experimentos |
