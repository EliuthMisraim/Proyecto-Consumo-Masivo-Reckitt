# 1. Usamos una imagen de Python ligera como base
FROM python:3.9-slim

# 2. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Instalamos herramientas básicas del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiamos el archivo de requerimientos e instalamos las librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos todo el contenido de tu proyecto al contenedor
COPY . .

# 6. Exponemos los puertos: 8501 para Streamlit y 8000 para la API
EXPOSE 8501
EXPOSE 8000

# 7. El comando por defecto (aquí es donde decides qué arrancar)
# Por ahora, arrancaremos la API, pero Docker nos permite elegir
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
