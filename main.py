from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

# Aseguramos que encuentre tus módulos en src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from model import predict_sales

# 1. Creamos la aplicación
app = FastAPI(
    title="Reckitt Demand Forecasting API",
    description="API para predecir la demanda de productos Reckitt por estado y mes.",
    version="1.0.0"
)

# 2. Definimos el esquema de los datos que recibiremos (Input)
class PredictionInput(BaseModel):
    item_code: str
    state: str
    month: int

# 3. Endpoint de Bienvenida
@app.get("/")
def home():
    return {"message": "API de Predicción Reckitt operativa. Ve a /docs para probarla."}

# 4. Endpoint de Predicción (POST)
@app.post("/predict")
def get_prediction(data: PredictionInput):
    try:
        # Llamamos a tu función lógica de model.py
        # El modelo actual requiere (month, year, item_code)
        # Por ahora usaremos 2024 como año predeterminado si no se incluye
        year_default = 2024
        resultado = predict_sales(data.month, year_default, data.item_code)
        
        return {
            "status": "success",
            "item_code": data.item_code,
            "state": data.state,
            "predicted_demand": round(float(resultado), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
