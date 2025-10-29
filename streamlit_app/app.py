import streamlit as st
import pandas as pd
import numpy as np
import pickle
import joblib
import altair as alt
import os
import re
import math

# -------------------------------
# Funções auxiliares
# -------------------------------

def input_metrics(data):

    data["qtd_bugs"] = data["percentual_bugs"] * data["cartoes_previstos"]

    data["qtd_retrabalho"] = data["percentual_retrabalho"] * data["cartoes_previstos"]

    data["carga_cartoes_por_membro"] = data["cartoes_previstos"] / data["qtd_membros"]

    # data["produtividade_estimada"] =  round(data["story_points_previstos"] / data["qtd_membros"], 2)
    

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
st.write("Estimativa de produtividade baseada em dados históricos.")


tutorial, input, csv, trello = st.tabs(["Tutorial","Input Manual", "Upload CSV", "Capturar do Trello (Em desenvolvimento)"])

with tutorial:
    st.title("📖 Tutorial do Agile Estimator")
    st.write("""
    Aqui você aprende como preencher cada campo de entrada e entender o que o modelo espera em cada etapa.
    """)

    st.subheader("💡 Inputs necessários")
    st.markdown("""
    Esses são os dados essenciais para que o modelo gere uma estimativa precisa da sua sprint:

    - **ID da Sprint** : Um identificador único para diferenciar cada sprint (exemplo: `sprint_1023`).

    - **Quantidade de Membros** : Número de pessoas envolvidas na sprint.

    - **Complexidade Média dos requisitos** : Grau médio de dificuldade das tarefas planejadas (0 a 100) — quanto maior o valor, maior o esforço esperado.

    - **Tipo de Tecnologia** : Área principal de desenvolvimento: **Web**, **Mobile**, **API** ou **Dados**.

    - **Story Points Planejados**: Total de pontos planejados para a execução das tarefas da sprint.

    - **Cartões Planejados**: Quantidade total de tarefas (tasks) planejados para o período.

    ---
    """)

    st.subheader("⚙️ Inputs adicionais (opcionais)")
    st.markdown("""
    Esses campos ajudam o modelo a entender melhor a qualidade e o esforço da sua sprint.

    - **Percentual de Bugs esperados (0 a 1)**  
    Indique a proporção aproximada de tarefas que geram bugs.  
    Exemplo: `0.05` → cerca de **5%** das entregas precisam de correção.

    - **Percentual de Retrabalho esperado(0 a 1)**  
    Informe quanto trabalho costuma ser refeito ou ajustado após a entrega.  
    Exemplo: `0.03` → cerca de **3%** das tarefas exigem retrabalho.
    """)

    st.info("📝 **Dica:** Se não tiver esses dados, deixe como **0**. O sistema ainda funcionará normalmente — esses valores apenas ajudam a tornar a previsão mais precisa.")
    st.markdown("---")


    st.subheader("📊 Outputs do projeto")
    st.markdown("""
    Aqui você pode ver o resultado que o **Agile Estimator** gera com base nas informações que você inseriu:

    #### **Produtividade Prevista:**  
                
    O modelo calcula **quanto o time pode produzir em uma sprint**, considerando uma jornada padrão de **8 horas úteis por dia**.  
    A partir dos dados fornecidos, ele **estima em quantos dias a sprint deve ser concluída** e mostra **previsões e insights** que ajudam o gestor a entender se a equipe está **dentro da capacidade esperada** ou se há **risco de atraso ou sobrecarga**.  

    Essas estimativas permitem **planejar melhor o trabalho**, **ajustar prazos** e **tomar decisões mais assertivas** durante o desenvolvimento do projeto.

    #### **Visualizações Interativas**: 
    
    Gráficos que mostram a **evolução da produtividade**, **distribuições**, e **relações com bugs e retrabalho** — tudo de forma dinâmica para facilitar a análise.

    #### **Download CSV**: 
    
    Exporte os resultados em formato `.csv` para análises adicionais ou integração com outras ferramentas.

    ---
    📊 **Insight:** use essas visualizações para identificar padrões e gargalos entre sprints — isso ajuda a ajustar estimativas futuras com mais precisão.
    """)

# --- ABA UPLOAD CSV ---
with csv:
    uploaded_file = st.file_uploader("📂 Carregue seu arquivo CSV", type="csv")

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.session_state.data = data.copy()
        st.session_state.last_source = "csv"
        st.success("✅ CSV carregado e salvo com sucesso!")
        # st.dataframe(st.session_state.data)
    else:
        st.info("📁 Nenhum CSV carregado.")


# --- ABA GET TRELLO ---
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
                # Exemplo de DataFrame simulado (substitua pela função real depois)

            st.session_state.data = pd.DataFrame([
                {"sprint_id": "trello_auto", "tipo_dominio": "Web", "qtd_membros": 3,
                "complexidade_media": 42.5, "produtividade_estimada": 70.0,
                "story_points_previstos": 50.0, "cartoes_previstos": 8,
                "percentual_bugs": 0.05, "percentual_retrabalho": 0.03}
            ])
            st.session_state.last_source = "trello"
            st.success("✅ Dados do Trello carregados e armazenados!")


        else:
            st.error("❌ Link inválido! Certifique-se de que segue o formato: https://api.trello.com/1/boards/<board_id>")

# --- ABA INPUT MANUAL ---
with input:
    st.subheader("📝 Inserir dados da Sprint manualmente")
    st.markdown("Preencha as informações abaixo ou clique em **Usar dados de exemplo** para testar.")

    # Inicializa input_user no session_state (default)
    if "input_user" not in st.session_state:
        st.session_state.input_user = {
            "sprint_id": f"sprint_{np.random.randint(1000,9999)}",
            "qtd_membros": 1,
            "complexidade_media": 2.3,
            "tipo_dominio": "Web",
            #"produtividade_estimada": 119.0,
            "story_points_previstos": 55.0,

            "cartoes_previstos": 10.0,
            "percentual_bugs": 0.05,
            "percentual_retrabalho": 0.03
        }

    col1, col2 = st.columns(2)

    with col1:

        sprint_id = st.text_input("🆔 ID da Sprint", value=st.session_state.input_user["sprint_id"])

        if not sprint_id.strip():
            sprint_id = f"sprint_{np.random.randint(1000,9999)}"

        qtd_membros = st.number_input("👥 Quantidade de Membros",
                                       min_value=1, step=1, 
                                       value=st.session_state.input_user["qtd_membros"])

        complexidade_media = st.number_input("⚙️ Complexidade Média (0-100)",
                                              min_value=0.0, max_value=100.0, 
                                              value=st.session_state.input_user["complexidade_media"], 
                                              step=1.0)

        cartoes_previstos = st.number_input("🗂️ Cartões previstos (número de cartões/tarefas)", 
                                            min_value=0.0, 
                                            step=1.0, 
                                            value=st.session_state.input_user["cartoes_previstos"])

    with col2:

        tipo_dominio = st.selectbox("🌐 Tipo de Tecnologia", 
                                    options=["Web", "Mobile", "API", "Dados"], 
                                    index=["Web","Mobile","API","Dados"]
                                    .index(st.session_state.input_user["tipo_dominio"]))

        # produtividade_estimada = st.number_input("📈 Produtividade Estimada (%)", min_value=0.0, max_value=1000.0, value=st.session_state.input_user["produtividade_estimada"], step=1.0)

        story_point = st.number_input("📊 Story points previstos para a sprint",
                                       min_value=0.0, max_value=1000.0, 
                                       value=st.session_state.input_user["story_points_previstos"], 
                                       step=1.0)

        percentual_bugs = st.number_input("🐞 Percentual de bugs (0-1)", 
                                          min_value=0.0, max_value=1.0, 
                                          value=st.session_state.input_user["percentual_bugs"], 
                                          step=1.0)

        percentual_retrabalho = st.number_input("🔁 Percentual de retrabalho (0-1)", 
                                                min_value=0.0, max_value=1.0, 
                                                value=st.session_state.input_user["percentual_retrabalho"], 
                                                step=1.0)
        
    produtividade_estimada = round(story_point / qtd_membros, 2)

    # Atualiza o input_user no session_state
    st.session_state.input_user = {
        "sprint_id": sprint_id,
        "qtd_membros": qtd_membros,
        "complexidade_media": complexidade_media,
        "tipo_dominio": tipo_dominio,
        "produtividade_estimada": produtividade_estimada,
        "story_points_previstos": story_point,
        "cartoes_previstos": cartoes_previstos,
        "percentual_bugs": percentual_bugs,
        "percentual_retrabalho": percentual_retrabalho
    }

    c1, c2 = st.columns([1,1])



with c2:
   
    empty, b1, b2 = st.columns([0.4, 1, 1])

    with b1:
        usar = st.button("✅ Adiconar Sprint", use_container_width=True)
    with b2:
        resetar = st.button("🔄 Resetar formulário", use_container_width=True)

    if usar:
        df = pd.DataFrame([st.session_state.input_user])
        numeric_cols = [
            "qtd_membros",
            "complexidade_media",
            "produtividade_estimada",
            "story_points_previstos",
            "cartoes_previstos",
            "percentual_bugs",
            "percentual_retrabalho"
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
        
        df = pd.concat([st.session_state.data, df], ignore_index=True) if st.session_state.get("data") is not None else df # Adicona novas sprints ao DataFrame existente ou cria novo

        st.session_state.data = df.copy()
        st.success("✅ Dados adicionados com sucesso!")
        st.session_state.last_source = "form"

    if resetar:
        st.session_state.input_user = {
            "sprint_id": f"sprint_{np.random.randint(1000,9999)}",
            "qtd_membros": 1,
            "complexidade_media": 0.0,
            "tipo_dominio": "Web",
            "produtividade_estimada": 0.0,
            "story_points_previstos": 0.0,
            "cartoes_previstos": 0.0,
            "percentual_bugs": 0.0,
            "percentual_retrabalho": 0.0
        }
        st.session_state.data = None
        st.info("🧹 Formulário resetado!")

st.markdown("---")
        

# --- depois do upload do arquivo ---

if st.session_state.get("data") is not None:

    if st.button("🧹 Limpar dados") and st.session_state.data is not None:
        st.session_state.data = None
        st.session_state.last_source = None
        st.success("Dados limpos com sucesso!")

    if "last_source" in st.session_state and st.session_state.last_source is not None:
        st.info(f"📂 Origem atual dos dados: **{st.session_state.last_source.upper()}**")
    else:
        st.info(f"📂 Sem dados carregados no momento") 


if "data" in st.session_state and st.session_state.data is not None and not st.session_state.data.empty:


    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Dados", "📈 Estimativas", "📊 Visualizações"])

    # -----------------------------------------------------
    # TAB 1 — VISUALIZAÇÃO DE DADOS
    # -----------------------------------------------------
    with tab1:
        st.subheader("📋 Pré-visualização dos dados")

        # Define as colunas esperadas dinamicamente
        columns = [
            col for col in [
                "sprint_id",
                "tipo_dominio",
                "qtd_membros",
                "story_points_previstos",
                "complexidade_media",
                "percentual_bugs",
                "cartoes_previstos",
                "percentual_retrabalho",  
            ] if col in st.session_state.data.columns
        ]

        #columns = st.session_state.data.columns

        if len(columns) > 0:
            st.dataframe(st.session_state.data[columns].head(50))
            st.caption(f"Total de registros: **{len(st.session_state.data)}**")
        else:
            st.warning("⚠️ Nenhuma coluna reconhecida foi encontrada nos dados.")

    # -----------------------------------------------------
    # TAB 2 — ESTIMATIVA
    # -----------------------------------------------------
    with tab2:
        st.subheader("⚡ Fazer Estimativa")

        if st.button("🚀 Calcular Produtividade Prevista", key="calc_estimativa"):
            try:
                df_input = st.session_state.data.copy()

                # Verifica colunas mínimas do pipeline
                required_pipeline_cols = [
                    "qtd_membros", "complexidade_media", "tipo_dominio",
                    "produtividade_estimada", "story_points_previstos",
                    "cartoes_previstos", "percentual_bugs", "percentual_retrabalho"
                ]

                missing = [c for c in required_pipeline_cols if c not in df_input.columns]

                if missing:
                    st.error(f"❌ Colunas faltando para o pipeline: {', '.join(missing)}")

                else:
                    # Tudo ok: preprocessa e prevê
                    processed_data = preprocess_input(df_input.copy(), scaler, label_encoder)

                    predictions = model.predict(processed_data)
                    st.session_state.data["produtividade_prevista"] = predictions

                    st.success("✅ Estimativas calculadas com sucesso!")

                    # Mostra pré-visualização das primeiras 5 sprints com produtividade prevista
                    st.session_state.data["semanas_estimadas"]  = st.session_state.data["produtividade_prevista"] / 7.0
                    st.session_state.data["semanas_estimadas"] = st.session_state.data["semanas_estimadas"].apply(math.ceil)

                    preview = st.session_state.data[["sprint_id", "produtividade_prevista", "semanas_estimadas"]].head(5).copy()

                    st.markdown("### 📈 Produtividade Prevista das Primeiras Sprints")

                    # Cria uma coluna visual de barras (mini indicador)
                    preview["Escala de produtividade"] = (
                        preview["produtividade_prevista"]
                        .apply(lambda x: "█" * int(x / preview["produtividade_prevista"].max() * 20))
                    )

                    # Exibe a tabela estilizada
                    st.dataframe(
                        preview.style.format(
                            {"produtividade_prevista": "{:.2f}"}
                        ).set_table_styles(
                            [
                                {"selector": "th", "props": [("text-align", "center"), ("background-color", "#0E1117"), ("color", "white")]},
                                {"selector": "td", "props": [("text-align", "center")]},
                            ]
                        ),
                        use_container_width=True
                    )

                    st.markdown("""
                        #### ℹ️ Informações adicionais  

                        Aqui está o que cada coluna representa, de forma simples:

                        - **Produtividade Prevista:** mostra a **estimativa de produtividade** calculada pelo *Agile Estimator*, considerando uma jornada de **8 horas úteis por dia**.  
                        - **Semanas Estimadas:** indica o **tempo total previsto para concluir a sprint**, em **semanas**, sempre **arredondado para cima** para garantir uma margem de segurança.  
                        - **Escala de Produtividade:** oferece uma **visão comparativa rápida** entre as sprints, mostrando o **tempo relativo de duração** de cada uma.  

                        Essas informações ajudam a **interpretar os resultados** de forma prática e entender **como o modelo projeta o ritmo de trabalho do time**.
                        """)


                    csv = st.session_state.data[["sprint_id", "produtividade_prevista", "semanas_estimadas"]].to_csv(index=False).encode("utf-8")

                    st.download_button("📥 Baixar resultados", data=csv, file_name="estimativas_produtividade_dias.csv", mime="text/csv")

            except Exception as e:
                st.exception(e)  # mostra stacktrace legível no Streamlit

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

                min_val = float(data["produtividade_prevista"].min())
                max_val = float(data["produtividade_prevista"].max())

                # Corrige caso todos os valores sejam iguais
                if min_val == max_val:
                    max_val += 0.001  # margem mínima para o slider não quebrar

                range_filter = st.slider(
                    "Intervalo da Produtividade Prevista",
                    min_value=min_val,
                    max_value=max_val,
                    value=st.session_state.range_filter,
                    key="range_filter",
                )


                dominio_filter = st.multiselect(
                    "Selecione a(s) Tecnologia(s)",
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
                st.caption("Mostra quantas vezes cada nível de produtividade aparece, separado por Tecnologia. Útil para enxergar a distribuição geral.")

                hist_chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X("produtividade_prevista:Q", bin=alt.Bin(maxbins=20), title="Produtividade Prevista"),
                    y=alt.Y("count()", title="Frequência"),
                    color= alt.Color("tipo_dominio:N", title="Tecnologia"),
                    tooltip=["count()", "tipo_dominio"]
                ).properties(width=600, height=400)

                st.altair_chart(hist_chart, use_container_width=True)

                # Boxplot

                st.subheader("📦 Boxplot por Tecnologia")
                st.caption("Mostra como a produtividade prevista varia em cada Tecnologia, incluindo valores médios e pontos fora do padrão.")

                box_plot = alt.Chart(chart_data).mark_boxplot().encode(
                    x="tipo_dominio:N", 
                    y=alt.Y("produtividade_prevista:Q", title="Produtividade Prevista"),
                    color= alt.Color("tipo_dominio:N", title="Tecnologia"),
                    tooltip=["tipo_dominio", "produtividade_prevista"]
                ).properties(width=600, height=400)
                st.altair_chart(box_plot, use_container_width=True)

                # Barras (média)   

                st.subheader("📊 Produtividade Média por Tamanho da Equipe")
                st.caption("Compara a produtividade média de acordo com o número de membros do time. Ajuda a entender como o tamanho da equipe influencia.")

                bar_chart = alt.Chart(chart_data).mark_bar().encode(
                    x="qtd_membros:N",
                    y=alt.Y("mean(produtividade_prevista):Q", title="Produtividade Média Prevista"),
                    color= alt.Color("tipo_dominio:N", title="Tecnologia"),
                    tooltip=[
                        "qtd_membros",
                        alt.Tooltip("mean(produtividade_prevista):Q", title="Produtividade Média"),
                        "tipo_dominio",
                    ],
                ).properties(width=600, height=400)
                st.altair_chart(bar_chart, use_container_width=True)

                st.subheader("🥧 Participação dos Tecnologias")
                st.caption("Mostra a proporção de produtividade média de cada Tecnologia em relação ao total. Facilita a comparação entre áreas.")

                pie_data = (
                    chart_data.groupby("tipo_dominio")["produtividade_prevista"]
                    .mean()
                    .reset_index()
                )

                pie_chart = alt.Chart(pie_data).mark_arc().encode(
                    theta="produtividade_prevista",
                    color= alt.Color("tipo_dominio:N", title="Tecnologia"),
                    tooltip=["tipo_dominio", "produtividade_prevista"],
                )
                st.altair_chart(pie_chart, use_container_width=True)

                # Linha

                st.subheader("📈 Evolução da Produtividade por Sprint")
                st.caption("Acompanha como a produtividade prevista muda ao longo das sprints. Ajuda a identificar tendências de crescimento ou queda.")

                line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                    x=alt.X("sprint_id:N", sort=list(chart_data["sprint_id"]), title="Sprint"),
                    y=alt.Y("produtividade_prevista:Q", title="Produtividade Prevista"),
                    color= alt.Color("tipo_dominio:N", title="Tecnologia"),
                    tooltip=["sprint_id", "produtividade_prevista", "tipo_dominio"]
                ).properties(width=600, height=400)
                st.altair_chart(line_chart, use_container_width=True)


                st.subheader("⚖️ Relação entre Produtividade, Bugs e Retrabalho")
                st.caption("Mostra se existe ligação entre produtividade, quantidade de bugs e retrabalho. Posição mais à direita indica maior produtividade; mais acima indica mais bugs.")

                scatter_chart = alt.Chart(chart_data).mark_circle(size=60).encode(
                    x=alt.X("produtividade_prevista:Q", title="Produtividade Prevista"),
                    y=alt.Y("percentual_bugs:Q", title="Percentual de Bugs (%)"),
                    color= alt.Color("tipo_dominio:N", title="Tecnologia"),
                    tooltip=[
                        alt.Tooltip("percentual_bugs:Q", title="Percentual de Bugs (%)"),
                        alt.Tooltip("percentual_retrabalho:Q", title="Percentual de Retrabalho (%)"),
                        alt.Tooltip("produtividade_prevista:Q", title="Produtividade Prevista"),
                        "tipo_dominio",
                    ]
                ).properties(width=600, height=400)
                st.altair_chart(scatter_chart, use_container_width=True)
            else:
                st.warning("⚠️ Por favor, calcule as estimativas primeiro na aba 'Estimativas'.")




 

# -------------------------------
# FAQ lateral
# -------------------------------
st.sidebar.title("ℹ️ FAQ")
# st.sidebar.button(on_click=close, label="🔄 Recarregar App")

st.sidebar.markdown("""
**O que é este aplicativo?**  
Um estimador de produtividade de equipes ágeis utilizando técnicas de Inteligência Artificial.  

**Como usar?**  
1. Carregue seus dados.  
2. Clique em **Fazer Estimativa**.  
3. Explore as visualizações interativas.  
4. Baixe os resultados.  

""")

st.markdown("---")
st.caption("Agile Estimator 0.0.1 — © 2025 Todos os direitos reservados.")
