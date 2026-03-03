import pandas as pd
import numpy as np
import unicodedata

def remove_accents(text):
    """Elimina tildes y normaliza a ASCII uppercase para hacer match con el shapefile."""
    if not isinstance(text, str):
        return text
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).upper()

def normalize_states(df):
    """
    Normaliza REGION_STATES al formato del shapefile INEGI:
    mayúsculas, sin tildes, con nombres completos oficiales.
    Ejemplo: 'Ciudad de México' -> 'DISTRITO FEDERAL'
             'Michoacán'        -> 'MICHOACAN DE OCAMPO'
    """
    if 'REGION_STATES' not in df.columns:
        return df

    # Normalización base: quitar tildes y pasar a mayúsculas
    df['REGION_STATES'] = df['REGION_STATES'].astype(str).str.strip().apply(remove_accents)

    # Ajustes finales para nombres que el shapefile trae diferente
    corrections = {
        'CIUDAD DE MEXICO':          'DISTRITO FEDERAL',
        'ESTADO DE MEXICO':          'MEXICO',
        'MICHOACAN':                 'MICHOACAN DE OCAMPO',
        'VERACRUZ':                  'VERACRUZ DE IGNACIO DE LA LLAVE',
        'COAHUILA':                  'COAHUILA DE ZARAGOZA',
        'QUERETARO':                 'QUERETARO DE ARTEAGA',
        'NUEVO LEON':                'NUEVO LEON',    # ya correcto
        'SAN LUIS POTOSI':           'SAN LUIS POTOSI',  # ya correcto
        'QUINTANA ROO':              'QUINTANA ROO',  # ya correcto
    }
    df['REGION_STATES'] = df['REGION_STATES'].replace(corrections)
    return df

def get_processed_data():
    try:
        df = pd.read_csv('data/FACT_SALES_GEO.csv')
        df.columns = df.columns.str.strip().str.upper()

        # Tipado numérico
        for col in ['TOTAL_UNIT_SALES', 'TOTAL_VALUE_SALES']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Normalización geográfica (match con shapefile)
        df = normalize_states(df)

        # Crear columna DATE desde WEEK (formato WW-YY)
        if 'WEEK' in df.columns:
            parts = df['WEEK'].astype(str).str.split('-', expand=True)
            df['DATE'] = pd.to_datetime(
                '20' + parts[1] + '-W' + parts[0] + '-1',
                format='%G-W%V-%u', errors='coerce'
            )
            df['MONTH'] = df['DATE'].dt.month

        return df
    except Exception as e:
        print(f"Error ETL: {e}")
        return None