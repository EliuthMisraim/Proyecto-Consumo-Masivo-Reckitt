# 🧼 Reckitt Sales Intelligence System
> **End-to-End Demand Forecasting & Analytics Platform**

Este proyecto es una solución integral de **Ciencia de Datos y MLOps** diseñada para la industria de consumo masivo (CPG). Permite visualizar el desempeño histórico de ventas de **Reckitt** en México y predecir la demanda futura mediante inteligencia artificial.

---

## 🚀 Características Principales

* **Dashboard Interactivo:** Visualización regional con mapas coropléticos (GeoJSON) y KPIs de negocio (Ventas Totales, Ticket Promedio, Top Productos).
* **Modelo de Machine Learning:** Algoritmo de *Random Forest* optimizado para proyectar unidades vendidas por SKU, Estado y Mes.
* **Arquitectura de Microservicios:** Separación de preocupaciones entre el Frontend (Streamlit) y el Backend (FastAPI).
* **Despliegue Profesional:** Contenerización con **Docker** y despliegue en la nube (**Render**).

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
| :--- | :--- |
| **Lenguaje** | Python 3.9+ |
| **Análisis de Datos** | Pandas, Numpy |
| **Visualización** | Streamlit, Plotly Express |
| **Machine Learning** | Scikit-Learn (Random Forest), Joblib |
| **Backend API** | FastAPI, Uvicorn, Pydantic |
| **Infraestructura** | Docker, Docker-Compose |
| **Cloud Hosting** | Render (API), Streamlit Cloud (Dashboard) |

---

## 🏗️ Arquitectura del Proyecto

El sistema está estructurado bajo principios de código limpio y modularidad:

```text
├── data/               # Datasets y archivos geográficos (GeoJSON)
├── src/                # Lógica central del negocio
│   ├── extract.py      # Pipeline ETL y normalización geográfica (INEGI)
│   └── model.py        # Entrenamiento y lógica de inferencia del modelo
├── app.py              # Interfaz de usuario (Streamlit)
├── main.py             # Servidor de la API (FastAPI)
├── Dockerfile          # Instrucciones de imagen Docker
├── docker-compose.yml  # Orquestación de servicios
└── requirements.txt    # Dependencias del proyecto
```

---

## ⚙️ Instalación y Uso

### 🐳 Usando Docker (Recomendado)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/EliuthMisraim/Proyecto-Consumo-Masivo-Reckitt.git
   cd Proyecto-Consumo-Masivo-Reckitt
   ```

2. **Levantar los servicios:**
   ```bash
   docker-compose up --build
   ```
   - El **Dashboard** estará disponible en: `http://localhost:8501`
   - La **API** estará disponible en: `http://localhost:8000/docs`

### 💻 Instalación Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/EliuthMisraim/Proyecto-Consumo-Masivo-Reckitt.git
   cd Proyecto-Consumo-Masivo-Reckitt
   ```

2. **Crear entorno e instalar dependencias:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Ejecutar Dashboard y API:**
   ```bash
   # En una terminal para la API
   uvicorn main:app --reload

   # En otra terminal para el Dashboard
   streamlit run app.py
   ```

---
*Desarrollado por [EliuthMisraim](https://github.com/EliuthMisraim)*
