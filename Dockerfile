FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copiar requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto 8501 predeterminado para Streamlit
EXPOSE 8501

# Usa un script de entrada para manejar correctamente la variable de entorno PORT
RUN echo '#!/bin/bash\n\
port=${PORT:-8501}\n\
echo "Starting Streamlit on port: $port"\n\
streamlit run --server.port=$port --server.address=0.0.0.0 app.py\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Comando para ejecutar la aplicación
CMD ["/app/start.sh"]