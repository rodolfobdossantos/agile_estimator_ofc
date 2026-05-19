"""
Gera docs/documentacao_tecnica_agile_estimator_v2.pdf
Documentacao tecnica completa cobrindo os Marcos 1-5.
"""
from fpdf import FPDF

TODAY = "11/05/2026"
OUT  = "docs/documentacao_tecnica_agile_estimator_v2.pdf"
BLUE  = (25,  55, 115)
DBLUE = (10,  30,  80)
GRAY  = (90,  90,  90)
LGRAY = (245, 245, 245)
WHITE = (255, 255, 255)
GREEN = (20, 110, 50)


class Doc(FPDF):
    # -- cabeçalho / rodapé ------------------------------------------
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 6, "Agile Estimator v2  |  Documentacao Tecnica Detalhada", align="L")
        self.set_draw_color(210, 210, 210)
        self.line(10, 15, 200, 15)
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-13)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 6, f"Pagina {self.page_no()}  |  Gerado em {TODAY}", align="C")

    # -- primitivas --------------------------------------------------
    def _reset_x(self):
        self.set_x(self.l_margin)

    def sec(self, title, subtitle=None):
        """Titulo de secao principal."""
        self.ln(3)
        self.set_fill_color(230, 238, 255)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*BLUE)
        self.cell(0, 9, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*BLUE)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_line_width(0.2)
        if subtitle:
            self.ln(1)
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(*GRAY)
            self._reset_x()
            self.multi_cell(190, 5, subtitle)
        self.ln(2)
        self._text()

    def sub(self, title):
        """Subtitulo."""
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*BLUE)
        self._reset_x()
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self._text()

    def sub2(self, title):
        """Sub-subtitulo."""
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DBLUE)
        self._reset_x()
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self._text()

    def _text(self):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(35, 35, 35)

    def p(self, text):
        """Paragrafo."""
        self._text()
        self._reset_x()
        self.multi_cell(190, 5.5, text)

    def li(self, text, indent=6):
        """Item de lista."""
        self._text()
        self.set_x(10 + indent)
        self.cell(5, 5.5, "-")
        self.multi_cell(185 - indent, 5.5, text)
        self._reset_x()

    def kv(self, key, val):
        """Linha key: value inline."""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DBLUE)
        self._reset_x()
        self.cell(55, 6, key + ":", align="R")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(35, 35, 35)
        self.cell(0, 6, "  " + val, new_x="LMARGIN", new_y="NEXT")

    def tbl(self, headers, rows, widths, row_height=6):
        """Tabela formatada."""
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*BLUE)
        self.set_text_color(*WHITE)
        self.set_draw_color(160, 175, 210)
        self.set_line_width(0.2)
        self._reset_x()
        for h, w in zip(headers, widths):
            self.cell(w, 7, h, border=1, fill=True)
        self.ln()
        self._text()
        for i, row in enumerate(rows):
            self.set_fill_color(243, 247, 255) if i % 2 == 0 else self.set_fill_color(*WHITE)
            self.set_text_color(30, 30, 30)
            self._reset_x()
            for val, w in zip(row, widths):
                self.cell(w, row_height, str(val), border=1, fill=True)
            self.ln()
        self.ln(2)

    def code(self, text):
        """Bloco de codigo."""
        lines = text.strip().split("\n")
        h = len(lines) * 5 + 6
        self._reset_x()
        self.set_fill_color(*LGRAY)
        self.set_draw_color(205, 205, 205)
        self.rect(10, self.get_y(), 190, h, style="FD")
        self.set_y(self.get_y() + 3)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(20, 20, 20)
        for line in lines:
            self.set_x(14)
            self.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self._text()

    def badge(self, text, color=GREEN):
        """Badge de status."""
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*[min(c + 170, 255) for c in color])
        self.set_text_color(*color)
        self._reset_x()
        self.cell(30, 6, f"  {text}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self._text()

    def marco_header(self, num, title, dates, status="ENTREGUE"):
        """Cabecalho padronizado de marco."""
        self.ln(2)
        self.set_fill_color(220, 230, 250)
        self.set_draw_color(*BLUE)
        self.set_line_width(0.4)
        y0 = self.get_y()
        self.rect(10, y0, 190, 20, style="FD")
        self.set_xy(13, y0 + 2)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*DBLUE)
        self.cell(0, 6, f"Marco {num}  -  {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_x(13)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GRAY)
        self.cell(100, 5, f"Data de entrega: {dates}")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*GREEN)
        self.cell(0, 5, f"Status: {status}", new_x="LMARGIN", new_y="NEXT")
        self.set_line_width(0.2)
        self.ln(4)
        self._text()


# ====================================================================
doc = Doc()
doc.set_auto_page_break(auto=True, margin=15)

# -- CAPA ------------------------------------------------------------
doc.add_page()
doc.set_y(40)
doc.set_font("Helvetica", "B", 30)
doc.set_text_color(*BLUE)
doc.cell(0, 14, "Agile Estimator v2", align="C", new_x="LMARGIN", new_y="NEXT")
doc.set_font("Helvetica", "B", 16)
doc.set_text_color(*GRAY)
doc.cell(0, 9, "Documentacao Tecnica Detalhada", align="C", new_x="LMARGIN", new_y="NEXT")
doc.ln(4)
doc.set_draw_color(*BLUE)
doc.set_line_width(1.0)
doc.line(35, doc.get_y(), 175, doc.get_y())
doc.set_line_width(0.2)
doc.ln(10)
doc.set_font("Helvetica", "", 11)
doc.set_text_color(45, 45, 45)
meta = [
    ("Versao", "2.0"),
    ("Responsavel tecnico", "Savio Mendes"),
    ("Data do documento", TODAY),
    ("Repositorio", "rodolfobdossantos/agile_estimator_ofc (GitHub)"),
    ("API em producao", "https://agile-estimator-ofc.onrender.com"),
]
for k, v in meta:
    doc.set_font("Helvetica", "B", 11)
    doc.cell(60, 7, k + ":", align="R")
    doc.set_font("Helvetica", "", 11)
    doc.cell(0, 7, "  " + v, new_x="LMARGIN", new_y="NEXT")
doc.ln(12)
doc.set_fill_color(235, 242, 255)
doc.set_draw_color(170, 195, 240)
box_y = doc.get_y()
doc.rect(25, box_y, 160, 50, style="FD")
doc.set_xy(30, box_y + 5)
doc.set_font("Helvetica", "B", 11)
doc.set_text_color(*DBLUE)
doc.cell(0, 6, "Marcos cobertos por este documento", new_x="LMARGIN", new_y="NEXT")
marcos = [
    ("Marco 1", "Engenharia de Dados", "14/03/2026"),
    ("Marco 2", "Modelagem de Machine Learning", "26/03/2026"),
    ("Marco 3", "Servico de Previsao (API)", "06/04/2026"),
    ("Marco 4", "Infraestrutura e Deploy", "16/04/2026"),
    ("Marco 5", "Integracao Streamlit + Documentacao Tecnica", "Fase 2"),
]
doc.set_font("Helvetica", "", 10)
doc.set_text_color(35, 35, 35)
for num, title, date in marcos:
    doc.set_x(30)
    doc.set_font("Helvetica", "B", 10)
    doc.cell(20, 5.5, num + ":")
    doc.set_font("Helvetica", "", 10)
    doc.cell(110, 5.5, title)
    doc.cell(0, 5.5, date, new_x="LMARGIN", new_y="NEXT")

# -- VISAO GERAL -----------------------------------------------------
doc.add_page()
doc.sec("Visao Geral do Sistema")
doc.p(
    "O Agile Estimator v2 e uma ferramenta de estimativa de esforco de desenvolvimento "
    "de software baseada em Machine Learning. O sistema prediz o esforco total de um "
    "projeto em horas-pessoa, com base em metricas de tamanho funcional (Function Points) "
    "e fatores de complexidade tecnica."
)
doc.ln(2)
doc.sub("Arquitetura Geral")
doc.code(
    "+----------------------------------------------------------+\n"
    "|              USUARIO (Browser)                           |\n"
    "|         Streamlit App  (streamlit_app/app.py)            |\n"
    "|                                                          |\n"
    "|  1. Entrada: Manual / CSV / Trello                       |\n"
    "|  2. Preprocessamento client-side (StandardScaler + PCA)  |\n"
    "|  3. POST /predict  {function_points_std, PC1, PC2}       |\n"
    "+------------------+---------------------------------------+\n"
    "                   |  HTTPS\n"
    "                   v\n"
    "+----------------------------------------------------------+\n"
    "|           FastAPI  (api/)  -  Render.com                 |\n"
    "|    https://agile-estimator-ofc.onrender.com              |\n"
    "|                                                          |\n"
    "|  POST /predict  ->  model.predict(X)  ->  np.exp()        |\n"
    "|  GET  /health   ->  3 verificacoes automaticas            |\n"
    "|  GET  /docs     ->  Swagger UI                            |\n"
    "+------------------+---------------------------------------+\n"
    "                   |\n"
    "        +----------+----------+\n"
    "        |  Artefatos (api/)   |\n"
    "        |  agile_estimator_v2.pkl        (Lasso Reg.)      |\n"
    "        |  pca_2.pkl                     (PCA n=2)         |\n"
    "        |  scaler_pca_features.pkl       (StandardScaler)  |\n"
    "        |  scaler_maxx.pkl               (fp scaler)       |\n"
    "        +------------------------------------------------+"
)
doc.sub("Stack Tecnologico")
doc.tbl(
    ["Camada", "Tecnologia", "Versao Minima", "Uso"],
    [
        ["Modelagem",      "scikit-learn",  ">= 1.3",  "Lasso, StandardScaler, PCA, GridSearchCV"],
        ["Rastreamento",   "MLflow",         ">= 2.0",  "Versionamento de experimentos e modelos"],
        ["API",            "FastAPI",        ">= 0.100","REST API com validacao Pydantic"],
        ["API Server",     "uvicorn",        ">= 0.22", "ASGI server para FastAPI"],
        ["Interface",      "Streamlit",      ">= 1.30", "Interface web interativa"],
        ["Visualizacao",   "Altair",         ">= 5.0",  "Graficos declarativos no Streamlit"],
        ["Dados",          "pandas",         ">= 2.0",  "Manipulacao de DataFrames"],
        ["Numerica",       "numpy",          ">= 1.25", "Operacoes matriciais e log/exp"],
        ["Serializacao",   "joblib",         ">= 1.3",  "Persistencia de artefatos .pkl"],
        ["HTTP Client",    "requests",       ">= 2.31", "Streamlit -> API e Trello API"],
        ["Infraestrutura", "Docker",         "3.11",    "Containerizacao da API"],
        ["Deploy",         "Render.com",     "-",       "Hosting com HTTPS e auto-deploy"],
    ],
    [28, 28, 28, 106],
)

# ====================================================================
# MARCO 1
# ====================================================================
doc.add_page()
doc.marco_header(1, "Engenharia de Dados", "14/03/2026")

doc.sub("1.1  Fonte de Dados")
doc.p(
    "O sistema foi treinado com o dataset Maxwell, coletado por K.D. Maxwell "
    "(\"Applied Statistics for Software Managers\", 2002). O dataset contem projetos "
    "reais de desenvolvimento de software em empresas de telecomunicacoes."
)
doc.p(
    "O repositorio contem dados brutos de quatro datasets publicos de benchmark "
    "de esforco em software (pasta model/data/raw/):"
)
doc.tbl(
    ["Dataset", "Arquivo", "Projetos", "Uso no v2"],
    [
        ["Maxwell",    "maxx.csv",                          "62",   "Dataset de treino (unico)"],
        ["China",      "china.csv",                         "499",  "Explorado na EDA; nao usado no modelo final"],
        ["Desharnais", "desh.csv",                          "81",   "Explorado na EDA; nao usado no modelo final"],
        ["NASA93",     "nasa93.csv",                        "93",   "Explorado na EDA; nao usado no modelo final"],
        ["ISBSG",      "EBSPM_Research_Repository_v07072017.csv", "varios", "Explorado; nao usado no modelo final"],
    ],
    [28, 72, 22, 68],
)
doc.p(
    "A escolha do Maxwell como unico dataset de treino foi motivada pela "
    "consistencia das variaveis disponiveis: tamanho funcional (Function Points / AFP) "
    "e fatores de ajuste tecnico (TCA) em escala Likert, diretamente alinhados "
    "com a abordagem IFPUG de estimativa."
)

doc.sub("1.2  Colunas do Dataset Maxwell e Mapeamento")
doc.tbl(
    ["Coluna Original", "Nome Canonico", "Tipo", "Descricao"],
    [
        ["Size",   "function_points",             "Continua", "Adjusted Function Points (AFP) - tamanho funcional"],
        ["Effort", "effort_hours",                "Continua", "Esforco total em horas-pessoa (variavel-alvo)"],
        ["T03",    "performance_requirements",    "Likert 1-5","Exigencia de desempenho e velocidade"],
        ["T09",    "complex_processing",          "Likert 1-5","Complexidade tecnica do processamento"],
        ["T11",    "installation_ease",           "Likert 1-5","Facilidade de instalacao e deploy (5=muito facil)"],
        ["T15",    "additional_complexity_factor","Likert 1-5","Fatores adicionais de complexidade"],
    ],
    [28, 55, 26, 81],
)

doc.sub("1.3  Pipeline de Limpeza e Pre-processamento")

doc.sub2("1.3.1  Remocao de Outliers (IQR)")
doc.p(
    "Outliers na variavel-alvo effort_hours foram removidos pelo metodo Tukey (IQR):"
)
doc.code(
    "Q3  = df['effort_hours'].quantile(0.75)\n"
    "IQR = df['effort_hours'].quantile(0.75) - df['effort_hours'].quantile(0.25)\n"
    "df  = df[df['effort_hours'] <= Q3 + 1.5 * IQR]\n"
    "# Resultado: 62 projetos originais -> 57 projetos apos limpeza"
)
doc.tbl(
    ["Metrica", "Valor"],
    [
        ["Projetos originais",          "62"],
        ["Projetos apos limpeza",       "57"],
        ["Outliers removidos",          "5"],
        ["effort_hours minimo",         "583 horas"],
        ["effort_hours maximo (apos)",  "18.500 horas"],
        ["Mediana",                     "4.557 horas"],
        ["Media",                       "5.653 horas"],
    ],
    [80, 110],
)

doc.sub2("1.3.2  Transformacao da Variavel-Alvo")
doc.p(
    "A variavel effort_hours foi transformada com logaritmo natural para "
    "normalizar a distribuicao assimetrica e estabilizar a variancia:"
)
doc.code(
    "y = np.log(df['effort_hours'])  # log-transform\n"
    "# Na inferencia, a API desfaz a transformacao:\n"
    "effort_hours_previsto = np.exp(model.predict(X)[0])"
)

doc.sub2("1.3.3  Padronizacao dos 4 Fatores Likert")
doc.p(
    "Os 4 fatores de complexidade tecnica (T03, T09, T11, T15) foram padronizados "
    "com StandardScaler antes da aplicacao do PCA. "
    "O scaler foi fitado nos 57 projetos Maxwell e salvo como artefato de producao:"
)
doc.code(
    "from sklearn.preprocessing import StandardScaler\n"
    "scaler = StandardScaler()\n"
    "X_scaled = scaler.fit_transform(df[['performance_requirements',\n"
    "                                    'complex_processing',\n"
    "                                    'installation_ease',\n"
    "                                    'additional_complexity_factor']])\n"
    "joblib.dump(scaler, 'api/artifacts/preprocessing/scaler_pca_features.pkl')"
)
doc.tbl(
    ["Feature", "Mean (media)", "Scale (desvio padrao)"],
    [
        ["performance_requirements",    "3.0000", "0.8983"],
        ["complex_processing",          "4.0351", "0.7484"],
        ["installation_ease",           "3.3158", "0.9395"],
        ["additional_complexity_factor","3.2982", "0.7484"],
    ],
    [90, 55, 55],
)

doc.sub2("1.3.4  Reducao de Dimensionalidade - PCA")
doc.p(
    "PCA com 2 componentes foi aplicado sobre os 4 fatores Likert padronizados. "
    "Os 2 componentes explicam ~70,6% da variancia total:"
)
doc.tbl(
    ["Componente", "Variancia Explicada", "Interpretacao", "Principais Cargas"],
    [
        ["PC1", "44,37%", "Complexidade tecnica geral",
         "complex_processing(0.61), add_complexity(0.55), install_ease(0.50)"],
        ["PC2", "26,25%", "Tradeoff performance vs. instalacao",
         "perf_requirements(0.81), install_ease(-0.51), complex_processing(-0.15)"],
    ],
    [24, 30, 52, 84],
)
doc.code(
    "from sklearn.decomposition import PCA\n"
    "pca = PCA(n_components=2)\n"
    "pca.fit(X_scaled)\n"
    "# explained_variance_ratio_: [0.4437, 0.2625]  => 70.62% total\n"
    "joblib.dump(pca, 'api/artifacts/preprocessing/pca_2.pkl')"
)

doc.sub2("1.3.5  Padronizacao de function_points")
doc.p(
    "O campo function_points (Size/AFP) foi padronizado separadamente. "
    "O dataset processado ja contem function_points padronizado, portanto a inferencia "
    "deve aplicar a mesma transformacao antes de enviar a API:"
)
doc.code(
    "# Parametros extraidos de scaler_maxx.pkl (indice 0 = function_points)\n"
    "fp_mean  = 514.8596   # media nos 57 projetos Maxwell\n"
    "fp_scale = 516.2373   # desvio padrao\n"
    "\n"
    "fp_std = (function_points_raw - fp_mean) / fp_scale"
)

doc.sub("1.4  Dataset Processado")
doc.p("O dataset final (model/data/raw/maxx_processed.csv) contem 57 linhas e 14 colunas:")
doc.li("function_points  - padronizado")
doc.li("effort_hours     - log(esforco original)")
doc.li("customer_participation, logical_complexity, requirements_volatility, "
       "requirements_quality, productivity_factors, installation_ease, "
       "team_technical_capability, individual_skill  - outros fatores Maxwell padronizados")
doc.li("PC1, PC2, PC3, PC4  - componentes PCA (somente PC1 e PC2 entram no modelo)")

doc.sub("1.5  Artefatos Gerados (Marco 1)")
doc.tbl(
    ["Artefato", "Caminho", "Descricao"],
    [
        ["scaler_pca_features.pkl", "api/artifacts/preprocessing/", "StandardScaler fitado nos 4 fatores Likert"],
        ["pca_2.pkl",               "api/artifacts/preprocessing/", "PCA n=2 fitado nos 4 fatores padronizados"],
        ["scaler_maxx.pkl",         "api/artifacts/preprocessing/", "Scaler Maxwell; indice 0 = function_points"],
        ["maxx_processed.csv",      "model/data/raw/",              "Dataset limpo e transformado, 57 x 14"],
    ],
    [55, 60, 75],
)

# ====================================================================
# MARCO 2
# ====================================================================
doc.add_page()
doc.marco_header(2, "Modelagem de Machine Learning", "26/03/2026")

doc.sub("2.1  Selecao de Features")
doc.p(
    "Apos analise de correlacao de Pearson (|r| > 0.20 com effort_hours) e reducao "
    "por PCA, foram selecionadas 3 features para o modelo final:"
)
doc.tbl(
    ["Feature", "Origem", "Descricao"],
    [
        ["function_points", "Maxwell - coluna Size",      "Tamanho funcional (AFP) - padronizado"],
        ["PC1",             "PCA sobre T03,T09,T11,T15",  "Complexidade tecnica geral (~44% variancia)"],
        ["PC2",             "PCA sobre T03,T09,T11,T15",  "Tradeoff performance vs. instalacao (~26% variancia)"],
    ],
    [38, 52, 100],
)
doc.p(
    "As demais colunas do dataset processado (customer_participation, logical_complexity, "
    "etc.) sao artefatos de um pipeline exploratório anterior e nao entram no modelo."
)

doc.sub("2.2  Algoritmos Avaliados")
doc.tbl(
    ["Algoritmo", "Regularizacao", "Grid de Hiperparametros", "Observacao"],
    [
        ["Ridge",            "L2", "alpha: [0.01, 0.1, 1, 10]",                         "Baseline linear regularizado"],
        ["Lasso",            "L1", "alpha: [0.001, 0.01, 0.1, 1]",                      "Selecao implicita de features"],
        ["SVR",              "-",  "C: [0.1,1,10], gamma: [scale,auto]",                "Pipeline com StandardScaler adicional"],
        ["RandomForest",     "-",  "n_estimators: [100,200,300], max_depth: varios",    "Ensemble; risco de overfitting com n=57"],
        ["GradientBoosting", "-",  "n_estimators: [100,200,300,400], lr: [0.05..0.3]", "Boosting sequencial"],
    ],
    [32, 16, 62, 80],
)

doc.sub("2.3  Estrategia de Validacao Cruzada")
doc.p(
    "Com apenas 57 observacoes, uma unica divisao treino/teste produziria estimativas "
    "instáveis. Foi utilizado RepeatedKFold para maximizar a estabilidade da avaliacao:"
)
doc.code(
    "from sklearn.model_selection import RepeatedKFold, GridSearchCV\n"
    "\n"
    "cv = RepeatedKFold(n_splits=5, n_repeats=10, random_state=42)\n"
    "# => 50 avaliações independentes por modelo\n"
    "# => cada fold: 80% treino (45 projetos) / 20% teste (12 projetos)\n"
    "\n"
    "grid = GridSearchCV(\n"
    "    pipeline, param_grid, cv=cv,\n"
    "    scoring='neg_root_mean_squared_error',\n"
    "    n_jobs=-1\n"
    ")"
)

doc.sub("2.4  Resultados Comparativos (holdout 20%)")
doc.tbl(
    ["Modelo", "MAE (h)", "RMSE (h)", "R2", "MAPE (%)", "Posicao"],
    [
        ["Lasso",            "1.616", "1.877", "0.378", "48.9%", "1 - SELECIONADO"],
        ["RandomForest",     "1.914", "2.213", "0.136", "44.2%", "2"],
        ["Ridge",            "1.879", "2.214", "0.136", "52.7%", "3"],
        ["GradientBoosting", "1.962", "2.261", "0.099", "43.3%", "4"],
        ["SVR",              "2.810", "3.589", "-1.27", "70.0%", "5"],
    ],
    [38, 22, 22, 18, 22, 68],
)
doc.p(
    "O Lasso foi selecionado por apresentar o menor RMSE absoluto no holdout, "
    "o melhor R2 (0.378) e o menor MAE. O MAPE de 48.9% e caracteristico de "
    "estimativas de esforco em software - a variabilidade intrinseca dos projetos "
    "impoe um limite superior de precisao mesmo com modelos sofisticados."
)

doc.sub("2.5  Modelo Selecionado - Lasso")
doc.tbl(
    ["Atributo", "Valor"],
    [
        ["Algoritmo",                  "sklearn.linear_model.Lasso"],
        ["Alpha (melhor)",             "0.1 (selecionado por GridSearchCV)"],
        ["Coeficiente - function_points", "0.3409"],
        ["Coeficiente - PC1",          "0.1666"],
        ["Coeficiente - PC2",          "-0.2723"],
        ["Intercept",                  "8.3585  =>  exp(8.3585) = 4.254 horas (media Maxwell)"],
        ["Target de treino",           "log(effort_hours)"],
        ["Predicao final",             "np.exp(model.predict(X)[0])  =>  horas-pessoa"],
    ],
    [65, 125],
)
doc.p(
    "Interpretacao dos coeficientes:\n"
    "- function_points (+0.341): aumento de 1 desvio-padrao no AFP => exp(0.341) = 1.41x mais esforco\n"
    "- PC1 (+0.167): maior complexidade tecnica geral => mais esforco\n"
    "- PC2 (-0.272): PC2 captura contraste performance vs. facilidade de instalacao"
)

doc.sub("2.6  Rastreamento com MLflow")
doc.p(
    "Todos os experimentos foram rastreados com MLflow em model/experiments/mlruns/. "
    "Para cada algoritmo foram registrados: hiperparametros do GridSearchCV, "
    "metricas no holdout (MAE, RMSE, R2, MAPE_percent) e o artefato .pkl do "
    "best_estimator_."
)
doc.code(
    "import mlflow, mlflow.sklearn\n"
    "\n"
    "mlflow.set_tracking_uri('file:model/experiments/mlruns')\n"
    "mlflow.set_experiment('agile_estimator_modeling')\n"
    "\n"
    "with mlflow.start_run(run_name=name):\n"
    "    grid.fit(X_train, y_train)\n"
    "    best_model = grid.best_estimator_   # modelo com alpha=0.1 correto\n"
    "    mlflow.log_params(grid.best_params_)\n"
    "    mlflow.log_metric('RMSE', rmse)\n"
    "    mlflow.sklearn.log_model(best_model, name)"
)
doc.p(
    "ATENCAO: o notebook foi corrigido para usar grid.best_estimator_ ao salvar o "
    "artefato final. O bug original re-fazia o fit com alpha=1.0 (padrao sklearn), "
    "zerando todos os coeficientes Lasso."
)

doc.sub("2.7  Interpretabilidade com SHAP")
doc.p(
    "Foi utilizado SHAP (SHapley Additive exPlanations) para interpretar as "
    "contribuicoes de cada feature no conjunto de teste. O grafico de barras "
    "mostra a importância media absoluta de cada feature; o summary plot mostra "
    "a direcao do efeito (valores altos vs. baixos de cada feature)."
)
doc.code(
    "import shap\n"
    "explainer    = shap.Explainer(best_model.predict, X_train)\n"
    "shap_values  = explainer(X_test)\n"
    "shap.plots.bar(shap_values)        # importancia media\n"
    "shap.summary_plot(shap_values, X_test)  # direcao do efeito"
)

doc.sub("2.8  Artefatos Gerados (Marco 2)")
doc.tbl(
    ["Artefato", "Caminho", "Descricao"],
    [
        ["agile_estimator_v2.pkl", "api/artifacts/model/",        "Pipeline Lasso - alpha=0.1, coef=[0.341, 0.167, -0.272]"],
        ["agile_estimator_v2.pkl", "model/artifacts/model/",      "Copia para o repositorio de modelagem"],
        ["features.json",          "api/artifacts/metadata/",     "Metadados do modelo: features, pipeline, metricas"],
        ["mlruns/",                "model/experiments/mlruns/",   "Experimentos MLflow com todos os runs e modelos"],
        ["modelagem-ml.ipynb",     "model/notebooks/treino/agile_v2/", "Notebook de treino documentado"],
    ],
    [50, 55, 85],
)

# ====================================================================
# MARCO 3
# ====================================================================
doc.add_page()
doc.marco_header(3, "Servico de Previsao (API)", "06/04/2026")

doc.sub("3.1  Estrutura do Projeto API")
doc.code(
    "api/\n"
    "+-- app/\n"
    "|   +-- main.py           # FastAPI app, CORS, rotas /predict e /health\n"
    "|   +-- predict.py        # Logica de inferencia e selecao de features\n"
    "|   +-- model_loader.py   # Carrega o .pkl mais recente de artifacts/model/\n"
    "|   +-- feature_loader.py # Le features.json para selecao dinamica de features\n"
    "|   +-- schemas.py        # Pydantic: PredictionInput (function_points, PC1, PC2)\n"
    "|   +-- logger.py         # Logger estruturado (formato ISO 8601)\n"
    "+-- artifacts/\n"
    "    +-- model/\n"
    "    |   +-- agile_estimator_v2.pkl\n"
    "    +-- preprocessing/\n"
    "    |   +-- pca_2.pkl\n"
    "    |   +-- scaler_pca_features.pkl\n"
    "    |   +-- scaler_maxx.pkl\n"
    "    +-- metadata/\n"
    "        +-- features.json"
)

doc.sub("3.2  Endpoints")
doc.tbl(
    ["Endpoint", "Metodo", "Descricao", "Autenticacao"],
    [
        ["POST /predict", "POST", "Inferencia - retorna esforco em horas-pessoa", "Nenhuma"],
        ["GET  /health",  "GET",  "Health check com 3 verificacoes automaticas",  "Nenhuma"],
        ["GET  /docs",    "GET",  "Swagger UI gerado automaticamente pelo FastAPI","Nenhuma"],
    ],
    [38, 20, 102, 30],
)

doc.sub("3.3  Schema de Entrada e Saida")
doc.code(
    "# Entrada (Pydantic - schemas.py)\n"
    "class PredictionInput(BaseModel):\n"
    "    function_points: float  # ja padronizado: (fp_raw - 514.86) / 516.24\n"
    "    PC1: float              # 1a componente PCA dos 4 fatores Likert\n"
    "    PC2: float              # 2a componente PCA dos 4 fatores Likert\n"
    "\n"
    "# Saida\n"
    '# {"prediction": 4982.3}   # horas-pessoa (ja transformado com np.exp())\n'
    "\n"
    "# Exemplo de chamada:\n"
    "curl -X POST https://agile-estimator-ofc.onrender.com/predict \\\n"
    '     -H "Content-Type: application/json" \\\n'
    "     -d '{\"function_points\": -0.029, \"PC1\": 0.52, \"PC2\": -0.31}'"
)

doc.sub("3.4  Fluxo de Inferencia (predict.py)")
doc.code(
    "def make_prediction(model, data: PredictionInput) -> float:\n"
    "    features = ['function_points', 'PC1', 'PC2']\n"
    "    df = pd.DataFrame([data.dict()])[features]\n"
    "    prediction = model.predict(df)       # retorna log(effort_hours)\n"
    "    return float(np.exp(prediction[0]))  # desfaz o log => horas-pessoa"
)

doc.sub("3.5  Carregamento Dinamico do Modelo (model_loader.py)")
doc.p(
    "O model_loader carrega automaticamente o arquivo .pkl mais recente da pasta "
    "artifacts/model/. Isso permite substituir o modelo sem alterar codigo:"
)
doc.code(
    "def get_latest_model():\n"
    "    files  = [f for f in os.listdir(MODEL_DIR) if f.endswith('.pkl')]\n"
    "    latest = max(files, key=lambda x: os.path.getctime(...))\n"
    "    return os.path.join(MODEL_DIR, latest)\n"
    "\n"
    "model = load_model()  # carregado no startup do FastAPI"
)

doc.sub("3.6  Endpoint de Health Check (GET /health)")
doc.p("O health check executa 3 verificacoes a cada chamada:")
doc.tbl(
    ["Verificacao", "O que checa", "Campo na resposta"],
    [
        ["1. Modelo em memoria",  "model is not None",                            "model_loaded: bool"],
        ["2. Arquivo no disco",   "os.path.exists(model_path)",                   "model_file_exists: bool"],
        ["3. Inferencia de sanidade", "predict([[1, 0.0, 0.0]]) sem excecao",    "inference_ok: bool"],
        ["4. Tempo de resposta",  "Tempo total do health check",                  "response_time_ms: float"],
    ],
    [45, 85, 60],
)
doc.code(
    '# Resposta esperada quando tudo ok:\n'
    '{\n'
    '  "status": "ok",\n'
    '  "checks": {\n'
    '    "model_loaded": true,\n'
    '    "model_file_exists": true,\n'
    '    "inference_ok": true,\n'
    '    "test_prediction": 8.358,\n'
    '    "response_time_ms": 12.4\n'
    '  }\n'
    '}'
)

doc.sub("3.7  Logging")
doc.p(
    "Logs estruturados via modulo logger.py usando o modulo padrao logging do Python:"
)
doc.code(
    "# Formato: YYYY-MM-DD HH:MM:SS,mmm - LEVEL - mensagem\n"
    "# Exemplo de saida:\n"
    "2026-05-11 14:32:01,123 - INFO  - Prediction: 4982.3\n"
    "2026-05-11 14:32:15,456 - ERROR - Error: Connection timeout"
)

doc.sub("3.8  Dependencias da API (requirements.txt)")
doc.code(
    "fastapi\n"
    "uvicorn[standard]\n"
    "pandas\n"
    "scikit-learn\n"
    "joblib\n"
    "mlflow"
)

# ====================================================================
# MARCO 4
# ====================================================================
doc.add_page()
doc.marco_header(4, "Infraestrutura e Deploy", "16/04/2026")

doc.sub("4.1  Containerizacao com Docker")
doc.p(
    "A API foi containerizada usando Docker com imagem base python:3.11-slim, "
    "garantindo reproducibilidade e portabilidade entre ambientes."
)
doc.sub2("Dockerfile")
doc.code(
    "FROM python:3.11-slim\n"
    "\n"
    "# Evita criacao de .pyc e bufferiza logs em tempo real\n"
    "ENV PYTHONDONTWRITEBYTECODE=1\n"
    "ENV PYTHONUNBUFFERED=1\n"
    "\n"
    "WORKDIR /app\n"
    "\n"
    "# Copia requirements primeiro (aproveita cache de camadas Docker)\n"
    "COPY requirements.txt .\n"
    "RUN pip install --no-cache-dir -r requirements.txt\n"
    "\n"
    "COPY . .\n"
    "\n"
    "EXPOSE 8000\n"
    "\n"
    "# Porta configuravel via variavel de ambiente $PORT (necessario no Render)\n"
    'CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]'
)

doc.sub2("docker-compose.yml (reinicio automatico em falha)")
doc.code(
    'version: "3.9"\n'
    "\n"
    "services:\n"
    "  api:\n"
    "    build: .\n"
    "    container_name: agile_api\n"
    "    ports:\n"
    '      - "8000:10000"\n'
    "    volumes:\n"
    "      - .:/app\n"
    "    restart: always    # reinicia automaticamente em caso de falha"
)
doc.p(
    "A diretiva 'restart: always' garante que o container seja reiniciado "
    "automaticamente em caso de crash ou reinicializacao do sistema operacional, "
    "sem intervencao manual."
)

doc.sub("4.2  Deploy em Producao - Render.com")
doc.tbl(
    ["Atributo", "Detalhe"],
    [
        ["Plataforma",        "Render.com (Web Service)"],
        ["URL",               "https://agile-estimator-ofc.onrender.com"],
        ["HTTPS",             "Certificado SSL automatico (Let's Encrypt)"],
        ["Deploy trigger",    "Push para branch main no GitHub (auto-deploy)"],
        ["Reinicio",          "Automatico em caso de crash (Docker restart: always)"],
        ["Cold start",        "~30s apos 15min de inatividade (plano gratuito)"],
        ["Mitigacao cold start", "GET /health antes de calcular estimativas"],
    ],
    [55, 135],
)

doc.sub("4.3  Fluxo de Deploy")
doc.p(
    "1. Desenvolvedor faz push para branch main no GitHub\n"
    "2. Render detecta o push via webhook\n"
    "3. Render faz docker build com o Dockerfile da pasta api/\n"
    "4. Container e iniciado com o novo artefato .pkl\n"
    "5. Render realiza health check automatico\n"
    "6. Trafego e redirecionado para o novo container (zero downtime deploy)"
)

doc.sub("4.4  Rodar Localmente com Docker")
doc.code(
    "# Construir e iniciar\n"
    "cd api\n"
    "docker-compose up --build\n"
    "\n"
    "# Testar\n"
    "curl http://localhost:8000/health\n"
    'curl -X POST http://localhost:8000/predict \\\n'
    '     -H "Content-Type: application/json" \\\n'
    "     -d '{\"function_points\": -0.029, \"PC1\": 0.52, \"PC2\": -0.31}'\n"
    "\n"
    "# Swagger UI\n"
    "# Abrir: http://localhost:8000/docs"
)

doc.sub("4.5  Rodar Localmente sem Docker")
doc.code(
    "cd api\n"
    "pip install -r requirements.txt\n"
    "uvicorn app.main:app --reload --port 8000\n"
    "# Acesse: http://localhost:8000/docs"
)

# ====================================================================
# MARCO 5
# ====================================================================
doc.add_page()
doc.marco_header(5, "Integracao Streamlit e Documentacao Tecnica", "Fase 2")

doc.sub("5.1  Adequacao da Interface para Consumir a API")
doc.p(
    "A interface Streamlit foi reescrita para nao executar nenhum modelo localmente. "
    "Todo processamento de inferencia ocorre exclusivamente na API REST hospedada "
    "no Render.com. O Streamlit e responsavel apenas pelo pre-processamento client-side "
    "das features brutas antes de enviar o payload a API."
)

doc.sub2("Pipeline Completo de Inferencia (client-side)")
doc.code(
    "# 1. Coleta de inputs (Manual / CSV / Trello)\n"
    "row = {'function_points': 500, 'performance_requirements': 3,\n"
    "       'complex_processing': 4, 'installation_ease': 3,\n"
    "       'additional_complexity_factor': 3}\n"
    "\n"
    "# 2. Padronizar function_points  (scaler_maxx.pkl, indice 0)\n"
    "#    FP_MEAN=514.8596, FP_SCALE=516.2373 (carregados no startup)\n"
    "fp_std = (row['function_points'] - FP_MEAN) / FP_SCALE\n"
    "\n"
    "# 3. Padronizar 4 fatores Likert  (scaler_pca_features.pkl)\n"
    "X = pd.DataFrame([row])[BUSINESS_FEATURES].astype(float)\n"
    "X_scaled = scaler.transform(X)\n"
    "\n"
    "# 4. Reducao de dimensionalidade  (pca_2.pkl)\n"
    "pcs = pca.transform(X_scaled)[0]\n"
    "PC1, PC2 = float(pcs[0]), float(pcs[1])\n"
    "\n"
    "# 5. POST /predict\n"
    'payload  = {"function_points": fp_std, "PC1": PC1, "PC2": PC2}\n'
    "resp     = requests.post(API_URL, json=payload, timeout=30)\n"
    "effort_h = float(resp.json()['prediction'])  # horas-pessoa"
)

doc.sub("5.2  Estrutura do Projeto Streamlit")
doc.code(
    "streamlit_app/\n"
    "+-- app.py                          # Aplicacao principal (600+ linhas)\n"
    "+-- scripts_app/\n"
    "    +-- get_public_trello_board.py  # Importador de boards publicos Trello"
)

doc.sub("5.3  Carregamento de Artefatos no Startup")
doc.code(
    "@st.cache_resource\n"
    "def load_artifacts():\n"
    "    # scaler_pca_features: 4 fatores Likert\n"
    "    scaler    = joblib.load('api/artifacts/preprocessing/scaler_pca_features.pkl')\n"
    "    pca       = joblib.load('api/artifacts/preprocessing/pca_2.pkl')\n"
    "    # scaler_maxx[0]: mean e scale de function_points\n"
    "    scaler_fp = joblib.load('api/artifacts/preprocessing/scaler_maxx.pkl')\n"
    "    fp_mean   = float(scaler_fp.mean_[0])   # 514.8596\n"
    "    fp_scale  = float(scaler_fp.scale_[0])  # 516.2373\n"
    "    return scaler, pca, fp_mean, fp_scale\n"
    "\n"
    "scaler, pca, FP_MEAN, FP_SCALE = load_artifacts()\n"
    "# @st.cache_resource => carregado 1 vez, reutilizado em todos os reruns"
)

doc.sub("5.4  Modos de Entrada de Dados")
doc.tbl(
    ["Modo", "Aba", "Descricao"],
    [
        ["Tutorial",      "Aba 1", "Explica o modelo, inputs, outputs, escala Likert e limitacoes"],
        ["Input Manual",  "Aba 2", "Formulario com 5 campos; validacao Likert 1-5; acumula projetos"],
        ["Upload CSV",    "Aba 3", "Importacao em lote; preview 10 linhas; botao de confirmacao"],
        ["Trello",        "Aba 4", "Importa de board publico via URL; sem autenticacao"],
    ],
    [30, 20, 140],
)

doc.sub("5.5  Calculadora IFPUG Embutida")
doc.p(
    "Disponivel como expander na aba Input Manual. Calcula Adjusted Function Points "
    "com os pesos padrao IFPUG:"
)
doc.tbl(
    ["Tipo de Funcao", "Simples", "Media", "Complexa"],
    [
        ["EI - External Input",          "3", "4",  "6"],
        ["EO - External Output",         "4", "5",  "7"],
        ["EQ - External Query",          "3", "4",  "6"],
        ["ILF - Internal Logical File",  "7", "10", "15"],
        ["EIF - External Interface File","5", "7",  "10"],
    ],
    [90, 25, 25, 60],
)
doc.code(
    "UFP = sum(quantidade_simples * peso_simples + ... para cada tipo)\n"
    "VAF = 0.65 + 0.01 * TDI   # TDI = soma dos 14 fatores de influencia (0-70)\n"
    "AFP = UFP * VAF            # ou AFP = UFP se VAF nao aplicado\n"
    "# Botao 'Usar este valor' transfere AFP diretamente para o campo Function Points"
)

doc.sub("5.6  Integracao com Trello (boards publicos)")
doc.p(
    "A integracao foi implementada em scripts_app/get_public_trello_board.py "
    "e permite importar projetos diretamente de boards Trello sem autenticacao:"
)
doc.code(
    "def get_trello_cards_public(url: str) -> pd.DataFrame:\n"
    "    board_id = re.match(r'https://trello.com/b/([a-zA-Z0-9]+)', url).group(1)\n"
    "    data = requests.get(f'https://trello.com/b/{board_id}.json').json()\n"
    "\n"
    "    # Mapeia field_id -> nome canonico (case-insensitive, com aliases)\n"
    "    field_map = {cf['id']: _resolve_field_name(cf['name'])\n"
    "                 for cf in data['customFields']}\n"
    "\n"
    "    # Extrai .value.number de cada customFieldItem por cartao\n"
    "    rows = [{'project_id': card['name'],\n"
    "             **{canonical: float(item['value']['number'])\n"
    "                for item in card['customFieldItems']\n"
    "                if (canonical := field_map.get(item['idCustomField']))}}\n"
    "            for card in data['cards'] if not card['closed']]\n"
    "\n"
    "    return pd.DataFrame(rows)   # project_id + 5 colunas de features"
)
doc.p("Aliases aceitos para nomes de campos (tolerancia a erros ortograficos):")
doc.tbl(
    ["Campo Canonico", "Aliases Aceitos"],
    [
        ["function_points",             "function_points, function points"],
        ["performance_requirements",    "performance_requirements, performance requirements"],
        ["complex_processing",          "complex_processing, complex processing"],
        ["installation_ease",           "installation_ease, instalation_ease, instalation ease, installation ease"],
        ["additional_complexity_factor","additional_complexity_factor, aditional_complexity_factor, aditional complexity factor"],
    ],
    [60, 130],
)

doc.sub("5.7  Secao de Resultados")
doc.tbl(
    ["Aba de Resultado", "Conteudo"],
    [
        ["Dados",          "Tabela com project_id e os 5 campos de entrada; contagem de projetos"],
        ["Estimativas",    "Botao 'Calcular'; tabela com horas, dias (h/8), semanas (dias/5); barra visual; download CSV"],
        ["Visualizacoes",  "Histograma do esforco; scatter FP x esforco; scatter complexidade x esforco; bar chart comparativo"],
    ],
    [35, 155],
)

doc.sub("5.8  Bugs Corrigidos Durante o Marco 5")
doc.tbl(
    ["Bug", "Causa Raiz", "Correcao"],
    [
        ["Predicoes identicas (~3981h) para todos os projetos",
         "Notebook de treino re-fitava o Lasso com alpha=1.0 (padrao sklearn), zerando coef",
         "Artefato substituido pelo modelo MLflow correto (alpha=0.1); notebook corrigido para usar grid.best_estimator_"],
        ["function_points sem efeito na predicao",
         "CSV de treino tem fp padronizado, mas app enviava fp raw para API (coef interpretado na escala errada)",
         "Adicionado (fp-514.86)/516.24 em preprocess_for_api() usando scaler_maxx.pkl[0]"],
        ["'Adicionar Projeto' nao adicionava projetos",
         "Ausencia de st.rerun() apos append no session_state; pagina nao refrescava",
         "Adicionado st.toast() + st.rerun() no callback do botao"],
        ["Importacao Trello sobreescrevia dados manuais a cada rerun",
         "O fetch rodava em todo rerun do Streamlit (fora de callback de botao)",
         "Fetch movido para callback do botao 'Buscar projetos do Trello'; preview antes de confirmar"],
        ["Upload CSV sobreescrevia dados a cada rerun",
         "Mesmo padrao: escrita fora de callback",
         "Adicionado botao 'Carregar este CSV' com preview de 10 linhas antes de confirmar"],
        ["Botoes 'Limpar dados' nao funcionavam",
         "Faltava st.rerun() apos limpeza do session_state",
         "Adicionado st.rerun() nos callbacks de limpeza"],
    ],
    [52, 68, 70],
    row_height=12,
)

# ====================================================================
# PROCESSO DE RETREINO
# ====================================================================
doc.add_page()
doc.sec("Processo de Re-treino Manual")
doc.p(
    "O re-treino e um processo manual executado pelo tecnico responsavel. "
    "Nao requer interrupcao da API em producao durante a execucao dos notebooks - "
    "apenas no momento do deploy do novo artefato."
)

doc.tbl(
    ["Passo", "Acao", "Arquivo / Ferramenta"],
    [
        ["1", "Atualizar dados brutos com novos projetos (se houver)",
         "model/data/raw/maxx.csv"],
        ["2", "Re-executar EDA: correlacoes, outliers, PCA",
         "model/notebooks/inferencia/agile_v2/eda.ipynb"],
        ["3", "Salvar artefatos de preprocessamento atualizados",
         "api/artifacts/preprocessing/scaler_pca_features.pkl, pca_2.pkl"],
        ["4", "Re-executar notebook de treino (GridSearchCV + MLflow)",
         "model/notebooks/treino/agile_v2/modelagem-ml.ipynb"],
        ["5", "Verificar coeficientes: nao-zero, alpha=0.1",
         "joblib.load('api/artifacts/model/agile_estimator_v2.pkl').steps[-1][1].coef_"],
        ["6", "Copiar artefato para api/artifacts/model/ e model/artifacts/model/",
         "Automatico via notebook (shutil.copy2)"],
        ["7", "git commit + git push para branch main",
         "Git / GitHub"],
        ["8", "Render refaz o deploy automaticamente (~2 min)",
         "Render.com (webhook GitHub)"],
        ["9", "Verificar health check em producao",
         "GET /health"],
    ],
    [10, 105, 75],
)

doc.sub("Script de Verificacao Pos-Retreino")
doc.code(
    "import joblib, numpy as np\n"
    "\n"
    "model = joblib.load('api/artifacts/model/agile_estimator_v2.pkl')\n"
    "lasso = model.steps[-1][1]\n"
    "\n"
    "print('Alpha:', lasso.alpha)          # deve ser < 1.0\n"
    "print('Coeficientes:', lasso.coef_)   # NENHUM deve ser exatamente 0.0\n"
    "print('Intercept:', lasso.intercept_) # esperado ~8.0-9.0\n"
    "\n"
    "# Teste de sanidade: projetos diferentes -> predicoes diferentes\n"
    "import pandas as pd\n"
    "p1 = model.predict(pd.DataFrame([{'function_points': -1.0, 'PC1': 0.0, 'PC2': 0.0}]))\n"
    "p2 = model.predict(pd.DataFrame([{'function_points':  1.0, 'PC1': 1.0, 'PC2': 0.0}]))\n"
    "assert p1[0] != p2[0], 'ERRO: modelo retorna mesma predicao para inputs diferentes'\n"
    "print('Predicao projeto pequeno:', np.exp(p1[0]), 'h')\n"
    "print('Predicao projeto grande: ', np.exp(p2[0]), 'h')"
)

# ====================================================================
# INSTRUCOES DE OPERACAO + INVENTARIO
# ====================================================================
doc.add_page()
doc.sec("Instrucoes de Operacao")

doc.sub("Acessar o Sistema em Producao")
doc.tbl(
    ["Recurso", "URL"],
    [
        ["Interface Streamlit",  "Disponivel via Streamlit Cloud ou instancia propria"],
        ["API REST",             "https://agile-estimator-ofc.onrender.com/predict"],
        ["Health Check",         "https://agile-estimator-ofc.onrender.com/health"],
        ["Swagger UI",           "https://agile-estimator-ofc.onrender.com/docs"],
        ["Board Trello demo",    "https://trello.com/b/DKf6KNh2/testeagileestimator"],
    ],
    [45, 145],
)

doc.sub("Usar a Interface Streamlit")
for i, step in enumerate([
    "Acesse o Tutorial (aba Ícone de livro) para entender os campos e a escala Likert.",
    "Escolha o modo de entrada: Input Manual, Upload CSV ou Capturar do Trello.",
    "Para Input Manual: preencha os 5 campos e clique em 'Adicionar Projeto'. Repita para cada projeto.",
    "Para CSV: faca upload do arquivo, visualize o preview e confirme clicando em 'Carregar este CSV'.",
    "Para Trello: cole a URL do board publico, clique 'Buscar projetos do Trello', confirme com 'Carregar estes projetos'.",
    "Na secao de resultados, clique em 'Calcular Esforco Total Estimado'.",
    "Visualize os resultados (Estimativas) e os graficos (Visualizacoes).",
    "Clique em 'Baixar resultados (CSV)' para exportar.",
], 1):
    doc.set_font("Helvetica", "B", 10)
    doc.set_text_color(*BLUE)
    doc.cell(8, 6, f"{i}.")
    doc.set_font("Helvetica", "", 10)
    doc.set_text_color(35, 35, 35)
    doc.multi_cell(182, 5.5, step)
    doc.ln(1)
    doc._reset_x()

doc.sub("Formato do CSV de Entrada")
doc.code(
    "# Colunas obrigatorias (project_id e opcional):\n"
    "project_id,function_points,performance_requirements,complex_processing,installation_ease,additional_complexity_factor\n"
    "projeto_alpha,450,3,4,3,3\n"
    "projeto_beta,800,4,5,2,4\n"
    "projeto_gamma,220,2,2,5,1"
)

doc.sub("Campos Customizados no Trello")
doc.p(
    "Cada cartao do board Trello deve ter campos customizados (Custom Fields) "
    "com os nomes abaixo (o sistema aceita variacoes ortograficas):"
)
doc.li("Function Points  (ou 'function_points')")
doc.li("Performance Requirements  (ou 'performance_requirements')")
doc.li("Complex Processing  (ou 'complex_processing')")
doc.li("Installation Ease  (ou 'installation_ease', 'instalation_ease')")
doc.li("Additional Complexity Factor  (ou 'aditional_complexity_factor')")
doc.p("Todos os campos devem ser do tipo Numero no Trello.")

doc.sub("Observacoes Importantes")
doc.li(
    "Cold start da API: a primeira requisicao apos 15 min de inatividade leva ~30s. "
    "Chamar GET /health antes de calcular estimativas aquece a instancia."
)
doc.li(
    "O modelo estima o esforco do PROJETO INTEIRO (nao por sprint ou por tarefa). "
    "Valores tipicos no dataset Maxwell: 583h (min) a 18.500h (max), mediana 4.557h."
)
doc.li(
    "Installation Ease: escala invertida. Valor 5 = muito facil de instalar "
    "(menor esforco nessa dimensao); valor 1 = muito dificil."
)
doc.li(
    "MAPE de ~49%: use as estimativas como baseline para comparacao relativa "
    "entre projetos, nao como compromisso contratual absoluto."
)

doc.sec("Inventario Completo de Artefatos")
doc.tbl(
    ["Artefato", "Caminho no Repositorio", "Descricao"],
    [
        ["agile_estimator_v2.pkl", "api/artifacts/model/",             "Lasso Pipeline - alpha=0.1, coef=[0.341,0.167,-0.272]"],
        ["agile_estimator_v2.pkl", "model/artifacts/model/",           "Copia para repositorio de modelagem"],
        ["pca_2.pkl",              "api/artifacts/preprocessing/",     "PCA n=2 - 70.6% variancia explicada"],
        ["scaler_pca_features.pkl","api/artifacts/preprocessing/",     "StandardScaler fitado nos 4 fatores Likert (57 projetos)"],
        ["scaler_maxx.pkl",        "api/artifacts/preprocessing/",     "Scaler Maxwell 9 features; indice 0=function_points"],
        ["features.json",          "api/artifacts/metadata/",          "Metadados: features, pipeline, metricas, dataset"],
        ["maxx_processed.csv",     "model/data/raw/",                  "Dataset limpo e transformado (57x14)"],
        ["modelagem-ml.ipynb",     "model/notebooks/treino/agile_v2/", "Notebook treino com GridSearchCV e MLflow"],
        ["eda.ipynb",              "model/notebooks/inferencia/agile_v2/", "EDA: correlacoes, outliers, PCA, selecao de features"],
        ["data_modelling.ipynb",   "model/notebooks/inferencia/agile_v2/", "Analise exploratoria de datasets benchmark"],
        ["app.py",                 "streamlit_app/",                   "Interface Streamlit - 4 modos entrada, 3 abas resultado"],
        ["get_public_trello_board.py", "streamlit_app/scripts_app/",   "Importador Trello com alias de campos"],
        ["main.py",                "api/app/",                         "FastAPI: rotas /predict, /health"],
        ["predict.py",             "api/app/",                         "Logica de inferencia"],
        ["model_loader.py",        "api/app/",                         "Carregamento dinamico do .pkl mais recente"],
        ["schemas.py",             "api/app/",                         "Pydantic: PredictionInput"],
        ["Dockerfile",             "api/",                             "python:3.11-slim; porta via $PORT"],
        ["docker-compose.yml",     "api/",                             "restart: always para reinicio automatico"],
        ["TECHNICAL_DOCUMENTATION.md", "docs/",                       "Este documento em formato Markdown"],
        ["BUSINESS_DOCUMENTATION.md",  "docs/",                       "Documentacao de negocio e proposta comercial"],
    ],
    [52, 60, 78],
    row_height=6,
)

doc.output(OUT)
print(f"PDF gerado: {OUT}")
