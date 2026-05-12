import joblib
import os

MODEL_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "artifacts", "model")
)

def get_latest_model():
    files = [f for f in os.listdir(MODEL_DIR) if f.endswith(".pkl")]
    
    if not files:
        raise FileNotFoundError("No model found")

    latest = max(files, key=lambda x: os.path.getctime(os.path.join(MODEL_DIR, x)))
    
    return os.path.join(MODEL_DIR, latest)


def load_model():
    model_path = get_latest_model()
    print(f"Loading model from {model_path}...")
    
    return joblib.load(model_path)