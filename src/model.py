import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import logging

def train_demand_model(df):
    """Entrena un modelo para predecir TOTAL_UNIT_SALES."""
    # Preparación de features básicas (ejemplo: Mes, Año, Producto)
    df_model = df.dropna(subset=['TOTAL_UNIT_SALES', 'MONTH', 'YEAR', 'ITEM_CODE'])
    
    # One-hot encoding para el código de ítem
    X = pd.get_dummies(df_model[['MONTH', 'YEAR', 'ITEM_CODE']], columns=['ITEM_CODE'])
    y = df_model['TOTAL_UNIT_SALES']
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Guardamos el modelo para usarlo en la app sin re-entrenar
    joblib.dump(model, 'src/sales_model.pkl')
    joblib.dump(X.columns.tolist(), 'src/model_columns.pkl')
    logging.info("Modelo entrenado y guardado en src/sales_model.pkl")
    return model

def predict_sales(month, year, item_code):
    """Carga el modelo y hace una predicción."""
    model = joblib.load('src/sales_model.pkl')
    model_columns = joblib.load('src/model_columns.pkl')
    
    # Crear input con las mismas columnas del entrenamiento
    input_df = pd.DataFrame(columns=model_columns).fillna(0)
    input_df.loc[0, 'MONTH'] = month
    input_df.loc[0, 'YEAR'] = year
    if f'ITEM_CODE_{item_code}' in model_columns:
        input_df.loc[0, f'ITEM_CODE_{item_code}'] = 1
        
    prediction = model.predict(input_df)
    return prediction[0]