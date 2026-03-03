import pandas as pd
import numpy as np

def normalize_states(df):
    # Limpieza de espacios en blanco y saltos de línea
    df['REGION_STATES'] = df['REGION_STATES'].astype(str).str.strip()
    
    mapping = {
        'Estado de México': 'México',
        'Ciudad de México': 'Distrito Federal',
        'Michoacán': 'Michoacán de Ocampo',
        'Veracruz': 'Veracruz de Ignacio de la Llave',
        'Coahuila': 'Coahuila de Zaragoza',
        'Querétaro': 'Querétaro de Arteaga'
    }
    df['REGION_STATES'] = df['REGION_STATES'].replace(mapping)
    return df

def get_processed_data():
    try:
        df = pd.read_csv('data/FACT_SALES_GEO.csv')
        df.columns = df.columns.str.strip().str.upper()
        
        # Tipado numérico fuerte
        for col in ['TOTAL_UNIT_SALES', 'TOTAL_VALUE_SALES']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        # Normalización geográfica
        df = normalize_states(df)
        
        # Crear columna DATE
        parts = df['WEEK'].str.split('-', expand=True)
        df['DATE'] = pd.to_datetime('20' + parts[1] + '-W' + parts[0] + '-1', format='%G-W%V-%u', errors='coerce')
        df['MONTH'] = df['DATE'].dt.month
        
        return df
    except Exception as e:
        print(f"Error ETL: {e}")
        return None