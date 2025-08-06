import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Lê o CSV
df = pd.read_csv("sprints_simuladas.csv")

print(df.columns.tolist())

with PdfPages("apresentacao_sprints.pdf") as pdf:

    # Dimensionamento das figuras
    fig, ax = plt.subplots(figsize=(18, 5))  
    ax.axis('tight')
    ax.axis('off')

    tabela = ax.table(
        cellText=df.head(10).values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center'
    )

    tabela.auto_set_font_size(False)
    tabela.set_fontsize(9)
    tabela.scale(2.0, 1.7)

    # Ajustar largura de colunas manualmente (fração do total)
    col_widths = [0.1, 0.11, 0.11, 0.07, 0.07, 0.09, 0.09, 0.11, 0.11, 0.09, 0.09, 0.09, 0.11, 0.11, 0.13]
    for i, width in enumerate(col_widths):
        for key, cell in tabela.get_celld().items():
            if key[1] == i:
                cell.set_width(width)

    fig.suptitle("Preview das 10 primeiras sprints", fontsize=16, fontweight='bold', y=0.95)

    # Garantie que o bbox seja tight pra evitar cortes laterais
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)

    # Gráfico 1 > story_points_previstos × entregues
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df["story_points_previstos"], df["story_points_entregues"], c='blue')
    ax.set_xlabel("Story Points Previstos")
    ax.set_ylabel("Story Points Entregues")
    ax.set_title("Dispersão: Story Points Previstos × Entregues")
    pdf.savefig(fig)
    plt.close(fig)

    #Gráfico 2 > complexidade × percentual de retrabalho
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df["complexidade_media"], df["percentual_retrabalho"], c='green')
    ax.set_xlabel("Complexidade Média")
    ax.set_ylabel("Percentual de Retrabalho")
    ax.set_title("Dispersão: Complexidade Média × Percentual de Retrabalho")
    pdf.savefig(fig)
    plt.close(fig)

    #Gráfico 3 > velocidade_passada × produtividade_estimada
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df["velocidade_passada"], df["produtividade_estimada"], c='red')
    ax.set_xlabel("Velocidade Passada")
    ax.set_ylabel("Produtividade Estimada")
    ax.set_title("Dispersão: Velocidade Passada × Produtividade Estimada")
    pdf.savefig(fig)
    plt.close(fig)

print("✅ PDF com preview e gráficos gerado: apresentacao_sprints.pdf")
