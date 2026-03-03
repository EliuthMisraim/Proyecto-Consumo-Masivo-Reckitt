import streamlit as st
import plotly.express as px
import os
import sys
import json

# Agregar src/ al path para que funcione en Streamlit Cloud
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from extract import get_processed_data
from model import train_demand_model, predict_sales

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Reckitt Sales Intelligence", layout="wide", page_icon="🧼")

MODEL_PATH  = '/tmp/sales_model.pkl'
SHP_ZIP     = 'dest_2010gw_c.zip'
SHP_FILE    = 'dest_2010cw.shp'
GEOJSON_TMP = '/tmp/mexico_states.geojson'

# ─── CARGA DE DATOS ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando datos de ventas...")
def load_data():
    return get_processed_data()

df = load_data()
if df is None:
    st.error("❌ No se pudo cargar FACT_SALES_GEO.csv")
    st.stop()

# ─── CARGA DEL GEOJSON DESDE SHAPEFILE LOCAL ─────────────────────────────────
@st.cache_data(show_spinner="Preparando mapa de México...")
def load_mexico_geojson():
    """
    Convierte el shapefile local (dest_2010gw_c.zip) a GeoJSON en memoria.
    Usa geopandas para reproyectar a WGS84 (lat/lon) que requiere plotly.
    """
    try:
        import geopandas as gpd
        gdf = gpd.read_file(f'zip://{SHP_ZIP}!{SHP_FILE}')
        # Re-proyectar a WGS84 (EPSG:4326) - requerido por plotly
        gdf = gdf.to_crs(epsg=4326)
        # Solo conservamos la columna de nombre del estado
        gdf = gdf[['ENTIDAD', 'geometry']].copy()
        return json.loads(gdf.to_json())
    except Exception as e:
        st.warning(f"⚠️ No se pudo cargar el shapefile: {e}")
        return None

geojson_data = load_mexico_geojson()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.title("🧼 Filtros Reckitt")
regiones = st.sidebar.multiselect(
    "Regiones", sorted(df['REGION_NAME'].unique()), default=sorted(df['REGION_NAME'].unique())
)
df_f = df[df['REGION_NAME'].isin(regiones)]
estados = st.sidebar.multiselect(
    "Estados", sorted(df_f['REGION_STATES'].unique()), default=sorted(df_f['REGION_STATES'].unique())
)
df_final = df_f[df_f['REGION_STATES'].isin(estados)]

# ─── ENCABEZADO ───────────────────────────────────────────────────────────────
st.title("Proyecto Consumo Masivo : Reckitt")
regiones_str = ", ".join(regiones) if regiones else "diversas regiones"
st.markdown(f"##### Análisis de ventas para productos **Reckitt** en {regiones_str} de México")
st.divider()

# ─── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
total_ventas   = df_final['TOTAL_VALUE_SALES'].sum()
total_unidades = df_final['TOTAL_UNIT_SALES'].sum()
ticket         = total_ventas / total_unidades if total_unidades > 0 else 0

k1.metric("💰 Ventas Totales",  f"${total_ventas:,.0f}")
k2.metric("📦 Volumen Unidades", f"{total_unidades:,.0f}")
k3.metric("🎫 Ticket Promedio",  f"${ticket:,.2f}")
k4.metric("🏷️ SKUs Activos",    df_final['ITEM_CODE'].nunique())

st.divider()

# ─── MAPA ─────────────────────────────────────────────────────────────────────
st.subheader("📍 Desempeño Geográfico por Estado")
map_data = (
    df_final.groupby('REGION_STATES')['TOTAL_VALUE_SALES']
    .sum().reset_index()
    .sort_values('TOTAL_VALUE_SALES', ascending=False)
)

if geojson_data is not None:
    fig_map = px.choropleth(
        map_data,
        geojson=geojson_data,
        locations='REGION_STATES',
        featureidkey='properties.ENTIDAD',   # campo del shapefile INEGI
        color='TOTAL_VALUE_SALES',
        color_continuous_scale='Blues',
        labels={'TOTAL_VALUE_SALES': 'Ventas ($)'},
        hover_name='REGION_STATES',
    )
    fig_map.update_geos(fitbounds='locations', visible=False)
    fig_map.update_layout(height=520, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)
else:
    # Fallback: gráfica de barras horizontal
    fig_bar = px.bar(
        map_data, x='TOTAL_VALUE_SALES', y='REGION_STATES',
        orientation='h', color='TOTAL_VALUE_SALES',
        color_continuous_scale='Blues',
        labels={'TOTAL_VALUE_SALES': 'Ventas ($)', 'REGION_STATES': 'Estado'}
    )
    fig_bar.update_layout(height=520, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ─── PREDICCIÓN ───────────────────────────────────────────────────────────────
st.header("🔮 Predicción Inteligente de Demanda")

model_ready = os.path.exists(MODEL_PATH) or st.session_state.get('model_trained', False)

if not model_ready:
    st.warning("⚠️ El modelo de demanda aún no ha sido entrenado.")
    if st.button("🚀 Entrenar Modelo Reckitt"):
        with st.spinner("Entrenando algoritmo con datos históricos..."):
            train_demand_model(df)
            st.session_state['model_trained'] = True
            st.success("✅ ¡Modelo entrenado! Ya puedes hacer predicciones.")
            st.rerun()
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        s_item  = st.selectbox("🏷️ SKU del Producto",  options=sorted(df['ITEM_CODE'].unique()))
    with c2:
        s_state = st.selectbox("📍 Estado",             options=sorted(df['REGION_STATES'].unique()))
    with c3:
        s_month = st.slider("📅 Mes a proyectar", 1, 12, 6)

    if st.button("📊 Calcular Predicción de Demanda"):
        try:
            res = predict_sales(s_month, s_item, s_state)
            st.success(f"### 📦 Demanda Estimada: **{res:,.0f} unidades**")
            st.caption("Basado en patrones históricos de ventas Reckitt por región y temporada.")
        except Exception as e:
            st.error(f"Error al calcular: {e}")