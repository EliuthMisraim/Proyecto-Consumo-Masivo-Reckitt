import pandas as pd
import numpy as np
import logging

# Configuración de logs para monitorear el proceso en la consola
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_data(file_path='data/FACT_SALES_GEO.csv'):
    """
    Carga el archivo principal de ventas con datos geográficos.
    """
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Archivo {file_path} cargado exitosamente.")
        return df
    except FileNotFoundError:
        logging.error(f"No se encontró el archivo en {file_path}. Revisa la carpeta 'data/'.")
        return None

def transform_data(df):
    """
    Realiza la limpieza, tipado de datos y feature engineering.
    """
    if df is None:
        return None
    
    # 1. Limpieza de nombres de columnas
    df.columns = df.columns.str.strip().str.upper()
    
    # 2. Manejo de tipos numéricos
    cols_numericas = ['TOTAL_UNIT_SALES', 'TOTAL_VALUE_SALES', 'TOTAL_UNIT_AVG_WEEKLY_SALES']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 3. Transformación de la columna WEEK a DATE (Formato: WW-YY)
    # Esto es vital para las gráficas de líneas y series de tiempo
    if 'WEEK' in df.columns:
        try:
            # Dividimos '34-22' en semana 34 y año 2022
            parts = df['WEEK'].str.split('-', expand=True)
            df['YEAR_TEMP'] = '20' + parts[1]
            df['WEEK_TEMP'] = parts[0]
            
            # Creamos una fecha real (lunes de esa semana)
            df['DATE'] = pd.to_datetime(
                df['YEAR_TEMP'] + '-W' + df['WEEK_TEMP'] + '-1', 
                format='%G-W%V-%u', 
                errors='coerce'
            )
            # Eliminamos columnas temporales
            df.drop(columns=['YEAR_TEMP', 'WEEK_TEMP'], inplace=True)
            logging.info("Columna DATE generada correctamente a partir de WEEK.")
        except Exception as e:
            logging.warning(f"No se pudo convertir WEEK a DATE: {e}")

    # 4. Feature Engineering para el Dashboard
    if 'DATE' in df.columns:
        df['MONTH'] = df['DATE'].dt.month
        df['YEAR'] = df['DATE'].dt.year
        df['MONTH_NAME'] = df['DATE'].dt.month_name()

    return df

def get_processed_data():
    """
    Función maestra que ejecuta el pipeline completo.
    """
    raw_data = load_data()
    processed_data = transform_data(raw_data)
    return processed_data

if __name__ == "__main__":
    # Prueba rápida al ejecutar el script directamente
    test_df = get_processed_data()
    if test_df is not None:
        print(test_df.head())
        print(test_df.info())