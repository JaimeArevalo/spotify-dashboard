import os
import subprocess

# Usar un puerto predeterminado (8080 es común en Railway)
port = 8080

# Si hay una variable de entorno PORT, úsala
if 'PORT' in os.environ:
    try:
        port = int(os.environ.get('PORT'))
        print(f"Using PORT from environment: {port}")
    except ValueError:
        print(f"Invalid PORT value: {os.environ.get('PORT')}, using default port {port}")

# Ejecutar Streamlit con el puerto especificado
cmd = f"streamlit run app.py --server.port={port} --server.address=0.0.0.0"
print(f"Running command: {cmd}")
subprocess.run(cmd, shell=True)