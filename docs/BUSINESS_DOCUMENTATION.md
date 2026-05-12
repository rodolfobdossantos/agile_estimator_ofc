# Agile Estimator v2 — Business Documentation

**Versão:** 2.0  
**Responsável:** Sávio Mendes  
**Data de entrega:** Maio / 2026  
**Proposta de referência:** Fase 2 — Modelagem + API + Deploy + Integração  

---

## 1. Visão Geral

O **Agile Estimator v2** é uma ferramenta de estimativa baseada em Inteligência Artificial que prevê o **esforço total em horas-pessoa** necessário para desenvolver um projeto de software do início ao fim.

A ferramenta combina:
- Um modelo de Machine Learning treinado em dados reais de projetos de software
- Uma API REST para inferência em produção
- Uma interface web interativa para uso pelos gestores e times de desenvolvimento
- Integração automática com boards do Trello (entrega adicional, fora do escopo original)

---

## 2. Proposta Comercial — O Que Foi Contratado

### Fase 2 — Modelagem, API e Integração

| Item | Detalhe |
|------|---------|
| **Valor** | R$ 2.300,00 |
| **Esforço estimado** | ~80 horas-pessoa |
| **Prazo contratado** | Início: 18/03 — Entrega final: 30/04/2026 |
| **Atraso real** | ~10 dias (entrega efetiva: maio/2026) |

### Marcos contratuais (Fase 2)

| Marco | Descrição | Status |
|-------|-----------|--------|
| M1 — Data Engineering | Pipeline de coleta e limpeza de dados reais (Maxwell dataset) | ✅ Entregue |
| M2 — Modeling | Treinamento, avaliação e seleção do modelo final (Lasso v2) | ✅ Entregue |
| M3 — API | API REST (FastAPI) com endpoint `/predict` para inferência | ✅ Entregue |
| M4 — Deploy | Containerização (Docker) e hospedagem na Render | ✅ Entregue |
| M5 — Integration | Interface Streamlit integrada com a API v2 | ✅ Entregue |

---

## 3. O Que Foi Entregue

### Escopo da Fase 2 (contratado)

- **Dataset:** Dados reais do dataset Maxwell (62 projetos de telecomunicações, K.D. Maxwell, 2002)
- **Modelo:** Regressão Lasso com validação cruzada repetida (RepeatedKFold), selecionado por menor RMSE entre 6 algoritmos
- **Pré-processamento:** StandardScaler + PCA (n=2) sobre 4 fatores de complexidade técnica
- **Variável predita:** `effort_hours` — esforço total do projeto em horas-pessoa
- **API:** FastAPI hospedada em `https://agile-estimator-ofc.onrender.com`
  - Endpoint: `POST /predict` com payload `{function_points, PC1, PC2}`
  - Retorno: `{prediction}` em horas-pessoa (já transformado via `exp`)
- **Deploy:** Docker + Render (plano gratuito)
- **Interface:** Streamlit com 4 modos de entrada (manual, CSV, Trello, tutorial)

### Entrega Adicional (fora do escopo — Phase 3 antecipada)

A **integração com o Trello** foi especificada na proposta como Phase 3 (trabalho futuro), mas foi **antecipada e entregue nesta fase** como entrega adicional sem custo adicional:

- Importação automática de projetos via link de board público do Trello
- Leitura dos 5 campos customizados diretamente dos cartões
- Validação de campos obrigatórios e tratamento de valores ausentes
- Zero configuração de chaves de API — funciona com boards públicos

---

## 4. Métricas do Modelo

| Métrica | Valor |
|---------|-------|
| **Algoritmo final** | Lasso Regression |
| **RMSE** | ~1.877 horas |
| **MAPE médio** | ~49% |
| **Dataset de treino** | Maxwell (57 projetos após remoção de outliers) |
| **Variância explicada pelo PCA** | ~70% |

### Interpretação das métricas

O MAPE de ~49% é esperado e aceitável para esta categoria de problema:

- Estimativas de esforço em software têm variabilidade intrínseca alta mesmo com dados reais
- O modelo é mais confiável para **comparar projetos entre si** do que para prever esforço absoluto
- Serve como **baseline quantitativo** — substitui estimativas puramente subjetivas por um ponto de referência consistente
- Projetos similares ao perfil Maxwell (telecomunicações, médio porte, linguagens tradicionais) terão estimativas mais precisas

---

## 5. Inputs do Sistema

O sistema requer **5 valores por projeto**:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| **Function Points** | Número livre (AFP) | Tamanho funcional do software em Adjusted Function Points. Calculável via a calculadora IFPUG embutida na interface. |
| **Performance Requirements** | Escala 1–5 (Likert) | Exigência de desempenho e velocidade do sistema |
| **Complex Processing** | Escala 1–5 (Likert) | Grau de complexidade técnica do processamento |
| **Installation Ease** | Escala 1–5 (Likert) | Facilidade de instalação/deploy *(5 = muito fácil, 1 = muito difícil)* |
| **Additional Complexity Factor** | Escala 1–5 (Likert) | Fatores adicionais de complexidade fora do escopo padrão |

Os 4 fatores em escala Likert seguem o padrão dos **Fatores de Ajuste Técnico (TCA)** do dataset Maxwell (colunas T03, T09, T11, T15).

---

## 6. Outputs do Sistema

Para cada projeto, o sistema retorna:

| Output | Cálculo | Uso recomendado |
|--------|---------|-----------------|
| **Esforço estimado (h)** | Direto do modelo | Base para negociação e planejamento |
| **Dias estimados** | Horas ÷ 8 (jornada diária) | Conversão para cronograma |
| **Semanas estimadas** | Dias ÷ 5 (semana útil) | Planejamento de releases |

---

## 7. Modos de Uso

### 7.1 Input Manual
Preenchimento campo a campo na interface. Inclui calculadora IFPUG embutida para quem não sabe o número de Function Points do projeto.

### 7.2 Upload de CSV
Importação em lote. O CSV deve conter as colunas:
```
project_id, function_points, performance_requirements, complex_processing, installation_ease, additional_complexity_factor
```

### 7.3 Importação do Trello
Cole o link de um board público do Trello. Os cartões devem ter campos customizados com os nomes correspondentes. O sistema importa automaticamente todos os cartões com os 5 campos preenchidos.

---

## 8. Limitações Conhecidas

| Limitação | Impacto | Mitigação |
|-----------|---------|-----------|
| Dataset pequeno (62 projetos) | MAPE ~49% | Use como estimativa inicial, não como compromisso contratual |
| Domínio específico (telecom) | Pode subestimar projetos de outros setores | Calibrar com histórico interno |
| Fatores subjetivos (escala Likert) | Avaliadores diferentes podem dar notas diferentes | Padronizar critérios de avaliação entre o time |
| API hospedada em plano gratuito (Render) | Cold start de ~30s se a API estiver inativa | Fazer uma requisição de "warm up" antes do uso crítico |

---

## 9. Roadmap Sugerido (Phase 3+)

| Fase | Iniciativa | Valor de Negócio |
|------|------------|-----------------|
| **Phase 3** | Integração completa com Trello autenticado (boards privados) | Permite uso em projetos reais da empresa |
| **Phase 3** | Retreinamento com dados históricos da empresa | Maior precisão para o domínio específico do cliente |
| **Phase 4** | Intervalo de confiança nas previsões (±MAPE band) | Gestores veem o range de risco, não só ponto estimado |
| **Phase 4** | Dashboard de acompanhamento por sprint | Comparar esforço estimado vs. realizado ao longo do projeto |
| **Phase 5** | Integração com Jira / Azure DevOps | Automação completa do pipeline de estimativa |

---

## 10. Contato e Suporte

**Responsável técnico:** Sávio Mendes  
**Repositório:** `c:\agile_estimator_ofc`  
**API em produção:** https://agile-estimator-ofc.onrender.com  
**Board de demonstração (Trello):** https://trello.com/b/DKf6KNh2/testeagileestimator  
