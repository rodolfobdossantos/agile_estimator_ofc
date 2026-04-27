from fastapi import FastAPI
import os
import pandas as pd
import time
from app.schemas import PredictionInput
from app.model_loader import load_model
from app.predict import make_prediction
from app.logger import get_logger

app = FastAPI()
logger = get_logger()

model = load_model()


@app.get("/health")
def health_check():
    start_time = time.time()

    checks = {}

    # 1. modelo carregado
    try:
        if model is None:
            raise Exception("Model is None")
        checks["model_loaded"] = True
    except Exception as e:
        checks["model_loaded"] = False
        checks["model_error"] = str(e)

    # 2. arquivo existe
    try:
        from app.model_loader import get_latest_model
        model_path = get_latest_model()

        checks["model_file_exists"] = os.path.exists(model_path)
        checks["model_path"] = model_path
    except Exception as e:
        checks["model_file_exists"] = False
        checks["model_file_error"] = str(e)

    #  3. predição teste (sanity check)
    try:

        test_df = pd.DataFrame([{
            "function_points": 1,
            "PC1": 0.0,
            "PC2": 0.0
        }])

        pred = model.predict(test_df)

        checks["inference_ok"] = True
        checks["test_prediction"] = float(pred[0])
    except Exception as e:
        checks["inference_ok"] = False
        checks["inference_error"] = str(e)

    # 4. tempo de resposta
    checks["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

    # status geral
    status = "ok" if all([
        checks.get("model_loaded"),
        checks.get("model_file_exists"),
        checks.get("inference_ok")
    ]) else "degraded"

    return {
        "status": status,
        "checks": checks
    }

@app.post("/predict")
def predict(data: PredictionInput):
    try:
        result = make_prediction(model, data)

        logger.info(f"Prediction: {result}")

        return {
            "prediction": result
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": str(e)}