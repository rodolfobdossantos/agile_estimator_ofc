import re
import requests
import pandas as pd

# Trello field name aliases → canonical model column names
_FIELD_ALIASES = {
    "function_points": "function_points",
    "function points": "function_points",
    "performance_requirements": "performance_requirements",
    "performance requirements": "performance_requirements",
    "complex_processing": "complex_processing",
    "complex processing": "complex_processing",
    "installation_ease": "installation_ease",
    "instalation_ease": "installation_ease",
    "instalation ease": "installation_ease",
    "installation ease": "installation_ease",
    "additional_complexity_factor": "additional_complexity_factor",
    "aditional_complexity_factor": "additional_complexity_factor",
    "aditional complexity factor": "additional_complexity_factor",
    "additional complexity factor": "additional_complexity_factor",
}

REQUIRED_COLUMNS = [
    "function_points",
    "performance_requirements",
    "complex_processing",
    "installation_ease",
    "additional_complexity_factor",
]


def _resolve_field_name(raw_name: str) -> str | None:
    return _FIELD_ALIASES.get(raw_name.strip().lower())


def get_trello_cards_public(url: str) -> pd.DataFrame:
    """
    Fetches cards from a public Trello board and returns a DataFrame
    with the 5 model features extracted from custom fields.

    Expects the board to have custom fields named (case-insensitive):
      - function_points
      - performance_requirements
      - complex_processing
      - installation_ease (also accepts 'instalation_ease')
      - additional_complexity_factor (also accepts 'aditional...')
    """
    match = re.match(r"^https://trello\.com/b/([a-zA-Z0-9]+)/?.*$", url)
    if not match:
        raise ValueError(
            "Link inválido! Formato esperado: https://trello.com/b/<BOARD_ID>"
        )

    board_id = match.group(1)

    response = requests.get(f"https://trello.com/b/{board_id}.json", timeout=15)
    response.raise_for_status()
    data = response.json()

    # Build field_id → canonical_name mapping
    field_map: dict[str, str] = {}
    for cf in data.get("customFields", []):
        canonical = _resolve_field_name(cf.get("name", ""))
        if canonical:
            field_map[cf["id"]] = canonical

    rows = []
    for card in data.get("cards", []):
        if card.get("closed"):
            continue

        row: dict = {"project_id": card.get("name", "")}

        for item in card.get("customFieldItems", []):
            canonical = field_map.get(item.get("idCustomField"))
            if canonical is None:
                continue
            value = item.get("value", {})
            if "number" in value:
                try:
                    row[canonical] = float(value["number"])
                except (TypeError, ValueError):
                    pass

        rows.append(row)

    df = pd.DataFrame(rows)

    # Ensure all required columns exist (fill missing with NaN)
    for col in ["project_id"] + REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = float("nan")

    return df[["project_id"] + REQUIRED_COLUMNS]
