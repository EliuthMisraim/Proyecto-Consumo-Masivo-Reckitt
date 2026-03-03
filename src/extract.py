import pandas as pd
import logging

# Configuración básica de logs para ver qué pasa en el proceso
logging.basicConfig(level=logging.INFO)

def load_data():
    """Carga los archivos CSV con sus codificaciones específicas."""
    try:
        dim_calendar = pd.read_csv('data/DIM_CALENDAR.csv', sep=';', encoding='utf-8-sig')
        dim_product = pd.read_csv('data/DIM_PRODUCT.csv', sep=';', encoding='latin1')
        fact_sales = pd.read_csv('data/FACT_SALES.csv', sep=',', quotechar='"')
        return dim_calendar, dim_product, fact_sales
    except Exception as e:
        logging.error(f"Error cargando archivos: {e}")
        return None

def clean_data(dim_calendar, dim_product, fact_sales):
    """Limpia nombres, convierte tipos y genera el df_master."""
    # Limpieza de espacios en columnas
    for df in [dim_calendar, dim_product, fact_sales]:
        df.columns = df.columns.str.strip()

    # Conversión numérica
    cols_to_fix = ['TOTAL_UNIT_SALES', 'TOTAL_VALUE_SALES']
    for col in cols_to_fix:
        fact_sales[col] = pd.to_numeric(fact_sales[col], errors='coerce')

    # Unión de tablas (Merge)
    cols_calendar = ['WEEK', 'DATE', 'YEAR', 'MONTH']
    df_master = pd.merge(fact_sales, dim_calendar[cols_calendar], on='WEEK', how='left')
    df_master = pd.merge(df_master, dim_product, left_on='ITEM_CODE', right_on='ITEM', how='left')

    # Formato de fecha
    df_master['DATE'] = pd.to_datetime(df_master['DATE'], format='%d/%m/%Y', errors='coerce')
    
    logging.info("ETL completado: df_master generado correctamente.")
    return df_master

if __name__ == "__main__":
    # Prueba rápida de funcionamiento
    cal, prod, sales = load_data()
    df = clean_data(cal, prod, sales)
    print(df.head())