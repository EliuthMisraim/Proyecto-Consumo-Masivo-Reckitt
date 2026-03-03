# 📊 Proyecto de Consumo Masivo - Reckitt (End-to-End)

Este repositorio contiene una solución integral de Ciencia de Datos para el sector de consumo masivo, abarcando desde la extracción y limpieza de datos (ETL) hasta el entrenamiento de modelos predictivos y el despliegue de una interfaz interactiva.

## 🚀 Descripción del Proyecto

El objetivo principal es proporcionar una herramienta visual para el monitoreo de ventas y la predicción de demanda de productos. Utiliza datos históricos de ventas, catálogos de productos y calendarios comerciales para generar insights accionables.

## 📁 Estructura del Proyecto

El proyecto sigue una organización modular y limpia:

- `data/`: Contiene los conjuntos de datos originales (CSV) utilizados para el análisis.
- `src/`: Directorio de código fuente.
  - `extract.py`: Lógica de carga de datos (ETL), limpieza y unión de tablas.
  - `model.py`: Entrenamiento del modelo `RandomForestRegressor` y funciones de predicción.
- `notebooks/`: Espacio para experimentación, análisis exploratorio (EDA) y prototipado.
- `app.py`: Aplicación web interactiva desarrollada con **Streamlit**.
- `requirements.txt`: Dependencias necesarias para ejecutar el proyecto.

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.x
- **Análisis de Datos:** Pandas, NumPy
- **Machine Learning:** Scikit-Learn, Joblib
- **Visualización:** Plotly, Streamlit
- **Control de Versiones:** Git & GitHub

## ⚙️ Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/EliuthMisraim/Proyecto-Consumo-Masivo-Reckitt.git
   cd Proyecto-Consumo-Masivo-Reckitt
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   streamlit run app.py
   ```

## 🧠 Características del Modelo

El modelo de predicción de demanda utiliza un **Random Forest Regressor** que considera variables como el mes, el año y el código del producto para estimar el volumen de ventas esperado. El pipeline incluye:
- Preprocesamiento y codificación de variables categóricas.
- Persistencia del modelo entrenado (`.pkl`) para una inferencia rápida en producción.

---
*Desarrollado por [EliuthMisraim](https://github.com/EliuthMisraim)*
