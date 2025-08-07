import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("BOARD_ID")

# Função genérica de GET com tratamento
def trello_get(url, params):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

# Parâmetros básicos
params = {
    "key": TRELLO_KEY,
    "token": TRELLO_TOKEN
}

# Obter dados do board
board_url = f"https://api.trello.com/1/boards/{BOARD_ID}"
board_data = trello_get(board_url, params)

if board_data:
    board_name = board_data.get("name")
    board_id = board_data.get("id")

    # Obter listas do board
    lists_url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
    listas = trello_get(lists_url, params)

    registros = []

    if listas:
        for lista in listas:
            registros.append({
                "board_name": board_name,
                "board_id": board_id,
                "list_name": lista.get("name"),
                "list_id": lista.get("id")
            })

        # Criar DataFrame
        df = pd.DataFrame(registros)

        # Salvar como CSV
        df.to_csv("listas_boards.csv", index=False, encoding="utf-8-sig")

        print("✅ CSV salvo com sucesso: listas_boards.csv")
    else:
        print("⚠️ Nenhuma lista encontrada no board.")
else:
    print("❌ Falha ao obter dados do board.")
