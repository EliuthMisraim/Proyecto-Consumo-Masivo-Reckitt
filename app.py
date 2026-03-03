import streamlit as st
import plotly.express as px
import os
import sys
import requests

# Agregar src/ al path para que funcione en Streamlit Cloud
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from extract import get_processed_data
from model import train_demand_model, predict_sales

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Reckitt Sales Intelligence", layout="wide", page_icon="🧼")

MODEL_PATH = '/tmp/sales_model.pkl'

# ─── CARGA DE DATOS ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando datos de ventas...")
def load_data():
    return get_processed_data()

df = load_data()

if df is None:
    st.error("❌ No se pudo cargar FACT_SALES_GEO.csv")
    st.stop()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.title("🧼 Filtros Reckitt")
regiones = st.sidebar.multiselect("Regiones", sorted(df['REGION_NAME'].unique()), default=sorted(df['REGION_NAME'].unique()))
df_f = df[df['REGION_NAME'].isin(regiones)]
estados = st.sidebar.multiselect("Estados", sorted(df_f['REGION_STATES'].unique()), default=sorted(df_f['REGION_STATES'].unique()))
df_final = df_f[df_f['REGION_STATES'].isin(estados)]

# ─── ENCABEZADO ───────────────────────────────────────────────────────────────
st.title("Proyecto Consumo Masivo : Reckitt")
regiones_str = ", ".join(regiones) if regiones else "diversas regiones"
st.markdown(f"##### Análisis de ventas para productos **Reckitt** en {regiones_str} de México")
st.divider()

# ─── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
total_ventas = df_final['TOTAL_VALUE_SALES'].sum()
total_unidades = df_final['TOTAL_UNIT_SALES'].sum()
ticket = total_ventas / total_unidades if total_unidades > 0 else 0

k1.metric("💰 Ventas Totales", f"${total_ventas:,.0f}")
k2.metric("📦 Volumen Unidades", f"{total_unidades:,.0f}")
k3.metric("🎫 Ticket Promedio", f"${ticket:,.2f}")
k4.metric("🏷️ SKUs Activos", df_final['ITEM_CODE'].nunique())

st.divider()

# ─── MAPA ─────────────────────────────────────────────────────────────────────
st.subheader("📍 Desempeño Geográfico por Estado")

map_data = df_final.groupby('REGION_STATES')['TOTAL_VALUE_SALES'].sum().reset_index()
map_data = map_data.sort_values('TOTAL_VALUE_SALES', ascending=False)

# Intentamos cargar el GeoJSON de México con manejo de errores
@st.cache_data(show_spinner=False)
def load_geojson():
    # URL confiable del GeoJSON de estados de México
    url = "https://raw.githubusercontent.com/PhantomInsights/mexican-states-geojson/master/states.geojson"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

geojson_data = load_geojson()

if geojson_data is not None:
    # Verificamos qué propiedad usar para los nombres
    try:
        sample_props = geojson_data['features'][0]['properties']
        # Este GeoJSON usa 'NOMBRE_EST' como clave de nombre
        name_key = 'NOMBRE_EST' if 'NOMBRE_EST' in sample_props else list(sample_props.keys())[0]

        fig_map = px.choropleth(
            map_data,
            geojson=geojson_data,
            locations='REGION_STATES',
            featureidkey=f"properties.{name_key}",
            color='TOTAL_VALUE_SALES',
            color_continuous_scale="Blues",
            labels={'TOTAL_VALUE_SALES': 'Ventas ($)'},
            hover_name='REGION_STATES',
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    except Exception as e:
        st.info(f"ℹ️ Mostrando gráfica de barras (el mapa no pudo renderizarse: {e})")
        _show_bar_chart(map_data)
else:
    # Fallback: Gráfica de barras por estado
    _show_bar_chart = lambda d: st.plotly_chart(
        px.bar(d, x='REGION_STATES', y='TOTAL_VALUE_SALES',
               labels={'TOTAL_VALUE_SALES': 'Ventas ($)', 'REGION_STATES': 'Estado'},
               color='TOTAL_VALUE_SALES', color_continuous_scale='Blues'),
        use_container_width=True
    )
    st.info("ℹ️ Mostrando gráfica de barras (GeoJSON no disponible)")
    _show_bar_chart(map_data)

st.divider()

# ─── PREDICCIÓN ───────────────────────────────────────────────────────────────
st.header("🔮 Predicción Inteligente de Demanda")

# El modelo se guarda en /tmp/ (siempre escribible en Streamlit Cloud)
# y se gestiona con session_state para no perderlo en reruns
model_ready = os.path.exists(MODEL_PATH) or st.session_state.get('model_trained', False)

if not model_ready:
    st.warning("⚠️ El modelo de demanda aún no ha sido entrenado.")
    if st.button("🚀 Entrenar Modelo Reckitt"):
        with st.spinner("Entrenando algoritmo con datos históricos..."):
            train_demand_model(df)
            st.session_state['model_trained'] = True
            st.success("✅ ¡Modelo entrenado con éxito! Ahora puedes hacer predicciones.")
            st.rerun()
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        s_item = st.selectbox("🏷️ SKU del Producto", options=sorted(df['ITEM_CODE'].unique()))
    with c2:
        s_state = st.selectbox("📍 Estado", options=sorted(df['REGION_STATES'].unique()))
    with c3:
        s_month = st.slider("📅 Mes a proyectar", 1, 12, 6)

    if st.button("📊 Calcular Predicción de Demanda"):
        try:
            res = predict_sales(s_month, s_item, s_state)
            st.success(f"### 📦 Demanda Estimada: **{res:,.0f} unidades**")
            st.caption("Basado en patrones históricos de ventas Reckitt por región y temporada.")
        except Exception as e:
            st.error(f"Error al calcular: {e}")