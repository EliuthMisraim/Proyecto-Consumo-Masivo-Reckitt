import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
import logging

# Configuración de rutas para guardar el cerebro del proyecto
MODEL_PATH = 'src/sales_model.pkl'
COLUMNS_PATH = 'src/model_columns.pkl'

logging.basicConfig(level=logging.INFO)

def train_demand_model(df):
    """
    Entrena un modelo de Random Forest para predecir TOTAL_UNIT_SALES.
    Usa el producto, el estado y el mes como variables predictoras.
    """
    logging.info("Iniciando el entrenamiento del modelo...")
    
    # 1. Selección de variables relevantes (Features)
    # Eliminamos nulos en la columna objetivo y en variables clave
    df_train = df.dropna(subset=['TOTAL_UNIT_SALES', 'MONTH', 'ITEM_CODE', 'REGION_STATES'])
    
    # 2. Preprocesamiento: Convertir texto a números (One-Hot Encoding)
    # Seleccionamos variables categóricas y temporales
    X = df_train[['MONTH', 'ITEM_CODE', 'REGION_STATES']]
    y = df_train['TOTAL_UNIT_SALES']
    
    # Transformamos ITEM_CODE y REGION_STATES en columnas numéricas (0 y 1)
    X = pd.get_dummies(X, columns=['ITEM_CODE', 'REGION_STATES'])
    
    # 3. Entrenamiento
    # Random Forest es excelente para capturar patrones no lineales en consumo masivo
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    
    # 4. Persistencia: Guardar el modelo y el orden de las columnas
    if not os.path.exists('src'):
        os.makedirs('src')
        
    joblib.dump(model, MODEL_PATH)
    joblib.dump(X.columns.tolist(), COLUMNS_PATH)
    
    logging.info(f"Modelo entrenado exitosamente. Guardado en {MODEL_PATH}")
    return model

def predict_sales(month, item_code, state):
    """
    Carga el modelo guardado y realiza una predicción basada en los inputs del usuario.
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(COLUMNS_PATH):
        raise FileNotFoundError("El modelo no ha sido entrenado. Ejecuta el entrenamiento primero.")

    # Cargar archivos
    model = joblib.load(MODEL_PATH)
    model_columns = joblib.load(COLUMNS_PATH)
    
    # Crear un DataFrame vacío con las mismas columnas que el entrenamiento
    input_data = pd.DataFrame(0, index=[0], columns=model_columns)
    
    # Llenar los datos del input
    input_data['MONTH'] = month
    
    # Activar el bit (1) para el producto y estado seleccionados
    col_item = f'ITEM_CODE_{item_code}'
    col_state = f'REGION_STATES_{state}'
    
    if col_item in input_data.columns:
        input_data[col_item] = 1
    if col_state in input_data.columns:
        input_data[col_state] = 1
        
    # Realizar predicción
    prediction = model.predict(input_data)[0]
    
    # No podemos vender unidades negativas
    return max(0, prediction)