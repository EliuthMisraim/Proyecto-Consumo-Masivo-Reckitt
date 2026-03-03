import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Agregar la carpeta src/ al path para que funcione en Streamlit Cloud
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from extract import get_processed_data
from model import predict_sales, train_demand_model

# 1. Configuración de la Identidad Visual
st.set_page_config(
    page_title="Executive Sales Intelligence | Consumo Masivo",
    page_icon="📊",
    layout="wide"
)

# Estilo para mejorar la estética
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Carga y Procesamiento de Datos
@st.cache_data
def load_and_clean():
    return get_processed_data()

df = load_and_clean()

if df is None:
    st.error("❌ No se pudo cargar FACT_SALES_GEO.csv. Asegúrate de que esté en la carpeta 'data/'.")
    st.stop()

# 3. Sidebar (Filtros Inteligentes)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3222/3222672.png", width=80)
st.sidebar.title("Panel de Control")
st.sidebar.markdown("---")

# Filtro de Región
region_list = sorted(df['REGION_NAME'].unique())
selected_regions = st.sidebar.multiselect("Selecciona Regiones", region_list, default=region_list)

# Filtro de Estado (Dependiente de la región)
df_filtered = df[df['REGION_NAME'].isin(selected_regions)]
state_list = sorted(df_filtered['REGION_STATES'].unique())
selected_states = st.sidebar.multiselect("Selecciona Estados", state_list, default=state_list)

# Filtro final aplicado
df_final = df_filtered[df_filtered['REGION_STATES'].isin(selected_states)]

# 4. Encabezado y KPIs
st.title("🚀 Inteligencia de Mercado: Consumo Masivo")
st.markdown(f"Análisis detallado para **{', '.join(selected_regions) if selected_regions else 'Todas las Regiones'}**")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    total_sales = df_final['TOTAL_VALUE_SALES'].sum()
    st.metric("Ventas Totales (Val)", f"${total_sales:,.2f}")
with kpi2:
    total_units = df_final['TOTAL_UNIT_SALES'].sum()
    st.metric("Volumen Unidades", f"{total_units:,.0f}")
with kpi3:
    avg_ticket = total_sales / total_units if total_units > 0 else 0
    st.metric("Ticket Promedio", f"${avg_ticket:,.2f}")
with kpi4:
    active_items = df_final['ITEM_CODE'].nunique()
    st.metric("SKUs Activos", f"{active_items}")

# 5. Visualizaciones Estratégicas
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Tendencia de Ventas Semanales")
    if 'DATE' in df_final.columns:
        sales_trend = df_final.groupby('DATE')['TOTAL_VALUE_SALES'].sum().reset_index()
        fig_line = px.line(sales_trend, x='DATE', y='TOTAL_VALUE_SALES', 
                          labels={'TOTAL_VALUE_SALES': 'Ventas ($)'},
                          color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.subheader("📍 Participación por Estado")
    fig_pie = px.pie(df_final, values='TOTAL_VALUE_SALES', names='REGION_STATES',
                    hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# 6. Simulador de Machine Learning
st.markdown("---")
st.header("🔮 Predicción Inteligente de Demanda")

# Verificar si el modelo existe
model_exists = os.path.exists('src/sales_model.pkl')

if not model_exists:
    st.warning("⚠️ El modelo de inteligencia aún no ha sido entrenado con los datos actuales.")
    if st.button("🚀 Entrenar Modelo Ahora"):
        with st.spinner("Entrenando algoritmo... esto tardará unos segundos"):
            train_demand_model(df)
            st.success("¡Modelo listo para predecir!")
            st.rerun()
else:
    c_sim1, c_sim2, c_sim3 = st.columns(3)
    with c_sim1:
        s_item = st.selectbox("Producto (SKU)", options=sorted(df['ITEM_CODE'].unique()))
    with c_sim2:
        s_state = st.selectbox("Estado de Destino", options=sorted(df['REGION_STATES'].unique()))
    with c_sim3:
        s_month = st.slider("Mes de Proyección", 1, 12, 6)

    if st.button("Calcular Demanda Estimada"):
        try:
            prediction = predict_sales(s_month, s_item, s_state)
            st.balloons()
            st.success(f"### Resultado: {prediction:,.2f} unidades estimadas")
            st.caption("Nota: Esta predicción se basa en patrones históricos, estacionalidad y comportamiento regional.")
        except Exception as e:
            st.error(f"Error en la predicción: {e}")