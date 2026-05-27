import streamlit as st
import pandas as pd
import numpy as np
import joblib
import altair as alt
import requests
import re
import os
import math
from scripts_app.get_public_trello_board import get_trello_cards_public, REQUIRED_COLUMNS

# ---------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------
st.set_page_config(page_title="Agile Estimator v2", layout="wide")

# ---------------------------------------------------------------
# CSS — dark-theme tooltip
# ---------------------------------------------------------------
st.markdown("""
    <style>
    [data-testid="stTooltipIcon"] {
        color: #FFD700 !important;
        font-size: 18px !important;
        opacity: 0.9;
    }
    div[data-baseweb="tooltip"] {
        background-color: #222 !important;
        color: #FFF !important;
        border: 1px solid #FFD700;
        font-size: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Load preprocessing artifacts (cached across reruns)
# ---------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREP_DIR = os.path.join(BASE_DIR, "..", "api", "artifacts", "preprocessing")

@st.cache_resource
def load_artifacts():
    # scaler_pca_features.pkl: StandardScaler for the 4 Maxwell Likert factors
    # scaler_maxx.pkl: 9-feature Maxwell scaler; index 0 is function_points (mean=514.86, scale=516.24)
    # The processed CSV already has standardized function_points, so inference must match that transform
    scaler    = joblib.load(os.path.join(PREP_DIR, "scaler_pca_features.pkl"))
    pca       = joblib.load(os.path.join(PREP_DIR, "pca_2.pkl"))
    scaler_fp = joblib.load(os.path.join(PREP_DIR, "scaler_maxx.pkl"))
    fp_mean   = float(scaler_fp.mean_[0])
    fp_scale  = float(scaler_fp.scale_[0])
    return scaler, pca, fp_mean, fp_scale

scaler, pca, FP_MEAN, FP_SCALE = load_artifacts()

# ---------------------------------------------------------------
# Constants
# ---------------------------------------------------------------
API_URL = "https://agile-estimator-ofc.onrender.com/predict"

BUSINESS_FEATURES = [
    "performance_requirements",
    "complex_processing",
    "installation_ease",
    "additional_complexity_factor",
]

FEATURE_LABELS = {
    "function_points":             "Function Points",
    "performance_requirements":    "Performance Requirements",
    "complex_processing":          "Complex Processing",
    "installation_ease":           "Installation Ease",
    "additional_complexity_factor":"Additional Complexity Factor",
}

# ---------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------

def preprocess_for_api(row: dict) -> dict:
    """Scale + PCA the 4 business features; standardize function_points; return API payload."""
    X = pd.DataFrame([row])[BUSINESS_FEATURES].astype(float)
    X_scaled = scaler.transform(X)
    pcs = pca.transform(X_scaled)[0]
    # function_points was standardized in the training CSV — inference must match that transform
    fp_std = (float(row["function_points"]) - FP_MEAN) / FP_SCALE
    return {
        "function_points": fp_std,
        "PC1": float(pcs[0]),
        "PC2": float(pcs[1]),
    }


def call_predict_api(payload: dict) -> float:
    """POST to Render API; return effort_hours (already exp-transformed)."""
    resp = requests.post(API_URL, json=payload, timeout=60)
    resp.raise_for_status()
    return float(resp.json()["prediction"])


def estimate_batch(df: pd.DataFrame) -> pd.DataFrame:
    """Run inference for all rows; add effort_hours_previsto column."""
    results = []
    errors  = []
    for _, row in df.iterrows():
        try:
            payload = preprocess_for_api(row.to_dict())
            results.append(call_predict_api(payload))
        except Exception as e:
            results.append(None)
            errors.append(str(e))
    df = df.copy()
    df["effort_hours_previsto"] = results
    df["dias_estimados"]  = df["effort_hours_previsto"].apply(
        lambda x: math.ceil(x / 8) if x else None
    )
    df["semanas_estimadas"] = df["dias_estimados"].apply(
        lambda x: math.ceil(x / 5) if x else None
    )
    return df, errors


def validate_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in REQUIRED_COLUMNS if c not in df.columns]

# ---------------------------------------------------------------
# Page header
# ---------------------------------------------------------------
st.title("🚀 Agile Estimator v2")
st.write("Estimativa de **esforço total de desenvolvimento** de projetos de software, baseada em IA.")

# ---------------------------------------------------------------
# Input tabs
# ---------------------------------------------------------------
tab_tutorial, tab_input, tab_csv, tab_trello = st.tabs([
    "📖 Tutorial", "✏️ Input Manual", "📂 Upload CSV", "🔗 Capturar do Trello"
])

# ===========================
# TUTORIAL
# ===========================
with tab_tutorial:
    st.title("📖 Como usar o Agile Estimator v2")
    st.markdown("""
    O **Agile Estimator v2** usa um modelo de Machine Learning treinado em dados reais de
    projetos de software para estimar o **esforço total em horas-pessoa** necessário para
    desenvolver um projeto do início ao fim.

    ---
    """)

    st.subheader("🧠 Sobre o modelo")
    st.markdown("""
    O modelo foi treinado no dataset **Maxwell** (62 projetos reais de telecomunicações),
    usando **Regressão Lasso** com validação cruzada repetida (RepeatedKFold).

    - **Variável-alvo:** `effort_hours` — esforço total do projeto em horas-pessoa
    - **Algoritmo:** Lasso (melhor RMSE entre Ridge, Lasso, SVR, RandomForest, GradientBoosting)
    - **MAPE médio:** ~49 % — útil como estimativa de baseline e comparação entre projetos
    - **Redução de dimensionalidade:** PCA aplicado sobre 4 fatores de complexidade (explicando ~70 % da variância)

    ---
    """)

    st.subheader("📥 Inputs necessários")
    st.markdown("""
    Você deve fornecer **5 valores** por projeto:

    | Campo | Tipo | Descrição |
    |-------|------|-----------|
    | **Function Points** | Número livre | Tamanho funcional do software em Adjusted Function Points (AFP). Quanto maior, mais esforço esperado. |
    | **Performance Requirements** | **Escala 1–5** | Quão exigente é o sistema em termos de desempenho e velocidade. |
    | **Complex Processing** | **Escala 1–5** | Grau de complexidade do processamento técnico (algoritmos, cálculos, lógica de negócio). |
    | **Installation Ease** | **Escala 1–5** | Facilidade de instalação e deploy. **Atenção: 5 = muito fácil, 1 = muito difícil**. |
    | **Additional Complexity Factor** | **Escala 1–5** | Fatores adicionais de complexidade fora do escopo padrão. |

    **Escala Likert (campos 2–5):**

    | Valor | Significado |
    |-------|-------------|
    | 1 | Muito Baixo |
    | 2 | Baixo |
    | 3 | Médio |
    | 4 | Alto |
    | 5 | Muito Alto |

    > 💡 **Dica:** Os 4 fatores de escala são transformados internamente por PCA (redução de dimensionalidade), que captura os padrões de complexidade do dataset Maxwell sem precisar de ajuste manual.

    ---
    """)

    st.subheader("📊 Outputs")
    st.markdown("""
    Para cada projeto, o sistema retorna:

    | Coluna | Descrição |
    |--------|-----------|
    | **Esforço Previsto (h)** | Total de horas-pessoa estimado para desenvolver o projeto |
    | **Dias Estimados** | Conversão: horas ÷ 8 (jornada diária), arredondado para cima |
    | **Semanas Estimadas** | Conversão: dias ÷ 5 (semana útil), arredondado para cima |

    ---
    """)

    st.subheader("⚠️ Limitações")
    st.info("""
    - O dataset de treino tem **62 projetos** — estimativas têm incerteza considerável (~49% MAPE).
    - O modelo é mais confiável para **comparar projetos entre si** do que para prever esforço absoluto.
    - Projetos muito fora do perfil de telecomunicações do dataset Maxwell podem ter estimativas menos precisas.
    """)

    st.subheader("🔄 Fluxo de uso")
    st.markdown("""
    1. Insira os dados do projeto (manual, CSV ou Trello).
    2. Clique em **Calcular Esforço Total Estimado**.
    3. Visualize os resultados e baixe o CSV.
    4. Use a aba **Visualizações** para comparar projetos.
    """)

# ===========================
# INPUT MANUAL
# ===========================
with tab_input:
    st.subheader("✏️ Inserir dados do projeto manualmente")

    if "input_user" not in st.session_state:
        st.session_state.input_user = {
            "project_id": "projeto_001",
            "function_points": 300.0,
            "performance_requirements": 3.0,
            "complex_processing": 4.0,
            "installation_ease": 3.0,
            "additional_complexity_factor": 3.0,
        }

    col1, col2 = st.columns(2)

    with col1:
        project_id = st.text_input(
            "🆔 ID do Projeto",
            value=st.session_state.input_user["project_id"],
            help="Identificador único do projeto (ex: projeto_alpha)"
        )
        if not project_id.strip():
            project_id = f"projeto_{np.random.randint(100, 999)}"

        function_points = st.number_input(
            "📐 Function Points",
            min_value=0.0,
            value=float(st.session_state.input_user["function_points"]),
            step=10.0,
            help="Tamanho funcional do software em Adjusted Function Points"
        )

        performance_requirements = st.number_input(
            "⚡ Performance Requirements (1–5)",
            min_value=1.0,
            max_value=5.0,
            value=float(st.session_state.input_user["performance_requirements"]),
            step=0.5,
            help="Escala Likert 1–5: exigência de desempenho/velocidade do sistema. 1=Muito Baixa, 5=Muito Alta."
        )

    with col2:
        complex_processing = st.number_input(
            "⚙️ Complex Processing (1–5)",
            min_value=1.0,
            max_value=5.0,
            value=float(st.session_state.input_user["complex_processing"]),
            step=0.5,
            help="Escala Likert 1–5: grau de complexidade do processamento técnico. 1=Muito Baixo, 5=Muito Alto."
        )

        installation_ease = st.number_input(
            "🚀 Installation Ease (1–5)",
            min_value=1.0,
            max_value=5.0,
            value=float(st.session_state.input_user["installation_ease"]),
            step=0.5,
            help="Escala Likert 1–5: facilidade de instalação/deploy. 1=Muito Difícil, 5=Muito Fácil. Atenção: maior valor = MENOS esforço neste campo."
        )

        additional_complexity_factor = st.number_input(
            "🔧 Additional Complexity Factor (1–5)",
            min_value=1.0,
            max_value=5.0,
            value=float(st.session_state.input_user["additional_complexity_factor"]),
            step=0.5,
            help="Escala Likert 1–5: fatores adicionais de complexidade fora do escopo padrão. 1=Muito Baixo, 5=Muito Alto."
        )

    st.session_state.input_user = {
        "project_id": project_id,
        "function_points": function_points,
        "performance_requirements": performance_requirements,
        "complex_processing": complex_processing,
        "installation_ease": installation_ease,
        "additional_complexity_factor": additional_complexity_factor,
    }

    _, col_btn1, col_btn2, _ = st.columns([1, 1, 1, 1])

    with col_btn1:
        if st.button("✅ Adicionar Projeto", use_container_width=True):
            new_row = pd.DataFrame([st.session_state.input_user])
            for col in REQUIRED_COLUMNS + ["function_points"]:
                if col in new_row.columns:
                    new_row[col] = pd.to_numeric(new_row[col], errors="coerce")

            existing = st.session_state.get("data")
            if existing is not None:
                st.session_state.data = pd.concat([existing, new_row], ignore_index=True)
            else:
                st.session_state.data = new_row.copy()

            st.session_state.last_source = "manual"
            st.toast("Projeto adicionado com sucesso!", icon="✅")
            st.rerun()

    with col_btn2:
        if st.button("🔄 Resetar formulário", use_container_width=True):
            st.session_state.input_user = {
                "project_id": "projeto_001",
                "function_points": 300.0,
                "performance_requirements": 3.0,
                "complex_processing": 4.0,
                "installation_ease": 3.0,
                "additional_complexity_factor": 3.0,
            }
            st.session_state.data = None
            st.toast("Formulário e dados resetados.", icon="🧹")
            st.rerun()

    st.markdown("---")
    with st.expander("🧮 Calculadora IFPUG de Function Points", expanded=False):
        st.markdown("""
        Use esta calculadora para obter os **Adjusted Function Points (AFP)** do seu projeto
        com base no método **IFPUG** — o mesmo padrão usado no dataset Maxwell.

        Conte quantas funções de cada tipo existem no projeto, separadas por complexidade (**Simples / Média / Complexa**):
        """)

        # IFPUG weights table
        IFPUG_WEIGHTS = {
            "EI — External Input":          (3, 4, 6),
            "EO — External Output":         (4, 5, 7),
            "EQ — External Query":          (3, 4, 6),
            "ILF — Internal Logical File":  (7, 10, 15),
            "EIF — External Interface File":(5, 7, 10),
        }

        fp_col_labels, fp_col_s, fp_col_m, fp_col_c = st.columns([3, 1, 1, 1])
        fp_col_labels.markdown("**Tipo**")
        fp_col_s.markdown("**Simples**")
        fp_col_m.markdown("**Média**")
        fp_col_c.markdown("**Complexa**")

        fp_counts: dict[str, tuple] = {}
        for func_type, (ws, wm, wc) in IFPUG_WEIGHTS.items():
            c0, c1, c2, c3 = st.columns([3, 1, 1, 1])
            c0.markdown(f"{func_type}  \n*(pesos: {ws} / {wm} / {wc})*")
            n_s = c1.number_input(f"S_{func_type}", min_value=0, value=0, step=1, label_visibility="collapsed", key=f"fp_s_{func_type}")
            n_m = c2.number_input(f"M_{func_type}", min_value=0, value=0, step=1, label_visibility="collapsed", key=f"fp_m_{func_type}")
            n_c = c3.number_input(f"C_{func_type}", min_value=0, value=0, step=1, label_visibility="collapsed", key=f"fp_c_{func_type}")
            fp_counts[func_type] = (n_s, n_m, n_c)

        ufp = sum(
            n_s * ws + n_m * wm + n_c * wc
            for (func_type, (ws, wm, wc)), (n_s, n_m, n_c) in zip(IFPUG_WEIGHTS.items(), fp_counts.values())
        )

        st.markdown("---")
        st.markdown(f"**UFP (Unadjusted Function Points): `{ufp}`**")

        use_vaf = st.checkbox("Aplicar ajuste VAF (Value Adjustment Factor)?", value=False,
                              help="O VAF ajusta o UFP com base em 14 características técnicas gerais, cada uma de 0 a 5.")
        if use_vaf:
            tdi = st.slider(
                "TDI — Total Degree of Influence (soma das 14 características, 0–70)",
                min_value=0, max_value=70, value=35,
                help="Soma dos 14 Fatores de Influência Técnica Geral do IFPUG (cada um de 0 a 5)."
            )
            vaf = 0.65 + 0.01 * tdi
            afp = round(ufp * vaf, 1)
            st.markdown(f"VAF = 0.65 + 0.01 × {tdi} = **{vaf:.2f}**")
            st.success(f"AFP (Adjusted Function Points) = UFP × VAF = **{ufp} × {vaf:.2f} = {afp}**")
            fp_result = afp
        else:
            fp_result = float(ufp)
            if ufp > 0:
                st.info(f"AFP = UFP = **{ufp}** (sem ajuste VAF)")

        if ufp > 0:
            if st.button("📋 Usar este valor como Function Points", key="use_fp_calc"):
                st.session_state.input_user["function_points"] = fp_result
                st.success(f"✅ Function Points definido para **{fp_result}**. Ajuste os demais campos e clique em *Adicionar Projeto*.")
                st.rerun()

# ===========================
# UPLOAD CSV
# ===========================
with tab_csv:
    st.subheader("📂 Carregar projetos via CSV")
    st.markdown("""
    O CSV deve conter as colunas abaixo (coluna `project_id` é opcional):

    ```
    project_id, function_points, performance_requirements, complex_processing, installation_ease, additional_complexity_factor
    ```
    """)

    uploaded_file = st.file_uploader("Selecione o arquivo CSV", type="csv")

    if uploaded_file is not None:
        df_csv = pd.read_csv(uploaded_file)
        missing = validate_columns(df_csv)

        if missing:
            st.error(f"❌ Colunas obrigatórias ausentes: {', '.join(missing)}")
        else:
            if "project_id" not in df_csv.columns:
                df_csv.insert(0, "project_id", [f"projeto_{i+1}" for i in range(len(df_csv))])

            st.dataframe(df_csv.head(10), use_container_width=True)
            st.caption(f"{len(df_csv)} projeto(s) encontrado(s) no arquivo.")

            if st.button("📥 Carregar este CSV", use_container_width=False):
                st.session_state.data = df_csv.copy()
                st.session_state.last_source = "csv"
                st.toast(f"{len(df_csv)} projeto(s) carregado(s)!", icon="✅")
                st.rerun()
    else:
        st.info("📁 Nenhum CSV carregado ainda.")

# ===========================
# TRELLO
# ===========================
with tab_trello:
    st.subheader("🔗 Importar projetos do Trello")
    st.markdown("""
    Cole o link de um board **público** do Trello. Os cartões devem conter campos customizados com os nomes:
    `Function Points`, `Performance Requirements`, `Complex Processing`, `Installation Ease`, `Additional Complexity Factor`.
    """)

    trello_url = st.text_input(
        "URL do board",
        placeholder="https://trello.com/b/DKf6KNh2/testeagileestimator"
    )

    trello_regex = r"^https://trello\.com/b/[a-zA-Z0-9]+(/[a-zA-Z0-9_-]+)?$"

    if trello_url:
        if not re.match(trello_regex, trello_url):
            st.error("❌ Link inválido. Use o formato: `https://trello.com/b/<board_id>`")
        else:
            if st.button("🔍 Buscar projetos do Trello", use_container_width=False):
                with st.spinner("Buscando dados do Trello..."):
                    try:
                        df_trello = get_trello_cards_public(trello_url)
                        missing = validate_columns(df_trello)

                        if missing:
                            st.warning(
                                f"⚠️ Campos não encontrados nos cartões: {', '.join(missing)}. "
                                "Verifique os nomes dos custom fields no board."
                            )
                        elif df_trello.dropna(subset=REQUIRED_COLUMNS).empty:
                            st.warning("⚠️ Nenhum cartão com todos os campos preenchidos foi encontrado.")
                        else:
                            df_trello = df_trello.dropna(subset=REQUIRED_COLUMNS).reset_index(drop=True)
                            st.session_state.trello_preview = df_trello.copy()
                    except Exception as e:
                        st.error(f"❌ Erro ao buscar dados do Trello: {e}")
                        st.session_state.pop("trello_preview", None)

            if "trello_preview" in st.session_state:
                df_preview = st.session_state.trello_preview
                st.dataframe(df_preview.head(10), use_container_width=True)
                st.caption(f"{len(df_preview)} projeto(s) encontrado(s) no board.")
                if st.button("📥 Carregar estes projetos", use_container_width=False):
                    st.session_state.data = df_preview.copy()
                    st.session_state.last_source = "trello"
                    st.session_state.pop("trello_preview", None)
                    st.toast(f"{len(df_preview)} projeto(s) importado(s) do Trello!", icon="✅")
                    st.rerun()

# ---------------------------------------------------------------
# Data status bar
# ---------------------------------------------------------------
st.markdown("---")

if st.session_state.get("data") is not None:
    col_status, col_clear = st.columns([4, 1])
    with col_status:
        source = st.session_state.get("last_source", "?").upper()
        n = len(st.session_state.data)
        st.info(f"📂 **{n} projeto(s)** carregado(s) — origem: **{source}**")
    with col_clear:
        if st.button("🗑️ Limpar dados", use_container_width=True):
            st.session_state.data = None
            st.session_state.last_source = None
            st.rerun()

# ---------------------------------------------------------------
# Results section
# ---------------------------------------------------------------
if "data" in st.session_state and st.session_state.data is not None and not st.session_state.data.empty:

    res_tab1, res_tab2, res_tab3 = st.tabs(["📋 Dados", "📈 Estimativas", "📊 Visualizações"])

    # -------------------------
    # TAB 1 — DADOS
    # -------------------------
    with res_tab1:
        st.subheader("📋 Projetos carregados")
        display_cols = [c for c in ["project_id"] + REQUIRED_COLUMNS
                        if c in st.session_state.data.columns]
        st.dataframe(
            st.session_state.data[display_cols].head(100),
            use_container_width=True
        )
        st.caption(f"Total de projetos: **{len(st.session_state.data)}**")

    # -------------------------
    # TAB 2 — ESTIMATIVAS
    # -------------------------
    with res_tab2:
        st.subheader("⚡ Calcular Esforço Total Estimado")

        if st.button("🚀 Calcular Esforço Total Estimado", key="calc_esforco"):
            missing = validate_columns(st.session_state.data)
            if missing:
                st.error(f"❌ Colunas faltando: {', '.join(missing)}")
            else:
                with st.spinner("Calculando estimativas via API..."):
                    try:
                        result_df, errors = estimate_batch(st.session_state.data)
                        st.session_state.data = result_df

                        if errors:
                            msg = errors[0]
                            cold_start = "timed out" in msg.lower() or "Read timed out" in msg
                            dica = (" A API pode estar em cold start (plano gratuito Render — aguarde ~30s e tente novamente)." if cold_start else "")
                            st.warning(f"⚠️ {len(errors)} erro(s) durante a inferência: {msg}{dica}")

                        valid = result_df["effort_hours_previsto"].notna().sum()
                        st.success(f"✅ Estimativas calculadas para {valid} projeto(s)!")
                    except Exception as e:
                        st.exception(e)

        if "effort_hours_previsto" in st.session_state.data.columns:
            data = st.session_state.data

            preview_cols = ["project_id", "effort_hours_previsto", "dias_estimados", "semanas_estimadas"]
            preview = data[[c for c in preview_cols if c in data.columns]].copy()

            max_h = preview["effort_hours_previsto"].max()
            if pd.notna(max_h) and max_h > 0:
                preview["Escala"] = preview["effort_hours_previsto"].apply(
                    lambda x: "█" * int((x / max_h) * 20) if pd.notna(x) else ""
                )

            valid_count = preview["effort_hours_previsto"].notna().sum()
            if valid_count == 0:
                st.warning("⚠️ Nenhuma estimativa disponível. Tente novamente — a API pode estar aquecendo (cold start ~30s).")
            else:
                st.markdown("### 📈 Resultados")
                fmt = {"effort_hours_previsto": lambda x: f"{x:.0f} h" if pd.notna(x) else "-"}
                st.dataframe(
                    preview.style.format(fmt),
                    use_container_width=True
                )

                st.markdown("""
                #### ℹ️ O que cada coluna significa

                | Coluna | Descrição |
                |--------|-----------|
                | **Esforço Previsto (h)** | Total de horas-pessoa estimado para desenvolver o projeto completo |
                | **Dias Estimados** | Horas ÷ 8 horas/dia útil, arredondado para cima |
                | **Semanas Estimadas** | Dias ÷ 5 dias úteis/semana, arredondado para cima |
                | **Escala** | Comparação visual relativa entre projetos |

                > ⚠️ O esforço estimado representa o **projeto inteiro**, não uma sprint individual.
                """)

                csv_bytes = data[[c for c in preview_cols if c in data.columns]].to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Baixar resultados (CSV)",
                    data=csv_bytes,
                    file_name="estimativas_esforco.csv",
                    mime="text/csv"
                )

    # -------------------------
    # TAB 3 — VISUALIZAÇÕES
    # -------------------------
    with res_tab3:
        if "effort_hours_previsto" not in st.session_state.data.columns:
            st.warning("⚠️ Calcule as estimativas primeiro na aba **Estimativas**.")
        else:
            data = st.session_state.data.dropna(subset=["effort_hours_previsto"]).copy()

            if data.empty:
                st.warning("⚠️ Nenhum resultado disponível para visualização.")
            else:
                st.subheader("📊 Distribuição do Esforço Estimado")
                st.caption("Distribuição do esforço total previsto entre os projetos analisados.")

                hist = alt.Chart(data).mark_bar().encode(
                    x=alt.X("effort_hours_previsto:Q",
                            bin=alt.Bin(maxbins=20),
                            title="Esforço Previsto (horas)"),
                    y=alt.Y("count()", title="Nº de Projetos"),
                    tooltip=["count()"]
                ).properties(height=350)
                st.altair_chart(hist, use_container_width=True)

                st.markdown("---")
                st.subheader("📐 Function Points × Esforço Previsto")
                st.caption("Quanto maior o tamanho funcional, maior tende a ser o esforço. Verifique se a relação faz sentido para seus projetos.")

                scatter_fp = alt.Chart(data).mark_circle(size=80, opacity=0.8).encode(
                    x=alt.X("function_points:Q", title="Function Points"),
                    y=alt.Y("effort_hours_previsto:Q", title="Esforço Previsto (h)"),
                    tooltip=[
                        alt.Tooltip("project_id:N", title="Projeto"),
                        alt.Tooltip("function_points:Q", title="Function Points"),
                        alt.Tooltip("effort_hours_previsto:Q", title="Esforço (h)", format=".0f"),
                    ]
                ).properties(height=350)
                st.altair_chart(scatter_fp, use_container_width=True)

                st.markdown("---")
                st.subheader("⚙️ Complex Processing × Esforço Previsto")
                st.caption("O fator de complexidade técnica captura uma parte significativa do esforço via PCA.")

                scatter_cp = alt.Chart(data).mark_circle(size=80, opacity=0.8, color="#F4845F").encode(
                    x=alt.X("complex_processing:Q", title="Complex Processing"),
                    y=alt.Y("effort_hours_previsto:Q", title="Esforço Previsto (h)"),
                    tooltip=[
                        alt.Tooltip("project_id:N", title="Projeto"),
                        alt.Tooltip("complex_processing:Q", title="Complex Processing"),
                        alt.Tooltip("effort_hours_previsto:Q", title="Esforço (h)", format=".0f"),
                    ]
                ).properties(height=350)
                st.altair_chart(scatter_cp, use_container_width=True)

                if len(data) > 1:
                    st.markdown("---")
                    st.subheader("📊 Comparativo de Esforço por Projeto")
                    st.caption("Barras ordenadas por esforço estimado — facilita priorização e comparação entre projetos.")

                    bar_data = data.sort_values("effort_hours_previsto", ascending=False).head(30)
                    bar = alt.Chart(bar_data).mark_bar().encode(
                        x=alt.X("project_id:N",
                                sort="-y",
                                title="Projeto",
                                axis=alt.Axis(labelAngle=-30)),
                        y=alt.Y("effort_hours_previsto:Q", title="Esforço Previsto (h)"),
                        color=alt.Color("effort_hours_previsto:Q",
                                        scale=alt.Scale(scheme="blues"),
                                        legend=None),
                        tooltip=[
                            alt.Tooltip("project_id:N", title="Projeto"),
                            alt.Tooltip("effort_hours_previsto:Q", title="Esforço (h)", format=".0f"),
                            alt.Tooltip("semanas_estimadas:Q", title="Semanas"),
                        ]
                    ).properties(height=400)
                    st.altair_chart(bar, use_container_width=True)

# ---------------------------------------------------------------
# Sidebar FAQ
# ---------------------------------------------------------------
st.sidebar.title("ℹ️ FAQ")
st.sidebar.markdown("""
**O que o Agile Estimator v2 faz?**
Estima o **esforço total** (em horas-pessoa) para desenvolver um projeto de software, usando IA treinada em dados reais.

**Qual a diferença para a v1?**
A v1 previa produtividade por sprint. A v2 prediz esforço total do projeto, usando um modelo mais robusto com validação cruzada e PCA.

**Como usar?**
1. Insira os dados (manual, CSV ou Trello).
2. Clique em **Calcular Esforço Total Estimado**.
3. Visualize e baixe os resultados.

**O que são Function Points?**
Uma métrica de tamanho funcional de software, independente de tecnologia. Representa a quantidade de funcionalidade entregue ao usuário.

**Qual a precisão do modelo?**
MAPE médio ~49%. Use como estimativa inicial e para comparação relativa entre projetos.
""")

st.markdown("---")
st.caption("Agile Estimator v2 — © 2025 Todos os direitos reservados.")
