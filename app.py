import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from extract import get_processed_data
from model import predict_sales, train_demand_model

# 1. Configuración de la Identidad Visual
st.set_page_config(
    page_title="Reckitt Sales Intelligence",
    page_icon="🧼", # Icono alusivo a limpieza/consumo
    layout="wide"
)

# 2. CSS Ajustado: Quitamos el fondo blanco de las tarjetas para que use el del tema (Light/Dark)
st.markdown("""
    <style>
    .main { background-color: transparent; }
    /* Estilizamos las métricas sin forzar fondo blanco */
    [data-testid="stMetric"] {
        border: 1px solid #464e5f;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Carga de datos
@st.cache_data
def load_and_clean():
    return get_processed_data()

df = load_and_clean()

# --- SIDEBAR ---
st.sidebar.title("Filtros Estratégicos")
region_list = sorted(df['REGION_NAME'].unique())
selected_regions = st.sidebar.multiselect("Regiones", region_list, default=region_list)

df_filtered = df[df['REGION_NAME'].isin(selected_regions)]
state_list = sorted(df_filtered['REGION_STATES'].unique())
selected_states = st.sidebar.multiselect("Estados", state_list, default=state_list)

df_final = df_filtered[df_filtered['REGION_STATES'].isin(selected_states)]

# --- ENCABEZADO PERSONALIZADO ---
st.title("Proyecto Consumo Masivo : Reckitt")

# Subtítulo solicitado
regiones_str = ", ".join(selected_regions) if selected_regions else "México"
st.markdown(f"#### Análisis detallado de ventas para productos **Reckitt** en {regiones_str} de México")

# --- KPIs SIN COLOR DE FONDO ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Ventas Totales", f"${df_final['TOTAL_VALUE_SALES'].sum():,.2f}")
with k2:
    st.metric("Volumen Unidades", f"{df_final['TOTAL_UNIT_SALES'].sum():,.0f}")
with k3:
    st.metric("Ticket Promedio", f"${(df_final['TOTAL_VALUE_SALES'].sum()/df_final['TOTAL_UNIT_SALES'].sum() if df_final['TOTAL_UNIT_SALES'].sum()>0 else 0):,.2f}")
with k4:
    st.metric("SKUs Activos", df_final['ITEM_CODE'].nunique())

# --- MAPA INTERACTIVO DE MÉXICO ---
st.subheader("📍 Desempeño Geográfico por Estado")

# Agrupamos datos para el mapa
map_data = df_final.groupby('REGION_STATES')['TOTAL_VALUE_SALES'].sum().reset_index()

# Para el mapa usamos un Choropleth. 
# NOTA: Para que funcione perfecto en México, usamos un GeoJSON público.
fig_map = px.choropleth(
    map_data,
    geojson='https://raw.githubusercontent.com/angelnm782/mexico-states-geojson/master/mexico.json',
    locations='REGION_STATES',
    featureidkey="properties.name", # Esto debe coincidir con los nombres en tu CSV
    color='TOTAL_VALUE_SALES',
    color_continuous_scale="Viridis",
    scope="north america",
    labels={'TOTAL_VALUE_SALES':'Ventas ($)'}
)

fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)

st.plotly_chart(fig_map, use_container_width=True)



# --- PREDICCIÓN (Se mantiene igual) ---
st.markdown("---")
st.header("🔮 Predicción Inteligente de Demanda")
# ... (aquí va el mismo código de predicción que ya tienes)