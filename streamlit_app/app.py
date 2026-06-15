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
st.set_page_config(page_title="Agile Estimator", layout="wide")

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

# Mapeamento de nomes internos para exibição ao usuário
COLUMN_DISPLAY = {
    "project_id":                   "Projeto",
    "function_points":              "Tamanho do Projeto (AFP)",
    "performance_requirements":     "Requisitos de Desempenho",
    "complex_processing":           "Complexidade Técnica",
    "installation_ease":            "Facilidade de Implantação",
    "additional_complexity_factor": "Complexidade Adicional",
    "effort_hours_previsto":        "Esforço Estimado (Horas)",
    "dias_estimados":               "Dias Estimados",
    "semanas_estimadas":            "Semanas Estimadas",
    "Escala":                       "Comparação Visual",
}

# ---------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------

def preprocess_for_api(row: dict) -> dict:
    """Scale + PCA the 4 business features; standardize function_points; return API payload."""
    X = pd.DataFrame([row])[BUSINESS_FEATURES].astype(float)
    X_scaled = scaler.transform(X)
    pcs = pca.transform(X_scaled)[0]
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


def display_df(df: pd.DataFrame) -> pd.DataFrame:
    """Rename internal column names to user-friendly display names."""
    return df.rename(columns=COLUMN_DISPLAY)

# ---------------------------------------------------------------
# Page header
# ---------------------------------------------------------------
st.title("🚀 Agile Estimator")
st.write("Estime o esforço de projetos de software com o apoio de **Inteligência Artificial**.")

# ---------------------------------------------------------------
# Input tabs
# ---------------------------------------------------------------
tab_tutorial, tab_input, tab_csv, tab_trello = st.tabs([
    ":material/info: Sobre o Agile Estimator",
    ":material/edit_note: Inserir dados manualmente",
    ":material/upload_file: Importar CSV",
    ":material/link: Importar do Trello",
])

# ===========================
# SOBRE O AGILE ESTIMATOR
# ===========================
with tab_tutorial:
    st.title(":material/info: Sobre o Agile Estimator")
    st.markdown("""
    O **Agile Estimator** utiliza Inteligência Artificial e técnicas de Machine Learning para estimar
    o esforço total necessário para o desenvolvimento de projetos de software. As previsões são geradas
    em horas-pessoa com base em dados históricos reais, validação estatística e na análise de múltiplos
    fatores que influenciam a complexidade e o esforço de implementação, proporcionando suporte mais
    consistente ao planejamento e à tomada de decisão em projetos de software.

    ---
    """)

    st.subheader(":material/model_training: Sobre o modelo")
    st.markdown("""
    As estimativas são geradas por um modelo de Inteligência Artificial treinado com dados reais de
    projetos de software. Durante o desenvolvimento, diferentes técnicas de Machine Learning foram
    avaliadas e comparadas para identificar a abordagem com melhor desempenho na previsão de esforço.

    O modelo considera fatores relacionados ao tamanho e à complexidade do projeto, analisando padrões
    observados em projetos anteriores para gerar uma estimativa do esforço total necessário para sua
    implementação.

    As previsões devem ser utilizadas como apoio ao planejamento e à tomada de decisão, complementando
    a experiência e o conhecimento da equipe do projeto.
    """)

    st.markdown("---")
    st.subheader(":material/checklist: Informações necessárias para gerar a estimativa")
    st.markdown("Para calcular o esforço do projeto, informe os seguintes dados:")

    st.markdown("""
    | Campo | Como preencher | Descrição |
    |-------|----------------|-----------|
    | **Tamanho do Projeto (AFP)** | Número | Representa o tamanho do sistema. Quanto mais funcionalidades, telas, relatórios e integrações o projeto possuir, maior tende a ser o esforço necessário para desenvolvê-lo. |
    | **Requisitos de Desempenho** | Escala de 1 a 5 | Indica o nível de exigência de desempenho do sistema. Utilize valores mais altos para aplicações que exigem alta velocidade de resposta, processamento intenso ou grande volume de usuários. |
    | **Complexidade Técnica** | Escala de 1 a 5 | Representa a complexidade técnica do projeto, considerando regras de negócio, cálculos, algoritmos, integrações e processamento de dados. |
    | **Facilidade de Implantação** | Escala de 1 a 5 | Indica o grau de facilidade para instalação e implantação da solução. **1 = muito difícil** e **5 = muito fácil**. |
    | **Complexidade Adicional** | Escala de 1 a 5 | Considere fatores adicionais que possam aumentar a complexidade do projeto, como requisitos especiais, restrições técnicas, integrações complexas ou necessidades específicas do cliente. |
    """)

    st.markdown("---")
    st.subheader(":material/bar_chart: Resultados da estimativa")
    st.markdown("""
    Após a análise dos dados informados, o Agile Estimator apresenta uma previsão do esforço necessário
    para o projeto nos seguintes formatos:

    | Resultado | Descrição |
    |-----------|-----------|
    | **Esforço Estimado (Horas)** | Quantidade total de horas-pessoa previstas para desenvolver o projeto do início ao fim. |
    | **Dias Estimados** | Conversão do esforço total para dias de trabalho, considerando uma jornada de 8 horas por dia. |
    | **Semanas Estimadas** | Conversão do esforço total para semanas úteis, considerando 5 dias de trabalho por semana. |

    **Importante:** Os valores representam uma estimativa inicial para apoiar o planejamento do projeto.
    O esforço real pode variar conforme fatores como tamanho da equipe, experiência dos profissionais,
    mudanças de escopo, riscos e particularidades do ambiente de desenvolvimento.
    """)

    st.markdown("---")
    st.subheader(":material/warning: Limitações da estimativa")
    st.markdown("""
    - As estimativas fornecidas representam uma previsão inicial e devem ser utilizadas como apoio ao planejamento e à tomada de decisão.
    - Como todo modelo preditivo, os resultados podem variar de acordo com as características específicas de cada projeto, equipe e contexto de desenvolvimento.
    - A ferramenta tende a ser mais útil para comparar cenários e analisar o impacto de diferentes características do projeto do que para determinar um prazo exato de execução.
    - Projetos com características muito diferentes dos projetos utilizados no treinamento do modelo podem apresentar maior variação nas estimativas.

    **Recomendação:** Utilize os resultados como uma referência inicial e combine-os com a experiência
    da equipe, análise de riscos e conhecimento do negócio para obter estimativas mais robustas.
    """)

    st.markdown("---")
    st.subheader(":material/help_outline: Como utilizar o Agile Estimator")
    st.markdown("""
    O processo é simples e pode ser realizado em poucos passos:
    """)

    st.markdown("""
    **1. Informe os dados do projeto**

    Escolha a forma mais conveniente para fornecer as informações:
    - Preenchimento manual;
    - Importação de arquivo CSV;
    - Integração com um board do Trello.

    **2. Gere a estimativa**

    Clique em **Calcular Estimativa** para que a ferramenta analise os dados informados e processe a previsão de esforço.

    **3. Analise os resultados**

    Visualize a estimativa de esforço em:
    - Horas-pessoa;
    - Dias de trabalho;
    - Semanas de projeto.

    **4. Exporte ou compartilhe os dados**

    Baixe os resultados em formato CSV para utilização em planejamentos, relatórios ou análises complementares.

    **5. Compare diferentes cenários**

    Utilize a aba **Visualizações** para analisar e comparar projetos, identificando diferenças de tamanho, complexidade e esforço estimado.

    **Dica:** Experimente alterar alguns parâmetros do projeto para entender como fatores como tamanho
    funcional e complexidade podem impactar a estimativa final.
    """)

# ===========================
# INPUT MANUAL
# ===========================
with tab_input:
    st.subheader("Inserir dados manualmente")

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
            "Projeto",
            value=st.session_state.input_user["project_id"],
            help="Identificador único do projeto (ex: projeto_alpha)"
        )
        if not project_id.strip():
            project_id = f"projeto_{np.random.randint(100, 999)}"

        function_points = st.number_input(
            "Tamanho do Projeto (AFP)",
            min_value=0.0,
            value=float(st.session_state.input_user["function_points"]),
            step=10.0,
            help="Tamanho funcional do software em Adjusted Function Points. Quanto mais funcionalidades, telas e integrações, maior tende a ser o valor."
        )

        performance_requirements = st.number_input(
            "Requisitos de Desempenho (1–5)",
            min_value=1.0,
            max_value=5.0,
            value=float(st.session_state.input_user["performance_requirements"]),
            step=0.5,
            help="Nível de exigência de desempenho do sistema. 1 = Muito Baixo, 5 = Muito Alto."
        )

    with col2:
        complex_processing = st.number_input(
            "Complexidade Técnica (1–5)",
            min_value=1.0,
            max_value=5.0,
            value=float(st.session_state.input_user["complex_processing"]),
            step=0.5,
            help="Complexidade técnica do projeto: regras de negócio, algoritmos, integrações. 1 = Muito Baixo, 5 = Muito Alto."
        )

        installation_ease = st.number_input(
            "Facilidade de Implantação (1–5)",
            min_value=1.0,
            max_value=5.0,
            value=float(st.session_state.input_user["installation_ease"]),
            step=0.5,
            help="Facilidade de instalação e implantação da solução. 1 = Muito Difícil, 5 = Muito Fácil."
        )

        additional_complexity_factor = st.number_input(
            "Complexidade Adicional (1–5)",
            min_value=1.0,
            max_value=5.0,
            value=float(st.session_state.input_user["additional_complexity_factor"]),
            step=0.5,
            help="Fatores adicionais de complexidade: requisitos especiais, restrições técnicas, integrações complexas. 1 = Muito Baixo, 5 = Muito Alto."
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
        if st.button("Adicionar Projeto", icon=":material/add_circle:", use_container_width=True):
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
            st.toast("Projeto adicionado com sucesso!", icon=None)
            st.rerun()

    with col_btn2:
        if st.button("Resetar formulário", icon=":material/restart_alt:", use_container_width=True):
            st.session_state.input_user = {
                "project_id": "projeto_001",
                "function_points": 300.0,
                "performance_requirements": 3.0,
                "complex_processing": 4.0,
                "installation_ease": 3.0,
                "additional_complexity_factor": 3.0,
            }
            st.session_state.data = None
            st.toast("Formulário e dados resetados.", icon=None)
            st.rerun()

    st.markdown("---")
    with st.expander("Calculadora IFPUG de Function Points", expanded=False):
        st.markdown("""
        Utilize esta calculadora para obter os **Adjusted Function Points (AFP)** do seu projeto
        com base no método **IFPUG** — o mesmo padrão utilizado no dataset de treinamento do modelo.

        Conte quantas funções de cada tipo existem no projeto, separadas por complexidade (**Simples / Média / Complexa**):
        """)

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
            for (_, (ws, wm, wc)), (n_s, n_m, n_c) in zip(IFPUG_WEIGHTS.items(), fp_counts.values())
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
            if st.button("Utilizar este valor como Tamanho do Projeto (AFP)", icon=":material/check:", key="use_fp_calc"):
                st.session_state.input_user["function_points"] = fp_result
                st.success(f"Tamanho do Projeto definido para **{fp_result}**. Ajuste os demais campos e clique em *Adicionar Projeto*.")
                st.rerun()

# ===========================
# UPLOAD CSV
# ===========================
with tab_csv:
    st.subheader("Importar projetos por arquivo CSV")
    st.markdown("""
    Envie um arquivo CSV contendo as informações dos projetos que deseja analisar.
    A ferramenta processará automaticamente cada registro e gerará as estimativas correspondentes.

    **Campos obrigatórios:**
    - `function_points`
    - `performance_requirements`
    - `complex_processing`
    - `installation_ease`
    - `additional_complexity_factor`

    **Campo opcional:**
    - `project_id` (nome ou identificador do projeto)

    **Dica:** Utilize o campo `project_id` para facilitar a identificação dos projetos nos resultados,
    gráficos e relatórios exportados.
    """)

    # Template download
    template_df = pd.DataFrame(columns=[
        "project_id", "function_points", "performance_requirements",
        "complex_processing", "installation_ease", "additional_complexity_factor"
    ])
    template_csv = template_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar Template de CSV",
        data=template_csv,
        file_name="template_agile_estimator.csv",
        mime="text/csv",
        icon=":material/download:",
    )

    st.markdown("---")
    uploaded_file = st.file_uploader("Selecione o arquivo CSV", type="csv")

    if uploaded_file is not None:
        df_csv = pd.read_csv(uploaded_file)
        missing = validate_columns(df_csv)

        if missing:
            st.error(f"Colunas obrigatórias ausentes: {', '.join(missing)}")
        else:
            if "project_id" not in df_csv.columns:
                df_csv.insert(0, "project_id", [f"projeto_{i+1}" for i in range(len(df_csv))])

            st.dataframe(df_csv.head(10), use_container_width=True)
            st.caption(f"{len(df_csv)} projeto(s) encontrado(s) no arquivo.")

            if st.button("Carregar este CSV", icon=":material/upload:", use_container_width=False):
                st.session_state.data = df_csv.copy()
                st.session_state.last_source = "csv"
                st.toast(f"{len(df_csv)} projeto(s) carregado(s)!", icon=None)
                st.rerun()
    else:
        st.info("Nenhum CSV carregado ainda.")

# ===========================
# TRELLO
# ===========================
with tab_trello:
    st.subheader("Importar projetos do Trello")
    st.markdown("""
    Importe automaticamente as informações dos projetos a partir de um board do Trello.
    Basta informar o link de um **board público** e a ferramenta irá analisar os cartões
    para gerar as estimativas de esforço.

    **Para que a importação funcione corretamente, cada cartão deve possuir os seguintes campos personalizados:**
    - Function Points
    - Performance Requirements
    - Complex Processing
    - Installation Ease
    - Additional Complexity Factor

    **Dica:** Utilize um cartão para cada projeto que deseja estimar. Os resultados serão
    gerados automaticamente após a importação dos dados.
    """)

    st.markdown("**Link do Board Trello**")
    st.markdown("Cole abaixo a URL do board público que deseja analisar.")

    trello_url = st.text_input(
        "URL do board",
        placeholder="https://trello.com/b/DKf6KNh2/testeagileestimator"
    )

    trello_regex = r"^https://trello\.com/b/[a-zA-Z0-9]+(/[a-zA-Z0-9_-]+)?$"

    if trello_url:
        if not re.match(trello_regex, trello_url):
            st.error("Link inválido. Utilize o formato: `https://trello.com/b/<board_id>`")
        else:
            if st.button("Buscar projetos do Trello", icon=":material/search:", use_container_width=False):
                with st.spinner("Buscando dados do Trello..."):
                    try:
                        df_trello = get_trello_cards_public(trello_url)
                        missing = validate_columns(df_trello)

                        if missing:
                            st.warning(
                                f"Campos não encontrados nos cartões: {', '.join(missing)}. "
                                "Verifique os nomes dos campos personalizados no board."
                            )
                        elif df_trello.dropna(subset=REQUIRED_COLUMNS).empty:
                            st.warning("Nenhum cartão com todos os campos preenchidos foi encontrado.")
                        else:
                            df_trello = df_trello.dropna(subset=REQUIRED_COLUMNS).reset_index(drop=True)
                            st.session_state.trello_preview = df_trello.copy()
                    except Exception as e:
                        st.error(f"Erro ao buscar dados do Trello: {e}")
                        st.session_state.pop("trello_preview", None)

            if "trello_preview" in st.session_state:
                df_preview = st.session_state.trello_preview
                st.dataframe(df_preview.head(10), use_container_width=True)
                st.caption(f"{len(df_preview)} projeto(s) encontrado(s) no board.")
                if st.button("Carregar estes projetos", icon=":material/download_done:", use_container_width=False):
                    st.session_state.data = df_preview.copy()
                    st.session_state.last_source = "trello"
                    st.session_state.pop("trello_preview", None)
                    st.toast(f"{len(df_preview)} projeto(s) importado(s) do Trello!", icon=None)
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
        st.info(f"**{n} projeto(s)** carregado(s) — origem: **{source}**")
    with col_clear:
        if st.button("Limpar dados", icon=":material/delete_outline:", use_container_width=True):
            st.session_state.data = None
            st.session_state.last_source = None
            st.rerun()

# ---------------------------------------------------------------
# Results section
# ---------------------------------------------------------------
if "data" in st.session_state and st.session_state.data is not None and not st.session_state.data.empty:

    res_tab1, res_tab2, res_tab3 = st.tabs([
        ":material/table_view: Dados",
        ":material/bar_chart: Estimativas",
        ":material/insights: Visualizações",
    ])

    # -------------------------
    # TAB 1 — DADOS
    # -------------------------
    with res_tab1:
        st.subheader("Projetos carregados")
        display_cols = [c for c in ["project_id"] + REQUIRED_COLUMNS
                        if c in st.session_state.data.columns]
        st.dataframe(
            display_df(st.session_state.data[display_cols].head(100)),
            use_container_width=True
        )
        st.caption(f"Total de projetos: **{len(st.session_state.data)}**")

    # -------------------------
    # TAB 2 — ESTIMATIVAS
    # -------------------------
    with res_tab2:
        st.subheader("Calcular Esforço Total Estimado")

        if st.button("Calcular Estimativa", icon=":material/calculate:", key="calc_esforco"):
            missing = validate_columns(st.session_state.data)
            if missing:
                st.error(f"Colunas faltando: {', '.join(missing)}")
            else:
                with st.spinner("Calculando estimativas via API..."):
                    try:
                        result_df, errors = estimate_batch(st.session_state.data)
                        st.session_state.data = result_df

                        if errors:
                            msg = errors[0]
                            cold_start = "timed out" in msg.lower() or "Read timed out" in msg
                            dica = (" A API pode estar em cold start (plano gratuito Render — aguarde ~30s e tente novamente)." if cold_start else "")
                            st.warning(f"{len(errors)} erro(s) durante a inferência: {msg}{dica}")

                        valid = result_df["effort_hours_previsto"].notna().sum()
                        st.success(f"Estimativas calculadas para {valid} projeto(s)!")
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
                st.warning("Nenhuma estimativa disponível. Tente novamente — a API pode estar aquecendo (cold start ~30s).")
            else:
                st.markdown("### Resultados")

                # Renomeia para exibição
                preview_display = display_df(preview)
                fmt_col = COLUMN_DISPLAY.get("effort_hours_previsto", "effort_hours_previsto")
                fmt = {fmt_col: lambda x: f"{x:.0f} h" if pd.notna(x) else "-"}
                st.dataframe(
                    preview_display.style.format(fmt),
                    use_container_width=True
                )

                st.markdown("""
                #### ℹ️ Como interpretar os resultados

                | Resultado | Descrição |
                |-----------|-----------|
                | **Esforço Estimado (Horas)** | Quantidade total de horas-pessoa previstas para desenvolver o projeto do início ao fim. |
                | **Dias Estimados** | Conversão do esforço total para dias de trabalho, considerando uma jornada de 8 horas por dia. |
                | **Semanas Estimadas** | Conversão do esforço total para semanas úteis, considerando 5 dias de trabalho por semana. |
                | **Comparação Visual** | Representação visual que facilita a comparação do esforço estimado entre diferentes projetos analisados. |

                **Importante:** As estimativas representam o esforço total necessário para a conclusão do projeto
                e devem ser utilizadas como apoio ao planejamento e à tomada de decisão.

                **Atenção:** Os valores apresentados referem-se ao projeto completo e não a uma sprint,
                tarefa específica ou período isolado de desenvolvimento.
                """)

                csv_bytes = data[[c for c in preview_cols if c in data.columns]].to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Exportar Resultados (CSV)",
                    data=csv_bytes,
                    file_name="estimativas_esforco.csv",
                    mime="text/csv",
                    icon=":material/download:",
                )

    # -------------------------
    # TAB 3 — VISUALIZAÇÕES
    # -------------------------
    with res_tab3:
        if "effort_hours_previsto" not in st.session_state.data.columns:
            st.warning("Calcule as estimativas primeiro na aba **Estimativas**.")
        else:
            data = st.session_state.data.dropna(subset=["effort_hours_previsto"]).copy()

            if data.empty:
                st.warning("Nenhum resultado disponível para visualização.")
            else:
                st.subheader(":material/bar_chart: Distribuição do Esforço Estimado entre Projetos")
                st.caption("Este gráfico mostra como o esforço estimado se distribui entre os projetos analisados. Cada barra representa a quantidade de projetos que se enquadra em uma determinada faixa de horas. Use-o para identificar se os projetos analisados são semelhantes em esforço ou se há grande variação entre eles.")

                hist = alt.Chart(data).mark_bar().encode(
                    x=alt.X("effort_hours_previsto:Q",
                            bin=alt.Bin(maxbins=20),
                            title="Esforço Estimado (Horas)"),
                    y=alt.Y("count()", title="Nº de Projetos"),
                    tooltip=["count()"]
                ).properties(height=350)
                st.altair_chart(hist, use_container_width=True)

                st.markdown("---")
                st.subheader(":material/scatter_plot: Tamanho do Projeto × Esforço Estimado")
                st.caption("Este gráfico mostra a relação entre o tamanho funcional de cada projeto e o esforço estimado para desenvolvê-lo. Cada ponto representa um projeto: quanto mais à direita, maior o seu tamanho funcional (AFP); quanto mais acima, maior o esforço previsto. Use-o para verificar se projetos maiores tendem a exigir mais horas de desenvolvimento.")

                scatter_fp = alt.Chart(data).mark_circle(size=80, opacity=0.8).encode(
                    x=alt.X("function_points:Q", title="Tamanho do Projeto (AFP)"),
                    y=alt.Y("effort_hours_previsto:Q", title="Esforço Estimado (h)"),
                    tooltip=[
                        alt.Tooltip("project_id:N", title="Projeto"),
                        alt.Tooltip("function_points:Q", title="Tamanho do Projeto (AFP)"),
                        alt.Tooltip("effort_hours_previsto:Q", title="Esforço (h)", format=".0f"),
                    ]
                ).properties(height=350)
                st.altair_chart(scatter_fp, use_container_width=True)

                st.markdown("---")
                st.subheader(":material/bubble_chart: Complexidade Técnica × Esforço Estimado")
                st.caption("Este gráfico mostra como a complexidade técnica de cada projeto influencia o esforço estimado. Cada ponto representa um projeto: quanto mais à direita, maior a sua complexidade técnica; quanto mais acima, maior o esforço previsto. Use-o para avaliar se projetos com regras de negócio mais elaboradas, integrações ou processamentos complexos tendem a demandar mais tempo de desenvolvimento.")

                scatter_cp = alt.Chart(data).mark_circle(size=80, opacity=0.8, color="#F4845F").encode(
                    x=alt.X("complex_processing:Q", title="Complexidade Técnica"),
                    y=alt.Y("effort_hours_previsto:Q", title="Esforço Estimado (h)"),
                    tooltip=[
                        alt.Tooltip("project_id:N", title="Projeto"),
                        alt.Tooltip("complex_processing:Q", title="Complexidade Técnica"),
                        alt.Tooltip("effort_hours_previsto:Q", title="Esforço (h)", format=".0f"),
                    ]
                ).properties(height=350)
                st.altair_chart(scatter_cp, use_container_width=True)

                if len(data) > 1:
                    st.markdown("---")
                    st.subheader(":material/bar_chart: Comparação do Esforço entre Projetos")
                    st.caption("Este gráfico apresenta uma barra para cada projeto analisado, com altura proporcional ao esforço estimado em horas. Quanto mais alta a barra, maior o esforço previsto para desenvolver aquele projeto. Os projetos são exibidos em ordem decrescente de esforço (da esquerda para a direita) facilitando a identificação imediata dos projetos mais e menos complexos. Use-o para comparar projetos entre si e apoiar decisões de priorização, alocação de equipe e definição de prazos.")

                    bar_data = data.sort_values("effort_hours_previsto", ascending=False).head(30)
                    bar = alt.Chart(bar_data).mark_bar().encode(
                        x=alt.X("project_id:N",
                                sort="-y",
                                title="Projeto",
                                axis=alt.Axis(labelAngle=-30)),
                        y=alt.Y("effort_hours_previsto:Q", title="Esforço Estimado (h)"),
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
# Sidebar
# ---------------------------------------------------------------
st.sidebar.title(":material/info: Sobre o Agile Estimator")
st.sidebar.markdown("""
**O que o Agile Estimator faz?**
Utiliza Inteligência Artificial e técnicas de Machine Learning para estimar o esforço total necessário
para o desenvolvimento de projetos de software. As previsões são geradas em horas-pessoa com base em
dados históricos reais, validação estatística e na análise de múltiplos fatores que influenciam a
complexidade e o esforço de implementação.

---

**Como utilizar?**
1. Informe os dados do projeto (manual, CSV ou Trello).
2. Clique em **Calcular Estimativa**.
3. Visualize e exporte os resultados.

---

**O que são Function Points (Pontos de Função)?**
Pontos de Função são uma forma de medir o tamanho de um software com base nas funcionalidades que ele
oferece aos usuários. Quanto mais telas, relatórios, integrações e recursos o sistema possuir, maior
tende a ser sua quantidade de Pontos de Função e, consequentemente, o esforço necessário para desenvolvê-lo.

---

**Qual a confiabilidade das estimativas?**
A ferramenta oferece estimativas iniciais baseadas em padrões identificados em projetos reais de software.
Como todo modelo preditivo, os resultados podem variar conforme as características de cada projeto e devem
ser utilizados como complemento à análise e experiência da equipe.
""")

st.markdown("---")
st.caption("Agile Estimator — © 2026 Todos os direitos reservados.")
