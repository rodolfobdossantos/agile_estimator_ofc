import pandas as pd
import random
from datetime import timedelta, date
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

# Gera o intervalo de datas para uma sprint de duração fixa
def gerar_datas_sprint(inicio, duracao_dias=14):
    data_inicio = inicio
    data_fim = inicio + timedelta(days=duracao_dias)
    return data_inicio, data_fim

# Gera dados sintéticos e realistas para uma sprint fictícia
def gerar_sprint(sprint_num, data_inicio, duracao_min=10, duracao_max=21):
    duracao_dias = random.randint(duracao_min, duracao_max)
    data_ini, data_fim = gerar_datas_sprint(data_inicio, duracao_dias=duracao_dias)
    qtd_membros = random.randint(3, 7)
    
    base_story_points = random.randint(5, 10)
    story_points_prev = int(base_story_points * duracao_dias * qtd_membros)
    story_points_entregue = int(story_points_prev * random.uniform(0.7, 1.0))
    
    cartoes_prev = random.randint(20, 50)
    cartoes_entregue = int(cartoes_prev * random.uniform(0.7, 1.0))
    
    tipo_dominio = random.choice(["Web", "Mobile", "API", "Dados"])
    complexidade = round(random.uniform(1.5, 4.5), 1)
    
    percentual_bugs = round(random.uniform(0.05, 0.25) + 0.02 * (complexidade - 2.5), 2)
    percentual_retrabalho = round(random.uniform(0.05, 0.2) + 0.02 * (complexidade - 2.5), 2)

    return {
        "sprint_id": f"Sprint_{sprint_num:02}",
        "tipo_dominio": tipo_dominio,
        "qtd_membros": qtd_membros,
        "story_points_previstos": story_points_prev,
        "complexidade_media": complexidade,
        "percentual_bugs": percentual_bugs,
        "cartoes_previstos": cartoes_prev,
        "percentual_retrabalho": percentual_retrabalho,
    }

# Função principal que gera N sprints e salva os dados em CSV e XLSX
def gerar_dataset_sprints(qtd_sprints=5, path_csv="sprints_simuladas.csv", path_excel="sprints_formatadas.xlsx"):
    dados = []
    data_base = date(2025, 1, 1)

    for i in range(qtd_sprints):
        sprint = gerar_sprint(i + 1, data_base)
        dados.append(sprint)
        data_base = data_base + timedelta(days=random.randint(15, 25))

    df = pd.DataFrame(dados)

    # Ordena as colunas no padrão esperado pelo app
    colunas_ordenadas = [
        "sprint_id",
        "tipo_dominio",
        "qtd_membros",
        "story_points_previstos",
        "complexidade_media",
        "percentual_bugs",
        "cartoes_previstos",
        "percentual_retrabalho",
    ]
    df = df[colunas_ordenadas]

    # Salva em CSV (limpo e padronizado)
    df.to_csv(path_csv, index=False)

    # Salva em Excel com cabeçalhos em negrito
    with pd.ExcelWriter(path_excel, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Sprints", index=False)
        sheet = writer.sheets["Sprints"]
        for col_num, column_title in enumerate(df.columns, 1):
            cell = sheet[f"{get_column_letter(col_num)}1"]
            cell.font = Font(bold=True)

    print("Arquivos gerados com sucesso:")
    print(f"  - {path_csv} (CSV simples)")
    print(f"  - {path_excel} (Excel com formatação)")

# Executa a função principal
if __name__ == "__main__":
    gerar_dataset_sprints(qtd_sprints=100, path_csv="sprints_teste_2.csv", path_excel="sprints_teste.xlsx")
