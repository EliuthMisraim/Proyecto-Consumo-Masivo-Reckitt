import streamlit as st
import pandas as pd
import plotly.express as px
from src.extract import load_data, clean_data

# Configuración de la página
st.set_page_config(page_title="Dashboard de Ventas Consumo Masivo", layout="wide")

st.title("📊 Monitor de Ventas y Predicción de Demanda")

# Carga de datos (Cache para velocidad)
@st.cache_data
def get_data():
    cal, prod, sales = load_data()
    if cal is not None and prod is not None and sales is not None:
        return clean_data(cal, prod, sales)
    return None

df = get_data()

if df is not None:
    # --- SIDEBAR (Filtros) ---
    st.sidebar.header("Filtros")
    region = st.sidebar.multiselect("Selecciona Región", options=df['REGION'].unique(), default=df['REGION'].unique())
    df_filtered = df[df['REGION'].isin(region)]

    # --- KPIs PRINCIPALES ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas Totales (Unid)", f"{df_filtered['TOTAL_UNIT_SALES'].sum():,.0f}")
    col2.metric("Ingresos Totales", f"${df_filtered['TOTAL_VALUE_SALES'].sum():,.2f}")
    col3.metric("Productos Activos", df_filtered['ITEM_CODE'].nunique())

    # --- GRÁFICA INTERACTIVA ---
    st.subheader("Tendencia de Ventas en el Tiempo")
    sales_time = df_filtered.groupby('DATE')['TOTAL_VALUE_SALES'].sum().reset_index()
    fig = px.line(sales_time, x='DATE', y='TOTAL_VALUE_SALES', title="Ventas Diarias")
    st.plotly_chart(fig, use_container_width=True)

    # --- SECCIÓN DE PREDICCIÓN ---
    st.divider()
    st.subheader("🔮 Simulador de Predicción de Demanda")
    with st.expander("Haz clic para predecir"):
        item = st.selectbox("Selecciona Producto", options=df['ITEM_CODE'].unique())
        mes = st.slider("Mes a predecir", 1, 12, 1)
        # Aquí llamarías a la función de model.py
        st.info(f"La demanda estimada para el producto {item} en el mes {mes} es de: XXX unidades")
else:
    st.error("No se pudieron cargar los datos. Por favor, verifica la carpeta data/.")