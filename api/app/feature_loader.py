import json
import os

BASE_DIR = os.path.dirname(__file__)

FEATURES_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "artifacts", "metadata", "features.json")
)

print(f"Loading features from: {FEATURES_PATH}")

def load_features():
    with open(FEATURES_PATH, "r") as f:
        data = json.load(f)
    return data