import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

def train_demand_model(df):
    # 1. Reducción de datos: El modelo no necesita millones de filas para el simulador
    # Tomamos una muestra representativa para que no se cuelgue en la nube
    df_train = df.sample(n=min(len(df), 50000), random_state=42)
    
    # 2. Convertimos categorías a códigos numéricos (EVITA EL CUELGUE)
    # En lugar de mil columnas, mantenemos solo una con IDs numéricos
    df_train['ITEM_ID'] = df_train['ITEM_CODE'].astype('category').cat.codes
    df_train['STATE_ID'] = df_train['REGION_STATES'].astype('category').cat.codes
    
    # Guardamos los mapeos para la predicción
    item_map = dict(zip(df_train['ITEM_CODE'], df_train['ITEM_ID']))
    state_map = dict(zip(df_train['REGION_STATES'], df_train['STATE_ID']))
    
    X = df_train[['MONTH', 'ITEM_ID', 'STATE_ID']]
    y = df_train['TOTAL_UNIT_SALES']
    
    # Modelo ligero: max_depth evita que el modelo crezca infinito y sature la RAM
    model = RandomForestRegressor(n_estimators=50, max_depth=10, n_jobs=-1, random_state=42)
    model.fit(X, y)
    
    # Guardamos todo en un solo combo
    payload = {
        'model': model,
        'item_map': item_map,
        'state_map': state_map
    }
    joblib.dump(payload, '/tmp/sales_model.pkl')
    return model

def predict_sales(month, item_code, state):
    payload = joblib.load('/tmp/sales_model.pkl')

    if state not in payload['state_map']:
        raise ValueError(
            f"El estado '{state}' no está en el modelo entrenado. "
            "Haz clic en '🔄 Reentrenar modelo' para actualizar."
        )

    item_id  = payload['item_map'].get(item_code, 0)
    state_id = payload['state_map'][state]

    import pandas as pd
    input_df = pd.DataFrame([[month, item_id, state_id]], columns=['MONTH', 'ITEM_ID', 'STATE_ID'])
    result = payload['model'].predict(input_df)[0]
    return max(0.0, result)   # nunca predecir unidades negativas
