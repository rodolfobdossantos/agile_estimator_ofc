import streamlit as st
import pandas as pd
import numpy as np
import pickle
import joblib
import altair as alt
import os
import re

from scripts.get_public_trello_board import get_trello_cards_public

# -------------------------------
# Funções auxiliares
# -------------------------------

def input_metrics(data):

    data["qtd_bugs"] = data["percentual_bugs"] * data["cartoes_previstos"]

    data["qtd_retrabalho"] = data["percentual_retrabalho"] * data["cartoes_previstos"]

    data["carga_cartoes_por_membro"] = data["cartoes_previstos"] / data["qtd_membros"]

    # Criar coluna auxiliar com o número da sprint

    return data[['produtividade_estimada',
       'tipo_dominio', 'complexidade_media',
       'qtd_bugs', 'qtd_retrabalho',
       'carga_cartoes_por_membro']]

def preprocess_input(data, scaler, label_encoder):

    # realizando o encoding do domino e escalonamento da produtividade_estimada
    data['tipo_dominio'] = label_encoder.transform(data['tipo_dominio'])
    
    columns_to_scale = ['produtividade_estimada','story_points_previstos']
    data[columns_to_scale] = scaler.transform(data[columns_to_scale])

    data = input_metrics(data)

    return data

def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)
    

# -------------------------------
# Carregar modelo e transformadores
# -------------------------------


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # streamlit_app/
ARTIFACTS_DIR = os.path.join(BASE_DIR, "..", "artifacts")

MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model", "agile_estimator.pkl")
SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler", "standard_scaler_produtividade_estimada_story_points_previstos.pkl")
ENCODER_PATH = os.path.join(ARTIFACTS_DIR, "encoder", "label_encoder_tipo_dominio.pkl")

model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_encoder = joblib.load(ENCODER_PATH)


# CSS para personalizar o tooltip em tema escuro (fundo preto)
st.markdown("""
    <style>
    /* Ícone do tooltip (interrogação) */
    [data-testid="stTooltipIcon"] {
        color: #FFD700 !important;  /* Amarelo dourado, destaque em fundo preto */
        font-size: 18px !important; /* Ajusta tamanho do ícone */
        opacity: 0.9;               /* Leve transparência para suavizar */
    }

    /* Texto do tooltip */
    div[data-baseweb="tooltip"] {
        background-color: #222 !important;  /* Fundo do balão do tooltip */
        color: #FFF !important;             /* Texto branco */
        border: 1px solid #FFD700;          /* Bordas com a mesma cor do ícone */
        font-size: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Interface principal
# -------------------------------

st.set_page_config(page_title="Agile Estimator", layout="wide")
st.title("🚀 Agile Estimator")
st.write("Estimativa de produtividade baseada em dados históricos do Trello.")

csv, trello = st.tabs(["Upload CSV", "Puxar do Trello"])

with csv:
    uploaded_file = st.file_uploader("📂 Carregue seu arquivo CSV", type="csv")

with trello:

    uploaded_trello = st.text_input(
        "📋 Carregue suas sprints do Trello",
        placeholder="https://api.trello.com/1/boards/meu_board"
    )

    # Regex para validar link do Trello
    trello_regex = r"^https://api\.trello\.com/1/boards/[a-zA-Z0-9_-]+$"

    if uploaded_trello:

        if re.match(trello_regex, uploaded_trello):
            st.markdown(f"✅ Link do Trello válido: {uploaded_trello}")
            #  lógica para conectar ao board get_trello_cards_public()
            uploaded_file = uploaded_trello

        else:
            st.error("❌ Link inválido! Certifique-se de que segue o formato: https://api.trello.com/1/boards/<board_id>")

# --- depois do upload do arquivo ---

if  uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.success("✅ Dados carregados com sucesso!")

    # guarda os dados brutos no session_state
    if "data" not in st.session_state:
        
        st.session_state.data = data.copy()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Dados", "📈 Estimativas", "📊 Visualizações"])

    with tab1:
        columns = ["sprint_id","data_inicio","qtd_membros","complexidade_media",]

        st.subheader("Pré-visualização dos dados")
        st.dataframe(st.session_state.data[columns].head(50))
        st.write(f"Total de registros: {len(st.session_state.data)}")
        st.dataframe(st.session_state.data.columns,
                     width=300)  # mostra as colunas carregadas


    with tab2:
        
        if st.button("⚡ Fazer Estimativa"):
            try:
                processed_data = preprocess_input(
                    st.session_state.data.copy(), scaler, label_encoder
                )
                predictions = model.predict(processed_data)
                st.session_state.data["produtividade_prevista"] = predictions  # <-- GUARDA NO SESSION_STATE

                st.success("✅ Estimativas calculadas!")
                st.dataframe(st.session_state.data.head(50))

                csv = st.session_state.data.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Baixar resultados",
                    data=csv,
                    file_name="estimativas_produtividade.csv",
                    mime="text/csv",
                )
            except Exception as e:
                st.error(f"Erro ao processar os dados: {e}")

        with tab3:
            if "produtividade_prevista" in st.session_state.data.columns:
                data = st.session_state.data.copy()
                st.subheader("🔎 Filtros")

                # ------------------ Filtros persistentes ------------------
                if "range_filter" not in st.session_state:
                    st.session_state.range_filter = (
                        float(data["produtividade_prevista"].min()),
                        float(data["produtividade_prevista"].max()),
                    )

                if "dominio_filter" not in st.session_state:
                    st.session_state.dominio_filter = list(data["tipo_dominio"].unique())

                range_filter = st.slider(
                    "Intervalo da produtividade prevista",
                    float(data["produtividade_prevista"].min()),
                    float(data["produtividade_prevista"].max()),
                    st.session_state.range_filter,
                    key="range_filter",
                )

                dominio_filter = st.multiselect(
                    "Selecione o(s) domínio(s)",
                    list(data["tipo_dominio"].unique()),
                    default=st.session_state.dominio_filter,
                    key="dominio_filter",
                )

                # Lista de sprints disponíveis
                all_sprints = list(data["sprint_id"].unique())

                # Checkbox para selecionar todas
                select_all = st.checkbox("Selecionar todas as sprints", value=True)

                if select_all:
                    sprint_filter = all_sprints
                else:
                    sprint_filter = st.multiselect(
                        "Selecione a(s) sprint(s)",
                        all_sprints,
                        default=st.session_state.sprint_filter if "sprint_filter" in st.session_state else all_sprints,
                        key="sprint_filter",
                    )

                filtered_data = data[
                    (data["produtividade_prevista"] >= range_filter[0])
                    & (data["produtividade_prevista"] <= range_filter[1])
                    & (data["tipo_dominio"].isin(dominio_filter))
                    & (data["sprint_id"].isin(sprint_filter))
                ]

                st.write(f"Mostrando **{len(filtered_data)} registros** após filtros.")

                chart_data = filtered_data.copy()
                if len(chart_data) > 500:
                    chart_data = chart_data.sample(500, random_state=42)

                chart_data["sprint_num"] = chart_data["sprint_id"].str.extract("(\d+)").astype(int)
                chart_data = chart_data.sort_values("sprint_num").reset_index(drop=True)


                st.subheader("📊 Histograma de Produtividade Prevista")
                st.caption("Mostra quantas vezes cada nível de produtividade aparece, separado por domínio. Útil para enxergar a distribuição geral.")

                hist_chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X("produtividade_prevista:Q", bin=alt.Bin(maxbins=20), title="Produtividade Prevista"),
                    y=alt.Y("count()", title="Frequência"),
                    color="tipo_dominio:N",
                    tooltip=["count()", "tipo_dominio"]
                ).properties(width=600, height=400)

                st.altair_chart(hist_chart, use_container_width=True)

                # Boxplot

                st.subheader("📦 Boxplot por Domínio")
                st.caption("Mostra como a produtividade prevista varia em cada domínio, incluindo valores médios e pontos fora do padrão.")

                box_plot = alt.Chart(chart_data).mark_boxplot().encode(
                    x="tipo_dominio:N", 
                    y=alt.Y("produtividade_prevista:Q", title="Produtividade Prevista"),
                    color="tipo_dominio:N",
                    tooltip=["tipo_dominio", "produtividade_prevista"]
                ).properties(width=600, height=400)
                st.altair_chart(box_plot, use_container_width=True)

                # Barras (média)   

                st.subheader("📊 Produtividade Média por Tamanho da Equipe")
                st.caption("Compara a produtividade média de acordo com o número de membros do time. Ajuda a entender como o tamanho da equipe influencia.")

                bar_chart = alt.Chart(chart_data).mark_bar().encode(
                    x="qtd_membros:N",
                    y=alt.Y("mean(produtividade_prevista):Q", title="Produtividade Média Prevista"),
                    color="tipo_dominio:N",
                    tooltip=[
                        "qtd_membros",
                        alt.Tooltip("mean(produtividade_prevista):Q", title="Produtividade Média"),
                        "tipo_dominio",
                    ],
                ).properties(width=600, height=400)
                st.altair_chart(bar_chart, use_container_width=True)

                st.subheader("🥧 Participação dos Domínios")
                st.caption("Mostra a proporção de produtividade média de cada domínio em relação ao total. Facilita a comparação entre áreas.")

                pie_data = (
                    chart_data.groupby("tipo_dominio")["produtividade_prevista"]
                    .mean()
                    .reset_index()
                )

                pie_chart = alt.Chart(pie_data).mark_arc().encode(
                    theta="produtividade_prevista",
                    color="tipo_dominio",
                    tooltip=["tipo_dominio", "produtividade_prevista"],
                )
                st.altair_chart(pie_chart, use_container_width=True)

                # Linha

                st.subheader("📈 Evolução da Produtividade por Sprint")
                st.caption("Acompanha como a produtividade prevista muda ao longo das sprints. Ajuda a identificar tendências de crescimento ou queda.")

                line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                    x=alt.X("sprint_id:N", sort=list(chart_data["sprint_id"]), title="Sprint"),
                    y=alt.Y("produtividade_prevista:Q", title="Produtividade Prevista"),
                    color="tipo_dominio:N",
                    tooltip=["sprint_id", "produtividade_prevista", "tipo_dominio"]
                ).properties(width=600, height=400)
                st.altair_chart(line_chart, use_container_width=True)


                st.subheader("⚖️ Relação entre Produtividade, Bugs e Retrabalho")
                st.caption("Mostra se existe ligação entre produtividade, quantidade de bugs e retrabalho. Posição mais à direita indica maior produtividade; mais acima indica mais bugs.")

                scatter_chart = alt.Chart(chart_data).mark_circle(size=60).encode(
                    x=alt.X("produtividade_prevista:Q", title="Produtividade Prevista"),
                    y=alt.Y("percentual_bugs:Q", title="Percentual de Bugs (%)"),
                    color="tipo_dominio:N",
                    tooltip=[
                        alt.Tooltip("percentual_bugs:Q", title="Percentual de Bugs (%)"),
                        alt.Tooltip("percentual_retrabalho:Q", title="Percentual de Retrabalho (%)"),
                        alt.Tooltip("produtividade_prevista:Q", title="Produtividade Prevista"),
                        "tipo_dominio",
                    ]
                ).properties(width=600, height=400)
                st.altair_chart(scatter_chart, use_container_width=True)




 

# -------------------------------
# FAQ lateral
# -------------------------------
st.sidebar.title("ℹ️ FAQ")
# st.sidebar.button(on_click=close, label="🔄 Recarregar App")

st.sidebar.markdown("""
**O que é este aplicativo?**  
Um estimador de produtividade de equipes ágeis com base em dados históricos do Trello.  

**Como usar?**  
1. Carregue seu CSV.  
2. Clique em **Fazer Estimativa**.  
3. Explore as visualizações interativas.  
4. Baixe os resultados.  

""")

st.markdown("---")
st.caption("Agile Estimator 0.0.1 — © 2025 Todos os direitos reservados.")
