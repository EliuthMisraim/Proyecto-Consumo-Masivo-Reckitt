import pandas as pd
import numpy as np
import logging

# Configuración de logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def normalize_states(df):
    """
    Estandariza los nombres de los estados de México para asegurar 
    compatibilidad total con el archivo GeoJSON del mapa.
    """
    # Diccionario de mapeo: 'Nombre en CSV': 'Nombre en GeoJSON'
    mapping = {
        'Estado de México': 'México',
        'Ciudad de México': 'Distrito Federal',
        'Michoacán': 'Michoacán de Ocampo',
        'Veracruz': 'Veracruz de Ignacio de la Llave',
        'Coahuila': 'Coahuila de Zaragoza',
        'Querétaro': 'Querétaro de Arteaga',
        'Nayarit': 'Nayarit',
        # Agrega más si detectas que algún estado sigue apareciendo en blanco
    }
    
    if 'REGION_STATES' in df.columns:
        df['REGION_STATES'] = df['REGION_STATES'].replace(mapping)
        logging.info("Nombres de estados normalizados para el mapa.")
    
    return df

def load_data(file_path='data/FACT_SALES_GEO.csv'):
    """Carga el archivo principal de ventas."""
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Archivo {file_path} cargado exitosamente.")
        return df
    except Exception as e:
        logging.error(f"Error al cargar el archivo: {e}")
        return None

def transform_data(df):
    """Pipeline principal de limpieza y transformación."""
    if df is None:
        return None
    
    # 1. Limpieza de nombres de columnas
    df.columns = df.columns.str.strip().str.upper()
    
    # 2. Tipado numérico
    cols_numericas = ['TOTAL_UNIT_SALES', 'TOTAL_VALUE_SALES']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 3. Conversión de WEEK a DATE (Formato WW-YY a Fecha Real)
    if 'WEEK' in df.columns:
        try:
            parts = df['WEEK'].str.split('-', expand=True)
            df['YEAR_TEMP'] = '20' + parts[1]
            df['WEEK_TEMP'] = parts[0]
            df['DATE'] = pd.to_datetime(
                df['YEAR_TEMP'] + '-W' + df['WEEK_TEMP'] + '-1', 
                format='%G-W%V-%u', 
                errors='coerce'
            )
            df.drop(columns=['YEAR_TEMP', 'WEEK_TEMP'], inplace=True)
        except Exception as e:
            logging.warning(f"Error en conversión de fechas: {e}")

    # 4. Normalización Geográfica (La nueva función)
    df = normalize_states(df)
    
    # 5. Columnas de tiempo para filtros
    if 'DATE' in df.columns:
        df['MONTH'] = df['DATE'].dt.month
        df['YEAR'] = df['DATE'].dt.year

    return df

def get_processed_data():
    """Función ejecutora para la App."""
    raw = load_data()
    return transform_data(raw)

if __name__ == "__main__":
    # Prueba local
    test_df = get_processed_data()
    if test_df is not None:
        print("Primeras filas con estados normalizados:")
        print(test_df[['REGION_STATES', 'TOTAL_VALUE_SALES']].head())