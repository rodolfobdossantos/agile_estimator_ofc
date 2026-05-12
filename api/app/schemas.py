from pydantic import BaseModel

class PredictionInput(BaseModel):
    function_points: float
    PC1: float
    PC2: float