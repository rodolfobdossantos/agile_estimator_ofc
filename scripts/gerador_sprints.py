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
    
    # Sorteia a duração da sprint entre min e max
    duracao_dias = random.randint(duracao_min, duracao_max)
    
    data_ini, data_fim = gerar_datas_sprint(data_inicio, duracao_dias=duracao_dias)
    
    qtd_membros = random.randint(3, 7)
    
    # Story points correlacionados com a duração da sprint
    base_story_points = random.randint(5, 10)  # ponto por membro por dia
    story_points_prev = int(base_story_points * duracao_dias * qtd_membros)
    story_points_entregue = int(story_points_prev * random.uniform(0.7, 1.0))
    
    cartoes_prev = random.randint(20, 50)
    cartoes_entregue = int(cartoes_prev * random.uniform(0.7, 1.0))
    
    tipo_dominio = random.choice(["Web", "Mobile", "API", "Dados"])
    complexidade = round(random.uniform(1.5, 4.5), 1)
    
    # Bugs e retrabalho aumentam levemente com a complexidade
    percentual_bugs = round(random.uniform(0.05, 0.25) + 0.02*(complexidade-2.5), 2)
    percentual_retrabalho = round(random.uniform(0.05, 0.2) + 0.02*(complexidade-2.5), 2)
    
    velocidade_passada = round(random.uniform(30, 70), 2)
    produtividade = round(story_points_prev / qtd_membros, 2)

    return {
        "sprint_id": f"Sprint_{sprint_num:02}",
        "data_inicio": data_ini,
        "data_fim": data_fim,
        "qtd_membros": qtd_membros,
        "duracao_dias": (data_fim - data_ini).days,
        "cartoes_previstos": cartoes_prev,
        "cartoes_entregues": cartoes_entregue,
        "story_points_previstos": story_points_prev,
        "story_points_entregues": story_points_entregue,
        "tipo_dominio": tipo_dominio,
        "complexidade_media": complexidade,
        "percentual_bugs": percentual_bugs,
        "percentual_retrabalho": percentual_retrabalho,
        "velocidade_passada": velocidade_passada,
        "produtividade_estimada": produtividade
    }

# Função principal que gera N sprints e salva os dados em .csv e .xlsx
def gerar_dataset_sprints(qtd_sprints=5, path_csv="sprints_simuladas.csv", path_excel="sprints_formatadas.xlsx"):
    dados = []
    data_base = date(2025, 1, 1)

    # Gera múltiplas sprints com datas sequenciais
    for i in range(qtd_sprints):
        sprint = gerar_sprint(i+1, data_base, duracao_min=10, duracao_max=21)
        dados.append(sprint)
        # Avança a data base para o dia seguinte ao fim da sprint atual
        data_base = sprint["data_fim"] + timedelta(days=1)

    # Cria o DataFrame com os dados
    df = pd.DataFrame(dados)

    # Salva em CSV (sem formatação)
    df.to_csv(path_csv, index=False)

    # Salva em Excel com formatação de cabeçalhos
    with pd.ExcelWriter(path_excel, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Sprints", index=False)
        sheet = writer.sheets["Sprints"]

        # Aplica negrito no cabeçalho
        for col_num, column_title in enumerate(df.columns, 1):
            cell = sheet[f"{get_column_letter(col_num)}1"]
            cell.font = Font(bold=True)

    print(f"Arquivos gerados com sucesso:")
    print(f"   - sprints_simuladas.csv (sem formatação)")
    print(f"   - sprints_formatadas.xlsx (com formatação)")

# Executa a função principal se for chamado diretamente
if __name__ == "__main__":
    gerar_dataset_sprints(qtd_sprints=100, path_csv="sprints_teste.csv", path_excel="sprints_teste.xlsx")
