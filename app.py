import streamlit as st
import plotly.express as px
import os
from extract import get_processed_data
from model import train_demand_model, predict_sales

st.set_page_config(page_title="Reckitt Sales Intelligence", layout="wide")

df = get_processed_data()

# --- TÍTULOS RECKITT ---
st.title("Proyecto Consumo Masivo : Reckitt")
st.sidebar.header("Filtros")

# Filtros (igual que antes)
regiones = st.sidebar.multiselect("Regiones", df['REGION_NAME'].unique(), default=df['REGION_NAME'].unique())
df_f = df[df['REGION_NAME'].isin(regiones)]
estados = st.sidebar.multiselect("Estados", df_f['REGION_STATES'].unique(), default=df_f['REGION_STATES'].unique())
df_final = df_f[df_f['REGION_STATES'].isin(estados)]

# --- MAPA (CÓDIGO REFORZADO) ---
st.subheader("📍 Desempeño Geográfico por Estado")
map_data = df_final.groupby('REGION_STATES')['TOTAL_VALUE_SALES'].sum().reset_index()

# Usamos una URL de GeoJSON alternativa y más rápida
mx_geojson = "https://raw.githubusercontent.com/isaacanton/Mexico-GeoJSON/master/mexico.json"

fig_map = px.choropleth(
    map_data,
    geojson=mx_geojson,
    locations='REGION_STATES',
    featureidkey="properties.name",
    color='TOTAL_VALUE_SALES',
    color_continuous_scale="Blues",
    scope="north america"
)
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)



# --- PREDICCIÓN (CON RE-ENTRENAMIENTO LIGERO) ---
st.divider()
if not os.path.exists('src/sales_model.pkl'):
    st.warning("⚠️ El cerebro del modelo está vacío.")
    if st.button("🚀 Entrenar Inteligencia Reckitt"):
        with st.spinner("Entrenando con optimización de memoria..."):
            train_demand_model(df)
            st.success("¡Modelo listo!")
            st.rerun()
else:
    # (Código del simulador igual que el anterior, usando predict_sales)
    pass