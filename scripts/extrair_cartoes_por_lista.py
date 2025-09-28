import os
from dotenv import load_dotenv
import requests
import pandas as pd

def get_trello_cards(url: str) -> pd.DataFrame:
    # Carrega variáveis do .env
    load_dotenv()

    TRELLO_KEY = os.getenv("TRELLO_KEY")
    TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
    BOARD_ID = os.getenv("BOARD_ID")  

    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN
    }

    try:
        # 1. Mapear campos customizados
        custom_fields_url = f"https://api.trello.com/1/boards/{BOARD_ID}/customFields"
        custom_fields_response = requests.get(custom_fields_url, params=params)
        custom_fields_mapping = {}

        if custom_fields_response.status_code == 200:
            for field in custom_fields_response.json():
                custom_fields_mapping[field["id"]] = field["name"]
        else:
            print("⚠️ Falha ao obter campos customizados do board")

        # 2. Obter listas do board
        lists_url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
        lists_response = requests.get(lists_url, params=params)
        lists_response.raise_for_status()

        listas = lists_response.json()
        all_cards = []

        for lista in listas:
            list_id = lista["id"]
            list_name = lista["name"]

            # 3. Buscar cards da lista
            cards_url = f"https://api.trello.com/1/lists/{list_id}/cards"
            cards_params = {
                "key": TRELLO_KEY,
                "token": TRELLO_TOKEN,
                "fields": "id,name,url,due,labels",
                "members": "true",
                "member_fields": "id,username,fullName",
                "customFieldItems": "true",
                "actions": "commentCard",
                "actions_limit": 100
            }

            cards_response = requests.get(cards_url, params=cards_params)
            if cards_response.status_code != 200:
                continue

            for card in cards_response.json():
                card_data = {
                    "list_id": list_id,
                    "list_name": list_name,
                    "card_id": card.get("id"),
                    "card_name": card.get("name"),
                    "card_url": card.get("url"),
                    "card_due": card.get("due"),
                    "card_labels": ", ".join([label["name"] for label in card.get("labels", [])]),
                    "card_members": ", ".join([member["fullName"] for member in card.get("members", [])]),
                }

                # Campos customizados ['produtividade_estimada','tipo_dominio', 'complexidade_media', 'qtd_bugs', 'qtd_retrabalho','carga_cartoes_por_membro']

                for cfi in card.get("customFieldItems", []):
                    field_id = cfi.get("idCustomField")
                    field_name = custom_fields_mapping.get(field_id, f"custom_{field_id}")
                    value = cfi.get("value")
                    id_value = cfi.get("idValue")
                    value_final = None

                    if value:
                        value_final = list(value.values())[0]  # pode ser texto, número, etc.
                    elif id_value:
                        value_final = id_value

                    card_data[f"custom_{field_name}"] = value_final

                # Comentários (actions)
                actions = card.get("actions", [])
                card_data["card_comments"] = " | ".join(
                    [action["data"]["text"] for action in actions if "data" in action and "text" in action["data"]]
                )


                all_cards.append(card_data)

        # 4. Criar DataFrame e salvar CSV
        df = pd.DataFrame(all_cards)
        df.to_csv("cartoes_por_lista.csv", index=False, encoding="utf-8-sig")
        print("✅ Arquivo 'cartoes_por_lista.csv' gerado com sucesso!")

    except requests.exceptions.RequestException as err:
        print(f"❌ Erro na requisição: {err}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
