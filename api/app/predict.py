import pandas as pd
import numpy as np
from app.feature_loader import load_features

def make_prediction(model, data):
    features_config = load_features()

    # pega só as features que o modelo usa
    selected_features = [
        f for f in features_config["features"]
        if f in ["function_points", "PC1", "PC2"]
    ]

    input_dict = data.dict()

    filtered_input = {k: input_dict[k] for k in selected_features}

    df = pd.DataFrame([filtered_input])

    prediction = model.predict(df)

    prediction_exp = np.exp(prediction[0])

    return float(prediction_exp)