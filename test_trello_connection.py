# Consulta simples ao board do Trello
import os
from dotenv import load_dotenv
import requests

# Carrega as variáveis do .env
load_dotenv()

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("BOARD_ID")

# Endpoint da API para obter listas do board
url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
params = {
    "key": TRELLO_KEY,
    "token": TRELLO_TOKEN
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()  # Lança erro para códigos 4xx e 5xx

    listas = response.json()

    print("✅ Consulta bem-sucedida!")
    print("📋 Listas encontradas no board:\n")
    for lista in listas:
        print(f"- {lista['name']} (ID: {lista['id']})")

except requests.exceptions.HTTPError as http_err:
    print(f"❌ Erro HTTP: {http_err} - Código: {response.status_code}")
except requests.exceptions.RequestException as req_err:
    print(f"❌ Erro na requisição: {req_err}")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
