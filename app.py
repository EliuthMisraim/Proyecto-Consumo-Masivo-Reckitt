import streamlit as st
import plotly.express as px
import os
import sys
import pandas as pd
import json

# Agregar src/ al path para que funcione en Streamlit Cloud
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from extract import get_processed_data
from model import train_demand_model, predict_sales

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Reckitt Sales Intelligence", layout="wide", page_icon="🧼")

MODEL_PATH  = '/tmp/sales_model.pkl'
SHP_JSON = 'data/mexico.geojson'

# ─── CARGA DE DATOS ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando datos de ventas...")
def load_data():
    return get_processed_data()

df = load_data()
if df is None:
    st.error("❌ No se pudo cargar FACT_SALES_GEO.csv")
    st.stop()


# ─── CARGA DEL GEOJSON ───────────────────────────────────────────────────────
@st.cache_data(show_spinner="Preparando mapa de México...")
def load_mexico_geojson():
    """
    Carga el GeoJSON estático pre-procesado para evitar tiempos largos
    de conversión de shapefile en la nube.
    """
    try:
        with open(SHP_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"⚠️ No se pudo cargar el shapefile estático: {e}")
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
)

if geojson_data is not None:
    # Aseguramos que los 32 estados estén en el DataFrame con 0 ventas si no hay filtro
    all_states = [f['properties']['ENTIDAD'] for f in geojson_data['features']]
    all_states_df = pd.DataFrame({'REGION_STATES': all_states})
    
    # Merge correcto: mantenemos todos los estados e insertamos las ventas reales
    map_data = pd.merge(all_states_df, map_data, on='REGION_STATES', how='left')
    map_data['TOTAL_VALUE_SALES'] = map_data['TOTAL_VALUE_SALES'].fillna(0)

    fig_map = px.choropleth(
        map_data,
        geojson=geojson_data,
        locations='REGION_STATES',
        featureidkey='properties.ENTIDAD',
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
    map_data = map_data.sort_values('TOTAL_VALUE_SALES', ascending=False)
    fig_bar = px.bar(
        map_data, x='TOTAL_VALUE_SALES', y='REGION_STATES',
        orientation='h', color='TOTAL_VALUE_SALES',
        color_continuous_scale='Blues',
        labels={'TOTAL_VALUE_SALES': 'Ventas ($)', 'REGION_STATES': 'Estado'}
    )
    fig_bar.update_layout(height=520, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

# ─── TENDENCIAS Y TOP PRODUCTOS ──────────────────────────────────────────────
st.divider()
c_chart1, c_chart2 = st.columns(2)

with c_chart1:
    st.subheader("📈 Tendencia de Ventas")
    if 'DATE' in df_final.columns:
        trend_data = df_final.groupby('DATE')['TOTAL_VALUE_SALES'].sum().reset_index().sort_values('DATE')
        fig_trend = px.line(
            trend_data, x='DATE', y='TOTAL_VALUE_SALES',
            labels={'TOTAL_VALUE_SALES': 'Ventas ($)', 'DATE': 'Fecha'},
            markers=True, line_shape='spline',
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No hay datos de fecha disponibles.")

with c_chart2:
    # --- TOP PRODUCTOS (INSIGHT DE NEGOCIO) ---
    st.subheader("🏆 Top 5 Productos Estratégicos")
    
    # Agrupamos por nombre de producto o SKU
    top_products = df_final.groupby('ITEM_CODE')['TOTAL_VALUE_SALES'].sum().nlargest(5).reset_index()
    
    col_table, col_chart = st.columns([1, 2])
    
    with col_table:
        st.write("Detalle de Ventas")
        st.dataframe(top_products.style.format({'TOTAL_VALUE_SALES': '${:,.2f}'}), hide_index=True)
    
    with col_chart:
        # Convertir ITEM_CODE a string puro, a veces pandas los lee como decimales y plotly se confunde
        top_products['ITEM_CODE'] = top_products['ITEM_CODE'].astype(str).str.replace(r'\.0$', '', regex=True)
        
        fig_top = px.bar(top_products, x='TOTAL_VALUE_SALES', y='ITEM_CODE', 
                         orientation='h', title="Top 5 por Valor de Venta",
                         color='TOTAL_VALUE_SALES', color_continuous_scale='Blues')
        
        # Formatear el hover para que muestre la moneda y el SKU completo
        fig_top.update_traces(hovertemplate='<b>SKU:</b> %{y}<br><b>Ventas:</b> $%{x:,.2f}<extra></extra>')
        fig_top.update_layout(yaxis={'categoryorder':'total ascending', 'type': 'category'}, 
                              margin={"r": 0, "t": 40, "l": 0, "b": 0})
        st.plotly_chart(fig_top, use_container_width=True)

st.divider()

# ─── PREDICCIÓN ───────────────────────────────────────────────────────────────
st.header("🔮 Predicción Inteligente de Demanda")

# Detectar modelo obsoleto: si los estados del modelo no coinciden con los datos actuales
def _model_is_stale():
    import joblib
    if not os.path.exists(MODEL_PATH):
        return True
    try:
        payload = joblib.load(MODEL_PATH)
        model_states = set(payload['state_map'].keys())
        data_states  = set(df['REGION_STATES'].unique())
        return not model_states.issubset(data_states)
    except Exception:
        return True

if _model_is_stale():
    # Limpiar flag de sesión si el modelo está obsoleto
    st.session_state.pop('model_trained', None)

model_ready = os.path.exists(MODEL_PATH) and not _model_is_stale()

if not model_ready:
    st.warning("⚠️ El modelo aún no ha sido entrenado (o los datos cambiaron).")
    if st.button("🚀 Entrenar Modelo Reckitt"):
        with st.spinner("Entrenando algoritmo con datos históricos..."):
            train_demand_model(df)
            st.success("✅ ¡Modelo entrenado! Ya puedes hacer predicciones.")
            st.rerun()
else:
    col_btn = st.columns([3, 1])
    with col_btn[1]:
        if st.button("🔄 Reentrenar modelo"):
            train_demand_model(df)
            st.success("✅ Modelo actualizado.")
            st.rerun()

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