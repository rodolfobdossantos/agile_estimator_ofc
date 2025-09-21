import streamlit as st
import pandas as pd
import numpy as np
import pickle
import joblib
import altair as alt

# -------------------------------
# Funções auxiliares
# -------------------------------
def preprocess_input(data, scaler, label_encoder):
    data['tipo_dominio'] = label_encoder.transform(data['tipo_dominio'])
    
    columns_to_scale = ['produtividade_estimada', 'story_points_previstos']
    data[columns_to_scale] = scaler.transform(data[columns_to_scale])

    data["qtd_bugs"] = data["percentual_bugs"] * data["cartoes_previstos"]
    data["qtd_retrabalho"] = data["percentual_retrabalho"] * data["cartoes_previstos"]

    data["carga_cartoes_por_membro"] = data["cartoes_previstos"] / data["qtd_membros"]
    data["carga_storypoints_por_membro"] = data["story_points_previstos"] / data["qtd_membros"]
    data["eficiencia"] = data["velocidade_passada"] / data["cartoes_previstos"]
    data["complexidade_total"] = data["complexidade_media"] * data["cartoes_previstos"]
    data["produtividade_gap"] = (data["velocidade_passada"] / data["qtd_membros"]) - data["produtividade_estimada"]

    return data[['qtd_membros', 'cartoes_previstos',
       'story_points_previstos', 'tipo_dominio', 'complexidade_media',
       'percentual_bugs', 'percentual_retrabalho', 'velocidade_passada',
       'produtividade_estimada', 'qtd_bugs', 'qtd_retrabalho',
       'carga_cartoes_por_membro', 'carga_storypoints_por_membro',
       'eficiencia', 'complexidade_total', 'produtividade_gap']]

def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)

# -------------------------------
# Carregar modelo e transformadores
# -------------------------------
model = load_model('../model/agile_estimator.pkl')
scaler = joblib.load('../scaler/standard_scaler_produtividade_estimada_story_points_previstos.pkl')
label_encoder = joblib.load('../encoder/label_encoder_tipo_dominio.pkl')

# -------------------------------
# Interface principal
# -------------------------------
st.set_page_config(page_title="Agile Estimator", layout="wide")
st.title("🚀 Agile Estimator")
st.write("Estimativa de produtividade baseada em dados históricos do Trello.")

uploaded_file = st.file_uploader("📂 Carregue seu arquivo CSV", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.success("✅ Dados carregados com sucesso!")

    # Tabs para organizar
    tab1, tab2, tab3 = st.tabs(["📋 Dados", "📈 Estimativas", "📊 Visualizações"])

    with tab1:
        st.subheader("Pré-visualização dos dados")
        st.dataframe(data.head(50))  # Mostra só 50 linhas

    with tab2:
        if st.button("⚡ Fazer Estimativa"):
            try:
                processed_data = preprocess_input(data.copy(), scaler, label_encoder)
                predictions = model.predict(processed_data)
                
                # 🔑 nome único para a previsão do modelo
                data['produtividade_prevista'] = predictions  

                st.success("✅ Estimativas calculadas!")
                st.dataframe(data.head(50))

                # Download do CSV com a nova coluna
                csv = data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar resultados",
                    data=csv,
                    file_name='estimativas_produtividade.csv',
                    mime='text/csv'
                )
            except Exception as e:
                st.error(f"Erro ao processar os dados: {e}")

    with tab3:
        if 'produtividade_estimativa' in data.columns:
            st.subheader("🔎 Filtros")

            # Filtros dinâmicos
            max_val = float(data['produtividade_estimativa'].max())
            min_val = float(data['produtividade_estimativa'].min())
            range_filter = st.slider("Intervalo da produtividade", min_val, max_val, (min_val, max_val))

            dominios = data['tipo_dominio'].unique()
            dominio_filter = st.multiselect("Selecione o(s) domínio(s)", dominios, default=dominios)

            filtered_data = data[
                (data['produtividade_estimativa'] >= range_filter[0]) &
                (data['produtividade_estimativa'] <= range_filter[1]) &
                (data['tipo_dominio'].isin(dominio_filter))
            ]

            st.write(f"Mostrando **{len(filtered_data)} registros** após filtros.")

            # Amostragem para não travar o gráfico
            if len(filtered_data) > 500:
                chart_data = filtered_data.sample(500, random_state=42)
            else:
                chart_data = filtered_data

            # Gráfico de barras
           # Gráfico de barras
            bar_chart = alt.Chart(chart_data).mark_bar().encode(
                x='qtd_membros:N',
                y='produtividade_prevista:Q',
                color='tipo_dominio:N',
                tooltip=['qtd_membros', 'produtividade_prevista', 'tipo_dominio']
            ).properties(width=600, height=400)

            st.altair_chart(bar_chart, use_container_width=True)

            # Gráfico de pizza
            pie_data = chart_data.groupby('tipo_dominio')['produtividade_prevista'].mean().reset_index()
            pie_chart = alt.Chart(pie_data).mark_arc().encode(
                theta='produtividade_prevista',
                color='tipo_dominio',
                tooltip=['tipo_dominio', 'produtividade_prevista']
            )
            st.altair_chart(pie_chart, use_container_width=True)


# -------------------------------
# FAQ lateral
# -------------------------------
st.sidebar.title("ℹ️ FAQ")
st.sidebar.markdown("""
**O que é este aplicativo?**  
Um estimador de produtividade de equipes ágeis com base em dados históricos do Trello.  

**Como usar?**  
1. Carregue seu CSV.  
2. Clique em **Fazer Estimativa**.  
3. Explore as visualizações interativas.  
4. Baixe os resultados.  

**Colunas necessárias no CSV:**  
- qtd_membros  
- cartoes_previstos  
- story_points_previstos  
- tipo_dominio  
- complexidade_media  
- percentual_bugs  
- percentual_retrabalho  
- velocidade_passada  
- produtividade_estimada  
""")

st.markdown("---")
st.caption("Agile Estimator 0.1 — © 2024 Todos os direitos reservados.")
