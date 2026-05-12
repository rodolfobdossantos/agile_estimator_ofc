from fpdf import FPDF

TODAY = "11/05/2026"
OUT_PATH = "docs/entrega_marcos_4_5.pdf"


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 7, "Agile Estimator v2  |  Relatorio de Entrega - Marcos 4 e 5", align="L")
        self.set_draw_color(200, 200, 200)
        self.line(10, 16, 200, 16)
        self.ln(5)

    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, f"Confidencial  |  Gerado em {TODAY}  |  Pagina {self.page_no()}", align="C")

    def cover_page(self):
        self.add_page()
        self.set_y(45)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(25, 55, 115)
        self.cell(0, 12, "Agile Estimator v2", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(70, 70, 70)
        self.cell(0, 8, "Relatorio de Entrega - Marcos 4 e 5", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(8)
        self.set_draw_color(25, 55, 115)
        self.set_line_width(0.8)
        self.line(40, self.get_y(), 170, self.get_y())
        self.ln(10)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(50, 50, 50)
        meta = [
            ("Responsavel tecnico", "Savio Mendes"),
            ("Data do relatorio", TODAY),
            ("API em producao", "https://agile-estimator-ofc.onrender.com"),
            ("Board Trello demo", "https://trello.com/b/DKf6KNh2/testeagileestimator"),
        ]
        for label, val in meta:
            self.set_font("Helvetica", "B", 11)
            self.cell(60, 7, label + ":", align="R")
            self.set_font("Helvetica", "", 11)
            self.cell(0, 7, "  " + val, new_x="LMARGIN", new_y="NEXT")
        self.ln(12)
        self.set_fill_color(238, 244, 255)
        self.set_draw_color(170, 195, 235)
        self.set_line_width(0.3)
        box_y = self.get_y()
        self.rect(28, box_y, 154, 36, style="FD")
        self.set_xy(33, box_y + 5)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(25, 55, 115)
        self.cell(0, 6, "Escopo deste documento", new_x="LMARGIN", new_y="NEXT")
        self.set_x(33)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(45, 45, 45)
        self.multi_cell(144, 5.5,
            "Este documento confirma a entrega completa dos Marcos 4 e 5 do contrato "
            "Fase 2 - Agile Estimator v2. Cobre o que foi entregue, como foi implementado, "
            "bugs corrigidos, artefatos gerados e instrucoes de operacao."
        )

    def sec(self, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(25, 55, 115)
        self.set_fill_color(232, 240, 255)
        self.cell(0, 8, "  " + title, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(25, 55, 115)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_text_color(35, 35, 35)
        self.set_line_width(0.2)

    def sub(self, title):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(25, 55, 115)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(35, 35, 35)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(self.l_margin)
        self.multi_cell(190, 5.5, text)

    def bullet(self, text, indent=6):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(10 + indent)
        self.cell(5, 5.5, "-")
        self.multi_cell(185 - indent, 5.5, text)

    def tbl(self, headers, rows, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(40, 80, 160)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(160, 160, 160)
        self.set_line_width(0.2)
        for h, w in zip(headers, widths):
            self.cell(w, 7, h, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 9)
        for i, row in enumerate(rows):
            if i % 2 == 0:
                self.set_fill_color(244, 248, 255)
            else:
                self.set_fill_color(255, 255, 255)
            self.set_text_color(30, 30, 30)
            for val, w in zip(row, widths):
                self.cell(w, 6, str(val), border=1, fill=True)
            self.ln()
        self.ln(2)

    def code(self, text):
        self.set_font("Courier", "", 8.5)
        self.set_fill_color(246, 246, 246)
        self.set_draw_color(210, 210, 210)
        lines = text.strip().split("\n")
        height = len(lines) * 5 + 6
        self.rect(10, self.get_y(), 190, height, style="FD")
        self.set_y(self.get_y() + 3)
        for line in lines:
            self.set_x(14)
            self.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_font("Helvetica", "", 10)

    def num_step(self, n, title, desc):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(25, 55, 115)
        self.set_x(self.l_margin)
        self.cell(8, 6, f"{n}.")
        self.cell(182, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(18)
        self.multi_cell(182, 5.5, desc)
        self.set_x(self.l_margin)
        self.ln(1)


pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)

# ---------- CAPA ----------
pdf.cover_page()

# ========================================================
# MARCO 4
# ========================================================
pdf.add_page()
pdf.sec("Marco 4 - Infraestrutura e Deploy")
pdf.ln(1)

pdf.set_font("Helvetica", "", 10)
pdf.tbl(
    ["Campo", "Detalhe"],
    [
        ["Data de entrega contratada", "16/04/2026"],
        ["Valor do marco", "R$ 460,00"],
        ["Status", "ENTREGUE"],
    ],
    [55, 135],
)

pdf.sub("4.1  Objetivo do Marco")
pdf.body(
    "Containerizar a API de inferencia com Docker e implanta-la em infraestrutura de nuvem "
    "com URL publica acessivel via HTTPS, garantindo reinicio automatico em caso de falha."
)

pdf.sub("4.2  O Que Foi Entregue")
pdf.tbl(
    ["Entregavel", "Descricao", "Status"],
    [
        ["Dockerfile", "Imagem python:3.11-slim; uvicorn; porta configuravel via $PORT", "Entregue"],
        ["docker-compose.yml", "restart: always - reinicio automatico em falha", "Entregue"],
        ["Deploy Render.com", "API publicada em URL publica com HTTPS automatico", "Entregue"],
        ["GET /health", "Verifica modelo carregado, arquivo .pkl e inferencia de sanidade", "Entregue"],
        ["POST /predict", "Endpoint de inferencia com schema Pydantic validado", "Entregue"],
        ["Logging estruturado", "Logs de predicao e erros via app/logger.py", "Entregue"],
    ],
    [50, 102, 38],
)

pdf.sub("4.3  Dockerfile")
pdf.code(
    "FROM python:3.11-slim\n"
    "ENV PYTHONDONTWRITEBYTECODE=1\n"
    "ENV PYTHONUNBUFFERED=1\n"
    "WORKDIR /app\n"
    "COPY requirements.txt .\n"
    "RUN pip install --no-cache-dir -r requirements.txt\n"
    "COPY . .\n"
    "EXPOSE 8000\n"
    'CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]'
)

pdf.sub("4.4  docker-compose.yml (reinicio automatico)")
pdf.code(
    "version: \"3.9\"\n"
    "services:\n"
    "  api:\n"
    "    build: .\n"
    "    container_name: agile_api\n"
    "    ports:\n"
    '      - "8000:10000"\n'
    "    volumes:\n"
    "      - .:/app\n"
    "    restart: always      # reinicia automaticamente em falha"
)

pdf.sub("4.5  Endpoints em Producao")
pdf.tbl(
    ["Endpoint", "Metodo", "Descricao"],
    [
        ["https://agile-estimator-ofc.onrender.com/predict", "POST", "Inferencia - retorna horas-pessoa"],
        ["https://agile-estimator-ofc.onrender.com/health", "GET", "Health check com 3 verificacoes"],
        ["https://agile-estimator-ofc.onrender.com/docs", "GET", "Swagger UI (FastAPI automatico)"],
    ],
    [103, 20, 67],
)

pdf.sub("4.6  Health Check (/health)")
pdf.body("O endpoint realiza 3 verificacoes a cada chamada:")
pdf.bullet("Modelo carregado em memoria (model is not None)")
pdf.bullet("Arquivo agile_estimator_v2.pkl existe no filesystem do container")
pdf.bullet("Inferencia de sanidade - executa predict() e verifica resultado valido")
pdf.body('\nRetorna {"status": "ok"} quando todos os checks passam, "degraded" se algum falha.')

pdf.sub("4.7  Plataforma de Deploy - Render.com")
pdf.bullet("Deploy automatico via push para branch main no GitHub")
pdf.bullet("HTTPS nativo com certificado SSL automatico")
pdf.bullet("Reinicio automatico em caso de crash (Docker restart: always)")
pdf.bullet("Cold start de ~30s se inativo ha mais de 15 minutos (plano gratuito)")
pdf.bullet("Para eliminar cold start: upgrade para plano pago ($7/mes) ou ping periodico via cron")

# ========================================================
# MARCO 5
# ========================================================
pdf.add_page()
pdf.sec("Marco 5 - Integracao Streamlit e Documentacao Tecnica")
pdf.ln(1)

pdf.tbl(
    ["Campo", "Detalhe"],
    [
        ["Escopo", "Integracao Streamlit com API REST + Documentacao + Testes"],
        ["Status", "ENTREGUE"],
    ],
    [55, 135],
)

pdf.sub("5.1  Objetivo do Marco")
pdf.body(
    "Adequar a interface Streamlit para consumir exclusivamente a API REST, removendo "
    "qualquer execucao direta do modelo no frontend. Documentar a arquitetura, o pipeline "
    "de dados, o processo de re-treino manual e as instrucoes de operacao. "
    "Realizar testes e validacoes finais."
)

pdf.sub("5.2  Integracao Streamlit - API REST (sem modelo local)")
pdf.body(
    "A interface nao executa o modelo localmente. Todo processamento de inferencia "
    "ocorre na API hospedada no Render. O Streamlit realiza somente pre-processamento client-side:"
)
pdf.ln(2)
pdf.tbl(
    ["Etapa", "Onde Ocorre", "Descricao"],
    [
        ["Coleta de inputs", "Streamlit", "Manual / CSV / Trello"],
        ["Padronizacao function_points", "Streamlit", "(fp - 514.86) / 516.24 via scaler_maxx.pkl[0]"],
        ["StandardScaler + PCA", "Streamlit", "4 fatores Likert -> PC1, PC2 via artefatos .pkl"],
        ["POST /predict", "Streamlit -> API REST", "Envia {function_points_std, PC1, PC2}"],
        ["Inferencia Lasso", "API no Render", "model.predict(X) + np.exp() -> effort_hours"],
        ["Resultados", "Streamlit", "Tabela, graficos Altair, download CSV"],
    ],
    [48, 44, 98],
)

pdf.sub("5.3  Funcionalidades da Interface")
pdf.tbl(
    ["Funcionalidade", "Descricao"],
    [
        ["Tutorial interativo", "Explica modelo, inputs, outputs, escala Likert e limitacoes"],
        ["Input Manual", "Formulario com 5 campos; validacao Likert 1-5; nao sobreescreve dados anteriores"],
        ["Calculadora IFPUG embutida", "Calcula AFP via pesos EI/EO/EQ/ILF/EIF; ajuste VAF opcional"],
        ["Upload CSV", "Importacao em lote; preview 10 linhas; botao de confirmacao antes de carregar"],
        ["Integracao Trello", "Importa de board publico via URL; sem autenticacao; preview antes de carregar"],
        ["Calculo de estimativas", "Chama API individualmente para cada projeto; dias e semanas estimados"],
        ["Visualizacoes (Altair)", "Histograma, scatter FP x esforco, scatter complexidade x esforco, bar chart"],
        ["Download CSV", "Exporta project_id, horas, dias e semanas estimados"],
        ["FAQ lateral (sidebar)", "Perguntas frequentes sobre o sistema e o modelo"],
    ],
    [58, 132],
)

pdf.sub("5.4  Integracao Trello (entrega adicional - Phase 3 antecipada)")
pdf.body(
    "A integracao Trello estava prevista para a Phase 3 (escopo futuro), mas foi "
    "antecipada e entregue nesta fase sem custo adicional."
)
pdf.bullet("Aceita URL no formato https://trello.com/b/<board_id>")
pdf.bullet("GET ao endpoint publico https://trello.com/b/<id>.json (sem autenticacao)")
pdf.bullet("Mapeamento case-insensitive de nomes de campos com tolerancia a erros ortograficos")
pdf.bullet("Preview dos dados antes de carregar (evita sobreescrita acidental)")
pdf.bullet("Validacao de campos obrigatorios com mensagem de erro descritiva")

# ========================================================
# PIPELINE TECNICO
# ========================================================
pdf.add_page()
pdf.sec("Pipeline de Dados e Modelo")

pdf.sub("Modelo de Machine Learning")
pdf.tbl(
    ["Atributo", "Valor"],
    [
        ["Algoritmo", "Lasso Regression (sklearn.linear_model.Lasso)"],
        ["Selecao", "Menor RMSE entre Ridge, Lasso, SVR, RandomForest, GradientBoosting"],
        ["Validacao cruzada", "RepeatedKFold(n_splits=5, n_repeats=10, random_state=42)"],
        ["Hiperparametro alpha", "0.1 (selecionado por GridSearchCV - grid: [0.001, 0.01, 0.1, 1])"],
        ["RMSE no holdout", "~1.877 horas"],
        ["MAPE no holdout", "~49%"],
        ["Dataset de treino", "Maxwell - 57 projetos (62 menos outliers por IQR em effort_hours)"],
        ["Variavel-alvo", "log(effort_hours); API retorna np.exp(prediction)"],
        ["Coeficientes Lasso", "function_points: 0.341  |  PC1: 0.167  |  PC2: -0.272"],
        ["Intercept", "8.358  =>  np.exp(8.358) ~ 4.254 horas (media do dataset)"],
    ],
    [68, 122],
)

pdf.sub("Pipeline de Pre-processamento de Inferencia")
pdf.code(
    "# 1. Padronizar function_points  (artefato: scaler_maxx.pkl, indice 0)\n"
    "fp_std = (function_points - 514.8596) / 516.2373\n"
    "\n"
    "# 2. Padronizar 4 fatores Likert  (artefato: scaler_pca_features.pkl)\n"
    "X_scaled = scaler_pca_features.transform([[perf_req, complex_proc, inst_ease, add_complexity]])\n"
    "\n"
    "# 3. Reducao de dimensionalidade  (artefato: pca_2.pkl, ~70% variancia explicada)\n"
    "PC1, PC2 = pca_2.transform(X_scaled)[0]\n"
    "\n"
    "# 4. POST /predict\n"
    'payload = {"function_points": fp_std, "PC1": PC1, "PC2": PC2}\n'
    "\n"
    "# 5. API retorna\n"
    "effort_hours = np.exp(model.predict([[fp_std, PC1, PC2]])[0])"
)

pdf.sub("Como Re-treinar o Modelo (processo manual)")
steps_retrain = [
    ("Passo 1 - Dados",
     "Atualizar model/data/raw/maxx.csv com novos projetos, se houver."),
    ("Passo 2 - EDA",
     "Executar model/notebooks/inferencia/agile_v2/eda.ipynb para re-validar "
     "correlacoes, outliers e PCA."),
    ("Passo 3 - Treino",
     "Executar model/notebooks/treino/agile_v2/modelagem-ml.ipynb. O notebook salva "
     "automaticamente os artefatos em api/artifacts/ e model/artifacts/."),
    ("Passo 4 - Validar",
     "Verificar que os coeficientes Lasso sao nao-zero. O notebook foi corrigido "
     "para usar grid.best_estimator_ (evita refit com alpha=1.0 padrao)."),
    ("Passo 5 - Deploy",
     "git push para branch main. O Render detecta alteracao nos .pkl e refaz o "
     "deploy automaticamente em ~2 minutos."),
]
for i, (title, desc) in enumerate(steps_retrain, 1):
    pdf.num_step(i, title, desc)

# ========================================================
# TESTES E VALIDACOES
# ========================================================
pdf.add_page()
pdf.sec("Testes e Validacoes Finais")

pdf.sub("Testes de Integracao Realizados")
pdf.tbl(
    ["Cenario de Teste", "Resultado Esperado", "Status"],
    [
        ["POST /predict com fp=500, fatores=3,3,3,3", "~3.000-5.000h; nao identico a outros inputs", "OK"],
        ["POST /predict: fp=200 vs fp=1000 (mesmos fatores)", "Predicoes diferentes proporcionais ao fp", "OK"],
        ["POST /predict: fatores 1,1,5,1 vs 5,5,1,5", "Predicoes diferentes por variacao Likert", "OK"],
        ["GET /health", "Status: ok; inference_ok: true", "OK"],
        ["Adicionar 3 projetos manuais diferentes", "Todos listados; estimativas distintas", "OK"],
        ["Upload CSV com 3 projetos", "Todos estimados individualmente", "OK"],
        ["Importar board Trello publico", "Cartoes com campos preenchidos importados", "OK"],
        ["Adicionar projeto apos importar Trello", "Nao sobreescreve dados do Trello", "OK"],
        ["Botao Limpar dados", "Zera st.session_state.data; lista some", "OK"],
        ["Download CSV de resultados", "Arquivo com horas, dias e semanas exportado", "OK"],
    ],
    [80, 72, 38],
)

pdf.sub("Bugs Identificados e Corrigidos")
pdf.tbl(
    ["Bug", "Causa Raiz", "Correcao Aplicada"],
    [
        ["Todas predicoes identicas (~3981h)",
         "Notebook salvava modelo com alpha=1.0 (coef=[0,0,0]) ao inves do alpha=0.1 do GridSearchCV",
         "Artefato substituido pelo modelo correto; notebook corrigido para usar grid.best_estimator_"],
        ["function_points sem efeito na predicao",
         "fp passado raw para API; modelo foi treinado com fp padronizado (CSV maxx_processed.csv)",
         "Adicionado (fp - 514.86) / 516.24 em preprocess_for_api() usando scaler_maxx.pkl[0]"],
        ["Botao 'Adicionar Projeto' nao funcionava",
         "Ausencia de st.rerun() apos append no session_state",
         "Adicionado st.toast() + st.rerun() no callback do botao"],
        ["Importacao Trello sobreescrevia dados manuais",
         "Fetch rodava em todo rerun do Streamlit, nao so no clique do usuario",
         "Fetch movido para dentro do callback do botao 'Buscar projetos do Trello'"],
        ["CSV sobreescrevia dados em todo rerun",
         "Mesmo padrao do Trello: escrita fora de callback de botao",
         "Adicionado botao 'Carregar este CSV' com preview antes de confirmar"],
        ["Botoes 'Limpar dados' nao funcionavam",
         "Ausencia de st.rerun() apos limpeza do session_state",
         "Adicionado st.rerun() nos callbacks de limpeza"],
    ],
    [50, 72, 68],
)

# ========================================================
# ARTEFATOS E OPERACAO
# ========================================================
pdf.add_page()
pdf.sec("Inventario de Artefatos Entregues")

pdf.tbl(
    ["Arquivo / Artefato", "Tipo", "Descricao"],
    [
        ["api/artifacts/model/agile_estimator_v2.pkl", "Lasso Pipeline", "alpha=0.1; coef=[0.341, 0.167, -0.272]"],
        ["api/artifacts/preprocessing/pca_2.pkl", "PCA n=2", "~70% variancia; PC1=complexidade tecnica"],
        ["api/artifacts/preprocessing/scaler_pca_features.pkl", "StandardScaler", "4 fatores Maxwell (T03,T09,T11,T15)"],
        ["api/artifacts/preprocessing/scaler_maxx.pkl", "StandardScaler", "Indice 0 = function_points (mean=514.86)"],
        ["api/Dockerfile", "Docker", "python:3.11-slim; porta via $PORT"],
        ["api/docker-compose.yml", "Docker Compose", "restart: always"],
        ["api/app/main.py", "FastAPI", "Rotas /predict e /health; CORS"],
        ["api/app/predict.py", "Python", "Logica de inferencia; feature selection"],
        ["api/app/schemas.py", "Pydantic", "PredictionInput: function_points, PC1, PC2"],
        ["streamlit_app/app.py", "Streamlit", "Interface completa; 4 modos entrada; 3 abas resultado"],
        ["streamlit_app/scripts_app/get_public_trello_board.py", "Python", "Importador Trello publico com alias de campos"],
        ["model/notebooks/treino/agile_v2/modelagem-ml.ipynb", "Jupyter", "Pipeline treino documentado e corrigido"],
        ["model/notebooks/inferencia/agile_v2/eda.ipynb", "Jupyter", "EDA com decisoes de modelagem documentadas"],
        ["docs/TECHNICAL_DOCUMENTATION.md", "Markdown", "Documentacao tecnica completa e atualizada"],
        ["docs/BUSINESS_DOCUMENTATION.md", "Markdown", "Documentacao de negocio e proposta comercial"],
    ],
    [93, 32, 65],
)

pdf.sec("Instrucoes de Operacao")

pdf.sub("Rodar Localmente")
pdf.code(
    "# API\n"
    "cd api\n"
    "pip install -r requirements.txt\n"
    "uvicorn app.main:app --reload --port 8000\n"
    "# Swagger: http://localhost:8000/docs\n"
    "\n"
    "# Interface Streamlit (terminal separado)\n"
    "cd streamlit_app\n"
    "streamlit run app.py\n"
    "# Para API local: altere API_URL em app.py para http://localhost:8000/predict\n"
    "\n"
    "# Via Docker\n"
    "cd api && docker-compose up --build"
)

pdf.sub("Testar a API Diretamente")
pdf.code(
    "# Health check\n"
    "curl https://agile-estimator-ofc.onrender.com/health\n"
    "\n"
    "# Predicao (function_points ja padronizado: (500 - 514.86) / 516.24 = -0.029)\n"
    "curl -X POST https://agile-estimator-ofc.onrender.com/predict \\\n"
    '     -H "Content-Type: application/json" \\\n'
    '     -d \'{"function_points": -0.029, "PC1": 0.5, "PC2": -0.3}\'\n'
    "\n"
    '# Resposta esperada: {"prediction": 4982.3}'
)

pdf.sub("Observacoes Importantes")
pdf.bullet(
    "Cold start da API: primeira requisicao apos 15 min de inatividade leva ~30s. "
    "Chamar GET /health antes de estimar reduz o impacto."
)
pdf.bullet(
    "O modelo estima o esforco do PROJETO INTEIRO (nao por sprint). "
    "Para 500 FP e complexidade media, espera-se ~3.000-5.000 horas-pessoa."
)
pdf.bullet(
    "Installation Ease e inversamente proporcional ao esforco: valor 5 = muito facil "
    "de instalar (menor esforco nessa dimensao). Valor 1 = muito dificil."
)
pdf.bullet(
    "MAPE ~49%: use as estimativas como baseline e para comparacao relativa entre "
    "projetos, nao como compromisso contratual absoluto."
)
pdf.bullet(
    "Re-treino do modelo: processo manual descrito na secao anterior. "
    "Nao requer intervencao na API durante o treino."
)

# ========================================================
# CONFIRMACAO DE ENTREGA
# ========================================================
pdf.add_page()
pdf.sec("Confirmacao de Entrega")
pdf.ln(6)

pdf.body(
    "Este documento comprova a entrega completa dos Marcos 4 e 5 do contrato "
    "Fase 2 - Agile Estimator v2, conforme acordado por email."
)
pdf.ln(6)

pdf.tbl(
    ["Marco", "Descricao Contratada", "Data Prevista", "Status", "Valor"],
    [
        ["Marco 4", "Infraestrutura e Deploy (Docker + Render)", "16/04/2026", "ENTREGUE", "R$ 460,00"],
        ["Marco 5", "Integracao Streamlit + Documentacao Tecnica", "Fase 2", "ENTREGUE", "Incluso"],
    ],
    [18, 84, 28, 26, 34],
)

pdf.ln(6)
pdf.body(
    "Todos os entregaveis listados neste documento foram implementados, testados "
    "e estao disponiveis no repositorio do projeto e em producao na URL publica "
    "https://agile-estimator-ofc.onrender.com."
)
pdf.ln(18)

pdf.set_draw_color(120, 120, 120)
pdf.set_line_width(0.4)
pdf.line(18, pdf.get_y(), 90, pdf.get_y())
pdf.line(108, pdf.get_y(), 192, pdf.get_y())
pdf.ln(2)
pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(100, 100, 100)
pdf.cell(72, 5, "Responsavel Tecnico: Savio Mendes", align="C")
pdf.set_x(108)
pdf.cell(84, 5, "Cliente / Contratante", align="C")
pdf.ln(4)
pdf.cell(72, 5, TODAY, align="C")
pdf.set_x(108)
pdf.cell(84, 5, "Data: ___/___/______", align="C")

pdf.output(OUT_PATH)
print(f"PDF gerado: {OUT_PATH}")
