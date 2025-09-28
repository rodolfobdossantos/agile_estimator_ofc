import re
import requests
import pandas as pd

def get_trello_cards_public(url: str) -> pd.DataFrame:
    """
    Recebe link público do Trello e retorna um DataFrame com cards e listas.
    Funciona sem autenticação (somente boards públicos).
    """
    # Regex para validar link público do Trello
    public_regex = r"^https://trello\.com/b/([a-zA-Z0-9]+)/?.*$"
    match = re.match(public_regex, url)
    
    if not match:
        raise ValueError("Link inválido! Formato esperado: https://trello.com/b/<BOARD_ID>/<BOARD_NAME>")

    board_id = match.group(1)
    print(f" Board ID detectado: {board_id}")

    try:
        # 1. Obter listas do board público
        lists_url = f"https://trello.com/b/{board_id}.json"
        response = requests.get(lists_url)
        response.raise_for_status()
        data = response.json()

        # O JSON do Trello público contém listas e cards
        lists = {lst["id"]: lst["name"] for lst in data["lists"]}
        all_cards = []

        for card in data["cards"]:
            list_name = lists.get(card.get("idList"), "Unknown")
            card_data = {
                "list_id": card.get("idList"),
                "list_name": list_name,
                "card_id": card.get("id"),
                "card_name": card.get("name"),
                "card_url": f"https://trello.com/c/{card.get('shortLink')}",
                "card_due": card.get("due"),
                "card_labels": ", ".join([label.get("name", "") for label in card.get("labels", [])]),
            }
            all_cards.append(card_data)

        df = pd.DataFrame(all_cards)
        return df

    except requests.exceptions.RequestException as err:
        print(f"Erro na requisição: {err}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return pd.DataFrame()


get_trello_cards_public("https://trello.com/b/DKf6KNh2/testeagileestimator")
