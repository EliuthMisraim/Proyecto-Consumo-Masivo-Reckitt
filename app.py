import streamlit as st
import pandas as pd
import plotly.express as px
import os
from extract import get_processed_data
from model import predict_sales, train_demand_model

# 1. Configuración de la Página
st.set_page_config(
    page_title="Reckitt Sales Intelligence",
    page_icon="🧼",
    layout="wide"
)

# 2. CSS Personalizado (KPIs transparentes y adaptativos)
st.markdown("""
    <style>
    /* Quitamos el fondo blanco de las métricas para que sean transparentes */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05); 
        border: 1px solid #464e5f;
        padding: 15px;
        border-radius: 10px;
    }
    /* Aseguramos que el texto sea legible */
    [data-testid="stMetricLabel"] {
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Carga de Datos
@st.cache_data
def load_data():
    return get_processed_data()

df = load_data()

if df is None:
    st.error("No se pudo cargar el archivo FACT_SALES_GEO.csv")
    st.stop()

# --- SIDEBAR (Filtros) ---
st.sidebar.title("Filtros Reckitt")
region_list = sorted(df['REGION_NAME'].unique())
selected_regions = st.sidebar.multiselect("Regiones", region_list, default=region_list)

# Filtro dinámico de estados según región
df_filtered_reg = df[df['REGION_NAME'].isin(selected_regions)]
state_list = sorted(df_filtered_reg['REGION_STATES'].unique())
selected_states = st.sidebar.multiselect("Estados", state_list, default=state_list)

df_final = df_filtered_reg[df_filtered_reg['REGION_STATES'].isin(selected_states)]

# --- ENCABEZADO PERSONALIZADO ---
st.title("Proyecto Consumo Masivo : Reckitt")

# Subtítulo solicitado dinámico
regiones_str = ", ".join(selected_regions) if selected_regions else "diversas regiones"
st.markdown(f"##### Análisis detallado de ventas para productos **Reckitt** en {regiones_str} de México")

# --- KPIs (Transparentes) ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Ventas Totales", f"${df_final['TOTAL_VALUE_SALES'].sum():,.2f}")
with k2:
    st.metric("Volumen Unidades", f"{df_final['TOTAL_UNIT_SALES'].sum():,.0f}")
with k3:
    venta_tot = df_final['TOTAL_VALUE_SALES'].sum()
    unid_tot = df_final['TOTAL_UNIT_SALES'].sum()
    ticket = venta_tot / unid_tot if unid_tot > 0 else 0
    st.metric("Ticket Promedio", f"${ticket:,.2f}")
with k4:
    st.metric("SKUs Activos", df_final['ITEM_CODE'].nunique())

# --- MAPA INTERACTIVO DE MÉXICO ---
st.subheader("📍 Desempeño Geográfico por Estado")

# Agrupamos por estado para el mapa
map_data = df_final.groupby('REGION_STATES')['TOTAL_VALUE_SALES'].sum().reset_index()

# GeoJSON de México para los límites de los estados
repo_url = 'https://raw.githubusercontent.com/angelnm782/mexico-states-geojson/master/mexico.json'

fig_map = px.choropleth(
    map_data,
    geojson=repo_url,
    locations='REGION_STATES',
    featureidkey="properties.name", # Coincidencia con nombres normalizados en extract.py
    color='TOTAL_VALUE_SALES',
    color_continuous_scale="Blues",
    labels={'TOTAL_VALUE_SALES': 'Ventas ($)'}
)

fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)

st.plotly_chart(fig_map, use_container_width=True)

# --- SECCIÓN DE PREDICCIÓN ---
st.markdown("---")
st.header("🔮 Predicción Inteligente de Demanda")

model_path = 'src/sales_model.pkl'

if not os.path.exists(model_path):
    st.warning("⚠️ El modelo de inteligencia no ha sido entrenado con los datos normalizados.")
    if st.button("🚀 Entrenar Modelo Ahora"):
        with st.spinner("Procesando patrones de venta de Reckitt..."):
            train_demand_model(df)
            st.success("¡Modelo actualizado exitosamente!")
            st.rerun()
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        s_item = st.selectbox("SKU del Producto", options=sorted(df['ITEM_CODE'].unique()))
    with c2:
        s_state = st.selectbox("Estado", options=sorted(df['REGION_STATES'].unique()))
    with c3:
        s_month = st.slider("Mes a proyectar", 1, 12, 6)

    if st.button("Calcular Predicción de Demanda"):
        try:
            res = predict_sales(s_month, s_item, s_state)
            st.success(f"### Demanda Estimada: {res:,.2f} unidades")
        except Exception as e:
            st.error(f"Error al calcular: {e}")