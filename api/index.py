"""
Simulador PAES 2026 - Vercel API
"""

import sys
import os
import subprocess

# Asegurar que el directorio raíz está en el path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
os.chdir(root_dir)

# Importar y ejecutar Streamlit
def handler(event, context):
    # Ejecutar Streamlit en modo headless
    subprocess.Popen([
        "streamlit", "run", "paes.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ])
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": """
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0; url=/">
            <title>Simulador PAES 2026</title>
        </head>
        <body>
            <h1>📚 Simulador PAES 2026</h1>
            <p>Cargando...</p>
        </body>
        </html>
        """
    }