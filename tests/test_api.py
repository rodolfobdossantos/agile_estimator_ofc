import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ---------- /health ----------

def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200

def test_health_status_ok():
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"

def test_health_model_loaded():
    response = client.get("/health")
    checks = response.json()["checks"]
    assert checks["model_loaded"] is True

def test_health_inference_ok():
    response = client.get("/health")
    checks = response.json()["checks"]
    assert checks["inference_ok"] is True

def test_health_model_file_exists():
    response = client.get("/health")
    checks = response.json()["checks"]
    assert checks["model_file_exists"] is True

# ---------- /predict ----------

VALID_PAYLOAD = {
    "function_points": -0.029,   # (500 - 514.86) / 516.24
    "PC1": 0.52,
    "PC2": -0.31
}

def test_predict_returns_200():
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200

def test_predict_returns_prediction_key():
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert "prediction" in response.json()

def test_predict_returns_positive_hours():
    response = client.post("/predict", json=VALID_PAYLOAD)
    prediction = response.json()["prediction"]
    assert isinstance(prediction, float)
    assert prediction > 0

def test_predict_range_realistic():
    """Estimativa deve estar dentro do range plausível do dataset Maxwell (100h–50000h)."""
    response = client.post("/predict", json=VALID_PAYLOAD)
    prediction = response.json()["prediction"]
    assert 100 < prediction < 50_000

def test_predict_different_inputs_give_different_outputs():
    """Projetos com características distintas devem ter estimativas distintas."""
    small = client.post("/predict", json={"function_points": -1.0, "PC1": -1.0, "PC2": 0.0})
    large = client.post("/predict", json={"function_points": 1.0, "PC1": 1.0, "PC2": 0.0})
    assert small.json()["prediction"] != large.json()["prediction"]

def test_predict_larger_fp_gives_more_effort():
    """Coeficiente de function_points é positivo (+0.341), mais FP = mais esforço."""
    small = client.post("/predict", json={"function_points": -1.0, "PC1": 0.0, "PC2": 0.0})
    large = client.post("/predict", json={"function_points": 1.0, "PC1": 0.0, "PC2": 0.0})
    assert large.json()["prediction"] > small.json()["prediction"]

def test_predict_invalid_payload_missing_fields():
    """Payload sem PC1 e PC2 deve retornar 422 (Pydantic validation error)."""
    response = client.post("/predict", json={"function_points": -0.029})
    assert response.status_code == 422

def test_predict_invalid_payload_wrong_type():
    """Strings onde float é esperado devem retornar 422."""
    response = client.post("/predict", json={
        "function_points": "alto",
        "PC1": 0.52,
        "PC2": -0.31
    })
    assert response.status_code == 422

def test_predict_empty_payload():
    response = client.post("/predict", json={})
    assert response.status_code == 422
