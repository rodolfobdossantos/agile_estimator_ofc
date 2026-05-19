import pytest
import joblib
import numpy as np
import pandas as pd
import os

SCALER_LIKERT = "api/artifacts/preprocessing/scaler_pca_features.pkl"
PCA_PATH      = "api/artifacts/preprocessing/pca_2.pkl"
SCALER_FP     = "api/artifacts/preprocessing/scaler_maxx.pkl"
MODEL_PATH    = "api/artifacts/model/agile_estimator_v2.pkl"

LIKERT_COLS = [
    "performance_requirements",
    "complex_processing",
    "installation_ease",
    "additional_complexity_factor",
]

SAMPLE_LIKERT = {
    "performance_requirements": 3,
    "complex_processing": 4,
    "installation_ease": 3,
    "additional_complexity_factor": 3,
}

@pytest.fixture(scope="module")
def artifacts():
    return {
        "scaler":    joblib.load(SCALER_LIKERT),
        "pca":       joblib.load(PCA_PATH),
        "scaler_fp": joblib.load(SCALER_FP),
        "model":     joblib.load(MODEL_PATH),
    }

# ---------- Artefatos ----------

def test_scaler_loaded(artifacts):
    assert artifacts["scaler"] is not None

def test_pca_loaded(artifacts):
    assert artifacts["pca"] is not None

def test_model_loaded(artifacts):
    assert artifacts["model"] is not None

# ---------- Parâmetros do scaler FP ----------

def test_fp_mean_correct(artifacts):
    fp_mean = float(artifacts["scaler_fp"].mean_[0])
    assert abs(fp_mean - 514.8596) < 1.0

def test_fp_scale_correct(artifacts):
    fp_scale = float(artifacts["scaler_fp"].scale_[0])
    assert abs(fp_scale - 516.2373) < 1.0

# ---------- Shapes do pipeline ----------

def test_scaler_output_shape(artifacts):
    X = pd.DataFrame([SAMPLE_LIKERT])[LIKERT_COLS].astype(float)
    result = artifacts["scaler"].transform(X)
    assert result.shape == (1, 4)

def test_pca_output_shape(artifacts):
    X = pd.DataFrame([SAMPLE_LIKERT])[LIKERT_COLS].astype(float)
    X_scaled = artifacts["scaler"].transform(X)
    result = artifacts["pca"].transform(X_scaled)
    assert result.shape == (1, 2)

# ---------- Modelo ----------

def test_model_coeficients_nonzero(artifacts):
    """Coeficientes Lasso não devem ser todos zero (bug do alpha=1.0)."""
    lasso = artifacts["model"].steps[-1][1]
    assert any(c != 0.0 for c in lasso.coef_), "Todos coeficientes são zero — modelo com bug!"

def test_model_alpha(artifacts):
    lasso = artifacts["model"].steps[-1][1]
    assert lasso.alpha < 1.0, f"Alpha={lasso.alpha} — modelo provavelmente re-fitado com default"

# ---------- Pipeline completo ponta a ponta ----------

def test_full_preprocessing_pipeline(artifacts):
    """Simula exatamente o que o Streamlit faz antes de chamar a API."""
    fp_raw = 500
    FP_MEAN  = float(artifacts["scaler_fp"].mean_[0])
    FP_SCALE = float(artifacts["scaler_fp"].scale_[0])
    fp_std = (fp_raw - FP_MEAN) / FP_SCALE

    X = pd.DataFrame([SAMPLE_LIKERT])[LIKERT_COLS].astype(float)
    X_scaled = artifacts["scaler"].transform(X)
    pcs = artifacts["pca"].transform(X_scaled)[0]

    X_model = pd.DataFrame([{
        "function_points": fp_std,
        "PC1": float(pcs[0]),
        "PC2": float(pcs[1]),
    }])

    pred_log = artifacts["model"].predict(X_model)
    effort_hours = np.exp(pred_log[0])

    assert effort_hours > 0
    assert 100 < effort_hours < 50_000

def test_pipeline_sensitivity(artifacts):
    """Projetos com FP diferentes devem gerar estimativas diferentes."""
    def predict(fp_raw):
        FP_MEAN  = float(artifacts["scaler_fp"].mean_[0])
        FP_SCALE = float(artifacts["scaler_fp"].scale_[0])
        fp_std = (fp_raw - FP_MEAN) / FP_SCALE
        X = pd.DataFrame([SAMPLE_LIKERT])[LIKERT_COLS].astype(float)
        X_scaled = artifacts["scaler"].transform(X)
        pcs = artifacts["pca"].transform(X_scaled)[0]
        X_model = pd.DataFrame([{"function_points": fp_std, "PC1": float(pcs[0]), "PC2": float(pcs[1])}])
        return np.exp(artifacts["model"].predict(X_model)[0])

    assert predict(200) != predict(800)
    assert predict(800) > predict(200)
