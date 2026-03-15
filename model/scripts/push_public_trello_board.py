import pandas as pd
import requests

def push_cards_to_trello(df, board_id, key, token):
    """
    Recebe DataFrame e cria cards no Trello.
    df deve ter colunas: list_name, card_name, card_desc (opcional), card_due (opcional)
    """
    # 1. Obter listas existentes do board
    
    lists_url = f"https://api.trello.com/1/boards/{board_id}/lists"
    params = {"key": key, "token": token}
    response = requests.get(lists_url, params=params)
    response.raise_for_status()
    existing_lists = response.json()

    # Mapear listas existentes
    list_map = {lst["name"]: lst["id"] for lst in existing_lists}

    for _, row in df.iterrows():
        list_name = row["list_name"]

        # Criar lista se não existir
        if list_name not in list_map:
            create_list_url = f"https://api.trello.com/1/boards/{board_id}/lists"
            list_data = {"name": list_name, "key": key, "token": token}
            res = requests.post(create_list_url, data=list_data)
            res.raise_for_status()
            list_id = res.json()["id"]
            list_map[list_name] = list_id
        else:
            list_id = list_map[list_name]

        # Criar o card
        card_url = "https://api.trello.com/1/cards"
        card_data = {
            "idList": list_id,
            "name": row["card_name"],
            "desc": row.get("card_desc", ""),
            "key": key,
            "token": token
        }
        if "card_due" in row and pd.notna(row["card_due"]):
            card_data["due"] = row["card_due"]

        r = requests.post(card_url, data=card_data)
        r.raise_for_status()

    print("✅ Todos os cards do DataFrame foram criados no Trello")


# ----------------- MAIN -----------------
# Lê seu CSV
df = pd.read_csv("sprints_teste_2.csv")
df = df.loc[10,::]

# Adaptar as colunas do CSV pro formato do Trello
# Aqui estou supondo que você tem: sprint_id, tipo_dominio, produtividade_prevista, qtd_membros, percentual_bugs, percentual_retrabalho
df_trello = pd.DataFrame({
    "list_name": df["sprint_id"],  # cada sprint vira uma lista
    "card_name": df["tipo_dominio"],  # nome do card = domínio
    "card_desc": (
        "Produtividade Prevista: " + df["produtividade_prevista"].astype(str) +
        "\nMembros: " + df["qtd_membros"].astype(str) +
        "\n% Bugs: " + df["percentual_bugs"].astype(str) +
        "\n% Retrabalho: " + df["percentual_retrabalho"].astype(str)
    )
})

# Seu board_id (peguei da URL)
board_id = "abc" 

# Sua chave e token (precisa gerar em https://trello.com/app-key)

trello_key = 123
trello_token = 123

# Subir os cards
push_cards_to_trello(df_trello, board_id, trello_key, trello_token)
